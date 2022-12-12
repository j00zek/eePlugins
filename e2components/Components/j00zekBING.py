#!/usr/bin/python
#######################################################################
#
#    download BING image of the day
#    Coded by j00zek (c)2018
#
#    Uszanuj moja prace i nie kasuj/zmieniaj informacji kto jest autorem konwertera
#    Please respect my work and don't delete/change name of the converter author
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#     
#######################################################################

from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
try:
    from Components.j00zekComponents import isINETworking, isPY2
except Exception:
    from j00zekComponents import isINETworking, isPY2

import json
if isPY2() == True:
    from urllib import urlretrieve
else:
    from urllib.request import urlretrieve
import urllib
import requests
from os.path import exists as OsPathExists

def getPicOfTheDay(CountryCode = 'pl_PL', downloadPathAndFileName = '/usr/share/enigma2/BlackHarmony/icons/BingPicOfTheDay.jpg'):
    retVal = False
    url = 'http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=%s' % CountryCode

    try:
        if isINETworking():
            #response = requests.get(webURL, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:54.0) Gecko/20100101 Firefox/54.0', 'Accept-Charset': 'utf-8'}, timeout=1)
            response = requests.get(url, timeout=1)
            response = response.content.decode()
            response = json.loads(response)
            if 'images' in response:
                images = response['images']
                for i in range(len(images)):
                    url = 'http://www.bing.com' + images[i]['url']
                    urlretrieve(url, downloadPathAndFileName)
                    if OsPathExists(downloadPathAndFileName):
                        retVal = True
                        break
    except Exception as e:
        print(str(e))
       
    return retVal


#for tests outside e2
if __name__ == '__main__':
    getPicOfTheDay()