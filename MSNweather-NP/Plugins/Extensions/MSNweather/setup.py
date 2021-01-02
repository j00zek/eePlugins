# -*- coding: utf-8 -*-
#
# WeatherPlugin E2
#
# Coded by Dr.Best (c) 2012
# Support: www.dreambox-tools.info
# E-Mail: dr.best@dreambox-tools.info
#
# This plugin is open source but it is NOT free software.
#
# This plugin may only be distributed to and executed on hardware which
# is licensed by Dream Multimedia GmbH.
# In other words:
# It's NOT allowed to distribute any parts of this plugin or its source code in ANY way
# to hardware which is NOT licensed by Dream Multimedia GmbH.
# It's NOT allowed to execute this plugin and its source code or even parts of it in ANY way
# on hardware which is NOT licensed by Dream Multimedia GmbH.
#
# If you want to use or modify the code or parts of it,
# you have to keep MY license and inform me about the modifications by mail.
#

# for localized messages
from . import _

from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import ConfigSubsection, ConfigText, ConfigSelection, getConfigListEntry, config, configfile, ConfigEnableDisable, ConfigIP
from Components.GUIComponent import GUIComponent
from Components.MenuList import MenuList
from Components.Sources.StaticText import StaticText
from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, RT_VALIGN_CENTER
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from skin import parseFont
from xml.etree.cElementTree import fromstring as cet_fromstring
from twisted.web.client import getPage
from urllib import quote as urllib_quote
import os

DBG = False
if DBG: from debug import printDEBUG

def initWeatherPluginEntryConfig(i=0):
    s = ConfigSubsection()
    s.city = ConfigText(default = "Warszawa", visible_width = 100, fixed_size = False)
    if s.city.value == 'Warszawa' and os.path.exists('/hdd/User_Configs/city.%s' % i):
        s.city.value = open('/hdd/User_Configs/city.%s' % i, 'r').readline().strip()
    s.degreetype = ConfigSelection(choices = [("C", _("metric system")), ("F", _("imperial system"))], default = "C")
    s.weatherlocationcode = ConfigText(default = "", visible_width = 100, fixed_size = False)
    s.geolatitude = ConfigText(default = "auto", visible_width = 100, fixed_size = False)
    s.geolongitude = ConfigText(default = "auto", visible_width = 100, fixed_size = False)
    s.weatherSearchFullName = ConfigText(default = "", visible_width = 100, fixed_size = False)

    #thingspeak
    s.thingSpeakChannelID = ConfigText(default = "", visible_width = 100, fixed_size = False)
    if s.thingSpeakChannelID.value == '' and os.path.exists('/hdd/User_Configs/thingSpeakChannelID.%s' % i):
        s.thingSpeakChannelID.value = open('/hdd/User_Configs/thingSpeakChannelID.%s' % i, 'r').readline().strip()

    #airly
    s.airlyID = ConfigText(default = '', visible_width = 100, fixed_size = False)
    if s.airlyID.value == '' and os.path.exists('/hdd/User_Configs/airlyID.%s' % i):
        s.airlyID.value = open('/hdd/User_Configs/airlyID.%s' % i, 'r').readline().strip()

    s.Fcity =  ConfigText(default = '', visible_width = 100, fixed_size = False)
    s.Fmeteo =  ConfigText(default = '', visible_width = 100, fixed_size = False)

    if s.Fcity.value == '' and os.path.exists('/hdd/User_Configs/Fcity.%s' % i):
        s.Fcity.value = open('/hdd/User_Configs/Fcity.%s' % i, 'r').readline().strip()
    if s.Fmeteo.value == '' and os.path.exists('/hdd/User_Configs/Fmeteo.%s' % i):
        s.Fmeteo.value = open('/hdd/User_Configs/Fmeteo.%s' % i, 'r').readline().strip()

    config.plugins.MSNweatherNP.Entry.append(s)
    
    s.entryType = ConfigSelection(choices = [("main", _("local")), ("client", _("remote"))], default = "main")
    s.mainEntryADDR = ConfigIP(default = [0,0,0,0])
    s.mainEntryID = ConfigSelection(choices = [("0", "0"),("1", "1"),("2", "2"),("3", "3"),("4", "4"),("5", "6"),], default = "0")

    return s

def initConfig():
    count = config.plugins.MSNweatherNP.entrycount.value
    if count != 0:
        i = 0
        while i < count:
            initWeatherPluginEntryConfig(i)
            i += 1

class MSNWeatherEntriesListConfigScreen(Screen):
    skin = """
        <screen name="MSNWeatherEntriesListConfigScreen" position="center,center" size="550,400">
            <widget render="Label" source="city" position="5,60" size="400,50" font="Regular;20" halign="left"/>
            <widget render="Label" source="degreetype" position="410,60" size="130,50" font="Regular;20" halign="left"/>
            <widget name="entrylist" position="0,80" size="550,300" scrollbarMode="showOnDemand"/>
            <widget render="Label" source="key_red" position="0,10" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <widget render="Label" source="key_green" position="140,10" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="green" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <widget render="Label" source="key_yellow" position="280,10" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="yellow" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <widget render="Label" source="key_blue" position="420,10" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <ePixmap position="0,10" zPosition="4" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
            <ePixmap position="140,10" zPosition="4" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
            <ePixmap position="280,10" zPosition="4" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
            <ePixmap position="420,10" zPosition="4" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.title = _("MSN weather: List of Entries")
        self["city"] = StaticText(_("City"))
        self["degreetype"] = StaticText(_("System"))
        self["key_red"] = StaticText(_("Back"))
        self["key_green"] = StaticText(_("Add"))        
        self["key_yellow"] = StaticText(_("Edit"))
        self["key_blue"] = StaticText(_("Delete"))
        self["entrylist"] = WeatherEntryList([])
        self["actions"] = ActionMap(["WizardActions","MenuActions","ShortcutActions"],
            {
             "ok"    :    self.keyOK,
             "back"  :    self.keyClose,
             "red"   :    self.keyClose,
             "green" :    self.keyGreen,             
             "yellow":    self.keyYellow,
             "blue"  :    self.keyDelete,
             "menu"  :    self.keyMenu,
             }, -1)
        self.onLayoutFinish.append(self.__onLayoutFinish)
        
    def __onLayoutFinish(self):
        self.updateList()
        
    def updateList(self):
        self["entrylist"].buildList()

    def keyClose(self):
        self.close(-1, None)

    def keyMenu(self):
        self.session.openWithCallback(self.updateList,MSNWeatherConfiguration)

    def keyGreen(self):
        try:
            selIDXs = self["entrylist"].getListSize()
        except Exception as e:
            selIDXs = None
        self.session.openWithCallback(self.updateList,MSNWeatherEntryConfigScreen, None, None, selIDXs)

    def keyOK(self):
        try:sel = self["entrylist"].l.getCurrentSelection()[0]
        except: sel = None
        self.close(self["entrylist"].getCurrentIndex(), sel)

    def keyYellow(self):
        try:
            sel = self["entrylist"].l.getCurrentSelection()[0]
            selIDX = self["entrylist"].getCurrentIndex()
            selIDXs = self["entrylist"].getListSize()
        except:
            sel = None
        if sel is None:
            return
        self.session.openWithCallback(self.updateList,MSNWeatherEntryConfigScreen, sel, selIDX, selIDXs)

    def keyDelete(self):
        try:sel = self["entrylist"].l.getCurrentSelection()[0]
        except: sel = None
        if sel is None:
            return
        self.session.openWithCallback(self.deleteConfirm, MessageBox, _("Really delete this WeatherPlugin Entry?"))

    def deleteConfirm(self, result):
        if result:
            os.system('rm -f /tmp/.MSNdata/*')
            sel = self["entrylist"].l.getCurrentSelection()[0]
            config.plugins.MSNweatherNP.entrycount.value -= 1
            config.plugins.MSNweatherNP.entrycount.save()
            config.plugins.MSNweatherNP.Entry.remove(sel)
            config.plugins.MSNweatherNP.Entry.save()
            config.plugins.MSNweatherNP.save()
            configfile.save()
            self.updateList()
        return

class WeatherEntryList(MenuList):
    def __init__(self, list, enableWrapAround = True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        GUIComponent.__init__(self)
        
        #default values:
        self.font0 = gFont("Regular", 20)
        self.font1 = gFont("Regular", 18)
        self.itemHeight = 20
        self.DimText0 = (5, 0, 400, 20, 1)
        self.DimText1 = (410, 0, 80, 20, 1)

    def applySkin(self, desktop, parent):
        def font(value):
            self.font0 = parseFont(value, ((1,1),(1,1)))
            self.font1 = parseFont(value, ((1,1),(1,1)))
        def font0(value):
            self.font0 = parseFont(value, ((1,1),(1,1)))
        def font1(value):
            self.font1 = parseFont(value, ((1,1),(1,1)))
        def itemHeight(value):
            self.itemHeight = int(value)
        def DimText0(value):
            self.DimText0 = ( int(value.split(',')[0]), int(value.split(',')[1]), int(value.split(',')[2]), int(value.split(',')[3]), int(value.split(',')[4]) )
        def DimText1(value):
            self.DimText1 = ( int(value.split(',')[0]), int(value.split(',')[1]), int(value.split(',')[2]), int(value.split(',')[3]), int(value.split(',')[4]) )
          
        for (attrib, value) in list(self.skinAttributes):
            try:
                locals().get(attrib)(value)
                self.skinAttributes.remove((attrib, value))
            except Exception as e:
                pass
                
        self.l.setFont(0,self.font0)
        self.l.setFont(1,self.font1)
        self.l.setItemHeight(self.itemHeight)
        return GUIComponent.applySkin(self, desktop, parent)

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    def buildList(self):
        list = []
        for c in config.plugins.MSNweatherNP.Entry:
            res = [
                c,
                (eListboxPythonMultiContent.TYPE_TEXT, self.DimText0[0], self.DimText0[1], self.DimText0[2], self.DimText0[3], self.DimText0[4], RT_HALIGN_LEFT|RT_VALIGN_CENTER, str(c.city.value)),
                (eListboxPythonMultiContent.TYPE_TEXT, self.DimText1[0], self.DimText1[1], self.DimText1[2], self.DimText1[3], self.DimText1[4], RT_HALIGN_LEFT|RT_VALIGN_CENTER, str(c.degreetype .value)),
            ]
            list.append(res)
        self.list = list
        self.l.setList(list)
        self.moveToIndex(0)
        
    def getListSize(self):
        return len(self.list)
    
class MSNWeatherEntryConfigScreen(ConfigListScreen, Screen):
    skin = """
        <screen name="MSNWeatherPluginEntryConfigScreen" position="center,center" size="550,400">
            <widget name="config" position="20,60" size="520,300" scrollbarMode="showOnDemand" />
            <ePixmap position="0,10" zPosition="4" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
            <ePixmap position="140,10" zPosition="4" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
            <ePixmap position="420,10" zPosition="4" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
            <ePixmap position="280,10" zPosition="4" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
            <widget source="key_red" render="Label" position="0,10" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <widget source="key_green" render="Label" position="140,10" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <widget render="Label" source="key_yellow" position="280,10" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="yellow" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <widget source="key_blue" render="Label" position="420,10" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
        </screen>"""

    def __init__(self, session, entry, selIDX, selIDXs):
        Screen.__init__(self, session)
        self.title = _("WeatherPlugin: Edit Entry")
        self["actions"] = ActionMap(["SetupActions", "ColorActions"],
        {
            "green": self.keySave,
            "red": self.keyCancel,
            "blue": self.keyDelete,
            "yellow": self.searchLocation,
            "cancel": self.keyCancel,
            "ok": self.keyOK
        }, -2)

        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("Save"))
        self["key_blue"] = StaticText(_("Delete"))
        self["key_yellow"] = StaticText(_("Search Code"))

        self.selIDX = selIDX
        self.selIDXs = selIDXs
        
        if entry is None:
            self.newmode = 1
            if self.selIDXs is None:
                self.current = initWeatherPluginEntryConfig()
            else:
                self.current = initWeatherPluginEntryConfig(self.selIDXs)
        else:
            self.newmode = 0
            self.current = entry

        if not self.selIDX is None:
            if self.current.Fcity.value == '' and os.path.exists('/hdd/User_Configs/Fcity.%s' % self.selIDX):
                self.current.Fcity.value = open('/hdd/User_Configs/Fcity.%s' % self.selIDX, 'r').readline().strip()
            if self.current.Fmeteo.value == '' and os.path.exists('/hdd/User_Configs/Fmeteo.%s' % self.selIDX):
                self.current.Fmeteo.value = open('/hdd/User_Configs/Fmeteo.%s' % self.selIDX, 'r').readline().strip()
            if self.current.thingSpeakChannelID.value == '' and os.path.exists('/hdd/User_Configs/thingSpeakChannelID.%s' % self.selIDX):
                self.current.thingSpeakChannelID.value = open('/hdd/User_Configs/thingSpeakChannelID.%s' % self.selIDX, 'r').readline().strip()

        ConfigListScreen.__init__(self, [], session, on_change = self.changedEntry)
        self.buildList()

    def buildList(self):
        if self.current.entryType.value == "client":
            cfglist = [ getConfigListEntry(_("Entry type:"), self.current.entryType),
                        getConfigListEntry(_("Main plugin IP address:"), self.current.mainEntryADDR),
                        getConfigListEntry(_("Main plugin entry ID:"), self.current.mainEntryID),
            ]
        else:
            cfglist = [ getConfigListEntry(_("Entry type DON'T CHANGE:"), self.current.entryType),
                        getConfigListEntry(_("City"), self.current.city),
                        getConfigListEntry(_("Location code"), self.current.weatherlocationcode),
                        getConfigListEntry(_("Location Full name"), self.current.weatherSearchFullName),
                        getConfigListEntry(_("System"), self.current.degreetype),
                        getConfigListEntry(_("Geo Latitude"), self.current.geolatitude),
                        getConfigListEntry(_("Geo Longitude"), self.current.geolongitude),
                        getConfigListEntry('\c00289496' + _("--- OPTIONAL, NOT REQUIRED ---"), config.plugins.MSNweatherNP.FakeEntry),
                        getConfigListEntry(_("thingSpeak meteo channel ID"), self.current.thingSpeakChannelID),
                        getConfigListEntry(_("Airly installation ID (OK)"), self.current.airlyID),
                        getConfigListEntry(_("Meteogram for www.foreca.net/<this part>"), self.current.Fcity),
                        #getConfigListEntry(_("Location in www.foreca.com/<this part>"), self.current.Fmeteo),
                    ]
        self["config"].list = cfglist
    
    def changedEntry(self):
        self.buildList()
        
    def keyOK(self):
        #open("/tmp/.MSNdata/keyOK.log", "w").write('%s\n' % 'keyOK')
        curIndex = self["config"].getCurrentIndex()
        currItemCfg = self["config"].list[curIndex][1]
        currItemNam = self["config"].list[curIndex][0]
        if currItemCfg == self.current.airlyID:
            #open("/tmp/.MSNdata/keyOK.log", "a").write('%s\n' % 'currItemCfg == self.current.airlyID')
            try:
                float(self.current.geolatitude.value)
                float(self.current.geolongitude.value)
            except Exception:
                #open("/tmp/.MSNdata/keyOK.log", "a").write('%s\n' % 'float exception')
                from Screens.MessageBox import MessageBox
                self.session.openWithCallback(self.doNothing, MessageBox, _("Set proper latitude and longitude!!!"), MessageBox.TYPE_INFO, timeout=10)
                return
            if config.plugins.MSNweatherNP.airlyAPIKEY.value == '':
                infoTXT = _("Set airly API key using one of the following methods:\n")
                infoTXT += _("global plugin settings\n")
                infoTXT += _("/hdd/User_Configs/airlyAPIKEY file\n")
                infoTXT += _("/etc/enigma2/Airly/api.txt file\n")
                from Screens.MessageBox import MessageBox
                self.session.openWithCallback(self.doNothing, MessageBox, infoTXT, MessageBox.TYPE_INFO, timeout=10)
                return
            InstList = self.Airlyinstallations(currItemCfg.value)
            if len(InstList) > 0:
                from Screens.ChoiceBox import ChoiceBox
                if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/Airly'):
                    ChoiceBoxTitle = _("Airly plugin detected - API key CAN be BLOCKED!!!")
                else:
                    ChoiceBoxTitle = _("10 closest Airly installations")
                self.session.openWithCallback(self.AirlyinstallationIDret, ChoiceBox, title = ChoiceBoxTitle, list = InstList)
                return
            else:
                currItemNam = _('No airly installations within 20km distance, provide ID manually')
                self.session.openWithCallback(self.keyOKret, VirtualKeyBoard, title= currItemNam, text = currItemCfg.value)
        else:
            self.session.openWithCallback(self.keyOKret, VirtualKeyBoard, title= currItemNam, text = currItemCfg.value)
            return
        
    def doNothing(self, ret = None):
        pass
    
    def Airlyinstallations(self, currentAirlyID):
        InstList = []
        if currentAirlyID != '':
            InstList.append(('%s:\t%s' % (currentAirlyID, _('Current selection')), currentAirlyID))
        #pobieranie danych
        try:
            import urllib, urllib2
            opener = urllib2.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            opener.addheaders = [('Accept', 'application/json')]
            opener.addheaders = [('Accept-Language', 'en')]
            opener.addheaders = [('apikey', config.plugins.MSNweatherNP.airlyAPIKEY.value)]
            request = urllib2.Request('https://airapi.airly.eu/v2/installations/nearest?lat=%s&lng=%s&maxDistanceKM=20&maxResults=10' % (self.current.geolatitude.value, self.current.geolongitude.value))
            webContent = opener.open(request).read()
            webContent = urllib.unquote(webContent)
            #analiza przygotowane danych
            import json
            json_data = json.dumps(json.loads(webContent), indent=4, ensure_ascii=False)
            open("/tmp/.MSNdata/airly_installations.json", "w").write('%s\n' % json_data)
            installations = json.loads(webContent.decode('utf-8'))
            for inst in installations:
                try:
                    myID = str(inst['id'])
                    myAddress = inst['address']
                    try:
                        myCity = myAddress['city'].encode('utf-8', 'ignore')
                    except Exception:
                        myCity = ''
                    try:
                        myStreet = myAddress['street'].encode('utf-8', 'ignore')
                    except Exception:
                        myStreet = ''
                    try:
                        myCountry = myAddress['country'].encode('utf-8', 'ignore')
                    except Exception:
                        myCountry = ''
                    myItem = '%s:\t%s, %s %s' % (myID, myCity, myStreet, myCountry)
                    InstList.append((myItem, myID))
                except Exception:
                    pass
        except Exception as e:
            from Screens.MessageBox import MessageBox
            self.session.openWithCallback(self.doNothing, MessageBox, _("Exception: \n%s") % str(e), MessageBox.TYPE_INFO, timeout=10)
            return []
        
        return InstList
        
    def AirlyinstallationIDret(self, retVal):
        if not retVal is None:
            os.system('rm -f /tmp/.MSNdata/airlyInfo_*.json') #po zmianie instalacji czyœcimy info o niej
            curIndex = self["config"].getCurrentIndex()
            currItemCfg = self["config"].list[curIndex][1]
            currItemCfg.value = retVal[1]
        
    def keyOKret(self, retVal):
        if not retVal is None:
            curIndex = self["config"].getCurrentIndex()
            try:
                currItem = self["config"].list[curIndex]
                if len(currItem) > 1:
                    currItemCfg = currItem[1]
                    currItemCfg.value = retVal
            except Exception:
                pass
      
    def searchLocation(self):
        if self.current.city.value != "":
            language = config.osd.language.value.replace("_","-")
            if language == "en-EN": # hack
                language = "en-US"
            elif language == "no-NO": # hack
                language = "nn-NO"
            url = "http://weather.service.msn.com/find.aspx?src=windows&outputview=search&weasearchstr=%s&culture=%s" % (urllib_quote(self.current.city.value), language)
            getPage(url).addCallback(self.xmlCallback).addErrback(self.error)
        else:
            self.session.open(MessageBox, _("You need to enter a valid city name before you can search for the location code."), MessageBox.TYPE_ERROR)

    def keySave(self):
        if self.current.city.value != "" and self.current.weatherlocationcode.value != "":
            os.system('rm -f /tmp/.MSNdata/*')
            if self.newmode == 1:
                config.plugins.MSNweatherNP.entrycount.value = config.plugins.MSNweatherNP.entrycount.value + 1
                config.plugins.MSNweatherNP.entrycount.save()
            ConfigListScreen.keySave(self)
            config.plugins.MSNweatherNP.save()
            configfile.save()
            self.close()
        else:
            if self.current.city.value == "":
                self.session.open(MessageBox, _("Please enter a valid city name."), MessageBox.TYPE_ERROR)
            else:
                self.session.open(MessageBox, _("Please enter a valid location code for the city."), MessageBox.TYPE_ERROR)

    def keyCancel(self):
        if self.newmode == 1:
            config.plugins.MSNweatherNP.Entry.remove(self.current)
        ConfigListScreen.cancelConfirm(self, True)

    def keyDelete(self):
        if self.newmode == 1:
            self.keyCancel()
        else:        
            self.session.openWithCallback(self.deleteConfirm, MessageBox, _("Really delete this WeatherPlugin Entry?"))

    def deleteConfirm(self, result):
        if result:
            os.system('rm -f /tmp/.MSNdata/*')
            config.plugins.MSNweatherNP.entrycount.value = config.plugins.MSNweatherNP.entrycount.value - 1
            config.plugins.MSNweatherNP.entrycount.save()
            config.plugins.MSNweatherNP.Entry.remove(self.current)
            config.plugins.MSNweatherNP.Entry.save()
            config.plugins.MSNweatherNP.save()
            configfile.save()
            self.close()
        return
        
        
    def xmlCallback(self, xmlstring):
        if DBG: printDEBUG('MSNWeatherPluginEntryConfigScreen().xmlCallback >>>')
        if xmlstring:
            errormessage = ""
            root = cet_fromstring(xmlstring)
            for childs in root:
                if childs.tag == "weather" and childs.attrib.has_key("errormessage"):
                    errormessage = childs.attrib.get("errormessage").encode("utf-8", 'ignore')
                    break
            if len(errormessage) !=0:
                self.session.open(MessageBox, errormessage, MessageBox.TYPE_ERROR)                    
            else:
                self.session.openWithCallback(self.searchCallback, MSNWeatherSearch, xmlstring)
            
    def error(self, error = None):
        if error is not None:
            print error
        
    def searchCallback(self, result): # result=(weatherlocationcode, searchlocation, weatherSearchFullName, geolatitude, geolongitude)
        if result:
            self.current.weatherlocationcode.value = result[0]
            self.current.city.value = result[1]
            self.current.weatherSearchFullName.value = result[2]
            self.current.geolatitude.value = result[3].replace(',','.')
            self.current.geolongitude.value = result[4].replace(',','.')
            self.current.geolongitude.value = result[4].replace(',','.')
            self.current.geolongitude.value = result[4].replace(',','.')
            if self.current.weatherlocationcode.value.startswith('wc:PL'): 
                self.current.Fcity.value =  "Poland/Warsaw"
    
class MSNWeatherSearch(Screen):
    skin = """
        <screen name="MSNWeatherSearch" position="center,center" size="550,400">
            <widget name="entrylist" position="0,60" size="550,200" scrollbarMode="showOnDemand"/>
            <widget render="Label" source="key_red" position="0,10" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <widget render="Label" source="key_green" position="140,10" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="green" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <ePixmap position="0,10" zPosition="4" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
            <ePixmap position="140,10" zPosition="4" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
            <ePixmap position="280,10" zPosition="4" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
            <ePixmap position="420,10" zPosition="4" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
        </screen>""" 

    def __init__(self, session, xmlstring):
        Screen.__init__(self, session)
        self.title = _("MSN location search result")
        self["key_red"] = StaticText(_("Back"))
        self["key_green"] = StaticText(_("OK"))        
        self["entrylist"] = MSNWeatherSearchResultList([])
        self["actions"] = ActionMap(["WizardActions","MenuActions","ShortcutActions"],
            {
             "ok"    : self.keyOK,
             "green" : self.keyOK,
             "back"  : self.keyClose,
             "red"   : self.keyClose,
             }, -1)
        self.xmlstring = xmlstring
        self.onLayoutFinish.append(self.__onLayoutFinish)

    def __onLayoutFinish(self):
        self.updateList()
        
    def updateList(self):
        self["entrylist"].buildList(self.xmlstring)

    def keyClose(self):
        self.close(None)

    def keyOK(self):
        pass
        try:sel = self["entrylist"].l.getCurrentSelection()[0]
        except: sel = None
        self.close(sel)
        
class MSNWeatherSearchResultList(MenuList):
    def __init__(self, list, enableWrapAround = True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        GUIComponent.__init__(self)
        
        #default values:
        self.font0 = gFont("Regular", 20)
        self.font1 = gFont("Regular", 18)
        self.itemHeight = 44
        self.DimText0 = (5, 0, 500, 20, 1)
        self.DimText1 = (5, 22, 500, 20, 1)

    def applySkin(self, desktop, parent):
        def font(value):
            self.font0 = parseFont(value, ((1,1),(1,1)))
            self.font1 = parseFont(value, ((1,1),(1,1)))
        def font0(value):
            self.font0 = parseFont(value, ((1,1),(1,1)))
        def font1(value):
            self.font1 = parseFont(value, ((1,1),(1,1)))
        def itemHeight(value):
            self.itemHeight = int(value)
        def DimText0(value):
            self.DimText0 = ( int(value.split(',')[0]), int(value.split(',')[1]), int(value.split(',')[2]), int(value.split(',')[3]), int(value.split(',')[4]) )
        def DimText1(value):
            self.DimText1 = ( int(value.split(',')[0]), int(value.split(',')[1]), int(value.split(',')[2]), int(value.split(',')[3]), int(value.split(',')[4]) )
          
        for (attrib, value) in list(self.skinAttributes):
            try:
                locals().get(attrib)(value)
                self.skinAttributes.remove((attrib, value))
            except Exception as e:
                pass
                
        self.l.setFont(0,self.font0)
        self.l.setFont(1,self.font1)
        self.l.setItemHeight(self.itemHeight)
        return GUIComponent.applySkin(self, desktop, parent)

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    def buildList(self, xml):
        if DBG: printDEBUG('MSNWeatherSearchResultList:buildList(%s)' % xml,'>>>')
        root = cet_fromstring(xml)
        searchlocation = ""
        weatherlocationcode = ""
        weatherSearchFullName = ""
        geolatitude = ""
        geolongitude = ""
        list = []
        for childs in root:
            if childs.tag == "weather":
                weatherlocationcode = childs.attrib.get("weatherlocationcode").encode("utf-8", 'ignore')
                searchlocation = childs.attrib.get("weatherlocationname").encode("utf-8", 'ignore')
                weatherSearchFullName = childs.attrib.get("weatherfullname").encode("utf-8", 'ignore')
                geolatitude = childs.attrib.get("lat").encode("utf-8", 'ignore')
                geolongitude = childs.attrib.get("long").encode("utf-8", 'ignore')
                res = [
                    (weatherlocationcode, searchlocation, weatherSearchFullName, geolatitude, geolongitude),
                    (eListboxPythonMultiContent.TYPE_TEXT, self.DimText0[0], self.DimText0[1], self.DimText0[2], self.DimText0[3], self.DimText0[4], RT_HALIGN_LEFT|RT_VALIGN_CENTER, searchlocation),
                    (eListboxPythonMultiContent.TYPE_TEXT, self.DimText1[0], self.DimText1[1], self.DimText1[2], self.DimText1[3], self.DimText1[4], RT_HALIGN_LEFT|RT_VALIGN_CENTER, '%s , (lat=%s, long=%s)' % (weatherSearchFullName, geolatitude, geolongitude)),
                ]
                list.append(res)
        self.list = list
        self.l.setList(list)
        self.moveToIndex(0)

class MSNWeatherConfiguration(Screen, ConfigListScreen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.skinName = [ "MSNWeatherConfiguration", "Setup" ]
        self.setup_title = _("MSN weather configuration")
        self.onChangedEntry = []
        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("OK"))
        self["actions"] = ActionMap(["SetupActions"], { "cancel": self.keyCancel, "save": self.keySave, })
        ConfigList = []
        ConfigListScreen.__init__(self, ConfigList, session = session, on_change = self.changed)
        self.changed()
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(self.setup_title)
        self.runSetup()
        
    def changed(self):
        for x in self.onChangedEntry:
            x()

    def getCurrentEntry(self):
        return self["config"].getCurrent()[0]

    def getCurrentValue(self):
        return str(self["config"].getCurrent()[1].getText())

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.keyRightLeftActions()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.keyRightLeftActions()
            
    def keyRightLeftActions(self):
        if self["config"].getCurrent()[1] == config.plugins.MSNweatherNP.DebugEnabled:
            self.runSetup()
            
    def runSetup(self):
        ConfigList = []
        ConfigList.append(getConfigListEntry('\c00289496' + _("*** Basic settings ***"), config.plugins.MSNweatherNP.FakeEntry))
        ConfigList.append(getConfigListEntry(_("Data presented (if now defined in skin):"), config.plugins.MSNweatherNP.skinOrientation))
        ConfigList.append(getConfigListEntry(_("Airly API key %s:") % config.plugins.MSNweatherNP.airlyLimits.value, config.plugins.MSNweatherNP.airlyAPIKEY))
        ConfigList.append(getConfigListEntry(_("Sensors priority:"), config.plugins.MSNweatherNP.SensorsPriority))
        ConfigList.append(getConfigListEntry(_("Icons type:"), config.plugins.MSNweatherNP.IconsType))
        ConfigList.append(getConfigListEntry(_("Icons scaling engine:"), config.plugins.MSNweatherNP.ScalePicType))
        ConfigList.append(getConfigListEntry(_("Build histograms:"), config.plugins.MSNweatherNP.BuildHistograms))
        if config.plugins.MSNweatherNP.BuildHistograms.value:
            ConfigList.append(getConfigListEntry(_("Period:"), config.plugins.MSNweatherNP.HistoryPeriod))

        ConfigList.append(getConfigListEntry(""))
        ConfigList.append(getConfigListEntry('\c00289496' + _("*** Home air condition ***")))
        ConfigList.append(getConfigListEntry(_("1st AC system:"), config.plugins.MSNweatherNP.AC1))
        if config.plugins.MSNweatherNP.AC1.value != 'off':
            ConfigList.append(getConfigListEntry('- ' + _("IP address:"), config.plugins.MSNweatherNP.AC1_IP))
            ConfigList.append(getConfigListEntry('- ' + _("Port:"), config.plugins.MSNweatherNP.AC1_PORT))
            ConfigList.append(getConfigListEntry('- ' + _("Description:"), config.plugins.MSNweatherNP.AC1inf))
        ConfigList.append(getConfigListEntry(_("2nd AC system:"), config.plugins.MSNweatherNP.AC2))
        if config.plugins.MSNweatherNP.AC2.value != 'off':
            ConfigList.append(getConfigListEntry('- ' + _("IP address:"), config.plugins.MSNweatherNP.AC2_IP))
            ConfigList.append(getConfigListEntry('- ' + _("Port:"), config.plugins.MSNweatherNP.AC2_PORT))
            ConfigList.append(getConfigListEntry('- ' + _("Description:"), config.plugins.MSNweatherNP.AC2inf))

        ConfigList.append(getConfigListEntry(""))
        ConfigList.append(getConfigListEntry('\c00289496' + _("*** Debuging options ***")))
        ConfigList.append(getConfigListEntry(_("Debug (require restart):"), config.plugins.MSNweatherNP.DebugEnabled))
        if config.plugins.MSNweatherNP.DebugEnabled.value:
            ConfigList.append(getConfigListEntry(_("Debug log file size:"), config.plugins.MSNweatherNP.DebugSize))
            ConfigList.append(getConfigListEntry("> MSNWeather(Source):", config.plugins.MSNweatherNP.DebugMSNWeatherSource))
            ConfigList.append(getConfigListEntry("> MSNWeather(Converter):", config.plugins.MSNweatherNP.DebugMSNWeatherConverter))
            ConfigList.append(getConfigListEntry("> MSNWeatherPixmap(Renderer):", config.plugins.MSNweatherNP.DebugMSNWeatherPixmapRenderer))
            ConfigList.append(getConfigListEntry("> WeatherMSN updater:", config.plugins.MSNweatherNP.DebugWeatherMSNupdater))
            ConfigList.append(getConfigListEntry("> getWeather basic:", config.plugins.MSNweatherNP.DebugGetWeatherBasic))
            ConfigList.append(getConfigListEntry("> getWeather raw data:", config.plugins.MSNweatherNP.DebugGetWeatherFULL))
            ConfigList.append(getConfigListEntry("> MSNweatherHistograms:", config.plugins.MSNweatherNP.DebugMSNweatherHistograms))
            ConfigList.append(getConfigListEntry("> MSNweatherMaps:", config.plugins.MSNweatherNP.DebugMSNweatherHistograms))
            #ConfigList.append(getConfigListEntry("> :", config.plugins.MSNweatherNP.))
        try:
            self["config"].list = ConfigList
            self["config"].setList(ConfigList)
        except Exception:
            pass

    def keySave(self):
        for x in self["config"].list:
            if len(x) >= 2:
                x[1].save()
        configfile.save()
        self.close()

    def keyCancel(self):
        for x in self["config"].list:
            if len(x) >= 2:
                x[1].cancel()
        self.close()  
