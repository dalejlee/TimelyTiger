import json

def is_free(time, ranges):
    for range in ranges:
        if (range[0] <= time) and (time < range[1]):
            return False;
    return True;

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
def dataToAvs(data):
    times = list()
    for x in data['calendars']['DanielPallaresBello@gmail.com']['busy']:
        times.append([convertToSecs(x['start']),convertToSecs(x['end'])])
    return times

def convertToSecs(time):
    year = int(time[0:4])
    month = int(time[5:7])
    day = int(time[8:10])
    hour = int(time[11:13])
    minute = int(time[14:16])
    seconds = int(time[17:19])
    return ((year - 1970) * 31540000) + (month * 2628000) + (day * 86400) + (hour * 3600) + (minute * 60) + seconds

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

if __name__ == '__main__':
    starttime = 1544831400
    endtime = 1544889000

    files = list();
    files.append('data.json')
    files.append('data1.json')
    avs = list();
    users = list();
    users.append('Daniel Pallares')
    users.append('Dale Lee')
    for file in files:
        with open(file) as f:
            data = json.load(f)
            avs.append(dataToAvs(data))
    mylist = checkRanges(createCutoffs(avs,starttime,endtime),avs,users)
    mylist.sort(reverse=True, key=sortingFunction)
    for interval in mylist:
        if len(interval[2]) >= 2:
            print convertToRFC(interval[0]), ' ', convertToRFC(interval[1]), ' ', interval[2], '\n'
