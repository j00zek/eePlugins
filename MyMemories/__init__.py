#### tlumaczenia
PluginName = 'MyMemories'

from Tools.Directories import resolveFilename, SCOPE_PLUGINS
PluginLanguageDomain = PluginName
PluginLanguagePath = resolveFilename(SCOPE_PLUGINS, 'Extensions/%s/locale' % (PluginName))
from Components.Language import language
import gettext
from os import environ
    
def localeInit():
    lang = language.getLanguage()[:2]
    environ["LANGUAGE"] = lang
    gettext.bindtextdomain(PluginName, PluginLanguagePath)

def mygettext(txt):
    t = gettext.dgettext(PluginName, txt)
    return t

localeInit()
language.addCallback(localeInit)
#_ = mygettext
