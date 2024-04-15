# -*- coding: utf-8 -*-
#
#  Konfigurator dla iptv 2013
#  autorzy: j00zek, samsamsam
#

###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayerMario.tools.iptvtools import printDBG, printExc, GetSkinsList, GetHostsList, GetEnabledHostsList, \
                                                          IsHostEnabled, IsExecutable, CFakeMoviePlayerOption, GetAvailableIconSize, \
                                                          IsWebInterfaceModuleAvailable, SetIconsHash, SetGraphicsHash, isOPKGinstall, \
                                                          defaultToolPath
from Plugins.Extensions.IPTVPlayerMario.iptvupdate.updatemainwindow import IPTVUpdateWindow, UpdateMainAppImpl
from Plugins.Extensions.IPTVPlayerMario.components.iptvplayerinit import TranslateTXT as _, IPTVPlayerNeedInit
from Plugins.Extensions.IPTVPlayerMario.components.configbase import ConfigBaseWidget, COLORS_DEFINITONS
from Plugins.Extensions.IPTVPlayerMario.components.confighost import ConfigHostsMenu
from Plugins.Extensions.IPTVPlayerMario.components.iptvdirbrowser import IPTVDirectorySelectorWidget
from Plugins.Extensions.IPTVPlayerMario.setup.iptvsetupwidget import IPTVSetupMainWidget
###################################################

###################################################
# FOREIGN import
###################################################
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

from Components.ActionMap import ActionMap, HelpableActionMap
from Components.Label import Label
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigDirectory, ConfigYesNo, ConfigOnOff, Config, ConfigInteger, \
                              ConfigSubList, ConfigText, getConfigListEntry, configfile, ConfigNothing, NoSave
from Components.ConfigList import ConfigListScreen
from Tools.BoundFunction import boundFunction
from Tools.Directories import resolveFilename, fileExists, SCOPE_PLUGINS
###################################################


###################################################
# Config options for HOST
###################################################
config.plugins.IPTVPlayerMario = ConfigSubsection()

config.plugins.IPTVPlayerMario.FakeEntry = NoSave(ConfigNothing())
#show/hide sections
config.plugins.IPTVPlayerMario.basicConfVisible = NoSave(ConfigNothing())
config.plugins.IPTVPlayerMario.prxyConfVisible = NoSave(ConfigNothing())
config.plugins.IPTVPlayerMario.buffConfVisible = NoSave(ConfigNothing())
config.plugins.IPTVPlayerMario.downConfVisible = NoSave(ConfigNothing())
config.plugins.IPTVPlayerMario.captConfVisible = NoSave(ConfigNothing())
config.plugins.IPTVPlayerMario.subtConfVisible = NoSave(ConfigNothing())
config.plugins.IPTVPlayerMario.playConfVisible = NoSave(ConfigNothing())
config.plugins.IPTVPlayerMario.otherConfVisible = NoSave(ConfigNothing())

from Plugins.Extensions.IPTVPlayerMario.components.configextmovieplayer import ConfigExtMoviePlayer

config.plugins.IPTVPlayerMario.plarform = ConfigSelection(default="auto", choices=[("auto", "auto"), ("mipsel", _("mipsel")), ("sh4", _("sh4")), ("i686", _("i686")), ("armv7", _("armv7")), ("armv5t", _("armv5t")), ("unknown", _("unknown"))])
config.plugins.IPTVPlayerMario.plarformfpuabi = ConfigSelection(default="", choices=[("", ""), ("hard_float", _("Hardware floating point")), ("soft_float", _("Software floating point"))])

config.plugins.IPTVPlayerMario.exteplayer3path = ConfigText(default=defaultToolPath("exteplayer3"), fixed_size=False)
config.plugins.IPTVPlayerMario.gstplayerpath = ConfigText(default="", fixed_size=False)
config.plugins.IPTVPlayerMario.wgetpath = ConfigText(default="", fixed_size=False)
config.plugins.IPTVPlayerMario.hlsdlpath = ConfigText(default="", fixed_size=False)
config.plugins.IPTVPlayerMario.cmdwrappath = ConfigText(default="", fixed_size=False)
config.plugins.IPTVPlayerMario.dukpath = ConfigText(default="", fixed_size=False)
config.plugins.IPTVPlayerMario.rtmpdumppath = ConfigText(default="", fixed_size=False)
config.plugins.IPTVPlayerMario.f4mdumppath = ConfigText(default="", fixed_size=False)
config.plugins.IPTVPlayerMario.uchardetpath = ConfigText(default="", fixed_size=False)
config.plugins.IPTVPlayerMario.set_curr_title = ConfigYesNo(default=False)
config.plugins.IPTVPlayerMario.curr_title_file = ConfigText(default="", fixed_size=False)

config.plugins.IPTVPlayerMario.showcover = ConfigYesNo(default=True)
config.plugins.IPTVPlayerMario.deleteIcons = ConfigSelection(default="3", choices=[("0", _("after closing")), ("1", _("after day")), ("3", _("after three days")), ("7", _("after a week"))])
config.plugins.IPTVPlayerMario.allowedcoverformats = ConfigSelection(default="jpeg,png", choices=[("jpeg,png,gif", _("jpeg,png,gif")), ("jpeg,png", _("jpeg,png")), ("jpeg", _("jpeg")), ("all", _("all"))])
config.plugins.IPTVPlayerMario.showinextensions = ConfigYesNo(default=True)
config.plugins.IPTVPlayerMario.hostsListType = ConfigSelection(default="G", choices=[("G", _("Graphic services selector")), ("S", _("Simple list")), ("T", _("Tree list"))])
config.plugins.IPTVPlayerMario.showinMainMenu = ConfigYesNo(default=False)
config.plugins.IPTVPlayerMario.ListaGraficzna = ConfigYesNo(default=True)
config.plugins.IPTVPlayerMario.group_hosts = ConfigYesNo(default=True)
config.plugins.IPTVPlayerMario.NaszaSciezka = ConfigDirectory(default="/hdd/movie/") #, fixed_size = False)
config.plugins.IPTVPlayerMario.bufferingPath = ConfigDirectory(default=config.plugins.IPTVPlayerMario.NaszaSciezka.value) #, fixed_size = False)
config.plugins.IPTVPlayerMario.buforowanie = ConfigYesNo(default=False)
config.plugins.IPTVPlayerMario.buforowanie_m3u8 = ConfigYesNo(default=True)
config.plugins.IPTVPlayerMario.buforowanie_rtmp = ConfigYesNo(default=False)
config.plugins.IPTVPlayerMario.requestedBuffSize = ConfigInteger(2, (1, 120))
config.plugins.IPTVPlayerMario.requestedAudioBuffSize = ConfigInteger(256, (1, 10240))

config.plugins.IPTVPlayerMario.IPTVDMRunAtStart = ConfigYesNo(default=False)
config.plugins.IPTVPlayerMario.IPTVDMShowAfterAdd = ConfigYesNo(default=True)
config.plugins.IPTVPlayerMario.IPTVDMMaxDownloadItem = ConfigSelection(default="1", choices=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4")])

config.plugins.IPTVPlayerMario.AktualizacjaWmenu = ConfigYesNo(default=True)
config.plugins.IPTVPlayerMario.sortuj = ConfigYesNo(default=True)
config.plugins.IPTVPlayerMario.remove_diabled_hosts = ConfigYesNo(default=False)
config.plugins.IPTVPlayerMario.IPTVWebIterface = ConfigYesNo(default=False)
config.plugins.IPTVPlayerMario.plugin_autostart = ConfigYesNo(default=False)
config.plugins.IPTVPlayerMario.plugin_autostart_method = ConfigSelection(default="wizard", choices=[("wizard", "wizard"), ("infobar", "infobar")])

if isOPKGinstall():
    config.plugins.IPTVPlayerMario.preferredupdateserver = ConfigSelection(default="4", choices=[("", _("Default")), ("4", "opkg repo")])
else:
    config.plugins.IPTVPlayerMario.preferredupdateserver = ConfigSelection(default="2", choices=[("", _("Default")), ("1", "http://iptvplayer.vline.pl/"), ("2", _("http://zadmario.gitlab.io/")), ("3", _("private"))])
config.plugins.IPTVPlayerMario.osk_type = ConfigSelection(default="", choices=[("", _("Auto")), ("system", _("System")), ("own", _("Own model"))])
config.plugins.IPTVPlayerMario.osk_layout = ConfigText(default="", fixed_size=False)
config.plugins.IPTVPlayerMario.osk_allow_suggestions = ConfigYesNo(default=True)
config.plugins.IPTVPlayerMario.osk_default_suggestions = ConfigSelection(default="", choices=[("", _("Auto")), ("none", _("None")), ("google", "google.com"), ("filmweb", "filmweb.pl"), ("imdb", "imdb.com"), ("filmstarts", "filmstarts.de")])
config.plugins.IPTVPlayerMario.osk_background_color = ConfigSelection(default="", choices=[('', _('Default')), ('transparent', _('Transparent')), ('#000000', _('Black')), ('#80000000', _('Darkgray')), ('#cc000000', _('Lightgray'))])


def GetMoviePlayerName(player):
    map = {"auto": _("auto"), "mini": _("internal"), "standard": _("standard"), 'exteplayer': _("external eplayer3"), 'extgstplayer': _("external gstplayer")}
    return map.get(player, _('unknown'))


def ConfigPlayer(player):
    return (player, GetMoviePlayerName(player))


config.plugins.IPTVPlayerMario.NaszPlayer = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer('extgstplayer'), ConfigPlayer("standard")])

# without buffering mode
#sh4
config.plugins.IPTVPlayerMario.defaultSH4MoviePlayer0 = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer("standard"), ConfigPlayer('exteplayer'), ConfigPlayer('extgstplayer')])
config.plugins.IPTVPlayerMario.alternativeSH4MoviePlayer0 = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer("standard"), ConfigPlayer('exteplayer'), ConfigPlayer('extgstplayer')])

#mipsel
config.plugins.IPTVPlayerMario.defaultMIPSELMoviePlayer0 = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer("standard"), ConfigPlayer('extgstplayer'), ConfigPlayer('exteplayer')])
config.plugins.IPTVPlayerMario.alternativeMIPSELMoviePlayer0 = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer("standard"), ConfigPlayer('extgstplayer'), ConfigPlayer('exteplayer')])

#i686
config.plugins.IPTVPlayerMario.defaultI686MoviePlayer0 = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer("standard"), ConfigPlayer('extgstplayer')])
config.plugins.IPTVPlayerMario.alternativeI686MoviePlayer0 = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer("standard"), ConfigPlayer('extgstplayer')])
# end without buffering mode players

#armv7
config.plugins.IPTVPlayerMario.defaultARMV7MoviePlayer0 = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer("standard"), ConfigPlayer('extgstplayer'), ConfigPlayer('exteplayer')])
config.plugins.IPTVPlayerMario.alternativeARMV7MoviePlayer0 = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer("standard"), ConfigPlayer('extgstplayer'), ConfigPlayer('exteplayer')])

#armv5t
config.plugins.IPTVPlayerMario.defaultARMV5TMoviePlayer0 = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer("standard"), ConfigPlayer('extgstplayer'), ConfigPlayer('exteplayer')])
config.plugins.IPTVPlayerMario.alternativeARMV5TMoviePlayer0 = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer("standard"), ConfigPlayer('extgstplayer'), ConfigPlayer('exteplayer')])

# with buffering mode
#sh4
config.plugins.IPTVPlayerMario.defaultSH4MoviePlayer = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer("standard"), ConfigPlayer('exteplayer'), ConfigPlayer('extgstplayer')])
config.plugins.IPTVPlayerMario.alternativeSH4MoviePlayer = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer("standard"), ConfigPlayer('exteplayer'), ConfigPlayer('extgstplayer')])

#mipsel
config.plugins.IPTVPlayerMario.defaultMIPSELMoviePlayer = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer("standard"), ConfigPlayer('extgstplayer'), ConfigPlayer('exteplayer')])
config.plugins.IPTVPlayerMario.alternativeMIPSELMoviePlayer = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer("standard"), ConfigPlayer('extgstplayer'), ConfigPlayer('exteplayer')])

#i686
config.plugins.IPTVPlayerMario.defaultI686MoviePlayer = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer("standard"), ConfigPlayer('extgstplayer')])
config.plugins.IPTVPlayerMario.alternativeI686MoviePlayer = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer("standard"), ConfigPlayer('extgstplayer')])

#armv7
config.plugins.IPTVPlayerMario.defaultARMV7MoviePlayer = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer("standard"), ConfigPlayer('extgstplayer'), ConfigPlayer('exteplayer')])
config.plugins.IPTVPlayerMario.alternativeARMV7MoviePlayer = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer("standard"), ConfigPlayer('extgstplayer'), ConfigPlayer('exteplayer')])

#armv5t
config.plugins.IPTVPlayerMario.defaultARMV5TMoviePlayer = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer("standard"), ConfigPlayer('extgstplayer'), ConfigPlayer('exteplayer')])
config.plugins.IPTVPlayerMario.alternativeARMV5TMoviePlayer = ConfigSelection(default="auto", choices=[ConfigPlayer("auto"), ConfigPlayer("mini"), ConfigPlayer("standard"), ConfigPlayer('extgstplayer'), ConfigPlayer('exteplayer')])

# end with buffering mode players

config.plugins.IPTVPlayerMario.SciezkaCache = ConfigDirectory(default="/hdd/IPTVCache/") #, fixed_size = False)
config.plugins.IPTVPlayerMario.NaszaTMP = ConfigDirectory(default="/tmp/") #, fixed_size = False)
config.plugins.IPTVPlayerMario.ZablokujWMV = ConfigYesNo(default=True)

config.plugins.IPTVPlayerMario.gitlab_repo = ConfigSelection(default="zadmario", choices=[("mosz_nowy", "mosz_nowy"), ("zadmario", "zadmario"), ("maxbambi", "maxbambi")])

config.plugins.IPTVPlayerMario.vkcom_login = ConfigText(default="", fixed_size=False)
config.plugins.IPTVPlayerMario.vkcom_password = ConfigText(default="", fixed_size=False)

config.plugins.IPTVPlayerMario.fichiercom_login = ConfigText(default="", fixed_size=False)
config.plugins.IPTVPlayerMario.fichiercom_password = ConfigText(default="", fixed_size=False)

config.plugins.IPTVPlayerMario.iptvplayer_login = ConfigText(default="", fixed_size=False)
config.plugins.IPTVPlayerMario.iptvplayer_password = ConfigText(default="", fixed_size=False)

config.plugins.IPTVPlayerMario.useSubtitlesParserExtension = ConfigYesNo(default=True)
config.plugins.IPTVPlayerMario.opensuborg_login = ConfigText(default="", fixed_size=False)
config.plugins.IPTVPlayerMario.opensuborg_password = ConfigText(default="", fixed_size=False)
config.plugins.IPTVPlayerMario.napisy24pl_login = ConfigText(default="", fixed_size=False)
config.plugins.IPTVPlayerMario.napisy24pl_password = ConfigText(default="", fixed_size=False)

config.plugins.IPTVPlayerMario.debugprint = ConfigSelection(default="", choices=[("", _("no")), ("console", _("yes, to console")),
                                                                            ("debugfile", _("yes, to file /hdd/iptv.dbg")),
                                                                            ("/tmp/iptv.dbg", _("yes, to file /tmp/iptv.dbg")),
                                                                            ("/home/root/logs/iptv.dbg", _("yes, to file /home/root/logs/iptv.dbg")),
                                                                            ])

#icons
config.plugins.IPTVPlayerMario.IconsSize = ConfigSelection(default="100", choices=[("135", "135x135"), ("120", "120x120"), ("100", "100x100")])
config.plugins.IPTVPlayerMario.numOfRow = ConfigSelection(default="0", choices=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("0", "auto")])
config.plugins.IPTVPlayerMario.numOfCol = ConfigSelection(default="0", choices=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"), ("6", "6"), ("7", "7"), ("8", "8"), ("0", "auto")])

config.plugins.IPTVPlayerMario.skin = ConfigSelection(default="auto", choices=GetSkinsList())

#Pin code
from Plugins.Extensions.IPTVPlayerMario.components.iptvpin import IPTVPinWidget
config.plugins.IPTVPlayerMario.fakePin = ConfigSelection(default="fake", choices=[("fake", "****")])
config.plugins.IPTVPlayerMario.pin = ConfigText(default="0000", fixed_size=False)
config.plugins.IPTVPlayerMario.disable_live = ConfigYesNo(default=False)
config.plugins.IPTVPlayerMario.configProtectedByPin = ConfigYesNo(default=False)
config.plugins.IPTVPlayerMario.pluginProtectedByPin = ConfigYesNo(default=False)

config.plugins.IPTVPlayerMario.httpssslcertvalidation = ConfigYesNo(default=False)

#PROXY
config.plugins.IPTVPlayerMario.proxyurl = ConfigText(default="http://user:pass@ip:port", fixed_size=False)
config.plugins.IPTVPlayerMario.german_proxyurl = ConfigText(default="http://user:pass@ip:port", fixed_size=False)
config.plugins.IPTVPlayerMario.russian_proxyurl = ConfigText(default="http://user:pass@ip:port", fixed_size=False)
config.plugins.IPTVPlayerMario.ukrainian_proxyurl = ConfigText(default="http://user:pass@ip:port", fixed_size=False)
config.plugins.IPTVPlayerMario.alternative_proxy1 = ConfigText(default="http://user:pass@ip:port", fixed_size=False)
config.plugins.IPTVPlayerMario.alternative_proxy2 = ConfigText(default="http://user:pass@ip:port", fixed_size=False)

config.plugins.IPTVPlayerMario.captcha_bypass = ConfigSelection(default="", choices=[("", _("Auto")), ("mye2i", "MyE2i"), ("2captcha.com", "2captcha.com"), ("9kw.eu", "9kw.eu")])

config.plugins.IPTVPlayerMario.api_key_9kweu = ConfigText(default="", fixed_size=False)
config.plugins.IPTVPlayerMario.api_key_2captcha = ConfigText(default="", fixed_size=False)

config.plugins.IPTVPlayerMario.myjd_login = ConfigText(default="", fixed_size=False)
config.plugins.IPTVPlayerMario.myjd_password = ConfigText(default="", fixed_size=False)
config.plugins.IPTVPlayerMario.myjd_jdname = ConfigText(default="", fixed_size=False)

# Update
config.plugins.IPTVPlayerMario.autoCheckForUpdate = ConfigYesNo(default=True)
config.plugins.IPTVPlayerMario.updateLastCheckedVersion = ConfigText(default="00.00.00.00", fixed_size=False)
config.plugins.IPTVPlayerMario.fakeUpdate = ConfigSelection(default="fake", choices=[("fake", "  ")])
config.plugins.IPTVPlayerMario.downgradePossible = ConfigYesNo(default=False)
config.plugins.IPTVPlayerMario.possibleUpdateType = ConfigSelection(default="all", choices=[("sourcecode", _("with source code")), ("precompiled", _("precompiled")), ("all", _("all types"))])

# Hosts lists
config.plugins.IPTVPlayerMario.fakeHostsList = ConfigSelection(default="fake", choices=[("fake", "  ")])


# External movie player settings
config.plugins.IPTVPlayerMario.fakExtMoviePlayerList = ConfigSelection(default="fake", choices=[("fake", "  ")])

# hidden options
config.plugins.IPTVPlayerMario.hiddenAllVersionInUpdate = ConfigYesNo(default=False)
config.plugins.IPTVPlayerMario.hidden_ext_player_def_aspect_ratio = ConfigSelection(default="-1", choices=[("-1", _("default")), ("0", _("4:3 Letterbox")), ("1", _("4:3 PanScan")), ("2", _("16:9")), ("3", _("16:9 always")), ("4", _("16:10 Letterbox")), ("5", _("16:10 PanScan")), ("6", _("16:9 Letterbox"))])

config.plugins.IPTVPlayerMario.search_history_size = ConfigInteger(50, (0, 1000000))
config.plugins.IPTVPlayerMario.autoplay_start_delay = ConfigInteger(3, (0, 9))

config.plugins.IPTVPlayerMario.watched_item_color = ConfigSelection(default="#808080", choices=COLORS_DEFINITONS)
config.plugins.IPTVPlayerMario.usepycurl = ConfigYesNo(default=False)

config.plugins.IPTVPlayerMario.prefer_hlsdl_for_pls_with_alt_media = ConfigYesNo(default=True)

###################################################

########################################################
# Generate list of hosts options for Enabling/Disabling
########################################################


class ConfigIPTVHostOnOff(ConfigOnOff):
    def __init__(self, default=False):
        ConfigOnOff.__init__(self, default=default)


gListOfHostsNames = GetHostsList()
for hostName in gListOfHostsNames:
    try:
        # as default all hosts are enabled
        if hostName in ['ipla']:
            enabledByDefault = 'False'
        else:
            enabledByDefault = 'True'
        exec('config.plugins.IPTVPlayerMario.host' + hostName + ' = ConfigIPTVHostOnOff(default = ' + enabledByDefault + ')')
    except Exception:
        printExc(hostName)


def GetListOfHostsNames():
    global gListOfHostsNames
    return gListOfHostsNames


def IsUpdateNeededForHostsChangesCommit(enabledHostsListOld, enabledHostsList=None, hostsFromFolder=None):
    if enabledHostsList == None:
        enabledHostsList = GetEnabledHostsList()
    if hostsFromFolder == None:
        hostsFromFolder = GetHostsList(fromList=False, fromHostFolder=True)

    bRet = False
    if config.plugins.IPTVPlayerMario.remove_diabled_hosts.value and enabledHostsList != enabledHostsListOld:
        hostsFromList = GetHostsList(fromList=True, fromHostFolder=False)
        diffDisabledHostsList = set(enabledHostsListOld).difference(set(enabledHostsList))
        diffList = set(enabledHostsList).symmetric_difference(set(enabledHostsListOld))
        for hostItem in diffList:
            if hostItem in hostsFromList:
                if hostItem in diffDisabledHostsList:
                    if hostItem in hostsFromFolder:
                        # standard host has been disabled but it is still in folder
                        bRet = True
                        break
                else:
                    if hostItem not in hostsFromFolder:
                        # standard host has been enabled but it is not in folder
                        bRet = True
                        break
    if bRet:
        SetGraphicsHash("")
        SetIconsHash("")
    return bRet

###################################################


class ConfigMenu(ConfigBaseWidget):

    def __init__(self, session):
        printDBG("ConfigMenu.__init__ -------------------------------")
        self.list = []
        ConfigBaseWidget.__init__(self, session)
        # remember old
        self.showcoverOld = config.plugins.IPTVPlayerMario.showcover.value
        self.SciezkaCacheOld = config.plugins.IPTVPlayerMario.SciezkaCache.value
        self.platformOld = config.plugins.IPTVPlayerMario.plarform.value
        self.remove_diabled_hostsOld = config.plugins.IPTVPlayerMario.remove_diabled_hosts.value
        self.enabledHostsListOld = GetEnabledHostsList()
        self.basicConfVisible = True #BASIC CONFIGURATION
        self.prxyConfVisible = False #PROXIES CONFIGURATION
        self.buffConfVisible = False #BUFFERING CONFIGURATION
        self.downConfVisible = False #DOWNLOADING CONFIGURATION
        self.captConfVisible = False #CAPTCHA CONFIGURATION
        self.subtConfVisible = False #SUBTITLES CONFIGURATION
        self.playConfVisible = False #PLAYERS CONFIGURATION
        self.otherConfVisible = False #OTHER SETTINGS

    def __del__(self):
        printDBG("ConfigMenu.__del__ -------------------------------")

    def __onClose(self):
        printDBG("ConfigMenu.__onClose -----------------------------")
        ConfigBaseWidget.__onClose(self)

    def layoutFinished(self):
        ConfigBaseWidget.layoutFinished(self)
        self.setTitle(_("E2iPlayer - settings"))

    @staticmethod
    def fillConfigList(list, hiddenOptions=False, basicConfVisible=True, prxyConfVisible=False, buffConfVisible=False, downConfVisible=False,
                                                  captConfVisible=False, subtConfVisible=False, playConfVisible=False, otherConfVisible=False):
        if hiddenOptions:
            list.append(getConfigListEntry('\\c00289496' + _("----- HIDDEN OPTIONS -----"), config.plugins.IPTVPlayerMario.FakeEntry))
            list.append(getConfigListEntry(_("Last checked version"), config.plugins.IPTVPlayerMario.updateLastCheckedVersion))
            list.append(getConfigListEntry(_("Show all version in the update menu"), config.plugins.IPTVPlayerMario.hiddenAllVersionInUpdate))
            list.append(getConfigListEntry(_("VFD set current title:"), config.plugins.IPTVPlayerMario.set_curr_title))
            list.append(getConfigListEntry(_("Write current title to file:"), config.plugins.IPTVPlayerMario.curr_title_file))
            list.append(getConfigListEntry(_("The default aspect ratio for the external player"), config.plugins.IPTVPlayerMario.hidden_ext_player_def_aspect_ratio))

            list.append(getConfigListEntry("exteplayer3path", config.plugins.IPTVPlayerMario.exteplayer3path))
            list.append(getConfigListEntry("gstplayerpath", config.plugins.IPTVPlayerMario.gstplayerpath))
            list.append(getConfigListEntry("wgetpath", config.plugins.IPTVPlayerMario.wgetpath))
            list.append(getConfigListEntry("rtmpdumppath", config.plugins.IPTVPlayerMario.rtmpdumppath))
            list.append(getConfigListEntry("hlsdlpath", config.plugins.IPTVPlayerMario.hlsdlpath))
            list.append(getConfigListEntry("cmdwrappath", config.plugins.IPTVPlayerMario.cmdwrappath))
            list.append(getConfigListEntry("dukpath", config.plugins.IPTVPlayerMario.dukpath))
            list.append(getConfigListEntry("f4mdumppath", config.plugins.IPTVPlayerMario.f4mdumppath))
            list.append(getConfigListEntry("uchardetpath", config.plugins.IPTVPlayerMario.uchardetpath))
            list.append(getConfigListEntry("MIPS Floating Point Architecture", config.plugins.IPTVPlayerMario.plarformfpuabi))
            list.append(getConfigListEntry("E2iPlayer auto start at Enigma2 start", config.plugins.IPTVPlayerMario.plugin_autostart))
            list.append(getConfigListEntry("Auto start method", config.plugins.IPTVPlayerMario.plugin_autostart_method))
            list.append(getConfigListEntry("Prefer hlsld for playlist with alt. media", config.plugins.IPTVPlayerMario.prefer_hlsdl_for_pls_with_alt_media))
            list.append(getConfigListEntry(_("Hosts List Type-NOT FINISHED"), config.plugins.IPTVPlayerMario.hostsListType))

        list.append(getConfigListEntry('\\c00289496' + _("----- BASIC CONFIGURATION (OK) -----"), config.plugins.IPTVPlayerMario.basicConfVisible))
        if basicConfVisible: #BASIC CONFIGURATION
            list.append(getConfigListEntry(_("Auto check for plugin update"), config.plugins.IPTVPlayerMario.autoCheckForUpdate))
            list.append(getConfigListEntry(_("The preferred update server"), config.plugins.IPTVPlayerMario.preferredupdateserver))
            if config.plugins.IPTVPlayerMario.preferredupdateserver.value == '2':
                list.append(getConfigListEntry(_("Add update from GitLab repository"), config.plugins.IPTVPlayerMario.gitlab_repo))
            if config.plugins.IPTVPlayerMario.preferredupdateserver.value == '3':
                list.append(getConfigListEntry(_("%s login") % 'E2iPlayer', config.plugins.IPTVPlayerMario.iptvplayer_login))
                list.append(getConfigListEntry(_("%s password") % 'E2iPlayer', config.plugins.IPTVPlayerMario.iptvplayer_password))
            if config.plugins.IPTVPlayerMario.preferredupdateserver.value != '4':
                list.append(getConfigListEntry(_("Update"), config.plugins.IPTVPlayerMario.fakeUpdate))

            list.append(getConfigListEntry(_("Virtual Keyboard type"), config.plugins.IPTVPlayerMario.osk_type))
            if config.plugins.IPTVPlayerMario.osk_type.value == 'own':
                list.append(getConfigListEntry(_("    Background color"), config.plugins.IPTVPlayerMario.osk_background_color))
                list.append(getConfigListEntry(_("    Show suggestions"), config.plugins.IPTVPlayerMario.osk_allow_suggestions))
                list.append(getConfigListEntry(_("    Default suggestions provider"), config.plugins.IPTVPlayerMario.osk_default_suggestions))

            list.append(getConfigListEntry(_("Platform"), config.plugins.IPTVPlayerMario.plarform))
            list.append(getConfigListEntry(_("Services configuration"), config.plugins.IPTVPlayerMario.fakeHostsList))
            list.append(getConfigListEntry(_("Remove disabled services"), config.plugins.IPTVPlayerMario.remove_diabled_hosts))
            list.append(getConfigListEntry(_("Initialize web interface (experimental)"), config.plugins.IPTVPlayerMario.IPTVWebIterface))

            list.append(getConfigListEntry(_("Disable live at plugin start"), config.plugins.IPTVPlayerMario.disable_live))
            list.append(getConfigListEntry(_("Pin protection for plugin"), config.plugins.IPTVPlayerMario.pluginProtectedByPin))
            list.append(getConfigListEntry(_("Pin protection for configuration"), config.plugins.IPTVPlayerMario.configProtectedByPin))
            if config.plugins.IPTVPlayerMario.pluginProtectedByPin.value or config.plugins.IPTVPlayerMario.configProtectedByPin.value:
                list.append(getConfigListEntry(_("Set pin code"), config.plugins.IPTVPlayerMario.fakePin))

            list.append(getConfigListEntry(_("Skin"), config.plugins.IPTVPlayerMario.skin))
            list.append(getConfigListEntry(_("Display thumbnails"), config.plugins.IPTVPlayerMario.showcover))
            if config.plugins.IPTVPlayerMario.showcover.value:
                list.append(getConfigListEntry(_("    Allowed formats of thumbnails"), config.plugins.IPTVPlayerMario.allowedcoverformats))
                list.append(getConfigListEntry(_("    Remove thumbnails"), config.plugins.IPTVPlayerMario.deleteIcons))
            #list.append(getConfigListEntry("Sortować listy?", config.plugins.IPTVPlayerMario.sortuj))
            list.append(getConfigListEntry(_("Graphic services selector"), config.plugins.IPTVPlayerMario.ListaGraficzna))
            if config.plugins.IPTVPlayerMario.ListaGraficzna.value == True:
                list.append(getConfigListEntry(_("    Enable hosts groups"), config.plugins.IPTVPlayerMario.group_hosts))
                list.append(getConfigListEntry(_("    Service icon size"), config.plugins.IPTVPlayerMario.IconsSize))
                list.append(getConfigListEntry(_("    Number of rows"), config.plugins.IPTVPlayerMario.numOfRow))
                list.append(getConfigListEntry(_("    Number of columns"), config.plugins.IPTVPlayerMario.numOfCol))

            list.append(getConfigListEntry(_("Use the PyCurl for HTTP(S) requests"), config.plugins.IPTVPlayerMario.usepycurl))
            list.append(getConfigListEntry(_("https - validate SSL certificates"), config.plugins.IPTVPlayerMario.httpssslcertvalidation))

        list.append(getConfigListEntry('\\c00289496' + _("----- PROXIES CONFIGURATION (OK) -----"), config.plugins.IPTVPlayerMario.prxyConfVisible))
        if prxyConfVisible: #PROXIES CONFIGURATION
            list.append(getConfigListEntry(_("Alternative proxy server (1)"), config.plugins.IPTVPlayerMario.alternative_proxy1))
            list.append(getConfigListEntry(_("Alternative proxy server (2)"), config.plugins.IPTVPlayerMario.alternative_proxy2))
            list.append(getConfigListEntry(_("Polish proxy server url"), config.plugins.IPTVPlayerMario.proxyurl))
            list.append(getConfigListEntry(_("German proxy server url"), config.plugins.IPTVPlayerMario.german_proxyurl))
            list.append(getConfigListEntry(_("Russian proxy server url"), config.plugins.IPTVPlayerMario.russian_proxyurl))
            list.append(getConfigListEntry(_("Ukrainian proxy server url"), config.plugins.IPTVPlayerMario.ukrainian_proxyurl))

            list.append(getConfigListEntry(_("Folder for cache data"), config.plugins.IPTVPlayerMario.SciezkaCache))
            list.append(getConfigListEntry(_("Folder for temporary data"), config.plugins.IPTVPlayerMario.NaszaTMP))

        list.append(getConfigListEntry('\\c00289496' + _("----- BUFFERING CONFIGURATION (OK) -----"), config.plugins.IPTVPlayerMario.buffConfVisible))
        if buffConfVisible: #BUFFERING CONFIGURATION
            list.append(getConfigListEntry(_("[HTTP] buffering"), config.plugins.IPTVPlayerMario.buforowanie))
            list.append(getConfigListEntry(_("[HLS/M3U8] buffering"), config.plugins.IPTVPlayerMario.buforowanie_m3u8))
            list.append(getConfigListEntry(_("[RTMP] buffering (rtmpdump required)"), config.plugins.IPTVPlayerMario.buforowanie_rtmp))

            if config.plugins.IPTVPlayerMario.buforowanie.value or config.plugins.IPTVPlayerMario.buforowanie_m3u8.value or config.plugins.IPTVPlayerMario.buforowanie_rtmp.value:
                list.append(getConfigListEntry(_("    Video buffer size [MB]"), config.plugins.IPTVPlayerMario.requestedBuffSize))
                list.append(getConfigListEntry(_("    Audio buffer size [KB]"), config.plugins.IPTVPlayerMario.requestedAudioBuffSize))
                list.append(getConfigListEntry(_("Buffering location"), config.plugins.IPTVPlayerMario.bufferingPath))

        list.append(getConfigListEntry('\\c00289496' + _("----- DOWNLOADING CONFIGURATION (OK) -----"), config.plugins.IPTVPlayerMario.downConfVisible))
        if downConfVisible: #DOWNLOADING CONFIGURATION
            list.append(getConfigListEntry(_("Downloads location"), config.plugins.IPTVPlayerMario.NaszaSciezka))
            list.append(getConfigListEntry(_("Start download manager per default"), config.plugins.IPTVPlayerMario.IPTVDMRunAtStart))
            list.append(getConfigListEntry(_("Show download manager after adding new item"), config.plugins.IPTVPlayerMario.IPTVDMShowAfterAdd))
            list.append(getConfigListEntry(_("Number of downloaded files simultaneously"), config.plugins.IPTVPlayerMario.IPTVDMMaxDownloadItem))

            list.append(getConfigListEntry(_("%s e-mail") % ('My JDownloader'), config.plugins.IPTVPlayerMario.myjd_login))
            list.append(getConfigListEntry(_("%s password") % ('My JDownloader'), config.plugins.IPTVPlayerMario.myjd_password))
            list.append(getConfigListEntry(_("%s device name") % ('My JDownloader'), config.plugins.IPTVPlayerMario.myjd_jdname))

        list.append(getConfigListEntry('\\c00289496' + _("----- CAPTCHA CONFIGURATION (OK) -----"), config.plugins.IPTVPlayerMario.captConfVisible))
        if captConfVisible: #CAPTCHA CONFIGURATION
            list.append(getConfigListEntry(_("Default captcha bypass"), config.plugins.IPTVPlayerMario.captcha_bypass))
            list.append(getConfigListEntry(_("%s API KEY") % 'https://9kw.eu/', config.plugins.IPTVPlayerMario.api_key_9kweu))
            list.append(getConfigListEntry(_("%s API KEY") % 'http://2captcha.com/', config.plugins.IPTVPlayerMario.api_key_2captcha))

        list.append(getConfigListEntry('\\c00289496' + _("----- SUBTITLES CONFIGURATION (OK) -----"), config.plugins.IPTVPlayerMario.subtConfVisible))
        if subtConfVisible: #SUBTITLES CONFIGURATION
            list.append(getConfigListEntry(_("Use subtitles parser extension if available"), config.plugins.IPTVPlayerMario.useSubtitlesParserExtension))
            list.append(getConfigListEntry("http://opensubtitles.org/ " + _("login"), config.plugins.IPTVPlayerMario.opensuborg_login))
            list.append(getConfigListEntry("http://opensubtitles.org/ " + _("password"), config.plugins.IPTVPlayerMario.opensuborg_password))
            list.append(getConfigListEntry("http://napisy24.pl/ " + _("login"), config.plugins.IPTVPlayerMario.napisy24pl_login))
            list.append(getConfigListEntry("http://napisy24.pl/ " + _("password"), config.plugins.IPTVPlayerMario.napisy24pl_password))

            list.append(getConfigListEntry("http://vk.com/ " + _("login"), config.plugins.IPTVPlayerMario.vkcom_login))
            list.append(getConfigListEntry("http://vk.com/ " + _("password"), config.plugins.IPTVPlayerMario.vkcom_password))

            list.append(getConfigListEntry("http://1fichier.com/ " + _("e-mail"), config.plugins.IPTVPlayerMario.fichiercom_login))
            list.append(getConfigListEntry("http://1fichier.com/ " + _("password"), config.plugins.IPTVPlayerMario.fichiercom_password))

        list.append(getConfigListEntry('\\c00289496' + _("----- PLAYERS CONFIGURATION (OK) -----"), config.plugins.IPTVPlayerMario.playConfVisible))
        if playConfVisible: #PLAYERS CONFIGURATION
            players = []
            bufferingMode = config.plugins.IPTVPlayerMario.buforowanie.value or config.plugins.IPTVPlayerMario.buforowanie_m3u8.value or config.plugins.IPTVPlayerMario.buforowanie_rtmp.value
            if 'sh4' == config.plugins.IPTVPlayerMario.plarform.value:
                list.append(getConfigListEntry(_("First movie player without buffering mode"), config.plugins.IPTVPlayerMario.defaultSH4MoviePlayer0))
                players.append(config.plugins.IPTVPlayerMario.defaultSH4MoviePlayer0)
                list.append(getConfigListEntry(_("Second movie player without buffering mode"), config.plugins.IPTVPlayerMario.alternativeSH4MoviePlayer0))
                players.append(config.plugins.IPTVPlayerMario.alternativeSH4MoviePlayer0)

                list.append(getConfigListEntry(_("First movie player in buffering mode"), config.plugins.IPTVPlayerMario.defaultSH4MoviePlayer))
                players.append(config.plugins.IPTVPlayerMario.defaultSH4MoviePlayer)
                list.append(getConfigListEntry(_("Second movie player in buffering mode"), config.plugins.IPTVPlayerMario.alternativeSH4MoviePlayer))
                players.append(config.plugins.IPTVPlayerMario.alternativeSH4MoviePlayer)

            elif 'mipsel' == config.plugins.IPTVPlayerMario.plarform.value:
                list.append(getConfigListEntry(_("First movie player without buffering mode"), config.plugins.IPTVPlayerMario.defaultMIPSELMoviePlayer0))
                players.append(config.plugins.IPTVPlayerMario.defaultMIPSELMoviePlayer0)
                list.append(getConfigListEntry(_("Second movie player without buffering mode"), config.plugins.IPTVPlayerMario.alternativeMIPSELMoviePlayer0))
                players.append(config.plugins.IPTVPlayerMario.alternativeMIPSELMoviePlayer0)

                list.append(getConfigListEntry(_("First movie player in buffering mode"), config.plugins.IPTVPlayerMario.defaultMIPSELMoviePlayer))
                players.append(config.plugins.IPTVPlayerMario.defaultMIPSELMoviePlayer)
                list.append(getConfigListEntry(_("Second movie player in buffering mode"), config.plugins.IPTVPlayerMario.alternativeMIPSELMoviePlayer))
                players.append(config.plugins.IPTVPlayerMario.alternativeMIPSELMoviePlayer)

            elif 'i686' == config.plugins.IPTVPlayerMario.plarform.value:
                list.append(getConfigListEntry(_("First movie player without buffering mode"), config.plugins.IPTVPlayerMario.defaultI686MoviePlayer0))
                players.append(config.plugins.IPTVPlayerMario.defaultI686MoviePlayer0)
                list.append(getConfigListEntry(_("Second movie player without buffering mode"), config.plugins.IPTVPlayerMario.alternativeI686MoviePlayer0))
                players.append(config.plugins.IPTVPlayerMario.alternativeI686MoviePlayer0)

                list.append(getConfigListEntry(_("First movie player in buffering mode"), config.plugins.IPTVPlayerMario.defaultI686MoviePlayer))
                players.append(config.plugins.IPTVPlayerMario.defaultI686MoviePlayer)
                list.append(getConfigListEntry(_("Second movie player in buffering mode"), config.plugins.IPTVPlayerMario.alternativeI686MoviePlayer))
                players.append(config.plugins.IPTVPlayerMario.alternativeI686MoviePlayer)

            elif 'armv7' == config.plugins.IPTVPlayerMario.plarform.value:
                list.append(getConfigListEntry(_("First movie player without buffering mode"), config.plugins.IPTVPlayerMario.defaultARMV7MoviePlayer0))
                players.append(config.plugins.IPTVPlayerMario.defaultARMV7MoviePlayer0)
                list.append(getConfigListEntry(_("Second movie player without buffering mode"), config.plugins.IPTVPlayerMario.alternativeARMV7MoviePlayer0))
                players.append(config.plugins.IPTVPlayerMario.alternativeARMV7MoviePlayer0)

                list.append(getConfigListEntry(_("First movie player in buffering mode"), config.plugins.IPTVPlayerMario.defaultARMV7MoviePlayer))
                players.append(config.plugins.IPTVPlayerMario.defaultARMV7MoviePlayer)
                list.append(getConfigListEntry(_("Second movie player in buffering mode"), config.plugins.IPTVPlayerMario.alternativeARMV7MoviePlayer))
                players.append(config.plugins.IPTVPlayerMario.alternativeARMV7MoviePlayer)
            elif 'armv5t' == config.plugins.IPTVPlayerMario.plarform.value:
                list.append(getConfigListEntry(_("First movie player without buffering mode"), config.plugins.IPTVPlayerMario.defaultARMV5TMoviePlayer0))
                players.append(config.plugins.IPTVPlayerMario.defaultARMV5TMoviePlayer0)
                list.append(getConfigListEntry(_("Second movie player without buffering mode"), config.plugins.IPTVPlayerMario.alternativeARMV5TMoviePlayer0))
                players.append(config.plugins.IPTVPlayerMario.alternativeARMV5TMoviePlayer0)

                list.append(getConfigListEntry(_("First movie player in buffering mode"), config.plugins.IPTVPlayerMario.defaultARMV5TMoviePlayer))
                players.append(config.plugins.IPTVPlayerMario.defaultARMV5TMoviePlayer)
                list.append(getConfigListEntry(_("Second movie player in buffering mode"), config.plugins.IPTVPlayerMario.alternativeARMV5TMoviePlayer))
                players.append(config.plugins.IPTVPlayerMario.alternativeARMV5TMoviePlayer)

            else:
                list.append(getConfigListEntry(_("Movie player"), config.plugins.IPTVPlayerMario.NaszPlayer))

            playersValues = [player.value for player in players]
            if 'exteplayer' in playersValues or 'extgstplayer' in playersValues or 'auto' in playersValues:
                list.append(getConfigListEntry(_("External movie player config"), config.plugins.IPTVPlayerMario.fakExtMoviePlayerList))

        list.append(getConfigListEntry('\\c00289496' + _("----- OTHER SETTINGS (OK) -----"), config.plugins.IPTVPlayerMario.otherConfVisible))
        if otherConfVisible: #OTHER SETTINGS
            list.append(getConfigListEntry(_("Autoplay start delay"), config.plugins.IPTVPlayerMario.autoplay_start_delay))
            list.append(getConfigListEntry(_("The number of items in the search history"), config.plugins.IPTVPlayerMario.search_history_size))
            list.append(getConfigListEntry(_("Block wmv files"), config.plugins.IPTVPlayerMario.ZablokujWMV))
            list.append(getConfigListEntry(_("Show IPTVPlayer in extension list"), config.plugins.IPTVPlayerMario.showinextensions))
            list.append(getConfigListEntry(_("Show IPTVPlayer in main menu"), config.plugins.IPTVPlayerMario.showinMainMenu))
            if config.plugins.IPTVPlayerMario.preferredupdateserver.value != '4': #4 = managed by opkg, no no update icon
                list.append(getConfigListEntry(_("Show update icon in service selection menu"), config.plugins.IPTVPlayerMario.AktualizacjaWmenu))
            list.append(getConfigListEntry(_("Debug logs"), config.plugins.IPTVPlayerMario.debugprint))
            if config.plugins.IPTVPlayerMario.preferredupdateserver.value != '4': #4 = managed by opkg, no no update icon
                list.append(getConfigListEntry(_("Allow downgrade"), config.plugins.IPTVPlayerMario.downgradePossible))
                list.append(getConfigListEntry(_("Update packet type"), config.plugins.IPTVPlayerMario.possibleUpdateType))

    def runSetup(self):
        self.list = []
        ConfigMenu.fillConfigList(self.list, self.isHiddenOptionsUnlocked(), self.basicConfVisible, self.prxyConfVisible, self.buffConfVisible, self.downConfVisible,
                                                                             self.captConfVisible, self.subtConfVisible, self.playConfVisible, self.otherConfVisible)
        ConfigBaseWidget.runSetup(self)

    def onSelectionChanged(self):
        currItem = self["config"].getCurrent()[1]
        if currItem in [config.plugins.IPTVPlayerMario.fakePin, config.plugins.IPTVPlayerMario.fakeUpdate, config.plugins.IPTVPlayerMario.fakeHostsList, config.plugins.IPTVPlayerMario.fakExtMoviePlayerList]:
            self.isOkEnabled = True
            self.isSelectable = False
            self.setOKLabel()
        else:
            ConfigBaseWidget.onSelectionChanged(self)

    def keyUpdate(self):
        printDBG("ConfigMenu.keyUpdate")
        if self.isChanged():
            self.askForSave(self.doUpdate, self.doUpdate)
        else:
            self.doUpdate()

    def doUpdate(self, forced=False):
        printDBG("ConfigMenu.doUpdate")
        if not forced:
            self.session.open(IPTVUpdateWindow, UpdateMainAppImpl(self.session))
        else:
            self.session.openWithCallback(self.closeAfterUpdate, IPTVUpdateWindow, UpdateMainAppImpl(self.session, allowTheSameVersion=True))

    def closeAfterUpdate(self, arg1=None, arg2=None):
        self.close()

    def save(self):
        ConfigBaseWidget.save(self)
        if self.showcoverOld != config.plugins.IPTVPlayerMario.showcover.value or \
           self.SciezkaCacheOld != config.plugins.IPTVPlayerMario.SciezkaCache.value:
           pass
           # plugin must be restarted if we wont to this options take effect
        if self.platformOld != config.plugins.IPTVPlayerMario.plarform.value:
            IPTVPlayerNeedInit(True)

    def getMessageBeforeClose(self, afterSave):
        needPluginUpdate = False
        if config.plugins.IPTVPlayerMario.preferredupdateserver.value == "4": #opkg
            return ''
        elif afterSave and config.plugins.IPTVPlayerMario.ListaGraficzna.value and 0 == GetAvailableIconSize(False):
            needPluginUpdate = True
        else:
            enabledHostsList = GetEnabledHostsList()
            hostsFromFolder = GetHostsList(fromList=False, fromHostFolder=True)
            if self.remove_diabled_hostsOld != config.plugins.IPTVPlayerMario.remove_diabled_hosts.value:
                if config.plugins.IPTVPlayerMario.remove_diabled_hosts.value:
                    for folderItem in hostsFromFolder:
                        if folderItem in enabledHostsList:
                            continue
                        else:
                            # there is host file which is not enabled,
                            # so we need perform update to remove it
                            needPluginUpdate = True
                            break
                else:
                    hostsFromList = GetHostsList(fromList=True, fromHostFolder=False)
                    if not set(hostsFromList).issubset(set(hostsFromFolder)):
                        # there is missing hosts files, we need updated does not matter
                        # if these hosts are enabled or disabled
                        needPluginUpdate = True
            elif IsUpdateNeededForHostsChangesCommit(self.enabledHostsListOld, enabledHostsList, hostsFromFolder):
                needPluginUpdate = True

        if needPluginUpdate:
            SetGraphicsHash("")
            SetIconsHash("")

        if not needPluginUpdate and config.plugins.IPTVPlayerMario.IPTVWebIterface.value != IsWebInterfaceModuleAvailable(True):
            needPluginUpdate = True

        if needPluginUpdate:
            return _('Some changes will be applied only after plugin update.\nDo you want to perform update now?')
        else:
            return ''

    def performCloseWithMessage(self, afterSave=True):
        message = self.getMessageBeforeClose(afterSave)
        if message == '':
            self.close()
        else:
            self.session.openWithCallback(self.closeAfterMessage, MessageBox, text=message, type=MessageBox.TYPE_YESNO)

    def closeAfterMessage(self, arg=None):
        if arg:
            self.doUpdate(True)
        else:
            self.close()

    def keyOK(self):
        curIndex = self["config"].getCurrentIndex()
        currItem = self["config"].list[curIndex][1]
        if isinstance(currItem, ConfigDirectory):
            def SetDirPathCallBack(curIndex, newPath):
                if None != newPath:
                    self["config"].list[curIndex][1].value = newPath
            self.session.openWithCallback(boundFunction(SetDirPathCallBack, curIndex), IPTVDirectorySelectorWidget, currDir=currItem.value, title=_("Select directory"))
        elif config.plugins.IPTVPlayerMario.fakePin == currItem:
            self.changePin(start=True)
        elif config.plugins.IPTVPlayerMario.fakeUpdate == currItem:
            self.keyUpdate()
        elif config.plugins.IPTVPlayerMario.fakeHostsList == currItem:
            self.hostsList()
        elif config.plugins.IPTVPlayerMario.fakExtMoviePlayerList == currItem:
            self.extMoviePlayerList()
        elif config.plugins.IPTVPlayerMario.basicConfVisible == currItem:
            self.basicConfVisible = not self.basicConfVisible
            self.runSetup()
        elif config.plugins.IPTVPlayerMario.prxyConfVisible == currItem:
            self.prxyConfVisible = not self.prxyConfVisible
            self.runSetup()
        elif config.plugins.IPTVPlayerMario.buffConfVisible == currItem:
            self.buffConfVisible = not self.buffConfVisible
            self.runSetup()
        elif config.plugins.IPTVPlayerMario.downConfVisible == currItem:
            self.downConfVisible = not self.downConfVisible
            self.runSetup()
        elif config.plugins.IPTVPlayerMario.captConfVisible == currItem:
            self.captConfVisible = not self.captConfVisible
            self.runSetup()
        elif config.plugins.IPTVPlayerMario.subtConfVisible == currItem:
            self.subtConfVisible = not self.subtConfVisible
            self.runSetup()
        elif config.plugins.IPTVPlayerMario.playConfVisible == currItem:
            self.playConfVisible = not self.playConfVisible
            self.runSetup()
        elif config.plugins.IPTVPlayerMario.otherConfVisible == currItem:
            self.otherConfVisible = not self.otherConfVisible
            self.runSetup()
        else:
            ConfigBaseWidget.keyOK(self)

    def getSubOptionsList(self):
        tab = [config.plugins.IPTVPlayerMario.buforowanie,
              config.plugins.IPTVPlayerMario.buforowanie_m3u8,
              config.plugins.IPTVPlayerMario.buforowanie_rtmp,
              config.plugins.IPTVPlayerMario.showcover,
              config.plugins.IPTVPlayerMario.ListaGraficzna,
              config.plugins.IPTVPlayerMario.pluginProtectedByPin,
              config.plugins.IPTVPlayerMario.configProtectedByPin,
              config.plugins.IPTVPlayerMario.plarform,
              config.plugins.IPTVPlayerMario.osk_type,
              config.plugins.IPTVPlayerMario.preferredupdateserver,
              ]
        players = []
        if 'sh4' == config.plugins.IPTVPlayerMario.plarform.value:
            players.append(config.plugins.IPTVPlayerMario.defaultSH4MoviePlayer0)
            players.append(config.plugins.IPTVPlayerMario.alternativeSH4MoviePlayer0)
            players.append(config.plugins.IPTVPlayerMario.defaultSH4MoviePlayer)
            players.append(config.plugins.IPTVPlayerMario.alternativeSH4MoviePlayer)
        elif 'mipsel' == config.plugins.IPTVPlayerMario.plarform.value:
            players.append(config.plugins.IPTVPlayerMario.defaultMIPSELMoviePlayer0)
            players.append(config.plugins.IPTVPlayerMario.alternativeMIPSELMoviePlayer0)
            players.append(config.plugins.IPTVPlayerMario.defaultMIPSELMoviePlayer)
            players.append(config.plugins.IPTVPlayerMario.alternativeMIPSELMoviePlayer)
        elif 'armv7' == config.plugins.IPTVPlayerMario.plarform.value:
            players.append(config.plugins.IPTVPlayerMario.defaultARMV7MoviePlayer0)
            players.append(config.plugins.IPTVPlayerMario.alternativeARMV7MoviePlayer0)
            players.append(config.plugins.IPTVPlayerMario.defaultARMV7MoviePlayer)
            players.append(config.plugins.IPTVPlayerMario.alternativeARMV7MoviePlayer)
        elif 'armv5t' == config.plugins.IPTVPlayerMario.plarform.value:
            players.append(config.plugins.IPTVPlayerMario.defaultARMV5TMoviePlayer0)
            players.append(config.plugins.IPTVPlayerMario.alternativeARMV5TMoviePlayer0)
            players.append(config.plugins.IPTVPlayerMario.defaultARMV5TMoviePlayer)
            players.append(config.plugins.IPTVPlayerMario.alternativeARMV5TMoviePlayer)
        elif 'i686' == config.plugins.IPTVPlayerMario.plarform.value:
            players.append(config.plugins.IPTVPlayerMario.defaultI686MoviePlayer0)
            players.append(config.plugins.IPTVPlayerMario.alternativeI686MoviePlayer0)
            players.append(config.plugins.IPTVPlayerMario.defaultI686MoviePlayer)
            players.append(config.plugins.IPTVPlayerMario.alternativeI686MoviePlayer)
        else:
            players.append(config.plugins.IPTVPlayerMario.NaszPlayer)
        tab.extend(players)
        return tab

    def changePin(self, pin=None, start=False):
        # 'PUT_OLD_PIN', 'PUT_NEW_PIN', 'CONFIRM_NEW_PIN'
        if True == start:
            self.changingPinState = 'PUT_OLD_PIN'
            self.session.openWithCallback(self.changePin, IPTVPinWidget, title=_("Enter old pin"))
        else:
            if pin == None:
                return
            if 'PUT_OLD_PIN' == self.changingPinState:
                if pin == config.plugins.IPTVPlayerMario.pin.value:
                    self.changingPinState = 'PUT_NEW_PIN'
                    self.session.openWithCallback(self.changePin, IPTVPinWidget, title=_("Enter new pin"))
                else:
                    self.session.open(MessageBox, _("Pin incorrect!"), type=MessageBox.TYPE_INFO, timeout=5)
            elif 'PUT_NEW_PIN' == self.changingPinState:
                self.newPin = pin
                self.changingPinState = 'CONFIRM_NEW_PIN'
                self.session.openWithCallback(self.changePin, IPTVPinWidget, title=_("Confirm new pin"))
            elif 'CONFIRM_NEW_PIN' == self.changingPinState:
                if self.newPin == pin:
                    config.plugins.IPTVPlayerMario.pin.value = pin
                    config.plugins.IPTVPlayerMario.pin.save()
                    configfile.save()
                    self.session.open(MessageBox, _("Pin has been changed."), type=MessageBox.TYPE_INFO, timeout=5)
                else:
                    self.session.open(MessageBox, _("Confirmation error."), type=MessageBox.TYPE_INFO, timeout=5)

    def hostsList(self):
        self.session.open(ConfigHostsMenu, GetListOfHostsNames())

    def extMoviePlayerList(self):
        self.session.open(ConfigExtMoviePlayer)


def GetMoviePlayer(buffering=False, useAlternativePlayer=False):
    printDBG("GetMoviePlayer buffering[%r], useAlternativePlayer[%r]" % (buffering, useAlternativePlayer))
    # select movie player

    availablePlayers = []
    if config.plugins.IPTVPlayerMario.plarform.value in ['sh4', 'mipsel', 'armv7', 'armv5t'] and IsExecutable(config.plugins.IPTVPlayerMario.exteplayer3path.value):
        availablePlayers.append('exteplayer')
    if IsExecutable(config.plugins.IPTVPlayerMario.gstplayerpath.value): #config.plugins.IPTVPlayerMario.plarform.value in ['sh4', 'mipsel', 'i686'] and
        availablePlayers.append('extgstplayer')
    availablePlayers.append('mini')
    availablePlayers.append('standard')

    player = None
    alternativePlayer = None

    if 'sh4' == config.plugins.IPTVPlayerMario.plarform.value:
        if buffering:
            player = config.plugins.IPTVPlayerMario.defaultSH4MoviePlayer
            alternativePlayer = config.plugins.IPTVPlayerMario.alternativeSH4MoviePlayer
        else:
            player = config.plugins.IPTVPlayerMario.defaultSH4MoviePlayer0
            alternativePlayer = config.plugins.IPTVPlayerMario.alternativeSH4MoviePlayer0

    elif 'mipsel' == config.plugins.IPTVPlayerMario.plarform.value:
        if buffering:
            player = config.plugins.IPTVPlayerMario.defaultMIPSELMoviePlayer
            alternativePlayer = config.plugins.IPTVPlayerMario.alternativeMIPSELMoviePlayer
        else:
            player = config.plugins.IPTVPlayerMario.defaultMIPSELMoviePlayer0
            alternativePlayer = config.plugins.IPTVPlayerMario.alternativeMIPSELMoviePlayer0

    elif 'armv7' == config.plugins.IPTVPlayerMario.plarform.value:
        if buffering:
            player = config.plugins.IPTVPlayerMario.defaultARMV7MoviePlayer
            alternativePlayer = config.plugins.IPTVPlayerMario.alternativeARMV7MoviePlayer
        else:
            player = config.plugins.IPTVPlayerMario.defaultARMV7MoviePlayer0
            alternativePlayer = config.plugins.IPTVPlayerMario.alternativeARMV7MoviePlayer0

    elif 'armv5t' == config.plugins.IPTVPlayerMario.plarform.value:
        if buffering:
            player = config.plugins.IPTVPlayerMario.defaultARMV5TMoviePlayer
            alternativePlayer = config.plugins.IPTVPlayerMario.alternativeARMV5TMoviePlayer
        else:
            player = config.plugins.IPTVPlayerMario.defaultARMV5TMoviePlayer0
            alternativePlayer = config.plugins.IPTVPlayerMario.alternativeARMV5TMoviePlayer0

    elif 'i686' == config.plugins.IPTVPlayerMario.plarform.value:
        if buffering:
            player = config.plugins.IPTVPlayerMario.defaultI686MoviePlayer
            alternativePlayer = config.plugins.IPTVPlayerMario.alternativeI686MoviePlayer
        else:
            player = config.plugins.IPTVPlayerMario.defaultI686MoviePlayer0
            alternativePlayer = config.plugins.IPTVPlayerMario.alternativeI686MoviePlayer0
    else:
        player = config.plugins.IPTVPlayerMario.NaszPlayer
        alternativePlayer = config.plugins.IPTVPlayerMario.NaszPlayer

    if player.value == 'auto':
        player = CFakeMoviePlayerOption(availablePlayers[0], GetMoviePlayerName(availablePlayers[0]))
    try:
        availablePlayers.remove(player.value)
    except Exception:
        printExc()

    if alternativePlayer.value == 'auto':
        alternativePlayer = CFakeMoviePlayerOption(availablePlayers[0], GetMoviePlayerName(availablePlayers[0]))
    try:
        availablePlayers.remove(alternativePlayer.value)
    except Exception:
        printExc()

    if useAlternativePlayer:
        return alternativePlayer

    return player
