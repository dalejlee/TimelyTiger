#!/usr/bin/env python

#-----------------------------------------------------------------------
# timelytiger.py
# Author: Cody Sedillo, Dale Lee
#-----------------------------------------------------------------------

from sys import argv
#from database import Database
from time import localtime, asctime, strftime
from urllib import quote_plus
from bottle import route, request, response, error, redirect, run
from bottle import template, TEMPLATE_PATH
import pdb               # Python debugger
import psycopg2 as p

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

TEMPLATE_PATH.insert(0, '')

@route('/')
@route('/Home')
def homePage():
    
    templateInfo = {}
    
    return template('homepage.tpl', templateInfo)
    

@route('/eventForm')
def eventForm():
    eventName = remove_none(request.get_cookie('eventName'))
    yEmail = remove_none(request.get_cookie('yEmail'))
    pEmail = remove_none(request.get_cookie('pEmail'))
    date = remove_none(request.get_cookie('date'))
    time = remove_none(request.get_cookie('time'))
    place = remove_none(request.get_cookie('place'))
    #Store form data in an Event object here
    eventName = 'study session'
    yEmail = 'person1@gmail.com'
    pEmail = 'person2@gmail.com'
    date = '01/01/2019'
    time = '30'
    place = 'my room'
    
    templateInfo = {
        'yEmail': yEmail,
        'pEmail': pEmail,
        'date': date,
        'time': time,
        'place': place}
    
    return template('eventpage.tpl', templateInfo)
    
@route('/showTimes')
def showTimes():

    yEmail = remove_none(request.query.get('yEmail'))
    pEmail = remove_none(request.query.get('pEmail'))
    date = remove_none(request.query.get('date'))
    time = remove_none(request.query.get('time'))
    place = remove_none(request.query.get('place'))
    eventName = 'study session'

    response.set_cookie('yEmail', yEmail)
    response.set_cookie('pEmail', pEmail)
    response.set_cookie('date', date)
    response.set_cookie('time', time)
    response.set_cookie('place', place)

    if eventName is None:
        eventName = 'study session'
    if yEmail is None:
        yEmail = 'person1@gmail.com'
    if pEmail is None:
        pEmail = 'person2@gmail.com'
    if date is None:
        date = '01/01/2019'
    if time is None:
        time = '30'
    if place is None:
        place = 'my room'

    #Update the database here
    con=p.connect(dbname="sample_db", user="postgres", host="localhost", port="5431")
    cur=con.cursor()

    debug = 'test'
    # cur.execute(InsertNewSQL)
    # pdb.set_trace()
    cur.execute("SELECT max(EVE_EventID)+1 FROM EVE_Events")
    maxEventID = cur.fetchall()
    print "maxEventID is "
    print maxEventID
    maxEventID = maxEventID[0][0]

    # cur.execute("INSERT INTO EVE_Events(EVE_EventID, EVE_Eventtitle) VALUES(%s, %s)", (maxEventID, eventName))
    #cur.execute("INSERT INTO EVE_Events (EVE_EventID, EVE_hostEmail, EVE_partnerEmail, EVE_StartRange, EVE_EndRange, EVE_Minutes, EVE_Location) VALUES(%s, %s, %s, %s, %s, %s, %s)", (maxEventID[0][0], yEmail, pEmail, date, date, time, place))
    cur.execute("INSERT INTO EVE_Events (EVE_EventID, EVE_Eventtitle, EVE_hostEmail, EVE_partnerEmail, EVE_Location) VALUES(%s, %s, %s, %s, %s)", (maxEventID, eventName, yEmail, pEmail, place))
    con.commit()
    print 'got here'

    cur.close()
    if con is not None:
        con.close()
        print('Database connection closed.')
    
    #Fetch Google Calendar data; generate list of times    
    list_times = ["3:00pm", "7:00pm", "8:00pm"]
    num_times = len(list_times)

    templateInfo = {
        'times': list_times,
        'num_times': num_times}
    return template('timespage.tpl', templateInfo)

@route('/eventDetails')
def eventDetails():
    #Add selected time to previous event
    time = request.query.time
    
    yEmail = remove_none(request.get_cookie('yEmail'))
    pEmail = remove_none(request.get_cookie('pEmail'))
    date = remove_none(request.get_cookie('date'))
    time = request.get_cookie('time')
    place = remove_none(request.get_cookie('place'))

    con=p.connect(dbname="sample_db", user="postgres", host="localhost", port="5431")
    cur=con.cursor()
    cur.execute("SELECT EVE_eventtitle FROM EVE_Events WHERE EVE_eventid = 101")
    eventtitle=cur.fetchall()

    cur.execute("SELECT EVE_location FROM EVE_Events WHERE EVE_eventid = 101")
    # pdb.set_trace()
    place=cur.fetchall()

    cur.close()

    if con is not None:
        con.close()
        print('Database connection closed.')


    templateInfo = {
        'eventtitle': eventtitle,
        'yEmail': yEmail,
        'pEmail': pEmail,
        'date': date,
        'time': time,
        'place': place}
    return template('eventdetails.tpl', templateInfo)
    
@error(404)
def notFound(error):
    return 'Not found'

# TODO: Handle error cases
    
if __name__ == '__main__':
    if len(argv) != 2:
        print 'Usage: ' + argv[0] + ' port'
        exit(1)
    run(host='0.0.0.0', port=argv[1], debug=True)
