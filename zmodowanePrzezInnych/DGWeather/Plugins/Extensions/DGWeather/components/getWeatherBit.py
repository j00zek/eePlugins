#ponizsze dwie linie sa niezbedne bo uruchamiamy zabawki z innych katalogow
#"status_message": "Your request count (58) is over the allowed limit of 55 per day - Upgrade your key, or retry after 465.36666666667 minutes" 

import os, sys, time
if '/usr/lib/enigma2/python/Plugins/Extensions/DGWeather/components/' not in sys.path:
    sys.path.append('/usr/lib/enigma2/python/Plugins/Extensions/DGWeather/components/')

from utils import *

def getWeatherBitDict(APIKEY, lat, long, CountryCode):
    dict = WeatherBitDict(APIKEY, lat, long, CountryCode)
    return buildDGweatherDict(dict)

def WeatherBitDict(APIKEY, lat, long, CountryCode):
    vcDict = {}
    #write_log(int(time.time()))
    #write_log(round(os.stat(os.path.join(logFolder, 'WeatherBitDict.json')).st_mtime))
    #write_log(time.time() - round(os.stat(os.path.join(logFolder, 'WeatherBitDict.json')).st_mtime))
    if os.path.exists(os.path.join(logFolder, 'WeatherBitDict.json')) and int(time.time()) - round(os.stat(os.path.join(logFolder, 'WeatherBitDict.json')).st_mtime) < 60 * 30:
        vcDict = LoadJsonDict('WeatherBitDict.json')
        write_log('getWeatherBitgDict() >>> loaded %s items from WeatherBitDict.json' % len(vcDict))
    else:
        write_log('getWeatherBitDict(API = "%s...", lat = "%s", long = "%s") >>>' % (APIKEY[0:5], lat, long))
        MainUrl = "https://api.weatherbit.io/v2.0/"

        if APIKEY != '' and lat != '' and long != '':
            locationSettingsURL = 'current?lat=%s&lon=%s&key=%s&lang=%s&include=minutely' % (lat, long, APIKEY, CountryCode)
            url = MainUrl + locationSettingsURL
            #write_log('VC-URL : ' + str(url))
            webContent = downloadWebPage(url)
            if 'API key not valid' in webContent:
                vcDict['currentConditions'] = {}
                vcDict['currentConditions']['conditions'] = _('WRONG API KEY')
                write_log('WRONG openweathermap API KEY')
            elif 'is over the allowed limit' in webContent:
                vcDict['currentConditions'] = {}
                vcDict['currentConditions']['conditions'] = _('LIMITWRONG API KEY QUERY LIMIT REACHED')
                write_log('WRONG openweathermap API KEY')
            else:
                vcDict['current'] = json.loads(webContent)
                #daily data
                locationSettingsURL = 'forecast/daily?lat=%s&lon=%s&key=%s&lang=%s' % (lat, long, APIKEY, CountryCode)
                url = MainUrl + locationSettingsURL
                #write_log('VC-URL : ' + str(url))
                webContent = downloadWebPage(url)
                vcDict['daily'] = json.loads(webContent)

                if 0:
                    #hourly data for free API "error": "Your API key does not allow access to this endpoint."
                    locationSettingsURL = 'forecast/hourly?lat=%s&lon=%s&key=%s&lang=%s' % (lat, long, APIKEY, CountryCode)
                    url = MainUrl + locationSettingsURL
                    write_log('VC-URL : ' + str(url))
                    webContent = downloadWebPage(url)
                    vcDict['hourly'] = json.loads(webContent)
                    #minutely "error": "Your API key does not allow access to this endpoint."
                    locationSettingsURL = 'forecast/minutely?lat=%s&lon=%s&key=%s&lang=%s' % (lat, long, APIKEY, CountryCode)
                    url = MainUrl + locationSettingsURL
                    write_log('VC-URL : ' + str(url))
                    webContent = downloadWebPage(url)
                    vcDict['minutely'] = json.loads(webContent)
            
            saveJsonDict('WeatherBitDict.json', vcDict) #tylko, zeby wiedziec co jest dostepne
        else:
            write_log('Brak wymaganych danych lokalizacyjnych')
        write_log('getWeatherBitDict() <<<')
    return vcDict

def buildDGweatherDict(sourceDict):
    write_log('buildDGweatherDict() >>>')
    dgDict = {} #LoadJsonDict('dgWeatherDict.json') #aktualizacja
    if 1:
        #aktualne dane
        try:
            tmpDict = sourceDict['current'].get('data','')[0]
        except Exception:
            tmpDict = {}
            Exc_log()
        
        sunsetMins = int(tmpDict.get('sunset', '0:0').split(':')[0])* 60 + int(tmpDict.get('sunset', '0:0').split(':')[1])
        sunriseMins = int(tmpDict.get('sunrise', '0:0').split(':')[0])* 60 + int(tmpDict.get('sunrise', '0:0').split(':')[1])
        dayLength = sunsetMins - sunriseMins
        Hlength = int(dayLength / 60)
        Mlength = int(dayLength - Hlength * 60)
        if Mlength < 10: Mlength = '0%s' % Mlength
        dgDict['astroDayLength'] = "%s:%s" % (Hlength, Mlength)

        dgDict['astroSunrise'] =        tmpDict.get('sunrise', '0:0')
        dgDict['astroSunset'] =         tmpDict.get('sunset', '0:0')
        
        solMins = sunriseMins + int(dayLength/2)
        HH = int(solMins / 60)
        MM = int(solMins - HH * 60)
        if MM < 10: MM = '0%s' % MM
        dgDict['astroDaySoltice'] =     "%s:%s" % (HH, MM) 
        dgDict['atmoHumidity'] =        tmpDict.get('rh', 0)
        dgDict['downloadDate'] =        tmpDict.get('ob_time', ' ').split(' ')[0]
        dgDict['downloadTime'] =        tmpDict.get('ob_time', ' ').split(' ')[1]
        dgDict['currentcloudCover'] =   tmpDict.get('clouds', 0)
        dgDict['currentPressure'] =     tmpDict.get('pres', 0)
        dgDict['currentWeatherCode'] =  tmpDict.get('weather', {}).get('code', '')
        dgDict['currentWeatherPicon'] = tmpDict.get('weather', {}).get('icon', '')
        dgDict['currentWeatherTemp'] =  tmpDict.get('temp', 0)
        dgDict['currentWeatherText'] =  tmpDict.get('weather', {}).get('description', '')
        dgDict['currentlywindGust'] =   tmpDict.get('gust', 0)
        dgDict['currentlywindSpeed'] =  tmpDict.get('wind_spd', 0)
        dgDict['dewPoint'] =            tmpDict.get('dewpt', 0)
        dgDict['uvIndex'] =             tmpDict.get('uv', 0)
        dgDict['windChill'] =           tmpDict.get('app_temp', 0)
        dgDict['windDirection'] =       tmpDict.get('wind_dir', 0)

        dgDict['timezone'] = tmpDict.get('timezone','')

        #below missing in current, taking from daily>day[0]
        tmpDict = sourceDict.get('daily', {}).get('data', [{}])[0]
        dgDict['atmoVisibility'] =      tmpDict.get('vis', 0)
        dgDict['currentlyIntensity'] =  tmpDict.get('precip', 0)
        dgDict['currentMoonPhase'] =    tmpDict.get('moon_phase', 0)
        dgDict['currentPrecip'] =       tmpDict.get('precip', 0)

        #dgDict['currentProbability'] =  tmpDict.get('precipprob', 0)
        #aktualne dzienne i godzinowe
        tmpDict = sourceDict.get('daily', {}).get('data', [{}])
        AvailableDays = len(tmpDict)
        dayToNameList = [(0, "forecastToday"), (1, "forecastTomorrow"), (2, "forecastTomorrow1"), (3, "forecastTomorrow2"), 
                         (4, "forecastTomorrow3"), (5, "forecastTomorrow4"), (6, "forecastTomorrow5"), (7, "forecastTomorrow6")
                        ]
        hourToNameList = [(0, "forecastHourly"),  (1, "forecastHourly1"), (2, "forecastHourly2"), 
                          (3, "forecastHourly3"), (4, "forecastHourly4"), (5, "forecastHourly5"), 
                          (6, "forecastHourly6"), (7, "forecastHourly7"), (8, "forecastHourly8")
                         ]
        
        write_log('WeatherBitDict site returned %s days' % AvailableDays)
        for currDay in dayToNameList:
            if currDay[0] >= AvailableDays:
                break
            try:
                dayDict = tmpDict[currDay[0]]
            except Exception as e:
                Exc_log(str(e))
                break
            dgDict[currDay[1] + 'Pressure'] =   dayDict.get('pres' , '?')
            dgDict[currDay[1] + 'Code'] =       dayDict.get('weather', {}).get('code', '')
            dgDict[currDay[1] + 'Day'] =        dayDict.get('datetime', '?')
            dgDict[currDay[1] + 'Date'] =       dayDict.get('datetime' , '?')
            dgDict[currDay[1] + 'TempMin'] =    dayDict.get('min_temp' , '?')
            dgDict[currDay[1] + 'TempMax'] =    dayDict.get('max_temp' , '?')
            dgDict[currDay[1] + 'Text'] =       dayDict.get('weather', {}).get('description', '')
            dgDict[currDay[1] + 'Picon'] =      dayDict.get('weather', {}).get('icon', '')
            dgDict[currDay[1] + 'windSpeed'] =  dayDict.get('wind_spd' , '?')
            dgDict[currDay[1] + 'windGust'] =   dayDict.get('wind_gust_spd' , '?')
            dgDict[currDay[1] + 'moonPhase'] =  dayDict.get('moon_phase' , '?')
            #dgDict[currDay[1] + 'Probability']= dayDict.get('precipprob' , '?')
            dgDict[currDay[1] + 'Intensity'] =  dayDict.get('precip' , '?')
            dgDict[currDay[1] + 'cloudCover'] = dayDict.get('clouds' , '?')
            dgDict[currDay[1] + 'Humidity'] =   dayDict.get('rh' , '?')
    if 0:
        dgDict['W-Info'] = ''
        dgDict['W-Info-h'] = ''
        dgDict['astroDaySoltice'] = ''
        dgDict['currentOzoneText'] = ''
        dgDict['PiconMoon'] = ''

    saveJsonDict('dgWeatherDict.json', dgDict) #kontrola WeatherInfoDict
    return dgDict
    
if __name__ == '__main__': # wychwytuje sytuacje gdy skrypt odpalany z konsoli
    # inicjacja zmiennych
    CountryCode = 'pl'
    APIKEY = open('/etc/enigma2/DGWeather/WeatherBit_apikey', 'r').read().strip()
    # !!!! openweathermap nie uzywa juz id_city tylko koordynatorow geo !!!!!
    latitude  = open('/etc/enigma2/DGWeather/geolatitude', 'r').read().strip()
    longitude = open('/etc/enigma2/DGWeather/geolongitude', 'r').read().strip()
    if APIKEY == '':
        print('Brak WeatherBit_apikey')
    elif latitude == '':
        print('Brak geolatitude')
    elif longitude == '':
        print('Brak geolongitude')
    else:
        dict = WeatherBitDict(APIKEY, latitude, longitude, CountryCode)
        buildDGweatherDict(dict)
