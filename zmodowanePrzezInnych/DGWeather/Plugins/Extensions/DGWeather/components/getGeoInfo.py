# pobiera dane o lokalizacji
# https://nominatim.openstreetmap.org/reverse?format=json&lat=50.043&lon=22.04&zoom=18&addressdetails=1

import sys
if '/usr/lib/enigma2/python/Plugins/Extensions/DGWeather/components/' not in sys.path:
    sys.path.append('/usr/lib/enigma2/python/Plugins/Extensions/DGWeather/components/')

from utils import *

def getGeoInfo(lat, long):
    write_log('getGeoInfo(lat = "%s", long = "%s") >>>' % (lat, long))
    naszDict = {}
    if lat != '' and long != '':
        locationSettingsURL = 'lat=%s&lon=%s&zoom=18&addressdetails=1' %(lat, long)
        url = 'https://nominatim.openstreetmap.org/reverse?format=json&' + locationSettingsURL
        write_log('geoInfo URL : ' + str(url))
        webContent = downloadWebPage(url)
        naszDict = json.loads(webContent)
        saveJsonDict('GeoInfo.json', naszDict) #tylko, zeby wiedziec co jest dostepne
    else:
        write_log('Brak wymaganych danych lokalizacyjnych')
    write_log('GeoInfo() <<<')
    return naszDict

if __name__ == '__main__': # wychwytuje sytuacje gdy skrypt odpalany z konsoli
    # inicjacja zmiennych
    latitude  = open('/etc/enigma2/DGWeather/geolatitude', 'r').read().strip()
    longitude = open('/etc/enigma2/DGWeather/geolongitude', 'r').read().strip()
    if latitude == '':
        print('Brak geolatitude')
    elif longitude == '':
        print('Brak geolongitude')
    else:
        getGeoInfo(latitude, longitude)
    