# for localized messages
from . import _

import os
import enigma
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigYesNo, ConfigSelection
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.ActionMap import ActionMap, HelpableActionMap
from Screens.HelpMenu import HelpableScreen
from Components.Button import Button
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor
from Components.Pixmap import Pixmap, MultiPixmap
from Components.ScrollLabel import ScrollLabel

# Configuration
config.plugins.hddsleep = ConfigSubsection()
config.plugins.hddsleep.enabled = ConfigYesNo(default = False)
delay=[("0",_("none")),("30",_("30 seconds")),("60",_("1 minute")),
	("180",_("3 minutes")),("300",_("5 minutes")),
	("600",_("10 minutes")),("900",_("15 minutes")),("1200",_("20 minutes")),
	("1800",_("30 minutes")),("3600",_("60 minutes"))]
config.plugins.hddsleep.sda = ConfigSelection(default = "0", choices = delay)
config.plugins.hddsleep.sdb = ConfigSelection(default = "0", choices = delay)
config.plugins.hddsleep.sdc = ConfigSelection(default = "0", choices = delay)
config.plugins.hddsleep.sdd = ConfigSelection(default = "0", choices = delay)
config.plugins.hddsleep.sde = ConfigSelection(default = "0", choices = delay)
config.plugins.hddsleep.logfile = ConfigYesNo(default = False)

# PATH variables
SCRIPT 	= "/usr/lib/enigma2/python/Plugins/Extensions/HddSleep/hddsleep.sh"
DEFAULT = "/etc/enigma2/hddsleep"
LINK    = "/etc/rcS.d/S99hddsleep"
TEMP 	= "/tmp/hddsleep.tmp"
LOG 	= "/tmp/hddsleep.log"

# Global
version = "1.72" # plugin made by IMS
cfg = config.plugins.hddsleep

#items in menu
#       0      1      2      3      4      5     6       7
DEV = [ None, 'sda', 'sdb', 'sdc', 'sdd', 'sde', None , 'path']
FIRST = 1
LAST = 6 #( 5 + 1 )
PATH = 7

SET_AUTORUN = "ln -s %s %s" % (SCRIPT,LINK)

# set hd-idle as arch tool
if not os.path.exists('/usr/bin/hd-idle'):
	arch = os.popen("uname -m").read()
	if 'mips' in arch:
		MIPS = "/usr/lib/enigma2/python/Plugins/Extensions/HddSleep/bin/mips/hd-idle"
		if os.path.exists(MIPS):
			os.chmod(MIPS, 755)
			os.system("cp %s /usr/bin/hd-idle" % MIPS)
	elif 'armv7l' in arch:
		ARMV71 = "/usr/lib/enigma2/python/Plugins/Extensions/HddSleep/bin/armv7l/hd-idle"
		if os.path.exists(ARMV71):
			os.chmod(ARMV71, 755)
			os.system("cp %s /usr/bin/hd-idle" % ARMV71)
	elif 'sh4' in arch:
		SH4 = "/usr/lib/enigma2/python/Plugins/Extensions/HddSleep/bin/sh4/hd-idle"
		if os.path.exists(SH4):
			os.chmod(SH4, 755)
			os.system("cp %s /usr/bin/hd-idle" % SH4)
	try:
		os.chmod(SCRIPT, 755)
	except Exception:
		pass

hdIdle_bin = "/usr/bin/hd-idle"

##################################
# Configuration GUI

class HddSleep(ConfigListScreen, Screen, HelpableScreen):
	skin = """
<screen position="center,center" size="620,400" title="HddSleep Configuration" >
	<ePixmap name="red"    position="0,0"   zPosition="2" size="40,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
	<ePixmap name="green"  position="150,0" zPosition="2" size="40,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
	<ePixmap name="yellow" position="300,0" zPosition="2" size="40,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" /> 
	<ePixmap name="blue"   position="450,0" zPosition="2" size="40,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" /> 

	<widget name="key_red" position="45,0" size="160,40" valign="center" halign="left" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
	<widget name="key_green" position="195,0" size="160,40" valign="center" halign="left" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
	<widget name="key_yellow" position="345,0" size="160,40" valign="center" halign="left" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
	<widget name="key_blue" position="495,0" size="160,40" valign="center" halign="left" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" shadowColor="background" shadowOffset="-2,-2" />

	<widget name="config" position="30,40" size="520,200" scrollbarMode="showOnDemand"/>

	<ePixmap pixmap="skin_default/div-h.png" position="0,250" zPosition="1" size="560,2" />

	<widget name="devices" position="10,265" size="200,25" font="Regular;20" />
	<widget name="mounted" position="240,265" size="310,120" font="Regular;20" />

	<ePixmap pixmap="~/author.png" position="10,305" zPosition="2" size="25,25" />
	<widget name="version" position="40,310" size="100,20" zPosition="2" foregroundColor="white" font="Regular;16" /> 

	<widget name="process" position="10,345" size="90,25" font="Regular;20" />
	<widget name="daemon0" alphatest="on" pixmap="skin_default/buttons/button_green_off.png" position="100,349" size="15,16" zPosition="10" transparent="1"/>
	<widget name="daemon1" alphatest="on" pixmap="skin_default/buttons/button_green.png" position="100,349" size="15,16" zPosition="10" transparent="1"/>

	<ePixmap pixmap="skin_default/div-h.png" position="0,376" zPosition="1" size="560,2" />
	<ePixmap alphatest="on" pixmap="skin_default/icons/clock.png" position="480,383" size="14,14" zPosition="3"/>
	<widget font="Regular;18" halign="left" position="505,380" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
		<convert type="ClockToText">Default</convert>
	</widget>
	<widget name="statusbar" position="10,380" size="470,20" font="Regular;18"  zPosition="1" />
	
	<widget name="0" pixmaps="skin_default/buttons/button_green_off.png,skin_default/buttons/button_green.png" position="10,43" zPosition="10" size="15,16" transparent="1" alphatest="on"/>
	<widget name="1" pixmaps="skin_default/buttons/button_blue_off.png,skin_default/buttons/button_blue.png" position="10,68" zPosition="10" size="15,16" transparent="1" alphatest="on"/>
	<widget name="2" pixmaps="skin_default/buttons/button_blue_off.png,skin_default/buttons/button_blue.png" position="10,93" zPosition="10" size="15,16" transparent="1" alphatest="on"/>
	<widget name="3" pixmaps="skin_default/buttons/button_blue_off.png,skin_default/buttons/button_blue.png" position="10,118" zPosition="10" size="15,16" transparent="1" alphatest="on"/>
	<widget name="4" pixmaps="skin_default/buttons/button_blue_off.png,skin_default/buttons/button_blue.png" position="10,143" zPosition="10" size="15,16" transparent="1" alphatest="on"/>
	<widget name="5" pixmaps="skin_default/buttons/button_blue_off.png,skin_default/buttons/button_blue.png" position="10,168" zPosition="10" size="15,16" transparent="1" alphatest="on"/>
	<widget name="6" pixmaps="skin_default/buttons/button_green_off.png,skin_default/buttons/button_green.png" position="10,193" zPosition="10" size="15,16" transparent="1" alphatest="on"/>
</screen>"""


	def __init__(self, session, plugin_path):
		self.skin = HddSleep.skin
		self.session = session
		self.skin_path = plugin_path
		self.setup_title = _("HDD Sleep")
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)

		self.epgpath = None
		try:    #some images does not using this value
			self.epgpath = config.misc.epgcache_filename 
		except Exception as e:
			print("[hddsleep] your image does not using epg path")

		try:
			epgcachefilename = config.plugins.epgrefresh_extra.epgcachefilename
		except Exception as e:
			epgcachefilename = None

		if epgcachefilename:
			self.epgpath = None
			print("[hddsleep] your image install plugin epgrefresh for using epg path")

		self.devInfo = []
		self.getDeviceInfo()

		menu = [
			getConfigListEntry(_("Enable sleeping"), cfg.enabled),
			getConfigListEntry("%s %s%s      %s" % (_("Sleep time for"),"/dev/",DEV[1],self.devInfo[0][0]), cfg.sda),
			getConfigListEntry("%s %s%s      %s" % (_("Sleep time for"),"/dev/",DEV[2],self.devInfo[1][0]), cfg.sdb),
			getConfigListEntry("%s %s%s      %s" % (_("Sleep time for"),"/dev/",DEV[3],self.devInfo[2][0]), cfg.sdc),
			getConfigListEntry("%s %s%s      %s" % (_("Sleep time for"),"/dev/",DEV[4],self.devInfo[3][0]), cfg.sdd),
			getConfigListEntry("%s %s%s      %s" % (_("Sleep time for"),"/dev/",DEV[5],self.devInfo[4][0]), cfg.sde),
			getConfigListEntry(_("Create log file"), cfg.logfile),
			]
		if self.epgpath is not None:
			menu1 = [getConfigListEntry(_("Path for epg.dat"), self.epgpath),]
			configList = menu + menu1
		else:
			configList = menu
		
		ConfigListScreen.__init__(self, configList, session=self.session, on_change = self.changedEntry)

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Save & Exit"))
		self["key_yellow"] = Button()
		self["key_blue"] = Button()
		self["devices"] = Label(_("Mounted devices:"))
		self["mounted"] = ScrollLabel()
		self["process"] = Label(_("Process:"))
		self["version"] = Label()
		self["statusbar"] = Label()
		self["daemon0"] = Pixmap()
		self["daemon0"].hide()
		self["daemon1"] = Pixmap()
		self["daemon1"].hide()

		for i in range(LAST+1): # 0-6
			self["%s" % (i)] = MultiPixmap()

		if self.epgpath is not None:
			self["HddSleepActions"] = HelpableActionMap(self, "HddSleepActions",
			{
				"red": ( self.cancel, _("close plugin")),
				"green": ( self.save, _("save configuration and exit")),
				"blue": ( self.sleepNow, _("sleep selected device")),
				"yellow": ( self.setEPG, _("store Epg.dat on selected device")),
				"cancel": ( self.cancel, _("close plugin")),
				"ok": ( self.save, _("save configuration and exit")),
				"scrollup": ( self["mounted"].pageUp, _("list of mounted devices up")),
				"scrolldown": ( self["mounted"].pageDown, _("list of mounted devices down")),
			}, -2)
		else:
			self["HddSleepActions"] = HelpableActionMap(self, "HddSleepActions",
			{
				"red": ( self.cancel, _("close plugin")),
				"green": ( self.save, _("save configuration and exit")),
				"blue": ( self.sleepNow, _("sleep selected device")),
				"cancel": ( self.cancel, _("close plugin")),
				"ok": ( self.save, _("save configuration and exit")),
				"scrollup": ( self["mounted"].pageUp, _("list of mounted devices up")),
				"scrolldown": ( self["mounted"].pageDown, _("list of mounted devices down")),
			}, -2)
		self.cfg_changes = False
		self.onChangedEntry = []
		self.mnt = {}
		self.idx = 0
		self.isRunning = 0
		if not os.path.exists('/usr/bin/hd-idle'):
			self.setTitle(_("HddSleep: not found tool hd-idle!"))
		else:
			self.setTitle(_("HddSleep Configuration"))
		self.onShown.append(self.prepare)
		self["config"].onSelectionChanged.append(self.configPosition)

	def changedEntry(self):
		self.setIcon(self.idx)
		for x in self.onChangedEntry:
			x()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary

	def prepare(self):
		self.getMount()
		self.isRunning = self.getDaemonStatus()
		self.daemonIcon()
		self.redrawIcons()
		self.info()
		self["version"].setText(_("Version") + ": %s" % (version))

	def configPosition(self):
		self.idx=self["config"].getCurrentIndex()
		self.setButtonText()

	def setButtonText(self):
		self["key_blue"].setText("")
		self["key_yellow"].setText("")
		if self.idx in range (FIRST,LAST): # 1-5
			if self.isMounted(self.idx):
				self["key_blue"].setText(_("Sleep") + " %s" % (DEV[self.idx]))
				if self.epgpath is not None:
					self["key_yellow"].setText(_("Epg.dat here"))
				self.info(self.devInfo[self.idx-1][1])
			else:
				self.info()
		elif self.idx == PATH and self.epgpath is not None:
			self["key_yellow"].setText(_("Default path"))
		else:
			self.info()

	def setEPG(self):
		if self.epgpath is not None:
			if self.idx in range(FIRST,LAST):
				if DEV[self.idx] in self.mnt:
					config.misc.epgcache_filename.value = self.mnt[DEV[self.idx]]+"/epg.dat"
					self["config"].invalidate(self["config"].list[PATH])
					self.epgMsg()
			elif self.idx == PATH:
				config.misc.epgcache_filename.value = config.misc.epgcache_filename.default
				self["config"].invalidate(self["config"].list[PATH])
				self.epgMsg()

	def epgMsg(self):
		if config.misc.epgcache_filename.value != config.misc.epgcache_filename.default:
			self.session.open(MessageBox, _("Before uninstall this plugin set epg.dat path back to default!"), MessageBox.TYPE_INFO, timeout=6)

	def sleepNow(self):
		if self.idx in range(FIRST,LAST):
			if DEV[self.idx] in self.mnt:
				os.system("hd-idle -t %s" % (DEV[self.idx]))

	def setIcon(self, idx):
		if idx == PATH:
			return
		if self["config"].list[idx][1].getValue() == "0" or self["config"].list[idx][1].getValue() == False:
			self["%s" % (idx)].setPixmapNum(0)
		else:
			self["%s" % (idx)].setPixmapNum(1)

	def redrawIcons(self):
		for i in range(LAST+1): # 0-6
			self.setIcon(i)

	def getDeviceInfo(self):
		for i in range(FIRST,LAST):
			self.devInfo.insert(i,[self.getDeviceType(DEV[i]),self.getDeviceName(DEV[i])])

	def readFile(self, filename):
		file = open(filename)
		data = file.read().strip()
		file.close()
		return data

	def getDeviceName(self, dev):
		model = "/sys/block/%s/device/model" % (dev)
		vendor = "/sys/block/%s/device/vendor" % (dev)
		try: return self.readFile(vendor) + " " + self.readFile(model)
		except Exception as e:
			return ""

	def getDeviceType(self, dev):
		hdd = self.removableDevice(dev)
		if hdd == "0":
			return "HDD"
		return ""

	def removableDevice(self,dev):
		removable = "/sys/block/%s/removable" % (dev)
		try: return self.readFile(removable)
		except Exception as e:
			return "-1"

	def getMount(self):
		devices = []
		for line in open('/proc/mounts','r'):
			items = line.split()
			if items[0].startswith('/dev/sd'):
				self.mnt[items[0][5:-1]] = items[1]
				devices.append("%s  %s  %s\n" % (items[0][5:],_("on"), items[1]))
		devices.reverse()
		tmp = ""
		for disk in devices:
			tmp += disk
		self["mounted"].setText(tmp)

	def isMounted(self, i):
		if DEV[i] in self.mnt:
			return 1
		return 0

	def autoRun(self): 
		os.system(SET_AUTORUN)
		print("[hddsleep] created link for autorun")

	def getDaemonStatus(self):
		os.system("pidof hd-idle > %s" % (TEMP))
		try:
			fd = open(TEMP,"r")
			if fd:
				test = fd.readline()
				#fd.close()
				os.unlink(TEMP)
				if test == "\n" or test == "":
					return 0
				else:
					return 1
		except Exception as e:
			print("[hddsleep] isRunning FAIL:", e)
			return 0

	def runDaemon(self):
		self.setParams()
		cmd = SCRIPT
		if self.isRunning:
			cmd +=  " restart"
		else:
			cmd +=  " start"
		return cmd

	def run(self):
		print("[hddsleep] start of hd-idle")
		os.system(self.runDaemon())

	def isAutorun(self): 
		if os.path.exists(LINK):
			return True
		else:
			return False

	def info(self, text = ""):
		if not self.isAutorun():
			self["statusbar"].setText(_("Autorun is disabled!") + "    %s" % text)
		elif text == "":
			self["statusbar"].setText(_("Autorun is enabled :)"))
		else:
			self["statusbar"].setText("%s" % text)

	def daemonIcon(self):
		if self.isRunning:
			self["daemon0"].hide()
			self["daemon1"].show()
		else:
			self["daemon1"].hide()
			self["daemon0"].show()

	def stopDaemon(self):
		cmd = SCRIPT + " stop"
		return cmd

	def stop(self):
		print("[hddsleep] canceling of hd-idle")
		os.system('rm -f %s' % LINK)
		os.system(self.stopDaemon())

	def save(self):
		self.setParams()
		if not self.isAutorun():
			self.autoRun()
		if cfg.enabled.value:
			self.run()
		else:
			self.stop()
		self.keySave()

	def cancel(self):
		self.keyCancel()

	# Parameters
	def setParams(self):
		enabled = "true"
		if not cfg.enabled.value:
			enabled = "false"
		line_1 = "START_HD_IDLE=%s" % (enabled)

#		line  = "HD_IDLE_OPTS="
		line_2 = "HD_IDLE_OPTS="
		line_2 += "'\"'"
		if cfg.sda.value != "0":
			line_2 += " -a sda -i %s" % (cfg.sda.value)
		if cfg.sdb.value != "0":
			line_2 += " -a sdb -i %s" % (cfg.sdb.value)
		if cfg.sdc.value != "0":
			line_2 += " -a sdc -i %s" % (cfg.sdc.value)
		if cfg.sdd.value != "0":
			line_2 += " -a sdd -i %s" % (cfg.sdd.value)
		if cfg.sde.value != "0":
			line_2 += " -a sde -i %s" % (cfg.sde.value)
		if cfg.logfile.value:
			line_2 += " -l %s" % (LOG)
		line_2 += "'\"'"
		print(line_2)
		try:
			#so much slow
#			file = open(DEFAULT, "w")
#			file.write("%s\n%s\"%s\"" % (line_1,line,line_2))
#			file.close()
			os.system("echo %s >  %s" % (line_1,DEFAULT))
			os.system("echo %s >> %s" % (line_2,DEFAULT))
			os.system("chmod 644 %s" % (DEFAULT))

		except Exception as e:
			print("[hddsleep] setParam FAIL:", e)

def HddSleepMain(session, **kwargs):
	session.open(HddSleep, plugin_path)

##################################

def Plugins(path,**kwargs):
	global plugin_path
	plugin_path = path
	result = [PluginDescriptor(name= _("HddSleep"),description = _("HDD sleeptime settings"),where = PluginDescriptor.WHERE_PLUGINMENU,icon = 'plugin.png',fnc = HddSleepMain)]
	return result
