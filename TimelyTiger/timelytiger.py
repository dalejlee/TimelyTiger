#!/usr/bin/env python

#-----------------------------------------------------------------------
# timelytiger.py
# Author: Cody Sedillo
#-----------------------------------------------------------------------

from sys import argv
#from database import Database
from time import localtime, asctime, strftime
from urllib import quote_plus
from bottle import route, request, response, error, redirect, run
from bottle import template, TEMPLATE_PATH

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

    yEmail = remove_none(request.query.get('yEmail'))
    pEmail = remove_none(request.query.get('pEmail'))
    date = remove_none(request.query.get('date'))
    time = remove_none(request.query.get('time'))
    place = remove_none(request.query.get('place'))

    response.set_cookie('yEmail', yEmail)
    response.set_cookie('pEmail', pEmail)
    response.set_cookie('date', date)
    response.set_cookie('time', time)
    response.set_cookie('place', place)

    #Store form data in an Event object here
 
    #Update the database here
    
    templateInfo = {
        'prevyEmail': yEmail,
        'prevpEmail': pEmail,
        'prevDate': date,
        'prevTime': time,
        'prevPlace': place}
    
    return template('eventpage.tpl', templateInfo)
    
@route('/showTimes')
def showTimes():
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
    
    yEmail = request.get_cookie('yEmail')
    pEmail = request.get_cookie('pEmail')
    date = request.get_cookie('date')
    time = request.get_cookie('time')
    place = request.get_cookie('place')

    templateInfo = {
        'time': time,
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
