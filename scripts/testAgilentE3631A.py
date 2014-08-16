import mtest
import time
import random

#globals
OUTPUT = 'P25V'
VOLTAGE = 1
CURRENT = 0.1
MEASUREMENT_TOLERANCE = 0.05
TIMEOUT_STEP = 0.1

try:
	print 'Connecting:'
	ps = mtest.AgilentE3631A('AgilentE3631A')
except:
	print 'Error: Could not connect to AgilentE3631A.'

print '\n----------\n'

try:
	print 'Testing all commands:\n'
	ps.get_id()
	ps.get_version()
	ps.reset()
	ps.set_output('on')
	ps.select_output(OUTPUT)
	ps.set_voltage(VOLTAGE)
	ps.set_current(CURRENT)
	ps.set_voltage_and_current(OUTPUT, VOLTAGE, CURRENT)
	ps.get_programmed_voltage()
	ps.get_voltage()
	ps.get_programmed_current()
	ps.get_current()
except:
	print 'Error: Could not successfully send all commands. Try increasing serialTimeout parameter in AgilentE3631A.json.'

print '\n----------\n'

try:
	print 'Tesing command functionality:\n'
	print 'Resetting'
	ps.reset()
	print 'Setting output to %s' % OUTPUT
	ps.select_output(OUTPUT)
	print 'Turning output on'
	ps.set_output('on')
	print 'Setting voltage to %f' % VOLTAGE
	ps.set_voltage(VOLTAGE)
	programmedVoltage = ps.get_programmed_voltage()
	print 'Reading programmed voltage: %f' % programmedVoltage
	if programmedVoltage == VOLTAGE:
		print 'Programmed voltage is correct'
	else:
		print 'Error: Programmed voltage is not correct.'
	measuredVoltage = ps.get_voltage()	
	print 'Reading measured voltage: %f' % measuredVoltage
	if abs(measuredVoltage - VOLTAGE) < MEASUREMENT_TOLERANCE:
		print 'Measured voltage matches programmed voltage'
	else:
		print 'Error: Measured voltage does not match programmed voltage.'
	print 'Setting current to %f' % CURRENT
	ps.set_current(CURRENT)
	programmedCurrent = ps.get_programmed_current()
	print 'Reading programmed current: %f' % programmedCurrent
	if programmedCurrent == CURRENT:
		print 'Programmed current is correct'
	else:
		print 'Error: Programmed current is not correct.'
except:
	print 'Error: Could not successfully complete testing command functionality. Try increasing serialTimeout parameter in AgilentE3631A.json.'

print '\n----------\n'

try:
	print 'Testing minimum timeout:\n'
	timeout = ps.timeout
	minTimeout = timeout
	while timeout >= 0:
		print 'Testing voltage measurement with %s second timeout:' % timeout
		ps.reset()
		ps.timeout = timeout
		ps.select_output(OUTPUT)
		ps.set_output('on')
		randomVoltage = random.random()
		print 'Setting voltage to %f' % randomVoltage
		ps.set_voltage(randomVoltage)
		measuredVoltage = ps.get_voltage()
		print 'Reading measured voltage: %f' % measuredVoltage
		if abs(measuredVoltage - randomVoltage) < MEASUREMENT_TOLERANCE:
			print 'Measured voltage matches programmed voltage'
			minTimeout = timeout
		else:
			print 'Error: Measured voltage does not match programmed voltage.'
		timeout -= TIMEOUT_STEP
		print '\n'
except:
	print 'This error should be expected during the minimum timeout test (likely due to the timeout being too short). Minimum timeout is %s seconds. Set timeout parameter in AgilentE3631A.json to this value to increase programming speed.' % minTimeout

print 'Minimum timeout is %f seconds. Set timeout parameter in AgilentE3631A.json to this value to increase programming speed.' % minTimeout

