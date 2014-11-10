import sys
import csv
import datetime

label = "testoutput_"+str(datetime.datetime.now())+".csv"
f = open(label, 'wt')

try:
    writer = csv.writer(f)
    writer.writerow( ('Time', 'VBAT') )
finally:
    f.close()

print "CSV test executed successfully. Or at least it didn't crash."
