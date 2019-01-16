#!/usr/bin/env python
#-----------------------------------------------------------------------
# TimelyTigerServer.py
# Author: Dale Lee, Cody Sedillo, Daniel Pallares
#-----------------------------------------------------------------------
from OpenSSL import SSL
import pdb               # Python debugger
#pdb.set_trace() # <<<<=======Debug breakpoint
from sys import argv

from bottle import route, request, response, error, redirect, run, static_file
from bottle import template, TEMPLATE_PATH

import psycopg2 as p # sudo pip 

# DEPLOY HEROKU CHECKLIST
# -----------------------
# 1. Comment out import pdb
# 2. Make sure no pdb.set_trace() in code
# 3. Check for database changes
# 4. Change tag APPLICATION_LOCATION='LOCAL' # 'HEROKU' # <<<< CHANGE WHEN DEPLOY TO HEROKU
# 5. Change tag TIMELY_TIGER_VERSION="2.14 (debug)"
# 6. Set SIMULATE_MOBILE='No'
# 7. DISABLE_AUTO_REFRESH='No'




# Google API imports
# sudo pip install --upgrade google-api-python-client
# pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2
# sudo pip install google-auth-oauthlib
# sudo pip install google-auth-httplib2
# sudo -H pip install psycopg2-binary

# sudo pip install --upgrade google-api-python-client --ignore-installed six
# sudo pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2
import google.oauth2.credentials 
import google_auth_oauthlib.flow 
import googleapiclient.discovery 

import json # sudo pip 
import os # sudo pip 

# working with Datetime and Time class
import timeAlg # sudo pip 
import time # sudo pip 
from time import gmtime, strftime, mktime
from datetime import datetime  
from datetime import timedelta

# sudo -H pip install --upgrade flask
# sudo -H pip install --upgrade requests
import flask
from flask import request, Flask, send_from_directory

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.

CLIENT_SECRETS_FILE = "client_secret_899885585030-j4o4conctbnpmke5qqjekejufeo8lb70.apps.googleusercontent.com.json"



# THINGS TO CHANGE UPON DEPLOYMENT....
#-------------------------------------
APPLICATION_LOCATION='HEROKU' # 'HEROKU' vs 'LOCAL'#
TIMELY_TIGER_VERSION="2.24"
SIMULATE_MOBILE='No' # 'No' 'Yes'
DISABLE_AUTO_REFRESH='No'  # stop refresh when debugging


UNKNOWN_PERSON_PHOTO_URL="https://artprojectsforkids.org/wp-content/uploads/2016/10/Draw-a-Tiger-Face.jpg"


# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ["https://www.googleapis.com/auth/userinfo.email",
          "https://www.googleapis.com/auth/userinfo.profile",
          "https://www.googleapis.com/auth/calendar",
          "https://www.googleapis.com/auth/plus.me"]
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'

app = flask.Flask(__name__)

app.secret_key = 'QUiXw4DPDmzZl7JKFqBoTWuI'

TEMPLATE_PATH.insert(0, '')



@app.route('/')
@app.route('/eventForm')
def eventForm():

    # Try to get credintials silently, else direct to login page....

    try:
        # Load credentials from the session.
        credentials = google.oauth2.credentials.Credentials(
            **flask.session['credentials'])

        service = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, credentials=credentials)
        calendar = service.calendars().get(calendarId='primary').execute()

    except:
        # Create flow instance to manage the OAuth 2.0 Authorization steps.
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES)

        flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

        authorization_url, state = flow.authorization_url(
            # Enable offline access so that you can refresh an access token without
            # re-prompting the user for permission. Recommended for web server apps.
            access_type='offline',
            # Enable incremental authorization. Recommended as a best practice.
            include_granted_scopes='true')

        # Store the state so the callback can verify the auth server response.
        flask.session['state'] = state

        return flask.redirect(authorization_url)

    # Get broswer and platform information 
    # to decide how events will be formatted
    browser = request.user_agent.browser
    version = request.user_agent.version and int(request.user_agent.version.split('.')[0])
    platform = request.user_agent.platform
    uas = request.user_agent.string

    # supported platforms: iphone, android, windows, mac 
    # supported browsers: chrome

    yEmail = calendar['id'].lower()
    name = calendar['summary']
    personInfo=getDBPerson(yEmail,name)
    templateInfo = {"LoginPersonEmail":personInfo["email"]
                    ,"LoginPersonName":personInfo["name"]
                    ,"loginPersonPhotoLink": personInfo["photoLink"]
                    ,"TTVersionNumber":TIMELY_TIGER_VERSION}

    if (request.user_agent.platform == 'iphone') or (request.user_agent.platform == 'android') or (SIMULATE_MOBILE=='Yes'):
        return template('TTMainPageMobile.tpl', templateInfo)
    else:
        return template('TTMainPage.tpl', templateInfo)

@app.route('/RefreshAttendeesDetailView')
def RefreshAttendeesDetailView():

    # Called by Ajax refresh timer to show changing attendee status
    # If the event is scheduled, refresh will set the SetTigerRefreshTimer
    # which will cause perpetual refreshes

    if UserLoggedInWithAnotherAccount():
        return 'ForceAuthorization,No HTML' # Send a message to processReadyStateChange()
        #--- FORCE LOGIN ----->


    TigerEventID=request.args.get('TigerEventID')
    UpdateAttendeesOneEvent(TigerEventID)
    Event=getDBEventDetails(TigerEventID,0)

    # return new HTML for the EventAttendees table
    return ("EventAttendees" + str(TigerEventID) + "," + AttendeesAndStatusAsHTML(2,TigerEventID,Event['googleid']))   

@app.route('/RefreshEventSummaryView')
def RefreshEventSummaryView():

    # Called by Ajax refresh timer to show changing attendee status
    # If the event is scheduled, refresh will set the SetTigerRefreshTimer
    # which will cause perpetual refreshes

    if UserLoggedInWithAnotherAccount():
        return 'ForceAuthorization,No HTML' # Send a message to processReadyStateChange()
        #--- FORCE LOGIN ----->


    TigerEventID=request.args.get('TigerEventID')
    timezone=request.args.get('tz')

    UpdateAttendeesOneEvent(TigerEventID)
    # get from database and send back new html
    Event = getDBEventDetails(TigerEventID,timezone)

    # return new HTML for the whole event row
    return ("TigerEvent" + str(Event['eventid']) + "," + MakeEventHTML(Event))


@app.route('/UpdateUserData')
def UpdateUserData():

    if UserLoggedInWithAnotherAccount():
        return 'ForceAuthorization,No HTML' # Send a message to processReadyStateChange()
        #--- FORCE LOGIN ----->


    # Add attendee to event
    email=request.args.get('Email').lower()
    name=request.args.get('Name')
    photoLink=request.args.get('PhotoLink')
    updateDBPerson(email,name,photoLink)
    # return new HTML for the EventAttendees table
    return ("LoginUser," + LoginUserHTML(email))

# Serve up pictures etc.
@app.route('/static/<filename>', methods=['GET'])
def server_static(filename):
    return send_from_directory("./Resources/", filename)

# Add/delete Attendees

@app.route('/DeleteAttendee')
def DeleteAttendee():

    if UserLoggedInWithAnotherAccount():
        return 'ForceAuthorization,No HTML' # Send a message to processReadyStateChange()
        #--- FORCE LOGIN ----->


    # Add attendee to event
    TigerEventID=request.args.get('TigerEventID')
    AttendeeEmail=request.args.get('AttendeeEmail').lower()
    updateDBEventDeleteAttendee(TigerEventID,AttendeeEmail)
    # return new HTML for the EventAttendees table
    return ("EventAttendees" + str(TigerEventID) + "," + AttendeesAndStatusAsHTML(2,TigerEventID,None))

@app.route('/AddAttendee')
def AddAttendeet():

    if UserLoggedInWithAnotherAccount():
        return 'ForceAuthorization,No HTML' # Send a message to processReadyStateChange()
        #--- FORCE LOGIN ----->

    # Add attendee to event
    TigerEventID=request.args.get('TigerEventID')
    NewAttendeeEmail=request.args.get('NewAttendeeEmail').lower()
    UserEmailFromClient=request.args.get('UserEmail').lower()

    # Try adding to event if the user is not adding themselves..
    if UserEmailFromClient != NewAttendeeEmail:
        updateDBEventAddAttendee(TigerEventID,NewAttendeeEmail)

    # return new HTML for the EventAttendees table
    return ("EventAttendees" + str(TigerEventID) + "," + AttendeesAndStatusAsHTML(2,TigerEventID,None))

# Edit/Save an New Event

@app.route('/SaveEvent')
def SaveEvent():

    if UserLoggedInWithAnotherAccount():
        return 'ForceAuthorization,No HTML' # Send a message to processReadyStateChange()
        #--- FORCE LOGIN ----->


    TigerEventID=request.args.get('TigerEventID')
    timezone=request.args.get('tz')

    # update database
    Event = {
            'eventid': TigerEventID
            ,'title': request.args.get('EventTitle')
            ,'description': request.args.get('EventDescription')
            ,'meetingLength': request.args.get('EventLength')
            ,'place': request.args.get('EventLocation')
            }
    updateDBEvent(Event)

    # get from database and send back new html
    Event = getDBEventDetails(TigerEventID,timezone)
    return ("TigerEvent" + str(Event['eventid']) + "," + MakeEventHTML(Event))

@app.route('/CloseEvent')
def CloseEvent():

    if UserLoggedInWithAnotherAccount():
        return 'ForceAuthorization,No HTML' # Send a message to processReadyStateChange()
        #--- FORCE LOGIN ----->


    TigerEventID=request.args.get('TigerEventID')
    timezone=request.args.get('tz')

    UpdateAttendeesOneEvent(TigerEventID)
    # get from database and send back new html
    Event = getDBEventDetails(TigerEventID,timezone)

    return ("TigerEvent" + str(Event['eventid']) + "," + MakeEventHTML(Event))


@app.route('/ScheduleEvent')
def ScheduleEvent():

    if UserLoggedInWithAnotherAccount():
        return 'ForceAuthorization,No HTML' # Send a message to processReadyStateChange()
        #--- FORCE LOGIN ----->


    TigerEventID=request.args.get('TigerEventID')
    timezone=request.args.get('tz')

    # Make sure all information in DB is up-to-date
    Event = {
        'eventid': TigerEventID
        ,'title': request.args.get('EventTitle')
        ,'description': request.args.get('EventDescription')
        ,'meetingLength': request.args.get('EventLength')
        ,'place': request.args.get('EventLocation')
        }
    updateDBEvent(Event)

    offset = int(request.args.get('tz'))
    offset *= 60

    # Schedule the event in google
    googleid = makeGoogleEvent(TigerEventID) 

    # get from database and send back new html
    Event = getDBEventDetails(TigerEventID,timezone)
    return ("TigerEvent" + str(Event['eventid']) + "," + MakeEventHTML(Event))


@app.route('/UnscheduleEvent')
def UnscheduleEvent():

    if UserLoggedInWithAnotherAccount():
        return 'ForceAuthorization,No HTML' # Send a message to processReadyStateChange()
        #--- FORCE LOGIN ----->


    TigerEventID=request.args.get('TigerEventID')
    timezone=request.args.get('tz')

    UnscheduleGoogleEvent(TigerEventID)

    # Get changed event from database
    Event=getDBEventDetails(TigerEventID,timezone)
    return ("TigerEvent" + str(Event['eventid']) + "," + MakeEventDetailHTML(Event))

@app.route('/DeleteEvent')
def DeleteEvent():

    if UserLoggedInWithAnotherAccount():
        return 'ForceAuthorization,No HTML' # Send a message to processReadyStateChange()
        #--- FORCE LOGIN ----->


    TigerEventID=request.args.get('TigerEventID')
    timezone=request.args.get('tz')

    Event = getDBEventDetails(TigerEventID,0)

    # remove from calendars if it was scheduled
    if Event['googleid']!=None:
        UnscheduleGoogleEvent(TigerEventID)

    # delete from database
    updateDBDeleteEvent(TigerEventID)


    # Refresh all events


    # Begin with the header row...
    ret =   "AllEvents,<tr style='border-bottom:1px solid black'>\
                <td align='left'></td>\
                <td align='left'>Status</td>\
                <td align='left'></td>\
                <td align='left'></td>\
                <th align='left'>Time</th>\
                <th align='left'>Date</th>\
                <th align='left'>Action</th>\
            </tr>"



    # Using the UserID get all events...
    user=request.args.get('UserEmail').lower()
    eventIDs = getDBUsersEventIDs(user)
    for eventID in eventIDs:
        Event = getDBEventDetails(eventID,timezone)
        ret += "<tr ID='TigerEvent" + str(eventID) + "' style='border-bottom:1px solid black'>"\
            + MakeEventHTML(Event) + "</tr>"
    return ret

@app.route('/EditEvent')
def EditEvent():

    if UserLoggedInWithAnotherAccount():
        return 'ForceAuthorization,No HTML' # Send a message to processReadyStateChange()
        #--- FORCE LOGIN ----->


    TigerEventID=request.args.get('TigerEventID')
    timezone=request.args.get('tz')

    # Most up-to-date attendee status
    UpdateAttendeesOneEvent(TigerEventID)

    Event=getDBEventDetails(TigerEventID,timezone)
    #Event={"EventID":TigerEventID}
    return ("TigerEvent" + str(Event['eventid']) + "," + MakeEventDetailHTML(Event))

@app.route('/CreateNewEvent')
def CreateNewEvent():

    #pdb.set_trace()
    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    calendar = service.calendars().get(calendarId='primary').execute()

    # need to send email etc. to display at top of template
    user = str(calendar['id']).lower()

    # Send user to login screen if emails don't match...
    # (user is logged in with different accounts at the same time in the same browser)
    UserEmailFromClient=request.args.get('UserEmail')
    if str(UserEmailFromClient).lower() != str(user).lower():
        return 'ForceAuthorization,No HTML' # Send a message to processReadyStateChange()
        #--- FORCE LOGIN ----->


    # Times will be entered in DB as UTC. Need to subtract time zone to look like now
    # now, when we read them back below
    sRightnow = str(datetime.utcnow())
    sTomorrowSameTime = str(datetime.utcnow() + timedelta(days=1))

    Event = {
        'eventtitle':''
        ,'description': ''
        ,'meetingLength': 60
        ,'startdate': sRightnow
        ,'enddate': sTomorrowSameTime
        ,'place': ''
        ,'ownerEmail': user
    }
    TigerEventID = createNewDBEvent(Event)

    eventIDs = getDBUsersEventIDs(user)

    # Begin with the header row...
    if (request.user_agent.platform == 'iphone') or (request.user_agent.platform == 'android') or (SIMULATE_MOBILE=='Yes'):

        # Include one fewer columns withOUT Action links if MOBILE. Use SMALL fonts

        ret =   "AllEvents,<tr style='border-bottom:1px solid black; font-size:small;'>\
                    <td align='left'></td>\
                    <th align='left'>Status</th>\
                    <td align='left'></td>\
                    <td align='left'></td>\
                    <th align='left'>Time</th>\
                    <th align='left'>Date</th>\
                </tr>"
    else:

        # Include one more column with Action links if NOT mobile

        ret =   "AllEvents,<tr style='border-bottom:1px solid black'>\
                    <td align='left'></td>\
                    <th align='left'>Status</th>\
                    <td align='left'></td>\
                    <td align='left'></td>\
                    <th align='left'>Time</th>\
                    <th align='left'>Date</th>\
                    <th align='left'>Action</th>\
                </tr>"

    timezone=request.args.get('tz')
    for eventID in eventIDs:
        Event = getDBEventDetails(eventID,timezone)
        if eventID == TigerEventID:
            ret += "<tr ID='TigerEvent" + str(eventID) + "' style='border-bottom:1px solid black'>"\
                + MakeEventDetailHTML(Event) + "</tr>"    
        else:
            ret += "<tr ID='TigerEvent" + str(eventID) + "' style='border-bottom:1px solid black'>"\
                + MakeEventHTML(Event) + "</tr>"
    return (ret)


# Load all events. This is called when the page
# is first opened and if a new event is created
@app.route('/RefreshAllEvents')
def RefreshAllEvents():

    if UserLoggedInWithAnotherAccount():
        return 'ForceAuthorization,No HTML' # Send a message to processReadyStateChange()
        #--- FORCE LOGIN ----->

    # Get up-to-date status on all attendees to all events
    user=request.args.get('UserEmail').lower()
    UpdateAttendeesAllEvents(user)

    # Begin with the header row...
    if (request.user_agent.platform == 'iphone') or (request.user_agent.platform == 'android') or (SIMULATE_MOBILE=='Yes'):

        # Include one fewer columns withOUT Action links if MOBILE. Use SMALL fonts

        ret =   "AllEvents,<tr style='border-bottom:1px solid black; font-size:small;'>\
                    <td align='left'></td>\
                    <th align='left'>Status</th>\
                    <td align='left'></td>\
                    <td align='left'></td>\
                    <th align='left'>Time</th>\
                    <th align='left'>Date</th>\
                </tr>"
    else:

        # Include one more column with Action links if NOT mobile

        ret =   "AllEvents,<tr style='border-bottom:1px solid black'>\
                    <td align='left'></td>\
                    <th align='left'>Status</th>\
                    <td align='left'></td>\
                    <td align='left'></td>\
                    <th align='left'>Time</th>\
                    <th align='left'>Date</th>\
                    <th align='left'>Action</th>\
                </tr>"

    # Add events after the header
    eventIDs = getDBUsersEventIDs(user)
    timezone=request.args.get('tz')

    for eventID in eventIDs:
        Event = getDBEventDetails(eventID,timezone)
        ret += "<tr ID='TigerEvent" + str(eventID) + "' style='border-bottom:1px solid black'>"\
            + MakeEventHTML(Event) + "</tr>"

    return ret


# Suggest and Select Times

@app.route('/GetSuggestedTimes')
def GetSuggestedTimes():

    if UserLoggedInWithAnotherAccount():
        return 'ForceAuthorization,No HTML' # Send a message to processReadyStateChange()
        #--- FORCE LOGIN ----->

    #pdb.set_trace()
    TigerEventID=request.args.get('TigerEventID')
    BeginDateTime=request.args.get('BeginDateTime')
    EndDateTime=request.args.get('EndDateTime')
    EventLength=request.args.get('EventLength')
    offset = int(request.args.get('tz'))
    offset *= 60

    ret =   "SuggestedTimesTableCell" + str(TigerEventID) + "," + SuggestedTimesHTML(TigerEventID,BeginDateTime,EndDateTime,EventLength,offset);
    return ret

@app.route('/SubmittSelectedTime')
def SubmittSelectedTime():

    if UserLoggedInWithAnotherAccount():
        return 'ForceAuthorization,No HTML' # Send a message to processReadyStateChange()
        #--- FORCE LOGIN ----->

    TigerEventID=request.args.get('TigerEventID')
    SelectedTime=request.args.get('SelectedTime')

    BeginDateTime=request.args.get('BeginDateTime')
    EndDateTime=request.args.get('EndDateTime')
    EventLength=request.args.get('EventLength')
    timezone=request.args.get('tz')

    # Save selected date-time in database
    EventDateTime={'eventid':TigerEventID, 'Minutes':EventLength,'DateAndTime':SelectedTime,'StartRange':BeginDateTime,'EndRange':EndDateTime,'timezone':timezone}
    updateDBEventSlectedTime(EventDateTime)

    # update form to show only selected time
    ret="SuggestedTimesTableCell" + str(TigerEventID) + "," + SelectedTimeHTML(TigerEventID,SelectedTime)\
    + "<button onclick='GetSuggestedTimes("+str(TigerEventID)+")'>choose again...</button>"
    return ret


# important
@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        prompt='select_account',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return flask.redirect(authorization_url)


# more redirection
@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    ## MIGHT NEED TO COMMENT OUT FOLLOWING LINE IF RUNNING LOCALLY
    authorization_response = authorization_response.replace('http', 'https')
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect('/eventForm')


    
# @error(404)
# def notFound(error):
#     return 'Not found'


# END OF HTML ROUTING
#---------------------


def UserLoggedInWithAnotherAccount():

    # Timely Tiger does not support concurrent login

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    calendar = service.calendars().get(calendarId='primary').execute()

    # need to get all user's events
    user = str(calendar['id']).lower()

    # Send user to login screen if emails don't match...
    # (user is logged in with different accounts at the same time in the same browser)
    UserEmailFromClient=request.args.get('UserEmail')
    if str(UserEmailFromClient).lower() != str(user).lower():
        return True # user logged in with a different account
    else:
        return False # No crediential missmatch


def credentials_to_dict(credentials):
    return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


# FUNCTIONS TO CREATE HTML
#--------------------------

def LoginUserHTML(email):

    # get the persons information
    person = getDBPersonNoUpdate(email)

    # form the html to go into <div id='LoginUser'>
    ret="<img src='" + person['photoLink'] + "' href='/authorize' width='50px' height='50px' alt='User Photo'>\
         <br><font style='font-size:12px'>" + person['name'] + "</font>\
         <A style='font-size:8px' href=\"javascript:UpdateUserDateEdit('" + email+ "','" + person['name'] + "','" + person['photoLink'] + "');\">edit</A>"
    return ret


def UpdateAttendeesAllEvents(email):

    # All events for this user
    EventIDList=getDBUsersEventIDs(email)

    for EventID in EventIDList:
        UpdateAttendeesOneEvent(EventID)

def UpdateAttendeesOneEvent(EventID):

    EventDetail = getDBEventDetails(EventID,0)
    EVE_googleID = EventDetail['googleid']

    # Check of the event was scheduled

    if EVE_googleID != None:

        # Scheduled! Get attendee status
        GoogleAttendees=attendee_status(EVE_googleID)

        # For each attendee in Timely Tiger, update the database with status from google

        TTAttendees = getDBEventAttendees(EventID)
        for TTAttendee in TTAttendees:
            ttAttendeeEmail = TTAttendee['email']
            updateDBAttendeeStatus( EventID,ttAttendeeEmail,GoogleAttendees[ttAttendeeEmail.lower()]) 


def SuggestedTimesHTML(EventID,BeginDateTime,EndDateTime,EventLength,offset):

    if BeginDateTime!="" and EndDateTime!="":

        # Load credentials from the session.
        credentials = google.oauth2.credentials.Credentials(
            **flask.session['credentials'])

        # Get the calendar IP for this logged in user
        service = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, credentials=credentials)
        calendar = service.calendars().get(calendarId='primary').execute()
        # yEmail = calendar['id']
        # pEmail = "dale.jing.l@gmail.com"


        listAttendees=[{"id":str(calendar['id'])}]   # first attendee is the interactive user
        people=[str(calendar['id'])]
        AttendeeList = getDBEventAttendees(EventID)
        for Attendee in AttendeeList:
            listAttendees.append({"id":str(Attendee["email"])})
            people.append(str(Attendee["email"]))

        # Convert to UTC and correct format
        dtStartRange = datetime.strptime(str(BeginDateTime),'%Y-%m-%dT%H:%M')+timedelta(minutes=offset/60)
        dtEndRange = datetime.strptime(str(EndDateTime),'%Y-%m-%dT%H:%M')+timedelta(minutes=offset/60)
        sBeginDateTime = dtStartRange.strftime("%Y-%m-%dT%H:%M") + ":00Z"
        sEndDateTime = dtEndRange.strftime("%Y-%m-%dT%H:%M") + ":00Z"
        body = {
              "timeMin": sBeginDateTime,
              "timeMax": sEndDateTime,
              "items": listAttendees,
              "timeZone": "UTC"
        }

        # # change from Unicde if any...
        # BeginDateTime=str(BeginDateTime)
        # EndDateTime=str(EndDateTime)
        # body = {
        #       "timeMin": BeginDateTime + ':00Z',
        #       "timeMax": EndDateTime + ':00Z',
        #       "items": listAttendees,
        #       "timeZone": "UTC"
        # }

    
        eventsResult = service.freebusy().query(body=body).execute()
        
        # put input into json format
        dumped = json.dumps(eventsResult)
        loadInfo = json.loads(dumped)



        #pdb.set_trace()
        list_times = timeAlg.timeAlgorithm(loadInfo, people, BeginDateTime, EndDateTime, str(EventLength), offset)
        num_times = len(list_times)

        dt_BeginDateTime=datetime.strptime(BeginDateTime,'%Y-%m-%dT%H:%M') #+ timedelta(seconds=int(offset))
        dt_EndDateTime=datetime.strptime(EndDateTime,'%Y-%m-%dT%H:%M') #+ timedelta(seconds=int(offset))

        ret="<form ID='SuggestedTimesForm"+ str(EventID) + "'' valign='top' style='width:150px; background-color: #E0E0E0;font-size:14px'>"
        for aTime in list_times:

            dt_aTime = datetime.strptime(aTime,'%Y-%m-%d %H:%M')

            # correct time when deployed in Heroku
            if APPLICATION_LOCATION=='HEROKU':
                dt_aTime += timedelta(seconds=int(offset))
            else:
                dt_aTime += timedelta(seconds=int(0))

            # List the time if it is within range
            if (dt_aTime >= dt_BeginDateTime) and (dt_aTime < dt_EndDateTime):
                #s_aTime = dt_aTime.strftime("%Y-%m-%d %H:%M")   # format must match updateDBEventSlectedTime()
                s_aTime = dt_aTime.strftime("%Y-%m-%d %I:%M %p") # format must match updateDBEventSlectedTime()

                ret += "<input name='TTradioTime' type='radio' value='" + s_aTime + "' >" + s_aTime + "<br>"
        
        # Display the submit button
        ret += "<input name='TTradioTime' type='button' value='submit' onclick='SubmitSelectedTime(" + str(EventID) + ")'></form>" # + "<br><br>body=" + str(body) + "<br><br>eventsResult=" + str(eventsResult)

    else:
        ret="set both times"

    return ret # + "Body=" + str(body) + ",BeginDateTime=" + str(BeginDateTime) + ",EndDateTime=" + str(EndDateTime) + ",offset=" + str(offset) + ",eventsResult=" + str(eventsResult)
# Create an event that is not in edit mode...
def MakeEventHTML(Event):

    # Show the summary form of an event. Sets a timer (see <A at end) to fresh fresh
    # the event to show status change of attendees.

    ret= "<td><table>" + AttendeesAndStatusAsHTML(1,Event['eventid'],Event['googleid']) + "</table></td>"

    # Show status. Small fonts if mobile...

    if (request.user_agent.platform == 'iphone') or (request.user_agent.platform == 'android') or (SIMULATE_MOBILE=='Yes'):
        # If google ID present, display 'scheduled'
        ret += "<td style='font-size:small;'>" 
    else:
        ret += "<td>" 

    if Event['googleid']==None:
        ret += ''
    else:
        ret += "scheduled"
    ret += "</td>"



    if (request.user_agent.platform == 'iphone') or (request.user_agent.platform == 'android') or (SIMULATE_MOBILE=='Yes'):
        # One less column and no delete link if MOBILE
        ret += "<td><button onclick='EditEvent("+str(Event['eventid'])+")'>view</button></td>\
             <td style='font-size:small;'>" + Event['eventtitle'] + "</td>\
             <td style='font-size:small;'> " + str(Event['meetingLength']) + " min</td>\
             <td style='font-size:small;'>" + str(Event['dateandtime']) + "</td>"
    else:
        # One more column and include delete link if NOT mobile
        ret += "</td>\
             <td><button onclick='EditEvent("+str(Event['eventid'])+")'>view details </button></td>\
             <td>" + Event['eventtitle'] + "</td>\
             <td> " + str(Event['meetingLength']) + " minutes</td>\
             <td>" + str(Event['dateandtime']) + "</td>\
             <td><A HREF='javascript:DeleteEvent(" + str(Event['eventid']) + ")''>delete</A></td>"
             #<load onload='SetTigerTimer(" + str(Event['eventid']) + ")' >"
             #<img onload='SetTigerTimer(" + str(Event['eventid']) + ")'src='http://2.bp.blogspot.com/-eoLbxykkD58/UU0vnWYBuTI/AAAAAAAAAkA/-emXI9iNDSg/s1600/queequeg.gif' >"

    return ret

def MakeEventDetailHTML(Event):
    # 
    # Create an event that IS in edit mode....
    #

    # Apply to style to enable disable controls...

    if Event['googleid']==None:
        EnableDisable=""
    else:
        EnableDisable="pointer-events: none;"

    # Create different HTML for mobile...

    if (request.user_agent.platform == 'iphone') or (request.user_agent.platform == 'android') or (SIMULATE_MOBILE=='Yes'):

        # One fewer columns, smaller margins for mobile for MOBILE

        ret = "<td align='left' colspan=6>\
                <table valign=top style='width:100%; margin-left:10px; margin-right:5px; margin-top:5px; margin-top:5px'>\
                    <tr style= 'font-size:12px'>\
                      <td>\
                        <b>Attendees</b>\
                      </td><td>\
                        <b>Title</b>\
                      </td><td>\
                        <b>Start Time Range</b>\
                      </td><td>\
                        <b>Suggested Meeting Times</b>\
                      </td>\
                    </tr>"
    else:

        # Non mobile has seperate columns for start end time range controls

          ret = "<td align='left' colspan=7>\
                <table style='width:100%; margin-left:10px; margin-right:10px; margin-top:10px; margin-top:10px'>\
                    <tr valign=top style= 'font-size:12px'>\
                      <td>\
                      <b>Attendees</b>\
                      </td><td>\
                      <b>Event Title</b>\
                      </td><td>\
                      <b>Start Time Range</b>\
                      </td><td>\
                      <b>End Time Range</b>\
                      </td><td>\
                      <b>Meeting Length</b>\
                      </td><td>\
                      <b>Suggested Meeting Times</b>\
                      </td>\
                    </tr>"      

    ret += "<tr valign=top style= 'font-size:12px'>\
                    <td style='width:30%' valign='top' rowspan='2'>\
                        <table ID='EventAttendees" + str(Event['eventid']) + "' style='" + EnableDisable + "'>"\
                        + AttendeesAndStatusAsHTML(2,Event['eventid'],Event['googleid']) \
                        + "</table>"

    if Event['googleid']==None:
        
        # Allow adding attendees if not scheduled

        ret +=          "<b>New attendee email</b>\
                        <br><input style='width:80%; background-color: #E0E0E0;' type='text' ID='NewAttendeeEmail"+ str(Event['eventid']) + "' name='EventAddPeople' value=''>\
                        <button onclick='AddAttendee("+ str(Event['eventid']) +" )'>add</button>"

    # Add location
    ret +=              "<br>\
                        <b>Location</b>\
                        <input style='width:95%; background-color: #E0E0E0;" + EnableDisable + "' type='text' ID='EventLocation"+ str(Event['eventid']) + "' value='" + str(Event['place']) + "'>\
                        <br><br>"

    # Decide how display Modify, Schedule and Save buttons

    if Event['googleid']==None:
        ret +=  "<button style='font-size:30px;border-radius:5px;background-color:#D5650D;color:#FFFFFF;padding: 1px 25px 5px 20px' onclick='ScheduleEvent("+ str(Event['eventid']) +")'>Schedule</button>\
                        <button style='font-size:30px;border-radius:5px;background-color:#D5650D;color:#FFFFFF;padding: 1px 25px 5px 20px' onclick='SaveEvent("+ str(Event['eventid']) +")'>Save</button>"
    else:
        ret +="<button style='font-size:30px;border-radius:5px;background-color:#D5650D;color:#FFFFFF;padding: 1px 25px 5px 20px' onclick='UnscheduleEvent("+ str(Event['eventid']) +")'>Modify</button>\
                        <button style='font-size:30px;border-radius:5px;background-color:#D5650D;color:#FFFFFF;padding: 1px 25px 5px 20px' onclick='CloseEvent("+ str(Event['eventid']) +")'>Close</button>"
 
    # Event title

    if (request.user_agent.platform == 'iphone') or (request.user_agent.platform == 'android') or (SIMULATE_MOBILE=='Yes'):

        # Flexiable size if MOBILE, Place the Event Length Control under title

        ret +=  "<td><input type='text' ID='EventTitle"+ str(Event['eventid']) + "' value='" + str(Event['eventtitle']) + "' style='width:95%; background-color: #E0E0E0;" + EnableDisable + "' >\
                 <br><b>Meeting Length</b>\
                  <select ID='EventLength"+ str(Event['eventid']) + "' style='width:95%; background-color: #E0E0E0;" + EnableDisable + "' onchange='GetSuggestedTimes(" + str(Event['eventid']) + ")' >"

        # Make the elements of a drop down control 
        # which looks like this, if 60 minutes was previously selected...
        #      <option value='15'>15 minutes</option>
        #      <option value='30'>30 minutes</option>
        #      <option value='60' selected>1 hour</option>
        #      <option value='120'>2 hours</option>\          

        times = [15,30,60,120]
        for selection in times:
            if selection==Event['meetingLength']:
                ret += "<option value='" + str(selection) + "' selected>" + str(selection) + " minutes</option>"
            else:
                ret += "<option value='" + str(selection) + "' >" + str(selection) + " minutes</option>"

        ret +=    "</select>\
            </td>"
    else:

        # Fixed size if NOT mobile
        ret +=  "<td><input type='text' ID='EventTitle"+ str(Event['eventid']) + "' value='" + str(Event['eventtitle']) + "' style='width:185px; background-color: #E0E0E0;" + EnableDisable + "' >\
                            </td>"

    # Controls for begin end time range

    if (request.user_agent.platform == 'iphone') or (request.user_agent.platform == 'android') or (SIMULATE_MOBILE=='Yes'):

        # Begin/End controls go into the same column if MOBILE

        ret +="<td> <input type='datetime-local' ID='RangeStart"+ str(Event['eventid']) + "' value='" + str(Event['startdate'])[0:10]+"T"+str(Event['startdate'])[11:16] + "' onchange='GetSuggestedTimes(" + str(Event['eventid']) + ")' style='width:185px; background-color: #E0E0E0;" + EnableDisable + "'>\
                    <br><b>End Time Range</b>\
                    <br><input type='datetime-local' ID='RangeEnd"+ str(Event['eventid']) + "' value='" + str(Event['enddate'])[0:10]+"T"+str(Event['enddate'])[11:16] + "' onchange='GetSuggestedTimes(" + str(Event['eventid']) + ")' style='width:185px; background-color: #E0E0E0;" + EnableDisable + "'>\
                </td>"
    else:

        # Begin/End controls go into different columns if NOT mobile

        ret +="<td><input type='datetime-local' ID='RangeStart"+ str(Event['eventid']) + "' value='" + str(Event['startdate'])[0:10]+"T"+str(Event['startdate'])[11:16] + "' onchange='GetSuggestedTimes(" + str(Event['eventid']) + ")' style='width:185px; background-color: #E0E0E0;" + EnableDisable + "'>\
                </td>\
                <td><input type='datetime-local' ID='RangeEnd"+ str(Event['eventid']) + "' value='" + str(Event['enddate'])[0:10]+"T"+str(Event['enddate'])[11:16] + "' onchange='GetSuggestedTimes(" + str(Event['eventid']) + ")' style='width:185px; background-color: #E0E0E0;" + EnableDisable + "'>\
                </td>"

    if (request.user_agent.platform == 'iphone') or (request.user_agent.platform == 'android') or (SIMULATE_MOBILE=='Yes'):
        ret += " "
    else:
        # Add control for meeting length
        ret += "<td>\
                  <select ID='EventLength"+ str(Event['eventid']) + "' style='width:100px; background-color: #E0E0E0;" + EnableDisable + "' onchange='GetSuggestedTimes(" + str(Event['eventid']) + ")' >"

        # Make the elements of a drop down control 
        # which looks like this, if 60 minutes was previously selected...
        #      <option value='15'>15 minutes</option>
        #      <option value='30'>30 minutes</option>
        #      <option value='60' selected>1 hour</option>
        #      <option value='120'>2 hours</option>\          

        times = [15,30,60,120]
        for selection in times:
            if selection==Event['meetingLength']:
                ret += "<option value='" + str(selection) + "' selected>" + str(selection) + " minutes</option>"
            else:
                ret += "<option value='" + str(selection) + "' >" + str(selection) + " minutes</option>"
        ret +=      "</select>\
                </td>"

    # Finally, Control for selecting time

    ret += "<td rowspan='2' style='" + EnableDisable + "' valign='top' ID='SuggestedTimesTableCell" + str(Event['eventid']) + "' >"\
                        + SelectedTimeHTML(Event['eventid'],Event['dateandtime'])\
                        + "<button onclick='GetSuggestedTimes("+str(Event['eventid'])+")'>choose again...</button>\
                                    </td>"


    # Add description box, which is in the 2nd row...

    if (request.user_agent.platform == 'iphone') or (request.user_agent.platform == 'android') or (SIMULATE_MOBILE=='Yes'):

        # Description box only takes THREE columns on MOBILE
        ret += "</tr>\
                    <tr valign='top'>\
                    <td colspan='2' style= 'font-size:12px'>\
              <b>Event description\
              <textarea style='width:95%; background-color: #E0E0E0;" + EnableDisable + "' ID='EventDescription"+ str(Event['eventid']) + "' rows='12'>" + str(Event['description']) + "</textarea>\
                    </td>\
                </tr>\
            </table>\
            </td>"
    else:

        # Description takes FOUR columns if NOT mobile
        ret += "</tr>\
                    <tr valign='top'>\
                    <td colspan='4' style= 'font-size:12px'>\
              <b>Event description\
              <textarea style='width:99%; background-color: #E0E0E0;" + EnableDisable + "' ID='EventDescription"+ str(Event['eventid']) + "' rows='15'>" + str(Event['description']) + "</textarea>\
                    </td>\
                </tr>\
            </table>\
            </td>"

    return ret

def SelectedTimeHTML(eventid,dateandtime):
    # Format selected time in a "<Div" with an ID, so that Javascript
    # can test that a time has been selected if the user clicks schedule
    if dateandtime != None:
        return "<div ID='SelectedTime" + str(eventid) + "'>" + str(dateandtime) + "</div>"
    else:
        return "None selected"

def AttendeesAndStatusAsHTML(size,eventid,googleid):

    Padding = size * 4
    PicSize=size * 20
    attendees=getDBEventAttendees(eventid)
# onload='SetTigerTimer(" + str(Event['eventid']) + ")'
#             picRow += "<td style='padding-left: " + str(Padding) + "px; padding-right: " + str(Padding) + "px;'><img src='"\
#"<td style='padding-left: " + str(Padding) + "px; padding-right: " + str(Padding) + "px;'><img onload='SetTigerEventTimer(" + str(eventid) + ")' src='"\
    # Begin a row for pictures and status

    #pdb.set_trace()

    if (request.user_agent.platform == 'iphone') or (request.user_agent.platform == 'android') or (SIMULATE_MOBILE=='Yes'):
        AttendeesPerRow = 2
    else:
        AttendeesPerRow = 4

    # because the <img tag has an onload event, we will use this to schedule a javascript-Ajax refresh of this event, 
    # if it is scheduled, in order to show status of attendees

    #pdb.set_trace()
    ScheduleTimer=False
    if (googleid != None) and (DISABLE_AUTO_REFRESH=="No"):
        ScheduleTimer=True


    attendeesThisRow=0
    ret = ""
    picRow=""
    statusRow=""

    for attendee in attendees:

        if attendeesThisRow==0:
            picRow = "<tr valign=top>"
            statusRow = "<tr valign=top>"

        if size==2:

            # If size=2 then images are displayed in the event edit mode and we will display an "X" to allow deleting

            picRow += "<td style='padding-left: " + str(Padding) + "px; padding-right: " + str(Padding) + "px;'>"
            picRow += "<img "

            if ScheduleTimer:
                # Schedule Javascript Ajax timer to refresh 
                picRow += " onload='SetTigerRefreshTimer(" + str(eventid) + ")' "
                ScheduleTimer = False #<-- only set timer once

            picRow +=" src='" + str(attendee['photoLink']) + "' width='" + str(PicSize) + "px' height='" + str(PicSize) + "' alt='photo'>"\
                 + "<img src='/static/RedX.png' width='15px' height='15px' onclick=\"DeleteAttendee(" + str(eventid) + ",'" + str(attendee['email']) + "')\" >"\
                 + "<br><font size='1'>" + str(attendee['name']) + "</font></td>"
        else:

            # Attendee photo is displayed in summary mode. No "X" is displayed

            picRow += "<td style='padding-left: " + str(Padding) + "px; padding-right: " + str(Padding) + "px;'>"
            picRow += "<img "

            if ScheduleTimer:
                # Schedule Javascript Ajax timer to refresh 
                picRow += " onload='SetTigerRefreshTimer(" + str(eventid) + ")' "
                ScheduleTimer = False #<-- only set timer once

            picRow +=" src='" + str(attendee['photoLink']) + "' width='" + str(PicSize) + "px' height='" + str(PicSize) + "' alt='photo'>"\
                     + "<br><font size='1'>" + str(attendee['name']) + "</font></td>"

        #pdb.set_trace()

        statusRow += "<td style='padding-left: " + str(Padding) + "px; padding-right: " + str(Padding) + "px;'>"
        if attendee['status']=='accepted':
            statusRow += "<img src='/static/AcceptIcon.png' width='" + str(PicSize) + "' height='" + str(PicSize) + "' alt='Accept'>"
        elif attendee['status']=='declined':
            statusRow += "<img src='/static/DeclineIcon.png' width='" + str(PicSize) + "' height='" + str(PicSize) + "' alt='Decline'>"
        statusRow += "</td>"

        attendeesThisRow += 1

        if attendeesThisRow==AttendeesPerRow:
            # finish this double row
            ret += picRow  + "</tr>"+ statusRow + "</tr>"
            # start a new row
            picRow=""
            statusRow=""
            attendeesThisRow=0 # new row

    #pdb.set_trace()
    # Finish our the last row if we ran out of attendees
    for i in range(1,AttendeesPerRow-attendeesThisRow+1):
        picRow += "<td></td>"
        statusRow += "<td></td>"
        if attendeesThisRow+i==AttendeesPerRow:
            ret += picRow  + "</tr>"+ statusRow + "</tr>"

    #pdb.set_trace()
    return ret


# DATABASE FUNCTIONS
#-------------------


def connectDB():

    if APPLICATION_LOCATION=='LOCAL':
        # FOR CONNECTING TO LOCAL DATABASE
        con=p.connect(dbname="sample_db", user="postgres", host="localhost", port="5431")
    else:
        # FOR CONNECTING TO HEROKU DATABASE
        con = p.connect(os.environ['DATABASE_URL'], sslmode='require')

    return con

def updateDBPerson(email,name,photoLink):

    con = connectDB()
    cur = con.cursor()

     # insert event details into database
    cur.execute("UPDATE PPL_People SET PPL_Name=%s, PPL_PhotoLink=%s WHERE LOWER(PPL_Email) like LOWER(%s)", (name, photoLink, str(email)))
    con.commit()

    cur.close()
    if con is not None:
        con.close()

    return

def updateDBAttendeeStatus(EventID,email,status):
    
    con = connectDB()
    cur = con.cursor()

     # insert event details into database
    cur.execute("UPDATE INV_Invitees SET INV_Status=%s WHERE INV_EVE_EventID=%s and LOWER(INV_PPL_Email) like LOWER(%s)", (str(status), EventID, email,))
    con.commit()

    cur.close()
    if con is not None:
        con.close()

    return

def getDBPerson(email, name):

    # tries to find the person in the DB. If not found, inserts email, name and UNKNOWN_PERSON_PHOTO_URL

    con = connectDB()
    cur = con.cursor()

    SQL = "SELECT PPL_Email, PPL_Name, PPL_PhotoLink  FROM PPL_People WHERE LOWER(PPL_Email) like LOWER(%s)"
    data = (email,)
    cur.execute(SQL, data)
    returnResults = cur.fetchall()


    if len(returnResults)==0:
        # Not in PPL_People. Use email for name
        data = (email,name,UNKNOWN_PERSON_PHOTO_URL)
        cur.execute("INSERT INTO PPL_People(PPL_Email, PPL_Name, PPL_PhotoLink) VALUES (LOWER(%s),%s, %s)",data)
        con.commit()
        # treat as unknown person
        person={'email': email \
                ,'name': name \
                ,'photoLink': UNKNOWN_PERSON_PHOTO_URL} 
    else:
        # Use fist person with this email
        person={'email': returnResults[0][0] \
                ,'name': returnResults[0][1] \
                ,'photoLink': returnResults[0][2]} 

    cur.close()
    if con is not None:
        con.close()

    return person

def getDBPersonNoUpdate(email):

    con = connectDB()
    cur = con.cursor()

    SQL = "SELECT PPL_Email, PPL_Name, PPL_PhotoLink  FROM PPL_People WHERE LOWER(PPL_Email) like LOWER(%s)"
    data = (email,)
    cur.execute(SQL, data)
    returnResults = cur.fetchall()

    person={'email': returnResults[0][0] \
        ,'name': returnResults[0][1] \
        ,'photoLink': returnResults[0][2]} 

    return person


def getDBEventAttendees(eventid):
    con = connectDB()
    cur = con.cursor()

    SQL = "SELECT PPL_Email, PPL_Name, PPL_PhotoLink, INV_Status FROM INV_Invitees inner join PPL_People ON  LOWER(INV_PPL_Email)=LOWER(PPL_Email) WHERE INV_EVE_EventID = %s"
    data = (eventid,)
    cur.execute(SQL, data)
    attendees = cur.fetchall()
    attendeeList = []
    for attendee in attendees:
        attendeeDetails={'email': attendee[0] \
                        ,'name': attendee[1] \
                        ,'photoLink': attendee[2] \
                        ,'status': attendee[3]} 
        attendeeList.append(attendeeDetails)

    cur.close()
    if con is not None:
        con.close()

    return attendeeList


def getDBEventDetails(eventid,timezone):
    con = connectDB()
    cur = con.cursor()
    

    SQL = "SELECT EVE_location, EVE_eventtitle, EVE_Description, EVE_Minutes, EVE_StartRange, EVE_EndRange, EVE_dateandtime, EVE_googleID FROM EVE_Events WHERE EVE_EventID = %s"
    data = (eventid,)
    cur.execute(SQL, data)
    eventInfo = cur.fetchall()
    eventInfo = eventInfo[0]


    # Convert UTC times to local times for display
    endRange=str(eventInfo[5]+timedelta(hours=-int(str(timezone))/60))
    startRange=str(eventInfo[4]+timedelta(hours=-int(str(timezone))/60))
    ScheduleTime=None
    if eventInfo[6] != None:
        ScheduleTime=eventInfo[6]+timedelta(hours=-int(str(timezone))/60)

    eventDetails = {
            'eventid': eventid
            ,'place': eventInfo[0]
            ,'eventtitle': eventInfo[1]
            ,'description': eventInfo[2]
            ,'meetingLength': eventInfo[3]
            ,'startdate': startRange
            ,'enddate': endRange
            ,'dateandtime': ScheduleTime # deal with as a datetime data type
            ,'googleid': eventInfo[7]
            }

    cur.close()
    if con is not None:
        con.close()

    return eventDetails

def updateDBAttendeesNeedAction(eventid):

    # connect to database
    con = connectDB()
    cur = con.cursor()

    cur.execute("UPDATE INV_Invitees SET INV_Status='needsAction' WHERE INV_EVE_EventID=%s",(eventid,))
    con.commit()

    cur.close()
    if con is not None:
        con.close()

    return eventid

def updateDBEventDeleteAttendee(eventid,AttendeeEmail):
    # connect to database
    con = connectDB()
    cur = con.cursor()

    cur.execute("DELETE FROM INV_Invitees WHERE INV_EVE_EventID=%s AND LOWER(INV_PPL_Email)=LOWER(%s) "\
        ,(eventid, AttendeeEmail))
    con.commit()

    cur.close()
    if con is not None:
        con.close()

    return eventid

def updateDBEventAddAttendee(eventid,NewAttendeeEmail):
    # connect to database
    con = connectDB()
    cur = con.cursor()
    
    # Don't add if invitee is already added
    SQL = "select * from INV_Invitees where INV_EVE_EventID=%s and LOWER(INV_PPL_Email)=LOWER(%s)"
    data = (eventid,NewAttendeeEmail,)
    cur.execute(SQL, data)
    returnResults = cur.fetchall()
    if len(returnResults)>0:
        return eventid
    

    # Add the attendee email to the event, thus joining table with PPL_People...
    cur.execute("INSERT INTO INV_Invitees(INV_EVE_EventID,INV_PPL_Email,INV_Status) VALUES (%s,LOWER(%s),'needsAction')"\
        ,(eventid, NewAttendeeEmail))
    con.commit()

    # Add this person to the PPL_People table if not already there...
    SQL = "SELECT *  FROM PPL_People WHERE LOWER(PPL_Email) like LOWER(%s)"
    data = (NewAttendeeEmail,)
    cur.execute(SQL, data)
    returnResults = cur.fetchall()

    if len(returnResults)==0:
        # Not in PPL_People. Use email for name
        data = (NewAttendeeEmail,NewAttendeeEmail,UNKNOWN_PERSON_PHOTO_URL)
        cur.execute("INSERT INTO PPL_People(PPL_Email, PPL_Name, PPL_PhotoLink) VALUES (LOWER(%s),LOWER(%s), %s)",data)
        con.commit()

    cur.close()
    if con is not None:
        con.close()

    return eventid

def updateDBEventSlectedTime(EventDateTime):

    # connect to database
    con = connectDB()
    cur = con.cursor()

    # Convert to UTC (add timezone offset)
    dtStartRange = datetime.strptime(str(EventDateTime['StartRange']),'%Y-%m-%dT%H:%M')+timedelta(hours=int(EventDateTime['timezone'])/60)
    dtEndRange = datetime.strptime(str(EventDateTime['EndRange']),'%Y-%m-%dT%H:%M')+timedelta(hours=int(EventDateTime['timezone'])/60)

    # format must match SuggestedTimesHTML
    #dtScheduledTime = datetime.strptime(str(EventDateTime['DateAndTime']),'%Y-%m-%d %H:%M')+timedelta(hours=int(EventDateTime['timezone'])/60)
    dtScheduledTime = datetime.strptime(str(EventDateTime['DateAndTime']),'%Y-%m-%d %I:%M %p')+timedelta(hours=int(EventDateTime['timezone'])/60)

    # UTC String version
    sStartRange = str(dtStartRange)
    sEndRange = str(dtEndRange)
    sScheduledTime = str(dtScheduledTime)

    # insert event details into database. All datetimes are saved in UTC.
    cur.execute("UPDATE EVE_Events SET EVE_Minutes=%s, EVE_DateAndTime=%s,  EVE_StartRange=%s, EVE_EndRange=%s WHERE EVE_EventID=%s"\
        , (EventDateTime['Minutes'], sScheduledTime,sStartRange, sEndRange, EventDateTime['eventid']))
    con.commit()

    cur.close()
    if con is not None:
        con.close()

    return EventDateTime['eventid']

def updateDBEvent(Event):

    # connect to database
    con = connectDB()
    cur = con.cursor()

    # insert event details into database
    cur.execute("UPDATE EVE_Events SET EVE_Eventtitle=%s, EVE_Description=%s, EVE_Location=%s, EVE_Minutes=%s WHERE EVE_EventID=%s"\
        , (Event['title'], Event['description'],Event['place'], Event['meetingLength'], Event['eventid']))
    con.commit()

    cur.close()
    if con is not None:
        con.close()

    return Event['eventid']


def createNewDBEvent(Event):

    # connect to database
    con = connectDB()
    cur = con.cursor()
    
    # creating new eventid for new event
    cur.execute("SELECT max(EVE_EventID)+1 FROM EVE_Events")
    maxEventID = cur.fetchall()
    maxEventID = maxEventID[0][0]

    # insert event details into database
    cur.execute("INSERT INTO EVE_Events (EVE_EventID, EVE_Eventtitle, EVE_Description, EVE_Owner_PPL_Email, EVE_Minutes, EVE_StartRange, EVE_EndRange, EVE_Location) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"\
        , (maxEventID, Event['eventtitle'], Event['description'], Event['ownerEmail'], Event['meetingLength'], Event['startdate'], Event['enddate'], Event['place']))
    con.commit()

    cur.close()
    if con is not None:
        con.close()

    return maxEventID

def getDBUsersEventIDs(user):
    con = connectDB()
    cur = con.cursor()
    
    SQL = "SELECT EVE_EventID FROM EVE_Events WHERE EVE_Owner_PPL_Email = %s ORDER BY EVE_EventID desc limit 10"
    data = (user,)
    cur.execute(SQL, data)
    eventIDs = cur.fetchall()
    eventIDsList = []
    for eventID in eventIDs:
        eventIDsList.append(eventID[0])
    cur.close()
    if con is not None:
        con.close()

    return eventIDsList

def updateDBGoogleID(eventid, googleid):
    con = connectDB()
    cur = con.cursor()
    
    # UPDATE GOOGLE INFORMATION
    cur.execute("UPDATE EVE_Events SET EVE_googleID=%s WHERE EVE_EventID=%s"\
        , (googleid, eventid))
    con.commit()

    cur.close()
    if con is not None:
        con.close()

def updateDBDeleteEvent(eventid):
    con = connectDB()
    cur = con.cursor()
    
    # Delete invitees
    cur.execute("DELETE FROM INV_Invitees WHERE INV_EVE_EventID=%s"\
        , (eventid,))
    con.commit()

    # Delete the event
    cur.execute("DELETE FROM EVE_Events WHERE EVE_EventID=%s"\
        , (eventid,))
    con.commit()

    cur.close()
    if con is not None:
        con.close()

# Google Code
#-------------
def attendee_status(EVE_googleID):

    credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])

    service = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    event = service.events().get(calendarId='primary', eventId=EVE_googleID).execute()

    attendees = {}
    for attendee in event['attendees']:
        attendees[attendee.get('email')] = attendee.get('responseStatus')

    return attendees


def makeGoogleEvent(eventid):

    # get service 
    credentials = google.oauth2.credentials.Credentials(
            **flask.session['credentials'])
    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    calendar = service.calendars().get(calendarId='primary').execute()

    eventdetails = getDBEventDetails(eventid,0) # get all datetimes as UTC (no timezone offset)
    attendeeList = getDBEventAttendees(eventid)

    # time format: '2019-01-02T11:00:00-05:00'
    # endtime = endtime[0:9] + '-' + endtime[11:15]
    # t = datetime.strptime(endtime, '%Y-%m-%d-%H:%M')
    # t = time.mktime(time.strptime(endtime, '%Y-%m-%d-%H:%M'))


    listAttendees=[{"email":str(calendar['id'])}]   # first attendee is the interactive user
    AttendeeList = getDBEventAttendees(eventid)

    for Attendee in AttendeeList:
        listAttendees.append({"email":str(Attendee["email"])})

    # endtime = str(time.strptime(str(eventdetails[dateandtime]), '%Y-%m-%d') + timedelta(minutes=1)) +":00.000-05:00"
    end = eventdetails['dateandtime'] + timedelta(minutes=int(eventdetails['meetingLength']))
    # endtime = timeAlg.convertToRFC(end.utcfromtimestamp(0))
    starttime = str(eventdetails['dateandtime'])[0:10]+"T"+str(eventdetails['dateandtime'])[11:16]
    endtime = str(end)[0:10]+"T"+str(end)[11:16]
    # event = {
    #   'summary': eventdetails['eventtitle'],
    #   'location': eventdetails['place'],
    #   'description': eventdetails['description'],
    #   'start': {
    #     'dateTime': starttime + ":00-05:00",  # '2019-01-02T11:00:00-05:00'
    #     'timeZone': 'America/New_York',
    #   },
    #   'end': {
    #     'dateTime': endtime + ":00-05:00",
    #     'timeZone': 'America/New_York',
    #   },
    #   'attendees': listAttendees
    # }

    # All datetimes are saved in the database as UTC. Schedule the event using UTC
    # The events will showup on peoples calendars for their google-calendar-timezones. Times will
    # showup in Timely Tiger in the browser timezone
    event = {
      'summary': eventdetails['eventtitle'],
      'location': eventdetails['place'],
      'description': eventdetails['description'],
      'start': {
        'dateTime': starttime + ":00",  # '2019-01-02T11:00:00-05:00'
        'timeZone': 'UTC',
      },
      'end': {
        'dateTime': endtime + ":00",
        'timeZone': 'UTC',
      },
      'attendees': listAttendees
    }

    event = service.events().insert(calendarId='primary', body=event, sendUpdates='none').execute() # changed all to none
    # print 'Event created: %s' % (event.get('htmlLink'))
    googleid = event.get('id')

    updateDBGoogleID(eventid, googleid)

def UnscheduleGoogleEvent(eventid):

    EventDetails = getDBEventDetails(eventid,0)
    googleID = EventDetails['googleid']

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])
    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    service.events().delete(calendarId='primary', eventId=googleID).execute()

    # Reset information in database
    updateDBGoogleID(eventid, None)
    updateDBAttendeesNeedAction(eventid)





    
# if __name__ == '__main__':
#     # if len(argv) != 2:
#     #     print 'Usage: ' + argv[0] + ' port'
#     #     exit(1)
#     #run(host='0.0.0.0', port=argv[1], debug=True)
#     # run(host='0.0.0.0', port=argv[1], debug=False)

#     os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

#     # Specify a hostname and port that are set as a valid redirect URI
#     # for your API project in the Google API Console.
#     app.run('localhost', 8080, debug=True)

if os.environ.get('APP_LOCATION') == 'heroku':
    app.run('0.0.0.0', int(os.environ.get("PORT", 5000)))  # ssl_context='adhoc'
else:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run('localhost', 8080, debug=True)
    #app.run('localhost', 8080, debug=False)






