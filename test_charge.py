import mtest
import time
import u3
import csv
import os
import math 
import json
import datetime

VBAT_IO_PIN = 0 #IO Pin on Labjack
CHG_IO_PIN = 1 #IO Pin on Labjack
HOURS_TO_RUN = 3 #in hours
SAMPLE_DELAY = 10 #in seconds

#connect to labjack
print 'Connecting to LabJack.'

try:
    lj = u3.U3() 
except AttributeError:
    print 'AttributeError. Yeah this is a thing that happens.'
except u3.NullHandleException:
    print 'Are you sure the Labjack is connected?'
finally:
    print 'LabJack connected. I think.'

#*10configure labjack
lj.configAnalog(VBAT_IO_PIN)
lj.configAnalog(CHG_IO_PIN)

#open CSV file
label = "test_charge"+str(datetime.datetime.now())+".csv"
f = open(label, 'wt')

#setup heading
try:
    writer = csv.writer(f)
    writer.writerow( ('Time', 'VBAT', 'CHG') )
finally:
    print "No Errors opening/writing to CSV"

#log data
range_end = HOURS_TO_RUN * 60 * 60/SAMPLE_DELAY #hours * minutes * samples/minute

for i in range(0,range_end):
    vbat = lj.getAIN(VBAT_IO_PIN)*2
    chg = lj.getAIN(CHG_IO_PIN)

    currentTime = datetime.datetime.now().time().__str__()
    writer.writerow( (currentTime, vbat, chg) )

    print '{}: VBAT - {}; CHG - {}'.format(currentTime, vbat, chg)

    time.sleep(SAMPLE_DELAY)

f.close()

