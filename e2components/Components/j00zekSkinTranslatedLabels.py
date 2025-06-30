# -*- coding: utf-8 -*-
#
# j00zek 2019/2020
#
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3

from Components.Language import language
from os import environ
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN
import gettext

def localeInit():
    lang = language.getLanguage()[:2]
    environ["LANGUAGE"] = lang
    gettext.bindtextdomain('TranslatedLabels',  resolveFilename(SCOPE_CURRENT_SKIN, 'locale'))

def translate(txt):
    #open("/tmp/test2.txt", "a").write('%s\n' % txt)
    t = gettext.dgettext('TranslatedLabels', txt)
    if t == txt:
            t = gettext.gettext(txt)
    return t

localeInit()
