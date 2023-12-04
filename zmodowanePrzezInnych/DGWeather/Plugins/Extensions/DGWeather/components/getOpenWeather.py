# pobiera o przygotowuje do uzycia dane json z OpenWeatherDict  do /tmp/dgWeather
# https://openweathermap.org/api
# forecast: api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API key}
# current:  api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API key}

#ponizsze dwie linie sa niezbedne bo uruchamiamy zabawki z innych katalogow
import sys
if '/usr/lib/enigma2/python/Plugins/Extensions/DGWeather/components/' not in sys.path:
    sys.path.append('/usr/lib/enigma2/python/Plugins/Extensions/DGWeather/components/')

from utils import *

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
        OpenWeatherDict(APIKEY, latitude, longitude, CountryCode)
    