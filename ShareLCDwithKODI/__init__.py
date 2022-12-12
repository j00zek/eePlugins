# -*- coding: utf-8 -*-
from version import Version
Info='@j00zek %s' % Version

#stale
PluginName = 'ShareLCDwithKODI'
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
    return t

localeInit()
language.addCallback(localeInit)
_ = mygettext

##################################################### LOAD SKIN DEFINITION #####################################################
def LoadSkin(SkinName):
    printDEBUG("LoadSkin >>> %s" % SkinName)
    from enigma import getDesktop
    model=''
    if os_path.exists("/proc/stb/info/vumodel"):
        with open("/proc/stb/info/vumodel", "r") as f:
            model=f.read().strip()
            f.close()
    elif os_path.exists("/proc/stb/info/model"):
        with open("/proc/stb/info/model", "r") as f:
            model=f.read().strip()
            f.close()
    
    if SkinName.endswith('.xml'):
        SkinName=SkinName[:-4]
    skinDef=None
    
    if getDesktop(0).size().width() == 1920 and os_path.exists("%sskins/%s%sFHD.xml" % (PluginPath,SkinName,model)):
        with open("%sskins/%s%sFHD.xml" % (PluginPath,SkinName,model),'r') as skinfile:
            skinDef=skinfile.read()
            skinfile.close()
    elif getDesktop(0).size().width() == 1920 and os_path.exists("%sskins/%sFHD.xml" % (PluginPath,SkinName)):
        with open("%sskins/%sFHD.xml" % (PluginPath,SkinName),'r') as skinfile:
            skinDef=skinfile.read()
            skinfile.close()
            
    elif os_path.exists("%sskins/%s%s.xml" % (PluginPath,SkinName,model)):
        with open("%sskins/%s%s.xml" % (PluginPath,SkinName,model),'r') as skinfile:
            skinDef=skinfile.read()
            skinfile.close()
    elif os_path.exists("%sskins/%s.xml" % (PluginPath,SkinName)):
        with open("%sskins/%s.xml" % (PluginPath,SkinName),'r') as skinfile:
            skinDef=skinfile.read()
            skinfile.close()
    else:
        printDEBUG("%s does not exists" % SkinName)
    return skinDef
