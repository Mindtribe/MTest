import mechanize
import visa
import os
import time
import csv
import shutil
from BeautifulSoup import BeautifulSoup as soup

#globals
CHANNELS = ['ch1', 'ch2', 'ch3', 'ch4']
OUTPUT_FORMAT = 'spreadsheet'
OUTPUT_WAVEFORMS_FILENAME = 'waveforms'
OUTPUT_FILE_EXTENSION = '.csv'
ROW_OFFSET = 19

#set up connection to scope over LAN
scope = visa.instrument("TCPIP::192.168.171.84")
#send stop command to freeze waveforms
scope.write("ACQuire:STATE STOP")

#create unique timestamped filename
timestr = time.strftime("%Y%m%d-%H%M%S")
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
	outputFile = open(os.path.join(tmpDir, channel + OUTPUT_FILE_EXTENSION), "wb")
	outputFile.write(response.read())
	outputFile.close()

#combine all csv channel waveform files into one
csvDict = {}
for channel in CHANNELS:
	f = open(os.path.join(tmpDir, channel + OUTPUT_FILE_EXTENSION), 'rb')
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

fout = open(os.path.join(outputDir, OUTPUT_WAVEFORMS_FILENAME + OUTPUT_FILE_EXTENSION), 'wb')
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
# filename = image['src'].lstrip('http://')
# filename = os.path.join(outputDir, filename.replace('/', '_'))
screenCaptureFilename = os.path.join(outputDir, 'screenCapture.png')
data = br.open(image['src']).read()
br.back()
save = open(screenCaptureFilename, 'wb')
save.write(data)
save.close()

#send run command to unfreeze waveforms
scope.write("ACQuire:STATE RUN")
