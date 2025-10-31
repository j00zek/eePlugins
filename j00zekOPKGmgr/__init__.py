# -*- coding: utf-8 -*-
from __future__ import absolute_import #zmiana strategii ladowania modulow w py2 z relative na absolute jak w py3
from Plugins.Extensions.j00zekOPKGmgr.version import Version

Info='@j00zek %s' % Version

#stale
PluginName = 'j00zekOPKGmgr'
PluginGroup = 'Extensions'

#Paths
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS
PluginFolder = PluginName
PluginPath = resolveFilename(SCOPE_PLUGINS, '%s/%s/' %(PluginGroup,PluginFolder))
SkinPath = resolveFilename(SCOPE_CURRENT_SKIN, '')

PluginLanguageDomain = "plugin-" + PluginName
PluginLanguagePath = resolveFilename(SCOPE_PLUGINS, '%s/%s/locale' % (PluginGroup,PluginFolder))
from Components.Language import language
import gettext
from os import environ

  
def localeInit():
    lang = language.getLanguage()[:2]
    environ["LANGUAGE"] = lang
    gettext.bindtextdomain(PluginLanguageDomain, PluginLanguagePath)

def mygettext(txt):
    t = gettext.dgettext(PluginLanguageDomain, txt)
    if t == txt:
            t = t
    return t

localeInit()
language.addCallback(localeInit)
_ = mygettext