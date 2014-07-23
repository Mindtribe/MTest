import mechanize

#globals
CHANNEL = 'ch1'
OUTPUT_FORMAT = 'spreadsheet'
OUTPUT_FILENAME = 'ch1.csv'

br = mechanize.Browser()
br.open('http://192.168.171.84:81/data/mso_data4.html')
br.select_form(name='firstForm')
channelControl = br.find_control('command')
channelControl.value = ['select:control ' + CHANNEL]
fileFormatControl = br.find_control('command1')
fileFormatControl.value = ['save:waveform:fileformat ' + OUTPUT_FORMAT]
response = br.submit()
fileobj = open(OUTPUT_FILENAME, "wb")
fileobj.write(response.read())