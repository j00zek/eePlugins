# -*- coding: utf-8 -*-
from __future__ import absolute_import #zmiana strategii ladowania modulow w py2 z relative na absolute jak w py3
import base64, json, os, re, requests, sys, warnings

warnings.filterwarnings('ignore', message='Unverified HTTPS request')
PyMajorVersion = sys.version_info.major

if PyMajorVersion == 3:
    from urllib.parse import quote as urllib_quote, unquote as urllib_unquote
else:
    from urllib import quote as urllib_quote,  unquote as urllib_unquote

from . import _ , readCFG
from Plugins.Extensions.MSNweather.MSNcomponents.mappings import clr
from Plugins.Extensions.MSNweather.version import Version

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

DBG = True
if DBG:
    from Plugins.Extensions.MSNweather.debug import printDEBUG

def findInContent(ContentString, reFindString):
    retTxt = ''
    FC = re.findall(reFindString, ContentString, re.S)
    if FC:
        for i in FC:
            retTxt += i

    return retTxt

def getList(retList, ContentString, reFindString):
    FC = re.findall(reFindString, ContentString, re.S)
    if FC:
        for i in FC:
            retList.append(i)
    return retList

def ensure_str(text):
    if type(text) is str:
        return text
    if PyMajorVersion == 2:
        if isinstance(text, unicode):
            return text.encode('utf-8', 'ignore')
    else: #PY3
        if isinstance(text, bytes):
            return text.decode('utf-8', 'ignore')
    return text
        
def initWeatherPluginEntryConfig(i=0):
    s = ConfigSubsection()
    
    s.city = ConfigText(default = readCFG('city.%s' % i , 'Warszawa') , visible_width=100, fixed_size=False)

    s.degreetype = ConfigSelection(choices=[('C', _('metric system')), ('F', _('imperial system'))], default='C')
    
    s.weatherlocationcode = ConfigText(default = readCFG('weatherlocationcode.%s' % i , ''), visible_width=100, fixed_size=False)
    
    s.geolatitude = ConfigText(default = readCFG('geolatitude.%s' % i , 'auto'), visible_width=100, fixed_size=False)
    s.geolongitude = ConfigText(default = readCFG('geolongitude.%s' % i , 'auto'), visible_width=100, fixed_size=False)
    
    s.weatherSearchFullName = ConfigText(default= readCFG('weatherSearchFullName.%s' % i , ''), visible_width=100, fixed_size=False)
    
    s.thingSpeakChannelID = ConfigText(default= readCFG('thingSpeakChannelID.%s' % i , ''), visible_width=100, fixed_size=False)
    s.looko2ID = ConfigText(default= readCFG('looko2ID.%s' % i , ''), visible_width=100, fixed_size=False)
    
    s.airlyID = ConfigText(default= readCFG('airlyID.%s' % i , ''), visible_width=100, fixed_size=False)
    
    s.Fcity = ConfigText(default= readCFG('Fcity.%s' % i , ''), visible_width=100, fixed_size=False)
    s.Fmeteo = ConfigText(default= readCFG('Fmeteo.%s' % i , ''), visible_width=100, fixed_size=False)
    s.FmeteoRainPrecip = ConfigSelection(choices=[('maxRainPrecip', _('maximum')), ('avgRainPrecip', _('average'))], default='maxRainPrecip')
    
    s.giosID = ConfigText(default= readCFG('giosID.%s' % i , ''), visible_width=100, fixed_size=False)
    s.bleboxID = ConfigText(default= readCFG('bleboxID.%s' % i , ''), visible_width=100, fixed_size=False)
    s.openSenseID = ConfigText(default= readCFG('openSenseID.%s' % i , ''), visible_width=100, fixed_size=False)
    s.smogTokID = ConfigText(default= readCFG('smogTokID.%s' % i , 'Geo'), visible_width=100, fixed_size=False)

    s.entryType = ConfigSelection(choices=[('main', _('local')), ('client', _('remote'))], default='main')
    s.mainEntryADDR = ConfigIP(default=[0, 0, 0, 0])
    s.mainEntryUSER = ConfigText(default='root', visible_width=100, fixed_size=False)
    s.mainEntryPASS = ConfigText(default='', visible_width=100, fixed_size=False)
    s.mainEntryID = ConfigSelection(choices=[('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '6')], default='0')
    config.plugins.MSNweatherNP.Entry.append(s)
    return s


def initConfig():
    count = config.plugins.MSNweatherNP.entrycount.value
    if count != 0:
        i = 0
        while i < count:
            initWeatherPluginEntryConfig(i)
            i += 1

def decodeUTF8(string2decode):
    if DBG: printDEBUG('decodeUTF8() >>>')
    if PyMajorVersion == 3:
        return string2decode.decode('utf8')
    else:
        return string2decode

class MSNWeatherEntriesListConfigScreen(Screen):
    def __init__(self, session):
        self.skin = """
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
        Screen.__init__(self, session)
        self.title = _('MSN weather: List of Entries')
        self['city'] = StaticText(_('City'))
        self['degreetype'] = StaticText(_('System'))
        self['key_red'] = StaticText(_('Back'))
        self['key_green'] = StaticText(_('Add'))
        self['key_yellow'] = StaticText(_('Edit'))
        self['key_blue'] = StaticText(_('Delete'))
        self['entrylist'] = WeatherEntryList([])
        self['actions'] = ActionMap(['WizardActions', 'MenuActions', 'ShortcutActions'], {'ok': self.keyOK, 
           'back': self.keyClose, 
           'red': self.keyClose, 
           'green': self.keyGreen, 
           'yellow': self.keyYellow, 
           'blue': self.keyDelete, 
           'menu': self.keyMenu}, -1)
        self.onLayoutFinish.append(self.__onLayoutFinish)

    def __onLayoutFinish(self):
        self.updateList()

    def updateList(self):
        self['entrylist'].buildList()

    def keyClose(self):
        self.close(-1, None)
        return

    def keyMenu(self):
        self.session.openWithCallback(self.updateList, MSNWeatherConfiguration)

    def keyGreen(self):
        try:
            selIDXs = self['entrylist'].getListSize()
        except Exception as e:
            selIDXs = None

        self.session.openWithCallback(self.updateList, MSNWeatherEntryConfigScreen, None, None, selIDXs)
        return

    def keyOK(self):
        try:
            sel = self['entrylist'].l.getCurrentSelection()[0]
            idx = self['entrylist'].getCurrentIndex()
        except:
            sel = None
            idx = -1

        self.close(idx, sel)
        return

    def keyYellow(self):
        try:
            sel = self['entrylist'].l.getCurrentSelection()[0]
            selIDX = self['entrylist'].getCurrentIndex()
            selIDXs = self['entrylist'].getListSize()
        except:
            sel = None

        if sel is None:
            return
        else:
            self.session.openWithCallback(self.updateList, MSNWeatherEntryConfigScreen, sel, selIDX, selIDXs)
            return

    def keyDelete(self):
        try:
            sel = self['entrylist'].l.getCurrentSelection()[0]
        except:
            sel = None

        if sel is None:
            return
        else:
            self.session.openWithCallback(self.deleteConfirm, MessageBox, _('Really delete this WeatherPlugin Entry?'))
            return

    def deleteConfirm(self, result):
        if result:
            os.system('rm -f /tmp/.MSNdata/*')
            sel = self['entrylist'].l.getCurrentSelection()[0]
            config.plugins.MSNweatherNP.entrycount.value -= 1
            config.plugins.MSNweatherNP.entrycount.save()
            config.plugins.MSNweatherNP.Entry.remove(sel)
            config.plugins.MSNweatherNP.Entry.save()
            config.plugins.MSNweatherNP.save()
            configfile.save()
            self.updateList()


class WeatherEntryList(MenuList):

    def __init__(self, list, enableWrapAround=True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        GUIComponent.__init__(self)
        self.font0 = gFont('Regular', 20)
        self.font1 = gFont('Regular', 18)
        self.itemHeight = 20
        self.DimText0 = (5, 0, 400, 20, 1)
        self.DimText1 = (410, 0, 80, 20, 1)

    def applySkin(self, desktop, parent):

        def font(value):
            self.font0 = parseFont(value, ((1, 1), (1, 1)))
            self.font1 = parseFont(value, ((1, 1), (1, 1)))

        def font0(value):
            self.font0 = parseFont(value, ((1, 1), (1, 1)))

        def font1(value):
            self.font1 = parseFont(value, ((1, 1), (1, 1)))

        def itemHeight(value):
            self.itemHeight = int(value)

        def DimText0(value):
            self.DimText0 = (int(value.split(',')[0]), int(value.split(',')[1]), int(value.split(',')[2]), int(value.split(',')[3]), int(value.split(',')[4]))

        def DimText1(value):
            self.DimText1 = (int(value.split(',')[0]), int(value.split(',')[1]), int(value.split(',')[2]), int(value.split(',')[3]), int(value.split(',')[4]))

        for attrib, value in list(self.skinAttributes):
            try:
                locals().get(attrib)(value)
                self.skinAttributes.remove((attrib, value))
            except Exception as e:
                pass

        self.l.setFont(0, self.font0)
        self.l.setFont(1, self.font1)
        self.l.setItemHeight(self.itemHeight)
        return GUIComponent.applySkin(self, desktop, parent)

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    def buildList(self):
        list = []
        for c in config.plugins.MSNweatherNP.Entry:
            res = [
             c,
             (
              eListboxPythonMultiContent.TYPE_TEXT, self.DimText0[0], self.DimText0[1], self.DimText0[2], self.DimText0[3], self.DimText0[4], RT_HALIGN_LEFT | RT_VALIGN_CENTER, str(c.city.value)),
             (
              eListboxPythonMultiContent.TYPE_TEXT, self.DimText1[0], self.DimText1[1], self.DimText1[2], self.DimText1[3], self.DimText1[4], RT_HALIGN_LEFT | RT_VALIGN_CENTER, str(c.degreetype.value))]
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
        self.title = _('WeatherPlugin: Edit Entry')
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'green': self.keySave, 
           'red': self.keyCancel, 
           'blue': self.keyDelete, 
           'yellow': self.searchLocation, 
           'cancel': self.keyCancel, 
           'ok': self.keyOK}, -2)
        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('Save'))
        self['key_blue'] = StaticText(_('Delete'))
        self['key_yellow'] = StaticText(_('Search Code'))
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
        ConfigListScreen.__init__(self, [], session, on_change=self.changedEntry)
        self.buildList()
        return

    def buildList(self):
        if self.current.entryType.value == 'client':
            cfglist = [
             getConfigListEntry(_('Entry type'), self.current.entryType),
             getConfigListEntry(_('Location name on the list'), self.current.weatherSearchFullName),
             getConfigListEntry(_('Main plugin IP address'), self.current.mainEntryADDR),
             getConfigListEntry(_('Main plugin username'), self.current.mainEntryUSER),
             getConfigListEntry(_('Main plugin password'), self.current.mainEntryPASS)]
        else:
            cfglist = [getConfigListEntry(_('Entry type'), self.current.entryType),
             getConfigListEntry('\\c00289496' + _('--- REQUIRED ---'), config.plugins.MSNweatherNP.FakeEntry),
             getConfigListEntry(_('City'), self.current.city),
             getConfigListEntry(_('Location code'), self.current.weatherlocationcode),
             getConfigListEntry(_('Location Full name'), self.current.weatherSearchFullName),
             getConfigListEntry(_('System'), self.current.degreetype),
             getConfigListEntry(_('Geo Latitude'), self.current.geolatitude),
             getConfigListEntry(_('Geo Longitude'), self.current.geolongitude),
             getConfigListEntry(  'foreca.com/...', self.current.Fmeteo),
             getConfigListEntry(_('foreca daily rain precip'), self.current.FmeteoRainPrecip),
             getConfigListEntry('\\c00289496' + '--- CZUJNIKI JAKOŚCI POWETRZA (najbliższy najlepszy)---', config.plugins.MSNweatherNP.FakeEntry),
             getConfigListEntry(_('thingSpeak meteo channel ID'), self.current.thingSpeakChannelID),
             getConfigListEntry(_('Airly installation ID (OK)'), self.current.airlyID),
             getConfigListEntry(_('looko2 sensor ID (OK)'), self.current.looko2ID),
             getConfigListEntry(_('GiOS sensor ID (OK)'), self.current.giosID),
             getConfigListEntry(_('blebox sensor ID (OK)'), self.current.bleboxID),
             getConfigListEntry(_('openSense sensor ID (OK)'), self.current.openSenseID),
             getConfigListEntry(_('smogOK sensor ID (OK)'), self.current.smogTokID),
             getConfigListEntry('\\c00289496' + _('--- OPTIONAL, NOT REQUIRED ---'), config.plugins.MSNweatherNP.FakeEntry),
             getConfigListEntry(_('Meteogram for www.foreca.net/<this part>'), self.current.Fcity)]
        self['config'].list = cfglist

    def changedEntry(self):
        curIndex = self['config'].getCurrentIndex()
        currItemCfg = self['config'].list[curIndex][1]
        if currItemCfg == self.current.entryType:
            self.buildList()

    def keyOK(self):
        curIndex = self['config'].getCurrentIndex()
        currItemCfg = self['config'].list[curIndex][1]
        currItemNam = self['config'].list[curIndex][0]
        if currItemCfg == self.current.airlyID:
            try:
                float(self.current.geolatitude.value)
                float(self.current.geolongitude.value)
            except Exception:
                self.session.openWithCallback(self.doNothing, MessageBox, _('Set proper latitude and longitude!!!'), MessageBox.TYPE_INFO, timeout=10)
                return

            if config.plugins.MSNweatherNP.airlyAPIKEY.value == '':
                infoTXT = _('Set airly API key using one of the following methods:\n')
                infoTXT += _('global plugin settings\n')
                infoTXT += _('/etc/enigma2/MSN_defaults/airlyAPIKEY file\n')
                self.session.openWithCallback(self.doNothing, MessageBox, infoTXT, MessageBox.TYPE_INFO, timeout=10)
                return
                
            InstList = self.Airlyinstallations(currItemCfg.value)
            if len(InstList) > 0:
                from Screens.ChoiceBox import ChoiceBox
                if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/Airly'):
                    ChoiceBoxTitle = _('Airly plugin detected - API key CAN be BLOCKED!!!')
                else:
                    ChoiceBoxTitle = _('10 closest Airly installations')
                self.session.openWithCallback(self.AirlyinstallationIDret, ChoiceBox, title=ChoiceBoxTitle, list=InstList)
                return
            currItemNam = _('No airly installations within 20km distance, provide ID manually')
            self.session.openWithCallback(self.keyOKret, VirtualKeyBoard, title=currItemNam, text=currItemCfg.value)
        elif currItemCfg == self.current.giosID:

            def GIOSinstallations(currentID):
                InstList = []
                try:
                    newHEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:88.0) Gecko/20100101 Firefox/88.0', 
                                  'Accept-Charset': 'utf-8', 
                                  'Accept-Language': 'en',
                                  'Accept': 'application/json',
                                  'Content-Type': 'text/html; charset=utf-8'
                                }
                    webURL = 'http://api.gios.gov.pl/pjp-api/rest/station/findAll'
                    webContent = self.downloadWebPage(webURL, newHEADERS)
                    import json
                    json_data = json.dumps(json.loads(webContent), indent=4, ensure_ascii=False)
                    open('/tmp/.MSNdata/gios_installations.json', 'w').write('%s\n' % json_data)
                    open('/tmp/.MSNdata/gios_installations.Exception', 'w').write('')
                    installations = json.loads(webContent.decode('utf-8'))
                    for inst in installations:
                        try:
                            myID = str(inst['id'])
                            myAddress = inst['stationName'].encode('utf-8', 'ignore')
                            myItem = '%s:\t%s' % (myID, myAddress)
                            InstList.append((myItem, myID, myAddress))
                        except Exception as e:
                            open('/tmp/.MSNdata/gios_installations.Exception', 'a').write('%s\n' % str(e))

                except Exception as e:
                    self.session.openWithCallback(self.doNothing, MessageBox, _('Exception: \n%s') % str(e), MessageBox.TYPE_INFO, timeout=10)
                    return []

                InstList.sort(key=lambda t: tuple(str(t[2]).lower()))
                if currentID != '':
                    InstList.insert(0, ('%s:\t%s' % (currentID, _('Current selection')), currentID, ''))
                return InstList

            def GIOSinstallationsIDret(retVal):
                if retVal is not None:
                    curIndex = self['config'].getCurrentIndex()
                    currItemCfg = self['config'].list[curIndex][1]
                    currItemCfg.value = retVal[1]
                return

            InstList = GIOSinstallations(currItemCfg.value)
            if len(InstList) > 0:
                from Screens.ChoiceBox import ChoiceBox
                ChoiceBoxTitle = _('GiOS %s installations' % len(InstList))
                self.session.openWithCallback(GIOSinstallationsIDret, ChoiceBox, title=ChoiceBoxTitle, list=InstList)
                return
            currItemNam = _('No airly installations within 20km distance, provide ID manually')
            self.session.openWithCallback(self.keyOKret, VirtualKeyBoard, title=currItemNam, text=currItemCfg.value)
        elif currItemCfg == self.current.looko2ID:
            title = 'https://looko2.com/tracker.php?lan=&search=%s<TA CZĘŚĆ>' % clr['B']
            self.session.openWithCallback(self.keyOKret, VirtualKeyBoard, title=title, text=currItemCfg.value)
        elif currItemCfg == self.current.bleboxID:
            title = 'https://mapa-jakosci-powietrza.blebox.eu/pl/%s<TA CZĘŚĆ>' % clr['B']
            self.session.openWithCallback(self.keyOKret, VirtualKeyBoard, title=title, text=currItemCfg.value)
        elif currItemCfg == self.current.openSenseID:
            title = 'https://opensensemap.org/explore/%s<TA CZĘŚĆ>' % clr['B']
            self.session.openWithCallback(self.keyOKret, VirtualKeyBoard, title=title, text=currItemCfg.value)
        else:
            self.session.openWithCallback(self.keyOKret, VirtualKeyBoard, title=currItemNam, text=currItemCfg.value)
            return

    def doNothing(self, ret=None):
        pass

    def Airlyinstallations(self, currentAirlyID):
        InstList = []
        if currentAirlyID != '':
            InstList.append(('%s:\t%s' % (currentAirlyID, _('Current selection')), currentAirlyID))
        try:
            newHEADERS = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:88.0) Gecko/20100101 Firefox/88.0', 
                        'Accept-Charset': 'utf-8', 
                        'Accept-Language': 'en',
                        'Accept': 'application/json',
                        'Content-Type': 'text/html; charset=utf-8',
                        'apikey': config.plugins.MSNweatherNP.airlyAPIKEY.value
                      }
            webURL = 'https://airapi.airly.eu/v2/installations/nearest?lat=%s&lng=%s&maxDistanceKM=20&maxResults=10' % (self.current.geolatitude.value, self.current.geolongitude.value)
            webContent = self.downloadWebPage(webURL, newHEADERS)
            import json
            json_data = json.dumps(json.loads(webContent), indent=4, ensure_ascii=False)
            open('/tmp/.MSNdata/airly_installations.json', 'w').write('%s\n' % json_data)
            installations = json.loads(webContent)
            for inst in installations:
                try:
                    myID = str(inst['id'])
                    myAddress = inst['address']
                    try: myCity = ensure_str(myAddress['city'])
                    except Exception: myCity = ''

                    try: myStreet = ensure_str(myAddress['street'])
                    except Exception: myStreet = ''

                    try: myCountry = ensure_str(myAddress['country'])
                    except Exception: myCountry = ''

                    myItem = '%s:\t%s, %s %s' % (myID, myCity, myStreet, myCountry)
                    InstList.append((myItem, myID))
                except Exception:
                    pass

        except Exception as e:
            self.session.openWithCallback(self.doNothing, MessageBox, _('Exception: \n%s') % str(e), MessageBox.TYPE_INFO, timeout=10)
            return []

        return InstList

    def AirlyinstallationIDret(self, retVal):
        if retVal is not None:
            os.system('rm -f /tmp/.MSNdata/airlyInfo_*.json')
            curIndex = self['config'].getCurrentIndex()
            currItemCfg = self['config'].list[curIndex][1]
            currItemCfg.value = retVal[1]
        return

    def keyOKret(self, retVal):
        if retVal is not None:
            curIndex = self['config'].getCurrentIndex()
            try:
                currItem = self['config'].list[curIndex]
                if len(currItem) > 1:
                    currItemCfg = currItem[1]
                    currItemCfg.value = retVal
            except Exception:
                pass

        return

    def xmlCallback(self, xmlstring, webContent):
        #example xmlstring:
        #    <weatherdata xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        #        <weather weatherlocationcode="wc:PLXX0028" weatherlocationname="Warszawa, MA" weatherfullname="Warszawa, Polska" searchlocation="" searchdistance="" searchscore="" url="http://a.msn.com/54/pl-PL/ct52.235,21.008?ctsrc=windows" imagerelativeurl="http://blob.weather.microsoft.com/static/weather4/en/" degreetype="C" provider="Foreca" isregion="True" region="MA" alert="" searchresult="" lat="52,235" long="21,008" entityid="35813">
        #            <current temperature="20" skycode="34" skytext="Przeważnie słonecznie" />
        #        </weather>
        #    </weatherdata>
        if DBG: printDEBUG('MSNWeatherPluginEntryConfigScreen().xmlCallback >>>')
        if DBG: open("/tmp/.MSNdata/setupNPcitySearchCallback.xml", "w").write(xmlstring)
        if xmlstring:
            errormessage = ''
            try:
                root = cet_fromstring(xmlstring)
                for childs in root:
                    if childs.tag == 'weather' and 'errormessage' in childs.attrib:
                        if PyMajorVersion == 3:
                            errormessage = childs.attrib.get('errormessage')
                        else:
                            errormessage = childs.attrib.get('errormessage').encode('utf-8', 'ignore')
                        break
            except Exception as e:
                open("/tmp/.MSNdata/setupNPcitySearchCallback.EXCEPTION", "w").write('EXCEPTION PARSING XML RESPONSE: %s\n!!!!!!!!!!page content:\n%s' % (str(e),xmlstring))
                try:
                    xmlstring = ''
                    #FC = findInContent(webContent, 'div id="WeatherOverviewLocationName".*div class="labelWeather-E1_1"')
                    #weatherSearchFullName = getList([], FC, 'title="([^"]*)"')[0]
                    FC = findInContent(webContent, 'div id="WeatherOverviewLocationName".*}</script></div>')
                    if FC == '':
                        FC = findInContent(webContent, 'div id="WeatherOverviewLocationName".*</script></div>')
                    bdata = getList([], FC, 'loc=([^"&;]*)')[0]
                    data = json.loads(ensure_str(base64.b64decode(bdata)))
                    xmlstring += '<weatherdata xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                    xmlstring += '<weather weatherlocationcode="loc=%s"' % ensure_str(bdata)
                    xmlstring += ' weatherlocationname="%s, %s"' % (data['l'],data['c']) #weatherSearchFullName
                    xmlstring += ' weatherfullname="%s, %s"' % (data['l'],data['r']) #weatherSearchFullName
                    xmlstring += ' lat="%s"' % data['y']
                    xmlstring += ' long="%s"' % data['x']
                    xmlstring += '/>'
                    xmlstring += '</weatherdata>'
                except Exception as ex:
                    open("/tmp/.MSNdata/webContent.Exception", "w").write('EXCEPTION PARSING WEBCONTENT RESPONSE: %s\n!!!!!!!!!!page content:\n%s' % (str(ex),ensure_str(webContent)))
                    errormessage = _('City not found :(')

            if len(errormessage) != 0:
                self.session.open(MessageBox, errormessage, MessageBox.TYPE_ERROR)
            else:
                self.session.openWithCallback(self.searchCallback, MSNWeatherSearch, xmlstring)

    def downloadWebPage(self, webURL, newHEADERS = None):
        def decodeHTML(text):
            text = text.replace('&#243;', 'ó')
            text = text.replace('&#176;', '°').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
            text = text.replace('&#228;', 'ä').replace('&#196;', 'Ă').replace('&#246;', 'ö').replace('&#214;', 'Ö').replace('&#252;', 'ü').replace('&#220;', 'Ü').replace('&#223;', 'ß')
            return text
        
        webContent = ''
        try:
            if newHEADERS is None:
                HEADERS = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:88.0) Gecko/20100101 Firefox/88.0', 
                        'Accept-Charset': 'utf-8', 
                        'Content-Type': 'text/html; charset=utf-8'
                      }
            else:
                HEADERS = newHEADERS
            resp = requests.get(webURL, headers=HEADERS, timeout=5)
            webContent = ensure_str(resp.content)
            webHeader = resp.headers
            webContent = urllib_unquote(webContent)
            webContent = decodeHTML(webContent)
            if DBG: printDEBUG("webHeader: %s" % resp.headers )
        except Exception as e:
            if DBG: printDEBUG("EXCEPTION '%s' in downloadWebPage() for %s" % (str(e), webURL) )
            webContent = ''
        return webContent

    def searchLocation(self):
        if self.current.city.value != '':
            language = config.osd.language.value.replace('_', '-')
            if language == 'en-EN':
                language = 'en-US'
            elif language == 'no-NO':
                language = 'nn-NO'
            url = 'http://weather.service.msn.com/find.aspx?src=windows&outputview=search&weasearchstr=%s&culture=%s' % (urllib_quote(self.current.city.value), language)
            xmlContent = self.downloadWebPage(url)
            url = 'https://www.msn.com/%s/pogoda/prognoza/in-%s' % (language.lower(),urllib_quote(self.current.city.value))
            webContent = self.downloadWebPage(url)
            self.xmlCallback(xmlContent, webContent)
        else:
            self.session.open(MessageBox, _('You need to enter a valid city name before you can search for the location code.'), MessageBox.TYPE_ERROR)

    def keySave(self):
        if self.current.entryType.value == 'client':
            self.current.city.value = self.current.weatherSearchFullName.value
            self.current.weatherlocationcode.value = self.current.weatherSearchFullName.value
        if self.current.city.value != '' and self.current.weatherlocationcode.value != '':
            os.system('rm -f /tmp/.MSNdata/*')
            if self.newmode == 1:
                config.plugins.MSNweatherNP.entrycount.value = config.plugins.MSNweatherNP.entrycount.value + 1
                config.plugins.MSNweatherNP.entrycount.save()
            ConfigListScreen.keySave(self)
            config.plugins.MSNweatherNP.save()
            configfile.save()
            self.close()
        elif self.current.city.value == '':
            self.session.open(MessageBox, _('Please enter a valid city name.'), MessageBox.TYPE_ERROR)
        else:
            self.session.open(MessageBox, _('Please enter a valid location code for the city.'), MessageBox.TYPE_ERROR)

    def keyCancel(self):
        if self.newmode == 1:
            config.plugins.MSNweatherNP.Entry.remove(self.current)
        ConfigListScreen.cancelConfirm(self, True)

    def keyDelete(self):
        if self.newmode == 1:
            self.keyCancel()
        else:
            self.session.openWithCallback(self.deleteConfirm, MessageBox, _('Really delete this WeatherPlugin Entry?'))

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

    def searchCallback(self, result):
        print(result)
        if result:
            self.current.weatherlocationcode.value = result[0]
            self.current.city.value = result[1]
            self.current.weatherSearchFullName.value = result[2]
            self.current.geolatitude.value = result[3].replace(',', '.')
            self.current.geolongitude.value = result[4].replace(',', '.')
            if self.current.weatherlocationcode.value.startswith('wc:PL'):
                self.current.Fcity.value = 'Poland/Warsaw'


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
        self.title = _('MSN location search result')
        self['key_red'] = StaticText(_('Back'))
        self['key_green'] = StaticText(_('OK'))
        self['entrylist'] = MSNWeatherSearchResultList([])
        self['actions'] = ActionMap(['WizardActions', 'MenuActions', 'ShortcutActions'], {'ok': self.keyOK, 
           'green': self.keyOK, 
           'back': self.keyClose, 
           'red': self.keyClose}, -1)
        self.xmlstring = xmlstring
        self.onLayoutFinish.append(self.__onLayoutFinish)

    def __onLayoutFinish(self):
        self.updateList()

    def updateList(self):
        self['entrylist'].buildList(self.xmlstring)

    def keyClose(self):
        self.close(None)
        return

    def keyOK(self):
        try:
            sel = self['entrylist'].l.getCurrentSelection()[0]
        except:
            sel = None

        self.close(sel)
        return


class MSNWeatherSearchResultList(MenuList):

    def __init__(self, list, enableWrapAround=True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        GUIComponent.__init__(self)
        self.font0 = gFont('Regular', 20)
        self.font1 = gFont('Regular', 18)
        self.itemHeight = 44
        self.DimText0 = (5, 0, 500, 20, 1)
        self.DimText1 = (5, 22, 500, 20, 1)

    def applySkin(self, desktop, parent):

        def font(value):
            self.font0 = parseFont(value, ((1, 1), (1, 1)))
            self.font1 = parseFont(value, ((1, 1), (1, 1)))

        def font0(value):
            self.font0 = parseFont(value, ((1, 1), (1, 1)))

        def font1(value):
            self.font1 = parseFont(value, ((1, 1), (1, 1)))

        def itemHeight(value):
            self.itemHeight = int(value)

        def DimText0(value):
            self.DimText0 = (int(value.split(',')[0]), int(value.split(',')[1]), int(value.split(',')[2]), int(value.split(',')[3]), int(value.split(',')[4]))

        def DimText1(value):
            self.DimText1 = (int(value.split(',')[0]), int(value.split(',')[1]), int(value.split(',')[2]), int(value.split(',')[3]), int(value.split(',')[4]))

        for attrib, value in list(self.skinAttributes):
            try:
                locals().get(attrib)(value)
                self.skinAttributes.remove((attrib, value))
            except Exception as e:
                pass

        self.l.setFont(0, self.font0)
        self.l.setFont(1, self.font1)
        self.l.setItemHeight(self.itemHeight)
        return GUIComponent.applySkin(self, desktop, parent)

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    def buildList(self, xml):
        if DBG: printDEBUG('MSNWeatherSearchResultList:buildList(%s)' % xml, '>>>')
        root = cet_fromstring(xml)
        searchlocation = ''
        weatherlocationcode = ''
        weatherSearchFullName = ''
        geolatitude = ''
        geolongitude = ''
        list = []
        for childs in root:
            if childs.tag == 'weather':
                weatherlocationcode = decodeUTF8(childs.attrib.get('weatherlocationcode').encode('utf-8', 'ignore'))
                searchlocation = decodeUTF8(childs.attrib.get('weatherlocationname').encode('utf-8', 'ignore'))
                weatherSearchFullName = decodeUTF8(childs.attrib.get('weatherfullname').encode('utf-8', 'ignore'))
                geolatitude = decodeUTF8(childs.attrib.get('lat').encode('utf-8', 'ignore'))
                geolongitude = decodeUTF8(childs.attrib.get('long').encode('utf-8', 'ignore'))
                res = [
                 (
                  weatherlocationcode, searchlocation, weatherSearchFullName, geolatitude, geolongitude),
                 (
                  eListboxPythonMultiContent.TYPE_TEXT, self.DimText0[0], self.DimText0[1], self.DimText0[2], self.DimText0[3], self.DimText0[4], RT_HALIGN_LEFT | RT_VALIGN_CENTER, searchlocation),
                 (
                  eListboxPythonMultiContent.TYPE_TEXT, self.DimText1[0], self.DimText1[1], self.DimText1[2], self.DimText1[3], self.DimText1[4], RT_HALIGN_LEFT | RT_VALIGN_CENTER, '%s , (lat=%s, long=%s)' % (weatherSearchFullName, geolatitude, geolongitude))]
                list.append(res)

        self.list = list
        self.l.setList(list)
        self.moveToIndex(0)


class MSNWeatherConfiguration(Screen, ConfigListScreen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skinName = ['MSNWeatherConfiguration', 'Setup']
        self.setup_title = _('MSN weather configuration')
        self.onChangedEntry = []
        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('OK'))
        self['actions'] = ActionMap(['SetupActions'], {'cancel': self.keyCancel, 'save': self.keySave})
        ConfigList = []
        ConfigListScreen.__init__(self, ConfigList, session=session, on_change=self.changed)
        self.changed()
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(self.setup_title)
        self.runSetup()

    def changed(self):
        for x in self.onChangedEntry:
            x()

    def getCurrentEntry(self):
        return self['config'].getCurrent()[0]

    def getCurrentValue(self):
        return str(self['config'].getCurrent()[1].getText())

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.keyRightLeftActions()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.keyRightLeftActions()

    def keyRightLeftActions(self):
        if self['config'].getCurrent()[1] == config.plugins.MSNweatherNP.DebugEnabled:
            self.runSetup()

    def runSetup(self):
        ConfigList = []
        ConfigList.append(getConfigListEntry('\\c00289496' + _('*** Basic settings ***'), config.plugins.MSNweatherNP.FakeEntry))
        ConfigList.append(getConfigListEntry(_('Default skin background:'), config.plugins.MSNweatherNP.skinOrientation))
        ConfigList.append(getConfigListEntry(_('MSNWeather API key:'), config.plugins.MSNweatherNP.msnAPIKEY))
        ConfigList.append(getConfigListEntry(_('Airly API key %s:') % config.plugins.MSNweatherNP.airlyLimits.value, config.plugins.MSNweatherNP.airlyAPIKEY))
        ConfigList.append(getConfigListEntry(_('Sensors priority:'), config.plugins.MSNweatherNP.SensorsPriority))
        ConfigList.append(getConfigListEntry(_('Daily icons type:'), config.plugins.MSNweatherNP.IconsType))
        ConfigList.append(getConfigListEntry(_('Hourly icons type:'), config.plugins.MSNweatherNP.hIconsType))
        ConfigList.append(getConfigListEntry(_('Icons scaling engine:'), config.plugins.MSNweatherNP.ScalePicType))
        ConfigList.append(getConfigListEntry(_('Build histograms:'), config.plugins.MSNweatherNP.BuildHistograms))
        if config.plugins.MSNweatherNP.BuildHistograms.value:
            ConfigList.append(getConfigListEntry(_('Period:'), config.plugins.MSNweatherNP.HistoryPeriod))
        ConfigList.append(getConfigListEntry(''))
        ConfigList.append(getConfigListEntry('\\c00289496' + _('*** Home solar system ***')))
        ConfigList.append(getConfigListEntry(_('Producer:'), config.plugins.MSNweatherNP.solarType))
        if config.plugins.MSNweatherNP.solarType.value != 'off':
            ConfigList.append(getConfigListEntry('- ' + _('ID:'), config.plugins.MSNweatherNP.solarID))
            ConfigList.append(getConfigListEntry('- ' + _('API key:'), config.plugins.MSNweatherNP.solarAPIKEY))
        ConfigList.append(getConfigListEntry(''))
        ConfigList.append(getConfigListEntry('\\c00289496' + _('*** Home air condition ***')))
        ConfigList.append(getConfigListEntry(_('1st AC system:'), config.plugins.MSNweatherNP.AC1))
        if config.plugins.MSNweatherNP.AC1.value != 'off':
            ConfigList.append(getConfigListEntry('- ' + _('IP address:'), config.plugins.MSNweatherNP.AC1_IP))
            ConfigList.append(getConfigListEntry('- ' + _('Port:'), config.plugins.MSNweatherNP.AC1_PORT))
            ConfigList.append(getConfigListEntry('- ' + _('Description:'), config.plugins.MSNweatherNP.AC1inf))
        ConfigList.append(getConfigListEntry(_('2nd AC system:'), config.plugins.MSNweatherNP.AC2))
        if config.plugins.MSNweatherNP.AC2.value != 'off':
            ConfigList.append(getConfigListEntry('- ' + _('IP address:'), config.plugins.MSNweatherNP.AC2_IP))
            ConfigList.append(getConfigListEntry('- ' + _('Port:'), config.plugins.MSNweatherNP.AC2_PORT))
            ConfigList.append(getConfigListEntry('- ' + _('Description:'), config.plugins.MSNweatherNP.AC2inf))
        ConfigList.append(getConfigListEntry(''))
        ConfigList.append(getConfigListEntry('\\c00289496' + _('*** Debuging options ***')))
        if 'dev' in Version:
            ConfigList.append(getConfigListEntry(_('Debug to /tmp/.MSNdata (require restart):'), config.plugins.MSNweatherNP.DebugEnabled))
        else:
            ConfigList.append(getConfigListEntry(_('Debug to /tmp/MSNdata_logs.tar.gz (requires restart):'), config.plugins.MSNweatherNP.DebugEnabled))
        if config.plugins.MSNweatherNP.DebugEnabled.value:
            ConfigList.append(getConfigListEntry(_('Debug log file size:'), config.plugins.MSNweatherNP.DebugSize))
        try:
            self['config'].list = ConfigList
            self['config'].setList(ConfigList)
        except Exception:
            pass

    def doNothing(self, ret=None):
        pass

    def keySave(self):
        for x in self['config'].list:
            if len(x) >= 2:
                x[1].save()

        configfile.save()
        self.close()

    def keyCancel(self):
        for x in self['config'].list:
            if len(x) >= 2:
                x[1].cancel()

        self.close()