MTest
======
## Description

A python library for instrumentation control. 

## Dependencies

* Python 2.7.5
* PyVISA
* NI-VISA 5.4.1 

## Installation

OSX:

1. Install NI-VISA 5.4.1: http://www.ni.com/download/ni-visa-5.4.1/4631/en/

2. Install python dependencies: pip install -r requirements.txt

3. Add the following line to your ~/.profile: alias python32='arch -i386 /usr/bin/python2.7'
   This creates an alias for 32-bit python. You will need to call all functions from 32-bit
   python since NI-VISA is a 32-bit library. 

## Example: Quick capture from Tektronix MSO 4104B-L Oscilloscope.

1. Turn on Tektronix MSO 4104B-L

2. Connect computer to Tektronix MSO 4104B-L via USB

3. Connect USB storage device to left USB port on Tektronix MSO 4104B-L front panel

4. Open terminal

5. cd [path to MTest/]

6. python32 tekCapture.py

This should save 3 files (waveforms, image, and settings) to the USB storage device


