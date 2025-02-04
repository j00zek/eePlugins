# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Components.config import *
import gettext, os
from shutil import move
PLUGIN_PATH = resolveFilename(SCOPE_PLUGINS, 'Extensions/DGWeather')
PluginLanguageDomain = 'DGWeather'

def localeInit():
    gettext.bindtextdomain(PluginLanguageDomain, PLUGIN_PATH + '/locale')


def _(txt):
    if gettext.dgettext(PluginLanguageDomain, txt):
        return gettext.dgettext(PluginLanguageDomain, txt)
    else:
        return gettext.gettext(txt)

if localeInit() is not None:
    language.addCallback(localeInit())

#inicjalizacja plikow konfiguracyjne
if not os.path.exists('/etc/enigma2/DGWeather'):
    os.mkdir('/etc/enigma2/DGWeather')
    for cfgFile in ['VisualWeather_apikey','VisualWeather_city','OpenWeathermap_apikey','OpenWeathermap_idcity','Airly_apikey','Airly_id', 'geolatitude', 'geolongitude', 'geoLocationName']:
        if not os.path.exists("/etc/enigma2/DGWeather/%s" % cfgFile):
            open("/etc/enigma2/DGWeather/%s" % cfgFile, "w").write('')

#instalacja konwertera i rendererow
#cmds=[]
#for mycomp in ['Converter/DGWeather2.py', 'Renderer/darkAnimatedMoon.py', 'Renderer/darkAnimatedWeather.py', 'Renderer/darkAirlyPicon.py']:
#    destPath = '/usr/lib/enigma2/python/Components/%s' % mycomp
#    if not os.path.exists(destPath) or not os.path.islink(destPath):
#        cmds.append('ln -sf /usr/lib/enigma2/python/Plugins/Extensions/DGWeather/components/%s %s' % (mycomp.split('/')[1], destPath))
#if len(cmds) > 0:
#    os.system('\n'.join(cmds))

#Wszystkie ustawienia w jednym miejscu
config.plugins.dgWeather = ConfigSubsection()

config.plugins.dgWeather.tempUnit = ConfigSelection(default='Celsius', choices=[('Celsius', _('Celsius')), ('Fahrenheit', _('Fahrenheit'))])
config.plugins.dgWeather.windspeedUnit = ConfigSelection(default='km/h', choices=[('km/h', _(' km/h')), ('m/s', _(' m/s')), ('mp/h', _(' mp/h')), ('ft/s', _(' ft/s'))])
config.plugins.dgWeather.winddirection = ConfigSelection(default='long', choices=[('long', _('Long')), ('short', _('Short'))])
if config.osd.language.value == "pl_PL":
    defVal = 'pl'
else:
    defVal = 'en'
config.plugins.dgWeather.CountryCode = ConfigSelection(default=defVal, choices=[('de', _('German')), ('ru', _('Russian')), ('en', _('English')), ('zh', _('Chines')), ('pl', _('Polish'))])
config.plugins.dgWeather.refreshInterval = ConfigNumber(default=60)
config.plugins.dgWeather.numbers = ConfigSelection(default='1', choices=['0', '1', '2'])
config.plugins.dgWeather.Provider = ConfigSelection(default='VisualWeather', choices=['VisualWeather', 'OpenWeathermap','WeatherBit'])

config.plugins.dgWeather.pressureUnit = ConfigSelection(default='mmHg', choices=[('mmHg', _(' mmHg')), ('mBar', _(' mBar')), ('hPa', _(' hPa'))])
config.plugins.dgWeather.WeekDay = ConfigSelection(default='dm', choices=[('dm', _('d.m.')), ('dmy', _('d.m.y.'))])
config.plugins.dgWeather.animatedWeather = ConfigSelection(default='static', choices=[('static', _('Static')), ('animated', _('Animated'))])
config.plugins.dgWeather.StartScreen = ConfigSelection(default='cfg', choices=[('cfg', _('Setup')), ('cst', _('Weather'))])

defVal = open('/etc/enigma2/DGWeather/geolatitude', 'r').read().strip()
config.plugins.dgWeather.geolatitude = ConfigText(default=defVal)
defVal = open('/etc/enigma2/DGWeather/geolongitude', 'r').read().strip()
config.plugins.dgWeather.geolongitude = ConfigText(default=defVal)
defVal = open('/etc/enigma2/DGWeather/geoLocationName', 'r').read().strip()
config.plugins.dgWeather.geoLocationName = ConfigText(default=defVal)

#konfiguracja dla serwisu VisualWeather
defVal = open('/etc/enigma2/DGWeather/VisualWeather_apikey', 'r').read().strip()
config.plugins.dgWeather.VisualWeather_apikey = ConfigText(default=defVal)

#konfiguracja dla serwisu OpenWeathermap
defVal = open('/etc/enigma2/DGWeather/OpenWeathermap_apikey', 'r').read().strip()
config.plugins.dgWeather.OpenWeathermap_apikey = ConfigText(default=defVal)
defVal = open('/etc/enigma2/DGWeather/OpenWeathermap_idcity', 'r').read().strip()
config.plugins.dgWeather.OpenWeathermap_idcity = ConfigText(default=defVal, fixed_size = False)

#konfiguracja dla serwisu WeatherBit
defVal = open('/etc/enigma2/DGWeather/WeatherBit_apikey', 'r').read().strip()
config.plugins.dgWeather.WeatherBit_apikey = ConfigText(default=defVal)

#konfiguracja dla serwisu Airly
if os.path.exists('/etc/enigma2/Airly/api.txt'): defVal = open('/etc/enigma2/Airly/api.txt', 'r').readline().strip()
else: defVal = open('/etc/enigma2/DGWeather/Airly_apikey', 'r').read().strip()

config.plugins.dgWeather.airlyAPIKEY = ConfigText(default=defVal, fixed_size = False)
defVal = open('/etc/enigma2/DGWeather/Airly_id', 'r').read().strip()
config.plugins.dgWeather.airlyID = ConfigText(default=defVal, fixed_size = False)
