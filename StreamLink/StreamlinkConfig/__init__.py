#### tlumaczenia
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
    for cfgPath in ['/j00zek/streamlink_defaults/','/hdd/User_Configs', '/etc/streamlink/']:
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
config.plugins.streamlinkSRV = ConfigSubsection()

config.plugins.streamlinkSRV.installBouquet   = NoSave(ConfigNothing())
config.plugins.streamlinkSRV.removeBouquet    = NoSave(ConfigNothing())
config.plugins.streamlinkSRV.generateBouquet  = NoSave(ConfigNothing())
config.plugins.streamlinkSRV.downloadBouquet  = NoSave(ConfigNothing())
config.plugins.streamlinkSRV.unmanagedBouquet = NoSave(ConfigNothing())
config.plugins.streamlinkSRV.VLCusingLUA      = NoSave(ConfigNothing())

config.plugins.streamlinkSRV.enabled = ConfigYesNo(default = False)
config.plugins.streamlinkSRV.logLevel = ConfigSelection(default = "debug", choices = [("none", _("none")),
                                                                                    ("info", _("info")),
                                                                                    ("warning", _("warning")),
                                                                                    ("error", _("error")),
                                                                                    ("critical", _("critical")),
                                                                                    ("debug", _("debug")),
                                                                                    ("trace", _("trace")),
                                                                              ])
config.plugins.streamlinkSRV.logToFile = ConfigEnableDisable(default = False)
config.plugins.streamlinkSRV.ClearLogFile = ConfigEnableDisable(default = True)
config.plugins.streamlinkSRV.logPath = ConfigSelection(default = "/tmp", choices = [("/home/root", "/home/root"), ("/tmp", "/tmp"), ("/hdd", "/hdd"), ])
config.plugins.streamlinkSRV.PortNumber = ConfigSelection(default = "8088", choices = [("8088", "8088"), ("88", "88"), ])
config.plugins.streamlinkSRV.bufferPath = ConfigText(default = "/tmp", fixed_size = False)
#Tryb pracy streamlinka
config.plugins.streamlinkSRV.binName = ConfigSelection(default = "streamlinkSRV", choices = [("streamlinkSRV", "W 100% zgodny ze streamlinkiem, ale wolniejszy"), ("streamlinkproxySRV", "Korzysta ze streamlinka, szybszy ale niektóre adresy mogą nie działać"),])
config.plugins.streamlinkSRV.StandbyMode = ConfigEnableDisable(default = True)

# pilot.wp.pl
config.plugins.streamlinkSRV.WPusername = ConfigText(readCFG('WPusername'), fixed_size = False)
config.plugins.streamlinkSRV.WPpassword = ConfigPassword(readCFG('WPpassword'), fixed_size = False)
config.plugins.streamlinkSRV.WPbouquet  = NoSave(ConfigNothing())
config.plugins.streamlinkSRV.WPlogin    = NoSave(ConfigNothing())
config.plugins.streamlinkSRV.WPpreferDASH = ConfigEnableDisable(default = False)
config.plugins.streamlinkSRV.WPdevice = ConfigSelection(default = "androidtv", choices = [("androidtv", "Android TV"), ("web", _("web client")), ])
config.plugins.streamlinkSRV.WPvideoDelay = ConfigSelection(default = "0", choices = [("0", _("don't delay")), ("0.25", _("by %s s." % '0.25')),
                                                                                      ("0.5", _("by %s s." % '0.5')), ("0.75", _("by %s s." % '0.75')),
                                                                                      ("1.0", _("by %s s." % '1.0')), ("5.0", _("by %s s." % '5.0'))])

def DBGlog(text):
    print(str(text))
    #open("/tmp/StreamlinkConfig.log", "a").write('%s\n' % str(text))
