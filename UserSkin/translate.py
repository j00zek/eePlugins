from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Plugins.Extensions.UserSkin.inits import PluginLanguagePath, PluginLanguageDomain
from Components.Language import language
import gettext
import os
import re
try:
    from Components.j00zekSkinTranslatedLabels import translate as skinTranslate
except Exception:
    def skinTranslate(txt):
        return txt

def localeInit():
    lang = language.getLanguage()[:2]
    os.environ["LANGUAGE"] = lang
    gettext.bindtextdomain(PluginLanguageDomain, PluginLanguagePath)

def translateName(name):
    wordsList=['Channel[ ]*Selections','Channel[ ]*Selection','double-spaced','DoubleSpaced','fulllist','Full',
               'Secondinfobars','SecondInfobar', 'Infobars','Infobar',
               'Messageboxes', 'MovieSelection', 
               '_no_','Screens by', 'BigFonts',
               'animated_zzpicon','animated_picon', 'animated']
    for word in wordsList:
        name = re.sub(word , gettext.dgettext(PluginLanguageDomain, word), name, flags=re.I)
    name = re.sub('(\_|\-|\.|\+)',' ', name, flags=re.I) #cleaning
    name = re.sub('(  [ ]*)',' ', name, flags=re.I) #merge multiple (2+) spaces into one
    return name

def _(txt):
    t = gettext.dgettext(PluginLanguageDomain, txt)
    if t == txt:
        t = gettext.gettext(txt)
        if t == txt:
            t = skinTranslate(txt)
            if t == txt:
                t = translateName(txt)
    return t

localeInit()
language.addCallback(localeInit)
