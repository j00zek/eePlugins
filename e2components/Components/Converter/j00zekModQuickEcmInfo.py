# QuickEcmInfo converter (c) 2boom 2012-13 v 1.0.2 
#<widget source="session.CurrentService" render="Label" position="462,153" size="50,22" font="Regular; 17" zPosition="2" backgroundColor="background1" foregroundColor="white" transparent="1">
#    <convert type="QuickEcmInfo">ecmfile | emuname | caids</convert>
#  </widget>
#
#  j00zek: this file has changed name just to avoid errors using opkg (situation when file was installed by different pockage)
#          All credits go to its author(s)
# 

from Components.Converter.Converter import Converter
from Components.Converter.Poll import Poll
from enigma import eTimer, iPlayableService, iServiceInformation, eServiceReference, iServiceKeys, getDesktop
from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry, ConfigText, ConfigPassword, ConfigClock, ConfigSelection, ConfigSubsection, ConfigYesNo, configfile, NoSave
from Components.Element import cached
from Tools.Directories import fileExists
import os
try:
	from bitratecalc import eBitrateCalculator
except Exception:
	pass

class j00zekModQuickEcmInfo(Poll, Converter, object):
	ecmfile = 0
	emuname = 1
	caids = 2
	pids = 3
	vtype = 4
	activecaid = 5
	bitrate = 6
	txtcaid = 7
	
	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		if type == "ecmfile":
			self.type = self.ecmfile
		elif type == "emuname":
			self.type = self.emuname
		elif type == "caids":
			self.type = self.caids
		elif type == "pids":
			self.type = self.pids
		elif type == "vtype":
			self.type = self.vtype
		elif type == "activecaid":
			self.type = self.activecaid
		elif type == "bitrate":
			self.type = self.bitrate
		elif type == "txtcaid":
			self.type = self.txtcaid
		self.poll_interval = 1000
		self.poll_enabled = True
		self.clearData()
		self.initTimer = eTimer()
		self.initTimer.callback.append(self.initBitrateCalc)
		
		self.systemTxtCaids = {
			"26" : "BiSS",
			"01" : "Seca Mediaguard",
			"06" : "Irdeto",
			"17" : "BetaCrypt",
			"05" : "Viaccess",
			"18" : "Nagravision",
			"09" : "NDS-Videoguard",
			"0B" : "Conax",
			"0D" : "Cryptoworks",
			"4A" : "DRE-Crypt",
			"27" : "ExSet",
			"0E" : "PowerVu",
			"22" : "Codicrypt",
			"07" : "DigiCipher",
			"56" : "Verimatrix",
			"7B" : "DRE-Crypt",
			"A1" : "Rosscrypt"}

	def getServiceInfoString(self, info, what, convert = lambda x: "%d" % x):
		v = info.getInfo(what)
		if v == -1:
			return "N/A"
		if v == -2:
			return info.getInfoString(what)
		return convert(v)
		
	def getServiceInfoString2(self, info, what, convert = lambda x: "%d" % x):
		v = info.getInfo(what)
		if v == -3:
			t_objs = info.getInfoObject(what)
			if t_objs and (len(t_objs) > 0):
				ret_val=""
				for t_obj in t_objs:
					ret_val += "%.4X " % t_obj
				return ret_val[:-1]
			else:
				return ""
		return convert(v)
		
	def clearData(self):
		self.videoBitrate = None
		self.audioBitrate = None
		self.video = self.audio = 0

	def initBitrateCalc(self):
		service = self.source.service
		vpid = apid = dvbnamespace = tsid = onid = -1
		if service:
			serviceInfo = service.info()
			vpid = serviceInfo.getInfo(iServiceInformation.sVideoPID)
			apid = serviceInfo.getInfo(iServiceInformation.sAudioPID)
			tsid = serviceInfo.getInfo(iServiceInformation.sTSID)
			onid = serviceInfo.getInfo(iServiceInformation.sONID)
			dvbnamespace = serviceInfo.getInfo(iServiceInformation.sNamespace)
		if vpid > 0 and self.type == self.bitrate:
			try:
				self.videoBitrate = eBitrateCalculator(vpid, dvbnamespace, tsid, onid, 1000, 1024*1024) 
				self.videoBitrate.callback.append(self.getVideoBitrateData)
			except Exception:
				pass
		if apid > 0 and self.type == self.bitrate:
			try:
				self.audioBitrate = eBitrateCalculator(apid, dvbnamespace, tsid, onid, 1000, 64*1024)
				self.audioBitrate.callback.append(self.getAudioBitrateData)
			except Exception:
				pass
		
	def caidstr(self):
		caidvalue = ""
		value = "0000"
		service = self.source.service
		info = service and service.info()
		if not info:
			return ""
		if self.getServiceInfoString(info, iServiceInformation.sCAIDs):
			if fileExists("/tmp/ecm.info"):
				try:
					for line in open("/tmp/ecm.info"):
						if line.find("caid:") > -1:
							caidvalue = line.strip("\n").split()[-1][2:]
							if len(caidvalue) < 4:
								caidvalue = value[len(caidvalue):] + caidvalue
						elif line.find("CaID") > -1 or line.find("CAID") > -1:
							caidvalue = line.split(",")[0].split()[-1][2:]
				except Exception:
					pass
		return caidvalue
		
	@cached
	def getText(self):
		ecminfo = ""
		caidvalue = ""
		service = self.source.service
		info = service and service.info()
		if not info:
			return ""
			
		if self.type == self.vtype:
			try:
				return ("MPEG2", "MPEG4", "MPEG1", "MPEG4-II", "VC1", "VC1-SM", "")[info.getInfo(iServiceInformation.sVideoType)]
			except Exception: 
				return " "
			
		elif self.type == self.bitrate:
			try:
				audio = service and service.audioTracks()
				if audio:
					if audio.getCurrentTrack() > -1:
						if self.audio != 0 or self.video != 0:
							audioTrackCodec = str(audio.getTrackInfo(audio.getCurrentTrack()).getDescription()) or ""
						else:
							audioTrackCodec = ""
				else:
					audioTrackCodec = ""
				yres = info.getInfo(iServiceInformation.sVideoHeight)
				mode = ("i", "p", "")[info.getInfo(iServiceInformation.sProgressive)]
				xres = info.getInfo(iServiceInformation.sVideoWidth)
				return "%sx%s(%s) VIDEO %s: %d kbit/s  AUDIO %s: %d kbit/s" % (str(xres), str(yres) + mode, self.getServiceInfoString(info, iServiceInformation.sFrameRate, lambda x: "%d" % ((x+500)/1000)), ("MPEG2", "MPEG4", "MPEG1", "MPEG4-II", "VC1", "VC1-SM", "")[info.getInfo(iServiceInformation.sVideoType)], self.video, audioTrackCodec, self.audio)
				#return "%sx%s(%s) VIDEO %s: %d kbit/s  AUDIO %s: %d kbit/s" % (str(xres), str(yres) + mode, self.getServiceInfoString(info, iServiceInformation.sFrameRate, lambda x: "%d" % ((x+500)/1000)), ("MPEG2", "MPEG4", "MPEG1", "MPEG4-II", "VC1", "VC1-SM", "")[info.getInfo(iServiceInformation.sVideoType)], self.video,str(audio.getTrackInfo(audio.getCurrentTrack()).getDescription()), self.audio)
			except Exception: 
				return " "
		elif self.type == self.txtcaid:
			caidvalue = "%s" % self.systemTxtCaids.get(self.caidstr()[:2].upper()) 
			if caidvalue != "None":
				return caidvalue
			else:
				return " "
			
		elif self.type == self.ecmfile:
			if self.getServiceInfoString(info, iServiceInformation.sCAIDs):
				try:
					ecmfiles = open("/tmp/ecm.info", "r")
					for line in ecmfiles:
						if line.find("caid:") > -1 or line.find("provider:") > -1 or line.find("provid:") > -1 or line.find("pid:") > -1 or line.find("hops:") > -1  or line.find("system:") > -1 or line.find("address:") > -1 or line.find("using:") > -1 or line.find("ecm time:") > -1:
							line = line.replace(' ',"").replace(":",": ")
						if line.find("caid:") > -1 or line.find("pid:") > -1 or line.find("reader:") > -1 or line.find("from:") > -1 or line.find("hops:") > -1  or line.find("system:") > -1 or line.find("Service:") > -1 or line.find("CAID:") > -1 or line.find("Provider:") > -1:
							line = line.strip('\n') + "  "
						if line.find("Signature") > -1:
							line = ""
						if line.find("=") > -1:
							line = line.lstrip('=').replace('======', "").replace('\n', "").rstrip() + ', '
						if line.find("ecmtime:") > -1:
							line = line.replace("ecmtime:", "ecm time:")
						if line.find("response time:") > -1:
							line = line.replace("response time:", "ecm time:").replace("decoded by", "by")
						if not line.startswith('\n'):
							if line.find('pkey:') > -1:
								line = '\n' + line + '\n'
							ecminfo += line
					ecmfiles.close()
					#if fileExists("/tmp/pid.info"):
						#for line in open("/tmp/pid.info"):
							#ecminfo += line
				except Exception:
					pass
###############################################################################
		elif self.type == self.activecaid:
			caidvalue = self.caidstr()
			return caidvalue
					
		elif self.type == self.pids:
			
			try:
				return "SID: %0.4X  VPID: %0.4X  APID: %0.4X  PRCPID: %0.4X  TSID: %0.4X  ONID: %0.4X" % (int(self.getServiceInfoString(info, iServiceInformation.sSID)), int(self.getServiceInfoString(info, iServiceInformation.sVideoPID)), int(self.getServiceInfoString(info, iServiceInformation.sAudioPID)), int(self.getServiceInfoString(info, iServiceInformation.sPCRPID)), int(self.getServiceInfoString(info, iServiceInformation.sTSID)), int(self.getServiceInfoString(info, iServiceInformation.sONID)))
			except Exception:
				try:
					return "SID: %0.4X  APID: %0.4X  PRCPID: %0.4X  TSID: %0.4X  ONID: %0.4X" % (int(self.getServiceInfoString(info, iServiceInformation.sSID)), int(self.getServiceInfoString(info, iServiceInformation.sAudioPID)), int(self.getServiceInfoString(info, iServiceInformation.sPCRPID)), int(self.getServiceInfoString(info, iServiceInformation.sTSID)), int(self.getServiceInfoString(info, iServiceInformation.sONID)))
				except Exception:
					try:
						return "SID: %0.4X  VPID: %0.4X  PRCPID: %0.4X  TSID: %0.4X  ONID: %0.4X" % (int(self.getServiceInfoString(info, iServiceInformation.sSID)), int(self.getServiceInfoString(info, iServiceInformation.sVideoPID)), int(self.getServiceInfoString(info, iServiceInformation.sPCRPID)), int(self.getServiceInfoString(info, iServiceInformation.sTSID)), int(self.getServiceInfoString(info, iServiceInformation.sONID)))
					except Exception:
						return ""
			
		elif self.type == self.caids:
			array_caids = []
			try:
				ecminfo = self.getServiceInfoString2(info, iServiceInformation.sCAIDs)
				if ecminfo == "-1":
					return " "
				for caid in ecminfo.split():
					array_caids.append(caid)
				ecminfo = ' '.join(str(x) for x in set(array_caids))
			except Exception:
				ecminfo = " "
					
		if self.type == self.emuname:
			serlist = None
			camdlist = None
			nameemu = []
			nameser = []
			# Alternative SoftCam Manager 
			if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/AlternativeSoftCamManager/plugin.py"): 
				if config.plugins.AltSoftcam.actcam.value != "none": 
					return config.plugins.AltSoftcam.actcam.value 
				else: 
					return None
			# TS-Panel
			elif fileExists("/etc/startcam.sh"):
				try:
					for line in open("/etc/startcam.sh"):
						if line.find("script") > -1:
							return "%s" % line.split("/")[-1].split()[0][:-3]
				except Exception:
					camdlist = None
			# domica 8120
			elif fileExists("/etc/init.d/cam"):
				if config.plugins.emuman.cam.value: 
					return config.plugins.emuman.cam.value
			#PKT
			elif fileExists("//usr/lib/enigma2/python/Plugins/Extensions/PKT/plugin.pyo"):
				if config.plugins.emuman.cam.value: 
					return config.plugins.emuman.cam.value
			#HDMU
			elif fileExists("/etc/.emustart") and fileExists("/etc/image-version"):
				try:
					for line in open("/etc/.emustart"):
						return line.split()[0].split('/')[-1]
				except Exception:
					camdlist = None
			# AAF & ATV & VTI 
			elif fileExists("/etc/image-version") and not fileExists("/etc/.emustart"):
				emu = ""
				server = ""
				for line in open("/etc/image-version"):
					if line.find("=AAF") > -1 or line.find("=openATV") > -1:
						if config.softcam.actCam.value: 
							emu = config.softcam.actCam.value
						if config.softcam.actCam2.value: 
							server = config.softcam.actCam2.value
							if config.softcam.actCam2.value == "no CAM 2 active":
								server = ""
					elif line.find("=vuplus") > -1:
						if fileExists("/tmp/.emu.info"):
							for line in open("/tmp/.emu.info"):
								emu = line.strip('\n')
				return "%s %s" % (emu, server)
			# BlackHole	
			elif fileExists("/etc/CurrentBhCamName"):
				try:
					camdlist = open("/etc/CurrentBhCamName", "r")
				except Exception:
					camdlist = None
			# Domica	
			elif fileExists("/etc/active_emu.list"):
				try:
					camdlist = open("/etc/active_emu.list", "r")
				except Exception:
					camdlist = None
			#Pli
			elif fileExists("/etc/init.d/softcam") or fileExists("/etc/init.d/cardserver"):
				try:
					for line in open("/etc/init.d/softcam"):
						if line.find("echo") > -1:
							nameemu.append(line)
					camdlist = "%s" % nameemu[1].split('"')[1]
				except Exception:
					pass
				try:
					for line in open("/etc/init.d/cardserver"):
						if line.find("echo") > -1:
							nameser.append(line)
					serlist = "%s" % nameser[1].split('"')[1]
				except Exception:
					pass
				if serlist is None:
					serlist = ""
				elif camdlist is None:
					camdlist = ""
				elif serlist is None and camdlist is None:
					serlist = ""
					camdlist = ""
				return ("%s %s" % (serlist, camdlist))
			# OoZooN
			elif fileExists("/tmp/cam.info"):
				try:
					camdlist = open("/tmp/cam.info", "r")
				except Exception:
					camdlist = None
			# Merlin2	
			elif fileExists("/etc/clist.list"):
				try:
					camdlist = open("/etc/clist.list", "r")
				except Exception:
					camdlist = None
			# GP3
			elif fileExists("/usr/lib/enigma2/python/Plugins/Bp/geminimain/lib/libgeminimain.so"):
				try:
					from Plugins.Bp.geminimain.plugin import GETCAMDLIST
					from Plugins.Bp.geminimain.lib import libgeminimain
					camdl = libgeminimain.getPyList(GETCAMDLIST)
					for x in camdl:
						if x[1] == 1:
							camdlist = x[2] 
				except Exception:
					camdlist = None
			# Unknown emu
			else:
				camdlist = None
				
			if serlist is not None:
				try:
					cardserver = ""
					for current in serlist.readlines():
						cardserver = current
					serlist.close()
				except Exception:
					pass
			else:
				cardserver = ""

			if camdlist is not None:
				try:
					emu = ""
					for current in camdlist.readlines():
						emu = current
					camdlist.close()
				except Exception:
					pass
			else:
				emu = ""
			ecminfo = "%s %s" % (cardserver.split('\n')[0], emu.split('\n')[0])
		return ecminfo
		
	text = property(getText)
	
	def getVideoBitrateData(self, value, status):
		if status:
			self.video = value
		else:
			self.videoBitrate = None
			self.video = 0
		Converter.changed(self, (self.CHANGED_POLL,))

	def getAudioBitrateData(self, value, status):
		if status:
			self.audio = value
		else:
			self.audioBitrate = None
			self.audio = 0
		Converter.changed(self, (self.CHANGED_POLL,))

	def changed(self, what):
		if what[0] == self.CHANGED_SPECIFIC:
			if what[1] == iPlayableService.evStart:
				self.initTimer.start(200, True)
			elif what[1] == iPlayableService.evEnd:
				self.clearData()
				Converter.changed(self, what)
		elif what[0] == self.CHANGED_POLL:
			self.downstream_elements.changed(what)
