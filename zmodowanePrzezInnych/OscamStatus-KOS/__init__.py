from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ as os_environ
import gettext

def localeInit():
    lang = language.getLanguage()[:2]
    os_environ['LANGUAGE'] = lang
    gettext.bindtextdomain('OscamStatus', resolveFilename(SCOPE_PLUGINS, 'Extensions/OscamStatus/locale'))


def _(txt):
    t = gettext.dgettext('OscamStatus', txt)
    if t == txt:
        print '[OscamStatus] fallback to default translation for', txt
        t = gettext.gettext(txt)
    return t


localeInit()
language.addCallback(localeInit)