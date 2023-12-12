# -*- coding: utf-8 -*-
from Components.Language import language
from Components.config import config
from Tools.Directories import *
from enigma import eTimer
from time import time, localtime, mktime, strftime, sleep, strptime
from datetime import timedelta, datetime
from math import pi, cos
import datetime
import gettext
import io
import json
import os

from Plugins.Extensions.DGWeather.__init__ import _
from Plugins.Extensions.DGWeather.components.utils import *
from Plugins.Extensions.DGWeather.components.getAirly import getAirlyDict
from Plugins.Extensions.DGWeather.components.getGeoInfo import getGeoInfo
from Plugins.Extensions.DGWeather.components.getVisualWeather import getVisualCrossingDict
from Plugins.Extensions.DGWeather.components.getOpenWeather import OpenWeatherDict

dsunits = 'si'

weather_data = None

class WeatherData:
    def __init__(self):
        self.numbers = '.%sf' % str(config.plugins.dgWeather.numbers.value)
        #pewne dane sa niezmienne bez sensu jest je odswierzac.
        getGeoInfo(config.plugins.dgWeather.geolatitude.value, config.plugins.dgWeather.geolongitude.value)
        addressDict = LoadJsonDict('GeoInfo.json').get('address',{})
        
        if config.plugins.dgWeather.geolatitude.value == '': latVal = 0
        else: latVal = config.plugins.dgWeather.geolatitude.value
        
        if config.plugins.dgWeather.geolongitude.value == '': latVal = 0
        else: longVal = config.plugins.dgWeather.geolongitude.value
        
        self.WeatherInfo = WeatherInfo = {
            'W-Info': ' ',
            'W-Info-h': ' ',
            'timezone': _('N/A'),
            'alerts': _('N/A'),
            'windChill': _('N/A'),
            'windDirection': _('N/A'),
            'atmoHumidity': _('N/A'),
            'dewPoint': _('N/A'),
            'atmoVisibility': _('N/A'),
            'astroSunrise': _('N/A'),
            'astroSunset': _('N/A'),
            'astroDaySoltice': _('N/A'),
            'astroDayLength': _('N/A'),
            'uvIndex': _('N/A'),
            'geoData':              '%s / %s' % (format(float(latVal), '.4f') , format(float(longVal), '.4f')),
            'geoLat':               format(float(latVal), '.4f'),
            'geoLong':              format(float(longVal), '.4f'),
            'downloadDate': _('N/A'),
            'downloadTime': _('N/A'),
            'currentCountry':       addressDict.get('country', _('N/A')),
            'currentWeatherCode': '(',
            'currentPressure': _('N/A'),
            'currentlywindSpeed': _('N/A'),
            'currentlywindGust': _('N/A'),
            'currentLocation':      addressDict.get('city', _('N/A')),
            'currentRegion':        addressDict.get('state', _('N/A')),
            'currentWeatherText': _('N/A'),
            'currentWeatherTemp': '0',
            'currentWeatherPicon': '3200',
            'currentProbability': _('N/A'),
            'currentPrecip': _('N/A'),
            'currentlyIntensity': _('N/A'),
            'currentOzoneText': _('N/A'),
            'currentcloudCover': '0',
            'currentMoonPicon': '3200',
            'currentMoonPhase': '',
            'forecastTodayPressure': '',
            'forecastTodayCode': '(',
            'forecastTodayDay': '',
            'forecastTodayDate': '',
            'forecastTodayTempMin': '',
            'forecastTodayTempMax': '',
            'forecastTodayText': '',
            'forecastTodayPicon': '3200',
            'forecastTodaywindSpeed': '',
            'forecastTodaywindGust': '',
            'forecastTodaymoonPhase': '',
            'forecastTodayProbability': '',
            'forecastTodayIntensity': '',
            'forecastTodaycloudCover': '',
            'forecastTodayHumidity': '',
            'forecastTomorrowPressure': '',
            'forecastTomorrowCode': '(',
            'forecastTomorrowDay': '',
            'forecastTomorrowDate': '',
            'forecastTomorrowTempMin': '',
            'forecastTomorrowTempMax': '',
            'forecastTomorrowText': '',
            'forecastTomorrowPicon': '3200',
            'forecastTomorrowwindSpeed': '',
            'forecastTomorrowwindGust': '',
            'forecastTomorrowmoonPhase': '',
            'forecastTomorrowProbability': '',
            'forecastTomorrowIntensity': '',
            'forecastTomorrowcloudCover': '',
            'forecastTomorrowHumidity': '',
            'forecastTomorrow1Pressure': '',
            'forecastTomorrow1Code': '(',
            'forecastTomorrow1Day': '',
            'forecastTomorrow1Date': '',
            'forecastTomorrow1TempMin': '',
            'forecastTomorrow1TempMax': '',
            'forecastTomorrow1Text': '',
            'forecastTomorrow1Picon': '3200',
            'forecastTomorrow1windSpeed': '',
            'forecastTomorrow1windGust': '',
            'forecastTomorrow1moonPhase': '',
            'forecastTomorrow1Probability': '',
            'forecastTomorrow1Intensity': '',
            'forecastTomorrow1cloudCover': '',
            'forecastTomorrow1Humidity': '',
            'forecastTomorrow2Pressure': '',
            'forecastTomorrow2Code': '(',
            'forecastTomorrow2Day': '',
            'forecastTomorrow2Date': '',
            'forecastTomorrow2TempMin': '',
            'forecastTomorrow2TempMax': '',
            'forecastTomorrow2Text': '',
            'forecastTomorrow2Picon': '3200',
            'forecastTomorrow2windSpeed': '',
            'forecastTomorrow2windGust': '',
            'forecastTomorrow2moonPhase': '',
            'forecastTomorrow2Probability': '',
            'forecastTomorrow2Intensity': '',
            'forecastTomorrow2cloudCover': '',
            'forecastTomorrow2Humidity': '',
            'forecastTomorrow3Pressure': '',
            'forecastTomorrow3Code': '(',
            'forecastTomorrow3Day': '',
            'forecastTomorrow3Date': '',
            'forecastTomorrow3TempMin': '',
            'forecastTomorrow3TempMax': '',
            'forecastTomorrow3Text': '',
            'forecastTomorrow3Picon': '3200',
            'forecastTomorrow3windSpeed': '',
            'forecastTomorrow3windGust': '',
            'forecastTomorrow3moonPhase': '',
            'forecastTomorrow3Probability': '',
            'forecastTomorrow3Intensity': '',
            'forecastTomorrow3cloudCover': '',
            'forecastTomorrow3Humidity': '',
            'forecastTomorrow4Pressure': '',
            'forecastTomorrow4Code': '(',
            'forecastTomorrow4Day': '',
            'forecastTomorrow4Date': '',
            'forecastTomorrow4TempMin': '',
            'forecastTomorrow4TempMax': '',
            'forecastTomorrow4Text': '',
            'forecastTomorrow4Picon': '3200',
            'forecastTomorrow4windSpeed': '',
            'forecastTomorrow4windGust': '',
            'forecastTomorrow4moonPhase': '',
            'forecastTomorrow4Probability': '',
            'forecastTomorrow4Intensity': '',
            'forecastTomorrow4cloudCover': '',
            'forecastTomorrow4Humidity': '',
            'forecastTomorrow5Pressure': '',
            'forecastTomorrow5Code': '(',
            'forecastTomorrow5Day': '',
            'forecastTomorrow5Date': '',
            'forecastTomorrow5TempMin': '',
            'forecastTomorrow5TempMax': '',
            'forecastTomorrow5Text': '',
            'forecastTomorrow5Picon': '3200',
            'forecastTomorrow5windSpeed': '',
            'forecastTomorrow5windGust': '',
            'forecastTomorrow5moonPhase': '',
            'forecastTomorrow5Probability': '',
            'forecastTomorrow5Intensity': '',
            'forecastTomorrow5cloudCover': '',
            'forecastTomorrow5Humidity': '',
            'forecastTomorrow6Pressure': '',
            'forecastTomorrow6Code': '(',
            'forecastTomorrow6Day': '',
            'forecastTomorrow6Date': '',
            'forecastTomorrow6TempMin': '',
            'forecastTomorrow6TempMax': '',
            'forecastTomorrow6Text': '',
            'forecastTomorrow6Picon': '3200',
            'forecastTomorrow6windSpeed': '',
            'forecastTomorrow6windGust': '',
            'forecastTomorrowmoonPhase': '',
            'forecastTomorrow6Probability': '',
            'forecastTomorrow6Intensity': '',
            'forecastTomorrow6cloudCover': '',
            'forecastTomorrow6Humidity': '',
            'forecastHourlyHour': _('N/A'),
            'forecastHourlyTemp': '0',
            'forecastHourlywindSpeed': _('N/A'),
            'forecastHourlyPressure': _('N/A'),
            'forecastHourlyHumidity': _('N/A'),
            'forecastHourlyText': _('N/A'),
            'forecastHourlyPicon': '3200',
            'forecastHourlyCloud': '0',
            'forecastHourlyIntensity': '0' + _(' mm/3h'),
            'forecastHourly1Hour': _('N/A'),
            'forecastHourly1Temp': '0',
            'forecastHourly1windSpeed': _('N/A'),
            'forecastHourly1Pressure': _('N/A'),
            'forecastHourly1Humidity': _('N/A'),
            'forecastHourly1Text': _('N/A'),
            'forecastHourly1Picon': '3200',
            'forecastHourly1Cloud': '0',
            'forecastHourly1Intensity': '0' + _(' mm/3h'),
            'forecastHourly2Hour': _('N/A'),
            'forecastHourly2Temp': '0',
            'forecastHourly2windSpeed': _('N/A'),
            'forecastHourly2Pressure': _('N/A'),
            'forecastHourly2Humidity': _('N/A'),
            'forecastHourly2Text': _('N/A'),
            'forecastHourly2Picon': '3200',
            'forecastHourly2Cloud': '0',
            'forecastHourly2Intensity': '0' + _(' mm/3h'),
            'forecastHourly3Hour': _('N/A'),
            'forecastHourly3Temp': '0',
            'forecastHourly3windSpeed': _('N/A'),
            'forecastHourly3Pressure': _('N/A'),
            'forecastHourly3Humidity': _('N/A'),
            'forecastHourly3Text': _('N/A'),
            'forecastHourly3Picon': '3200',
            'forecastHourly3Cloud': '0',
            'forecastHourly3Intensity': '0' + _(' mm/3h'),
            'forecastHourly4Hour': _('N/A'),
            'forecastHourly4Temp': '0',
            'forecastHourly4windSpeed': _('N/A'),
            'forecastHourly4Pressure': _('N/A'),
            'forecastHourly4Humidity': _('N/A'),
            'forecastHourly4Text': _('N/A'),
            'forecastHourly4Picon': '3200',
            'forecastHourly4Cloud': '0',
            'forecastHourly4Intensity': '0' + _(' mm/3h'),
            'forecastHourly5Hour': _('N/A'),
            'forecastHourly5Temp': '0',
            'forecastHourly5windSpeed': _('N/A'),
            'forecastHourly5Pressure': _('N/A'),
            'forecastHourly5Humidity': _('N/A'),
            'forecastHourly5Text': _('N/A'),
            'forecastHourly5Picon': '3200',
            'forecastHourly5Cloud': '0',
            'forecastHourly5Intensity': '0' + _(' mm/3h'),
            'forecastHourly6Hour': _('N/A'),
            'forecastHourly6Temp': '0',
            'forecastHourly6windSpeed': _('N/A'),
            'forecastHourly6Pressure': _('N/A'),
            'forecastHourly6Humidity': _('N/A'),
            'forecastHourly6Text': _('N/A'),
            'forecastHourly6Picon': '3200',
            'forecastHourly6Cloud': '0',
            'forecastHourly6Intensity': '0' + _(' mm/3h'),
            'forecastHourly7Hour': _('N/A'),
            'forecastHourly7Temp': '0',
            'forecastHourly7windSpeed': _('N/A'),
            'forecastHourly7Pressure': _('N/A'),
            'forecastHourly7Humidity': _('N/A'),
            'forecastHourly7Text': _('N/A'),
            'forecastHourly7Picon': '3200',
            'forecastHourly7Cloud': '0',
            'forecastHourly7Intensity': '0' + _(' mm/3h'),
            'forecastHourly8Hour': _('N/A'),
            'forecastHourly8Temp': '0',
            'forecastHourly8windSpeed': _('N/A'),
            'forecastHourly8Pressure': _('N/A'),
            'forecastHourly8Humidity': _('N/A'),
            'forecastHourly8Text': _('N/A'),
            'forecastHourly8Picon': '3200',
            'forecastHourly8Cloud': '0',
            'forecastHourly8Hour': _('N/A'),
            'forecastHourly8Temp': '0',
            'PiconMoon': '3200',
            'indexBackPNG': '',
            'caqi': '',
            'pm25': '',
            'pm10': '',
            'pm1': '',
            'ldesc': '',
            'pres': '',
          }
        if config.plugins.dgWeather.refreshInterval.value > 0:
            self.timer = eTimer()
            self.timer.callback.append(self.GetWeather)
    
    def GetWeather(self):
        timeout = config.plugins.dgWeather.refreshInterval.value * 1000 * 60
        if timeout > 0:
            if os.path.isfile(logFile) and os.stat(logFile).st_size >= 100000: #kasowanie tylko jak log wiekszy od 100KB
                os.remove(logFile)
                write_log('----- LOG ZA DUZY, SKROCONO -----')
            else:
                write_log('----- GetWeather() >>> -----')
            write_log('GetWeather() >>>')
            #inicjacja kolejnego odswierzenia
            self.timer.start(timeout, True)
            

            #jak brak koordynatow to nie ma co pobierac
            if config.plugins.dgWeather.geolatitude.value == '' or config.plugins.dgWeather.geolongitude.value == '':
                write_log('!!!!! BRAK geolatitude lub geolongitude !!!!!')
                return
            
            #pobieranie z VisualWeather
            if config.plugins.dgWeather.Provider.value == 'VisualWeather' and config.plugins.dgWeather.VisualWeather_apikey.value != '':
                write_log('WeatherData.GetWeather() VisualCrossingDict...')
                self.WeatherInfo.update(getVisualCrossingDict(config.plugins.dgWeather.VisualWeather_apikey.value,
                                                                            config.plugins.dgWeather.geolatitude.value,
                                                                            config.plugins.dgWeather.geolongitude.value,
                                                                            config.plugins.dgWeather.CountryCode.value
                                                                           )
                                        )
                
                #obliczenia faz ksiezyca
                moonData = self.moonphase(self.WeatherInfo['currentMoonPhase'])
                self.WeatherInfo['currentMoonPicon'] = moonData[1]
                self.WeatherInfo['PiconMoon'] = moonData[1]
                write_log('self.WeatherInfo[PiconMoon] = %s' % self.WeatherInfo['PiconMoon'])

                #dopasowanie WeatherInfo
                for key, value in self.WeatherInfo.items():
                    #write_log('%s = %s' %(key,value))
                    if key ==   'atmoVisibility':   self.WeatherInfo[key] = self.convert_km_miles(value)
                    elif key == 'astroDaySoltice':  self.WeatherInfo[key] = self.convertAstroSun(value)
                    elif key == 'dewPoint':         self.WeatherInfo[key] = self.convertTemperature(value)
                    elif key == 'downloadDate':     self.WeatherInfo[key] = strftime('%Y-%m-%d', localtime(value))
                    elif key == 'downloadTime':     self.WeatherInfo[key] = strftime('%H:%M:%S', localtime(value))
                    elif key == 'windChill':        self.WeatherInfo[key] = self.convertTemperature(value)
                    
                    elif key.endswith('Code'):      self.WeatherInfo[key] = self.ConvertIconCode(value)
                    elif key.endswith('Day'):       self.WeatherInfo[key] = self.convertCurrentDay(value)
                    elif key.endswith('Hour'):      self.WeatherInfo[key] = self.convertHMStoHM(value)
                    elif key.endswith('moonPhase'): self.WeatherInfo[key] = self.moonphase(value)[0]
                    elif key.endswith('Picon'):     self.WeatherInfo[key] = self.convertIconName(value)
                    elif key.endswith('Pressure'):  self.WeatherInfo[key] = self.convertPressure(value)
                    elif key.endswith('windGust'):  self.WeatherInfo[key] = self.convertwindSpeed(value)
                    elif key.endswith('windSpeed'): self.WeatherInfo[key] = self.convertwindSpeed(value)
                    elif key.endswith('Temp'):      self.WeatherInfo[key] = self.convertTemperature(value)
                
            #pobieranie z OpenWeathermap
            elif config.plugins.dgWeather.Provider.value == 'OpenWeathermap' and config.plugins.dgWeather.OpenWeathermap_apikey.value != '':
                write_log('WeatherData.GetWeather() OpenWeatherDict...')
                self.WeatherInfo.update(OpenWeatherDict(config.plugins.dgWeather.OpenWeathermap_apikey.value,
                                                       config.plugins.dgWeather.geolatitude.value,
                                                       config.plugins.dgWeather.geolongitude.value,
                                                       config.plugins.dgWeather.CountryCode.value
                                                      )
                                        )
                #dopasowanie WeatherInfo
                    
            
            #pobieranie z airly
            if config.plugins.dgWeather.airlyAPIKEY.value != '' and config.plugins.dgWeather.airlyID.value != '':
                write_log('DOWNLOAD airlyDict...')
                airlyDict = getAirlyDict(config.plugins.dgWeather.airlyAPIKEY.value, config.plugins.dgWeather.airlyID.value, config.plugins.dgWeather.CountryCode.value)
                try:
                    self.WeatherInfo['indexBackPNG'] = '/usr/lib/enigma2/python/Plugins/Extensions/DGWeather/AirlyIcons/%s.png' % str(airlyDict['data']['current']['indexes'][0]['level'])
                    self.WeatherInfo['caqi'] = str(int(float(airlyDict['data']['current']['indexes'][0]['value']) + 0.5))
                    self.WeatherInfo['ldesc'] = str(airlyDict['data']['current']['indexes'][0]['description'])
                    for item in airlyDict['data']['current']['values']:
                        iName = item['name']
                        iVal = str(int(float(item['value']) + 0.5))
                        if iName == 'PM25': self.WeatherInfo['pm25'] = 'PM2.5: %s µg/m3' % iVal
                        elif iName == 'PM10': self.WeatherInfo['pm10'] = 'PM10: %s µg/m3' % iVal
                        elif iName == 'PM1': self.WeatherInfo['pm1'] = 'PM1: %s µg/m3' % iVal
                        elif iName == 'PRESSURE': self.WeatherInfo['pres'] = '%s hPa' % iVal
                        #write_log('%s="%s"' % (iName,iVal))
                except Exception as e:
                    Exc_log('Exception loading airly dict: %s' % str(e))
            
            #zapisujemy wynikowy json do  przez konwerter
            saveJsonDict('WeatherInfoDict.json', self.WeatherInfo) # zeby wiedziec co jest dostepne
            write_log('GetWeather() <<<')
        return

    def returnWeatherDict(self):
        return self.WeatherInfo
#!!!!!!!!!!!!! UZYTE

    def convertHMStoHM(self, HMS):
        if HMS.startswith('0'): return HMS[1:len(HMS)-3]
        else: return HMS[:len(HMS)-3]

    def convertPressure(self, pressure):
        if config.plugins.dgWeather.pressureUnit.value == 'mmHg': return '%s mmHg' % format(pressure * 0.75, self.numbers)
        if config.plugins.dgWeather.pressureUnit.value == 'mBar': return '%s mBar' % format(pressure, self.numbers)
        if config.plugins.dgWeather.pressureUnit.value == 'hPa':  return '%s hPa'  % format(pressure, self.numbers)
        return str(pressure)

    def convert_km_miles(self, value):
        if config.plugins.dgWeather.windspeedUnit.value == 'mp/h': return _('%s miles') % format(float(value) * 0.62137, self.numbers)
        else: return _('%s km') % format(float(value), self.numbers)

    def convertwindSpeed(self, windSpeed):
        if config.plugins.dgWeather.windspeedUnit.value == 'm/s':
            windSpeed = format(windSpeed, self.numbers) + _(' m/s')
        if config.plugins.dgWeather.windspeedUnit.value == 'km/h':
            windSpeed = format(windSpeed * 3.6, self.numbers) + _(' km/h')
        if config.plugins.dgWeather.windspeedUnit.value == 'mp/h':
            windSpeed = format(windSpeed * 0.447, self.numbers) + _(' mp/h')
        if config.plugins.dgWeather.windspeedUnit.value == 'ft/s':
            windSpeed = format(windSpeed * 0.3048, self.numbers) + _(' ft/s')
        return str(windSpeed)

    def convertTemperature(self, temp):
        if config.plugins.dgWeather.tempUnit.value == 'Celsius': return '%s °C' % format(temp, self.numbers)
        elif config.plugins.dgWeather.tempUnit.value == 'Fahrenheit': return '%s °F' % format(temp * 1.8 + 32, self.numbers)
        else: return temp

    def convertCurrentDay(self, val):
        wdays = [_('Sunday'), _('Monday'), _('Tuesday'), _('Wednesday'), _('Thursday'), _('Friday'), _('Saturday')]
        swdays = [_('Sun'), _('Mon'), _('Tue'), _('Wed'), _('Thu'), _('Fri'), _('Sat')]
        value = wdays[int(datetime.datetime.fromtimestamp(int(val)).strftime('%w'))]
        write_log('GetWeather().convertCurrentDay(%s) = %s' % (val,value))
        return value

    def convertIconName(self, IconName):
        IconName = str(IconName)
        if IconName ==   'clear-day':   return '32'
        elif IconName == 'clear-night': return '31'
        elif IconName == 'cloudy':      return '26'
        elif IconName == 'fog':         return '20'
        elif IconName == 'partly-cloudy-day':   return '30'
        elif IconName == 'partly-cloudy-night': return '29'
        elif IconName == 'rain':  return '12'
        elif IconName == 'sleet': return '7'
        elif IconName == 'snow':  return '14'
        elif IconName == 'wind':  return '23'
        write_log('MISSING IconName: "%s"' % IconName)
        return '3200'
        
    def ConvertIconCode(self, IconName):
        if IconName == '01d':   return 'B'
        elif IconName == '02d': return 'H'
        elif IconName == '03d': return 'H'
        elif IconName == '04d': return 'N'
        elif IconName == '05d': return 'Q'
        elif IconName == '06d': return 'O'
        elif IconName == '07d': return 'U'
        elif IconName == '08d': return 'W'
        elif IconName == '09d': return 'X'
        elif IconName == '10d': return 'Q'
        elif IconName == '11d': return 'S'
        elif IconName == '12d': return 'X'
        elif IconName == '13d': return 'W'
        elif IconName == '14d': return 'O'
        elif IconName == '15d': return 'N'
        elif IconName == '20d': return 'E'
        elif IconName == '21d': return 'E'
        elif IconName == '22d': return 'Z'
        elif IconName == '23d': return 'T'
        elif IconName == '30d': return 'S'
        elif IconName == '31d': return 'S'
        elif IconName == '32d': return 'T'
        elif IconName == '33d': return 'W'
        elif IconName == '34d': return 'W'
        elif IconName == '40d': return 'H'
        elif IconName == '46d': return 'Q'
        elif IconName == '47d': return 'Q'
        elif IconName == '48d': return 'U'
        elif IconName == '49d': return 'T'
        elif IconName == '50d': return 'M'
        elif IconName == '01n': return 'C'
        elif IconName == '02n': return 'I'
        elif IconName == '03n': return 'I'
        elif IconName == '04n': return 'N'
        elif IconName == '05n': return 'O'
        elif IconName == '06n': return 'I'
        elif IconName == '07n': return 'U'
        elif IconName == '08n': return 'U'
        elif IconName == '09n': return 'Q'
        elif IconName == '10n': return 'U'
        elif IconName == '11n': return 'I'
        elif IconName == '13n': return 'U'
        elif IconName == '40n': return 'Q'
        elif IconName == '41n': return 'U'
        elif IconName == 'clear-day':   return 'B'
        elif IconName == 'clear-night': return 'C'
        elif IconName == 'cloudy': return 'H'
        elif IconName == 'fog':    return 'M'
        elif IconName == 'partly-cloudy-day':   return 'H'
        elif IconName == 'partly-cloudy-night': return 'I'
        elif IconName == 'rain':  return 'X'
        elif IconName == 'sleet': return 'W'
        elif IconName == 'snow':  return 'W'
        elif IconName == 'wind':  return 'F'
        return ')'

    def moonphase(self, phase = None):
        picon = ''
        ptext = ''
        if phase is None:
            syn_moon_month = 29.530589
            hist_fullmoon = (2018, 9, 25, 6, 1, 36, 0, 0, 1)
            moon_time = mktime(hist_fullmoon)
            hist_fullmoon_days = moon_time / 86400
            now_days = mktime(localtime()) / 86400
            days_since_hist_fullmoon = now_days - hist_fullmoon_days
            full_moons_since = days_since_hist_fullmoon / syn_moon_month
            phase = round(full_moons_since, 2)
            phase = phase - int(phase)
        if phase == 0:
            phase = 1
        if phase < 0.25:
            ptext = _('Waning gibbous')
        elif phase == 0.25:
            ptext = _('First Quarter Moon')
        elif 0.25 < phase < 0.5:
            ptext = _('Waning crescent')
        elif phase == 0.5:
            ptext = _('New moon')
        elif 0.5 < phase < 0.75:
            ptext = _('Waxing crescent')
        elif phase == 0.75:
            ptext = _('Waxing gibbous')
        elif 0.75 < phase < 0.98:
            ptext = _('Waxing gibbous')
        elif 0.98 <= phase <= 1:
            ptext = _('Full moon')
        hmoonA = float(pi / 2)
        if phase < 0.5:
            s = cos(phase * pi * 2)
            ellipse = s * 1 * pi
            hEllA = ellipse / 2
            illA = hmoonA + hEllA
        else:
            s = -cos(phase * pi * 2)
            ellipse = s * 1 * pi
            hEllA = ellipse / 2
            illA = hmoonA - hEllA
        illumperc = illA / pi * 100
        illumperc = round(illumperc, 1)
        if phase > 0 and illumperc > 95:
            picon = '095'
        elif phase > 0.07 and illumperc > 90:
            picon = '090'
        elif phase > 0.1 and illumperc > 85:
            picon = '085'
        elif phase > 0.12 and illumperc > 80:
            picon = '080'
        elif phase > 0.14 and illumperc > 75:
            picon = '075'
        elif phase > 0.16 and illumperc > 70:
            picon = '070'
        elif phase > 0.18 and illumperc > 65:
            picon = '065'
        elif phase > 0.2 and illumperc > 60:
            picon = '060'
        elif phase > 0.21 and illumperc > 55:
            picon = '055'
        elif phase > 0.23 and illumperc > 50:
            picon = '050'
        elif phase > 0.24 and illumperc > 45:
            picon = '045'
        elif phase > 0.26 and illumperc > 40:
            picon = '040'
        elif phase > 0.28 and illumperc > 35:
            picon = '035'
        elif phase > 0.29 and illumperc > 30:
            picon = '030'
        elif phase > 0.31 and illumperc > 25:
            picon = '025'
        elif phase > 0.33 and illumperc > 20:
            picon = '020'
        elif phase > 0.35 and illumperc > 15:
            picon = '015'
        elif phase > 0.37 and illumperc > 10:
            picon = '010'
        elif phase > 0.39 and illumperc > 5:
            picon = '05'
        elif phase > 0.42 and illumperc >= 0:
            picon = '1'
        elif phase > 0.5 and illumperc > 0:
            picon = '5'
        elif phase > 0.57 and illumperc > 5:
            picon = '10'
        elif phase > 0.6 and illumperc > 10:
            picon = '15'
        elif phase > 0.62 and illumperc > 15:
            picon = '20'
        elif phase > 0.64 and illumperc > 20:
            picon = '25'
        elif phase > 0.66 and illumperc > 25:
            picon = '30'
        elif phase > 0.68 and illumperc > 30:
            picon = '35'
        elif phase > 0.7 and illumperc > 35:
            picon = '40'
        elif phase > 0.71 and illumperc > 40:
            picon = '45'
        elif phase > 0.73 and illumperc > 45:
            picon = '50'
        elif phase > 0.75 and illumperc > 50:
            picon = '55'
        elif phase > 0.76 and illumperc > 55:
            picon = '60'
        elif phase > 0.78 and illumperc > 60:
            picon = '65'
        elif phase > 0.79 and illumperc > 65:
            picon = '70'
        elif phase > 0.81 and illumperc > 70:
            picon = '75'
        elif phase > 0.83 and illumperc > 75:
            picon = '80'
        elif phase > 0.85 and illumperc > 80:
            picon = '85'
        elif phase > 0.87 and illumperc > 85:
            picon = '90'
        elif phase > 0.89 and illumperc > 90:
            picon = '95'
        elif phase > 0.92 and illumperc > 95:
            picon = '100'
        return (ptext, picon)


#  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!DO SKASOWANIA
    def GotDGWeatherData(self, data = None):
        write_log('GotDGWeatherData >>>')
        #write_log('Data : ' + str(data))
        if data is not None:
            try:
                parsed_json = json.loads(data)
                #for k, v in parsed_json.items():
                #    write_log(str(k) + ':' + str(v))
            except Exception as ex:
                Exc_log('EXCEPTION parsowania json: ' + str(ex))
                write_log('Data : ' + str(data))
                return
                
            #current data
            try:
                CurrentDict = parsed_json.get('currently',{})

                write_log('\t assigning current data')
                self.WeatherInfo['timezone'] = _(str(parsed_json.get('timezone', '---')))
                if config.plugins.dgWeather.winddirection.value == 'short':
                    self.WeatherInfo['windDirection'] = str(self.ConvertDirectionShort(CurrentDict.get('windBearing','')))
                else:
                    self.WeatherInfo['windDirection'] = str(self.ConvertDirectionLong(CurrentDict.get('windBearing','')))
                self.WeatherInfo['atmoHumidity'] = format(float(CurrentDict.get('humidity',0)) * 100, '.0f') + ' %'
                    
                self.WeatherInfo['uvIndex'] = format(float(CurrentDict.get('uvIndex',0)), '.0f') + ' / 10'
                self.WeatherInfo['downloadDate'] = self.convertCurrentDate(CurrentDict.get('time',''))
                self.WeatherInfo['downloadTime'] = self.convertCurrentTime(CurrentDict.get('time',''))
                self.WeatherInfo['currentWeatherText'] = str(CurrentDict.get('summary',''))
                self.WeatherInfo['currentProbability'] = format(float(CurrentDict.get('precipProbability',0)) * 100, self.numbers) + ' %'
                self.WeatherInfo['currentcloudCover'] = format(float(CurrentDict.get('cloudCover',0)) * 100, self.numbers) + ' %'
                self.WeatherInfo['currentlyIntensity'] = format(float(CurrentDict.get('precipIntensity',0)), '.4f') + _(' mm/h')
                self.WeatherInfo['currentOzoneText'] = format(float(CurrentDict.get('ozone',0)), self.numbers) + _(' DU')
            except Exception as ex:
                Exc_log('EXCEPTION: ' + str(ex))

            #hourly data
            try:
                write_log('\t assigning hourly data')
                hourlyDict = parsed_json.get('hourly',{})
                self.WeatherInfo['W-Info-h'] = str(hourlyDict.get('summary','---'))
                hourly = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
                for hour in hourly:
                    ahour = int(hour) + 1
                    if hour == '0':
                        hour = ''
                    self.WeatherInfo['forecastHourly' + hour + 'Hour'] = self.convertAstroSun(hourlyDict['data'][ahour]['time'])
                    self.WeatherInfo['forecastHourly' + hour + 'Humidity'] = format(float(hourlyDict['data'][ahour]['humidity']) * 100, '.0f') + ' %'
                    self.WeatherInfo['forecastHourly' + hour + 'Cloud'] = format(float(hourlyDict['data'][ahour]['cloudCover']) * 100, self.numbers) + ' %'
                    self.WeatherInfo['forecastHourly' + hour + 'Text'] = self.convertWeatherText(hourlyDict['data'][ahour]['summary'])
            except Exception as ex:
                Exc_log('EXCEPTION: ' + str(ex))

            #daily data
            write_log('\t assigning forecastToday data')
            dailyDict = parsed_json.get('daily',{})
            dailyData = dailyDict.get('data',[{},{},{},{},{},{},{},{}])
            #write_log('dailyData:\n%s\n' % json.dumps(dailyData))
            dayDict = dailyData[0]
            try:
                self.WeatherInfo['W-Info'] = str(dailyDict.get('summary',''))
                if dayDict.get('sunriseTime',0) != 0 and dayDict.get('sunsetTime',0) != 0:
                    self.WeatherInfo['astroDayLength'] = self.convertAstroDayLength(float(dayDict['sunsetTime'] - dayDict['sunriseTime']) - 10800)
                    self.WeatherInfo['astroSunrise'] = self.convertAstroSun(dayDict['sunriseTime'])
                    self.WeatherInfo['astroSunset'] = self.convertAstroSun(dayDict['sunsetTime'])
                    self.WeatherInfo['astroDaySoltice'] = self.convertAstroSun(float(dayDict['sunsetTime'] + dayDict['sunriseTime']) * 0.5)
            except Exception as ex:
                Exc_log('EXCEPTION in astroDay...: ' + str(ex))
                write_log('dayDict:\n%s\n' % json.dumps(dayDict))
            try:
                if not dayDict.get('summary', None) is None: self.WeatherInfo['forecastTodayText'] = self.convertWeatherText(dayDict['summary'])
                if not dayDict.get('precipProbability', None) is None: self.WeatherInfo['forecastTodayProbability'] = format(float(dayDict['precipProbability']) * 100, self.numbers) + ' %'
                if not dayDict.get('cloudCover', None) is None: self.WeatherInfo['forecastTodaycloudCover'] = format(float(dayDict['cloudCover']) * 100, self.numbers) + ' %'
                if not dayDict.get('precipIntensity', None) is None: self.WeatherInfo['forecastTodayIntensity'] = format(float(dayDict['precipIntensity']), self.numbers) + _(' mm')
                if not dayDict.get('ozone', None) is None: self.WeatherInfo['forecastTodayOzoneText'] = format(float(dayDict['ozone']), self.numbers) + _(' DU')
                if not dayDict.get('moonPhase', None) is None: self.WeatherInfo['PiconMoon'] = self.convertPiconMoon(float(dayDict['moonPhase']))
            except Exception as ex:
                Exc_log('EXCEPTION in forecastToday: ' + str(ex))
                write_log('dayDict:\n%s\n' % json.dumps(dayDict))
                
            write_log('\t assigning forecastTomorrow data')
            try:
                days = ['0', '1', '2', '3', '4', '5', '6']
                for day in days:
                    aday = int(day) + 1
                    dayDict = dailyData[aday]
                    if day == '0':
                        day = ''
                    if not dayDict.get('time', None) is None: self.WeatherInfo['forecastTomorrow' + day + 'Date'] = self.convertCurrentDate(dayDict['time'])
                    if not dayDict.get('summary', None) is None: self.WeatherInfo['forecastTomorrow' + day + 'Text'] = self.convertWeatherText(dayDict['summary'])
                    if not dayDict.get('precipProbability', None) is None: self.WeatherInfo['forecastTomorrow' + day + 'Probability'] = format(float(dayDict['precipProbability']) * 100, self.numbers) + ' %'
                    if not dayDict.get('cloudCover', None) is None: self.WeatherInfo['forecastTomorrow' + day + 'cloudCover'] = format(float(dayDict['cloudCover']) * 100, self.numbers) + ' %'
            except Exception as ex:
                Exc_log('EXCEPTION: ' + str(ex))
            
            for k, v in self.WeatherInfo.items():
                write_log('WeatherInfo : ' + str(k) + ':' + str(v))
        return

    def GotDGWeatherWeatherData(self, data = None):
        write_log('###################################### DGWeather Data ################################################')
        #write_log('Data : ' + str(data))
        if data is not None:
            try:
                parsed_json = json.loads(data)
                for k, v in parsed_json.items():
                    write_log(str(k) + ':' + str(v))

                write_log(str(len(parsed_json['list'])))
                write_log('###################################### DGWeather ################################################')
                for k, v in parsed_json['list'][0].items():
                    write_log(str(k) + ':' + str(v))

                self.WeatherInfo['forecastTomorrow4Date'] = ' '
                self.WeatherInfo['forecastTomorrow4Day'] = ' '
                self.WeatherInfo['forecastTomorrow4Code'] = ' '
                self.WeatherInfo['forecastTomorrow4Picon'] = ' '
                self.WeatherInfo['forecastTomorrow4TempMax'] = ' '
                self.WeatherInfo['forecastTomorrow4TempMin'] = ' '
                self.WeatherInfo['forecastTomorrow4Text'] = ' '
                hourly = ['0',
                 '1',
                 '2',
                 '3',
                 '4',
                 '5',
                 '6',
                 '7']
                for hour in hourly:
                    ahour = int(hour)
                    if hour == '0':
                        hour = ''
                    self.WeatherInfo['forecastHourly' + hour + 'Hour'] = str(parsed_json['list'][ahour]['dt_txt'])
                    self.WeatherInfo['forecastHourly' + hour + 'Humidity'] = format(float(parsed_json['list'][ahour]['main']['humidity']), '.0f') + ' %'
                    self.WeatherInfo['forecastHourly' + hour + 'Cloud'] = format(float(parsed_json['list'][ahour]['clouds']['all'])) + ' %'
                    self.WeatherInfo['forecastHourly' + hour + 'Picon'] = self.convertOWMIconName(parsed_json['list'][ahour]['weather'][0]['icon'])
                    self.WeatherInfo['forecastHourly' + hour + 'Text'] = str(parsed_json['list'][ahour]['weather'][0]['description'])
                    if 'rain' in parsed_json['list'][ahour]:
                        self.WeatherInfo['forecastHourly' + hour + 'Intensity'] = str(parsed_json['list'][ahour]['rain']['3h']) + _(' mm/3h')
                    elif 'snow' in parsed_json['list'][ahour]:
                        self.WeatherInfo['forecastHourly' + hour + 'Intensity'] = str(parsed_json['list'][ahour]['snow']['3h']) + _(' mm/3h')
                    else:
                        self.WeatherInfo['forecastHourly' + hour + 'Intensity'] = '0' + _(' mm/3h')

                i = 0
                next_day = 0
                sNOW = datetime.datetime.now().strftime('%d.%m.%Y')
                while i < 8:
                    if str(self.convertCurrentDateLong(parsed_json['list'][i]['dt'])) != sNOW:
                        next_day = i
                        write_log('morgen startet bei Index ' + str(next_day))
                        break
                    i += 1

                self.WeatherInfo['forecastTodayDay'] = self.convertCurrentDay(parsed_json['list'][0]['dt'])
                self.WeatherInfo['forecastTodayDate'] = self.convertCurrentDate(parsed_json['list'][0]['dt'])
                i = 0
                icons = []
                description = []
                clouds = []
                wspeed = []
                pressure = []
                humidity = []
                tempmin = 100
                tempmax = -100
                if int(next_day) > 0:
                    while i < int(next_day):
                        icons.append(parsed_json['list'][i]['weather'][0]['icon'])
                        description.append(parsed_json['list'][i]['weather'][0]['description'])
                        clouds.append(format(float(parsed_json['list'][i]['clouds']['all'])))
                        wspeed.append(parsed_json['list'][i]['wind']['speed'])
                        pressure.append(parsed_json['list'][i]['main']['pressure'])
                        humidity.append(format(float(parsed_json['list'][i]['main']['humidity'])))
                        if float(parsed_json['list'][i]['main']['temp']) < tempmin:
                            tempmin = float(parsed_json['list'][i]['main']['temp'])
                        if float(parsed_json['list'][i]['main']['temp']) > tempmax:
                            tempmax = float(parsed_json['list'][i]['main']['temp'])
                        i += 1

                    self.WeatherInfo['forecastTodayPicon'] = str(self.convertOWMIconName(icons[int(len(icons) / 2)]))
                    self.WeatherInfo['forecastTodayText'] = str(description[int(len(description) / 2)])
                    self.WeatherInfo['forecastTodaycloudCover'] = str(clouds[int(len(clouds) / 2)]) + ' %'
                    self.WeatherInfo['forecastTodayHumidity'] = str(humidity[int(len(humidity) / 2)]) + ' %'
                else:
                    while i < 8:
                        icons.append(parsed_json['list'][i]['weather'][0]['icon'])
                        description.append(parsed_json['list'][i]['weather'][0]['description'])
                        clouds.append(format(float(parsed_json['list'][i]['clouds']['all'])))
                        wspeed.append(parsed_json['list'][i]['wind']['speed'])
                        pressure.append(parsed_json['list'][i]['main']['pressure'])
                        humidity.append(format(float(parsed_json['list'][i]['main']['humidity'])))
                        if float(parsed_json['list'][i]['main']['temp']) < tempmin:
                            tempmin = float(parsed_json['list'][i]['main']['temp'])
                        if float(parsed_json['list'][i]['main']['temp']) > tempmax:
                            tempmax = float(parsed_json['list'][i]['main']['temp'])
                        i += 1

                    self.WeatherInfo['forecastTodayPicon'] = str(self.convertOWMIconName(icons[int(len(icons) / 2)]))
                    self.WeatherInfo['forecastTodayText'] = str(description[int(len(description) / 2)])
                    self.WeatherInfo['forecastTodaycloudCover'] = str(clouds[int(len(clouds) / 2)]) + ' %'
                    self.WeatherInfo['forecastTodayHumidity'] = str(humidity[int(len(humidity) / 2)]) + ' %'
                if next_day == 0:
                    next_day = 8
                i = next_day
                icons = []
                description = []
                clouds = []
                wspeed = []
                pressure = []
                humidity = []
                tempmin = 100
                tempmax = -100
                self.WeatherInfo['forecastTomorrowDate'] = self.convertCurrentDate(parsed_json['list'][i]['dt'])
                while i < int(next_day + 8):
                    icons.append(parsed_json['list'][i]['weather'][0]['icon'])
                    description.append(parsed_json['list'][i]['weather'][0]['description'])
                    clouds.append(format(float(parsed_json['list'][i]['clouds']['all'])))
                    wspeed.append(parsed_json['list'][i]['wind']['speed'])
                    pressure.append(parsed_json['list'][i]['main']['pressure'])
                    humidity.append(format(float(parsed_json['list'][i]['main']['humidity'])))
                    if float(parsed_json['list'][i]['main']['temp']) < tempmin:
                        tempmin = float(parsed_json['list'][i]['main']['temp'])
                    if float(parsed_json['list'][i]['main']['temp']) > tempmax:
                        tempmax = float(parsed_json['list'][i]['main']['temp'])
                    i += 1

                self.WeatherInfo['forecastTomorrowPicon'] = str(self.convertOWMIconName(icons[int(len(icons) / 2)]))
                self.WeatherInfo['forecastTomorrowText'] = str(description[int(len(description) / 2)])
                self.WeatherInfo['forecastTomorrowcloudCover'] = str(clouds[int(len(clouds) / 2)]) + ' %'
                self.WeatherInfo['forecastTomorrowHumidity'] = str(humidity[int(len(humidity) / 2)]) + ' %'
                if next_day == 8:
                    next_day = 16
                else:
                    next_day = next_day + 8
                day = 0
                for aday in range(0, 4):
                    day += 1
                    i = next_day + aday * 8
                    nd = i
                    icons = []
                    description = []
                    clouds = []
                    wspeed = []
                    pressure = []
                    humidity = []
                    tempmin = 100
                    tempmax = -100
                    if i < int(len(parsed_json['list'])):
                        self.WeatherInfo['forecastTomorrow' + str(day) + 'Date'] = self.convertCurrentDate(parsed_json['list'][i]['dt'])
                        while i < int(nd + 8) and i < int(len(parsed_json['list'])):
                            icons.append(parsed_json['list'][i]['weather'][0]['icon'])
                            description.append(parsed_json['list'][i]['weather'][0]['description'])
                            clouds.append(format(float(parsed_json['list'][i]['clouds']['all'])))
                            wspeed.append(parsed_json['list'][i]['wind']['speed'])
                            pressure.append(parsed_json['list'][i]['main']['pressure'])
                            humidity.append(format(float(parsed_json['list'][i]['main']['humidity'])))
                            if float(parsed_json['list'][i]['main']['temp']) < tempmin:
                                tempmin = float(parsed_json['list'][i]['main']['temp'])
                            if float(parsed_json['list'][i]['main']['temp']) > tempmax:
                                tempmax = float(parsed_json['list'][i]['main']['temp'])
                            i += 1

                        self.WeatherInfo['forecastTomorrow' + str(day) + 'Text'] = str(description[int(len(description) / 2)])
                        self.WeatherInfo['forecastTomorrow' + str(day) + 'Picon'] = str(self.convertOWMIconName(icons[int(len(icons) / 2)]))
                        self.WeatherInfo['forecastTomorrow' + str(day) + 'cloudCover'] = str(clouds[int(len(clouds) / 2)]) + ' %'
                        self.WeatherInfo['forecastTomorrow' + str(day) + 'Humidity'] = str(humidity[int(len(humidity) / 2)]) + ' %'

            except Exception as ex:
                Exc_log('Mistake in GotDGWeatherWeatherData : ' + str(ex))

        return

    def GotCurrentDGWeatherWeatherData(self, data = None):
        write_log('###################################### Current DGWeather Data ################################################')
        write_log('Data : ' + str(data))
        if data is not None:
            try:
                parsed_json = json.loads(data)
                self.WeatherInfo['currentCountry'] = str(parsed_json['sys']['country'])
                if 'deg' in parsed_json['wind']:
                    if config.plugins.dgWeather.winddirection.value == 'short':
                        self.WeatherInfo['windDirection'] = str(self.ConvertDirectionShort(parsed_json['wind']['deg']))
                    else:
                        self.WeatherInfo['windDirection'] = str(self.ConvertDirectionLong(parsed_json['wind']['deg']))
                else:
                    self.WeatherInfo['windDirection'] = '--'
                self.WeatherInfo['currentcloudCover'] = format(float(parsed_json['clouds']['all'])) + ' %'
                self.WeatherInfo['atmoHumidity'] = format(float(parsed_json['main']['humidity']), '.0f') + ' %'
                self.WeatherInfo['astroSunrise'] = self.convertAstroSun(parsed_json['sys']['sunrise'])
                self.WeatherInfo['astroSunset'] = self.convertAstroSun(parsed_json['sys']['sunset'])
                self.WeatherInfo['astroDaySoltice'] = self.convertAstroSun(float(parsed_json['sys']['sunset'] + parsed_json['sys']['sunrise']) * 0.5)
                self.WeatherInfo['astroDayLength'] = self.convertAstroDayLength(float(parsed_json['sys']['sunset'] - parsed_json['sys']['sunrise']) - 10800)
                self.WeatherInfo['downloadDate'] = self.convertCurrentDateLong(parsed_json['dt'])
                self.WeatherInfo['downloadTime'] = self.convertCurrentTime(parsed_json['dt'])
                self.WeatherInfo['currentWeatherText'] = str(parsed_json['weather'][0]['description'])
                write_log('###################################### Current DGWeather ################################################')
                for k, v in parsed_json.items():
                    write_log(str(k) + ':' + str(v))

            except Exception as ex:
                Exc_log('Mistake in GotCurrentDGWeatherWeatherData : ' + str(ex))

        return

    def ConvertDirectionShort(self, direction):
        dir = int(direction)
        if 0 <= dir <= 20:
            direction = _('N')
        elif 21 <= dir <= 35:
            direction = _('N-NE')
        elif 36 <= dir <= 55:
            direction = _('NE')
        elif 56 <= dir <= 70:
            direction = _('E-NE')
        elif 71 <= dir <= 110:
            direction = _('E')
        elif 111 <= dir <= 125:
            direction = _('E-SE')
        elif 126 <= dir <= 145:
            direction = _('SE')
        elif 146 <= dir <= 160:
            direction = _('S-SE')
        elif 161 <= dir <= 200:
            direction = _('S')
        elif 201 <= dir <= 215:
            direction = _('S-SW')
        elif 216 <= dir <= 235:
            direction = _('SW')
        elif 236 <= dir <= 250:
            direction = _('W-SW')
        elif 251 <= dir <= 290:
            direction = _('W')
        elif 291 <= dir <= 305:
            direction = _('W-NW')
        elif 306 <= dir <= 325:
            direction = _('NW')
        elif 326 <= dir <= 340:
            direction = _('N-NW')
        elif 341 <= dir <= 360:
            direction = _('N')
        else:
            direction = _('N/A')
        return str(direction)

    def ConvertDirectionLong(self, direction):
        dir = int(direction)
        if 0 <= dir <= 20:
            direction = _('North')
        elif 21 <= dir <= 35:
            direction = _('North-Northeast')
        elif 36 <= dir <= 55:
            direction = _('Northeast')
        elif 56 <= dir <= 70:
            direction = _('East-Northeast')
        elif 71 <= dir <= 110:
            direction = _('East')
        elif 111 <= dir <= 125:
            direction = _('East-Southeast')
        elif 126 <= dir <= 145:
            direction = _('Southeast')
        elif 146 <= dir <= 160:
            direction = _('South-Southeast')
        elif 161 <= dir <= 200:
            direction = _('South')
        elif 201 <= dir <= 215:
            direction = _('South-Southwest')
        elif 216 <= dir <= 235:
            direction = _('Southwest')
        elif 236 <= dir <= 250:
            direction = _('West-Southwest')
        elif 251 <= dir <= 290:
            direction = _('West')
        elif 291 <= dir <= 305:
            direction = _('West-Northwest')
        elif 306 <= dir <= 325:
            direction = _('Northwest')
        elif 326 <= dir <= 340:
            direction = _('North-Northwest')
        elif 341 <= dir <= 360:
            direction = _('North')
        else:
            direction = _('N/A')
        return str(direction)

    def convertWeatherText(self, WeatherText):
        return str(_(WeatherText.replace('-', ' ')))

    def convertAstroSun(self, val):
        write_log('convertAstroSun(%s)' % val)
        value = datetime.datetime.fromtimestamp(int(val))
        return value.strftime('%_H:%M')

    def convertAstroDayLength(self, val):
        value = datetime.datetime.fromtimestamp(int(val))
        return value.strftime(_('%_H h. %_M min.'))

    def convertCurrentDate(self, val):
        value = datetime.datetime.fromtimestamp(int(val))
        if config.plugins.dgWeather.WeekDay.value == 'dm':
            return value.strftime('%_d.%m')
        else:
            return value.strftime('%_d.%m.%Y')

    def convertCurrentDateLong(self, val):
        value = datetime.datetime.fromtimestamp(int(val))
        return value.strftime('%_d.%m.%Y')

    def convertCurrentTime(self, val):
        value = datetime.datetime.fromtimestamp(int(val))
        return value.strftime('%_H:%M:%S')

    def convertDateTime(self, val):
        value = datetime.datetime.fromtimestamp(int(val))
        return value.strftime('%d.%m.%Y %_H:%M:%S')

    def convertOWMIconName(self, IconName):
        if IconName == '01d':
            return '32'
        elif IconName == '02d':
            return '34'
        elif IconName == '03d':
            return '28'
        elif IconName == '04d':
            return '26'
        elif IconName == '05d':
            return '39'
        elif IconName == '06d':
            return '37'
        elif IconName == '07d':
            return '5'
        elif IconName == '08d':
            return '13'
        elif IconName == '09d':
            return '12'
        elif IconName == '10d':
            return '12'
        elif IconName == '11d':
            return '38'
        elif IconName == '12d':
            return '5'
        elif IconName == '13d':
            return '14'
        elif IconName == '14d':
            return '17'
        elif IconName == '15d':
            return '19'
        elif IconName == '20d':
            return '37'
        elif IconName == '21d':
            return '37'
        elif IconName == '22d':
            return '3'
        elif IconName == '23d':
            return '5'
        elif IconName == '30d':
            return '38'
        elif IconName == '31d':
            return '38'
        elif IconName == '32d':
            return '5'
        elif IconName == '33d':
            return '13'
        elif IconName == '34d':
            return '14'
        elif IconName == '40d':
            return '39'
        elif IconName == '46d':
            return '11'
        elif IconName == '47d':
            return '11'
        elif IconName == '48d':
            return '5'
        elif IconName == '49d':
            return '6'
        elif IconName == '50d':
            return '20'
        elif IconName == '01n':
            return '31'
        elif IconName == '02n':
            return '29'
        elif IconName == '03n':
            return '27'
        elif IconName == '04n':
            return '26'
        elif IconName == '05n':
            return '47'
        elif IconName == '06n':
            return '47'
        elif IconName == '07n':
            return '46'
        elif IconName == '08n':
            return '46'
        elif IconName == '09n':
            return '12'
        elif IconName == '10n':
            return '12'
        elif IconName == '11n':
            return '47'
        elif IconName == '13n':
            return '14'
        elif IconName == '40n':
            return '12'
        elif IconName == '41n':
            return '46'
        elif IconName == '50n':
            return '20'
        else:
            write_log('missing IconName : ' + str(IconName))
            return '3200'
