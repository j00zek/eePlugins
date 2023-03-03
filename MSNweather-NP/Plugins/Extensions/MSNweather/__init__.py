# -*- coding: utf-8 -*-
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import os, gettext, sys

PyMajorVersion = sys.version_info.major

PluginLanguageDomain = "MSNweather"
PluginLanguagePath = "Extensions/MSNweather/locale"

if os.path.exists('/tmp/.MSNdata' ): #porzadki przy starcie
    os.system('rm -f /tmp/.MSNdata/*.log') 

if not os.path.exists('/etc/enigma2/MSN_defaults/'):
    if os.path.exists('/j00zek/MSN_defaults'):
        os.symlink('/j00zek/MSN_defaults', '/etc/enigma2/MSN_defaults')
    elif os.path.exists('/hdd/MSN_defaults'):
        os.symlink('/j00zek/MSN_defaults', '/etc/enigma2/MSN_defaults')
    elif os.path.exists('/autofs/sda1/MSN_defaults'):
        os.symlink('/j00zek/MSN_defaults', '/etc/enigma2/MSN_defaults')
    elif os.path.exists('/autofs/sdb1/MSN_defaults'):
        os.symlink('/j00zek/MSN_defaults', '/etc/enigma2/MSN_defaults')
    else:
        os.mkdir('/etc/enigma2/MSN_defaults/')
    for cfgFile in [('airlyAPIKEY',''), ('msnAPIKEY',''), ('SensorsPriority','SmogOK,LO2,TS,Airly,GIOS,BleBox,OpenSense,MSN'),
                    ('airlyID.0',''), ('Fcity.0',''), ('geolongitude.0','auto'), ('geolatitude.0','auto'), 
                    ('city.0', 'Warszawa'), ('weatherlocationcode.0', ''), ('weatherSearchFullName.0', ''), 
                    ('thingSpeakChannelID.0', ''), ('airlyID.0', ''), ('Fcity.0', ''), ('Fmeteo.0', ''), 
                    ('giosID.0', ''), ('bleboxID.0', ''), ('openSenseID.0', ''), ('smogokID.0', ''),
                    ('HistoryPeriod','43200')]:
        if not os.path.exists('/etc/enigma2/MSN_defaults/%s' % cfgFile[0]):
            with open('/etc/enigma2/MSN_defaults/%s' % cfgFile[0], 'w') as cf:
                cf.write(cfgFile[1])
                cf.close()

def readCFG(cfgName, defVal = ''):
    cfgPath = '/etc/enigma2/MSN_defaults/%s' % cfgName
    if os.path.exists(cfgPath):
        retValue = open(cfgPath, 'r').readline().strip()
    else:
        retValue = defVal
    return retValue

def localeInit():
    langPath = resolveFilename(SCOPE_PLUGINS, PluginLanguagePath)
    gettext.bindtextdomain(PluginLanguageDomain, langPath)
    gettext.bindtextdomain('skytext2skycode', langPath)
    gettext.bindtextdomain('airQuality', langPath)

def _(txt):
    if gettext.dgettext(PluginLanguageDomain, txt):
        return gettext.dgettext(PluginLanguageDomain, txt)
    else:
        #print("[" + PluginLanguageDomain + "] fallback to default translation for " + txt)
        return gettext.gettext(txt)

localeInit()
language.addCallback(localeInit)
