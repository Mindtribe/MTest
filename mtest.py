import json
import os
import serial
import visa
from sys import platform

#globals
INSTRUMENT_DIRECTORY = './instruments'
SERIAL_BAUDRATE = 9600
SERIAL_READ_SIZE = 256 
SERIAL_ADDRESSES_OSX = ['/dev/tty.usbserial-PXWYFRKG', '/dev/tty.usbserial-PXHF1TCW']
SERIAL_ADDRESS_WINDOWS = 'COM5'
MAC_OSX_ALIAS = 'darwin'
WINDOWS_ALIAS = 'win32'
LINUX_ALIAS = 'linux'
LINUX2_ALIAS = 'linux2'

#base class
class Instrument(object):

    def __init__(self, name, communicationProtocol='serial'):
        self.name = name
        self.communicationProtocol = communicationProtocol
        instrumentFile = open(os.path.join(INSTRUMENT_DIRECTORY, name + '.json'))
        instrumentFileDict = json.load(instrumentFile)
        self.parametersDict = instrumentFileDict['parameters']
        self.terminationCharacters = str(self.parametersDict['terminationCharacters'])
        if self.parametersDict['ipAddress'] == 'None':
            self.ipAddress = None
        else:
            self.ipAddress = self.parametersDict['ipAddress']
        if self.parametersDict['serialTimeout'] == 'None':
            self.serialTimeout = None
        else:
            self.serialTimeout = float(self.parametersDict['serialTimeout'])
        self.commandDict = instrumentFileDict['commands']
        self.connect()

    def __del__(self):
        self.disconnect()

    def print_commands(self):
        for command in self.commandDict:
            print command

    def print_command_description(self, commandName):
        print self.commandDict[commandName]['description']

    def print_command_arguments(self, commandName):
        print self.commandDict[commandName]['arguments']

    def get_command_string(self, commandName):
        return str(self.commandDict[commandName]['commandString'])

    def get_command_arguments(self, commandName):
        return self.commandDict[commandName]['arguments']

    def send_command(self, commandName, *parameters):
        #form parameter tuple
        parametersTuple = ()
        for parameter in parameters:
            #note that we typecast all parameters as strings here
            parametersTuple += (str(parameter),)
        if self.communicationProtocol is 'serial':
            #note that pyserial no longer allows you to specify termination characters explicitly, so instead, we append them to the end of each command.
            self.handle.write((self.get_command_string(commandName) % parametersTuple) + self.terminationCharacters)
            return self.handle.read(SERIAL_READ_SIZE)
        elif self.communicationProtocol is 'ethernet':
            return self.handle.ask(self.get_command_string(commandName) % parametersTuple)


    def connect(self):
        if self.communicationProtocol is 'serial':
            # Set up serial port depending on operating system according to Prologix instructions
            if platform == MAC_OSX_ALIAS: 
                for serialAddress in SERIAL_ADDRESSES_OSX:
                    try:
                        print 'Connecting to %s...' % serialAddress
                        self.handle = serial.Serial(serialAddress, baudrate=SERIAL_BAUDRATE, timeout=self.serialTimeout)
                        print 'Connected.'
                    except:
                        print 'Could not connect to %s.' %serialAddress
                self.handle.read(SERIAL_READ_SIZE)
            elif platform == WINDOWS_ALIAS:
                self.handle = serial.Serial(SERIAL_ADDRESS_WINDOWS, baudrate=SERIAL_BAUDRATE, timeout=self.serialTimeout)
            elif platform == LINUX_ALIAS or platform == LINUX2_ALIAS:
                print 'This library has not been tested on Linux. Attempting to connect using OSX protocol: '
                self.handle = serial.Serial(SERIAL_ADDRESS_OSX, baudrate=SERIAL_BAUDRATE, timeout=self.serialTimeout)

            #set Prologix GPIB USB to controller mode
            self.handle.write('++mode 1\n')
            self.handle.read(SERIAL_READ_SIZE)
            #set GPIB address. Most instruments have default GPIB addresses of 5. Since we are actually making a serial connection, I think this is unncessary. Should possibly remove this later. 
            self.handle.write('++addr 5\n')
            self.handle.read(SERIAL_READ_SIZE)

        elif self.communicationProtocol is 'ethernet':
            #check if device can connect via ethernet
            if self.ipAddress is None:
                print 'Error. This instrument has not been configured to connect via ethernet. Please specify the instrument\'s IP address in its corresponding JSON file.'
            else:
                self.handle = visa.instrument(self.ipAddress)
                #set termination characters so instrument knows when to stop listening and execute a command
                self.handle.term_chars = self.terminationCharacters

    def disconnect(self):
        if self.communicationProtocol is 'serial':
            self.handle.close()
        elif self.communicationProtocol is 'ethernet':
            self.handle.close()

    def get_id(self):
        return self.send_command('get_id')

    def reset(self):
        return self.send_command('reset')

#dc power supply class
class DCPowerSupply(Instrument):
    def get_version(self):
        return self.send_command('get_version')

    def set_output(self, output):
        self.send_command('set_output', output)

    def set_voltage(self, voltage):
        self.send_command('set_voltage', voltage)

    def set_current(self, current):
        self.send_command('set_current', current)

    def get_voltage(self):
        return self.send_command('get_voltage')

    def get_current(self):
        return self.send_command('get_current')

    def get_programmed_voltage(self):
        return self.send_command('get_programmed_voltage')

    def get_programmed_current(self):
        return self.send_command('get_programmed_current')

    def set_range(self, range):
        self.send_command('set_range', range)

#electronic load class
class ElectronicLoad(Instrument):
    def set_input(self, input):
        self.send_command('set_input', input)

    def set_voltage(self, voltage):
        self.send_command('set_voltage', voltage)

    def set_current(self, current):
        self.send_command('set_current', current)

    def set_resistance(self, resistance):
        self.send_command('set_resistance', resistance)

    def set_range_current(self, range):
        self.send_command('set_range_current', range)

    def set_range_resistance(self, range):
        self.send_command('set_range_resistance', range)

    def set_slew_voltage(self, slew):
        self.send_command('set_slew_voltage', slew)

    def set_slew_current(self, slew):
        self.send_command('set_slew_current', slew)

    def set_mode(self, mode):
        self.send_command('set_mode', mode)

    def get_programmed_voltage(self):
        return self.send_command('get_programmed_voltage')

    def get_programmed_current(self):
        return self.send_command('get_programmed_current')

    def get_programmed_resistance(self):
        return self.send_command('get_programmed_resistance')

    def get_voltage(self):
        return self.send_command('get_voltage')

    def get_current(self):
        return self.send_command('get_current')

    def get_power(self):
        return self.send_command('get_power')

#specific instrument classes
#dc power supplies
class AgilentE3631A(DCPowerSupply):
    def set_voltage_and_current(self, range, voltage, current):
        self.send_command('set_voltage_and_current', range, voltage, current)

class AgilentE3633A(DCPowerSupply):
    def set_voltage_and_current(self, voltage, current):
        self.send_command('set_voltage_and_current', voltage, current)

    def set_voltage_limit(self, voltageLimit):
        self.send_command('set_voltage_limit', voltageLimit)

    def set_current_limit(self, currentLimit):
        self.send_command('set_current_limit', currentLimit)

#electronic loads
class Agilent6060B(ElectronicLoad):
    def get_error(self):
        return self.send_command('get_error')
