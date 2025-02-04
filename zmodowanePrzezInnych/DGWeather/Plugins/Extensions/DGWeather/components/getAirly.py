# downloads Airly json data to /tmp/dgWeather
#ponizsze dwie linie sa niezbedne bo uruchamiamy zabawki z innych katalogow
import sys
if '/usr/lib/enigma2/python/Plugins/Extensions/DGWeather/components/' not in sys.path:
    sys.path.append('/usr/lib/enigma2/python/Plugins/Extensions/DGWeather/components/')

from utils import *

def getAirlyDict(airlyAPIKEY, airlyID, CountryCode):
    write_log('getAirlyDict() >>>')
    airlyDict = {'data': {}, 'info': {}}
    if airlyAPIKEY != '' and airlyID != '':
        airlyHeader = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:54.0) Gecko/20100101 Firefox/54.0', 
                       'Accept': 'application/json', 
                       'apikey': airlyAPIKEY,
                       'Accept-Language': CountryCode}
        #dane z czujnikow
        try:
            url = 'https://airapi.airly.eu/v2/measurements/installation?includeWind=true&indexType=AIRLY_CAQI&installationId=%s' % airlyID
            webContent = downloadWebPage(url, airlyHeader)
            airlyDict['data'] = json.loads(webContent)
        except Exception as e:
            Exc_log('Exception downloading airly data: %s' % str(e))

        #dane o lokalizacji
        try:
            if len(airlyDict['info']) == 0:
                url = 'https://airapi.airly.eu/v2/installations/%s' % airlyID
                webContent = downloadWebPage(url, airlyHeader)
                airlyDict['info'] = json.loads(webContent)
        except Exception as e:
            Exc_log('Exception downloading airly installations: %s' % str(e))
        saveJsonDict('airlyDict.json', airlyDict) #tylko, zeby wiedziec co jest dostepne
    else:
        write_log('missing data')
    write_log('getAirlyDict() <<<')
    return airlyDict

if __name__ == '__main__': # wychwytuje sytuacje gdy skrypt odpalany z konsoli
    # inicjacja zmiennych
    CountryCode = 'pl'
    airlyID = ''
    for cfg in ('/etc/enigma2/DGWeather/Airly_id', '/etc/enigma2/MSN_defaults/airlyID.0'):
        if os.path.exists(cfg) and os.stat(cfg).st_size != 0:
            airlyID = open(cfg, 'r').readline().strip()
            break
    airlyAPIKEY = ''
    for cfg in ('/etc/enigma2/Airly/api.txt', '/etc/enigma2/DGWeather/Airly_apikey', '/etc/enigma2/MSN_defaults/airlyAPIKEY'):
        if os.path.exists(cfg) and os.stat(cfg).st_size != 0: 
            airlyAPIKEY = open(cfg, 'r').readline().strip()
            break
    if airlyID == '':
        print('Missing airlyID')
    elif airlyAPIKEY == '':
        print('Missing airlyAPIKEY')
    else:
        getAirlyDict(airlyAPIKEY, airlyID, CountryCode)
    