from time import gmtime, strptime, mktime
from datetime import datetime


#------------------------------------------------------------------------------------------#
# Main program logic. Returns list of free times, partitioned by meeting_length.
#------------------------------------------------------------------------------------------#
def timeAlgorithm(file, people, start_date, end_date, meeting_length, offset, limit=12):
    # date format: u'2019-01-05T09:16'
    start_date = str(start_date)
    start_time = mktime(strptime(start_date, '%Y-%m-%dT%H:%M'))
    start_hour = int(start_date[11:13]) * 3600
    start_minute = int(start_date[14:16]) * 60
    start_of_day = start_time - start_hour - start_minute

    end_date = str(end_date)
    end_time = mktime(strptime(end_date, '%Y-%m-%dT%H:%M'))
    end_hour = int(end_date[11:13]) * 3600
    end_minute = int(end_date[14:16]) * 60
    start_of_end = end_time - end_hour - end_minute
    
    # List of busy times, indexed for each person 
    avs = list() 
    for person in people:
        avs.append(dataToAvs(file, person, offset))

    # Convert busy times to free times
    free_list = checkRanges(createCutoffs(avs,start_time,end_time),avs,people)
    free_list.sort(reverse=True, key=sortingFunction)
    
    # Partition and trim free_list
    my_list = partitionSeconds((free_list), meeting_length)
    return shorten(my_list, offset, start_time, end_time, limit, start_of_day, start_of_end)

#------------------------------------------------------------------------------------------#
# Remaining functions appear in the order they are called in timeAlgorithm.
#------------------------------------------------------------------------------------------#

# returns array of int ranges for times
def dataToAvs(data, user, offset):
    times = list()
    for x in data['calendars'][user]['busy']:
        times.append([convertToSecs(x['start'])-offset,convertToSecs(x['end'])-offset])
    return times

# Google response => int seconds
def convertToSecs(time_response): 
    t = time_response[0:19]
    t = mktime(strptime(t, '%Y-%m-%dT%H:%M:%S'))
    return t

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

def is_free(time, ranges):
    for range in ranges:
        if (range[0] <= time) and (time < range[1]):
            return False
    return True

def sortingFunction(item):
    return len(item[2])

# Partitions list of free times into list of smaller free blocks. Returns list of tuples containing
# Index 0: int_start_time; Index 1: int_end_time; Index 2: list_people
def partitionSeconds(freelist, meetingLength):
    meetingLength = int(meetingLength) * 60
    meetingoptions = list()
    
    for freeblock in freelist:
        if len(freeblock[2]) >= 2:
            end = freeblock[1]
            while (end - freeblock[0] >= meetingLength):
                freeblock[1] = freeblock[0] + meetingLength
                meetingoptions.append([freeblock[0], freeblock[1], freeblock[2]])
                freeblock[0] += meetingLength
 
    return meetingoptions

# Shortens the list down to the limit if needed
def shorten(myList, offset, start_time, end_time, limit, start_of_day, start_of_end):
    completeList = list()
    num_people = myList[0][2]

    # Pref between 6am and 9pm. 48600 seconds is 13.5 hours
    pref_offset = 48600
    six_am_offset = 21600
    nine_pm_offset = 75600

    # Numerical representation of the start of each day in range
    day_list = list()
    i = start_of_day
    #print i
    while (i <= start_of_end):
        day_list.append(i)
        i += 86400
        
    # Sort the list by preferred times 
    for block in myList:
        if block[2] == num_people:
            var = abs((i/2) + pref_offset - block[0])
            for time in day_list:
                if (block[0] >= time + six_am_offset) and (block[0] <= time + nine_pm_offset):
                    #print "Pref time found!"
                    var = abs(time + pref_offset - block[0])
                    break
            completeList.append([block[0],block[1],block[2],var])

    completeList.sort(reverse=False, key=betaSortingFunction)

    shortenedList = list()
    for block in completeList:
        if len(shortenedList) < limit:
            sdt = str(datetime.fromtimestamp(mktime(gmtime(block[0]-offset))).strftime("%Y-%m-%d %H:%M"))
            shortenedList.append(sdt)

    #shortenedList.sort(reverse=True, key=sortingFunction)
    shortenedList.sort()
    return shortenedList

def betaSortingFunction(item):
    return item[3]

def timeZoneString(offset):
    if offset == 0:
        return 'Z'
    hours = str(offset/3600)
    minutes = str((offset%3600)/60)
    ret = '-' + hours.zfill(2) + ':' + minutes.zfill(2)
    return ret

#----------------------------------------------------------------------------------#
# Functions not used anywhere, but potentially useful.
#----------------------------------------------------------------------------------#
from time import strftime, localtime
def convert(date):
    return datetime.strptime(date, '%Y-%m-%d')

# TODO: offset append
def convertToUTC(time):# int -> 2018-11-23T09:30:00
    return strftime('%Y-%m-%dT%H:%M:%S', localtime(time))

# 2018-11-23T09:30:00-05:00 -> int seconds
def getOffset(time_response):
    # UTC time; no offset
    if len(time_response) < 22:
        offset = 0
    # Not UTC time; convert offset from hours to seconds
    else:
        hours = int(time_response[20:22])
        minutes = int(time_response[23:25])
        offset = hours*3600 + minutes*60
    return offset


# if __name__ == '__main__':

