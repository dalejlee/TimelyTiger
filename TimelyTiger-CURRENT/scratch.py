import datetime
from datetime import datetime 
from datetime import timedelta
import time
from time import gmtime, strftime, mktime
import pdb
import timeAlg

# pdb.set_trace()
meetingLength = 60
meetingLength = meetingLength*60
startdate1 = '2018-12-14 06:00'
startdateMod = startdate1[0:10] + 'T' + startdate1[12:19] + ':00-05:00'

startdate2 = timeAlg.convertToSecs(startdateMod)
startdate2 = startdate2 + meetingLength
edt = str(datetime.fromtimestamp(mktime(gmtime(startdate2))).strftime("%Y-%m-%d %H:%M"))

enddateMod = edt[0:10] + 'T' + edt[12:19] + ':00-05:00'

endtimeCompare = '2018-12-14T06:00:00'

# t = datetime.strptime(endtime, '%Y-%m-%d-%H:%M') 
# t = t + t.timedelta(hours=1)
print startdateMod
print startdate2
print edt
print enddateMod