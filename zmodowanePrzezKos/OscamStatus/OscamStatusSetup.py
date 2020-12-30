from __init__ import _
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.MenuList import MenuList
from Components.ConfigList import ConfigListScreen
from Components.Sources.List import List
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components.config import config
from Components.config import NoSave
from Components.config import ConfigIP
from Components.config import ConfigText
from Components.config import ConfigYesNo
from Components.config import ConfigInteger
from Components.config import ConfigPassword
from Components.config import ConfigSubsection
from Components.config import getConfigListEntry
from enigma import eListboxPythonMultiContent, eListbox, getDesktop, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, RT_WRAP, ePoint, eSize, eRect, loadPNG
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_CURRENT_PLUGIN, SCOPE_SKIN
import re, os.path
config.plugins.OscamStatus = ConfigSubsection()
config.plugins.OscamStatus.lastServer = ConfigInteger(default=0)
config.plugins.OscamStatus.extMenu = ConfigYesNo(default=True)
config.plugins.OscamStatus.xOffset = ConfigInteger(default=50, limits=(0, 100))
config.plugins.OscamStatus.useECM = ConfigYesNo(default=False)
config.plugins.OscamStatus.useIP = ConfigYesNo(default=True)
config.plugins.OscamStatus.usePicons = ConfigYesNo(default=False)
LASTSERVER = config.plugins.OscamStatus.lastServer
EXTMENU = config.plugins.OscamStatus.extMenu
XOFFSET = config.plugins.OscamStatus.xOffset
USEECM = config.plugins.OscamStatus.useECM
USEPICONS = config.plugins.OscamStatus.usePicons
oscam_regex = {'ConfigDir': re.compile('ConfigDir:\\s*(?P<ConfigDir>.*)\\n'),
 'httpport': re.compile('httpport\\s*=\\s*(?P<httpport>[\\+]?\\d+)\\n'),
 'httpuser': re.compile('httpuser\\s*=\\s*(?P<httpuser>.*)\\n'),
 'httppwd': re.compile('httppwd\\s*=\\s*(?P<httppwd>.*)\\n')}

def _parse_line(line):
    for key, rx in oscam_regex.items():
        match = rx.search(line)
        if match:
            return (key, match)

    return (None, None)


def parse_oscam_version_file(filepath, data):
    if os.path.isfile(filepath):
        with open(filepath, 'r') as file_object:
            line = file_object.readline()
            while line:
                key, match = _parse_line(line)
                if key == 'ConfigDir':
                    data.ConfigDir = match.group('ConfigDir')
                line = file_object.readline()

        return 1
    return 0


def parse_oscam_conf_file(filepath, data):
    if os.path.isfile(filepath):
        with open(filepath, 'r') as file_object:
            line = file_object.readline()
            while line:
                key, match = _parse_line(line)
                if key == 'httpport':
                    port = match.group('httpport')
                    data.serverName = 'Autodetected'
                    if port[0] == '+':
                        data.useSSL = True
                        data.serverPort = port[1:]
                    else:
                        data.serverPort = port
                if key == 'httpuser':
                    data.username = match.group('httpuser')
                if key == 'httppwd':
                    data.password = match.group('httppwd')
                line = file_object.readline()


def dlg_xh(w):
    x = getDesktop(0).size().width() - w - XOFFSET.value
    if x < 0:
        x = 0
    h = getDesktop(0).size().height()
    return (x, h)


class globalsConfigScreen(Screen, ConfigListScreen):
    w = getDesktop(0).size().width()
    if w >= 1920:
        skin = """
              <screen flags="wfNoBorder" position="%d,0" size="860,%d" name="globalsConfigScreen" >
                <widget render="Label" source="title" position="30,20" size="600,49" valign="center" zPosition="5" transparent="0" foregroundColor="#fcc000" font="Regular;33"/>
                <widget name="config" position="30,80" size="800,900" scrollbarMode="showOnDemand" font="Regular;28" itemHeight="36"/>
                <eLabel text="" position="30,932" size="800,3" transparent="0" backgroundColor="#ffffff" />
                <ePixmap name="ButtonRed" pixmap="skin_default/buttons/red.png" position="30,940" size="210,60" zPosition="4" transparent="1" alphatest="on"/>
                <widget render="Label" source= "ButtonRedtext" position="30,940" size="210,60" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;30"/>
                <ePixmap name="ButtonGreen" pixmap="skin_default/buttons/key_green.png" position="245,940" size="210,60" zPosition="4" transparent="1" alphatest="on"/>
                <widget render="Label" source= "ButtonGreentext" position="245,940" size="210,60" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;30"/>
              </screen>""" % dlg_xh(860)
    else:
        skin = """
              <screen flags="wfNoBorder" position="%d,0" size="440,%d" name="globalsConfigScreen" >
                <widget render="Label" source="title" position="20,80" size="400,26" valign="center" zPosition="5" transparent="0" foregroundColor="#fcc000" font="Regular;22"/>
                <widget name="config" position="20,130" size="400,200" scrollbarMode="showOnDemand" />
                <eLabel text="" position="20,450" size="400,2" transparent="0" backgroundColor="#ffffff" />
                <ePixmap name="ButtonRed" pixmap="skin_default/buttons/red.png" position="20,460" size="140,40" zPosition="4" transparent="1" alphatest="on"/>
                <widget render="Label" source= "ButtonRedtext" position="20,460" size="140,40" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>
                <ePixmap name="ButtonGreen" pixmap="skin_default/buttons/key_green.png" position="160,460" size="140,40" zPosition="4" transparent="1" alphatest="on"/>
                <widget render="Label" source= "ButtonGreentext" position="160,460" size="140,40" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>
              </screen>""" % dlg_xh(440)

    def __init__(self, session):
        self.skin = globalsConfigScreen.skin
        self.session = session
        Screen.__init__(self, session)
        list = []
        list.append(getConfigListEntry(_('Show Plugin in Extensions Menu'), config.plugins.OscamStatus.extMenu))
        list.append(getConfigListEntry(_('X-Offset (move left)'), config.plugins.OscamStatus.xOffset))
        list.append(getConfigListEntry(_('ECM Time in connected Dialog'), config.plugins.OscamStatus.useECM))
        list.append(getConfigListEntry(_('Server address always in IP Format'), config.plugins.OscamStatus.useIP))
        list.append(getConfigListEntry(_('Use Picons'), config.plugins.OscamStatus.usePicons))
        ConfigListScreen.__init__(self, list, session=session)
        self['title'] = StaticText(_('Oscam Status globals Setup'))
        self['ButtonRedtext'] = StaticText(_('return'))
        self['ButtonGreentext'] = StaticText(_('save'))
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'red': self.Exit,
         'green': self.Save,
         'cancel': self.Exit}, -1)
        self.onLayoutFinish.append(self.LayoutFinished)

    def LayoutFinished(self):
        x, h = dlg_xh(self.instance.size().width())
        self.instance.move(ePoint(x, 0))

    def Save(self):
        for x in self['config'].list:
            x[1].save()

        self.close()

    def Exit(self):
        for x in self['config'].list:
            x[1].cancel()

        self.close()

    def createSummary(self):
        return OscamLCDScreen


class oscamServer:
    serverName = _('NewServer')
    serverIP = '127.0.0.1'
    serverPort = '8081'
    username = _('username')
    password = _('password')
    useSSL = False


CFG = resolveFilename(SCOPE_CURRENT_PLUGIN, '/etc/enigma2/oscamstatus.cfg')

def readCFG():
    cfg = None
    oscamServers = []
    try:
        cfg = file(CFG, 'r')
    except:
        pass

    if cfg:
        print '[OscamStatus] reading config file...'
        d = cfg.read()
        cfg.close()
        for line in d.splitlines():
            v = line.strip().split(' ')
            if len(v) == 6:
                tmp = oscamServer()
                tmp.username = v[0]
                tmp.password = v[1]
                tmp.serverIP = v[2]
                tmp.serverPort = v[3]
                tmp.serverName = v[4]
                tmp.useSSL = bool(int(v[5]))
                if tmp.serverName != 'Autodetected':
                    oscamServers.append(tmp)

    if len(oscamServers) == 0:
        print '[OscamStatus] no config file found'
    tmp = oscamServer()
    if parse_oscam_version_file('/tmp/.oscam/oscam.version', tmp):
        if hasattr(tmp, 'ConfigDir'):
            parse_oscam_conf_file(tmp.ConfigDir + '/oscam.conf', tmp)
    oscamServers.append(tmp)
    return oscamServers


def writeCFG(oscamServers):
    cfg = file(CFG, 'w')
    savedconfig = 0
    print '[OscamStatus] writing datfile...'
    for line in oscamServers:
        if line.serverName != 'Autodetected':
            cfg.write(line.username + ' ')
            cfg.write(line.password + ' ')
            cfg.write(line.serverIP + ' ')
            cfg.write(line.serverPort + ' ')
            cfg.write(line.serverName + ' ')
            cfg.write(str(int(line.useSSL)) + '\n')
            savedconfig = 1

    cfg.close()
    if not savedconfig:
        os.remove(CFG)


class OscamServerEntryList(MenuList):

    def __init__(self, list, enableWrapAround = True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        w = getDesktop(0).size().width()
        if w >= 1920:
            self.l.setFont(0, gFont('Regular', 30))
            self.l.setFont(1, gFont('Regular', 27))
        else:
            self.l.setFont(0, gFont('Regular', 20))
            self.l.setFont(1, gFont('Regular', 18))
        
        if os.path.exists(resolveFilename(SCOPE_SKIN, 'skin_default/icons/lock_off.png')):
            self.pic0 = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN, 'skin_default/icons/lock_off.png'))
        else:
            self.pic0 = None
        if os.path.exists(resolveFilename(SCOPE_SKIN, 'skin_default/icons/lock_on.png')):
            self.pic1 = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN, 'skin_default/icons/lock_on.png'))
        else:
            self.pic1 = None

    def postWidgetCreate(self, instance):
        MenuList.postWidgetCreate(self, instance)
        instance.setItemHeight(40)

    def makeList(self, index):
        self.list = []
        oscamServers = readCFG()
        for cnt, i in enumerate(oscamServers):
            res = [i]
            if cnt == index:
                if self.pic1:
                    res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST,
                     5,
                     1,
                     25,
                     24,
                     self.pic1))
                else:
                    res.append((eListboxPythonMultiContent.TYPE_TEXT,
                     5,
                     3,
                     25,
                     24,
                     1,
                     RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                     'x'))
            elif self.pic0:
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST,
                 5,
                 1,
                 25,
                 24,
                 self.pic0))
            else:
                res.append((eListboxPythonMultiContent.TYPE_TEXT,
                 5,
                 3,
                 25,
                 24,
                 1,
                 RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                 ' '))
            res.append((eListboxPythonMultiContent.TYPE_TEXT,
             40,
             3,
             120,
             24,
             1,
             RT_HALIGN_LEFT | RT_VALIGN_CENTER,
             i.serverName))
            w = getDesktop(0).size().width()
            if w >= 1920:
                res.append((eListboxPythonMultiContent.TYPE_TEXT,
                 40,
                 1,
                 270,
                 28,
                 1,
                 RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                 i.serverName))
                res.append((eListboxPythonMultiContent.TYPE_TEXT,
                 330,
                 1,
                 210,
                 36,
                 1,
                 RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                 i.serverIP))
            else:
                res.append((eListboxPythonMultiContent.TYPE_TEXT,
                 40,
                 3,
                 120,
                 24,
                 1,
                 RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                 i.serverName))
                res.append((eListboxPythonMultiContent.TYPE_TEXT,
                 165,
                 3,
                 275,
                 24,
                 1,
                 RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                 i.serverIP))
            if i.useSSL:
                tx = 'SSL'
            else:
                tx = ''
            if w >= 1920:
                res.append((eListboxPythonMultiContent.TYPE_TEXT,
                 545,
                 3,
                 50,
                 36,
                 1,
                 RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                 tx))
            else:
                res.append((eListboxPythonMultiContent.TYPE_TEXT,
                 370,
                 3,
                 30,
                 24,
                 1,
                 RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                 tx))
            self.list.append(res)

        self.l.setList(self.list)
        self.moveToIndex(index)


class OscamServerEntriesListConfigScreen(Screen):
    w = getDesktop(0).size().width()
    if w >= 1920:
        skin = '\n\t\t\t<screen flags="wfNoBorder" position="%d,0" size="700,%d" name="OscamServerEntriesListConfigScreen" >\n\t\t\t\t<widget render="Label" source="title" position="30,30" size="360,36" valign="center" zPosition="5" transparent="0" foregroundColor="#fcc000" font="Regular;33"/>\n\t\t\t\t<widget name="list" position="30,80" size="620,840" scrollbarMode="showOnDemand" />\n\t\t\t\t<eLabel text="" position="30,932" size="640,3" transparent="0" backgroundColor="#ffffff" />\n\t\t\t\t<ePixmap name="ButtonGreen" pixmap="skin_default/buttons/key_green.png" position="20,940" size="210,60" zPosition="4" transparent="1" alphatest="on"/>\n\t\t\t\t<widget render="Label" source= "ButtonGreentext" position="20,940" size="210,60" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;27"/>\n\t\t\t\t<ePixmap name="ButtonYellow" pixmap="skin_default/buttons/yellow.png" position="235,940" size="210,60" zPosition="4" transparent="1" alphatest="on"/>\n\t\t\t\t<widget render="Label" source= "ButtonYellowtext" position="235,940" size="210,60" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;27"/>\n\t\t\t\t<ePixmap name="ButtonBlue" pixmap="skin_default/buttons/blue.png" position="450,940" size="210,60" zPosition="4" transparent="1" alphatest="on"/>\n\t\t\t\t<widget render="Label" source= "ButtonBluetext" position="450,940" size="210,60" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;27"/>\n\t\t\t</screen>' % dlg_xh(700)
    else:
        skin = '\n\t\t\t<screen flags="wfNoBorder" position="%d,0" size="440,%d" name="OscamServerEntriesListConfigScreen" >\n\t\t\t\t<widget render="Label" source="title" position="20,80" size="360,26" valign="center" zPosition="5" transparent="0" foregroundColor="#fcc000" font="Regular;22"/>\n\t\t\t\t<widget name="list" position="20,130" size="400,288" scrollbarMode="showOnDemand" />\n\t\t\t\t<eLabel text="" position="20,450" size="400,2" transparent="0" backgroundColor="#ffffff" />\n\t\t\t\t<ePixmap name="ButtonGreen" pixmap="skin_default/buttons/key_green.png" position="10,460" size="140,40" zPosition="4" transparent="1" alphatest="on"/>\n\t\t\t\t<widget render="Label" source= "ButtonGreentext" position="10,460" size="140,40" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>\n\t\t\t\t<ePixmap name="ButtonYellow" pixmap="skin_default/buttons/yellow.png" position="150,460" size="140,40" zPosition="4" transparent="1" alphatest="on"/>\n\t\t\t\t<widget render="Label" source= "ButtonYellowtext" position="150,460" size="140,40" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="black" font="Regular;18"/>\n\t\t\t\t<ePixmap name="ButtonBlue" pixmap="skin_default/buttons/blue.png" position="290,460" size="140,40" zPosition="4" transparent="1" alphatest="on"/>\n\t\t\t\t<widget render="Label" source= "ButtonBluetext" position="290,460" size="140,40" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>\n\t\t\t</screen>' % dlg_xh(440)

    def __init__(self, session):
        self.skin = OscamServerEntriesListConfigScreen.skin
        self.session = session
        Screen.__init__(self, session)
        self['list'] = OscamServerEntryList([])
        self['list'].makeList(config.plugins.OscamStatus.lastServer.value)
        self['title'] = StaticText(_('Oscam Servers'))
        self['ButtonGreentext'] = StaticText(_('new'))
        self['ButtonYellowtext'] = StaticText(_('edit'))
        self['ButtonBluetext'] = StaticText(_('delete'))
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'green': self.keyNew,
         'yellow': self.keyEdit,
         'blue': self.keyDelete,
         'ok': self.keyOk,
         'cancel': self.keyClose}, -1)
        self.onLayoutFinish.append(self.LayoutFinished)

    def LayoutFinished(self):
        x, h = dlg_xh(self.instance.size().width())
        self.instance.move(ePoint(x, 0))

    def updateEntrys(self):
        self['list'].makeList(config.plugins.OscamStatus.lastServer.value)

    def keyNew(self):
        self.session.openWithCallback(self.updateEntrys, OscamServerEntryConfigScreen, None, -1)
        return

    def keyEdit(self):
        try:
            entry = self['list'].l.getCurrentSelection()[0]
        except:
            entry = None

        if entry:
            self.session.openWithCallback(self.updateEntrys, OscamServerEntryConfigScreen, entry, self['list'].getSelectionIndex())
        return

    def keyDelete(self):
        try:
            self.index = self['list'].getSelectionIndex()
        except:
            self.index = -1

        if self.index > -1:
            if self.index == config.plugins.OscamStatus.lastServer.value:
                print '[OscamStatus] you can not delete the active entry...'
                return
        message = _('Do you really want to delete this entry?')
        msg = self.session.openWithCallback(self.Confirmed, MessageBox, message)
        msg.setTitle('Oscam Status')

    def Confirmed(self, confirmed):
        if not confirmed:
            return
        oscamServers = readCFG()
        del oscamServers[self.index]
        writeCFG(oscamServers)
        if self.index < config.plugins.OscamStatus.lastServer.value:
            config.plugins.OscamStatus.lastServer.value -= 1
        self.updateEntrys()

    def keyOk(self):
        try:
            entry = self['list'].l.getCurrentSelection()[0]
        except:
            entry = None

        if entry:
            config.plugins.OscamStatus.lastServer.value = self['list'].getSelectionIndex()
            config.plugins.OscamStatus.lastServer.save()
            self.close(entry)
        return

    def keyClose(self):
        self.close(False)

    def createSummary(self):
        return OscamLCDScreen


class OscamServerEntryConfigScreen(Screen, ConfigListScreen):
    w = getDesktop(0).size().width()
    if w >= 1920:
        skin = '\n\t\t\t<screen flags="wfNoBorder" position="%d,0" size="800,%d" name="OscamServerEntryConfigScreen" >\n\t\t\t\t<widget render="Label" source="title" position="20,60" size="600,39" valign="center" zPosition="5" transparent="0" foregroundColor="#fcc000" font="Regular;33"/>\n\t\t\t\t<widget name="config" position="20,110" size="760,800" scrollbarMode="showOnDemand" font="Regular;28" itemHeight="32" />\n\t\t\t\t<eLabel text="" position="20,900" size="800,4" transparent="0" backgroundColor="#ffffff" />\n\t\t\t\t<ePixmap name="ButtonRed" pixmap="skin_default/buttons/red.png" position="20,930" size="210,60" zPosition="4" transparent="1" alphatest="on"/>\n\t\t\t\t<widget render="Label" source= "ButtonRedtext" position="20,930" size="210,60" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;28"/>\n\t\t\t\t<ePixmap name="ButtonGreen" pixmap="skin_default/buttons/key_green.png" position="240,930" size="210,60" zPosition="4" transparent="1" alphatest="on"/>\n\t\t\t\t<widget render="Label" source= "ButtonGreentext" position="240,930" size="210,60" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;28"/>\n\t\t\t</screen>' % dlg_xh(800)
    else:
        skin = '\n\t\t\t<screen flags="wfNoBorder" position="%d,0" size="440,%d" name="OscamServerEntryConfigScreen" >\n\t\t\t\t<widget render="Label" source="title" position="20,80" size="400,26" valign="center" zPosition="5" transparent="0" foregroundColor="#fcc000" font="Regular;22"/>\n\t\t\t\t<widget name="config" position="20,130" size="400,200" scrollbarMode="showOnDemand" />\n\t\t\t\t<eLabel text="" position="20,450" size="400,2" transparent="0" backgroundColor="#ffffff" />\n\t\t\t\t<ePixmap name="ButtonRed" pixmap="skin_default/buttons/red.png" position="20,460" size="140,40" zPosition="4" transparent="1" alphatest="on"/>\n\t\t\t\t<widget render="Label" source= "ButtonRedtext" position="20,460" size="140,40" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>\n\t\t\t\t<ePixmap name="ButtonGreen" pixmap="skin_default/buttons/key_green.png" position="160,460" size="140,40" zPosition="4" transparent="1" alphatest="on"/>\n\t\t\t\t<widget render="Label" source= "ButtonGreentext" position="160,460" size="140,40" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>\n\t\t\t</screen>' % dlg_xh(440)

    def __init__(self, session, entry, index):
        self.skin = OscamServerEntryConfigScreen.skin
        self.session = session
        Screen.__init__(self, session)
        if entry == None:
            entry = oscamServer()
        self.index = index
        serverIP = self.isIPaddress(entry.serverIP)
        if serverIP and config.plugins.OscamStatus.useIP.value:
            self.isIP = True
        else:
            self.isIP = False
        serverPort = int(entry.serverPort)
        self.serverNameConfigEntry = NoSave(ConfigText(default=entry.serverName, fixed_size=False, visible_width=20))
        if self.isIP:
            self.serverIPConfigEntry = NoSave(ConfigIP(default=serverIP, auto_jump=True))
        else:
            self.serverIPConfigEntry = NoSave(ConfigText(default=entry.serverIP, fixed_size=False, visible_width=20))
            self.serverIPConfigEntry.setUseableChars(u'1234567890aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ.-_')
        self.portConfigEntry = NoSave(ConfigInteger(default=serverPort, limits=(0, 65536)))
        self.usernameConfigEntry = NoSave(ConfigText(default=entry.username, fixed_size=False, visible_width=20))
        self.passwordConfigEntry = NoSave(ConfigPassword(default=entry.password, fixed_size=False))
        self.useSSLConfigEntry = NoSave(ConfigYesNo(entry.useSSL))
        ConfigListScreen.__init__(self, [], session=session)
        self.createSetup()
        self['title'] = StaticText(_('Oscam Server Setup'))
        self['ButtonRedtext'] = StaticText(_('return'))
        self['ButtonGreentext'] = StaticText(_('save'))
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'red': self.Close,
         'green': self.Save,
         'cancel': self.Close}, -1)
        self.onLayoutFinish.append(self.LayoutFinished)
        return

    def LayoutFinished(self):
        x, h = dlg_xh(self.instance.size().width())
        self.instance.move(ePoint(x, 0))

    def createSetup(self):
        self.list = []
        self.list.append(getConfigListEntry(_('Oscam Server Name'), self.serverNameConfigEntry))
        self.list.append(getConfigListEntry(_('Oscam Server Address'), self.serverIPConfigEntry))
        self.list.append(getConfigListEntry(_('Port'), self.portConfigEntry))
        self.list.append(getConfigListEntry(_('Username (httpuser)'), self.usernameConfigEntry))
        self.list.append(getConfigListEntry(_('Password (httppwd)'), self.passwordConfigEntry))
        self.list.append(getConfigListEntry(_('use SSL'), self.useSSLConfigEntry))
        self['config'].setList(self.list)

    def isIPaddress(self, txt):
        theIP = txt.split('.')
        if len(theIP) != 4:
            return False
        serverIP = []
        for x in theIP:
            try:
                serverIP.append(int(x))
            except:
                return False

        return serverIP

    def Close(self):
        self.close()

    def Save(self):
        entry = oscamServer()
        entry.username = self.usernameConfigEntry.value
        entry.password = self.passwordConfigEntry.value
        entry.serverName = self.serverNameConfigEntry.value
        if self.isIP:
            entry.serverIP = '%d.%d.%d.%d' % tuple(self.serverIPConfigEntry.value)
        else:
            entry.serverIP = self.serverIPConfigEntry.value
        entry.serverPort = str(self.portConfigEntry.value)
        entry.useSSL = self.useSSLConfigEntry.value
        oscamServers = readCFG()
        if self.index == -1:
            oscamServers.append(entry)
        else:
            oscamServers[self.index] = entry
        writeCFG(oscamServers)
        self.close()

    def createSummary(self):
        return OscamLCDScreen


class OscamLCDScreen(Screen):
    skin = '\n\t<screen position="0,0" size="132,64" title="Oscam Status configuration">\n\t\t<widget name="headline" position="4,0" size="128,22" font="Regular;20"/>\n\t</screen>'

    def __init__(self, session, parent):
        Screen.__init__(self, session, parent)
        self['headline'] = Label(_('Oscam Status configuration'))