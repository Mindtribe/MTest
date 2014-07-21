import visa
import time

#globals
WAIT_TIME = 0.5

#before running this script, connect computer to scope via usb
#set up connection to scope
scope = visa.instrument('USB0::0x0699::0x041C::C025028')
#create unique timestamped filename
timestr = time.strftime("%Y%m%d-%H%M%S")
#save scope settings
scope.write("SAVE:SETUP \"E:/setup-" + timestr + ".txt\"")
#wait until file is done saving before executing new commands
#copy and pasting this code snippet is bad style. will fix later
while '1' in scope.ask("BUSY?"):
        time.sleep(WAIT_TIME)
#save screencapture
scope.write("SAVE:IMAGE \"E:/screencapture-" + timestr + ".png\"")
while '1' in scope.ask("BUSY?"):
        time.sleep(WAIT_TIME)
#save waveforms
scope.write("SAVE:WAVEFORM ALL,\"E:/waveforms-" + timestr + ".csv\"")
while '1' in scope.ask("BUSY?"):
        time.sleep(WAIT_TIME)

