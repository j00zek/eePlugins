# -*- coding: utf-8 -*-
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from . import _
from Plugins.Extensions.MSNweather.version import Version

from Components.config import config
from enigma import eEnv, eConsoleAppContainer
from Tools.Directories import resolveFilename, SCOPE_SKIN
from twisted.internet import defer
from twisted.web.client import getPage, downloadPage
from xml.etree.cElementTree import fromstring as cet_fromstring
import json, os, time, sys

PyMajorVersion = sys.version_info.major

class WeatherIconItem:
    def __init__(self, url='', filename='', index=-1, error=False):
        self.url = url
        self.filename = filename
        self.index = index
        self.error = error

class MSNWeatherItem:
    def __init__(self):
        self.temperature = ''
        self.skytext = ''
        self.humidity = ''
        self.winddisplay = ''
        self.observationtime = ''
        self.observationpoint = ''
        self.feelslike = ''
        self.skycode = ''
        self.date = ''
        self.day = ''
        self.low = ''
        self.high = ''
        self.skytextday = ''
        self.skycodeday = ''
        self.shortday = ''
        self.iconFilename = ''
        self.code = ''
        self.rainprecip = ''
        self.ForecaCity = ''
        self.dictWeather = {}


class getWeather:
    ERROR = 0
    OK = 1

    def __init__(self):
        paths = (
         os.path.dirname(resolveFilename(SCOPE_SKIN, config.skin.primary_skin.value)) + '/weather_icons/',
         '/etc/enigma2/weather_icons/',
         eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/MSNweather/icons/'))
        self.iconextension = '.png'
        for path in paths:
            if os.path.exists(path):
                self.iconpath = path
                break

        self.initialize(True)

    def EXCEPTIONDEBUG(self, myFUNC='', myText=''):
        from Plugins.Extensions.MSNweather.debug import printDEBUG
        printDEBUG(myFUNC, myText, 'getWeather.log')

    def GetAsyncWebDataDEBUG(self, myFUNC='', myText=''):
        if config.plugins.MSNweatherNP.DebugEnabled.value == True:
            from Plugins.Extensions.MSNweather.debug import printDEBUG
            printDEBUG(myFUNC, myText, 'GetAsyncWebData.log')
        elif os.path.exists('/tmp/.MSNdata/GetAsyncWebData.log'):
            os.remove('/tmp/.MSNdata/GetAsyncWebData.log')

    def DEBUG(self, myFUNC='', myText=''):
        if config.plugins.MSNweatherNP.DebugEnabled.value == True:
            from Plugins.Extensions.MSNweather.debug import printDEBUG
            printDEBUG(myFUNC, myText, 'getWeather.log')

    def initialize(self, full=False):
        self.city = ''
        self.degreetype = ''
        self.url = ''
        self.weatherItems = {}
        self.thingSpeakItems = {}
        self.dictWeather = {}
        self.callback = None
        self.callbackShowIcon = None
        self.callbackAllIconsDownloaded = None
        self.WebCurrentItems = {}
        self.WebhourlyItems = {}
        self.WebDailyItems = {}
        self.collectDataForHistogram = False
        self.GetAsyncWebData = eConsoleAppContainer()
        self.GetAsyncWebData.appClosed.append(self.GetAsyncWebDataClosed)
        self.GetAsyncWebData.dataAvail.append(self.GetAsyncWebDataAvail)
        return

    def cancel(self):
        self.DEBUG('cancel', '>>>')
        self.callback = None
        self.callbackShowIcon = None
        return

    def returnDict(self, dictName):
        self.DEBUG('getWeather().returnDict(dictName=%s)' % dictName, '>>>')
        if dictName is None:
            return {}
        else:
            if dictName == 'weatherItems':
                return self.weatherItems
            else:
                if dictName == 'thingSpeakItems':
                    self.DEBUG('\t', 'len(thingSpeakItems)=%s' % len(self.thingSpeakItems))
                    return self.thingSpeakItems
                if dictName == 'WebCurrentItems':
                    return self.WebCurrentItems
                if dictName == 'WebhourlyItems':
                    return self.WebhourlyItems
                if dictName == 'WebDailyItems':
                    return self.WebDailyItems
                return {}

            return

    def getDefaultWeatherData(self, callback=None, callbackAllIconsDownloaded=None):
        self.DEBUG('getWeather().getDefaultWeatherData()')
        self.initialize()
        weatherPluginEntryCount = int(config.plugins.MSNweatherNP.entrycount.value)
        if weatherPluginEntryCount >= 1:
            self.DEBUG('if weatherPluginEntryCount >= 1:')
            weatherPluginEntry = config.plugins.MSNweatherNP.Entry[0]
            self.getWeatherDataProc(weatherPluginEntry, callback, None, callbackAllIconsDownloaded, Histogram=True)
            return 1
        else:
            return 0

    def getWeatherData(self, weatherPluginEntry, callback, callbackShowIcon, callbackAllIconsDownloaded=None, Histogram=False):
        self.getWeatherDataProc(weatherPluginEntry, callback, callbackShowIcon, callbackAllIconsDownloaded, Histogram)

    def getWeatherDataProc(self, weatherPluginEntry, callback, callbackShowIcon, callbackAllIconsDownloaded=None, Histogram=False):
        self.DEBUG('getWeather().getWeatherDataProc', '>>>')
        if weatherPluginEntry.weatherSearchFullName.value == '':
            self.DEBUG('', 'END due to weatherSearchFullName = ""')
            return
        self.initialize()
        self.collectDataForHistogram = Histogram
        language = config.osd.language.value.replace('_', '-')
        if language == 'en-EN':
            language = 'en-US'
        elif language == 'no-NO':
            language = 'nn-NO'
        elif language == 'lt-LT':
            language = 'en-xl'
        self.city = weatherPluginEntry.city.value
        self.callback = callback
        self.callbackShowIcon = callbackShowIcon
        self.callbackAllIconsDownloaded = callbackAllIconsDownloaded
        params = [
         "VersionMSN='%s'" % Version,
         "tmpFolder='%s'" % config.plugins.MSNweatherNP.tmpFolder.value,
         "Histogram='%s'" % Histogram,
         "language='%s'" % language,
         "iconExtension='%s'" % self.iconextension,
         "iconPath='%s'" % self.iconpath,
         "pluginPath='%s'" % '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather',
         "msnAPIKEY='%s'" % config.plugins.MSNweatherNP.msnAPIKEY.value,
         "airlyAPIKEY='%s'" % config.plugins.MSNweatherNP.airlyAPIKEY.value,
         "BuildHistograms='%s'" % config.plugins.MSNweatherNP.BuildHistograms.value,
         "DEBUG='%s'" % config.plugins.MSNweatherNP.DebugEnabled.value,
         "HistoryPeriod='%s'" % config.plugins.MSNweatherNP.HistoryPeriod.value,
         "IconsType='%s'" % config.plugins.MSNweatherNP.IconsType.value,
         "hIconsType='%s'" % config.plugins.MSNweatherNP.hIconsType.value,
         "SensorsPriority='%s'" % config.plugins.MSNweatherNP.SensorsPriority.value,
         "currEntryID='%s'" % config.plugins.MSNweatherNP.currEntry.value,
         "airBleboxID='%s'" % weatherPluginEntry.bleboxID.value,
         "airGiosID='%s'" % weatherPluginEntry.giosID.value,
         "airLooko2ID='%s'" % weatherPluginEntry.looko2ID.value,
         "airlyID='%s'" % weatherPluginEntry.airlyID.value,
         "airOpenSenseID='%s'" % weatherPluginEntry.openSenseID.value,
         "airSmogTokID='%s'" % weatherPluginEntry.smogTokID.value,
         "airThingSpeakChannelID='%s'" % weatherPluginEntry.thingSpeakChannelID.value,
         "city='%s'" % weatherPluginEntry.city.value,
         "degreetype='%s'" % weatherPluginEntry.degreetype.value,
         "entryType='%s'" % weatherPluginEntry.entryType.value,
         "Fcity='%s'" % weatherPluginEntry.Fcity.value,
         "Fmeteo='%s'" % weatherPluginEntry.Fmeteo.value,
         "FmeteoRainPrecip='%s'" % weatherPluginEntry.FmeteoRainPrecip.value,
         "geolatitude='%s'" % weatherPluginEntry.geolatitude.value,
         "geolongitude='%s'" % weatherPluginEntry.geolongitude.value,
         "locationcode='%s'" % weatherPluginEntry.weatherlocationcode.value,
         "weatherSearchFullName='%s'" % weatherPluginEntry.weatherSearchFullName.value,
         "mainEntryID='%s'" % weatherPluginEntry.mainEntryID.value,
         "mainEntryADDR='%s'" % '%s.%s.%s.%s' % (weatherPluginEntry.mainEntryADDR.value[0],
          weatherPluginEntry.mainEntryADDR.value[1],
          weatherPluginEntry.mainEntryADDR.value[2],
          weatherPluginEntry.mainEntryADDR.value[3]),
         "mainEntryPASS='%s'" % weatherPluginEntry.mainEntryPASS.value,
         "mainEntryUSER='%s'" % weatherPluginEntry.mainEntryUSER.value]
        self.GetAsyncWebDataDEBUG('INIT', '.GetAsyncWebData.execute >>>')
        self.DEBUG('getWeather().getWeatherDataProc', 'execute GetAsyncWebData >>>')
        if PyMajorVersion == 2:
            if weatherPluginEntry.weatherSearchFullName.value != '':
                #with open('/proc/sys/vm/drop_caches', 'w') as (f):
                #    f.write('1\n')
                #if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/MSNcomponents/GetAsyncWebDataNP.py'):
                #    os.system("cd /usr/lib/enigma2/python/Plugins/Extensions/MSNweather/MSNcomponents;nice -n 10 /usr/bin/python -c 'import GetAsyncWebDataNP'")
                self.GetAsyncWebData.execute('nice -n 10 /usr/bin/python /usr/lib/enigma2/python/Plugins/Extensions/MSNweather/MSNcomponents/GetAsyncWebDataNP.py %s' % (' ').join(params))
                if os.path.exists('/j00zek'):
                    #open('/tmp/.MSNdata/testCMD.sh', 'w').write("cd /usr/lib/enigma2/python/Plugins/Extensions/MSNweather/MSNcomponents;nice -n 10 /usr/bin/python -c 'import GetAsyncWebDataNP'\n")
                    open('/tmp/.MSNdata/testCMD.sh', 'w').write('rm -f /tmp/.MSNdata/dictWeather_%s.json > /dev/null\n' % config.plugins.MSNweatherNP.currEntry.value)
                    open('/tmp/.MSNdata/testCMD.sh', 'a').write('/usr/bin/python /usr/lib/enigma2/python/Plugins/Extensions/MSNweather/MSNcomponents/GetAsyncWebDataNP.py %s' % (' ').join(params))
                    mode = os.stat('/tmp/.MSNdata/testCMD.sh').st_mode
                    mode |= (mode & 292) >> 2
                    os.chmod('/tmp/.MSNdata/testCMD.sh', mode)
        else: #py3
            if weatherPluginEntry.weatherSearchFullName.value != '':
                self.GetAsyncWebData.execute('nice -n 10 /usr/bin/python /usr/lib/enigma2/python/Plugins/Extensions/MSNweather/MSNcomponents/GetAsyncWebDataNP.py %s' % (' ').join(params))
                if os.path.exists('/j00zek'):
                    open('/tmp/.MSNdata/testCMD.sh', 'w').write('rm -f /tmp/.MSNdata/dictWeather_%s.json > /dev/null\n' % config.plugins.MSNweatherNP.currEntry.value)
                    open('/tmp/.MSNdata/testCMD.sh', 'a').write('/usr/bin/python /usr/lib/enigma2/python/Plugins/Extensions/MSNweather/MSNcomponents/GetAsyncWebDataNP.py %s' % (' ').join(params))
                    mode = os.stat('/tmp/.MSNdata/testCMD.sh').st_mode
                    mode |= (mode & 292) >> 2
                    os.chmod('/tmp/.MSNdata/testCMD.sh', mode)
          
        
    def GetAsyncWebDataAvail(self, text):
        self.GetAsyncWebDataDEBUG('GetAsyncWebDataAvail ', text)
        self.DEBUG('MSNWeather().GetAsyncWebDataAvail()', ' ')

    def GetAsyncWebDataClosed(self, retval):
        self.DEBUG('GetAsyncWebDataClosed(retval = %s)' % retval)
        testDictInfo = ''

        def getJSONdata(fileName):
            try:
                if PyMajorVersion == 2:
                    with open('/tmp/.MSNdata/%s' % fileName, 'r') as (json_file):
                        data = json_file.read().decode('utf-8')
                        json_file.close()
                        retDict = json.loads(data)
                else:
                    with open('/tmp/.MSNdata/%s' % fileName, 'r') as (json_file):
                        retDict = json.load(json_file)
                        json_file.close()
            except Exception as e:
                retDict = {}
                self.EXCEPTIONDEBUG('getWeather().getJSONdata(%s) >>> %s' % (fileName, str(e)))

            return retDict

        def getKeyValue(myKey, KeyValue, defVal):
            if PyMajorVersion == 2:
                return dictWeather.get('currentData', {}).get(myKey, {}).get(KeyValue, defVal).encode('utf-8', 'ignore')
            else:
                return dictWeather.get('currentData', {}).get(myKey, {}).get(KeyValue, defVal)

        dictWeather = getJSONdata('dictWeather_%s.json' % config.plugins.MSNweatherNP.currEntry.value)
        currentWeather = MSNWeatherItem()
        if len(dictWeather) > 0:
            try:
                currentWeather.dictWeather = dictWeather
                currentWeather.temperature = str(getKeyValue('temperature', 'val', '?'))
                currentWeather.skytext = str(getKeyValue('skytext', 'val', ''))
                currentWeather.humidity = str(getKeyValue('humidity', 'val', ''))
                currentWeather.winddisplay = str(getKeyValue('wind_speed', 'val', ''))
                currentWeather.observationtime = str(getKeyValue('observationtime', 'time', ''))
                currentWeather.observationpoint = testDictInfo + str(getKeyValue('observationpoint', 'val', ''))
                currentWeather.feelslike = str(getKeyValue('feelslike', 'val', ''))
                currentWeather.skycode = str(getKeyValue('skycode', 'val', ''))
                currentWeather.code = str(getKeyValue('code', 'val', ''))
                currentWeather.iconFilename = str(getKeyValue('iconfilename', 'val', 'fakePNG'))
                if os.path.exists(currentWeather.iconFilename) and self.callbackShowIcon is not None:
                    self.callbackShowIcon(index, currentWeather.iconFilename)
            except Exception as e:
                self.EXCEPTIONDEBUG('GetAsyncWebDataClosed.EXCEPTION ', str(e))

            self.weatherItems[str(-1)] = currentWeather
            if self.callbackAllIconsDownloaded is not None:
                self.callbackAllIconsDownloaded()
            remaining = dictWeather.get('currentData', {}).get('airlyLimitsDailyRemaining', '')
            limit = dictWeather.get('currentData', {}).get('airlyLimitsDaily', '')
            if remaining != '' and limit != '':
                config.plugins.MSNweatherNP.airlyLimits.value = '(%s/%s)' % (remaining, limit)
            else:
                config.plugins.MSNweatherNP.airlyLimits.value = ''
            config.plugins.MSNweatherNP.callbacksCount.value += 1
        if self.callback is not None:
            self.DEBUG('MSNWeather().webCallback() invoking callback')
            self.callback(self.OK, None)
        return