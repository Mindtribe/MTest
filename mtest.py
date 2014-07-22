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

    def get_version(self):
        return self.handle.ask(self.get_command('get_version'))

    def reset(self):
        return self.handle.ask(self.get_command('reset'))