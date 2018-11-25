# -*- coding: utf-8 -*-

import os
import flask
from flask import request
import requests

from bottle import template, TEMPLATE_PATH

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

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

TEMPLATE_PATH.insert(0, '')

@app.route('/')
def index():
    
    templateInfo = {}

    # button in homepage.tpl redirects to authentication until i find a better solution
    return template('homepage.tpl', templateInfo)

@app.route('/eventForm')
def eventForm():
    yEmail = remove_none(request.cookies.get('yEmail'))
    pEmail = remove_none(request.cookies.get('pEmail'))
    date = remove_none(request.cookies.get('date'))
    time = remove_none(request.cookies.get('time'))
    place = remove_none(request.cookies.get('place'))
    
    templateInfo = {
        'yEmail': yEmail,
        'pEmail': pEmail,
        'date': date,
        'time': time,
        'place': place}
    
    return template('eventpage.tpl', templateInfo)

@app.route('/showTimes')
def showTimes():

    yEmail = remove_none(request.args.get('yEmail'))
    pEmail = remove_none(request.args.get('pEmail'))
    date = remove_none(request.args.get('date'))
    time = remove_none(request.args.get('time'))
    place = remove_none(request.args.get('place'))

    # cookies broke 
    #response.set_cookie('yEmail', yEmail)
    #response.set_cookie('pEmail', pEmail)
    #response.set_cookie('date', date)
    #response.set_cookie('time', time)
    #response.set_cookie('place', place)

    # apparently this is how flask returns templates?
    #resp = make_response(render_template('readcookie.html'))
    #resp.set_cookie('userID', user)
    #return resp

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    calendar = service.calendars().get(calendarId='primary').execute()
    # Leave commented while testing other features
    #create_event(service)
    email = calendar['id']
    timeMin = date
    timeMin += "T00:00:00.000Z"
    timeMax = date
    timeMax += "T23:59:59.000Z"

    # Call the Calendar API, freebusy for the month of November
    body = {
          "timeMin": timeMin,
          "timeMax": timeMax,
          "timeZone": "America/New_York",
          "items": [{"id": yEmail},
                    {"id": pEmail}]
    }
    eventsResult = service.freebusy().query(body=body).execute()
    flask.session['credentials'] = credentials_to_dict(credentials)
    return flask.jsonify(**eventsResult)

    # Program does not reach beyond this point
    #Fetch Google Calendar data; generate list of times    
    list_times = [eventsResult]
    num_times = len(list_times)

    templateInfo = {
        'times': list_times,
        'num_times': num_times}
    return template('timespage.tpl', templateInfo)

@app.route('/eventDetails')
def eventDetails():
    #Add selected time to previous event
    time = request.args['time']
    
    yEmail = remove_none(request.cookies.get('yEmail'))
    pEmail = remove_none(request.cookies.get('pEmail'))
    date = remove_none(request.cookies.get('date'))
    place = remove_none(request.cookies.get('place'))

    templateInfo = {
        'yEmail': yEmail,
        'pEmail': pEmail,
        'date': date,
        'time': time,
        'place': place}
    return template('eventdetails.tpl', templateInfo)

## SHouldn't be called by current code at all
@app.route('/test')
def test_api_request():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    calendar = service.calendars().get(calendarId='primary').execute()
    email = calendar['id']

    # Call the Calendar API
    body = {
          "timeMin": "2018-11-01T00:00:00.000Z",
          "timeMax": "2018-11-30T00:00:00.000Z",
          "timeZone": "America/New_York",
          "items": [{"id": 'codyunit@gmail.com'},
                    {"id": 'csedillo@princeton.edu'},
                    {"id": 'dalelee@princeton.edu'}]
    }
    eventsResult = service.freebusy().query(body=body).execute()
      #cal_dict = eventsResult[u'calendars']
      #for cal_name in cal_dict:
      #  print(cal_name, cal_dict[cal_name])

      # Save credentials back to session in case access token was refreshed.
      # ACTION ITEM: In a production app, you likely want to save these
      #              credentials in a persistent database instead.
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect('/eventForm')

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

if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #     When running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  app.run('localhost', 8080, debug=True)
