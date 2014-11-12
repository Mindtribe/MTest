import serial 
import os.path
import csv
import datetime
from time import sleep

#global varz
serialPort = '/dev/tty.usbmodemfd121'
baudRate =  9600
cycles = 10
sampleDelay = 30 #this needs to be synchronized with the Arduino firmware
chargedVoltage = 4.2 
dischargedVoltage = 3.5

def quit(ser):
    ser.close()
    sleep(2)
    exit()

def SetUpSerial():
    ser = serial.Serial(serialPort, baudRate, timeout=10)
    #give the serial connection time to initialize
    sleep(5)
    return ser

#ser being the serial handle
def getReading(ser):
    while True:
        try:
            line = ser.readline()
            if(len(line) is 0):
                print "No data coming from serial. Check that."
                quit(ser)
            elif(len(line) is not 124):
                print "Bad line length (" + str(len(line)) + "). Trying again."
                print line
                continue
            else:               
                step1 = line.split(",")
                step2 = [x.split(":") for x in step1]
                inputMap = {k.strip():float(v) for k,v in step2}
        except ValueError:
            print "Unable to parse line, trying again..."
            continue
        else:
            return inputMap

#Send a command to the Arduino
#Acceptable commands:
##R = Reset
##C = Charge
##D = Discharge
#ser = serial port handle
def sendCommand(ser, char):
    if char is 'R':
        command = 'reset'
    elif char is 'C': 
        command = 'charge'
    elif char is 'D': 
        command = 'discharge'
    else:
        print "Invalid command"
        quit(ser)
        
    written = ser.write(char)

    if written is not 1:
        print "State transition signal not sent to Arduino."
        quit(ser)
    else:
        print "Command sent: " + command
        sleep(1)

if __name__ == '__main__':

    #Init serial stuff
    print "Initializing serial connection..."
    ser = SetUpSerial()
    print "Serial connection set up."
    print "Getting data...."
    data = getReading(ser)
    print "Current electronic state received."
    print data

    #Make a directory
    #If the subdirectory for today already exists, move along 
    today = datetime.datetime.today().date()
    subdirectory = str(today)
    try:
        os.mkdir(subdirectory)
    except OSError:
       pass 

    #Check CHG state
    vbat = data['VBAT']

    #Intialize our state for the state machine
    ###
    #Note: By default both VUSB is off.
    ####
    if(vbat < chargedVoltage):
        print "Battery is charging"
        state = "CHARGING"
        sendCommand(ser, 'C') #remember to connect VUSB
    else:
        print "Battery is charged"
        state = "DISCHARGING"

    #Run "cycles" number of charges and discharges
    #each charge/discharge (NOT as a pair) counts as a cycle 
    for currentCycle in range (0, cycles):

        ### State Machine ###
        if(state is "CHARGING"):
            print "Starting charge cycle"

            #open the log and csv file for this iteration
            #log
            logFile = os.path.join(subdirectory, "ChargeTest"+str(currentCycle)+".log") 
            logFileHandle = open(logFile, 'w')
            #csv
            csvFile = os.path.join(subdirectory, "ChargeTest"+str(currentCycle)+".csv") 
            csvFileHandle = open(csvFile, 'w')
            csvWriter = csv.writer(csvFileHandle)
            
            #initialize the log file
            startTime = datetime.datetime.now()
            logFileHandle.write("Start time: " + str(startTime) + '\n')

            #initialize the csv file
            csvWriter.writerow( ('Time', 'VBAT', 'CHG') )

            #And now we wait.
            #Grab the state every 60 seconds until CHG goes high
            #write it to the CSV file
            while True:
                print "Charging..."
                sleep(sampleDelay)

                data = getReading(ser)
                print data

                vbat = data['VBAT']
                chg = data['CHG']
                currentTime = str(datetime.datetime.now())
                csvWriter.writerow( (currentTime, str(vbat), str(chg)) )
                if(vbat >= chargedVoltage):
                    #battery is done charging
                    print "Charge Complete (Hit ~4.2V)"
                    
                    #log stop time and elapsed
                    stopTime = datetime.datetime.now()
                    elapsedTime = stopTime-startTime
                    logFileHandle.write("Stop time: " + str(stopTime)+ '\n')
                    logFileHandle.write("Elapsed time: " + str(elapsedTime)+ '\n')

                    #close files
                    logFileHandle.close()
                    csvFileHandle.close()

                    #change state
                    state = "DISCHARGING"
                    break

            #Transition to discharging state
            sendCommand(ser, 'D')

            #move along
            continue

        elif(state is "DISCHARGING"):
            print "Starting discharge cycle"
            #open the log and csv file for this iteration
            #log
            logFile = os.path.join(subdirectory, "DischargeTest"+str(currentCycle)+".log") 
            logFileHandle = open(logFile, 'w')
            #csv
            csvFile = os.path.join(subdirectory, "DischargeTest"+str(currentCycle)+".csv") 
            csvFileHandle = open(csvFile, 'w')
            csvWriter = csv.writer(csvFileHandle)
            
            #initialize the log file
            startTime = datetime.datetime.now()
            logFileHandle.write("Start time: " + str(startTime)+ '\n')

            #initialize the csv file
            csvWriter.writerow( ('Time', 'VBAT', 'CHG') )

            #And now we wait.
            #Grab the state every 60 seconds until VBAT hits 3.5
            #write it to the CSV file
            while True:
                print "Discharging..."
                sleep(sampleDelay)

                data = getReading(ser)
                print data

                vbat = data['VBAT']
                chg = data['CHG']
                currentTime = str(datetime.datetime.now())
                csvWriter.writerow( (currentTime, str(vbat), str(chg)) )
                if(vbat < dischargedVoltage):
                    #battery has discharged 
                    print "Discharged."
                    
                    #log stop time and elapsed
                    stopTime = datetime.datetime.now()
                    elapsedTime = stopTime-startTime
                    logFileHandle.write("Stop time: " + str(stopTime)+ '\n')
                    logFileHandle.write("Elapsed time: " + str(elapsedTime)+ '\n')

                    #close files
                    logFileHandle.close()
                    csvFileHandle.close()

                    #change state
                    state = "CHARGING"
                    break

            ###
            #Reset the Arduino
            #This is necessary to re-enable the CHG line, which nominally only
            #indicates charging during the system's first charge cycle
            ###
            sendCommand(ser, 'R')

            #Transition to charging state
            sendCommand(ser, 'C')

            #move along
            continue
