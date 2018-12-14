import json
import pdb
import time
from time import gmtime, strftime, mktime
from datetime import datetime

def is_free(time, ranges):
    for range in ranges:
        if (range[0] <= time) and (time < range[1]):
            return False;
    return True;

# returns busy times of all people, 
# listing start, end, start, end ... of busy time segments
def createCutoffs(avs, start, end):
    set = {start, end}
    for x in avs:
        for range in x:
            set.add(range[0])
            set.add(range[1])
    cutoffs = list()
    for item in set:
        cutoffs.append(item)
    cutoffs.sort()
    return cutoffs


def checkRanges(cutoffs, avs, users):
    i = 1
    ranges = list()
    while i < len(cutoffs):
        midpoint = float(cutoffs[i] + cutoffs[i-1]) / 2
        people = list()
        index = 0
        while index < len(users):
            if is_free(midpoint, avs[index]):
                people.append(users[index])
            index += 1
        ranges.append([cutoffs[i-1],cutoffs[i],people])
        i+=1
    return ranges

def sortingFunction(item):
    return len(item[2])
    
# returns array of int ranges for times
def dataToAvs(data, user):
    times = list()
    for x in data['calendars'][user]['busy']:
        times.append([convertToSecs(x['start']),convertToSecs(x['end'])])
    return times

def convertToSecs(timeinfo): # mktiny

    t = timeinfo.replace('T', '-')
    t = t[:-6]
    t = str(t)
    t = time.mktime(time.strptime(t, '%Y-%m-%d-%H:%M:%S'))

    ## SUBTRACT 5 HOURS FOR -05:00 TIME (NEED TO FIX)
    t = t - 18000
    return t

    # year = int(time[0:4])
    # month = int(time[5:7])
    # day = int(time[8:10])
    # hour = int(time[11:13])
    # minute = int(time[14:16])
    # seconds = int(time[17:19])
    # return ((year - 1970) * 31540000) + (month * 2628000) + (day * 86400) + (hour * 3600) + (minute * 60) + seconds

def convertToRFC(time):# int -> 2018-11-23T09:30:00-05:00
    year = str((time / 31540000) + 1970)
    time %= 31540000
    month =  time / 2628000
    if month < 10:
        month = '0' + str(month)
    else:
        month = str(month)
    time %= 2628000
    day = time / 86400
    if day < 10:
        day = '0' + str(day)
    else:
        day = str(day)
    time %=  86400
    hour = time / 3600
    if hour < 10:
        hour = '0' + str(hour)
    else:
        hour = str(hour)
    time %=  3600
    minute = time / 60
    if minute < 10:
        minute = '0' + str(minute)
    else:
        minute = str(minute)
    seconds =  time % 60
    return str(year) + '-' + str(month) + '-' + str(day) + 'T' + str(hour) + ':' + str(minute) + ':' + str(seconds) + '-05:00'

# 2018-12-14 06:00, 60  --> 2018-12-14T07:00:00-05:00
def createEndTime(startdate, meetingLength):
    seconds = meetingLength*60
    startdateMod = startdate[0:10] + 'T' + startdate[11:19] + ':00-05:00'

    startdate2 = convertToSecs(startdateMod)
    startdate2 = startdate2 + seconds
    edt = str(datetime.fromtimestamp(mktime(gmtime(startdate2))).strftime("%Y-%m-%d %H:%M"))

    enddateMod = edt[0:10] + 'T' + edt[11:19] + ':00-05:00'
    return enddateMod

def timeAlgorithm(file, people, startTimeRange, endTimeRange, meetingLength):
    # starttime = 1544831400
    # endtime = 1544889000
    starttime = startTimeRange - 18000
    endtime = endTimeRange + 86400 - 18000 # NEED TO FIX: for now just adding the number of seconds in a day to make the endtime inclusive


    avs = list(); # list of busy times, indexed for each person 
    users = list(); # list of host and invitees
    for person in people:
        users.append(person)

    # with open(file) as f:
    #     data = json.load(f)

    for user in users:
        avs.append(dataToAvs(file, user))

    # avs = [[[1543780800, 1543802400]], [[1543780800, 1543784400]]] # replace second algorithm
    
    mylist = checkRanges(createCutoffs(avs,starttime,endtime),avs,users)
    mylist.sort(reverse=True, key=sortingFunction)
    
    return shorten(partitionSeconds((mylist), meetingLength))

    # return meetingoptions

# shortens to most likely times if necessary
def shorten(myList):
    
    if len(myList) <= 10:
        return myList
    completeList = list()
    num_people = myList[0][2]
    total_start_time = 0
    total_items = 0
    for block in myList:
        if block[2] == num_people:
            total_start_time += block[0]
            total_items += 1

    average_start_time = total_start_time / total_items

    for block in myList:
        if block[2] == num_people:
            completeList.append([block[0],block[1],block[2],abs(average_start_time - block[0])])

    completeList.sort(reverse=False, key=betaSortingFunction)
    

    shortenedList = list()
    for block in completeList:
        if len(shortenedList) < 10:
            sdt = str(datetime.fromtimestamp(mktime(gmtime(block[0]))).strftime("%Y-%m-%d %H:%M"))
            shortenedList.append(sdt)

    shortenedList.sort(reverse=True, key=sortingFunction)
    return shortenedList

def betaSortingFunction(item):
    return item[3]

def partition(freelist, meetingLength):
    meetingLength = int(meetingLength) * 60
    meetingoptions = list();
    for freeblock in freelist:
        if len(freeblock[2]) >= 2:
            end = freeblock[1]
            while (end - freeblock[0] >= meetingLength):
                freeblock[1] = freeblock[0] + meetingLength
                timeoption = ''
                
                sdt = str(datetime.fromtimestamp(mktime(gmtime(freeblock[0]))).strftime("%Y-%m-%d %H:%M"))
                edt = str(datetime.fromtimestamp(mktime(gmtime(freeblock[1]))).strftime("%Y-%m-%d %H:%M"))
                timeoption += sdt  # + '  to  ' + edt + ', ' + str(freeblock[2])
                meetingoptions.append(timeoption)

                freeblock[0] += meetingLength


    return meetingoptions

def partitionSeconds(freelist, meetingLength):
    meetingLength = int(meetingLength) * 60
    meetingoptions = list();
    for freeblock in freelist:
        if len(freeblock[2]) >= 2:
            end = freeblock[1]
            while (end - freeblock[0] >= meetingLength):
                freeblock[1] = freeblock[0] + meetingLength
                
                meetingoptions.append([freeblock[0], freeblock[1], freeblock[2]])

                freeblock[0] += meetingLength

    
    return meetingoptions





# if __name__ == '__main__':

#     dumped = '{"timeMax": "2018-12-03T04:59:59.000Z", "kind": "calendar#freeBusy", "calendars": {"csedillo@princeton.edu": {"busy": [{"start": "2018-12-02T15:00:00-05:00", "end": "2018-12-02T16:00:00-05:00"}]}, "dalelee@princeton.edu": {"busy": [{"start": "2018-12-02T15:00:00-05:00", "end": "2018-12-02T21:00:00-05:00"}]}}, "timeMin": "2018-12-02T05:00:00.000Z"}'
#     loadInfo = json.loads(dumped)
#     people = ['dalelee@princeton.edu', 'csedillo@princeton.edu']
#     starttime = 1543726800.0
#     endtime = 1543726800.0
#     print endtime
#     print timeAlgorithm(loadInfo, people, starttime, endtime)





