#### tlumaczenia
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3

PluginName = 'StreamlinkConfig'

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
