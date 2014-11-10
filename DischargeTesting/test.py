import mtest
import time
import u3
import csv
import os
import math 
import json
import datetime

#connect to labjack
print 'Connecting to LabJack.'

try:
    lj = u3.U3() 
except AttributeError:
    print 'AttributeError. Yeah this is a thing that happens.'

print 'LabJack connected. I think.'

#configure labjack
lj.configAnalog(0)
lj.configAnalog(1)
lj.configAnalog(2)

#open CSV file
label = "test_discharge"+str(datetime.datetime.now())+".csv"
f = open(label, 'wt')

#setup heading
try:
    writer = csv.writer(f)
    writer.writerow( ('Time', 'VBAT-Board3', 'VBAT-Board12', 'VBAT-Board13') )
finally:
    print "No Errors opening/writing to CSV"

for i in range(0,6*60*36*10):
    VBATBoard3  = lj.getAIN(0)*2
    VBATBoard12 = lj.getAIN(1)*2
    VBATBoard13 = lj.getAIN(2)*2

    currentTime = datetime.datetime.now().time().__str__()
    writer.writerow( (currentTime, VBATBoard3, VBATBoard12, VBATBoard13) )

    print '{}: VBATBoard3 - {}; VBATBoard12 - {}; VBATBoard13 - {}'.format(currentTime, VBATBoard3, VBATBoard12, VBATBoard13)

    time.sleep(1)

f.close()

