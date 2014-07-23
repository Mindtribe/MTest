import json
import os
import visa

#globals
INSTRUMENT_DIRECTORY = './instruments'

class Instrument(object):

    def __init__(self, name):
        self.name = name
        instrumentFile = open(os.path.join(INSTRUMENT_DIRECTORY, name + '.json'))
        instrumentFileDict = json.load(instrumentFile)
        self.addressDict = instrumentFileDict['addresses']
        self.commandDict = instrumentFileDict['commands']
        self.connect()

    def __del__(self):
        self.disconnect()

    def get_command(self, commandName):
        return self.commandDict[commandName]['commandString']

    def connect(self):
        self.handle = visa.instrument(self.addressDict['serial'])
        #set termination characters so instrument knows when to stop listening and execute a command
        self.handle.term_chars = '\r\n'

    def disconnect(self):
        # return control to panel
        #self.handle.write('SYST:LOC')
        self.handle.close()

    def get_id(self):
        return self.handle.ask(self.get_command('get_id'))

    def reset(self):
        return self.handle.write(self.get_command('reset'))

class DCPowerSupply(Instrument):
    def set_output(self, output):
        self.handle.write(self.get_command('set_output') % output)

    def set_voltage(self, voltage):
        self.handle.write(self.get_command('set_voltage') % str(voltage))

    def set_current(self, current):
        self.handle.write(self.get_command('set_current') % str(current))

    def set_voltage_and_current(self, voltage, current):
        self.handle.write(self.get_command('set_voltage_and_current') % (str(voltage), str(current)))

    def get_voltage(self):
        return (self.handle.ask(self.get_command('get_voltage')))

    def get_current(self):
        return (self.handle.ask(self.get_command('get_current')))

    def set_voltage_limit(self, voltageLimit):
        self.handle.write(self.get_command('set_voltage_limit') % str(voltageLimit))

    def set_current_limit(self, currentLimit):
        self.handle.write(self.get_command('set_current_limit') % str(currentLimit))

    def set_range(self, range):
        self.handle.write(self.get_command('set_range') % range)

class AgilentE3631A(DCPowerSupply):
    def get_version(self):
        return self.handle.ask(self.get_command('get_version'))
