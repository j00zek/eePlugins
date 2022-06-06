#### tlumaczenia
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3

PluginName = 'StreamlinkConfig'

from Components.config import *
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
PluginLanguageDomain = "plugin-" + PluginName
PluginLanguagePath = resolveFilename(SCOPE_PLUGINS, 'Extensions/%s/locale' % (PluginName))
from Components.Language import language
import gettext, os
    
#### get user configs ####
def readCFG(cfgName, defVal = ''):
    retValue = defVal
    for cfgPath in ['/j00zek/streamlink_defaults/','/hdd/User_Configs']:
        if os.path.exists(os.path.join(cfgPath, cfgName)):
            retValue = open(os.path.join(cfgPath, cfgName), 'r').readline().strip()
            break
    return retValue

def localeInit():
    lang = language.getLanguage()[:2]
    os.environ["LANGUAGE"] = lang
    gettext.bindtextdomain(PluginLanguageDomain, PluginLanguagePath)

def mygettext(txt):
    t = gettext.dgettext(PluginLanguageDomain, txt)
    return t

localeInit()
language.addCallback(localeInit)

################################################################################################
config.plugins.streamlinksrv = ConfigSubsection()

config.plugins.streamlinksrv.installBouquet = NoSave(ConfigNothing())
config.plugins.streamlinksrv.removeBouquet = NoSave(ConfigNothing())
config.plugins.streamlinksrv.generateBouquet = NoSave(ConfigNothing())
config.plugins.streamlinksrv.One = NoSave(ConfigNothing())
config.plugins.streamlinksrv.Two = NoSave(ConfigNothing())
config.plugins.streamlinksrv.Three = NoSave(ConfigNothing())
config.plugins.streamlinksrv.Four = NoSave(ConfigNothing())
config.plugins.streamlinksrv.Five = NoSave(ConfigNothing())

config.plugins.streamlinksrv.enabled = ConfigYesNo(default = False)
config.plugins.streamlinksrv.logLevel = ConfigSelection(default = "info", choices = [("none", _("none")),
                                                                                    ("info", _("info")),
                                                                                    ("warning", _("warning")),
                                                                                    ("error", _("error")),
                                                                                    ("critical", _("critical")),
                                                                                    ("debug", _("debug")),
                                                                                    ("trace", _("trace")),
                                                                              ])
config.plugins.streamlinksrv.logToFile = ConfigEnableDisable(default = False)
config.plugins.streamlinksrv.ClearLogFile = ConfigEnableDisable(default = True)
config.plugins.streamlinksrv.logPath = ConfigSelection(default = "/tmp", choices = [("/home/root", "/home/root"), ("/tmp", "/tmp"), ("/hdd", "/hdd"), ])
config.plugins.streamlinksrv.PortNumber = ConfigSelection(default = "8088", choices = [("8088", "8088"), ("88", "88"), ])
config.plugins.streamlinksrv.bufferPath = ConfigText(default = "/tmp", fixed_size = False)
config.plugins.streamlinksrv.EPGserver = ConfigEnableDisable(default = False)
config.plugins.streamlinksrv.Recorder = ConfigEnableDisable(default = False)
config.plugins.streamlinksrv.useCLI = ConfigSelection(default = "n", choices = [("n", "No"), ("a", "Yes, for all"), ("s", "Yes, only for defined sites only"),])
#config.plugins.streamlinksrv.managePicons = ConfigEnableDisable(default = True)
config.plugins.streamlinksrv.StandbyMode = ConfigEnableDisable(default = False)
config.plugins.streamlinksrv.streamlinkProxy1 = ConfigText(default = "https://pilot.wp.pl/api/v1/channel/271", fixed_size = False)

# pilot.wp.pl
config.plugins.streamlinksrv.WPusername = ConfigText(readCFG('WPusername'), fixed_size = False)
config.plugins.streamlinksrv.WPpassword = ConfigPassword(readCFG('WPpassword'), fixed_size = False)
config.plugins.streamlinksrv.WPbouquet  = NoSave(ConfigNothing())
config.plugins.streamlinksrv.WPlogin    = NoSave(ConfigNothing())
config.plugins.streamlinksrv.WPpreferDASH = ConfigEnableDisable(default = False)
config.plugins.streamlinksrv.WPdevice = ConfigSelection(default = "androidtv", choices = [("androidtv", "Android TV"), ("web", _("web client")), ])
config.plugins.streamlinksrv.WPvideoDelay = ConfigSelection(default = "0", choices = [("0", _("don't delay")), ("0.25", _("by %s s." % '0.25')),
                                                                                      ("0.5", _("by %s s." % '0.5')), ("0.75", _("by %s s." % '0.75')),
                                                                                      ("1.0", _("by %s s." % '1.0')), ("5.0", _("by %s s." % '5.0'))])

# remote E2
config.plugins.streamlinksrv.remoteE2address = ConfigText(default = "192.168.1.8")
config.plugins.streamlinksrv.remoteE2port = ConfigText(default = "8001")
config.plugins.streamlinksrv.remoteE2username = ConfigText(default = "root")
config.plugins.streamlinksrv.remoteE2password = ConfigPassword(default = "root")
config.plugins.streamlinksrv.remoteE2zap = ConfigEnableDisable(default = False)
config.plugins.streamlinksrv.remoteE2wakeup = ConfigEnableDisable(default = False)


def DBGlog(text):
    if config.plugins.streamlinksrv.logLevel.value == 'none':
        pass
    elif config.plugins.streamlinksrv.logLevel.value == 'info':
        print(text)
    else:
        open("/tmp/StreamlinkConfig.log", "a").write('%s\n' % str(text))
