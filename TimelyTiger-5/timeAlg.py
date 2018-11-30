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

    print timeinfo
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

    return partition(mylist, meetingLength)

    meetingoptions = list(); 
    for interval in mylist:
        if len(interval[2]) >= 2:
            timeoption = ''
            
            start = gmtime(interval[0])
            sdt = str(datetime.fromtimestamp(mktime(start)).strftime("%Y-%m-%d %H:%M"))
            end = gmtime(interval[1])
            edt = str(datetime.fromtimestamp(mktime(end)).strftime("%Y-%m-%d %H:%M"))

            # time += convertToRFC(interval[0]) + ', ' + convertToRFC(interval[1]) + ', ' + str(interval[2])
            # time = str(convertToRFC(interval[0])) + ', ' + str(convertToRFC(interval[1])) + ', ' + str(interval[2])
            timeoption += sdt  + '  to  ' + edt + ', ' + str(interval[2])
            meetingoptions.append(timeoption)


    # return meetingoptions

def partition(freelist, meetingLength):
    pdb.set_trace()
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

    pdb.set_trace()

    return meetingoptions





# if __name__ == '__main__':

#     dumped = '{"timeMax": "2018-12-03T04:59:59.000Z", "kind": "calendar#freeBusy", "calendars": {"csedillo@princeton.edu": {"busy": [{"start": "2018-12-02T15:00:00-05:00", "end": "2018-12-02T16:00:00-05:00"}]}, "dalelee@princeton.edu": {"busy": [{"start": "2018-12-02T15:00:00-05:00", "end": "2018-12-02T21:00:00-05:00"}]}}, "timeMin": "2018-12-02T05:00:00.000Z"}'
#     loadInfo = json.loads(dumped)
#     people = ['dalelee@princeton.edu', 'csedillo@princeton.edu']
#     starttime = 1543726800.0
#     endtime = 1543726800.0
#     print endtime
#     print timeAlgorithm(loadInfo, people, starttime, endtime)





