#
# mod by Kos, j00zek

# List of changes:
# 04.10.2020 - added audio codec & bitrate to genere --> favorites, Yellow button stations from shoutcast.com
# 24.12.2019 - improved display of tags in the station list, improved 'def ok_pressed'
# 23.12.2019 - improve VFD/LCD handling + code clean ups
# 22.12.2019 - improve skins flexibility bu using defined renderers in skins instead of hard coded label


from Plugins.Plugin import PluginDescriptor
from urlparse import urlparse
from Screens.Screen import Screen
from Screens.InfoBar import InfoBar
from Components.SystemInfo import SystemInfo
from Components.ActionMap import ActionMap
from Components.Label import Label
from enigma import eServiceReference, eListboxPythonMultiContent, eListbox, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_VALIGN_CENTER, getDesktop, iPlayableService, iServiceInformation, eTimer, eConsoleAppContainer, ePicLoad
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists
import xml.etree.cElementTree
from twisted.internet import reactor, defer
from twisted.web import client
from twisted.web.client import HTTPClientFactory
from Components.Pixmap import Pixmap
from Components.ScrollLabel import ScrollLabel
import string, os, re, skin
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigDirectory, ConfigYesNo, Config, ConfigInteger, ConfigSubList, ConfigText, ConfigNumber, getConfigListEntry, configfile
from Components.ConfigList import ConfigListScreen
from Screens.MessageBox import MessageBox
from Components.GUIComponent import GUIComponent
from Components.Sources.StaticText import StaticText
from urllib import quote
from twisted.web.client import downloadPage
from Screens.ChoiceBox import ChoiceBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.Input import Input
from Screens.InputBox import InputBox
from Components.FileList import FileList
from . import _
coverfiles = ('/tmp/.cover.ping', '/tmp/.cover.pong')
containerStreamripper = None
config.plugins.shoutcast = ConfigSubsection()
config.plugins.shoutcast.showcover = ConfigYesNo(default=True)
config.plugins.shoutcast.where = ConfigSelection(default='0', choices=[('0', (_('Bing'))), ('1', (_('Google')))])
config.plugins.shoutcast.showinextensions = ConfigYesNo(default=False)
config.plugins.shoutcast.streamingrate = ConfigSelection(default='0', choices=[('0', (_('All speeds'))),
 ('64', ('>= 64 kbps')),
 ('96', ('>= 96 kbps')),
 ('128', ('>= 128 kbps')),
 ('192', ('>= 192 kbps')),
 ('256', ('>= 256 kbps')),
 ('320', ('>= 320 kbps'))])
config.plugins.shoutcast.reloadstationlist = ConfigSelection(default='0', choices=[('0', (_('Off'))),
 ('1', (_('every minute'))),
 ('3', (_('every three minutes'))),
 ('5', (_('every five minutes')))])
config.plugins.shoutcast.dirname = ConfigDirectory(default='/media/hdd/streamripper/')
config.plugins.shoutcast.riptosinglefile = ConfigYesNo(default=False)
config.plugins.shoutcast.createdirforeachstream = ConfigYesNo(default=True)
config.plugins.shoutcast.addsequenceoutputfile = ConfigYesNo(default=False)
config.plugins.shoutcast.pos_cover_width = ConfigNumber(default=605)
config.plugins.shoutcast.pos_cover_height = ConfigNumber(default=585)
config.plugins.shoutcast.size_cover_width = ConfigNumber(default=500)
config.plugins.shoutcast.size_cover_height = ConfigNumber(default=500)
config.plugins.shoutcast.lista = ConfigInteger(1, (1, 7))
devid = 'fa1jo93O_raeF0v9'

class SHOUTcastGenre():

    def __init__(self, name = '', id = 0, haschilds = 'false', parentid = 0, opened = 'false'):
        self.name = name
        self.id = id
        self.haschilds = haschilds
        self.parentid = parentid
        self.opened = opened


class SHOUTcastStation():

    def __init__(self, name = '', mt = '', id = '', br = '', genre = '', ct = '', lc = '', ml = '', nsc = '', cst = ''):
        self.name = name.replace('- a SHOUTcast.com member station', '')
        self.mt = mt
        self.id = id
        self.br = br
        self.genre = genre
        self.ct = ct
        self.lc = lc
        self.ml = ml
        self.nsc = nsc
        self.cst = cst


class Favorite():

    def __init__(self, configItem = None):
        self.configItem = configItem


class myHTTPClientFactory(HTTPClientFactory):

    def __init__(self, url, method = 'GET', postdata = None, headers = None, agent = 'Mozilla/5.0 (Windows NT 6.1; rv:17.0) Gecko/20100101 Firefox/17.0', timeout = 0, cookies = None, followRedirect = 1, lastModified = None, etag = None):
        HTTPClientFactory.__init__(self, url, method=method, postdata=postdata, headers=headers, agent=agent, timeout=timeout, cookies=cookies, followRedirect=followRedirect)

    def clientConnectionLost(self, connector, reason):
        lostreason = 'Connection was closed cleanly' in vars(reason)
        if lostreason == None:
            print '[SHOUTcast] Lost connection, reason: %s ,trying to reconnect!' % reason
            connector.connect()
        return

    def clientConnectionFailed(self, connector, reason):
        print '[SHOUTcast] connection failed, reason: %s,trying to reconnect!' % reason
        connector.connect()


def sendUrlCommand(url, contextFactory = None, timeout = 60, *args, **kwargs):
    parsed = urlparse(url)
    scheme = parsed.scheme
    host = parsed.hostname
    port = parsed.port or (443 if scheme == 'https' else 80)
    path = parsed.path or '/'
    factory = myHTTPClientFactory(url, *args, **kwargs)
    # print "scheme=%s host=%s port=%s path=%s\n" % (scheme, host, port, path)
    reactor.connectTCP(host, port, factory, timeout=timeout)
    return factory.deferred


def main(session, **kwargs):
    session.open(SHOUTcastWidget)


def Plugins(**kwargs):
    list = [PluginDescriptor(name='SHOUTcast', description=_('listen to shoutcast internet-radio'), where=[PluginDescriptor.WHERE_PLUGINMENU], icon='plugin.png', fnc=main)]
    if config.plugins.shoutcast.showinextensions.value:
        list.append(PluginDescriptor(name='SHOUTcast', description=_('listen to shoutcast internet-radio'), where=[PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=main))
    return list


class SHOUTcastWidget(Screen):
    GENRELIST = 0
    STATIONLIST = 1
    FAVORITELIST = 2
    SEARCHLIST = 3
    STREAMRIPPER_BIN = '/usr/bin/streamripper'
    SC = 'http://api.shoutcast.com'
    SCY = 'http://yp.shoutcast.com'
    FAVORITE_FILE_DEFAULT = '/usr/lib/enigma2/python/Plugins/Extensions/SHOUTcast/favorites'
    FAVORITE_FILE_OLD = '/usr/lib/enigma2/python/Plugins/Extensions/SHOUTcast/favorites.user'
    FAVORITE_FILE = '/etc/enigma2/SHOUTcast.favorites'
    sz_w = getDesktop(0).size().width() - 90
    sz_h = getDesktop(0).size().height() - 95
    print '[SHOUTcast] desktop size %dx%d\n' % (sz_w + 90, sz_h + 100)
    if sz_h < 500:
        sz_h += 4
    skin = '\n\t\t<screen name="SHOUTcastWidget" position="center,65" title="SHOUTcast" size="%d,%d" backgroundColor="#00000000">\n\t\t\t<ePixmap position="5,0" zPosition="4" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap position="150,0" zPosition="4" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap position="295,0" zPosition="4" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap position="440,0" zPosition="4" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap pixmap="skin_default/buttons/key_menu.png" position="585,10" zPosition="0" size="35,25" alphatest="on" />\n\t\t\t<widget render="Label" source="key_red" position="5,0" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget render="Label" source="key_green" position="150,0" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget render="Label" source="key_yellow" position="295,0" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget render="Label" source="key_blue" position="440,0" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;20" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget source="headertext" render="Label" position="5,47" zPosition="1" size="%d,23" font="Regular;20" transparent="1"  backgroundColor="#00000000"/>\n\t\t\t<widget source="statustext" render="Label" position="200,240" zPosition="1" size="%d,90" font="Regular;20" halign="center" valign="center" transparent="0"  backgroundColor="#00000000"/>\n\t\t\t<widget name="list" position="5,80" zPosition="2" size="%d,%d" scrollbarMode="showOnDemand" transparent="0"  backgroundColor="#00000000"/>\n\t\t\t<widget source="titel" render="Label" position="0,%d" zPosition="1" size="%d,40" font="Regular;30" transparent="1"  backgroundColor="#00000000"/>\n\t\t\t<widget source="station" render="Label" position="0,%d" zPosition="1" size="%d,40" font="Regular;30" transparent="1"  backgroundColor="#00000000"/>\n\t\t\t<widget name="console" position="115,%d" zPosition="1" size="%d,40" font="Regular;18" transparent="1"  backgroundColor="#00000000"/>\n\t\t\t<widget name="cover" zPosition="2" position="%d,%d" size="%d,%d" alphatest="blend" />\n\t\t\t<ePixmap position="%d,0" zPosition="4" size="120,35" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SHOUTcast/shoutcast-logo1-fs8.png" transparent="1" alphatest="on" />\n\t\t</screen>' % (sz_w,
     sz_h,
     sz_w - 135,
     sz_w - 100,
     sz_w - 700,
     sz_h - 225,
     sz_h - 85,
     sz_w - 125,
     sz_h - 50,
     sz_w - 125,
     sz_h - 25,
     sz_w - 125,
     sz_w - int(config.plugins.shoutcast.pos_cover_width.value),
     sz_h - int(config.plugins.shoutcast.pos_cover_height.value),
     int(config.plugins.shoutcast.size_cover_width.value),
     int(config.plugins.shoutcast.size_cover_height.value),
     sz_w - 125)

    def __init__(self, session):
        global containerStreamripper
        self.session = session
        Screen.__init__(self, session)
        self.setTitle(_('You Listen to Internet Radio...'))
        self.oldtitle = None
        self.currentcoverfile = 0
        self.currentGoogle = None
        self.nextGoogle = None
        self.currPlay = None
        self.CurrentService = self.session.nav.getCurrentlyPlayingServiceReference()
        self.session.nav.stopService()
        self.session.nav.event.append(self.__event)
        self['cover'] = Cover()
        self['key_red'] = StaticText(_('Record'))
        self['key_green'] = StaticText(_('Genres'))
        self['key_yellow'] = StaticText(_('Stations'))
        self['key_blue'] = StaticText(_('Favorites'))
        self.mode = self.FAVORITELIST
        self['list'] = SHOUTcastList()
        self['list'].connectSelChanged(self.onSelectionChanged)
        self['actions'] = ActionMap(['WizardActions',
         'DirectionActions',
         'ColorActions',
         'EPGSelectActions'], {'ok': self.ok_pressed,
         'back': self.close,
         'menu': self.menu_pressed,
         'input_date_time': self.menu_pressed,
         'red': self.red_pressed,
         'green': self.green_pressed,
         'yellow': self.yellow_pressed,
         'blue': self.blue_pressed,
         'nextBouquet': self.nextPipService,
         'prevBouquet': self.prevPipService}, -1)
        self.stationList = []
        self.stationListIndex = 0
        self.genreList = []
        self.genreListIndex = 0
        self.favoriteList = []
        self.favoriteListIndex = 0
        self.favoriteConfig = Config()
        if os.path.exists(self.FAVORITE_FILE):
            self.favoriteConfig.loadFromFile(self.FAVORITE_FILE)
        elif os.path.exists(self.FAVORITE_FILE_OLD):
            self.favoriteConfig.loadFromFile(self.FAVORITE_FILE_OLD)
        else:
            self.favoriteConfig.loadFromFile(self.FAVORITE_FILE_DEFAULT)
        self.favoriteConfig.entriescount = ConfigInteger(0)
        self.favoriteConfig.Entries = ConfigSubList()
        self.initFavouriteConfig()
        self.stationListXML = ''
        self['titel'] = StaticText()
        self['station'] = StaticText()
        self['headertext'] = StaticText()
        self['statustext'] = StaticText()
        self['console'] = Label()
        self.headerTextString = ''
        self.stationListHeader = ''
        self.tunein = ''
        self.searchSHOUTcastString = ''
        self.currentStreamingURL = ''
        self.currentStreamingStation = ''
        self.stationListURL = ''
        self.onClose.append(self.__onClose)
        self.onLayoutFinish.append(self.getFavoriteList)
        self.reloadStationListTimer = eTimer()
        self.reloadStationListTimer.timeout.get().append(self.reloadStationListTimerTimeout)
        self.reloadStationListTimerVar = int(config.plugins.shoutcast.reloadstationlist.value)
        self.visible = True
        if containerStreamripper is None:
            containerStreamripper = eConsoleAppContainer()
        containerStreamripper.dataAvail.append(self.streamripperDataAvail)
        containerStreamripper.appClosed.append(self.streamripperClosed)
        if containerStreamripper.running():
            self['key_red'].setText(_('Stop record'))
            # just to listen to recording music when starting the plugin...
            self.currentStreamingStation = _('Recording stream station')
            self.playServiceStream('http://localhost:9191')            
        if InfoBar.instance is not None:
            self.servicelist = InfoBar.instance.servicelist
        else:
            self.servicelist = None
        slist = self.servicelist
        if slist:
            try:
                self.pipZapAvailable = slist.dopipzap
            except:
                self.pipZapAvailable = None

    def openServiceList(self):
        if self.pipZapAvailable is None:
            return
        if self.servicelist and self.servicelist.dopipzap:
            self.session.execDialog(self.servicelist)
        else:
            self.showWindow()

    def activatePiP(self):
        if self.pipZapAvailable is None:
            return
        else:
            if SystemInfo.get('NumVideoDecoders', 1) > 1:
                if InfoBar.instance is not None:
                    modeslist = []
                    keyslist = []
                    if InfoBar.pipShown(InfoBar.instance):
                        slist = self.servicelist
                        if slist:
                            try:
                                if slist.dopipzap:
                                    modeslist.append((_('Zap focus to main screen'), 'pipzap'))
                                else:
                                    modeslist.append((_('Zap focus to Picture in Picture'), 'pipzap'))
                                keyslist.append('red')
                            except:
                                pass

                        modeslist.append((_('Move Picture in Picture'), 'move'))
                        keyslist.append('green')
                        modeslist.append((_('Disable Picture in Picture'), 'stop'))
                        keyslist.append('blue')
                    else:
                        if len(self.currentStreamingURL) == 0:
                            self.session.open(MessageBox, _('First play streaming!'), MessageBox.TYPE_INFO, timeout=5)
                            return
                        modeslist.append((_('Activate Picture in Picture'), 'start'))
                        keyslist.append('blue')
                    dlg = self.session.openWithCallback(self.pipAnswerConfirmed, ChoiceBox, title=_('Choose action:'), list=modeslist, keys=keyslist)
                    dlg.setTitle(_('Menu PiP'))

    def pipAnswerConfirmed(self, answer):
        answer = answer and answer[1]
        if answer is None:
            return
        else:
            if answer == 'pipzap':
                try:
                    InfoBar.togglePipzap(InfoBar.instance)
                    if self.visible:
                        self.hideWindow()
                except:
                    pass

            elif answer == 'move':
                if InfoBar.instance is not None:
                    InfoBar.movePiP(InfoBar.instance)
            elif answer == 'stop':
                if InfoBar.instance is not None:
                    if InfoBar.pipShown(InfoBar.instance):
                        slist = self.servicelist
                        try:
                            if slist and slist.dopipzap:
                                slist.togglePipzap()
                        except:
                            pass

                        if hasattr(self.session, 'pip'):
                            del self.session.pip
                        self.session.pipshown = False
            elif answer == 'start':
                prev_playingref = self.session.nav.getCurrentlyPlayingServiceReference()
                if prev_playingref:
                    self.session.nav.currentlyPlayingServiceReference = None
                InfoBar.showPiP(InfoBar.instance)
                if self.visible:
                    self.hideWindow()
                if prev_playingref:
                    self.session.nav.currentlyPlayingServiceReference = prev_playingref
                slist = self.servicelist
                if slist:
                    try:
                        if not slist.dopipzap and hasattr(self.session, 'pip'):
                            InfoBar.togglePipzap(InfoBar.instance)
                    except:
                        pass

    def nextPipService(self):
        if self.pipZapAvailable is None:
            return
        elif self.visible:
            return
        else:
            try:
                slist = self.servicelist
                if slist and slist.dopipzap:
                    if slist.inBouquet():
                        prev = slist.getCurrentSelection()
                        if prev:
                            prev = prev.toString()
                            while True:
                                if config.usage.quickzap_bouquet_change.value and slist.atEnd():
                                    slist.nextBouquet()
                                else:
                                    slist.moveDown()
                                cur = slist.getCurrentSelection()
                                if not cur or not cur.flags & 64 or cur.toString() == prev:
                                    break

                    else:
                        slist.moveDown()
                    slist.zap(enable_pipzap=True)
            except:
                pass

    def prevPipService(self):
        if self.pipZapAvailable is None:
            return
        elif self.visible:
            return
        else:
            try:
                slist = self.servicelist
                if slist and slist.dopipzap:
                    if slist.inBouquet():
                        prev = slist.getCurrentSelection()
                        if prev:
                            prev = prev.toString()
                            while True:
                                if config.usage.quickzap_bouquet_change.value:
                                    if slist.atBegin():
                                        slist.prevBouquet()
                                slist.moveUp()
                                cur = slist.getCurrentSelection()
                                if not cur or not cur.flags & 64 or cur.toString() == prev:
                                    break

                    else:
                        slist.moveUp()
                    slist.zap(enable_pipzap=True)
            except:
                pass

    def streamripperClosed(self, retval):
        if retval == 0:
            self['console'].setText('')
            self['statustext'].setText('')
        self['key_red'].setText(_('Record'))


    def streamripperDataAvail(self, data):
        sData = data.replace('\n', '')
        self['console'].setText(sData)
        self['statustext'].setText ('\c00289496' + (_('Recording station:  ') + ('\c00??;?00%s') % self.currentStreamingStation))

    def stopReloadStationListTimer(self):
        if self.reloadStationListTimer.isActive():
            self.reloadStationListTimer.stop()

    def reloadStationListTimerTimeout(self):
        self.stopReloadStationListTimer()
        if self.mode == self.STATIONLIST:
            # print "[SHOUTcast] reloadStationList: %s " % self.stationListURL
            sendUrlCommand(self.stationListURL, None, 10).addCallback(self.callbackStationList).addErrback(self.callbackStationListError)

    def InputBoxStartRecordingCallback(self, returnValue = None):
        if returnValue:
            recordingLength = int(returnValue) * 60
            if not os.path.exists(config.plugins.shoutcast.dirname.value):
                try:
                    os.mkdir(config.plugins.shoutcast.dirname.value)
                except:
                    self.session.open(MessageBox, _('Error create directory %s!') % config.plugins.shoutcast.dirname.value, MessageBox.TYPE_ERROR, timeout=10)
                    return

            args = []
            args.append(self.currentStreamingURL)
            args.append('-d')
            args.append(config.plugins.shoutcast.dirname.value)
            args.append('-r')
            args.append('9191')
            if recordingLength != 0:
                args.append('-l')
                args.append('%d' % int(recordingLength))
            if config.plugins.shoutcast.riptosinglefile.value:
                args.append('-a')
                args.append('-A')
            if not config.plugins.shoutcast.createdirforeachstream.value:
                args.append('-s')
            if config.plugins.shoutcast.addsequenceoutputfile.value:
                args.append('-q')
            if not fileExists(self.STREAMRIPPER_BIN):
                self.session.open(MessageBox, _('streamripper not installed!'), MessageBox.TYPE_ERROR, timeout=10)
                return
            cmd = [self.STREAMRIPPER_BIN, self.STREAMRIPPER_BIN] + args
            containerStreamripper.execute(*cmd)
            self['key_red'].setText(_('Stop record'))

    def deleteRecordingConfirmed(self, val):
        if val:
            containerStreamripper.sendCtrlC()

    def red_pressed(self):
        if self.visible:
            if containerStreamripper.running():
                self.session.openWithCallback(self.deleteRecordingConfirmed, MessageBox, _('Do you really want to stop the recording?'))
            elif len(self.currentStreamingURL) != 0:
                self.session.openWithCallback(self.InputBoxStartRecordingCallback, InputBox, windowTitle=_('Recording length'), title=_('Enter in minutes (0 means unlimited)'), text='0', type=Input.NUMBER)
            else:
                self.session.open(MessageBox, _('Only running streamings can be recorded!'), type=MessageBox.TYPE_INFO, timeout=20)
        elif self.pipZapAvailable is not None and SystemInfo.get('NumVideoDecoders', 1) > 1:
            self.activatePiP()
        else:
            self.showWindow()

    def green_pressed(self):
        if self.visible:
            if self.mode != self.GENRELIST:
                self['statustext'].setText(_('Select a genre, then press OK to proceed.'))
                self.stopReloadStationListTimer()
                self.mode = self.GENRELIST
            if not self.genreList:
                self.getGenreList()
            else:
                self.showGenreList()
        else:
            self.showWindow()

    def yellow_pressed(self):
        baza_list = ['http://api.shoutcast.com/station/advancedsearch&f=xml&k=fa1jo93O_raeF0v9&search=Polska',
         'http://api.shoutcast.com/station/advancedsearch&f=xml&k=fa1jo93O_raeF0v9&search=Trance',
         'http://api.shoutcast.com/station/advancedsearch&f=xml&k=fa1jo93O_raeF0v9&search=Dance',
         'http://api.shoutcast.com/station/advancedsearch&f=xml&k=fa1jo93O_raeF0v9&search=Techno',
         'http://api.shoutcast.com/station/advancedsearch&f=xml&k=fa1jo93O_raeF0v9&search=90s',
         'http://api.shoutcast.com/station/randomstations?k=fa1jo93O_raeF0v9&f=xml',
         'http://api.shoutcast.com/station/advancedsearch&f=xml&k=fa1jo93O_raeF0v9&search=all']
        self.stationListURL = baza_list[config.plugins.shoutcast.lista.value - 1]
        tag = self.stationListURL.replace('http://api.shoutcast.com/station/advancedsearch&f=xml&k=fa1jo93O_raeF0v9&search=all', '')
        if tag == '':
            tag = _('ALL STATIONS')         
        elif tag == 'http://api.shoutcast.com/station/advancedsearch&f=xml&k=fa1jo93O_raeF0v9&search=Polska':
            tag = _('Poland')
        elif tag == 'http://api.shoutcast.com/station/advancedsearch&f=xml&k=fa1jo93O_raeF0v9&search=Trance':
            tag = _('Trance')
        elif tag == 'http://api.shoutcast.com/station/advancedsearch&f=xml&k=fa1jo93O_raeF0v9&search=Dance':
            tag = _('Dance')          
        elif tag == 'http://api.shoutcast.com/station/advancedsearch&f=xml&k=fa1jo93O_raeF0v9&search=Techno':
            tag = _('Techno')            
        elif tag == 'http://api.shoutcast.com/station/advancedsearch&f=xml&k=fa1jo93O_raeF0v9&search=90s':
            tag = _('90s')
        elif tag == 'http://api.shoutcast.com/station/randomstations?k=fa1jo93O_raeF0v9&f=xml':
            tag = _('Random stations')
        if self.visible:
            if self.mode != self.STATIONLIST:
                if self.visible:
                    self.mode = self.STATIONLIST
                    self.stationListHeader = ' www.api.shoutcast.com'
                    self.headerTextString = _('Station list from %s %s') % (self.stationListHeader, tag)
                    self['headertext'].setText(self.headerTextString)
                    self['statustext'].setText(_('Loading station list, please wait ...'))
                    self['list'].setMode(self.mode)
                    self['list'].setList([ (x,) for x in self.stationList ])
                    self['list'].moveToIndex(self.stationListIndex)
                    self.reloadStationListTimer.start(10000 * self.reloadStationListTimerVar)
                    
        else:
            self.showWindow()

    def blue_pressed(self):
        if self.visible:
            if self.mode != self.FAVORITELIST:
                self.stopReloadStationListTimer()
                self.getFavoriteList(self.favoriteListIndex)
        elif self.pipZapAvailable is not None and SystemInfo.get('NumVideoDecoders', 1) > 1:
            self.openServiceList()
        else:
            self.showWindow()
        return

    def getFavoriteList(self, favoriteListIndex = 0):
        if config.plugins.shoutcast.where.value == '0':
            gdzie = _(' - Cover from Bing')
        else:
            gdzie = _(' - Cover from Google')
        self.headerTextString = _('Favorite list') + gdzie
        self['headertext'].setText(self.headerTextString)
        self['statustext'].setText(_('Select a station then press OK to start playback.'))
        self.mode = self.FAVORITELIST
        self['list'].setMode(self.mode)
        favoriteList = []
        for item in self.favoriteConfig.Entries:
            favoriteList.append(Favorite(configItem=item))
        self['list'].setList([ (x,) for x in favoriteList ])
        if len(favoriteList):
            self['list'].moveToIndex(favoriteListIndex)
        self['list'].show()

    def getGenreList(self, genre = _('all'), id = 0):
        self['headertext'].setText('')
        self['statustext'].setText(_('Getting SHOUTcast genre list for %s') % genre)
        self['list'].hide()
        if len(devid) > 8:
            url = self.SC + '/genre/secondary?parentid=%s&k=%s&f=xml' % (id, devid)
        else:
            url = 'http://207.200.98.1/sbin/newxml.phtml'
        print '[SHOUTcast] getGenreList %s' % url
        sendUrlCommand(url, None, 10).addCallback(self.callbackGenreList).addErrback(self.callbackGenreListError)
        return

    def callbackGenreList(self, xmlstring):
        self['headertext'].setText(_('SHOUTcast genre list'))
        self.genreListIndex = 0
        self.mode = self.GENRELIST
        self.genreList = self.fillGenreList(xmlstring)
        self['statustext'].setText('')
        if not len(self.genreList):
            self['statustext'].setText(_('Got 0 genres. Could be a network problem.\nPlease try again...'))
        else:
            self.showGenreList()

    def callbackGenreListError(self, error = None):
        if error is not None:
            try:
                self['list'].hide()
                self['statustext'].setText(_('%s\nPress green-button to try again...') % str(error.getErrorMessage()))
            except:
                pass

        return

    def fillGenreList(self, xmlstring):
        genreList = []
        # print "[SHOUTcast] fillGenreList\n%s" % xmlstring
        try:
            root = xml.etree.cElementTree.fromstring(xmlstring)
        except:
            return []

        data = root.find('data')
        if data == None:
            print '[SHOUTcast] could not find data tag, assume flat listing\n'
            return [ SHOUTcastGenre(name=childs.get('name')) for childs in root.findall('genre') ]
        else:
            for glist in data.findall('genrelist'):
                for childs in glist.findall('genre'):
                    gn = childs.get('name')
                    gid = childs.get('id')
                    gparentid = childs.get('parentid')
                    ghaschilds = childs.get('haschildren')
                    genreList.append(SHOUTcastGenre(name=gn, id=gid, parentid=gparentid, haschilds=ghaschilds))
                    if ghaschilds == 'true':
                        for childlist in childs.findall('genrelist'):
                            for genre in childlist.findall('genre'):
                                gn = genre.get('name')
                                gid = genre.get('id')
                                gparentid = genre.get('parentid')
                                ghaschilds = genre.get('haschildren')
                                genreList.append(SHOUTcastGenre(name=gn, id=gid, parentid=gparentid, haschilds=ghaschilds))

            return genreList

    def showGenreList(self):
        self['headertext'].setText(_('SHOUTcast genre list'))
        self['statustext'].setText(_('Select a genre, then press OK to proceed.'))
        self['list'].setMode(self.mode)
        self['list'].setList([ (x,) for x in self.genreList ])
        self['list'].moveToIndex(self.genreListIndex)
        self['list'].show()

    def onSelectionChanged(self):
        pass

    def ok_pressed(self):
        print '[gender]   press OK'
        if self.visible:
            sel = None
            try:
                sel = self['list'].l.getCurrentSelection()[0]
            except:
                return

            if sel is None:
                return
            if self.mode == self.GENRELIST:
                print '[gender]   GENRELIST'
                self.genreListIndex = self['list'].getCurrentIndex()
                self.getStationList(sel.name)
            elif self.mode == self.STATIONLIST:
                print '[gender]   STATIONLIST %s' % sel.ct
                self.stationListIndex = self['list'].getCurrentIndex()
                self.stopPlaying()
                if sel.ct == None or 'http' not in sel.ct:
                    if len(devid) > 8:
                        url = self.SCY + '/sbin/tunein-station.pls?id=%s' % sel.id
                    self['list'].hide()
                    self['statustext'].setText(_('Getting streaming data from\n%s') % sel.name)
                    self.currentStreamingStation = sel.name
                    sendUrlCommand(url, None, 10).addCallback(self.callbackPLS).addErrback(self.callbackStationListError)
                elif sel.ct.startswith('http'):
                    self['headertext'].setText(self.headerTextString)
                    self.currentStreamingStation = sel.name
                    self.playServiceStream(sel.ct)
                    self['statustext'].setText ('\c00289496' + (_('Stations selected:  ') + ('\c00??;?00%s') % self.currentStreamingStation))
            elif self.mode == self.FAVORITELIST:
                self.favoriteListIndex = self['list'].getCurrentIndex()
                if sel.configItem.type.value == 'url':
                    self.stopPlaying()
                    self['headertext'].setText(self.headerTextString)
                    self.currentStreamingStation = sel.configItem.name.value
                    self.playServiceStream(sel.configItem.text.value)
                    self['statustext'].setText ('\c00289496' + (_('Stations selected:  ') + ('\c00??;?00%s') % self.currentStreamingStation))
                elif sel.configItem.type.value == 'pls':
                    self.stopPlaying()
                    url = sel.configItem.text.value
                    self['list'].hide()
                    self['statustext'].setText(_('Getting streaming data from\n%s') % sel.configItem.name.value)
                    self.currentStreamingStation = sel.configItem.name.value
                    sendUrlCommand(url, None, 10).addCallback(self.callbackPLS).addErrback(self.callbackStationListError)
                elif sel.configItem.type.value == 'genre':
                    self.getStationList(sel.configItem.name.value)
            elif self.mode == self.SEARCHLIST and self.searchSHOUTcastString != '':
                self.searchSHOUTcast(self.searchSHOUTcastString)
        else:
            self.showWindow()

    def stopPlaying(self):
        self.currentStreamingURL = ''
        self.currentStreamingStation = ''
        self['headertext'].setText('')
        self['titel'].setText('')
        self['station'].setText('')
        self.session.summary.setText('')
        if config.plugins.shoutcast.showcover.value:
            self['cover'].doHide()
            self.session.summary.hideSongPic()
        self.session.nav.stopService()

    def callbackPLS(self, result):
        self['headertext'].setText(self.headerTextString)
        found = False
        parts = string.split(result, '\n')
        for lines in parts:
            if lines.find('File1=') != -1:
                line = string.split(lines, 'File1=')
                found = True
                
                self.playServiceStream(line[-1].rstrip().strip())
                self['statustext'].setText ('\c00289496' + (_('Stations selected:  ') + ('\c00??;?00%s') % self.currentStreamingStation))
        if found:
            #####self['statustext'].setText('')
            self['list'].show()
        else:
            self.currentStreamingStation = ''
            self['statustext'].setText(_('No streaming data found...'))
            self['list'].show()

    def getStationList(self, genre):
        print '[gender] getStationList'
        self.stationListHeader = _('genre: ( %s )') % genre
        self.headerTextString = _('SHOUTcast station list for %s') % self.stationListHeader
        self['headertext'].setText('')
        self['statustext'].setText(_('Getting  -  %s') % self.headerTextString)
        self['list'].hide()
        if len(devid) > 8:
            self.stationListURL = self.SC + '/station/advancedsearch&f=xml&k=%s&search=%s' % (devid, genre)
        else:
            self.stationListURL = 'http://207.200.98.1/sbin/newxml.phtml?genre=%s' % genre
        self.stationListIndex = 0
        sendUrlCommand(self.stationListURL, None, 10).addCallback(self.callbackStationList).addErrback(self.callbackStationListError)
       
    def callbackStationList(self, xmlstring):
        self.searchSHOUTcastString = ''
        self.stationListXML = xmlstring
        self['headertext'].setText(self.headerTextString)
        self.mode = self.STATIONLIST
        self['list'].setMode(self.mode)
        self.stationList = self.fillStationList(xmlstring)
        self['statustext'].setText('')
        self['list'].setList([ (x,) for x in self.stationList ])
        if len(self.stationList):
            self['list'].moveToIndex(self.stationListIndex)
        self['list'].show()
        if self.reloadStationListTimerVar != 0:
           self.reloadStationListTimer.start(60000)

    def fillStationList(self, xmlstring):
        print '[SHOUTcast] fillStationList'
        stationList = []
        try:
            root = xml.etree.cElementTree.fromstring(xmlstring)
        except:
            return []

        config_bitrate = int(config.plugins.shoutcast.streamingrate.value)
        data = root.find('data')
        if data != None:
            for slist in data.findall('stationlist'):
                for childs in slist.findall('tunein'):
                    self.tunein = childs.get('base')

                for childs in slist.findall('station'):
                    try:
                        bitrate = int(childs.get('br'))
                    except:
                        bitrate = 0

                    if bitrate >= config_bitrate:
                        stationList.append(SHOUTcastStation(name=childs.get('name'), mt=childs.get('mt'), id=childs.get('id'), br=childs.get('br'), genre=childs.get('genre'), ct=childs.get('ct'), lc=childs.get('lc'), ml=childs.get('ml'), nsc=childs.get('nsc'), cst=childs.get('cst')))

        data = root.find('station')
        if data != None:
            for childs in root.findall('station'):
                print '[gender] id %s' % childs.get('id')
                print '[gender] url %s' % childs.get('url')
                if not childs.get('url').endswith('.pls') and not childs.get('url').endswith('.m3u') and not childs.get('url').endswith('winamp'):
                    stationList.append(SHOUTcastStation(name=str(childs.get('name')), mt=childs.get('codec'), id=childs.get('id'), br=childs.get('bitrate'), genre=childs.get('genre'), ct=childs.get('url'), lc=childs.get('lc'), ml=childs.get('ml'), nsc=childs.get('nsc'), cst=childs.get('cst')))

        return stationList

    def menu_pressed(self):
        if not self.visible:
            self.showWindow()
        options = [(_('Config'), self.config), (_('Search'), self.search)]
        if self.mode == self.FAVORITELIST and self.getSelectedItem() is not None:
            options.extend(((_('rename current selected favorite'), self.renameFavorite),))
            options.extend(((_('remove current selected favorite'), self.removeFavorite),))
        elif self.mode == self.GENRELIST and self.getSelectedItem() is not None:
            options.extend(((_('Add current selected genre to favorite'), self.addGenreToFavorite),))
        elif self.mode == self.STATIONLIST and self.getSelectedItem() is not None:
            options.extend(((_('Add current selected station to favorite'), self.addStationToFavorite),))
        if len(self.currentStreamingURL) != 0:
            options.extend(((_('Add current playing stream to favorite'), self.addCurrentStreamToFavorite),))
        options.extend(((_('Hide'), self.hideWindow),))
        if self.pipZapAvailable is not None and SystemInfo.get('NumVideoDecoders', 1) > 1:
            options.extend(((_('Menu PiP'), self.activatePiP),))
        self.session.openWithCallback(self.menuCallback, ChoiceBox, title=_('Choose action:'), list=options)

    def menuCallback(self, ret):
        ret and ret[1]()

    def hideWindow(self):
        self.visible = False
        self.hide()

    def showWindow(self):
        self.visible = True
        self.show()

    def addGenreToFavorite(self):
        sel = self.getSelectedItem()
        if sel is not None:
            self.addFavorite(name=sel.name, text=sel.name, favoritetype='genre', audio=sel.mt, bitrate=sel.br)

    def addStationToFavorite(self):
        sel = self.getSelectedItem()
        if sel is not None:
            self.addFavorite(name=sel.name, text=self.SCY + '/sbin/tunein-station.pls?id=%s' % sel.id, favoritetype='pls', audio=sel.mt, bitrate=sel.br)

    def addCurrentStreamToFavorite(self):
        self.addFavorite(name=self.currentStreamingStation, text=self.currentStreamingURL, favoritetype='url')

    def addFavorite(self, name = '', text = '', favoritetype = '', audio = '', bitrate = ''):
        self.favoriteConfig.entriescount.value = self.favoriteConfig.entriescount.value + 1
        self.favoriteConfig.entriescount.save()
        newFavorite = self.initFavouriteEntryConfig()
        newFavorite.name.value = name
        newFavorite.text.value = text
        newFavorite.type.value = favoritetype
        newFavorite.audio.value = audio
        newFavorite.bitrate.value = bitrate
        newFavorite.save()
        self.favoriteConfig.saveToFile(self.FAVORITE_FILE)

    def renameFavorite(self):
        sel = self.getSelectedItem()
        if sel is not None:
            self.session.openWithCallback(self.renameFavoriteFinished, VirtualKeyBoard, title=_('Enter new name for favorite item'), text=sel.configItem.name.value)

    def renameFavoriteFinished(self, text = None):
        if text:
            sel = self.getSelectedItem()
            sel.configItem.name.value = text
            sel.configItem.save()
            self.favoriteConfig.saveToFile(self.FAVORITE_FILE)
            self.favoriteListIndex = 0
            self.getFavoriteList()

    def removeFavorite(self):
        sel = self.getSelectedItem()
        if sel is not None:
            self.favoriteConfig.entriescount.value = self.favoriteConfig.entriescount.value - 1
            self.favoriteConfig.entriescount.save()
            self.favoriteConfig.Entries.remove(sel.configItem)
            self.favoriteConfig.Entries.save()
            self.favoriteConfig.saveToFile(self.FAVORITE_FILE)
            self.favoriteListIndex = 0
            self.getFavoriteList()

    def search(self):
        self.session.openWithCallback(self.searchSHOUTcast, VirtualKeyBoard, title=_('Enter text to search for'))

    def searchSHOUTcast(self, searchstring = None):
        if searchstring:
            self.stopReloadStationListTimer()
            self.stationListHeader = _('search-criteria %s') % searchstring
            self.headerTextString = _('SHOUTcast station list for %s') % self.stationListHeader
            self['headertext'].setText('')
            self['statustext'].setText(_('Searching SHOUTcast for %s...') % searchstring)
            self['list'].hide()
            if len(devid) > 8:
                self.stationListURL = self.SC + '/station/advancedsearch&f=xml&k=%s&search=%s' % (devid, searchstring)
            else:
                self.stationListURL = 'http://207.200.98.1/sbin/newxml.phtml?search=%s' % searchstring
            self.mode = self.SEARCHLIST
            self.searchSHOUTcastString = searchstring
            self.stationListIndex = 0
            sendUrlCommand(self.stationListURL, None, 10).addCallback(self.callbackStationList).addErrback(self.callbackStationListError)

    def config(self):
        self.stopReloadStationListTimer()
        self.session.openWithCallback(self.setupFinished, SHOUTcastSetup)

    def setupFinished(self, result):
        if result:
            if config.plugins.shoutcast.showcover.value:
                self['cover'].doShow()
                self.session.summary.showSongPic()
            else:
                self['cover'].doHide()
                self.session.summary.hideSongPic()
            if self.mode == self.STATIONLIST:
                self.reloadStationListTimerVar = int(config.plugins.shoutcast.reloadstationlist.value)
                self.stationListIndex = 0
                self.callbackStationList(self.stationListXML)

    def callbackStationListError(self, error = None):
        if error is not None:
            try:
                self['list'].hide()
                self['statustext'].setText(_('%s\nPress OK to try again...') % str(error.getErrorMessage()))
            except:
                pass

    def Error(self, error = None):
        if error is not None:
            try:
                self['list'].hide()
                self['statustext'].setText(str(error.getErrorMessage()))
            except:
                pass

        if self.nextGoogle:
            self.currentGoogle = self.nextGoogle
            self.nextGoogle = None
            sendUrlCommand(self.currentGoogle, None, 10).addCallback(self.GoogleImageCallback).addErrback(self.Error)
        else:
            self.currentGoogle = None

    def __onClose(self):
        global coverfiles
        for f in coverfiles:
            try:
                os.unlink(f)
            except:
                pass

        self.stopReloadStationListTimer()
        self.session.nav.playService(self.CurrentService)
        self.session.nav.event.remove(self.__event)
        self.currPlay = None
        containerStreamripper.dataAvail.remove(self.streamripperDataAvail)
        containerStreamripper.appClosed.remove(self.streamripperClosed)

    def GoogleImageCallback(self, result):
        global coverfiles
        bad_link = ['https://www.allmusic.com',
         'http://www.jaren80muziek.nl',
         'http://www.inthestudio.net',
         'http://www.israel-music.com',
         'https://www.discogs.com',
         'https://i1.sndcdn.com',
         'http://www.lyrics007.com',
         'https://lametralleta.es',
         'http://www.caramail.tv',
         'http://cloud.freehandmusic.netdna-cdn.com',
         'http://rockyourlyrics.com',
         'http://www.franceinter.fr',
         'http://audio-max.home.pl',
         'https://www.mystic.pl',
         'http://radiobox2.omroep.nl',
         'http://s0.hulkshare.com',
         'http://static2.ising.pl',
         'http://www.disco-polo.info',
         'http://merlin.pl',
         'http://www.muzikbuldum.com',
         'http://img2.zcdn.com.au',
         'http://www.duoviva.com',
         'http://thumbnail.mixcloud.com',
         'http://www.modern-talking.net',
         'http://galleryplus.ebayimg.com',
         'http://www.radiotrip.it',
         'https://dlmetal.org',
         'http://i.iplsc.com',
         'http://www.copertinedvd.org',
         'http://flacmusic.org',
         'https://imgcdn.ok.de',
         'http://www.mediaboom.org',
         'http://democracy.allerdale.gov.uk',
         'http://lahoradelrelax.com',
         'http://www.isvent.com',
         'http://www.wallpaperfo.com',
         'http://www.analyticdatasolutions.net',
         'http://caratulascd.com',
         'http://img.youtube.com',
         'http://satpic.ru',
         'http://imagizer.imageshack.us',
         'https://img.discogs.com',
         'https://upload.wikimedia.org']
        nr = 0
        url = 'http://memytutaj.pl/uploads/2015/07/27/55b66ab973ad1.jpg'
        if self.nextGoogle:
            self.currentGoogle = self.nextGoogle
            self.nextGoogle = None
            sendUrlCommand(self.currentGoogle, None, 10).addCallback(self.GoogleImageCallback).addErrback(self.Error)
            return
        else:
            self.currentGoogle = None
            with open('/tmp/datafull', 'w') as titleFile:
                titleFile.write(result)
            if config.plugins.shoutcast.where.value == '0':
                r = re.findall('murl&quot;:&quot;(http.*?)&quot', result, re.S | re.I)
            else:
                r = re.findall('"ou":"(http.*?)"', result, re.S | re.I)
            if r:
                url = r[nr]
                print '[SHOUTcast] pierwszy:%s' % url
                for link in bad_link:
                    if url.startswith(link):
                        nr += 1
                        url = r[nr]
                        print '[SHOUTcast] drugi:%s' % url
                        for link in bad_link:
                            if url.startswith(link):
                                nr += 1
                                url = r[nr]
                                print '[SHOUTcast] trzeci:%s' % url
                                for link in bad_link:
                                    if url.startswith(link):
                                        nr += 1
                                        url = r[nr]
                                        print '[SHOUTcast] czwarty:%s' % url

                if len(url) > 15:
                    url = url.replace(' ', '%20')
                    print 'download url: %s ' % url
                    validurl = True
                else:
                    validurl = False
                    print '[SHOUTcast] invalid cover url or pictureformat!'
                    if config.plugins.shoutcast.showcover.value:
                        self['cover'].doHide()
                        self.session.summary.hideSongPic()
                if validurl:
                    self.currentcoverfile = (self.currentcoverfile + 1) % len(coverfiles)
                    try:
                        os.unlink(coverfiles[self.currentcoverfile - 1])
                    except:
                        pass

                    coverfile = coverfiles[self.currentcoverfile]
                    print '[SHOUTcast] downloading cover from %s to %s numer%s' % (url, coverfile, str(nr))
                    downloadPage(url, coverfile).addCallback(self.coverDownloadFinished, coverfile).addErrback(self.coverDownloadFailed)

    def coverDownloadFailed(self, result):
        print '[SHOUTcast] cover download failed:', result
        if config.plugins.shoutcast.showcover.value:
            self['statustext'].setText(_('Error downloading cover...'))
            self['cover'].doHide()
            self.session.summary.hideSongPic()

    def coverDownloadFinished(self, result, coverfile):
        if config.plugins.shoutcast.showcover.value:
            print '[SHOUTcast] cover download finished:', coverfile
            self['statustext'].setText('')
            self['cover'].updateIcon(coverfile)
            self['cover'].doShow()
            self.session.summary.showSongPic(coverfile)

    def __event(self, ev):
        if ev != 17 and ev != 18:
            print '[SHOUTcast] EVENT ==>', ev
        if ev == 1 or ev == 4:
            print '[SHOUTcast] Tuned in, playing now!'
        if ev == 3 or ev == 7:
            self['statustext'].setText(_('Stream stopped playing, playback of stream stopped!'))
            print '[SHOUTcast] Stream stopped playing, playback of stream stopped!'
            self.session.nav.stopService()
        if ev == 5:
            if not self.currPlay:
                return
            sTitle = self.currPlay.info().getInfoString(iServiceInformation.sTagTitle)
            if self.oldtitle != sTitle:
                self.oldtitle = sTitle
                sTitle = sTitle.replace('Title:', '')[:]
                sTitle = re.sub(' w .+', '', sTitle)
                sTitle = re.sub('00:0.+', '', sTitle)
                if len(sTitle) < 4:
                    sTitle = ''
                if config.plugins.shoutcast.showcover.value:
                    searchpara = sTitle
                    if sTitle:
                        if config.plugins.shoutcast.where.value == '0':
                            url = 'http://www.bing.com/images/search?q=%s&FORM=HDRSC2' % quote(searchpara)
                        else:
                            url = 'http://www.google.pl/search?hl=pl&site=imghp&tbm=isch&source=hp&biw=1152&bih=733&q=%s' % quote(sTitle)
                    else:
                        url = 'http://www.bing.com/images/search?q=%s&FORM=HDRSC2' % quote('shoutcast logo')
                    print '[SHOUTcast] coverurl = %s ' % url
                    if self.currentGoogle:
                        self.nextGoogle = url
                    else:
                        self.currentGoogle = url
                        sendUrlCommand(url, None, 10).addCallback(self.GoogleImageCallback).addErrback(self.Error)
                if len(sTitle) == 0:
                    sTitle = _('n/a')
                title = ('\c00289496'+_('Title: ') + ('\c00?25=01''%s') % sTitle)
                print '[SHOUTcast] Title: %s ' % title
                self['titel'].setText(title)
                self.session.summary.setText(title)
                self.session.summary.setSongName(sTitle)
            else:
                print '[SHOUTcast] Ignoring useless updated info provided by streamengine!'
        return

    def playServiceStream(self, url):
        self.currPlay = None
        print '[SHOUTcast] play %s' % url
        self.session.nav.stopService()
        if config.plugins.shoutcast.showcover.value:
            self['cover'].doHide()
            self.session.summary.hideSongPic()
        sref = eServiceReference('4097:0:0:0:0:0:0:0:0:0:%s' % url.replace(':', '%3a'))
        try:
            self.session.nav.playService(sref, adjust=False)
        except:
            print '[SHOUTcast] Could not play %s' % sref

        try:
            self.session.nav.playService(sref)
        except:
            print '[SHOUTcast] Could not play %s' % sref
          
        self.currPlay = self.session.nav.getCurrentService()
        self.currentStreamingURL = url
        self['titel'].setText(_('Title: n/a'))
        self['station'].setText('\\c00289496' + _('Station: ') + '\\c00??;?00%s' % self.currentStreamingStation)
        self.session.summary.setRadioName(self.currentStreamingStation)

    def createSummary(self):
        return SHOUTcastLCDScreen

    def initFavouriteEntryConfig(self):
        self.favoriteConfig.Entries.append(ConfigSubsection())
        i = len(self.favoriteConfig.Entries) - 1
        self.favoriteConfig.Entries[i].name = ConfigText(default='')
        self.favoriteConfig.Entries[i].text = ConfigText(default='')
        self.favoriteConfig.Entries[i].type = ConfigText(default='')
        self.favoriteConfig.Entries[i].audio = ConfigText(default='')
        self.favoriteConfig.Entries[i].bitrate = ConfigText(default='')
        return self.favoriteConfig.Entries[i]

    def initFavouriteConfig(self):
        count = self.favoriteConfig.entriescount.value
        if count != 0:
            i = 0
            while i < count:
                self.initFavouriteEntryConfig()
                i += 1

    def getSelectedItem(self):
        sel = None
        try:
            sel = self['list'].l.getCurrentSelection()[0]
        except:
            return

        return sel


class Cover(Pixmap):
    visible = 0

    def __init__(self):
        Pixmap.__init__(self)
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.paintIconPixmapCB)
        self.decoding = None
        self.decodeNext = None
        return

    def doShow(self):
        if not self.visible:
            self.visible = True
            print '[SHOUTcast] cover visible %s self.show' % self.visible
            self.show()

    def doHide(self):
        if self.visible:
            self.visible = False
            print '[SHOUTcast] cover visible %s self.hide' % self.visible
            self.hide()

    def onShow(self):
        Pixmap.onShow(self)
        coverwidth = self.instance.size().width()
        coverheight = self.instance.size().height()
        self.picload.setPara((coverwidth,
         coverheight,
         1,
         1,
         False,
         1,
         '#00000000'))

    def paintIconPixmapCB(self, picInfo = None):
        ptr = self.picload.getData()
        if ptr != None:
            self.instance.setPixmap(ptr.__deref__())
            if self.visible:
                self.doShow()
        if self.decodeNext is not None:
            self.decoding = self.decodeNext
            self.decodeNext = None
            if self.picload.startDecode(self.decoding) != 0:
                print '[Shoutcast] Failed to start decoding next image'
                self.decoding = None
        else:
            self.decoding = None
        return

    def updateIcon(self, filename):
        if self.decoding is not None:
            self.decodeNext = filename
        elif self.picload.startDecode(filename) == 0:
            self.decoding = filename
        else:
            print '[Shoutcast] Failed to start decoding image'
            self.decoding = None
        return


class SHOUTcastList(GUIComponent, object):

    def buildEntry(self, item):
        width = self.l.getItemSize().width()
        res = [None]
        if self.mode == 0:
            print '[SHOUTcast] list name=%s haschilds=%s opened=%s\n' % (item.name, item.haschilds, item.opened)
            if item.parentid == '0':
                if item.haschilds == 'true':
                    if item.opened == 'true':
                        iname = '- %s' % item.name
                    else:
                        iname = '+ %s' % item.name
                else:
                    iname = item.name
            else:
                iname = '     %s' % item.name
            res.append((eListboxPythonMultiContent.TYPE_TEXT,
             0,
             0,
             width,
             self.pard,
             0,
             RT_HALIGN_LEFT | RT_VALIGN_CENTER,
             iname))
        elif self.mode == 1:
            res.append((eListboxPythonMultiContent.TYPE_TEXT,
             0,
             3,
             width,
             self.para,
             1,
             RT_HALIGN_LEFT | RT_VALIGN_CENTER,
             item.name))
            res.append((eListboxPythonMultiContent.TYPE_TEXT,
             0,
             self.parb,
             width,
             self.para,
             1,
             RT_HALIGN_LEFT | RT_VALIGN_CENTER,
             item.ct))
            res.append((eListboxPythonMultiContent.TYPE_TEXT,
             0,
             self.parc,
             width / 2,
             self.para,
             1,
             RT_HALIGN_LEFT | RT_VALIGN_CENTER,
             _('Audio: %s') % item.mt))
            res.append((eListboxPythonMultiContent.TYPE_TEXT,
             width / 2,
             self.parc,
             width / 2,
             self.para,
             1,
             RT_HALIGN_RIGHT | RT_VALIGN_CENTER,
             _('Bit rate: %s kbps') % item.br))
        elif self.mode == 2:
            res.append((eListboxPythonMultiContent.TYPE_TEXT,
             0,
             3,
             width,
             self.para,
             1,
             RT_HALIGN_LEFT | RT_VALIGN_CENTER,
             item.configItem.name.value))
            res.append((eListboxPythonMultiContent.TYPE_TEXT,
             0,
             self.parb,
             width,
             self.para,
             1,
             RT_HALIGN_LEFT | RT_VALIGN_CENTER,
             '%s (%s)' % (item.configItem.text.value, item.configItem.type.value)))
            if len(item.configItem.audio.value) != 0:
                res.append((eListboxPythonMultiContent.TYPE_TEXT,
                 0,
                 self.parc,
                 width / 2,
                 self.para,
                 1,
                 RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                 _('Audio: %s') % item.configItem.audio.value))
            if len(item.configItem.bitrate.value) != 0:
                res.append((eListboxPythonMultiContent.TYPE_TEXT,
                 width / 2,
                 self.parc,
                 width / 2,
                 self.para,
                 1,
                 RT_HALIGN_RIGHT | RT_VALIGN_CENTER,
                 _('Bit rate: %s kbps') % item.configItem.bitrate.value))
        return res

    def __init__(self):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.fontsize0, self.fontsize1, self.cenrylist, self.favlist, self.para, self.parb, self.parc, self.pard = skin.parameters.get('SHOUTcastListItem', (20, 18, 22, 69, 20, 23, 43, 22))
        self.onSelectionChanged = []
        self.mode = 0

    def setMode(self, mode):
        self.mode = mode
        if mode == 0:
            self.l.setItemHeight(self.cenrylist)
        elif mode == 1 or mode == 2:
            self.l.setItemHeight(self.favlist)

    def connectSelChanged(self, fnc):
        if fnc not in self.onSelectionChanged:
            self.onSelectionChanged.append(fnc)

    def disconnectSelChanged(self, fnc):
        if fnc in self.onSelectionChanged:
            self.onSelectionChanged.remove(fnc)

    def selectionChanged(self):
        for x in self.onSelectionChanged:
            x()

    def getCurrent(self):
        cur = self.l.getCurrentSelection()
        return cur and cur[0]

    GUI_WIDGET = eListbox

    def postWidgetCreate(self, instance):
        instance.setContent(self.l)
        instance.setWrapAround(True)
        instance.selectionChanged.get().append(self.selectionChanged)

    def preWidgetRemove(self, instance):
        instance.setContent(None)
        instance.selectionChanged.get().remove(self.selectionChanged)

    def moveToIndex(self, index):
        self.instance.moveSelectionTo(index)

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    currentIndex = property(getCurrentIndex, moveToIndex)
    currentSelection = property(getCurrent)

    def setList(self, list):
        self.l.setList(list)

    def applySkin(self, desktop, parent):
        font = 'Regular'
        for attrib, value in list(self.skinAttributes):
            if attrib == 'font':
                font = value.split(';')[0]
                self.skinAttributes.remove((attrib, value))
                break

        self.l.setFont(0, gFont(font, self.fontsize0))
        self.l.setFont(1, gFont(font, self.fontsize1))
        self.l.setBuildFunc(self.buildEntry)
        self.l.setItemHeight(self.cenrylist)
        return GUIComponent.applySkin(self, desktop, parent)


class SHOUTcastLCDScreen(Screen):
    try:
        ssw = getDesktop(1).size().width()
        ssh = getDesktop(1).size().height()
    except Exception:
        ssw = 132
        ssh = 64
    if ssw >= 220 and ssh >= 176:
        hasLCD = True
    else:
        hasLCD = False
        
    if ssw >= 800 and ssh >= 480:
        skin = """
    <screen position="0,0" size="800,480" title=" ">
        <widget name="text1" position="10,0"  size="800,110" font="Regular;50" halign="center" valign="center" backgroundColor="#20000000" foregroundColor="#0174DF" transparent="1"/>
        <widget source="text2" render="Label" position="10,110" size="800,90" font="Regular;40" halign="center" valign="center" backgroundColor="#20000000" foregroundColor="#FFBF00" transparent="1"/>
        <widget name="songPic" position="0,0" zPosition="4" size="800,480" alphatest="blend" />
    </screen>"""
    elif ssw >= 480 and ssh >= 320:
        skin = """
    <screen position="0,0" size="480,320" title=" ">
        <widget name="text1" position="10,10" zPosition="2" size="460,90" font="Regular;40" halign="center" valign="top" foregroundColor="#0174DF" transparent="1"/>
        <widget source="text2" render="Label" position="10,230" zPosition="2" size="460,80" font="Regular;35" halign="center" valign="bottom" foregroundColor="#FFBF00" transparent="1"/>
        <widget name="songPic" position="0,0" zPosition="1" size="480,320" alphatest="blend" />
    </screen>"""
    elif ssw >= 220 and ssh >= 176:
        skin = """
    <screen position="0,0" size="220,176" title=" ">
        <widget name="text1" position="5,0" size="210,50" font="Regular;24" halign="center" valign="center" backgroundColor="#20000000" foregroundColor="#0174DF" transparent="1"/>
        <widget source="text2" render="Label" position="5,80" size="210,50" font="Regular;22" halign="center" valign="center" backgroundColor="#20000000" foregroundColor="#FFBF00" transparent="1"/>
        <widget name="songPic" position="0,0" size="220,176" zPosition="4" alphatest="blend" />
    </screen>"""
    else:
        skin = """
    <screen position="0,0" size="132,64" title="SHOUTcast">
        <widget name="text1" position="4,0" size="132,14" font="Regular;12" halign="center" valign="center"/>
        <widget source="text2" render="Label" position="4,14" size="132,49" font="Regular;10" halign="center" valign="center"/>
    </screen>"""

    def __init__(self, session, parent):
        Screen.__init__(self, session)
        self['text1'] = Label('SHOUTcast')
        self['text2'] = StaticText()
        if self.hasLCD:
            try: self['songPic'] = Cover()
            except Exception: pass

    def setText(self, text):
        if not self.hasLCD:
            self['text2'].setText(text[28:])
            with open('/tmp/shoutcast.title', 'w') as titleFile:
                titleFile.write(text[28:])

    def setSongName(self, text):
        if self.hasLCD:
            self["text2"].setText(text)
            
    def setRadioName(self, text):
        if self.hasLCD:
            self["text1"].setText(text)
            
    def showSongPic(self, picPath = ''):
        if self.hasLCD:
            try:
                if picPath != '' and fileExists(picPath):
                    self["songPic"].updateIcon(picPath)
                self["songPic"].doShow()
            except Exception: pass

    def hideSongPic(self):
        if self.hasLCD:
            try: self["songPic"].doHide()
            except Exception: pass 


class SHOUTcastSetup(Screen, ConfigListScreen):
    skin = """
        <screen position="center,center" size="600,400" title="SHOUTcast Setup" >
            <ePixmap pixmap="skin_default/buttons/red.png" position="10,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/green.png" position="155,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="300,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/blue.png" position="445,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
            <widget render="Label" source="key_red" position="10,0" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <widget render="Label" source="key_green" position="150,0" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <widget name="config" position="10,50" size="580,400" scrollbarMode="showOnDemand" />
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skinName = [self.skinName, 'Setup']
        self.setTitle(_('SHOUTcast setup'))
        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('OK'))
        self['description'] = Label(_('Station List number: ( 1 - Poland ) ( 2 - Trance ) ( 3 - Dance ) ( 4 - Techno ) ( 5 - 90s ) ( 6 - Random stations ) ( 7 - All Stations )'))
        self.list = [getConfigListEntry(_('Show cover:'), config.plugins.shoutcast.showcover),
         getConfigListEntry(_('Cover from:'), config.plugins.shoutcast.where),
         getConfigListEntry(_('Cover Position H:'), config.plugins.shoutcast.pos_cover_width),
         getConfigListEntry(_('Cover Position V:'), config.plugins.shoutcast.pos_cover_height),
         getConfigListEntry(_('Cover Size H:'), config.plugins.shoutcast.size_cover_width),
         getConfigListEntry(_('Cover Size V:'), config.plugins.shoutcast.size_cover_height),
         getConfigListEntry(_('Streaming rate:'), config.plugins.shoutcast.streamingrate),
         getConfigListEntry(_('Reload station list:'), config.plugins.shoutcast.reloadstationlist),
         getConfigListEntry(_('Rip to single file, name is timestamped:'), config.plugins.shoutcast.riptosinglefile),
         getConfigListEntry(_('Create a directory for each stream:'), config.plugins.shoutcast.createdirforeachstream),
         getConfigListEntry(_('Add sequence number to output file:'), config.plugins.shoutcast.addsequenceoutputfile),
         getConfigListEntry(_('Show in extension menu:'), config.plugins.shoutcast.showinextensions),
         getConfigListEntry(_('Station List number:'), config.plugins.shoutcast.lista)]
        self.dirname = getConfigListEntry(_('Recording location:'), config.plugins.shoutcast.dirname)
        self.list.append(self.dirname)
        ConfigListScreen.__init__(self, self.list, session)
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions'], {'green': self.keySave,
         'cancel': self.keyClose,
         'ok': self.keySelect}, -2)

    def keySelect(self):
        cur = self['config'].getCurrent()
        if cur == self.dirname:
            self.session.openWithCallback(self.pathSelected, SHOUTcastStreamripperRecordingPath, config.plugins.shoutcast.dirname.value)

    def pathSelected(self, res):
        if res is not None:
            config.plugins.shoutcast.dirname.value = res
        return

    def keySave(self):
        if config.plugins.shoutcast.dirname.value == '':
            config.plugins.shoutcast.dirname.value = '/media/hdd/streamripper/'
        for x in self['config'].list:
            x[1].save()

        configfile.save()
        self.close(True)

    def keyClose(self):
        for x in self['config'].list:
            x[1].cancel()

        self.close(False)


class SHOUTcastStreamripperRecordingPath(Screen):
    skin = """
        <screen name="SHOUTcastStreamripperRecordingPath" position="center,center" size="560,320" title="Select record path for streamripper">
            <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
            <widget name="target" position="0,60" size="540,22" valign="center" font="Regular;22" />
            <widget name="filelist" position="0,100" zPosition="1" size="560,220" scrollbarMode="showOnDemand"/>
            <widget render="Label" source="key_red" position="0,0" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <widget render="Label" source="key_green" position="140,0" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
        </screen>"""

    def __init__(self, session, initDir):
        Screen.__init__(self, session)
        self.setTitle(_('Select record path for streamripper'))
        inhibitDirs = ['/bin',
         '/boot',
         '/dev',
         '/etc',
         '/lib',
         '/proc',
         '/sbin',
         '/sys',
         '/usr',
         '/var']
        inhibitMounts = []
        self['filelist'] = FileList(initDir, showDirectories=True, showFiles=False, inhibitMounts=inhibitMounts, inhibitDirs=inhibitDirs)
        self['target'] = Label()
        self['actions'] = ActionMap(['WizardActions',
         'DirectionActions',
         'ColorActions',
         'EPGSelectActions'], {'back': self.cancel,
         'left': self.left,
         'right': self.right,
         'up': self.up,
         'down': self.down,
         'ok': self.ok,
         'green': self.green,
         'red': self.cancel}, -1)
        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('OK'))

    def cancel(self):
        self.close(None)

    def green(self):
        self.close(self['filelist'].getSelection()[0])

    def up(self):
        self['filelist'].up()
        self.updateTarget()

    def down(self):
        self['filelist'].down()
        self.updateTarget()

    def left(self):
        self['filelist'].pageUp()
        self.updateTarget()

    def right(self):
        self['filelist'].pageDown()
        self.updateTarget()

    def ok(self):
        if self['filelist'].canDescent():
            self['filelist'].descent()
            self.updateTarget()

    def updateTarget(self):
        currFolder = self['filelist'].getSelection()[0]
        if currFolder is not None:
            self['target'].setText(currFolder)
        else:
            self['target'].setText(_('Invalid Location'))

    def up(self):
        self['filelist'].up()
        self.updateTarget()

    def down(self):
        self['filelist'].down()
        self.updateTarget()

    def left(self):
        self['filelist'].pageUp()
        self.updateTarget()

    def right(self):
        self['filelist'].pageDown()
        self.updateTarget()

    def ok(self):
        if self['filelist'].canDescent():
            self['filelist'].descent()
            self.updateTarget()

    def updateTarget(self):
        currFolder = self['filelist'].getSelection()[0]
        if currFolder is not None:
            self['target'].setText(currFolder)
        else:
            self['target'].setText(_('Invalid Location'))
