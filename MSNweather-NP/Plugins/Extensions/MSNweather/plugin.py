# -*- coding: utf-8 -*-
from __future__ import absolute_import #zmiana strategii ladowania modulow w py2 z relative na absolute jak w py3
from . import _ , readCFG, PyMajorVersion
from Plugins.Extensions.MSNweather.debug import printDEBUG, clearLogs
from Plugins.Extensions.MSNweather.version import Version
from Plugins.Extensions.MSNweather.getWeather import getWeather
from Plugins.Extensions.MSNweather.setupNP import initConfig, MSNWeatherEntriesListConfigScreen

from Components.config import ConfigSubsection, ConfigSubList, ConfigInteger, config, NoSave, ConfigEnableDisable, ConfigSelection, ConfigText, ConfigIP, ConfigYesNo, ConfigNothing, ConfigPassword
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_SKIN
import time, os

if PyMajorVersion > 2:
    from importlib import reload

DBG = False
    
config.plugins.MSNweatherNP = ConfigSubsection()
config.plugins.MSNweatherNP.FakeEntry = NoSave(ConfigNothing())
config.plugins.MSNweatherNP.airlyLimits = NoSave(ConfigText(default='', fixed_size=False))
choicesList = [
 (
  'skin_MSNweatherNP-vertical.xml', _('Vertically')),
 (
  'skin_MSNweatherNP-horizontal.xml', _('Horizontally'))]

if os.path.exists('/usr/share/enigma2/BlackHarmony/allScreens/MSNweatherNP/'):
    for mFile in os.listdir('/usr/share/enigma2/BlackHarmony/allScreens/MSNweatherNP/'):
        if mFile.startswith('skin_MSNweatherNP-') and mFile.endswith('.xml'):
            sFile = mFile[18:-4]
            sFile = 'BlackHarmony ' + _(sFile)
            choicesList.append((os.path.join('/usr/share/enigma2/BlackHarmony/allScreens/MSNweatherNP/', mFile), sFile))

config.plugins.MSNweatherNP.skinOrientation = ConfigSelection(choices=choicesList, default='skin_MSNweatherNP-horizontal.xml')

config.plugins.MSNweatherNP.SensorsPriority = ConfigSelection(choices=[
 ('MSN,SmogTok,LO2,TS,Airly,GIOS,BleBox,OpenSense', 'MSN/F,SmogTok,LO2,TS,Airly,GIOS,BleBox,OpenSense'),
 ('SmogTok,LO2,TS,Airly,GIOS,BleBox,OpenSense,MSN', 'SmogTok,LO2,TS,Airly,GIOS,BleBox,OpenSense,MSN/F'),
 ('LO2,TS,Airly,GIOS,BleBox,OpenSense,SmogTok,MSN', 'LO2,TS,Airly,GIOS,BleBox,OpenSense,SmogTok,MSN/F'),
 ('TS,Airly,GIOS,BleBox,OpenSense,SmogTok,LO2,MSN', 'TS,Airly,GIOS,BleBox,OpenSense,SmogTok,LO2,MSN/F'),
 ('Airly,GIOS,BleBox,OpenSense,SmogTok,LO2,TS,MSN', 'Airly,GIOS,BleBox,OpenSense,SmogTok,LO2,TS,MSN/F'),
 ('GIOS,BleBox,OpenSense,SmogTok,LO2,TS,Airly,MSN', 'GIOS,BleBox,OpenSense,SmogTok,LO2,TS,Airly,MSN/F'),
 ('BleBox,OpenSense,SmogTok,LO2,TS,Airly,GIOS,MSN', 'BleBox,OpenSense,SmogTok,LO2,TS,Airly,GIOS,MSN/F'),
 ('OpenSense,SmogTok,LO2,TS,Airly,GIOS,BleBox,MSN', 'OpenSense,SmogTok,LO2,TS,Airly,GIOS,BleBox,MSN/F'),
 ('/etc/enigma2/MSN_defaults/SensorsPriority', 'z pliku /etc/enigma2/MSN_defaults/SensorsPriority')], default = readCFG('SensorsPriority'))

config.plugins.MSNweatherNP.BuildHistograms = ConfigEnableDisable(default=False)
config.plugins.MSNweatherNP.airlyAPIKEY = ConfigPassword(default= readCFG('airlyAPIKEY'), visible_width=100, fixed_size=False)
config.plugins.MSNweatherNP.msnAPIKEY = ConfigPassword(default= readCFG('msnAPIKEY'), visible_width=100, fixed_size=False)
config.plugins.MSNweatherNP.entrycount = ConfigInteger(0)
config.plugins.MSNweatherNP.currEntry = NoSave(ConfigInteger(0))
config.plugins.MSNweatherNP.callbacksCount = NoSave(ConfigInteger(0))
config.plugins.MSNweatherNP.Entry = ConfigSubList()
#ikony dzienne
availableOptions = [
     (
      'serviceIcons', _('MSN/F service icons'))]
if os.path.exists(os.path.dirname(resolveFilename(SCOPE_SKIN, config.skin.primary_skin.value)) + '/weather_icons/'):
        availableOptions.append(('weatherIcons', _('skin Icons')))
if os.path.exists('/usr/share/enigma2/animatedWeatherIcons'):
        availableOptions.append(('animIcons', _('animated Icons')))
config.plugins.MSNweatherNP.IconsType = ConfigSelection(choices=availableOptions, default='serviceIcons')
#ikony godzinowe
availableOptions = [
     (
      'serviceIcons', _('MSN/F service icons'))]
if os.path.exists(os.path.dirname(resolveFilename(SCOPE_SKIN, config.skin.primary_skin.value)) + '/weather_icons/'):
        availableOptions.append(('weatherIcons', _('skin Icons')))
config.plugins.MSNweatherNP.hIconsType = ConfigSelection(choices=availableOptions, default='serviceIcons')

config.plugins.MSNweatherNP.ScalePicType = ConfigSelection(choices=[('self.instance.setScale', _('internal E2')),
     (
      'ePicLoad', _('ePicLoad (E.g. Vu+ org)'))], default='self.instance.setScale')
config.plugins.MSNweatherNP.AC1 = ConfigSelection(choices=[('off', _('not installed')), ('daikin', _('Daikin Air Conditioner')), ('samsung', _('Samsung Air Conditioner'))], default='off')
config.plugins.MSNweatherNP.AC1_IP = ConfigIP(default=[0, 0, 0, 0])
config.plugins.MSNweatherNP.AC1_PORT = ConfigInteger(default=80, limits=(80, 999))
config.plugins.MSNweatherNP.AC1inf = ConfigText(default=_('AC in the living room'), visible_width=100, fixed_size=False)
config.plugins.MSNweatherNP.AC2 = ConfigSelection(choices=[('off', _('not installed')), ('daikin', _('Daikin Air Conditioner')), ('samsung', _('Samsung Air Conditioner'))], default='off')
config.plugins.MSNweatherNP.AC2_IP = ConfigIP(default=[0, 0, 0, 0])
config.plugins.MSNweatherNP.AC2_PORT = ConfigInteger(default=80, limits=(80, 999))
config.plugins.MSNweatherNP.AC2inf = ConfigText(default=_('AC in the bedroom'), visible_width=100, fixed_size=False)

config.plugins.MSNweatherNP.solarType = ConfigSelection(default= readCFG('solarType'), choices=[('solaredge', 'solaredge'), ('off', _('not installed'))])
config.plugins.MSNweatherNP.solarID = ConfigText(default= readCFG('solarID'), visible_width=100, fixed_size=False)
config.plugins.MSNweatherNP.solarAPIKEY = ConfigPassword(default= readCFG('solarAPIKEY'), visible_width=100, fixed_size=False)

config.plugins.MSNweatherNP.DebugEnabled = ConfigEnableDisable(default=False)
config.plugins.MSNweatherNP.DebugSize = ConfigSelection(choices=[('10000', '10KB'), ('100000', '100KB'), ('1000000', '1MB')], default='100000')
config.plugins.MSNweatherNP.HistoryPeriod = ConfigSelection(choices=[('86400', _('Last 24h')), ('43200', _('Last 12h')), ('21600', _('Last 6h')),
                                                                     ('10800', _('Last 3h')), ('3600', _('Last hour'))], default= readCFG('HistoryPeriod'))

config.plugins.MSNweatherNP.tmpFolder = NoSave(ConfigText(default='/tmp/.MSNdata'))

choicesList = None #cleanup
initConfig() #init entries

try:
    from Plugins.Extensions.MSNweather.updater import weathermsn
    WeatherMSNComp = weathermsn
except Exception as e:
    WeatherMSNComp = None
    printDEBUG('Exception: %s' % str(e))

def main(session, **kwargs):
    clearLogs()
    printDEBUG('INIT', ' MSNweather NP plugin %s' % Version)
    printDEBUG('config.plugins.MSNweatherNP.IconsType = "%s"' % config.plugins.MSNweatherNP.IconsType.value)
    import Plugins.Extensions.MSNweather.MSNweatherNP
    reload(Plugins.Extensions.MSNweather.MSNweatherNP)
    session.open(Plugins.Extensions.MSNweather.MSNweatherNP.MSNweatherNP)


def sessionstart(session, **kwargs):
    session.screen['MSNweatherNP'] = getWeather()


def Plugins(**kwargs):
    list = [
     PluginDescriptor(name=_('MSN weather NP'), where=[PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU], icon='weather.png', fnc=main),
     PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionstart)]
    return list
