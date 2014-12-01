import serial 
import os.path
import csv
import datetime
import time
from time import sleep

#global varz
serialPort = '/dev/tty.usbmodemfa1321'
baudRate =  9600
cycles =1000 
statePause = 2 
timesToBreathe = 5 
charging = True
testsFailed = 0
thisCycle = 0

#save the keystrokes!
X = 'X'
Y = 'Y'
S = 'S'
L = 'L'
R = 'R'
D = 'D'
C = 'C'

#return a map of correct values for the indicated state
def getCorrectValues(state, charging):

    #success criteria

    if charging is True:
        chg_min = 0
        chg_max = 0.6
    else:
        chg_min = 3.95
        chg_max = 4.25

    valuesOffUnplugged = {
        'CHG'       :[3.95,4.25],
        'PG'        :[3.95,4.25],
        'BLEDR1'    :True,
        'BLEDR2'    :True,
        'TLEDR1'    :True,
        'TLEDR2'    :True,
        'VBAT'      :[3.8,4.25],
        'REAR_LEDS' :[0,0.5],
        'FRONT_LEDS':[0,0.5],
        'PWM_FRONT' :True,
        'PWM_REAR'  :True
    }
    
    valuesOffPluggedIn = {
        'CHG'       :[chg_min, chg_max],
        'PG'        :[0,0.6],
        'BLEDR1'    :True,
        'BLEDR2'    :True,
        'TLEDR1'    :True,
        'TLEDR2'    :True,
        'VBAT'      :[3.8,4.25],
        'REAR_LEDS' :True,
        'FRONT_LEDS':[0,0.5],
        'PWM_FRONT' :True,
        'PWM_REAR'  :[0.4,1.4] if charging else [0.4,0.6]
        }
    
    valuesOnPluggedIn = {
        'CHG'       :[chg_min, chg_max],
        'PG'        :[0,0.6],
        'BLEDR1'    :True,
        'BLEDR2'    :True,
        'TLEDR1'    :True,
        'TLEDR2'    :True,
        'VBAT'      :[3.8,4.25],
        'REAR_LEDS' :True,
        'FRONT_LEDS':True,
        'PWM_FRONT' :[2.8,3.3],
        'PWM_REAR'  :[0.05,0.65]
    }

    if state == "OFF/UNPLUGGED": 
        return valuesOffUnplugged
    if state == "OFF/PLUGGEDIN":
        return valuesOffPluggedIn
    if state == "ON/PLUGGEDIN" : 
        return valuesOnPluggedIn
    if state == "BREATHING/PLUGGEDIN": 
        print "this shouldn't happen"

#take in a map of the sampled data and the correct ranges for the current state
#compare! log failures
def checkValues(sample, correct, csvWriter, logFileHandle, state):
    global testsFailed

    #print "sample: " + str(sample)
    #print "correct: " + str(correct)

    for key, value in sample.iteritems():
        okRange = correct[key]
        #you know the okRange value will be True or a 2-entry list indicating the acceptable range
        if okRange is True: 
            pass
        else:
            if not(value >= okRange[0] and value <= okRange[1]):
                #error happened
                error = "Test failed. Node: {}, Value: {}, Range({}-{})".format(key, value, okRange[0], okRange[1])
                print error 
                #log the error
                csvWriter.writerow(['FAILURE', error])
                logFileHandle.write("\nFailed test on cycle {} in state {}".format(thisCycle, state))
                #increment error counter
                testsFailed += 1
            else: 
                pass

#make a dict a list so you can write it to a CSV
def listify(aDict):
    aList = []
    for key,value in aDict.iteritems():
        aList.append(str(key)+": "+str(value))
    return aList

#quit in a pleasant way that closes the serial port
def quit(ser):
    ser.close()
    sleep(2)
    exit()

#set up the serial connection
def SetUpSerial():
    ser = serial.Serial(serialPort, baudRate, timeout=10)
    #give the serial connection time to initialize
    sleep(5)
    return ser

#snag a reading from the serial port
#ser being the serial handle
def getReading(ser):
    while True:
        try:
            line = ser.readline()
            if(len(line) is 0):
                print "No serial data available. Returning."
                return 0
            elif(len(line) is not 157):
               #print "Bad line length (" + str(len(line)) + "). Trying again."
               #print line
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
    elif char is 'M': 
        command = "disable test mode"
    elif char is 'X': 
        command = "fetch one line of data"
    elif char is 'Y': 
        command = "fetch 100 lines of data"
    elif char is 'L': 
        command = "long press"
    elif char is 'S': 
        command = "short press"
    else:
        print "Invalid command"
        quit(ser)
        
    #good command? send it off
    written = ser.write(char)

    if written is not 1:
        print "State transition signal not sent to Arduino."
        quit(ser)
    else:
        print "Command sent: " + command
        #give electrical transitions some time
        if char == ('M' or 'Y'): sleep (1)
        else: sleep(5)

#do test things
if __name__ == '__main__':

    #Init serial stuff
    print "Initializing serial connection..."
    ser = SetUpSerial()
    print "Serial connection set up."
    print "Getting data...."
    sendCommand(ser, X)
    data = getReading(ser)
    print "Current electronic state properly received."
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
    chg = data['CHG']
    if chg < 0.5: charging = True
    else: charging = False

    #Intialize our state for the state machine
    #Note: Firmware starts stress test in OFF/PLUGGEDIN state
    #make sure to unplug first
    sendCommand(ser, D)
    state = "OFF/UNPLUGGED"

    #open the log and csv file for this iteration
    #log
    logFile = os.path.join(subdirectory, "StressTest"+".log") 
    logFileHandle = open(logFile, 'w')
    #csv
    csvFile = os.path.join(subdirectory, "StressTest"+".csv") 
    csvFileHandle = open(csvFile, 'w')
    csvWriter = csv.writer(csvFileHandle)

    #initialize the log file
    startTime = datetime.datetime.now()
    logFileHandle.write("Start time: " + str(startTime) + '\n')

    #Run "cycles" number of tests
    for currentCycle in range (0, cycles):
        thisCycle = currentCycle
        csvWriter.writerow( ("current Cycle: ", currentCycle) )
        
        breathingCycles = 0 #used to track how many times we have done the step 3-4 inner loop

        #Internal loop to keep things circulating until next cycle
        #Mostly to keep steps 3-4 cycling with a state change + break
        #Steps 3 and 4 being OFF/PLUGGEDIN and BREATHING/PLUGGEDIN
        while True:

            ### State Machine ###
            if(state == "OFF/UNPLUGGED"):
                currentTime = str(datetime.datetime.now())
                sendCommand(ser,X)
                data = getReading(ser)
                data2 = listify(data)

                print '\n'
                print state
                print currentTime 
                print data
                print '\n'
                sleep(statePause)

                #update CSV
                csvWriter.writerow( [state] )
                csvWriter.writerow( [currentTime] )
                csvWriter.writerow( data2 )

                #check sampled data for correctness
                correct = getCorrectValues(state, charging)
                print "Checking data from state: " + state
                checkValues(data, correct, csvWriter, logFileHandle, state)
                
                #Transition to OFF/PLUGGEDIN
                sendCommand(ser,C)
                state = "OFF/PLUGGEDIN"

                #move along
                continue

            if(state == "OFF/PLUGGEDIN"):
                currentTime = str(datetime.datetime.now())
                sendCommand(ser, X)
                data = getReading(ser)
                data2 = listify(data)

                print '\n'
                print state
                print currentTime 
                print data
                print '\n'
                sleep(statePause)

                #update CSV
                csvWriter.writerow( [state] )
                csvWriter.writerow( [currentTime] )
                csvWriter.writerow( data2 )

                #check sampled data for correctness
                correct = getCorrectValues(state, charging)
                print "Checking data from state: " + state
                checkValues(data, correct, csvWriter, logFileHandle, state)
                
                #Transition to ....
                if(breathingCycles is not timesToBreathe):
                    sendCommand(ser, S)
                    state = "ON/PLUGGEDIN"
                else:
                    sendCommand(ser, D)
                    state = "OFF/UNPLUGGED"
                    break #Finish the cycle

                #move along
                continue
            
            if(state == "ON/PLUGGEDIN"):
                currentTime = str(datetime.datetime.now())
                sendCommand(ser, X)
                data = getReading(ser)
                data2 = listify(data)

                print '\n'
                print state
                print currentTime 
                print data
                print '\n'
                sleep(statePause)
                
                #update CSV
                csvWriter.writerow( [state] )
                csvWriter.writerow( [currentTime] )
                csvWriter.writerow( data2 )

                #check sampled data for correctness
                correct = getCorrectValues(state, charging)
                print "Checking data from state: " + state
                checkValues(data, correct, csvWriter, logFileHandle, state)

                #Transition to ....

                #if the inner loop is still going, start breathing
                if(breathingCycles is not timesToBreathe):
                    sendCommand(ser, S)
                    state = "BREATHING/PLUGGEDIN"
                #otherwise, skip to turning off
                else:
                    sendCommand(ser, L)
                    state = "OFF/PLUGGEDIN"

                #move along
                continue

            if(state == "BREATHING/PLUGGEDIN"):
                #inner loop counter check
                if(breathingCycles is timesToBreathe):
                    state = "ON/PLUGGEDIN"
                    continue
                #increment inner loop counter
                breathingCycles = breathingCycles+1

                #otherwise carry on
                currentTime = str(datetime.datetime.now())
                sendCommand(ser, Y)
                dataList = [] #store all the datas gathered
                
                print '\n'
                print state
                print breathingCycles
                print currentTime 
                print '\n'
                sleep(statePause)

                csvWriter.writerow( [state] )
                csvWriter.writerow( [currentTime] )

                #snag all 100 lines
                #Note! Breathing takes almost exactly 30seconds. We'll make sure we wait 35.
                breathingStart = time.time()
                while(True): #will fail when getreading doesn't get a line
                    #grab data
                    data = getReading(ser)
                    #break if that's all the data there is
                    if data is 0: 
                        break
                    #otherwise do all the things
                    else: 
                        dataList.append(data)
                        print data
                        #write to CSV
                        data2 = listify(data)
                        csvWriter.writerow( data2 )

                #check for breathing
                #This is a rough first-order approximation of breathing.
                #We check the max slope of the DC level of the FRONT_LEDS signal
                #A slope of ~.025 V/sample indicates roughly that breathing happened
                pwmList = []
                for dataPoint in dataList:
                    pwmList.append(dataPoint['PWM_FRONT'])
                pwmList.sort()
		slope = (pwmList[99]-pwmList[0])/100
                if not( slope >= 0.0240):
	            error = "No breathing detected (min: {}, max: {}, slope: {})".format(pwmList[0], pwmList[99], slope)
		
		    print error
		    csvWriter.writerow(['FAILURE', error])
		    logFileHandle.write("Failed test on cycle {} in state {}".format(thisCycle, state))
		    #increment error counter
		    testsFailed += 1
                
                #wait until breathing is done
                print "Waiting for breathing to finish....."
                while(time.time() - breathingStart < 35): continue
                print "Done! Continuing..."

                #Transition to ON/PLUGGEDIN
                state = "ON/PLUGGEDIN"

                #move along
                continue
    
    #last writes
    logFileHandle.write("Total tests failed: " + str(testsFailed)+'\n')
    stopTime = datetime.datetime.now()
    elapsedTime = stopTime - startTime
    logFileHandle.write("Stop time: " + str(startTime) + '\n')
    logFileHandle.write("Elapsed time: " + str(elapsedTime) + '\n')
    #tidy up
    logFileHandle.close()
    csvFileHandle.close()
    #indicate
    print "Stress Test Complete!"
    quit(ser)
