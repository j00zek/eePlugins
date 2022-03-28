#### tlumaczenia
PluginName = 'DynamicLCDbrightnessInStandby'

from Tools.Directories import resolveFilename, SCOPE_PLUGINS
PluginLanguageDomain = "plugin-" + PluginName
PluginLanguagePath = resolveFilename(SCOPE_PLUGINS, 'Extensions/%s/locale' % (PluginName))
from Components.Language import language
import gettext
from os import environ
    
def localeInit():
    lang = language.getLanguage()[:2]
    environ["LANGUAGE"] = lang
    gettext.bindtextdomain(PluginLanguageDomain, PluginLanguagePath)

def mygettext(txt):
    t = gettext.dgettext(PluginLanguageDomain, txt)
    return t

localeInit()
language.addCallback(localeInit)
#_ = mygettext
