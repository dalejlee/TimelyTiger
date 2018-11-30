#!/usr/bin/env python

#-----------------------------------------------------------------------
# timelytiger.py
# Author: Cody Sedillo, Dale Lee
#-----------------------------------------------------------------------

from sys import argv
#from database import Database
from time import localtime, asctime, strftime
from urllib import quote_plus
# from bottle import route, request, response, error, redirect, run
from bottle import template, TEMPLATE_PATH
import pdb               # Python debugger pdb.set_trace()
import psycopg2 as p

import os
import flask
from flask import request
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import timeAlg
import time
import json

# Processes entry in preparation for templateInfo
def remove_none(entry):
    if entry == None:
        return ''
    else:
        return entry

# Processes entry in preparation for database search    
def parse_entry(entry):
    if entry == '':
        return '%'
    else:
        return '%' + entry.replace('%','\%').replace('_','\_') + '%'

##################### ADDED FROM CODY'S test.py #####################


def credentials_to_dict(credentials):
    return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def create_event(service):
    event = {
      'summary': 'Timely Tiger test event',
      'location': 'Princeton University',
      'description': 'I hope this works',
      'start': {
        'dateTime': '2018-11-25T1:00:00-05:00',
        'timeZone': 'America/Los_Angeles',
      },
      'end': {
        'dateTime': '2018-11-25T02:00:00-05:00',
        'timeZone': 'America/Los_Angeles',
      },
      'attendees': [
        {'email': 'dalelee@princeton.edu'},
      ]
    }

    event = service.events().insert(calendarId='primary', body=event, sendUpdates='all').execute()
    print 'Event created: %s' % (event.get('htmlLink'))

    

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.

CLIENT_SECRETS_FILE = "client_secret_899885585030-j4o4conctbnpmke5qqjekejufeo8lb70.apps.googleusercontent.com.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ["https://www.googleapis.com/auth/userinfo.email",
          "https://www.googleapis.com/auth/userinfo.profile",
          "https://www.googleapis.com/auth/calendar",
          "https://www.googleapis.com/auth/plus.me"]
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'

app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See http://flask.pocoo.org/docs/0.12/quickstart/#sessions.
app.secret_key = 'QUiXw4DPDmzZl7JKFqBoTWuI'


##################### ADDED FROM CODY'S test.py #####################

TEMPLATE_PATH.insert(0, '')


@app.route('/')
def index():
    templateInfo = {}
    
    return template('homepage.tpl', templateInfo)
    

@app.route('/eventForm')
def eventForm():

    eventName = remove_none(request.args.get('eventName'))
    yEmail = remove_none(request.args.get('yEmail'))
    pEmail = remove_none(request.args.get('pEmail'))
    meetingLength = remove_none(request.args.get('meetingLength'))
    startdate = remove_none(request.args.get('startdate'))
    enddate = remove_none(request.args.get('enddate'))
    place = remove_none(request.args.get('place'))

    ## cookies broken
    # response.set_cookie('eventName', eventName)
    # response.set_cookie('yEmail', yEmail)
    # response.set_cookie('pEmail', pEmail)
    # response.set_cookie('meetingLength', meetingLength)
    # response.set_cookie('startdate', startdate)
    # response.set_cookie('enddate', enddate)
    # response.set_cookie('place', place)

    #Store form data in an Event object here

    # eventName = 'study session'
    # yEmail = 'person1@gmail.com'
    # pEmail = 'person2@gmail.com'
    # date = '01/01/2019'
    # time = '30'
    # place = 'my room'
    
    templateInfo = {
        'eventName': eventName,
        'yEmail': yEmail,
        'pEmail': pEmail,
        'meetingLength': meetingLength,
        'startdate': startdate,
        'enddate': enddate,
        'place': place}
    
    return template('eventpage.tpl', templateInfo)
    
@app.route('/showTimes')
def showTimes():

    eventName = remove_none(request.args.get('eventName'))
    yEmail = remove_none(request.args.get('yEmail'))
    pEmail = remove_none(request.args.get('pEmail'))
    meetingLength = remove_none(request.args.get('meetingLength'))
    startdate = remove_none(request.args.get('startdate'))
    enddate = remove_none(request.args.get('enddate'))
    place = remove_none(request.args.get('place'))


    # response.set_cookie('eventName', eventName)
    # response.set_cookie('yEmail', yEmail)
    # response.set_cookie('pEmail', pEmail)
    # response.set_cookie('meetingLength', meetingLength)
    # response.set_cookie('startdate', startdate)
    # response.set_cookie('enddate', enddate)
    # response.set_cookie('place', place)

    # if eventName is None:
    #     eventName = 'study session'
    # if yEmail is None:
    #     yEmail = 'person1@gmail.com'
    # if pEmail is None:
    #     pEmail = 'person2@gmail.com'
    # if date is None:
    #     date = '01/01/2019'
    # if time is None:
    #     time = '30'
    # if place is None:
    #     place = 'my room'

    #Update the database here
    con=p.connect(dbname="sample_db", user="postgres", host="localhost", port="5431")
    cur=con.cursor()

    debug = 'test'
    # cur.execute(InsertNewSQL)

    cur.execute("SELECT max(EVE_EventID)+1 FROM EVE_Events")
    maxEventID = cur.fetchall()
    print "maxEventID is "
    print maxEventID
    maxEventID = maxEventID[0][0]

    # cur.execute("INSERT INTO EVE_Events(EVE_EventID, EVE_Eventtitle) VALUES(%s, %s)", (maxEventID, eventName))
    #cur.execute("INSERT INTO EVE_Events (EVE_EventID, EVE_hostEmail, EVE_partnerEmail, EVE_StartRange, EVE_EndRange, EVE_Minutes, EVE_Location) VALUES(%s, %s, %s, %s, %s, %s, %s)", (maxEventID[0][0], yEmail, pEmail, date, date, time, place))
    cur.execute("INSERT INTO EVE_Events (EVE_EventID, EVE_Eventtitle, EVE_hostEmail, EVE_partnerEmail, EVE_Minutes, EVE_StartRange, EVE_EndRange, EVE_Location) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)", (maxEventID, eventName, yEmail, pEmail, meetingLength, startdate, enddate, place))
    con.commit()
    print 'got here'

    cur.close()
    if con is not None:
        con.close()
        print('Database connection closed.')
    


##################### ADDED FROM CODY'S test.py #####################

# Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    calendar = service.calendars().get(calendarId='primary').execute()
    # Leave commented while testing other features
    #create_event(service)
    email = calendar['id']
    timeMin = startdate
    timeMin += "T00:00:00.000-05:00"
    timeMax = enddate
    timeMax += "T23:59:59.000-05:00"
    # Call the Calendar API, freebusy for the month of November
    body = {
          "timeMin": timeMin,
          "timeMax": timeMax,
          "timeZone": "America/New_York",
          "items": [{"id": yEmail},
                    {"id": pEmail}]
    }
    eventsResult = service.freebusy().query(body=body).execute()

    dumped = json.dumps(eventsResult)
    print dumped

    loadInfo = json.loads(dumped)
    print loadInfo



    #  flask.session['credentials'] = credentials_to_dict(credentials)
    # json = flask.jsonify(**eventsResult)


    # data = json.json()
    
    # f = open("jsonfile.json", "w")
    # f.write(str(eventsResult))

    # print 'here !!!!!!!'
    # print json
    # Program does not reach beyond this point
    #Fetch Google Calendar data; generate list of times    
    # list_times = [eventsResult]
    # num_times = len(list_times)

    print startdate
    print enddate

    people = [yEmail, pEmail]
    startdate = time.mktime(time.strptime(startdate, '%Y-%m-%d'))
    enddate = time.mktime(time.strptime(enddate, '%Y-%m-%d'))

    list_times = timeAlg.timeAlgorithm(loadInfo, people, startdate, enddate, meetingLength)
    num_times = len(list_times)
    print list_times
##################### ADDED FROM CODY'S test.py #####################



    #Fetch Google Calendar data; generate list of times    
    # list_times = ["3:00pm", "7:00pm", "8:00pm"]
    # num_times = len(list_times)

    templateInfo = {
        'times': list_times,
        'num_times': num_times}
    return template('timespage.tpl', templateInfo)


@app.route('/eventDetails')
def eventDetails():

    #Add selected time to previous event
    time = request.args['time']
    
    # yEmail = remove_none(request.get_cookie('yEmail'))
    # pEmail = remove_none(request.get_cookie('pEmail'))
    # date = remove_none(request.get_cookie('date'))
    # time = request.get_cookie('time')
    # place = remove_none(request.get_cookie('place'))

    con=p.connect(dbname="sample_db", user="postgres", host="localhost", port="5431")
    cur=con.cursor()

    cur.execute("SELECT max(EVE_EventID)+1 FROM EVE_Events")
    maxEventID = cur.fetchall()
    print "maxEventID is "
    print maxEventID
    maxEventID = maxEventID[0][0]
    print "maxEventID again"
    print maxEventID
    currentMaxEventID = int(maxEventID - 1)
    print currentMaxEventID
    val = int(160)

 
    # cur.execute("SELECT EVE_eventtitle FROM EVE_Events WHERE EVE_eventid = 100")
    cur.execute("SELECT EVE_eventtitle FROM EVE_Events WHERE EVE_EventID = (SELECT max(EVE_EventID) FROM EVE_Events)")
    eventtitle=cur.fetchall()

    cur.execute("SELECT EVE_location FROM EVE_Events WHERE EVE_eventid = (SELECT max(EVE_EventID) FROM EVE_Events)")

    place=cur.fetchall()
    cur.execute("SELECT EVE_EventID, EVE_Eventtitle, EVE_hostEmail, EVE_partnerEmail, EVE_Minutes, EVE_StartRange, EVE_EndRange, EVE_Location from EVE_Events WHERE EVE_eventid = (SELECT max(EVE_EventID) FROM EVE_Events)") # FIX SO THAT ID IS PASSED THROUGH COOKIES
    # cur.execute("SELECT EVE_EventID, EVE_Eventtitle, EVE_hostEmail, EVE_partnerEmail, EVE_Minutes, EVE_StartRange, EVE_EndRange, EVE_Location from EVE_Events WHERE EVE_eventid = (val)")
    eventInfo = cur.fetchall()
    eventInfo = eventInfo[0]
    print "event info is: " 
    print eventInfo
    eventid = eventInfo[0]
    eventtitle = eventInfo[1]
    yEmail = eventInfo[2]
    pEmail = eventInfo[3]
    meetingLength = eventInfo[4]
    startdate = eventInfo[5]
    enddate = eventInfo[6]
    place = eventInfo[7]
    dateandtime = time

    # cur.execute("SELECT EVE_hostEmail FROM EVE_Events WHERE EVE_eventid =" + str(maxEventID))
    # yEmail = cur.fetchall()

    # cur.execute("SELECT EVE_partnerEmail FROM EVE_Events WHERE EVE_eventid = %s" + str(maxEventID))
    # pEmail=cur.fetchall()

    cur.close()

    if con is not None:
        con.close()
        print('Database connection closed.')


    templateInfo = {
        'eventid': eventid,
        'eventtitle': eventtitle,
        'yEmail': yEmail,
        'pEmail': pEmail,
        'meetingLength': meetingLength,
        'startdate': startdate,
        'enddate': enddate,
        'dateandtime': dateandtime,
        'place': place}
    return template('eventdetails.tpl', templateInfo)
    
# @app.error(404)
# def notFound(error):
#     return 'Not found'

# TODO: Handle error cases

##################### ADDED FROM CODY'S test.py #####################
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
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect('/eventForm')

##################### ADDED FROM CODY'S test.py #####################


    
if __name__ == '__main__':
    # if len(argv) != 2:
    #     print 'Usage: ' + argv[0] + ' port'
    #     exit(1)
    # run(host='0.0.0.0', port=argv[1], debug=True)

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    app.run('localhost', 8080, debug=True)



