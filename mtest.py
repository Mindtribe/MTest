import json
import os
import glob
import visa
from sys import platform
import mechanize
import time
import csv
import shutil
from BeautifulSoup import BeautifulSoup as soup

#iniitalize resource manager to help find connected devices. This is required to properly initialize the INSTRUMENT_ADDRESSES global variable.
rm = visa.ResourceManager()

#globals
INSTRUMENT_DIRECTORY = '/Users/Andrew/MTest/instruments/'
INSTRUMENT_ADDRESSES = [address for address in rm.list_resources()]
MAC_OSX_ALIAS = 'darwin'
WINDOWS_ALIAS = 'win32'
LINUX_ALIAS = 'linux'
LINUX2_ALIAS = 'linux2'

print '\nFinding instrument addresses\n(This process may throw AttributeError Exceptions, which can be ignored)\n'
#remove busy addresses
for instrumentAddress in INSTRUMENT_ADDRESSES:
    try:
        temporaryHandle = visa.instrument(instrumentAddress)
    except:
        INSTRUMENT_ADDRESSES.remove(instrumentAddress)
        pass

#base class
class Instrument(object):

    def __init__(self, name, communicationProtocol='serial', instrumentAddress=None):
        self.name = name
        self.communicationProtocol = communicationProtocol
        self.instrumentAddress = instrumentAddress
        instrumentFile = open(os.path.join(INSTRUMENT_DIRECTORY, name + '.json'))
        instrumentFileDict = json.load(instrumentFile)
        self.parametersDict = instrumentFileDict['parameters']
        self.id = str(self.parametersDict['id'])
        self.terminationCharacters = str(self.parametersDict['terminationCharacters'])
        if self.parametersDict['ipAddress'] == 'None':
            self.ipAddress = None
        else:
            self.ipAddress = self.parametersDict['ipAddress']
        if self.parametersDict['timeout'] == 'None':
            self.timeout = 0
        else:
            self.timeout = float(self.parametersDict['timeout'])
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

    def send_read_command(self, commandName, *parameters):
        """
        This function sends commands that are meant to receive and return data from the instrument. 
        Accordingly, pyvisa's ask() function is used rather than its write() function. Note that time.sleep
        is called in order to explicitly allow the instrument enough time to process the command before 
        another command can be sent.  
        """
        #form parameters tuple
        parametersTuple = ()
        for parameter in parameters:
            #note that we typecast all parameters as strings here
            parametersTuple += (str(parameter),)
        result = self.handle.ask(self.get_command_string(commandName) % parametersTuple)
        #wait for instrument to process command
        time.sleep(self.timeout)
        return result

    def send_write_command(self, commandName, *parameters):
        """
        This function sends commands that are not meant to receive or return data from the instrument. 
        Accordingly, pyvisa's write() function is used rather than its ask() function. Note that time.sleep
        is called in order to explicitly allow the instrument enough time to process the command before
        another command can be sent. 
        """
        #form parameters tuple
        parametersTuple = ()
        for parameter in parameters:
            #note that we typecast all parameters as strings here
            parametersTuple += (str(parameter),)
        self.handle.write(self.get_command_string(commandName) % parametersTuple)
        #wait for instrument to process command
        time.sleep(self.timeout)

    def connect(self):
        if (self.communicationProtocol is 'serial') or (self.communicationProtocol is 'usb'):
            if self.instrumentAddress is not None:
                #if user specified instrument address, try connecting to it
                try:
                    self.handle = visa.instrument(self.instrumentAddress)
                    #set termination characters so instrument knows when to stop listening and execute a command
                    self.handle.term_chars = self.terminationCharacters
                    if self.get_id() == self.id:
                        print '%s connected to %s.' % (self.name, self.instrumentAddress)
                    else:
                        #wrong instrument
                        raise Exception('The instrument you are attempting to connect to does not match its corresponding object class')
                        self.disconnect()                    
                except:
                    print 'Could not connect to %s.' % self.instrumentAddress

            else:
                #if user did not specify instrument address, try connecting to all available addresses
                for instrumentAddress in INSTRUMENT_ADDRESSES:
                    if self.instrumentAddress is None:
                        try:
                            self.handle = visa.instrument(instrumentAddress)
                            #set termination characters so instrument knows when to stop listening and execute a command
                            self.handle.term_chars = self.terminationCharacters
                            if self.get_id() == self.id:
                                print '%s connected to %s.' % (self.name, instrumentAddress)
                                self.instrumentAddress = instrumentAddress
                                break
                            else:
                                #wrong instrument
                                self.disconnect()
                        except:
                            pass

        elif self.communicationProtocol is 'ethernet':
            #check if device can connect via ethernet
            if self.ipAddress is None:
                print 'Error. This instrument has not been configured to connect via ethernet. Please specify the instrument\'s IP address in its corresponding JSON file.'
            else:
                try:
                    self.handle = visa.instrument(self.ipAddress)
                    #set termination characters so instrument knows when to stop listening and execute a command
                    self.handle.term_chars = self.terminationCharacters
                    if self.get_id() == self.id:
                        print '%s connected to %s.' % (self.name, self.ipAddress)
                    else:
                        #wrong instrument
                        raise Exception('The instrument you are attempting to connect to does not match its corresponding object class')
                        self.disconnect()
                except:
                    print 'Could not connect to %s.' % ipAddress

    def disconnect(self):
        self.handle.close()

    def get_id(self):
        return self.send_read_command('get_id')

    def reset(self):
        self.send_write_command('reset')

#dc power supply class
class DCPowerSupply(Instrument):
    def set_output(self, output):
        self.send_write_command('set_output', output)

    def set_voltage(self, voltage):
        self.send_write_command('set_voltage', voltage)

    def set_current(self, current):
        self.send_write_command('set_current', current)

    def get_version(self):
        return self.send_read_command('get_version')

    def get_voltage(self):
        return float(self.send_read_command('get_voltage'))

    def get_current(self):
        return float(self.send_read_command('get_current'))

    def get_programmed_voltage(self):
        return float(self.send_read_command('get_programmed_voltage'))

    def get_programmed_current(self):
        return float(self.send_read_command('get_programmed_current'))

#electronic load class
class ElectronicLoad(Instrument):
    def set_input(self, input):
        self.send_write_command('set_input', input)

    def set_voltage(self, voltage):
        self.send_write_command('set_voltage', voltage)

    def set_current(self, current):
        self.send_write_command('set_current', current)

    def set_resistance(self, resistance):
        self.send_write_command('set_resistance', resistance)

    def set_range_current(self, range):
        self.send_write_command('set_range_current', range)

    def set_range_resistance(self, range):
        self.send_write_command('set_range_resistance', range)

    def set_slew_voltage(self, slew):
        self.send_write_command('set_slew_voltage', slew)

    def set_slew_current(self, slew):
        self.send_write_command('set_slew_current', slew)

    def set_mode(self, mode):
        self.send_write_command('set_mode', mode)

    def get_programmed_voltage(self):
        return float(self.send_read_command('get_programmed_voltage'))

    def get_programmed_current(self):
        return float(self.send_read_command('get_programmed_current'))

    def get_programmed_resistance(self):
        return float(self.send_read_command('get_programmed_resistance'))

    def get_voltage(self):
        return float(self.send_read_command('get_voltage'))

    def get_current(self):
        return float(self.send_read_command('get_current'))

    def get_power(self):
        return float(self.send_read_command('get_power'))

#oscilloscope class
class Oscilloscope(Instrument):
    def get_screen_capture(self):
        self.send_write_command('get_screen_capture')

#specific instrument classes
#dc power supplies
class AgilentE3631A(DCPowerSupply):
    def set_voltage_and_current(self, range, voltage, current):
        self.send_write_command('set_voltage_and_current', range, voltage, current)

    def select_output(self, output):
        self.send_write_command('select_output', output)

class AgilentE3633A(DCPowerSupply):
    def set_voltage_and_current(self, voltage, current):
        self.send_write_command('set_voltage_and_current', voltage, current)

    def set_voltage_limit(self, voltageLimit):
        self.send_write_command('set_voltage_limit', voltageLimit)

    def set_current_limit(self, currentLimit):
        self.send_write_command('set_current_limit', currentLimit)

    def set_range(self, range):
        self.send_write_command('set_range', range)

#electronic loads
class Agilent6060B(ElectronicLoad):
    def set_transient_voltage(self, voltage):
        self.send_write_command('set_transient_voltage', voltage)

    def set_transient_current(self, current):
        self.send_write_command('set_transient_current', current)

    def set_transient_resistance(self, resistance):
        self.send_write_command('set_transient_resistance', resistance)   

    def get_error(self):
        return self.send_read_command('get_error')

#oscilloscopes
class TektronixMSO4104BL(Oscilloscope):
    """Saves all 4 channels to a csv file and saves a screenshot as a png image."""

    def get_screen_capture(self):
        if (self.communicationProtocol is 'usb') or (self.communicationProtocol is 'serial'):
            #globals
            WAIT_TIME = 0.5
            OUTPUT_WAVEFORMS_FILENAME = 'waveforms'
            OUTPUT_SCREENCAPTURE_FILENAME = 'screenCapture'
            OUTPUT_WAVEFORMS_FILE_EXTENSION = '.csv'
            OUTPUT_SCREENCAPTURE_FILE_EXTENSION = '.png'

            #send stop command to freeze waveforms
            self.handle.write("ACQuire:STATE STOP")

            drives = ['E:', 'F:']
            #attempt to write to both drives so the user does not have to specify which USB port they connected their thumb drive to
            for drive in drives:
                #create unique timestamped filename
                timestr = time.strftime('%Y%m%d-%H%M%S')
                #create directory to save screen captures and final csv file with all channel waveforms
                outputDir = os.path.join(drive, timestr + '-scope-capture')
                self.handle.write("FILESystem:MKDir \"" + outputDir + "\"")

                #save waveforms
                waveformsFilename = os.path.join(outputDir, OUTPUT_WAVEFORMS_FILENAME + OUTPUT_WAVEFORMS_FILE_EXTENSION)
                self.handle.write("SAVE:WAVEFORM ALL,\"" + waveformsFilename + "\"")
                while '1' in self.handle.ask("BUSY?"):
                        time.sleep(WAIT_TIME)

                #save screencapture
                screenCaptureFilename = os.path.join(outputDir, OUTPUT_SCREENCAPTURE_FILENAME + OUTPUT_SCREENCAPTURE_FILE_EXTENSION)
                self.handle.write("SAVE:IMAGE \"" + screenCaptureFilename + "\"")
                while '1' in self.handle.ask("BUSY?"):
                        time.sleep(WAIT_TIME)

            #send run command to unfreeze waveforms
            self.handle.write("ACQuire:STATE RUN")

        elif self.communicationProtocol is 'ethernet':
            #globals
            CHANNELS = ['ch1', 'ch2', 'ch3', 'ch4']
            OUTPUT_FORMAT = 'spreadsheet'
            OUTPUT_WAVEFORMS_FILENAME = 'waveforms'
            OUTPUT_SCREENCAPTURE_FILENAME = 'screenCapture'
            OUTPUT_WAVEFORMS_FILE_EXTENSION = '.csv'
            OUTPUT_SCREENCAPTURE_FILE_EXTENSION = '.png'
            ROW_OFFSET = 19

            #send stop command to freeze waveforms
            self.handle.write("ACQuire:STATE STOP")

            #create unique timestamped filename
            timestr = time.strftime('%Y%m%d-%H%M%S')
            #create temporary directory for individual channel waveform csv files
            tmpDir = timestr + '-scope-capture-tmp'
            os.mkdir(tmpDir)
            #create directory to save screen captures and final csv file with all channel waveforms
            outputDir = timestr + '-scope-capture'
            os.mkdir(outputDir)

            #save waveform to csv for each channel
            for channel in CHANNELS:
                br = mechanize.Browser()
                br.open('http://192.168.171.84:81/data/mso_data4.html')
                br.select_form(name='firstForm')
                channelControl = br.find_control('command')
                channelControl.value = ['select:control ' + channel]
                fileFormatControl = br.find_control('command1')
                fileFormatControl.value = ['save:waveform:fileformat ' + OUTPUT_FORMAT]
                response = br.submit()
                outputFile = open(os.path.join(tmpDir, channel + OUTPUT_WAVEFORMS_FILE_EXTENSION), "wb")
                outputFile.write(response.read())
                outputFile.close()

            #combine all csv channel waveform files into one
            csvDict = {}
            for channel in CHANNELS:
                f = open(os.path.join(tmpDir, channel + OUTPUT_WAVEFORMS_FILE_EXTENSION), 'rb')
                reader = csv.reader(f)
                rows = []
                for rowNumber, row in enumerate(reader):
                    if rowNumber < ROW_OFFSET:
                        rows.append(row)
                    else:
                        if len(row) > 0:
                            rows.append(row)
                csvDict[channel] = rows
                f.close()

            #check to make sure that all csv files had the same number of rows
            numRows = len(csvDict[CHANNELS[0]])
            for key in csvDict:
                if len(csvDict[key]) != numRows:
                    raise Exception('Error: The number of rows in the csv files for individual channels are not equal.')

            waveformsFilename = os.path.join(outputDir, OUTPUT_WAVEFORMS_FILENAME + OUTPUT_WAVEFORMS_FILE_EXTENSION)
            fout = open(waveformsFilename, 'wb')
            writer = csv.writer(fout)
            for row in range(numRows):
                rowList = []
                for numChannel, channel in enumerate(CHANNELS):
                    if row < ROW_OFFSET:
                        if numChannel is 0:
                            rowList += csvDict[channel][row]
                    else:
                        if numChannel is 0:
                            rowList += csvDict[channel][row]
                        else:
                            rowList += [csvDict[channel][row][1]]
                writer.writerow(rowList)

            #delete temporary directory
            shutil.rmtree(tmpDir)

            #get screencapture
            br = mechanize.Browser()
            html = br.open('http://192.168.171.84:81/control/control.html')
            bsoup = soup(html)
            image_tags = bsoup.findAll('img', {'id': 'thescreen'})
            image = image_tags[0]
            screenCaptureFilename = os.path.join(outputDir, OUTPUT_SCREENCAPTURE_FILENAME + OUTPUT_SCREENCAPTURE_FILE_EXTENSION)
            data = br.open(image['src']).read()
            br.back()
            save = open(screenCaptureFilename, 'wb')
            save.write(data)
            save.close()

            #send run command to unfreeze waveforms
            self.handle.write("ACQuire:STATE RUN")

