#
# j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different pockage)
#
# BlackHarmonyRouteInfo
# Copyright (c) 2boom 2012-13
# v.0.8
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# <widget source="session.CurrentService" render="Label" position="189,397" zPosition="4" size="50,20" valign="center" halign="center" font="Regular;14" foregroundColor="foreground" transparent="1"  backgroundColor="background">
#	<convert type="RouteInfo">Info</convert>
# </widget>
#<widget source="session.CurrentService" render="Pixmap" pixmap="750HD/icons/ico_lan_on.png" position="1103,35" zPosition="1" size="28,15" transparent="1" alphatest="blend">
#    <convert type="RouteInfo">Lan  | Wifi | Modem</convert>
#    <convert type="ConditionalShowHide" />
#  </widget>

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Converter.Converter import Converter
from Components.Element import cached

class j00zekModRouteInfo(Converter, object):
	Info = 0
	Lan = 1
	Wifi = 2
	Modem = 3

	def __init__(self, type):
		Converter.__init__(self, type)
		if type == "Info":
			self.type = self.Info
		elif type == "Lan":
			self.type = self.Lan
		elif type == "Wifi":
			self.type = self.Wifi
		elif type == "Modem":
			self.type = self.Modem

	@cached
	def getBoolean(self):
		info = False
		for line in open("/proc/net/route"):
			if self.type == self.Lan and line.split()[0] == "eth0" and line.split()[3] == "0003":
				info = True
			elif self.type == self.Wifi and (line.split()[0] == "wlan0" or line.split()[0] == "ra0") and line.split()[3] == "0003":
				info = True
			elif self.type == self.Modem and line.split()[0] == "ppp0" and line.split()[3] == "0003":
				info = True
		return info
		
	boolean = property(getBoolean)
	
	@cached
	def getText(self):
		info = ""
		for line in open("/proc/net/route"):
			if self.type == self.Info and line.split()[0] == "eth0" and line.split()[3] == "0003":
				info = "lan"
			elif self.type == self.Info and  (line.split()[0] == "wlan0" or line.split()[0] == "ra0") and line.split()[3] == "0003":
				info = "wifi"
			elif self.type == self.Info and line.split()[0] == "ppp0" and line.split()[3] == "0003":
				info = "3g"
		return info

	text = property(getText)

	def changed(self, what):
		Converter.changed(self, what)
