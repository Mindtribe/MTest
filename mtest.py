import json
import os
import visa

#globals
INSTRUMENT_DIRECTORY = './instruments'

#base class
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

#DC Power Supply class
class DCPowerSupply(Instrument):
    def set_output(self, output):
        self.handle.write(self.get_command('set_output') % str(output))

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
        self.handle.write(self.get_command('set_range') % str(range))

#Electronic Load class
class ElectronicLoad(Instrument):
    def set_input(self, input):
        self.handle.write(self.get_command('set_input') % str(input))

    def set_voltage(self, voltage):
        self.handle.write(self.get_command('set_voltage') % str(voltage))

    def set_current(self, current):
        self.handle.write(self.get_command('set_current') % str(current))

    def set_resistance(self, resistance):
        self.handle.write(self.get_command('set_resistance') % str(resistance))

    def set_range_current(self, range):
        self.handle.write(self.get_command('set_range_current') % str(range))

    def set_range_resistance(self, range):
        self.handle.write(self.get_command('set_range_resistance') % str(range))

    def set_slew_voltage(self, slew):
        self.handle.write(self.get_command('set_slew_voltage') % str(slew))

    def set_slew_current(self, slew):
        self.handle.write(self.get_command('set_slew_current') % str(slew))

    def set_mode(self, mode):
        self.handle.write(self.get_command('set_mode') % str(mode))

    def get_programmed_voltage(self):
        return (self.handle.ask(self.get_command('get_programmed_voltage')))

    def get_programmed_current(self):
        return (self.handle.ask(self.get_command('get_programmed_current')))

    def get_programmed_resistance(self):
        return (self.handle.ask(self.get_command('get_programmed_resistance')))

    def get_voltage(self):
        return (self.handle.ask(self.get_command('get_voltage')))

    def get_current(self):
        return (self.handle.ask(self.get_command('get_current')))

    def get_power(self):
        return (self.handle.ask(self.get_command('get_power')))

#Specific instrument classes
#DC Power Supplies
class AgilentE3631A(DCPowerSupply):
    def get_version(self):
        return self.handle.ask(self.get_command('get_version'))

#Electronic Loads
class Agilent6060B(ElectronicLoad):
    def get_error(self):
        return self.handle.ask(self.get_command('get_error'))
