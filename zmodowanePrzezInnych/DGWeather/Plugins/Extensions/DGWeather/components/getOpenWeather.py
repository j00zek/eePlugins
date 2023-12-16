# pobiera o przygotowuje do uzycia dane json z OpenWeatherDict  do /tmp/dgWeather
# https://openweathermap.org/api
# forecast: api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API key}
# current:  api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API key}

#ponizsze dwie linie sa niezbedne bo uruchamiamy zabawki z innych katalogow
import os, sys, time
if '/usr/lib/enigma2/python/Plugins/Extensions/DGWeather/components/' not in sys.path:
    sys.path.append('/usr/lib/enigma2/python/Plugins/Extensions/DGWeather/components/')

from utils import *

def getOpenWeatherDict(APIKEY, lat, long, CountryCode):
    dict = OpenWeatherDict(APIKEY, lat, long, CountryCode)
    return buildDGweatherDict(dict)

def OpenWeatherDict(APIKEY, lat, long, CountryCode):
    write_log('getOpenWeather(API = "%s", lat = "%s", long = "%s") >>>' % (APIKEY, lat, long))
    naszDict = {'forecast': {}, 'current': {}}
    if APIKEY != '' and lat != '' and long != '':
        locationSettingsURL = 'lat=%s&lon=%s&appid=%s&units=metric&lang=%s' %(lat, long, APIKEY, CountryCode)
        url = 'http://api.openweathermap.org/data/2.5/forecast?' + locationSettingsURL
        write_log('OWM-URL : ' + str(url))
        webContent = downloadWebPage(url)
        if 'Invalid API key' in webContent:
            self.WeatherInfo['currentWeatherText'] = _('WRONG API KEY')
            write_log('WRONG openweathermap API KEY')
        else:
            naszDict['forecast'] = json.loads(webContent)
            url = 'http://api.openweathermap.org/data/2.5/weather?' + locationSettingsURL
            write_log('COWMURL : ' + str(url))
            webContent = downloadWebPage(url)
            naszDict['current'] = json.loads(webContent)
        #tutaj ewentualne modyfikacje danych
        #zysk: pracujemy na konkretnym zestawie danych i nie wplywamy na dane z innych zrodel
        saveJsonDict('OpenWeatherDict.json', naszDict) #tylko, zeby wiedziec co jest dostepne
    else:
        write_log('Brak wymaganych danych lokalizacyjnych')
    write_log('getOpenWeatherDict() <<<')
    return naszDict

def buildDGweatherDict(sourceDict):
    write_log('buildDGweatherDict() >>>')
    dgDict = {} #LoadJsonDict('dgWeatherDict.json') #aktualizacja
    if 1:
        #aktualne dane
        tmpDict = sourceDict.get('current', {})
        dgDict['timezone'] = tmpDict.get('timezone','')
        dgDict['atmoVisibility'] =      tmpDict.get('visibility', 0)

        dayLengthEpoc = tmpDict.get('sys', {}).get('sunset', 0) -  tmpDict.get('sys', {}).get('sunrise', 0)
        Hlength = int(dayLengthEpoc / 3600)
        Mlength = int((dayLengthEpoc - Hlength * 3600) / 60)
        Slength = dayLengthEpoc - Hlength * 3600 - Mlength * 60
        dgDict['astroDayLength'] =      "%s:%s:%s" % (Hlength, Mlength, Slength)
        dgDict['astroSunrise'] =        tmpDict.get('sys', {}).get('sunrise', 0)
        dgDict['astroSunset'] =         tmpDict.get('sys', {}).get('sunset', 0)
        
        dgDict['atmoHumidity'] =        tmpDict.get('main', {}).get('humidity', 0)
        #
        dgDict['downloadDate'] =        tmpDict.get('dt', 0)
        dgDict['downloadTime'] =        tmpDict.get('dt', 0)

        dgDict['currentcloudCover'] =   tmpDict.get('clouds', {}).get('all', 0)
        dgDict['currentPressure'] =     tmpDict.get('main', {}).get('pressure', 0)
        dgDict['currentWeatherCode'] =  tmpDict.get('weather', {})[0].get('icon', '?')
        dgDict['currentWeatherPicon'] = tmpDict.get('weather', {})[0].get('icon', '?')
        dgDict['currentWeatherTemp'] =  tmpDict.get('main', {}).get('temp', 0)
        dgDict['currentWeatherText'] =  tmpDict.get('weather', {})[0].get('description','?')
        dgDict['currentlywindSpeed'] =  tmpDict.get('wind', {}).get('speed', 0)
        dgDict['windChill'] =           tmpDict.get('main', {}).get('feels_like', 0)
        dgDict['windDirection'] =       tmpDict.get('wind', {}).get('deg', 0)
    else:
        dgDict['currentlyIntensity'] =  tmpDict.get('precip', 0)
        dgDict['currentPrecip'] =       tmpDict.get('precip', 0)

        dgDict['currentProbability'] =  tmpDict.get('precipprob', 0)
        dgDict['currentlywindGust'] =   tmpDict.get('windgust', 0)
        dgDict['uvIndex'] =             tmpDict.get('uvindex', 0)
        dgDict['dewPoint'] =            tmpDict.get('dew', 0)
        #aktualne dzienne i godzinowe
        tmpDict = sourceDict.get('days', [])
        AvailableDays = len(tmpDict)
        dayToNameList = [(0, "forecastToday"), (1, "forecastTomorrow"), (2, "forecastTomorrow1"), (3, "forecastTomorrow2"), 
                         (4, "forecastTomorrow3"), (5, "forecastTomorrow4"), (6, "forecastTomorrow5"), (7, "forecastTomorrow6")
                        ]
        hourToNameList = [(0, "forecastHourly"),  (1, "forecastHourly1"), (2, "forecastHourly2"), 
                          (3, "forecastHourly3"), (4, "forecastHourly4"), (5, "forecastHourly5"), 
                          (6, "forecastHourly6"), (7, "forecastHourly7"), (8, "forecastHourly8")
                         ]
        
        for currDay in dayToNameList:
            try:
                dayDict = tmpDict[currDay[0]]
            except Exception as e:
                Exc_log(str(e))
                break
            dgDict[currDay[1] + 'Pressure'] =   dayDict.get('pressure' , '?')
            dgDict[currDay[1] + 'Code'] =       dayDict.get('icon' , '?')
            dgDict[currDay[1] + 'Day'] =        dayDict.get('datetimeEpoch' , '?')
            dgDict[currDay[1] + 'Date'] =       dayDict.get('datetime' , '?')
            dgDict[currDay[1] + 'TempMin'] =    dayDict.get('tempmin' , '?')
            dgDict[currDay[1] + 'TempMax'] =    dayDict.get('tempmax' , '?')
            dgDict[currDay[1] + 'Text'] =       dayDict.get('conditions' , '?')
            dgDict[currDay[1] + 'Picon'] =      dayDict.get('icon' , '?')
            dgDict[currDay[1] + 'windSpeed'] =  dayDict.get('windspeed' , '?')
            dgDict[currDay[1] + 'windGust'] =   dayDict.get('windgust' , '?')
            dgDict[currDay[1] + 'moonPhase'] =  dayDict.get('moonphase' , '?')
            dgDict[currDay[1] + 'Probability']= dayDict.get('precipprob' , '?')
            dgDict[currDay[1] + 'Intensity'] =  dayDict.get('precip' , '?')
            dgDict[currDay[1] + 'cloudCover'] = dayDict.get('cloudcover' , '?')
            dgDict[currDay[1] + 'Humidity'] =   dayDict.get('humidity' , '?')
            
            if currDay[0] == 0:
                hoursDict = dayDict.get('hours', [])
                for currHour in hourToNameList:
                    try:
                        hourDict = hoursDict[currHour[0]]
                    except Exception as e:
                        Exc_log(str(e))
                        break
                    dgDict[currHour[1] + 'Hour'] =      hourDict.get('datetime' , '?')
                    dgDict[currHour[1] + 'Temp'] =      hourDict.get('temp' , '?')
                    dgDict[currHour[1] + 'windSpeed'] = hourDict.get('windspeed' , '?')
                    dgDict[currHour[1] + 'Pressure'] =  hourDict.get('pressure' , '?')
                    dgDict[currHour[1] + 'Humidity'] =  hourDict.get('humidity' , '?')
                    dgDict[currHour[1] + 'Text'] =      hourDict.get('conditions' , '?')
                    dgDict[currHour[1] + 'Picon'] =     hourDict.get('icon' , '?')
                    dgDict[currHour[1] + 'Cloud'] =     hourDict.get('cloudcover' , '?')
                    dgDict[currHour[1] + 'Intensity'] = hourDict.get('precip' , '?')
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
    APIKEY = open('/etc/enigma2/DGWeather/OpenWeathermap_apikey', 'r').read().strip()
    # !!!! openweathermap nie uzywa juz id_city tylko koordynatorow geo !!!!!
    latitude  = open('/etc/enigma2/DGWeather/geolatitude', 'r').read().strip()
    longitude = open('/etc/enigma2/DGWeather/geolongitude', 'r').read().strip()
    if APIKEY == '':
        print('Brak OpenWeathermap_apikey')
    elif latitude == '':
        print('Brak geolatitude')
    elif longitude == '':
        print('Brak geolongitude')
    else:
        dict = OpenWeatherDict(APIKEY, latitude, longitude, CountryCode)
        buildDGweatherDict(dict)
    