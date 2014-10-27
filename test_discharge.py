import mtest
import time
import u3
import csv
import os
import math 
import json
import datetime

VBAT3_IO_PIN    = 0 #IO Pin on Labjack
VBAT12_IO_PIN   = 2 #IO Pin on Labjack
VBAT13_IO_PIN   = 3 #IO Pin on Labjack
VBAT1_IO_PIN    = 4 

HOURS_TO_RUN    = 36 #in hours
SAMPLE_DELAY    = 20 #in seconds

#connect to labjack
print 'Connecting to LabJack.'

try:
    lj = u3.U3() 
except AttributeError:
    print 'AttributeError. Yeah this is a thing that happens.'

print 'LabJack connected. I think.'

#configure labjack
lj.configAnalog(VBAT3_IO_PIN)
lj.configAnalog(VBAT12_IO_PIN)
lj.configAnalog(VBAT13_IO_PIN)
lj.configAnalog(VBAT1_IO_PIN)

#open CSV file
label = "test_discharge_"+str(datetime.datetime.now())+".csv"
f = open(label, 'wt')

#setup heading
try:
    writer = csv.writer(f)
    writer.writerow( ('Time', 'VBAT-Board3', 'VBAT-Board12', 'VBAT-Board13', 'VBAT-Board1') )
finally:
    print "No Errors opening/writing to CSV"

range_end = HOURS_TO_RUN * 60 * 60/SAMPLE_DELAY #hours * minutes/hour * samples/minute

for i in range(0,range_end):
    VBATBoard3  = lj.getAIN(VBAT3_IO_PIN)*2
    VBATBoard12 = lj.getAIN(VBAT12_IO_PIN)*2
    VBATBoard13 = lj.getAIN(VBAT13_IO_PIN)*2
    VBATBoard1 = lj.getAIN(VBAT1_IO_PIN)*2

    currentTime = datetime.datetime.now().time().__str__()
    writer.writerow( (currentTime, VBATBoard3, VBATBoard12, VBATBoard13, VBATBoard1)

    print("currentTime: ") + str(currentTime) + '\n'
    print("vbat3: ") + str(VBATBoard3) + '\n'
    print("vbat12: ") + str(VBATBoard12) + '\n'
    print("vbat13: ") + str(VBATBoard13) + '\n'
    print("vbat1: ") + str(VBATBoard1) + '\n'

    time.sleep(SAMPLE_DELAY)

f.close()

