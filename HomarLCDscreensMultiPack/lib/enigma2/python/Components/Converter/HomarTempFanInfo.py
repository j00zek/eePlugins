#
# j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different package)
#
#
#  CPU/SYS TEMP and FAN RPM Info
#
#  Coded by tomele for Kraven Skins
#  Thankfully inspired by different unknown authors
#
#  This code is licensed under the Creative Commons 
#  Attribution-NonCommercial-ShareAlike 3.0 Unported 
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ 
#  or send a letter to Creative Commons, 559 Nathan 
#  Abbott Way, Stanford, California 94305, USA.
#

from Components.config import config
from Components.Converter.Converter import Converter
from Components.Element import cached
from enigma import iServiceInformation, iPlayableService
from Poll import Poll
from os import path

class HomarTempFanInfo(Poll, Converter, object):
	TEMPINFO = 0
	FANINFO = 1

	def __init__(self, type):
		Poll.__init__(self)
		Converter.__init__(self, type)
		self.type = type
		self.poll_interval = 2000
		self.poll_enabled = True
		if type == 'TempInfo':
			self.type = self.TEMPINFO
		elif type == 'FanInfo':
			self.type = self.FANINFO

	@cached
	def getText(self):
		textvalue = ''
		if self.type == self.TEMPINFO:
			textvalue = self.tempfile()
		elif self.type == self.FANINFO:
			textvalue = self.fanfile()
		return textvalue

	text = property(getText)

	def tempfile(self):
		systemp = "N/A"
		try:
			if path.exists('/proc/stb/sensors/temp0/value'):
				f = open('/proc/stb/sensors/temp0/value', 'rb')
				systemp = str(f.readline().strip())
				f.close()
			elif path.exists('/proc/stb/fp/temp_sensor'):
				f = open('/proc/stb/fp/temp_sensor', 'rb')
				systemp = str(f.readline().strip())
				f.close()
			elif path.exists('/proc/stb/sensors/temp/value'):
				f = open('/proc/stb/sensors/temp/value', 'rb')
				systemp = str(f.readline().strip())
				f.close()
			elif path.exists('/proc/stb/fp/temp_sensor_avs'):
				f = open('/proc/stb/fp/temp_sensor_avs', 'rb')
				systemp = str(f.readline().strip())
				f.close()
			elif path.exists('/sys/devices/virtual/thermal/thermal_zone0/temp'):
				f = open('/sys/devices/virtual/thermal/thermal_zone0/temp', 'rb')
				systemp = str(f.readline().strip())
				systemp = systemp[:-3]
				f.close()
		except:
			pass
		if systemp != "N/A":
			if len(systemp) > 2:
				systemp = systemp[:2]
			systemp = systemp + str('\xc2\xb0') + "C"
		return systemp

	def fanfile(self):
		faninfo = "N/A"
		try:
			if path.exists('/proc/stb/fp/fan_speed'):
				f = open('/proc/stb/fp/fan_speed', 'rb')
				faninfo = str(f.readline().strip())
				f.close()
		except:
			pass
		if faninfo != "N/A":
			faninfo = faninfo[:-4]
		return faninfo

