# pobiera o przygotowuje do uzycia dane json z visualcrossing  do /tmp/dgWeather
# https://www.visualcrossing.com/resources/documentation/weather-api/timeline-weather-api/
# Weather Query Builder: https://www.visualcrossing.com/weather/weather-data-services
# prognoza dzienna: weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{lon}?unitGroup=metric&include=days&key={API key}&contentType=json
# obecnie: weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{lon}?unitGroup=metric&include=current&key={API key}&contentType=json
# wszystko na raz 
#   po koordynatach: weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{lon}?unitGroup=metric&key={API key}&contentType=json
#   po nazwie lokalizacji: weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{NAZWA LOKALIZACJI}?unitGroup=us&key={API key}&contentType=json

#ponizsze dwie linie sa niezbedne bo uruchamiamy zabawki z innych katalogow
import os, sys, time
if '/usr/lib/enigma2/python/Plugins/Extensions/DGWeather/components/' not in sys.path:
    sys.path.append('/usr/lib/enigma2/python/Plugins/Extensions/DGWeather/components/')

from utils import *

def getVisualCrossingDict(APIKEY, lat, long, CountryCode):
    dict = VisualCrossingDict(APIKEY, lat, long, CountryCode)
    return buildDGweatherDict(dict)

def VisualCrossingDict(APIKEY, lat, long, CountryCode):
    vcDict = {}
    #write_log(int(time.time()))
    #write_log(round(os.stat(os.path.join(logFolder, 'VisualCrossingDict.json')).st_mtime))
    #write_log(time.time() - round(os.stat(os.path.join(logFolder, 'VisualCrossingDict.json')).st_mtime))
    if os.path.exists(os.path.join(logFolder, 'VisualCrossingDict.json')) and int(time.time()) - round(os.stat(os.path.join(logFolder, 'VisualCrossingDict.json')).st_mtime) < 60 * 20:
        vcDict = LoadJsonDict('VisualCrossingDict.json')
        write_log('getVisualCrossingDict() >>> loaded %s items from VisualCrossingDict.json' % len(vcDict))
    else:
        write_log('getVisualCrossingDict(API = "%s...", lat = "%s", long = "%s") >>>' % (APIKEY[0:5], lat, long))
        MainUrl = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
        if APIKEY != '' and lat != '' and long != '':
            locationSettingsURL = '%s,%s?unitGroup=metric&key=%s&contentType=json&lang=%s' % (lat, long, APIKEY, CountryCode)
            url = MainUrl + locationSettingsURL
            write_log('VC-URL : ' + str(url))
            webContent = downloadWebPage(url)
            if 'Invalid API key' in webContent:
                vcDict['currentConditions'] = {}
                vcDict['currentConditions']['conditions'] = _('WRONG API KEY')
                write_log('WRONG openweathermap API KEY')
            else:
                vcDict = json.loads(webContent)
            saveJsonDict('VisualCrossingDict.json', vcDict) #tylko, zeby wiedziec co jest dostepne
        else:
            write_log('Brak wymaganych danych lokalizacyjnych')
        write_log('getVisualCrossingDict() <<<')
    return vcDict

def buildDGweatherDict(sourceDict):
    write_log('buildDGweatherDict() >>>')
    dgDict = {} #LoadJsonDict('dgWeatherDict.json') #aktualizacja
    if 1:
        dgDict['timezone'] = sourceDict.get('timezone','')
        #dane z ALERTS
        tmpDict = sourceDict.get('alerts', {})
        if len(tmpDict) > 0: dgDict['alerts'] = tmpDict[0].get('event','')
        #aktualne dane
        tmpDict = sourceDict.get('currentConditions', {})

        dayLengthEpoc = tmpDict.get('sunsetEpoch', 0) -  tmpDict.get('sunriseEpoch', 0)
        Hlength = int(dayLengthEpoc / 3600)
        Mlength = int((dayLengthEpoc - Hlength * 3600) / 60)
        Slength = dayLengthEpoc - Hlength * 3600 - Mlength * 60
        if Mlength < 10: Mlength = '0%s' % Mlength
        if Slength < 10: Slength = '0%s' % Slength

        dgDict['atmoVisibility'] =      tmpDict.get('visibility', 0)
        dgDict['astroDayLength'] =      "%s:%s:%s" % (Hlength, Mlength, Slength)
        dgDict['astroSunrise'] =        tmpDict.get('sunrise', 0)
        dgDict['astroSunset'] =         tmpDict.get('sunset', 0)
        dgDict['astroDaySoltice'] =     float(tmpDict.get('sunsetEpoch', 0) + tmpDict.get('sunriseEpoch', 0)) * 0.5
        dgDict['atmoHumidity'] =        tmpDict.get('humidity', 0)
        dgDict['downloadDate'] =        tmpDict.get('datetimeEpoch', 0)
        dgDict['downloadTime'] =        tmpDict.get('datetimeEpoch', 0)

        dgDict['currentcloudCover'] =   tmpDict.get('cloudcover', 0)
        dgDict['currentlyIntensity'] =  tmpDict.get('precip', 0)
        dgDict['currentMoonPhase'] =    tmpDict.get('moonphase', 0)
        dgDict['currentPrecip'] =       tmpDict.get('precip', 0)
        dgDict['currentPressure'] =     tmpDict.get('pressure', 0)
        dgDict['currentProbability'] =  tmpDict.get('precipprob', 0)
        dgDict['currentWeatherCode'] =  tmpDict.get('icon', '?')
        dgDict['currentWeatherPicon'] = tmpDict.get('icon', '?')
        dgDict['currentWeatherTemp'] =  tmpDict.get('temp', 0)
        dgDict['currentWeatherText'] =  tmpDict.get('conditions','?')
        dgDict['currentlywindGust'] =   tmpDict.get('windgust', 0)
        dgDict['currentlywindSpeed'] =  tmpDict.get('windspeed', 0)
        dgDict['uvIndex'] =             tmpDict.get('uvindex', 0)
        dgDict['windChill'] =           tmpDict.get('feelslike', 0)
        dgDict['dewPoint'] =            tmpDict.get('dew', 0)
        dgDict['windDirection'] =       tmpDict.get('winddir', 0)
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
    else:
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
    APIKEY = open('/etc/enigma2/DGWeather/VisualWeather_apikey', 'r').read().strip()
    # !!!! openweathermap nie uzywa juz id_city tylko koordynatorow geo !!!!!
    latitude  = open('/etc/enigma2/DGWeather/geolatitude', 'r').read().strip()
    longitude = open('/etc/enigma2/DGWeather/geolongitude', 'r').read().strip()
    if APIKEY == '':
        print('Brak VisualWeather_apikey')
    elif latitude == '':
        print('Brak geolatitude')
    elif longitude == '':
        print('Brak geolongitude')
    else:
        dict = VisualCrossingDict(APIKEY, latitude, longitude, CountryCode)
        buildDGweatherDict(dict)
