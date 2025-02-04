# -*- coding: utf-8 -*-
###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayerMario.components.iptvplayerwidget import E2iPlayerWidget
from Plugins.Extensions.IPTVPlayerMario.components.iptvconfigmenu import ConfigMenu
from Plugins.Extensions.IPTVPlayerMario.components.iptvpin import IPTVPinWidget
from Plugins.Extensions.IPTVPlayerMario.components.iptvplayerinit import TranslateTXT as _, IPTVPlayerNeedInit
from Plugins.Extensions.IPTVPlayerMario.setup.iptvsetupwidget import IPTVSetupMainWidget
from Plugins.Extensions.IPTVPlayerMario.tools.iptvtools import printDBG, IsExecutable, IsWebInterfaceModuleAvailable
###################################################

###################################################
# FOREIGN import
###################################################
from enigma import getDesktop
from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Tools.BoundFunction import boundFunction
from Components.config import config
from Tools.Directories import resolveFilename, fileExists, SCOPE_PLUGINS
###################################################
import os
####################################################
# Wywołanie wtyczki w roznych miejscach
####################################################


def Plugins(**kwargs):
    os.system('/usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayerMario/tools/pathsPatcher.sh &')
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 1920:
        iconFile = "icons/iptvlogohd.png"
    else:
        iconFile = "icons/iptvlogo.png"
    desc = _("Watch Videos Online")
    list = []
    if config.plugins.IPTVPlayerMario.plugin_autostart.value:
        if config.plugins.IPTVPlayerMario.plugin_autostart_method.value == 'wizard':
            list.append(PluginDescriptor(name=(('E2iPlayerMario')), description=desc, where=[PluginDescriptor.WHERE_WIZARD], fnc=(9, pluginAutostart), needsRestart=False))
        elif config.plugins.IPTVPlayerMario.plugin_autostart_method.value == 'infobar':
            list.append(PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc=pluginAutostartSetup))

    list.append(PluginDescriptor(name=(('E2iPlayerMario')), description=desc, where=[PluginDescriptor.WHERE_PLUGINMENU], icon=iconFile, fnc=main)) # always show in plugin menu
    list.append(PluginDescriptor(name=(('E2iPlayerMario')), description=desc, where=PluginDescriptor.WHERE_MENU, fnc=startIPTVfromMenu))
    if config.plugins.IPTVPlayerMario.showinextensions.value:
        list.append(PluginDescriptor(name=(('E2iPlayerMario')), description=desc, where=[PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=main))
    if IsWebInterfaceModuleAvailable() and config.plugins.IPTVPlayerMario.IPTVWebIterface.value:
        try:
            list.append(PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=sessionstart, needsRestart=False)) # activating IPTV web interface
        except Exception:
            print("IPTVplayer Exception appending PluginDescriptor.WHERE_SESSIONSTART descriptor.")
    return list


######################################################
# Autostart from InfoBar - trick
######################################################
gInfoBar__init__ = None


def InfoBar__init__wrapper(self, *args, **kwargs):
    global gInfoBar__init__
    gInfoBar__init__(self, *args, **kwargs)
    self.onShow.append(doPluginAutostart)


def pluginAutostartSetup(reason, **kwargs):
    global gInfoBar__init__
    if reason == 0 and gInfoBar__init__ == None:
        from Screens.InfoBar import InfoBar
        gInfoBar__init__ = InfoBar.__init__
        InfoBar.__init__ = InfoBar__init__wrapper


def doPluginAutostart():
    from Screens.InfoBar import InfoBar
    InfoBar.instance.onShow.remove(doPluginAutostart)
    runMain(InfoBar.instance.session)
######################################################

####################################################
# Konfiguracja wtyczki
####################################################

#from __init__ import _


def startIPTVfromMenu(menuid, **kwargs):
    if menuid == "system":
        return [(_("Configure %s") % 'E2iPlayerMario', mainSetup, 'iptvMario_config', None)]
    elif menuid == "mainmenu" and config.plugins.IPTVPlayerMario.showinMainMenu.value == True:
        return [('E2iPlayerMario', main, 'iptvMario_main', None)]
    else:
        return []


def mainSetup(session, **kwargs):
    if config.plugins.IPTVPlayerMario.configProtectedByPin.value:
        session.openWithCallback(boundFunction(pinCallback, session, runSetup), IPTVPinWidget, title=_("Enter pin"))
    else:
        runSetup(session)


def runSetup(session):
    session.open(ConfigMenu)


def main(session, **kwargs):
    if config.plugins.IPTVPlayerMario.pluginProtectedByPin.value:
        session.openWithCallback(boundFunction(pinCallback, session, runMain), IPTVPinWidget, title=_("Enter pin"))
    else:
        runMain(session)


class pluginAutostart(Screen):
    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self.onShow.append(self.onStart)

    def onStart(self):
        self.onShow.remove(self.onStart)
        runMain(self.session, self.iptvDoRunMain)

    def iptvDoRunMain(self, session):
        session.openWithCallback(self.iptvDoClose, E2iPlayerWidget)

    def iptvDoClose(self, **kwargs):
        self.close()


def doRunMain(session):
    session.open(E2iPlayerWidget)


def runMain(session, nextFunction=doRunMain):
    def allToolsFromOPKG():
        if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayerMario/plugin.pe2i'): #users of private version jave all tools installed by design
            return True
        else:
            toolsList = ['enigma2-plugin-extensions-e2iplayer-deps', 'duktape', 'exteplayer3', 'uchardet', 'gstplayer', 'rtmpdump', 'python3-e2icjson', 'python3-pycurl']
            for tool in toolsList:
                tryToInstall = ''
                if not os.path.exists(os.path.join('/var/lib/opkg/info/', tool) + '.control'):
                    tryToInstall += ' ' + tool
            if tryToInstall != '':
                printDBG('allToolsFromOPKG() >>> Trying to install missing packages: %s' % tryToInstall)
                os.system('(opkg update;opkg install %s)&' % tryToInstall)
                return False
            else:
                printDBG('allToolsFromOPKG() >>> All required packages installed :)')
                return True

    for DBGfile in ['/hdd/iptv.dbg', '/tmp/iptv.dbg', '/home/root/logs/iptv.dbg', '/tmp/print.log']:
        if os.path.exists(DBGfile):
            try:
                os.remove(DBGfile)
            except Exception:
                pass

    wgetpath = IsExecutable(config.plugins.IPTVPlayerMario.wgetpath.value)
    rtmpdumppath = IsExecutable(config.plugins.IPTVPlayerMario.rtmpdumppath.value)
    f4mdumppath = IsExecutable(config.plugins.IPTVPlayerMario.f4mdumppath.value)
    platform = config.plugins.IPTVPlayerMario.plarform.value
    if platform in ["auto", "unknown"] or not wgetpath or not rtmpdumppath or not f4mdumppath:
        session.openWithCallback(boundFunction(nextFunction, session), IPTVSetupMainWidget)
    elif IPTVPlayerNeedInit() and os.path.exists('/var/lib/opkg/info/') and not allToolsFromOPKG():
        session.openWithCallback(boundFunction(nextFunction, session), IPTVSetupMainWidget, True)
    else:
        nextFunction(session)


def pinCallback(session, callbackFun, pin=None):
    if None == pin:
        return
    if pin != config.plugins.IPTVPlayerMario.pin.value:
        session.open(MessageBox, _("Pin incorrect!"), type=MessageBox.TYPE_INFO, timeout=5)
        return
    callbackFun(session)


def sessionstart(reason, **kwargs):
    if reason == 0 and 'session' in kwargs:
        try:
            import Plugins.Extensions.IPTVPlayerMario.Web.initiator
        except Exception as e:
            print("EXCEPTION initiating IPTVplayer WebComponent:", str(e))
