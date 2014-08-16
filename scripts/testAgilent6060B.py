import mtest
import time
import random

#globals
VOLTAGE = 1
CURRENT = 0.1
RESISTANCE = 10
VOLTAGE_SLEW = 1
CURRENT_SLEW = 1
MEASUREMENT_TOLERANCE = 0.05
TIMEOUT_STEP = 0.1

try:
	print 'Connecting:'
	el = mtest.Agilent6060B('Agilent6060B')
except:
	print 'Error: Could not connect to Agilent6060B.'

print '\n----------\n'

try:
	print 'Testing all commands:\n'
	el.get_id()
	el.reset()
	el.set_input('ON')
	el.set_voltage(VOLTAGE)
	el.set_current(CURRENT)
	el.set_resistance(RESISTANCE)
	el.set_transient_voltage(VOLTAGE)
	el.set_transient_current(CURRENT)
	el.set_transient_resistance(RESISTANCE)
	el.set_range_resistance(RESISTANCE)
	el.set_range_current(CURRENT)
	el.set_slew_voltage(VOLTAGE_SLEW)
	el.set_slew_current(CURRENT_SLEW)
	el.set_mode('CURRent')
	el.get_programmed_voltage()
	el.get_programmed_current()
	el.get_programmed_resistance()
	el.get_voltage()
	el.get_current()
	el.get_power()
	el.get_error()
except:
	print 'Error: Could not successfully send all commands. Try increasing serialTimeout parameter in AgilentE3631A.json.'

print '\n----------\n'

try:
	print 'Tesing command functionality:\n'
	print 'Resetting'
	el.reset()
	print 'Setting mode to %s' % 'VOLTage'
	el.set_mode('VOLTage')
	print 'Turning input on'
	el.set_input('on')
	print 'Setting voltage to %f' % VOLTAGE
	el.set_voltage(VOLTAGE)
	programmedVoltage = el.get_programmed_voltage()
	print 'Reading programmed voltage: %f' % programmedVoltage
	if programmedVoltage == VOLTAGE:
		print 'Programmed voltage is correct'
	else:
		print 'Error: Programmed voltage is not correct'
	print 'Setting current to %f' % CURRENT
	el.set_current(CURRENT)
	programmedCurrent = el.get_programmed_current()
	print 'Reading programmed current: %f' % programmedCurrent
	if programmedCurrent == CURRENT:
		print 'Programmed current is correct'
	else:
		print 'Error: Programmed current is not correct'
	print 'Setting resistance to %f' % RESISTANCE
	el.set_resistance(RESISTANCE)
	programmedResistance = el.get_programmed_resistance()
	print 'Reading programmed resistance: %f' % programmedResistance
	if programmedResistance == RESISTANCE:
		print 'Programmed resistance is correct'
	else:
		print 'Error: Programmed resistance is not correct'
except:
	print 'Error: Could not successfully complete testing command functionality. Try increasing serialTimeout parameter in AgilentE3631A.json.'

print '\n----------\n'

if el.communicationProtocol == 'serial':
	try:
		print 'Testing minimum timeout:\n'
		timeout = el.timeout
		minTimeout = timeout
		while timeout >= 0:
			print 'Testing current measurement with %s second timeout:' % timeout
			el.reset()
			el.timeout = timeout
			el.set_mode('CURRent')
			el.set_input('on')
			randomCurrent = random.random()
			print 'Setting current to %f' % randomCurrent
			el.set_current(randomCurrent)
			measuredCurrent = el.get_current()
			print 'Reading measured current: %f' % measuredCurrent
			if abs(measuredCurrent - 0) < MEASUREMENT_TOLERANCE:
				print 'Measured current matches expected current (0A, since the input terminals are floating)'
				minTimeout = timeout
			else:
				print 'Error: Measured current does not match expected current'
			timeout -= TIMEOUT_STEP
			print '\n'
	except:
		print 'This error should be expected during the minimum timeout test (likely due to the timeout being too short). Minimum timeout is %s seconds. Set timeout parameter in AgilentE3631A.json to this value to increase programming speed.' % minTimeout

	print 'Minimum timeout is %f seconds. Set timeout parameter in AgilentE3631A.json to this value to increase programming speed.' % minTimeout

