# pobiera o przygotowuje do uzycia dane json z OpenWeatherDict  do /tmp/dgWeather
# https://openweathermap.org/api
# forecast: api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API key}
# current:  api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API key}

#ponizsze dwie linie sa niezbedne bo uruchamiamy zabawki z innych katalogow
import os, sys, time
if '/usr/lib/enigma2/python/Plugins/Extensions/DGWeather/components/' not in sys.path:
    sys.path.append('/usr/lib/enigma2/python/Plugins/Extensions/DGWeather/components/')

from utils import *
from datetime import datetime

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
            dgDict['currentWeatherText'] = _('WRONG API KEY')
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
    if 1: #aktualne dane
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
        dgDict['astroDaySoltice'] =     float(dgDict['astroSunset'] + dgDict['astroSunrise']) * 0.5
        
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

        try:
            dgDict['currentlywindGust'] = sourceDict['forecast']['list'][0]['wind']['gust']
        except Exception as e:
            print(e)

    if 1: #dane godzinowe
        hourToNameList = [(0, "forecastHourly"),  (1, "forecastHourly1"), (2, "forecastHourly2"), 
                          (3, "forecastHourly3"), (4, "forecastHourly4"), (5, "forecastHourly5"), 
                          (6, "forecastHourly6"), (7, "forecastHourly7"), (8, "forecastHourly8")
                         ]
        tmpDict = sourceDict.get('forecast', {}).get('list', [])
        for currHour in hourToNameList:
            try:
                hourDict = tmpDict[currHour[0]]
            except Exception as e:
                Exc_log(str(e))
                break
            dgDict[currHour[1] + 'Hour'] =      hourDict.get('dt_txt' , '?')
            dgDict[currHour[1] + 'Temp'] =      hourDict.get('main' , {}).get('temp' , '?')
            dgDict[currHour[1] + 'Humidity'] =  hourDict.get('main' , {}).get('humidity' , '?')
            dgDict[currHour[1] + 'Cloud'] =     hourDict.get('clouds' , {}).get('all' , '?')
            dgDict[currHour[1] + 'windSpeed'] = hourDict.get('wind' , {}).get('speed' , 0)
            dgDict[currHour[1] + 'Picon'] =     hourDict.get('weather' , [])[0].get('icon' , '?')
            dgDict[currHour[1] + 'Text'] =      hourDict.get('weather' , [])[0].get('description' , '?')
            dgDict[currHour[1] + 'Pressure'] =  hourDict.get('main' , {}).get('pressure' , '?')
            dgDict[currHour[1] + 'Intensity'] = float(hourDict.get('rain' , {}).get('3h' , 0)) + float(hourDict.get('snow' , {}).get('3h' , 0))
            
    if 1: #dane dzienne agregowane z godzinowych
        tmpDict = sourceDict.get('forecast', {}).get('list', [])
        i = 0
        next_day = 0
        sNOW = datetime.now().strftime('%Y-%m-%d')
        while i < 8:
            if tmpDict[i]['dt_txt'].split(' ')[0] != sNOW:
                next_day = i
                break
            i += 1
        write_log('next day starts at Index ' + str(next_day))

        dgDict['forecastTodayDay'] = tmpDict[0]['dt']
        dgDict['forecastTodayDate'] = tmpDict[0]['dt']
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
                icons.append(tmpDict[i]['weather'][0]['icon'])
                description.append(tmpDict[i]['weather'][0]['description'])
                clouds.append(format(float(tmpDict[i]['clouds']['all'])))
                wspeed.append(tmpDict[i]['wind']['speed'])
                pressure.append(tmpDict[i]['main']['pressure'])
                humidity.append(format(float(tmpDict[i]['main']['humidity'])))
                if float(tmpDict[i]['main']['temp']) < tempmin:
                    tempmin = float(tmpDict[i]['main']['temp'])
                if float(tmpDict[i]['main']['temp']) > tempmax:
                    tempmax = float(tmpDict[i]['main']['temp'])
                i += 1

            dgDict['forecastTodayCode'] = icons[int(len(icons) / 2)]
            dgDict['forecastTodayPicon'] = icons[int(len(icons) / 2)]
            dgDict['forecastTodayText'] = description[int(len(description) / 2)]
            dgDict['forecastTodayTempMax'] = tempmax
            dgDict['forecastTodayTempMin'] = tempmin
            dgDict['forecastTodaycloudCover'] = clouds[int(len(clouds) / 2)]
            dgDict['forecastTodaywindSpeed'] = wspeed[int(len(wspeed) / 2)]
            dgDict['forecastTodayPressure'] = pressure[int(len(pressure) / 2)]
            dgDict['forecastTodayHumidity'] = humidity[int(len(humidity) / 2)]
        else:
            while i < 8:
                icons.append(tmpDict[i]['weather'][0]['icon'])
                description.append(tmpDict[i]['weather'][0]['description'])
                clouds.append(format(float(tmpDict[i]['clouds']['all'])))
                wspeed.append(tmpDict[i]['wind']['speed'])
                pressure.append(tmpDict[i]['main']['pressure'])
                humidity.append(format(float(tmpDict[i]['main']['humidity'])))
                if float(tmpDict[i]['main']['temp']) < tempmin:
                    tempmin = float(tmpDict[i]['main']['temp'])
                if float(tmpDict[i]['main']['temp']) > tempmax:
                    tempmax = float(tmpDict[i]['main']['temp'])
                i += 1

            dgDict['forecastTodayCode'] = icons[int(len(icons) / 2)]
            dgDict['forecastTodayPicon'] = icons[int(len(icons) / 2)]
            dgDict['forecastTodayText'] = description[int(len(description) / 2)]
            dgDict['forecastTodayTempMax'] = tempmax
            dgDict['forecastTodayTempMin'] = tempmin
            dgDict['forecastTodaycloudCover'] = clouds[int(len(clouds) / 2)]
            dgDict['forecastTodaywindSpeed'] = wspeed[int(len(wspeed) / 2)]
            dgDict['forecastTodayPressure'] = pressure[int(len(pressure) / 2)]
            dgDict['forecastTodayHumidity'] = humidity[int(len(humidity) / 2)]
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
        dgDict['forecastTomorrowDay'] = tmpDict[i]['dt']
        dgDict['forecastTomorrowDate'] = tmpDict[i]['dt']
        while i < int(next_day + 8):
            icons.append(tmpDict[i]['weather'][0]['icon'])
            description.append(tmpDict[i]['weather'][0]['description'])
            clouds.append(format(float(tmpDict[i]['clouds']['all'])))
            wspeed.append(tmpDict[i]['wind']['speed'])
            pressure.append(tmpDict[i]['main']['pressure'])
            humidity.append(format(float(tmpDict[i]['main']['humidity'])))
            if float(tmpDict[i]['main']['temp']) < tempmin:
                tempmin = float(tmpDict[i]['main']['temp'])
            if float(tmpDict[i]['main']['temp']) > tempmax:
                tempmax = float(tmpDict[i]['main']['temp'])
            i += 1

        dgDict['forecastTomorrowCode'] = icons[int(len(icons) / 2)]
        dgDict['forecastTomorrowPicon'] = icons[int(len(icons) / 2)]
        dgDict['forecastTomorrowText'] = description[int(len(description) / 2)]
        dgDict['forecastTomorrowcloudCover'] = clouds[int(len(clouds) / 2)]
        dgDict['forecastTomorrowTempMax'] = tempmax
        dgDict['forecastTomorrowTempMin'] = tempmin
        dgDict['forecastTomorrowwindSpeed'] = wspeed[int(len(wspeed) / 2)]
        dgDict['forecastTomorrowPressure'] = pressure[int(len(pressure) / 2)]
        dgDict['forecastTomorrowHumidity'] = humidity[int(len(humidity) / 2)]
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
            if i < int(len(tmpDict)):
                dgDict['forecastTomorrow' + str(day) + 'Day'] = tmpDict[i]['dt']
                dgDict['forecastTomorrow' + str(day) + 'Date'] = tmpDict[i]['dt']
                while i < int(nd + 8) and i < int(len(tmpDict)):
                    icons.append(tmpDict[i]['weather'][0]['icon'])
                    description.append(tmpDict[i]['weather'][0]['description'])
                    clouds.append(format(float(tmpDict[i]['clouds']['all'])))
                    wspeed.append(tmpDict[i]['wind']['speed'])
                    pressure.append(tmpDict[i]['main']['pressure'])
                    humidity.append(format(float(tmpDict[i]['main']['humidity'])))
                    if float(tmpDict[i]['main']['temp']) < tempmin:
                        tempmin = float(tmpDict[i]['main']['temp'])
                    if float(tmpDict[i]['main']['temp']) > tempmax:
                        tempmax = float(tmpDict[i]['main']['temp'])
                    i += 1

                dgDict['forecastTomorrow' + str(day) + 'Text'] = description[int(len(description) / 2)]
                dgDict['forecastTomorrow' + str(day) + 'Code'] = icons[int(len(icons) / 2)]
                dgDict['forecastTomorrow' + str(day) + 'Picon'] = icons[int(len(icons) / 2)]
                dgDict['forecastTomorrow' + str(day) + 'cloudCover'] = clouds[int(len(clouds) / 2)]
                dgDict['forecastTomorrow' + str(day) + 'TempMax'] = tempmax
                dgDict['forecastTomorrow' + str(day) + 'TempMin'] = tempmin
                dgDict['forecastTomorrow' + str(day) + 'windSpeed'] = wspeed[int(len(wspeed) / 2)]
                dgDict['forecastTomorrow' + str(day) + 'Pressure'] = pressure[int(len(pressure) / 2)]
                dgDict['forecastTomorrow' + str(day) + 'Humidity'] = humidity[int(len(humidity) / 2)]

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
    