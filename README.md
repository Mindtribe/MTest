MTest
======


## Description

A python library for instrumentation control

By: Alex Omid-Zohoor 

Released August 2014


## Dependencies

* Python 2.7.5
* PyVISA 1.5
* mechanize 0.2.5
* BeautifulSoup 3.2.1
* NI-VISA 5.4.1 


## Installation

OSX:

1. Download and install sublimetext: http://www.sublimetext.com

2. To install git (an open source version control system), open a terminal and type the following command: git

  If the terminal outputs documentation for git, you already have git installed. But if the terminal instead brings up a prompt, go ahead and download and install command line tools. This will install git. 

3. To clone this MTest code repository, open a terminal and type the following commands:  
  cd ~
  git clone https://github.com/MindTribe/MTest.git

  You should now have a directory called MTest in your home directory. 
  
4. To install pip (an open source python package manager), open a terminal window and type the following command: sudo easy_install pip  
  
  This should install pip to the following location: /usr/local/bin/pip
  
5. To install python dependencies, open a terminal window, and type the following commands:  
  cd ~/MTest 
  sudo pip install -r requirements.txt

6. In order be able to call mtest.py from anywhere, you must change the value of the INSTRUMENT_DIRECTORY global variable in MTest/mtest.py. To do this, open a finder window, and from the menu toolbar select Go->Go To Folder... Enter "~/MTest" and click "Go". Right click mtest.py and select Open With sublimetext. Change the line:

  INSTRUMENT_DIRECTORY = './MTest/instruments'

  To:

  INSTRUMENT_DIRECTORY = '/Users/alex/MTest/instruments'

  Where alex is a placeholder for your computer's username. For example, on Andy's computer this might be '/Users/andy/MTest/instruments'

7. Install NI-VISA 5.4.1: smb://mt-data/Software/MTestInstallers/NI/OSX/NI-VISA-5.4.1.dmg

8. Install the Prologix GPIB-USB Controller 6.0 USB Driver for OSX: smb://mt-data/Software/MTestInstallers/Prologix/OSX/64-bit/FTDIUSBSerialDriver_v2_2_18.dmg

9. Add path to the MTest directory to PYTHONPATH. This can be done by adding the following line to
   your ~/.bash_profile: export PYTHONPATH="\<path to MTest\>:$PYTHONPATH"

10. Add the following line to your ~/.bash_profile: alias python32='arch -i386 /usr/bin/python2.7'
   This creates an alias for 32-bit python. You will need to call all functions from 32-bit
   python since NI-VISA is a 32-bit library

WINDOWS: Note that this set of instructions is rough. If you are having trouble, please grab someone from the Software team. 

1. Install NI-VISA 5.4.1: smb://mt-data/Software/MTestInstallers/NI/WINDOWS/NIVISA541full_downloader.exe

2. To install python dependencies, you will need pip. If you do not already have pip installed, you will need to install it: https://pip.pypa.io/en/latest/installing.html

  Once pip is installed, cd into the MTest/ directory and run the following command: pip install -r requirements.txt

3. Add path to the MTest directory to PYTHONPATH. This can be done by going to 
   My Computer > Properties > Advanced System Settings > Environment Variables >
   Then under system variables, create a new Variable called PYTHONPATH, and set the 
   Variable value to <path to MTest>. Or if PYTHONPATH already exists, simply append
   <path to MTest> to the end of the Variable value

4. Install the Prologix GPIB-USB Controller 6.0 USB Driver for WINDOWS: smb://mt-data/Software/MTestInstallers/Prologix/WINDOWS/CDM20828_Setup.exe 

5. In order to call mtest.py from anywhere, set the value of the INSTRUMENT_DIRECTORY global variable in 
   MTest/mtest.py to the absolute path of MTest/instruments. Otherwise you will only be able to call
   mtest.py from MTest/


## Instruments

Currently supported instruments include:

1. Agilent E3631A (DC Power Supply)
2. Agilent E3633A (DC Power Supply)
3. Agilent 6060B (Electronic Load)
4. Tektronix MSO 4104B-L (Oscilloscope)

Excluded instruments failed to meet at least one of the following criteria:

1. Remote controllable via serial, usb, or ethernet
2. Useful in an automated test setting. (For example, some older oscilloscopes are remote controllable but can only store waveform data on antiquated local storage media such as CompactFlash. Since this media can only hold a few screenshots and waveforms, it is not useful for longterm automated testing)

Instrument representation:

Each supported instrument is represented by a json file in the MTest/instruments directory with the same name as the instrument. These json files contain a python dictionary with two main keys called 'parameters' and 'commands'. The 'parameters' entry contains information about the instrument itself such as:

id: The identification string of the instrument. This is the string that the instrument sends when asked to identify itself (for many instruments, the command to ask an instrument to identify itself is "*IDN?")

ipAddress: The IP address of the instrument if it is able to connect via ethernet

terminationCharacters: Characters used by the instrument to indicate the end of a message (see instrument's User's Manual)

timeout: Time to wait between sending instrument commands, since it takes instruments some time to receive and process commands. A good value for this parameter can be determined experimentally by writing a test script that sends several commands in a row and checks to see if the commands were properly executed. 

The 'commands' entry is effectively a lookup table for various instrument commands. Each key, which is the name of a python function in mtest.py, corresponds to a value, which is a python dictionary that contains information about the command itself such as:

commandString: The string that is sent to the instrument to execute the command. Note that % placeholders are used for arguments that must be specified by the user at runtime

arguments: Brief description of the arguments that the command takes

description: Description of the command copied from the instrument's User Manual or Programming Manual


## Organization 

mtest.py is organized in an object-oriented fashion, where each instrument inherits properties from a base class of Instrument. 
Subclasses of Instrument currently include DCPowerSupply, Oscilloscope, and ElectronicLoad. Subclasses of these classes are 
individual instruments themselves, such as Agilent6060B, AgilentE3633A, AgilentE3631A, and TektronixMSO4104BL. 

* Instrument
  * DCPowerSupply
    * AgilentE3633A
    * AgilentE3631A
  * ElectronicLoad
    * Agilent6060B
  * Oscilloscope
    * TektronixMSO4104BL

This structure was mainly chosen to keep the code organized and scalable. The level of code reuse is minor, as each time a new 
instrument is added a custom JSON file must be created in MTest/instruments. However, this structure can help guide the process
of adding a new instrument. For example, all instruments inherit from the base instrument class, and thus must contain commands
for the Instrument methods of get_id() and reset(). All instruments that inherit from the DCPowerSupply class must include a
command for set_voltage(), etc.
## Examples

In the following examples, '\>\>' indicates a terminal, command prompt, or python prompt command. 

Confirm successful installation of mtest python module:

1. Open terminal in OSX or command prompt in WINDOWS

2. Start 32-bit python: 

	OSX: \>\> python32   
	WINDOWS: \>\> python 

3. \>\> import mtest

4. If the module imports without raising an ImportError, installation was successful

Quick capture from Tektronix MSO4104B-L Oscilloscope:

1. Turn on Tektronix MSO 4104B-L

2. Open terminal in OSX or command prompt in WINDOWS

3. Start 32-bit python: 

	OSX: \>\> python32   
	WINDOWS: \>\> python 

4. \>\> import mtest

5. \>\> osc = mtest.TektronixMSO4104BL('TektronixMSO4104BL', 'ethernet')

6. \>\> osc.get_screen_capture()

7. This should create a timestamped directory with a csv file containing the waveform data of all 4 channels and a screenshot png image

# Useful Commands

When using mtest interactively from the terminal, the print_commands(), print_command_description(), and print_command_arguments() functions may be helpful. 

print_commands(): prints all commands associated with a given instrument

print_command_description(commandName): prints the description associated with a given command

print_command_arguments(commandName): prints the arguments that a given command takes

Here is an example output:

\>\> import mtest
\>\> ps = mtest.AgilentE3633A()
\>\> ps.print_commands()
reset
set_voltage_and_current
set_range
get_current
get_version
set_current_limit
get_programmed_current
get_id
set_voltage
set_voltage_limit
get_voltage
get_programmed_voltage
set_current
set_output
\>\> ps.print_command_description('set_output')
This command enables or disables the outputs of the power supply. When the output is disabled, the voltage value is 0 V and the current value is 20 mA. At *RST, the output state is OFF.
\>\> ps.print_command_arguments('set_output')
output {OFF|ON}

## Scripts

There are a number of test and functional scripts in the MTest/scripts directory. Test scripts are meant to test the ability
to control specific instruments with mtest, as well as determine the minimum instrument timeout (if relevant). When adding
a new instrument to MTest, one should also create a corresponding test script. Functional scripts, such as batteryCycle.py, are
template scripts that can be used for automated testing. 


## Creating Your Own Script

To create your own script, you will need a plain text editor, and basic familiarity with Python. Sublimetext (http://www.sublimetext.com/) is one possible free and cross-platform plain text editor, but any plain text editor (e.g. TextEdit for OSX or NotePad for Windows) will do. Just make sure that you do not use a rich text editor like Microsoft Word. If you are unfamiliar with Python and would like to learn more, you can find a good online introductory course here: https://developers.google.com/edu/python/. The following is an example of how to create and run a basic script that uses mtest. 

1. Open your favorite plain text editor and create a new document. 

2. Save this document to a directory as powersupply.py. For this example, we'll assume the directory is your Desktop folder.

3. Add the following lines to the file:

  import mtest #imports the mtest module  
    
  ps = mtest.AgilentE3633A('AgilentE3633A') #creates an AgilentE3633A object named ps  
  print ps.get_id() #asks ps to identify itself and prints the id string to the terminal  
  ps.set_voltage(1) #sets the voltage of ps to 1 Volt  

4. Save the file. 

5. Open a terminal. On OSX, you can simply search for terminal in spotlight. On Windows, from the start menu search bar, search for cmd and open cmd.exe

6. Navigate to the directory where your script exists using the 'cd' command

7. Connect your computer to an AgilentE3633A power supply using the Prologix GPIB-USB Controller 6.0, and turn on the AgilentE3633A power supply. 

8. Run your script from the terminal. On OSX, use the command: python32 powersupply.py. On Windows, use the command: python powersupply.py. 

9. This is should run your script. You should see the following string printed to the terminal: 'HEWLETT-PACKARD,E3633A,0,2.1-6.1-2.1'. Then, the voltage of the AgilentE3633A should be set to 1 Volt. 

IMPORTANT:

Note that mtest is designed to use an explicit 'timeout' after any command is sent. This 'timeout' parameter is set per instrument in the instrument's corresponding json file. The default values should be sufficient, but if your script is not working, it may be because you are issueing commands too fast and the instrument is unable to execute one command before the next one is sent. In order to resolve this problem, you can increase the 'timeout' parameter. If this description is unclear, please grab someone from the Software team. 




