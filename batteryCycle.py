# Test script to cycle the electronic load, as if it were the motor, to determine maximum usage duty cycles for a battery. 
# Samples battery current and voltage and outputs results to csv files.
# Before running the script, you should set the CURRENT_PROFILE variable, which is a list of ordered pairs that specify
# (currentToBeApplied, duration). For example, if you want to apply 1A for 1s, then 0A for 10s, set 
# CURRENT_PROFILE = [(1,0), (0,10)]

import mtest
import time
import u3
import csv
import os
import math 

#global constants
#list of ordered pairs that specify (currentToBeApplied, duration). 
CURRENT_PROFILE = [(3.5, 0.2), (1, 0.2), (5, 0.2), (2.5, 1.8), (1.5, 0.3), (3.5, 0.2), (0, 2.0), (0.6, 4.0)]
#voltage at which battery is considered drained
MIN_BATTERY_VOLTAGE = 3.7
#voltage at which battery is considered charged
CHARGED_BATTERY_VOLTAGE = 3.8
DISCHARGE_SAMPLING_PERIOD = 0.5
CHARGE_SAMPLING_PERIOD = 60
SWITCH_GATE_OFF_VOLTAGE = 5
SWITCH_GATE_ON_VOLTAGE = 0
SWITCHING_DAC_NUMBER = 0
ANALOG_INPUT_PORT = 1
VOLTAGE_DIVIDER_RATIO = 0.5
#note that this is an empirical approximation of the time it takes to set the current on the electronic load. 
#This value is determined mostly by the timeout parameter set in AGILENT_6060B.py. 
PROGRAMMING_DELAY = 0.2
ELECTRONIC_LOAD_SERIAL_ADDRESS = 'ASRL3'

def WriteRow(csvWriter, entryList):
	csvWriter.writerow(entryList)

def ApplyCurrentProfile(electronicLoad, labJackHandle, currentProfile, startTime, csvWriter, dischargeCycle):
	#currentProfile should be a list of tuples which represent ordered pairs of (currentToBeApplied, duration).
	#write before current ramping
	WriteRow(csvWriter, [time.time()-startTime, ReadVoltage(labJackHandle), 0, 'discharge', dischargeCycle])
	for pairNumber, pair in enumerate(currentProfile):
		current = pair[0]
		duration = pair[1]
		#assume that setting the current takes PROGRAMMING_DELAY seconds
		electronicLoad.set_current(current)
		print 'Set current to %f' % current
		voltage = ReadVoltage(labJackHandle)
		if pairNumber is len(currentProfile) - 1:
			WriteRow(csvWriter, [time.time()-startTime, voltage, current, 'recover', dischargeCycle])
		else:
			WriteRow(csvWriter, [time.time()-startTime, voltage, current, 'discharge', dischargeCycle])
		numSamples = int(math.floor((duration-PROGRAMMING_DELAY)/DISCHARGE_SAMPLING_PERIOD))
		for sample in range(numSamples):
			time.sleep(DISCHARGE_SAMPLING_PERIOD)
			voltage = ReadVoltage(labJackHandle)
			if pairNumber is len(currentProfile) - 1:
				WriteRow(csvWriter, [time.time()-startTime, voltage, current, 'recover', dischargeCycle])
			else:
				WriteRow(csvWriter, [time.time()-startTime, voltage, current, 'discharge', dischargeCycle])

def ReadVoltage(labJackHandle):
	#multiply by two to account for the resistive divider (which is necessary since the labjack's full scale range is only 0-2.4V)
	return labJackHandle.getAIN(ANALOG_INPUT_PORT)/VOLTAGE_DIVIDER_RATIO

def ConnectCharger(labJackHandle):
	dacCode = labJackHandle.voltageToDACBits(SWITCH_GATE_ON_VOLTAGE, is16Bits=True)
	labJackHandle.getFeedback(u3.DAC16(SWITCHING_DAC_NUMBER, dacCode))	

def DisconnectCharger(labJackHandle):
	dacCode = labJackHandle.voltageToDACBits(SWITCH_GATE_OFF_VOLTAGE, is16Bits=True)
	labJackHandle.getFeedback(u3.DAC16(SWITCHING_DAC_NUMBER, dacCode))

def main():
	#bounds check on CURRENT_PROFILE durations
	for pair in CURRENT_PROFILE:
		if pair[1] < PROGRAMMING_DELAY:
			raise Exception('ERROR: all durations in CURRENT_PROFILE must be greater than %f. This is the minimum time required to set current on the electronic load.' % PROGRAMMING_DELAY)

	#configure electronic load
	print 'Connecting to Agilent 6060B'
	el = mtest.Agilent6060B('Agilent6060B', serialAddress=ELECTRONIC_LOAD_SERIAL_ADDRESS)
	el.set_input('ON')
	el.set_mode('CURRENT')

	#configure labjack
	print 'Connecting to LabJack'
	lj = u3.U3() 
	DisconnectCharger(lj)
	# Set ANALOG_INPUT_PORT to analog
	lj.configAnalog(ANALOG_INPUT_PORT)

	#set initial time
	startTime = time.time()

	#create output base filename (YYYYMMDD-HHMMSS)
	outputBaseFilename = 'battery-cycle-test-' + time.strftime("%Y%m%d") + '-' + time.strftime("%H%M%S")

	#create directory for output files
	os.mkdir(outputBaseFilename)

	#create summary file
	summaryFile = open(os.path.join(outputBaseFilename, 'summary.csv'), 'wb')
	summaryWriter = csv.writer(summaryFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
	WriteRow(summaryWriter, ['Charge Cycle', 'Number of Discharge Cycles'])

	chargeCycle = 0
	while True:
		chargeCycle += 1
		#create output file
		outputFile = open(os.path.join(outputBaseFilename, 'charge-cycle-%d.csv' % chargeCycle), 'wb')
		writer = csv.writer(outputFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
		WriteRow(writer, ['Time (s)', 'Voltage (V)', 'Current (A)', 'Phase', 'Discharge Cycle'])
		dischargeCycle = 0
		print '\nCharge cycle: %d' % chargeCycle
		while ReadVoltage(lj) >= MIN_BATTERY_VOLTAGE:
			dischargeCycle += 1
			print '\nDischarge cycle: %d' % dischargeCycle
			ApplyCurrentProfile(el, lj, CURRENT_PROFILE, startTime, writer, dischargeCycle)
			print 'Recover voltage: %f' % ReadVoltage(lj)
			print '____________________________'
		el.set_current(0)
		el.set_input('OFF')
		WriteRow(summaryWriter, [chargeCycle, dischargeCycle])
		while ReadVoltage(lj) < CHARGED_BATTERY_VOLTAGE:
				ConnectCharger(lj)
				WriteRow(writer, [time.time()-startTime, ReadVoltage(lj), None, 'charge', None])
				print ReadVoltage(lj)
				time.sleep(CHARGE_SAMPLING_PERIOD)
		DisconnectCharger(lj)

if __name__ == '__main__':
    main()
