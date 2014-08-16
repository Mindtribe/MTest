import mtest

try:
	print 'Connecting via ethernet:'
	osc = mtest.TektronixMSO4104BL('TektronixMSO4104BL', 'ethernet')
except:
	raise Exception('Error: Could not connect to TektronixMSO4104BL via ethernet. Make sure the TektronixMSO4104BL ethernet cable is plugged in and your computer is connected to the network.')

print '\n----------\n'

try:
	print 'Testing all commands:\n'
	osc.get_id()
	osc.reset()
	osc.get_screen_capture()
except:
	raise Exception('Error: Could not successfully send all commands.')

del osc

print '\n----------\n'

try:
	print 'Connecting via USB:'
	osc = mtest.TektronixMSO4104BL('TektronixMSO4104BL', 'usb')
except:
	raise Exception('Error: Could not connect to TektronixMSO4104BL via USB. Make sure the TektronixMSO4104BL is connected to your computer via USB.')

print '\n----------\n'

try:
	print 'Testing all commands:\n'
	osc.get_id()
	osc.reset()
	osc.get_screen_capture()
except:
	raise Exception('Error: Could not successfully send all commands.')



