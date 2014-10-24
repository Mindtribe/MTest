import mtest
import time
import u3
import csv
import os
import math 
import json
import datetime

VBAT_IO = 0 #IO Pin on Labjack
CHG_IO = 1
FRONT_LEDS_IO = 2
REAR_LEDS_IO = 3
PG_IO = 4
TLEDR1_IO = 5
BLEDR1_IO = 6
BLEDR2_IO = 7

HOURS_TO_RUN = 5 #in hours
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

#configure labjack
lj.configAnalog(VBAT_IO)
lj.configAnalog(CHG_IO)
lj.configAnalog(FRONT_LEDS_IO)
lj.configAnalog(REAR_LEDS_IO)
lj.configAnalog(PG_IO)
lj.configAnalog(TLEDR1_IO)
lj.configAnalog(BLEDR1_IO)
lj.configAnalog(BLER2_IO)

#open CSV file
#label = "test_charge"+str(datetime.datetime.now())+".csv"
#f = open(label, 'wt')

#setup heading
#try:
#    writer = csv.writer(f)
#    writer.writerow( ('Time', 'VBAT', 'CHG') )
#finally:
#    print "No Errors opening/writing to CSV"

#log data
range_end = HOURS_TO_RUN * 60 * 60/SAMPLE_DELAY #hours * minutes * samples/minute

for i in range(0,range_end):

    #analog inputs
    vbat = lj.getAIN(VBAT_IO)*2
    chg = lj.getAIN(CHG_IO)*2
    front_leds = lj.getAIN(FRONT_LEDS_IO)*2
    rear_leds = lj.getAIN(REAR_LEDS_IO)*2
    pg = lj.getAIN(PG_IO)*2
    tledr1 = lj.getAIN(TLEDR1_IO)*2
    bledr1 = lj.getAIN(BLEDR1_IO)*2
    bledr2 = lj.getAIN(BLEDR2_IO)*2

    currentTime = datetime.datetime.now().time().__str__()
#    writer.writerow( (currentTime, vbat, chg) )

    print(currentTime) + '\n'
    print(vbat) + '\n'
    print(chg) + '\n'
    print(front_leds) + '\n'
    print(rear_leds) + '\n'
    print(pg) + '\n'
    print(tledr1) + '\n'
    print(bledr1) + '\n'
    print(bledr2) + '\n'
    print '\n'

    time.sleep(SAMPLE_DELAY)

#f.close()

