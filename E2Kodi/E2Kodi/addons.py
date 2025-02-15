from Components.ActionMap import ActionMap
from Components.config import *
from enigma import eConsoleAppContainer, eDVBDB, eTimer, getDesktop
#from importlib import reload #NIE dziala bo zaladowany do eventow
from Plugins.Extensions.E2Kodi.plugin import safeSubprocessCMD
from Plugins.Extensions.E2Kodi.version import Version
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

import json, os, signal, sys, subprocess, time, traceback

import Screens.Standby
####MENU
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.MenuList import MenuList
from Tools.LoadPixmap import LoadPixmap
### E2KodiConfiguration
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Screens.ChoiceBox import ChoiceBox
from Screens.Setup import SetupSummary

from emukodi.xbmcE2 import *
from emukodi.e2Console import emukodiConsole
###

DBG = True

################################################################################################
config.plugins.E2Kodi = ConfigSubsection()
config.plugins.E2Kodi.configItem = NoSave(ConfigNothing())
config.plugins.E2Kodi.MenuInitIndex = NoSave(ConfigInteger(default = 0))
config.plugins.E2Kodi.ConfigurationInitIndex = NoSave(ConfigInteger(default = 0))
config.plugins.E2Kodi.PlayerInitIndex = NoSave(ConfigInteger(default = 0))
config.plugins.E2Kodi.openSelected = NoSave(ConfigText(default = '', fixed_size = False))
config.plugins.E2Kodi.username  = NoSave(ConfigText(default = '', fixed_size = False))
config.plugins.E2Kodi.password  = NoSave(ConfigPassword(default = '', fixed_size = False))
config.plugins.E2Kodi.PBGOklient  = NoSave(ConfigSelection(default = "iCOK", choices = [("iCOK", "iCOK (konto w iPolsat Box)"), 
                                                            ("polsatbox", "polsatbox (konto w Polsat Box Go)"), ]))
config.plugins.E2Kodi.LoginCode  = NoSave(ConfigText(default = '', fixed_size = False))
config.plugins.E2Kodi.avaliable_only = NoSave(ConfigSelection(default = "false", choices = [("false", "wszystkie materiały"), 
                                                            ("true", "tylko materiały dostępne w Twoim pakiecie"), ]))

FrameworksList = [("Odtwarzacz zewnętrzny, framework 1 (zalecany)","1e"), ("Odtwarzacz zewnętrzny, framework 4097 (zalecany dla Vu+)","4097e"), ("Odtwarzacz zewnętrzny, framework 5002","5002e")]

if not os.path.exists('/etc/E2Kodi'):
    os.mkdir('/etc/E2Kodi')

################################################################################################

def readCFG(cfgName, defVal = ''):
    retValue = defVal
    for cfgPath in ['/j00zek/E2Kodi_defaults/','/hdd/User_Configs', '/etc/E2Kodi/']:
        if os.path.exists(os.path.join(cfgPath, cfgName)):
            retValue = open(os.path.join(cfgPath, cfgName), 'r').readline().strip()
            break
    return retValue

def saveCFG(cfgName, val = ''):
    with open(os.path.join('/etc/E2Kodi/', cfgName), 'w') as fw:
        fw.write(val.strip())
        fw.close()

def ensure_str(string2decode):
    if isinstance(string2decode, bytes):
        return string2decode.decode('utf-8', 'ignore')
    return string2decode


class E2Kodi_Menu(Screen):
    skin = """
<screen position="center,center" size="880,540">
        <widget source="list" render="Listbox" position="0,0" size="880,500" scrollbarMode="showOnDemand">
                <convert type="TemplatedMultiContent">
                        {"template": [
                                MultiContentEntryPixmapAlphaTest(pos = (2, 2), size = (120, 40), png = 0),
                                MultiContentEntryText(pos = (138, 2), size = (760, 40), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1),
                                ],
                                "fonts": [gFont("Regular", 24)],
                                "itemHeight": 45
                        }
                </convert>
        </widget>
        <widget name="key_red"    position="20,510" zPosition="2" size="150,30" foregroundColor="red" valign="center" halign="left" font="Regular;22" transparent="1" />
        <widget name="key_green"  position="170,510" zPosition="2" size="150,30" foregroundColor="green" valign="center" halign="left" font="Regular;22" transparent="1" />
        <widget name="key_yellow"  position="360,510" zPosition="2" size="250,30" foregroundColor="yellow" valign="center" halign="left" font="Regular;22" transparent="1" />
        <widget name="key_blue"  position="490,510" zPosition="2" size="200,30" foregroundColor="blue" valign="center" halign="left" font="Regular;22" transparent="1" />
        <widget name="key_ok"  position="690,510" zPosition="2" size="350,30" foregroundColor="gray" valign="center" halign="left" font="Regular;22" transparent="1" />
</screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        print('E2Kodi_Menu.__init__() >>>')
        self.setup_title = "E2Kodi menu v. %s" % Version
        Screen.setTitle(self, self.setup_title)
        self["list"] = List()
        # Buttons
        self["key_red"] = Label("Anuluj")
        self.ShowAllServices = False
        self["key_green"] = Label('Pokaż wszystkie')
        self["key_ok"] = Label() #OK - Konfiguracja')
        self["key_yellow"] = Label('Wejdź do wtyczki')
        self["key_blue"] = Label('wł/wył')
        self["setupActions"] = ActionMap(["E2KodiMenu"],
            {
                    "cancel": self.quit,
                    "config": self.configSelected,
                    "keyGreen": self.keyGreen,
                    "keyYellow": self.keyYellow,
                    "keyBlue": self.keyBlue,
            }, -2)
        self.setTitle(self.setup_title)
        try:
            with open('/usr/lib/enigma2/python/Plugins/Extensions/E2Kodi/addons.json', 'r') as jf:
                self.addonsDict = json.load(jf)
        except Exception as e:
            print('E2Kodi_Menu', str(e))
            self.addonsDict = {'Błąd ładowania danych :(': {"enabled": None, "error": True}}
        self["list"].list = []
        self.createsetup()

    def keyBlue(self):
        SelectedAddonKey = str(self["list"].getCurrent()[2])
        SelectedAddonDef = self.addonsDict.get(SelectedAddonKey, None)
        if SelectedAddonDef is None:
            return
        elif SelectedAddonDef.get('addonScript', None) is None:
            return
        isHiddenFile = SelectedAddonDef['addonScript'].split('/')[0] + '.ukryty'
        isHiddenFile = os.path.join('/etc/E2Kodi/',isHiddenFile)
        if os.path.exists(isHiddenFile):
            os.remove(isHiddenFile)
        elif SelectedAddonDef.get('enabled', False) == False:
            return
        else:
            open(isHiddenFile, "w").write('')
        self.createsetup()

    def keyGreen(self):
        if self.ShowAllServices:
            self.ShowAllServices = False
            self["key_green"].setText('Pokaż wszystkie')
        else:
            self.ShowAllServices = True
            self["key_green"].setText('Pokaż tylko wspierane')
        self.createsetup()

    def keyYellow(self):
        SelectedAddonKey = str(self["list"].getCurrent()[2])
        SelectedAddonDef = self.addonsDict.get(SelectedAddonKey, None)
        if SelectedAddonDef is None or SelectedAddonDef.get('enabled', False) == False:
            print('[E2Kodi_Menu.keyYellow] %s addon not existing or not enabled, exiting' % SelectedAddonKey)
            return
        else:
            self.storeselectedMenuIndex()
            #tworzenie katalogu konfiguracyjnego
            cfgDir = SelectedAddonDef.get('cfgDir', '')
            if not os.path.exists('/etc/E2Kodi/%s' % cfgDir):
                os.system('mkdir -p /etc/E2Kodi/%s' % cfgDir)
            #uruchamianie ekranu konfiguracyjnego
            try:
                self.session.openWithCallback(self.doNothing, E2KodiPlayer, SelectedAddonDef)
            except Exception as e:
                import traceback
                exc_formatted = traceback.format_exc().strip()
                print('[E2Kodi_Menu.keyYellow] exception:', exc_formatted)
                self.session.openWithCallback(self.doNothing,MessageBox, '...' + '\n'.join(exc_formatted.splitlines()[-6:]), MessageBox.TYPE_INFO)
            return

    def createsetup(self):
        Mlist = []
        cdmStatus = None
        try:
            from  pywidevine.cdmdevice.checkCDMvalidity import testDevice
            cdmStatus = testDevice()
            print('E2Kodi_Menu cdmStatus = "%s"' % cdmStatus)
        except Exception as e: 
            print('E2Kodi_Menu',str(e))
            Mlist.append(self.buildListEntry(None, r'\c00981111' + "*** Błąd ładowania modułu urządzenia cdm ***", "info.png"))
        open('/etc/E2Kodi/cdmStatus','w').write(str(cdmStatus))
        if cdmStatus is None:
            Mlist.append(self.buildListEntry(None, r'\c00981111' + "*** Błąd sprawdzania urządzenia cdm ***", "info.png"))

        if not cdmStatus is None:
            listAddons = True
            if os.path.exists('/iptvplayer_rootfs/usr/bin/exteplayer3'):
                if not os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/plugin.pe2i'):
                    ActiveExtPlayer = 'prywatny dzięki uprzejmości SSS'
                else:
                    ActiveExtPlayer = 'z prywatnego pakietu e2iplayer-a'
            elif os.path.exists('/usr/bin/exteplayer3'):
                ActiveExtPlayer = 'publiczny'
                print('E2Kodi_Menu cpuinfo', open('/proc/cpuinfo', 'r').read())
            else:
                ActiveExtPlayer = 'BRAK doinstaluj pakiet exteplayer3, lub serviceapp !!!'
                listAddons = False
            Mlist.append(self.buildListEntry(None, "Aktywny odtwarzacz: %s" % ActiveExtPlayer, "noCover.png"))
            addonKeysList = []
            if listAddons:
                for addonKey in sorted(self.addonsDict, key=str.casefold):
                    addonDef = self.addonsDict[addonKey]
                    isHiddenFile = addonDef['addonScript'].split('/')[0] + '.ukryty'
                    isHiddenFile = os.path.join('/etc/E2Kodi/',isHiddenFile)
                    if os.path.exists(isHiddenFile):
                        addonDef['UserHidden'] = True
                    else:
                        addonDef['UserHidden'] = False
                    if addonDef.get('error', False):
                        Mlist = []
                        Mlist.append(self.buildListEntry(addonKey))
                    elif (addonDef.get('enabled', False) and addonDef['UserHidden'] == False) or self.ShowAllServices:
                        Mlist.append(self.buildListEntry(addonKey))

        self["list"].list = Mlist
        self["list"].setCurrentIndex(config.plugins.E2Kodi.MenuInitIndex.value)
        print('E2Kodi_Menu setCurrentIndex', config.plugins.E2Kodi.MenuInitIndex.value)

    def buildListEntry(self, addonKey, description = '', image='',):
        if addonKey is not None:
            addonDef = self.addonsDict[addonKey]
            image = addonDef.get('icon', 'config.png')
            #opis
            if addonDef['UserHidden']:
                description = r'\c00ffa500' + "!!! WYłĄCZONA: " + r'\c00ffffff' + addonKey
            elif addonDef.get('enabled', False) == False:
                description = r'\c00ff0000' + "!!! BEZ WSPARCIA: " + r'\c00ffffff' + addonKey
            else:
                description = addonKey
        #ladowanie loga
        if image.endswith('.cfg'):
            addonKey = image
            image = 'config.png'
        image = '/usr/lib/enigma2/python/Plugins/Extensions/E2Kodi/pic/%s' % image
        if os.path.exists(image):
            pixmap = LoadPixmap(image)
        else:
            pixmap = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/E2Kodi/pic/config.png')
        return((pixmap, description, addonKey))

    def storeselectedMenuIndex(self):
        try:
            config.plugins.E2Kodi.MenuInitIndex.value = self["list"].getCurrentIndex()
        except Exception:
            config.plugins.E2Kodi.MenuInitIndex.value = self["list"].getSelectedIndex() #np. openvix
        print('getCurrentIndex', config.plugins.E2Kodi.MenuInitIndex.value)

    def configSelected(self):
        SelectedAddonKey = str(self["list"].getCurrent()[2])
        SelectedAddonDef = self.addonsDict.get(SelectedAddonKey, None)
        if SelectedAddonKey == 'OFF-ActiveServiceappPlayer.cfg':
            if os.path.exists('/etc/E2Kodi/ActiveServiceappPlayer'):
                os.remove('/etc/E2Kodi/ActiveServiceappPlayer')
            else:
                open("/etc/E2Kodi/ActiveServiceappPlayer", "w").write('')
            self.createsetup()
        elif SelectedAddonDef is None:
            print('E2Kodi_Menu.configSelected(%s) addon not existing, exiting' % SelectedAddonKey)
            return
        elif os.path.exists(os.path.join('/etc/E2Kodi/',SelectedAddonDef['addonScript'].split('/')[0] + '.ukryty')):
            print('E2Kodi_Menu.configSelected(%s) addon disabled by user, exiting' % SelectedAddonKey)
            self.session.openWithCallback(self.doNothing,MessageBox, "Najpierw włącz dodatek!", MessageBox.TYPE_INFO, timeout = 5)
            return
        else:
            self.storeselectedMenuIndex()
            #tworzenie katalogu konfiguracyjnego
            cfgDir = SelectedAddonDef.get('cfgDir', None)
            if cfgDir is None:
                self.keyYellow()
                return
            else:
                if not os.path.exists('/etc/E2Kodi/%s' % cfgDir):
                    os.system('mkdir -p /etc/E2Kodi/%s' % cfgDir)
                if len(SelectedAddonDef.get('cfgValues', [])) == 0 and len(SelectedAddonDef.get('cfgFiles', [])) == 0:
                    self.keyYellow()
                    return
                else: #uruchamianie ekranu konfiguracyjnego
                    try:
                        self.session.openWithCallback(self.doNothing, E2KodiConfiguration, SelectedAddonDef)
                    except Exception as e:
                        exc_formatted = traceback.format_exc().strip()
                        print('E2Kodi_Menu.configSelected exception:', exc_formatted)
                        self.session.openWithCallback(self.doNothing,MessageBox, '...' + '\n'.join(exc_formatted.splitlines()[-6:]), MessageBox.TYPE_INFO)
            return

    def doNothing(self, retVal = None):
        return
                
    def quit(self):
        self.close()

######################################################################################################################################################

class E2KodiConfiguration(Screen, ConfigListScreen):
    if getDesktop(0).size().width() == 1920: #definicja skin-a musi byc tutaj, zeby vti sie nie wywalalo na labelach, inaczej trzeba uzywasc zrodla statictext
        skin = """<screen name="E2KodiConfiguration" position="center,center" size="1000,300" title="E2Kodi configuration">
                    <widget name="config"     position="20,20"   zPosition="1" size="960,220" scrollbarMode="showOnDemand" />
                    <widget name="key_red"    position="20,250"  zPosition="2" size="240,30" foregroundColor="red"    valign="center" halign="left" font="Regular;22" transparent="1" />
                    <widget name="key_green"  position="260,250" zPosition="2" size="240,30" foregroundColor="green"  valign="center" halign="left" font="Regular;22" transparent="1" />
                    <widget name="key_yellow"  position="500,250" zPosition="2" size="240,30" foregroundColor="yellow" valign="center" halign="left" font="Regular;22" transparent="1" />
                  </screen>"""
    else:
        skin = """<screen name="E2KodiConfiguration" position="center,center" size="700,300" title="E2Kodi configuration">
                    <widget name="config"     position="20,20" size="640,225" zPosition="1" scrollbarMode="showOnDemand" />
                    <widget name="key_red"    position="20,250" zPosition="2" size="150,30" foregroundColor="red" valign="center" halign="left" font="Regular;22" transparent="1" />
                    <widget name="key_green"  position="170,250" zPosition="2" size="150,30" foregroundColor="green" valign="center" halign="left" font="Regular;22" transparent="1" />
                    <widget name="key_yellow"  position="360,250" zPosition="2" size="240,30" foregroundColor="yellow" valign="center" halign="left" font="Regular;22" transparent="1" />
                  </screen>"""
    def buildList(self):
        Mlist = []
        for cfgFile in self.SelectedAddonDef.get('cfgFiles',[]):
            if '=' in cfgFile:
                defVal = str(cfgFile.split('=')[1])
                cfgFile = cfgFile.split('=')[0]
            else:
                defVal = ""
            if not os.path.exists('/etc/E2Kodi/%s/%s' % (self.addonName,cfgFile)):
                open('/etc/E2Kodi/%s/%s' % (self.addonName,cfgFile), 'w').write(defVal)
                            
        #ladowanie konfiguracji
        self.cfgValues2Configs = []
        if self.SelectedAddonDef.get('cfgValues',[]) != []:
            #info
            Mlist.append(getConfigListEntry(r'\c00f2ec73' + "Możesz też wpisać dane bezpośrednio w /etc/E2Kodi/%s" % self.addonName))
            for cfgValue in self.SelectedAddonDef.get('cfgValues',[]):
                actVal = readCFG('%s/%s' % (self.addonName, cfgValue), defVal = '')
                if cfgValue == 'username':
                    config.plugins.E2Kodi.username.value = actVal
                    Mlist.append(getConfigListEntry( 'Użytkownik' , config.plugins.E2Kodi.username))
                    self.cfgValues2Configs.append(('username', config.plugins.E2Kodi.username))
                elif cfgValue == 'password':
                    config.plugins.E2Kodi.password.value = actVal
                    Mlist.append(getConfigListEntry( 'Hasło' , config.plugins.E2Kodi.password))
                    self.cfgValues2Configs.append(('password', config.plugins.E2Kodi.password))
                elif cfgValue == 'klient':
                    config.plugins.E2Kodi.PBGOklient.value = actVal
                    Mlist.append(getConfigListEntry( 'Klient' , config.plugins.E2Kodi.PBGOklient))
                    self.cfgValues2Configs.append(('klient', config.plugins.E2Kodi.PBGOklient))
                elif cfgValue == 'LoginCode':
                    config.plugins.E2Kodi.LoginCode.value = actVal
                    Mlist.append(getConfigListEntry( 'LoginCode' , config.plugins.E2Kodi.LoginCode))
                    self.cfgValues2Configs.append(('LoginCode', config.plugins.E2Kodi.LoginCode))
                elif cfgValue == 'avaliable_only':
                    config.plugins.E2Kodi.avaliable_only.value = actVal
                    Mlist.append(getConfigListEntry( 'avaliable_only' , config.plugins.E2Kodi.avaliable_only))
                    self.cfgValues2Configs.append(('avaliable_only', config.plugins.E2Kodi.avaliable_only))

        #Akcje
        login_info = readCFG('%s/login_info' % self.addonName, defVal = '')
        if login_info != '':
            login_info = login_info.replace('[COLOR gold]','').replace('[/COLOR]','')
            Mlist.append(getConfigListEntry(login_info))
        #logowanie
        if len(self.SelectedAddonDef.get('login',[])) > 0:
            Mlist.append(getConfigListEntry( "Logowanie do serwisu", config.plugins.E2Kodi.configItem, 'login'))
        #logowanieTV
        elif len(self.SelectedAddonDef.get('loginTV',[])) > 0:
            Mlist.append(getConfigListEntry('Logowanie kodem urządzenia (w przeglądarce)', config.plugins.E2Kodi.configItem, 'loginTV'))
        #pobieranie listy
        if len(self.SelectedAddonDef.get('userbouquet',[])) > 0:
            Mlist.append(getConfigListEntry( "Generowanie bukietu programów" , config.plugins.E2Kodi.configItem, 'userbouquet'))
        #wylogowanie
        if len(self.SelectedAddonDef.get('logout',[])) > 0:
            Mlist.append(getConfigListEntry( "Wylogowanie z serwisu", config.plugins.E2Kodi.configItem, 'logout'))
        #czyszczenie danych
        Mlist.append(getConfigListEntry( "Czyszczenie/kasowanie konfiguracji", config.plugins.E2Kodi.configItem, 'clean'))
        return Mlist
    
    def __init__(self, session, SelectedAddonDef):
        print('E2KodiConfiguration.__init__() >>>')
        self.SelectedAddonDef = SelectedAddonDef
        self.addonName = self.SelectedAddonDef.get('cfgDir','')
        self.plikBukietu = '/etc/enigma2/userbouquet.%s.tv' % self.addonName
        self.cfgValues2Configs = []
        self.pythonRunner = '/usr/bin/python'
        self.addonScript = self.SelectedAddonDef.get('addonScript','')
        self.runAddon = '%s %s' % (self.pythonRunner, os.path.join(addons_path, self.addonScript))

        Screen.__init__(self, session)
        self.session = session

        # Summary
        self.setup_title = 'Konfguracja %s' % self.SelectedAddonDef.get('cfgDir','')
        self.onChangedEntry = []

        # Buttons
        self["key_red"] = Label(_("Cancel"))
        self["key_green"] = Label(_("Save"))
        self["key_yellow"] = Label('Wejdź do wtyczki')
        #self["key_blue"] = Label()

        # Define Actions
        self["actions"] = ActionMap(["E2KodiConfiguration"],
            {
                "cancel":   self.exit,
                "red"   :   self.exit,
                "green" :   self.save,
                "keyYellow" :   self.keyYellow,
                "ok":       self.Okbutton,
            }, -2)
        
        self.onLayoutFinish.append(self.layoutFinished)
        ConfigListScreen.__init__(self, self.buildList(), on_change = self.changedEntry)

    def saveCFGs(self):
        for value2Config in self.cfgValues2Configs:
            actVal = readCFG('%s/%s' % (self.addonName, value2Config[0]), defVal = '')
            if readCFG('%s/%s' % (self.addonName, value2Config[0]), defVal = '') != value2Config[1].value:
                saveCFG('%s/%s' % (self.addonName, value2Config[0]), value2Config[1].value)

    def save(self):
        self.saveCFGs()
        self.close(None)
        
    def doNothing(self, ret = False):
        return

    def keyYellow(self):
        try:
            self.session.openWithCallback(self.doNothing, E2KodiPlayer, self.SelectedAddonDef)
        except Exception as e:
            exc_formatted = traceback.format_exc().strip()
            print('E2KodiConfiguration.playSelected exception:', exc_formatted)
            self.session.openWithCallback(self.doNothing,MessageBox, '...' + '\n'.join(exc_formatted.splitlines()[-6:]), MessageBox.TYPE_INFO)
        return
    
    def exit(self):
        self.close(None)
        
    def layoutFinished(self):
        self.setTitle(self.setup_title)
        
    def changedEntry(self):
        print('E2KodiConfiguration.changedEntry() >>>')
        try:
            for x in self.onChangedEntry:
                x()
        except Exception as e:
            print('E2KodiConfiguration.changedEntry()', str(e))

    def getCurrentEntry(self):
        return self["config"].getCurrent()[0]

    def getCurrentValue(self):
        if len(self["config"].getCurrent()) >= 2:
            return str(self["config"].getCurrent()[1].getText())

    def createSummary(self):
        return SetupSummary

    def buildemuKodiCmdsFor(self, ForVal):
        for cmd in self.SelectedAddonDef.get(ForVal,[]):
            cmdLine = '%s %s' % (self.runAddon, cmd)
            print('E2KodiConfiguration.buildemuKodiCmdsFor() cmdLine:', cmdLine)
            self.emuKodiCmdsList.append(cmdLine)
    
    def Okbutton(self):
        try:
            curIndex = self["config"].getCurrentIndex()
            selectedItem = self["config"].list[curIndex]
            print('E2KodiConfiguration.Okbutton() selectedItem:' , str(selectedItem))
            if len(selectedItem) >= 2:
                currItem = selectedItem[1]
                currInfo = selectedItem[0]
                if isinstance(currItem, ConfigText):
                    from Screens.VirtualKeyBoard import VirtualKeyBoard
                    self.session.openWithCallback(self.OkbuttonTextChangedConfirmed, VirtualKeyBoard, title=(currInfo), text = currItem.value)
                elif currItem == config.plugins.E2Kodi.configItem: #bouquets based on KODI plugins
                    self.currAction = selectedItem[2]
                    self.autoClose = False
                    self.emuKodiCmdsList = []
                    if self.currAction == 'login':
                        self.saveCFGs()
                        self.buildemuKodiCmdsFor('login')
                        self.emuKodiActionConfirmed(True)
                        return
                    elif self.currAction == 'loginTV':
                        self.saveCFGs()
                        self.buildemuKodiCmdsFor('loginTV')
                        MsgInfo = "Zostaniesz poproszony o podanie kodu w przeglądarce.\nBędziesz mieć na to maksimum 340 sekund i nie będziesz mógł przerwać.\n\nJesteś gotowy?"
                        self.session.openWithCallback(self.emuKodiActionConfirmed, MessageBox, MsgInfo, MessageBox.TYPE_YESNO, default = False, timeout = 15)
                        return
                    elif self.currAction == 'userbouquet':
                        if os.path.exists(self.plikBukietu):
                            MsgInfo = "Zaktualizować plik %s ?" % self.plikBukietu
                        else:
                            MsgInfo = "Utworzyć plik %s ?" % self.plikBukietu
                        self.session.openWithCallback(self.userbouquetConfirmed, MessageBox, MsgInfo, MessageBox.TYPE_YESNO, default = False, timeout = 15)
                        return
                    elif self.currAction == 'logout':
                        self.buildemuKodiCmdsFor('logout')
                        self.emuKodiActionConfirmed(True)
                        return
                    elif self.currAction == 'clean':
                        self.emuKodiCmdsList.append("rm -f /etc/E2Kodi/%s/*" % self.addonName)
                        self.emuKodiCmdsList.append("echo 'Skasowano wszystkie dane serwisu %s. Wymagany restart!!!'" % self.addonName)
                        self.emuKodiCmdsList.append("sleep 2")
                        self.autoClose = True
                        self.session.openWithCallback(self.emuKodiActionConfirmed, MessageBox, "Na pewno skasować konfigurację %s?" % self.addonName, MessageBox.TYPE_YESNO, default = False, timeout = 15)
                        return
        except Exception as e:
            print('E2KodiConfiguration.Okbutton() Exception: %s' % str(e))

    def OkbuttonTextChangedConfirmed(self, ret ):
        if ret is None:
            print("E2KodiConfiguration.OkbuttonTextChangedConfirmed(ret ='%s')" % str(ret))
        else:
            try:
                curIndex = self["config"].getCurrentIndex()
                self["config"].list[curIndex][1].value = ret
            except Exception as e:
                print('E2KodiConfiguration.OkbuttonTextChangedConfirmed()', str(e))

    def userbouquetConfirmed(self, ret = False):
        if ret:
            self.session.openWithCallback(self.SelectedFramework, ChoiceBox, title = _("Select Multiframework"), list = FrameworksList)

    def SelectedFramework(self, ret):
        if not ret or ret == "None" or isinstance(ret, (int, float)):
            ret = (None,'4097')
        wybranyFramework = ret[1]
        self.emuKodiCmdsList.append("echo 'Pobieranie listy kanałów'")
        self.buildemuKodiCmdsFor('userbouquet')
        self.emuKodiCmdsList.append("sleep 1") #zeby dac czas na zapis plikow kodi.
        self.emuKodiCmdsList.append('%s %s %s "%s" %s' % (self.pythonRunner, os.path.join(emukodi_path, 'e2Bouquets.py'), self.plikBukietu, self.addonScript, wybranyFramework))
        self.emuKodiActionConfirmed(True)

    def emuKodiActionConfirmed(self, ret = False):
        if ret:
            #uruchomienie lancucha komend
            if len(self.emuKodiCmdsList) > 0:
                cleanWorkingDir()
                log("===== %s - %s ====" % (self.addonName, self.currAction))
                self.session.openWithCallback(self.emuKodiConsoleCallback ,emukodiConsole, title = "SL %s %s-%s" % (Version, 'E2Kodi', self.addonName), 
                                                cmdlist = self.emuKodiCmdsList, closeOnSuccess = self.autoClose)

    def emuKodiConsoleCallback(self, ret = False):
        if self.currAction == 'userbouquet':
            #czyszczenie bouquets.tv
            for TypBukietu in('/etc/enigma2/bouquets.tv','/etc/enigma2/bouquets.radio'):
                f = ''
                for line in open(TypBukietu,'r'):
                    if 'FROM BOUQUET' in line:
                        fname = line.split('FROM BOUQUET')[1].strip().split('"')[1].strip()
                        if os.path.exists('/etc/enigma2/%s' % fname):
                            f += line
                    else:
                        f += line
            open(TypBukietu,'w').write(f)
            #przeladowanie bukietow
            eDVBDB.getInstance().reloadBouquets()
            self.session.openWithCallback(self.doNothing,MessageBox, "Bukiety zostały przeładowane", MessageBox.TYPE_INFO, timeout = 5)

######################################################################################################################################################

class E2KodiPlayer(Screen):
    skin = """
<screen position="center,center" size="1200,700" flags="wfNoBorder" >
        <widget name="Title" position="5,5" size="1190,30" font="Regular;24" halign="left" noWrap="1" transparent="1" />
        <widget source="list" render="Listbox" position="5,40" size="1190,500" scrollbarMode="showOnDemand" transparent="1" >
                <convert type="TemplatedMultiContent">
                        {"template": [
                                MultiContentEntryPixmapAlphaTest(pos = (10, 10), size = (40, 40), png = 0),
                                MultiContentEntryText(pos = (60, 2), size = (1130, 40), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1),
                                ],
                                "fonts": [gFont("Regular", 26)],
                                "itemHeight": 45
                        }
                </convert>
        </widget>
        <eLabel position="0,550" size="1200,2"  backgroundColor="#aaaaaa" />
        <widget name="KodiNotificationsAndStatus" position="5,560" size="1190,100" font="Regular;18" halign="left" noWrap="0" transparent="1" backgroundColor="#aa000000"/>

        <widget name="key_red"    position="20,665" zPosition="2" size="150,30" foregroundColor="red" valign="center" halign="left" font="Regular;22" transparent="1" />
        <widget name="key_green"  position="200,665" zPosition="2" size="250,30" foregroundColor="green" valign="center" halign="left" font="Regular;22" transparent="1" />
        <widget name="key_yellow"  position="500,665" zPosition="2" size="350,30" foregroundColor="yellow" valign="center" halign="left" font="Regular;22" transparent="1" />
        <widget name="key_ok"  position="800,665" zPosition="2" size="400,30" foregroundColor="gray" valign="center" halign="left" font="Regular;22" transparent="1" />

</screen>"""

    def __init__(self, session, SelectedAddonDef):
        print('E2KodiPlayer.__init__() >>>')
        self.prev_running_service = None
        self.SelectedAddonDef = SelectedAddonDef
        self.addonName = self.SelectedAddonDef.get('cfgDir','')
        self.plikBukietu = '/etc/enigma2/userbouquet.%s.tv' % self.addonName
        self.cfgValues2Configs = []
        self.pythonRunner = '/usr/bin/python'
        self.addonScript = self.SelectedAddonDef.get('addonScript','')
        self.runAddon = '%s %s' % (self.pythonRunner, os.path.join(addons_path, self.addonScript))
        self.AddonCmd = ''
        self.AddonCmdsDict = {}
        self.InitAddonCmd = "'1' ' '"
        self.LastAddonCmd = ''
        self.headerStatus = ''
        self.deviceCDM = None
        
        self.KodiDirectoryItemsPath = os.path.join(working_dir, 'xbmcplugin_DirectoryItems')
        self.KodiVideoInfoPath = os.path.join(working_dir, 'xbmc_player')

        Screen.__init__(self, session)
        self.setup_title = "%s Player" % self.addonName

        self["key_red"] = Label("Wyjdź")
        self["key_green"] = Label('')
        self["key_ok"] = Label('OK-Wybierz')
        self["key_yellow"] = Label('')

        self["KodiNotificationsAndStatus"] = Label()
        self["Title"] = Label(self.setup_title)
        self["list"] = List()
        self["setupActions"] = ActionMap(["E2KodiPlayer"],
            {
                    "cancel": self.quit,
                    "ok": self.openSelectedMenuItem,
                    "menu": self.quit,
                    "keyYellow": self.keyYellow,
                    "keyGreen": self.keyGreen,
            }, -2)
        
        self["list"].list = []
        self.infoTimer = eTimer()
        self.infoTimer.callback.append(self.showKodiNotificationAndStatus)
        self.timer = eTimer()
        self.timer.callback.append(self.E2KodiCmdRun)
        self.onShown.append(self._onShown)
        self.E2KodiCmd = eConsoleAppContainer()
        self.E2KodiCmd.appClosed.append(self.E2KodiCmdClosed)
        self.E2KodiCmd.dataAvail.append(self.E2KodiCmdAvail)
        try: self.LastPlayedService = self.session.nav.getCurrentlyPlayingServiceReference()
        except Exception: self.LastPlayedService = None
        if not self.selectionChanged in self["list"].onSelectionChanged:
            self["list"].onSelectionChanged.append(self.selectionChanged)
        
    def _onShown(self):
        self.prev_running_service = self.session.nav.getCurrentlyPlayingServiceReference()
        self.AddonCmd = self.InitAddonCmd
        self.headerStatus = ' - inicjalizacja'
        self.LastAddonCmd = ''
        self.timer.start(1000,True) # True=singleshot
        self.infoTimer.start(100)
        self.isShown = True

    def keyGreen(self):
        self.selectedBouquet = None

        def UserbouquetSelected( ret = False): #bukiet wybrany, wybór frameworka
            if ret:
                self.selectedBouquet = ret[1]
                print('UserbouquetSelected', self.selectedBouquet)
                self.session.openWithCallback(SelectedFramework, ChoiceBox, title = _("Select Multiframework"), list = FrameworksList)

        def SelectedFramework(ret = (None,'4097')): #bukiet wybrany, framework wybrany, dodanie do bukietu i odswierzenie
            if not ret or ret == "None":
                ret = (None,'4097')
            wybranyFramework = str(ret[1]).replace('e','')
            refPart = '1:0:0:0:0:0:0:0:0:0:'
            lineToAdd = '#SERVICE %s:0:0:0:0:0:0:0:0:0:' % wybranyFramework
            lineToAdd += 'http%3a//cdmplayer/'
            lineDict = self["list"].getCurrent()[2]
            AddonCmd = str(lineDict.get('url'))
            AddonCmd = AddonCmd.split('Plugins/')[1]
            lineToAdd += AddonCmd
            lineToAdd += ':'
            lineToAdd += self.cleanKodiText(lineDict.get('label', lineDict.get('Title', 'Nieznane wideo')), True)
            print('[E2KodiPlayer.keyGreen] lineToAdd',lineToAdd)
            with open(os.path.join('/etc/enigma2', self.selectedBouquet), 'a') as File:
                File.write(lineToAdd+'\n')
                File.close()
            #przeladowanie bukietow
            eDVBDB.getInstance().reloadBouquets()
            self.session.openWithCallback(self.doNothing,MessageBox, "Material dodany do bukietu i bukiety zostały przeładowane", MessageBox.TYPE_INFO, timeout = 5)
        
        #wybor bukietu
        currItem = self["list"].getCurrent()[2]
        if currItem.get('isPlayable', False):
            listaBukietow = []
            with open('/etc/enigma2/bouquets.tv', 'r') as inFile:
                for line in inFile:
                    if line.startswith('#SERVICE'):
                        line = line.split('"')[1]
                        listaBukietow.append((line.replace('userbouquet.','').replace('.tv',''), line))
            print('listaBukietow', listaBukietow)
            self.session.openWithCallback(UserbouquetSelected, ChoiceBox, title = "Wybierz bukiet", list = listaBukietow)

    def keyYellow(self):
        if self.isShown:
            self.hide()
            self.isShown = False
        else:
            self.show()

    def showKodiNotificationAndStatus(self):
        self["Title"].setText(self.setup_title + self.headerStatus)

    def cleanKodiText(self, textToClean, doRemove = False):
        #https://html-color.codes/
        colorCodes = [('[B]',''), ('[/B]',''),
                      ('[I]',''), ('[/I]',''),
                      ('[CR]',' \n'),
                      ('()',''),
                      ('[/COLOR]',           r'\c00ffffff'),
                      ('[COLOR blue]',       r'\c000000ff'),
                      ('[COLOR cyan]',       r'\c0000ffff'),
                      ('[COLOR gold]',       r'\c00ffd700'),
                      ('[COLOR khaki]',      r'\c00C3B091'),
                      ('[COLOR lightblue]',  r'\c00add8e6'),
                      ('[COLOR lime]',       r'\c0000ff00'),
                      ('[COLOR orange]',     r'\c00ffa500'),
                      ('[COLOR red]',        r'\c00ff0000'),
                      ('[COLOR violet]',     r'\c00ee82ee'),
                      ('[COLOR white]',      r'\c00ffffff'),
                      ('[COLOR yellowgreen]',r'\c00adff2f'),
                    ]
        for colorCode in colorCodes:
            if doRemove:
                textToClean = textToClean.replace(colorCode[0],'')
            else:
                textToClean = textToClean.replace(colorCode[0],colorCode[1])
        return textToClean
    
    def selectionChanged(self):
        print('E2KodiPlayer.selectionChanged()')
        try:
            currItem = self["list"].getCurrent()[2]
            if currItem.get('plot', None) is not None:
                self["KodiNotificationsAndStatus"].setText(self.cleanKodiText(currItem.get('plot', '')))
            else:
                self["KodiNotificationsAndStatus"].setText(' ')
            if currItem.get('isPlayable', False):
                self["key_green"].setText('Dodaj do bukietu')
            else:
                self["key_green"].setText('')
        except Exception as e:
            print('E2KodiPlayer.selectionChanged()', str(e))

    def E2KodiCmdRun(self):
        self.timer.stop()
        if self.AddonCmd == '':
            print('E2KodiPlayer.E2KodiCmdRun() - nie podano komendy :(')
        elif 0: #self.AddonCmdsDict.get(self.AddonCmd, None) is not None:
            self.E2KodiCmdClosed('Mlist')
        else:
            self.headerStatus = ' - ładowanie danych'
            cleanWorkingDir()
            cmd2run = '%s %s ' % (self.runAddon, self.AddonCmd)
            print('E2KodiPlayer.E2KodiCmdRun() cmd2run "%s"' % cmd2run)
            self.E2KodiCmd.execute(cmd2run)

    def E2KodiCmdAvail(self, text = ''):
        text = ensure_str(text)
        if text != '':
            tmpText = self["KodiNotificationsAndStatus"].getText()
            self["KodiNotificationsAndStatus"].setText(tmpText + text)
        
    def E2KodiCmdClosed(self, retval):
        print('E2KodiPlayer.E2KodiCmdClosed(retval = %s)' % retval)
        if retval == 'Mlist':
            self.AddonCmdsDict.get(self.AddonCmd, {})
        elif os.path.exists(self.KodiVideoInfoPath):
            self.headerStatus = ' - odtwarzanie materiału'
            self.playVideo()
        else:
            self.createTree()
            self.headerStatus = ' - oczekiwanie'
            self.LastAddonCmd = self.AddonCmd

    def createTree(self):
        print('E2KodiPlayer.createTree() >>>')
        Mlist = []
        
        if self.AddonCmd != self.InitAddonCmd:
            Mlist.append(self.buildListEntry({'label': '<< Początek', 'thumbnailImage': None, 'url': self.InitAddonCmd, 'isFolder': True}))
            Mlist.append(self.buildListEntry({'label': '< Cofnij', 'thumbnailImage': None, 'url': self.LastAddonCmd}))
        else:
            if os.path.exists(self.plikBukietu):
                Mlist.append(self.buildListEntry({'label': '>>> Wygenerowany bukiet <<<', 'thumbnailImage': None, 'url': 'plikBukietu'}))

        if self.AddonCmd == 'plikBukietu':
            with open(self.plikBukietu, 'r') as inFile:
                for line in inFile:
                    if line.startswith('#SERVICE'):
                        items = line.split(':')
                        Mlist.append(self.buildListEntry({'label': items[11], 'thumbnailImage': None, 'url': items[10]}))
                    
        
        elif os.path.exists(self.KodiDirectoryItemsPath):
            with open(self.KodiDirectoryItemsPath, 'r') as inFile:
                for line in inFile:
                    try:
                        lineDict = json.loads(line)
                        #print(lineDict)
                        Mlist.append(self.buildListEntry(lineDict))
                    except Exception as e:
                        exc_formatted = traceback.format_exc().strip()
                        print('E2KodiPlayer.createTree exception:', exc_formatted)
                        Mlist.append(self.buildListEntry({'label': 'Błąd ładowania linii :(', 'thumbnailImage':'error.png'}))
        self["list"].list = Mlist
        self.AddonCmdsDict[self.AddonCmd] = Mlist
        self.setTitle(self.setup_title + ' - oczekiwanie')

    def buildListEntry(self, lineDict): #&name=...&url=...&thumbnailImage=...&iconlImage=...&url=...
        title = self.cleanKodiText(lineDict.get('label', ''))
        if lineDict.get('label2', None) is not None:
            if lineDict.get('label2') != lineDict.get('label'):
                title += '' + self.cleanKodiText(lineDict.get('label2'))
        elif lineDict.get('plot', None) is not None:
            if lineDict.get('plot') != lineDict.get('label'):
                plot = self.cleanKodiText(lineDict.get('plot'))
                plot = plot.split('\n')[0]
                title += ' ' + plot
        if len(title) > 90:
            title = title[:90] + '...'
        #ladowanie image
        #print(lineDict.get('IsPlayable', 'AQQ'))
        if lineDict.get('isFolder', False):
            image = 'folder.png'
        elif lineDict.get('isPlayable', False) == True or lineDict.get('IsPlayable', '') == 'true':
            lineDict['isPlayable'] = True
            image = 'movie.png'
        elif not lineDict.get('thumbnailImage', None) is None:
            image = lineDict.get('thumbnailImage')
        elif not lineDict.get('iconImage', None) is None:
            image = lineDict.get('iconImage')
        else:
            image = 'noCover.png'
        if len(image) > 4 and image[-4:] in ('.png','.jpg', '.svg'):
            image = '/usr/lib/enigma2/python/Plugins/Extensions/E2Kodi/pic/%s' % image
            if not os.path.exists(image):
                image = '/usr/lib/enigma2/python/Plugins/Extensions/E2Kodi/pic/noCover.png'
        pixmap = LoadPixmap(image)
        return((pixmap, title, lineDict))

    def stopVideo(self):
        print("[E2KodiPlayer.stopVideo] >>>")
        self["key_yellow"].setText('')
        if not self.deviceCDM is None:
            self.deviceCDM.stopPlaying() #wyłącza playera i czyści bufor dvb, bez tego  mamy 5s opóźnienia
        for pidFile in ['/var/run/cdmDevicePlayer.pid', '/var/run/emukodiCLI.pid', '/var/run/exteplayer3.pid']:
            if os.path.exists(pidFile):
                pid = open(pidFile, 'r').readline().strip()
                if os.path.exists('/proc/%s' % pid):
                    os.kill(int(pid), signal.SIGTERM) #or signal.SIGKILL
                os.remove(pidFile)

    def playVideo(self, url = ''):
        self["key_yellow"].setText('ukryj/pokaż GUI')
        if self.deviceCDM is None: #tutaj, zeby bez sensu nie ladować jak ktos nie ma/nie uzywa
            try:
                import pywidevine.cdmdevice.cdmDevice
                #reload(pywidevine.cdmdevice.cdmDevice) #NIE dziala bo zaladowany do eventow
                self.deviceCDM = pywidevine.cdmdevice.cdmDevice.cdmDevice()
                print("[E2KodiPlayer.playVideo] deviceCDM loaded")
            except ImportError:
                self.deviceCDM = False
                print("[E2KodiPlayer.playVideo] EXCEPTION loading deviceCDM")
        if self.deviceCDM != False:
            print("[E2KodiPlayer.playVideo] self.deviceCDM != False")
            self.session.nav.stopService()
            if url == '':
                self.deviceCDM.tryToDoSomething(self.addonScript)
            else:
                self.deviceCDM.tryToDoSomething(url)
    
    def openSelectedMenuItem(self):
        self.stopVideo()
        lineDict = self["list"].getCurrent()[2]
        print('E2KodiPlayer.openSelectedMenuItem',lineDict)
        self["KodiNotificationsAndStatus"].setText(str(lineDict))
        
        if 1: #lineDict.get('isFolder', False):
            self.AddonCmd = str(lineDict.get('url', "?"))
            if self.AddonCmd == "?":
                self["KodiNotificationsAndStatus"].setText("Nie zdefinowana komenda :( ")
                return
            elif self.AddonCmd == "plikBukietu":
                self["KodiNotificationsAndStatus"].setText("ładuje plik bukietu")
                self.createTree()
                return
            elif self.AddonCmd.startswith('http%3a//cdmplayer/'):
                self["KodiNotificationsAndStatus"].setText(self.AddonCmd)
                self.playVideo(self.AddonCmd)
                return
            elif 0: #str(lineDict.get('IsPlayable', '?')) in ['true','True'] or 'playvid' in self.AddonCmd:
                self["KodiNotificationsAndStatus"].setText('Play')
                self.playVideo(self.AddonCmd)
                return
            elif self.AddonCmd.startswith('/usr/') and "?" in self.AddonCmd:
                self.AddonCmd = "'1' '?" + self.AddonCmd.split('?')[1] + "' 'resume:false'"
            
            self["KodiNotificationsAndStatus"].setText(self.AddonCmd)
            self.headerStatus = ' - ładowanie %s' % lineDict.get('label', "?")
            self.E2KodiCmdRun()
        
    def doNothing(self, retVal = None):
        return
                
    def quit(self):
        self.stopVideo()
        if self.prev_running_service:
            self.session.nav.playService(self.prev_running_service)
        self.close()
