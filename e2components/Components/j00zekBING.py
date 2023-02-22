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

if isPY2() == True:
    from urllib import urlretrieve
else:
    from urllib.request import urlretrieve

import json, os, requests, sys, time, urllib

def getPicOfTheDay(CountryCode = 'pl_PL', downloadPathAndFileName = '/usr/share/enigma2/BlackHarmony/icons/BingPicOfTheDay.jpg', mergePic = ''):
    retVal = False
    url = 'http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=%s' % CountryCode

    try:
        if isINETworking():
            if os.path.exists(downloadPathAndFileName) and (int(time.time()) - int(os.path.getmtime(downloadPathAndFileName))) < 86400:
                print('to early to get new bing pic of the day')
            else:
                #response = requests.get(webURL, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:54.0) Gecko/20100101 Firefox/54.0', 'Accept-Charset': 'utf-8'}, timeout=1)
                response = requests.get(url, timeout=1)
                response = response.content.decode()
                response = json.loads(response)
                if 'images' in response:
                    images = response['images']
                    for i in range(len(images)):
                        url = 'http://www.bing.com' + images[i]['url']
                        urlretrieve(url, downloadPathAndFileName)
                        if os.path.exists(downloadPathAndFileName):
                            print('new bing pic of the day downloaded')
                            retVal = True
                            break
    except Exception as e:
        print(str(e))
    
    #PIL
    mergedPic = mergePic.replace('.png','-Bing.png').replace('.jpg','-Bing.jpg')
    if mergePic == '':
        print('mergePic not provided, nothing to merge bing with')
    elif not os.path.exists(mergePic):
        print('mergePic does not exist, nothing to merge bing with')
    elif not os.path.exists(downloadPathAndFileName):
        print('no bing picture, nothing to merge to %s' % mergePic)
    elif retVal == False and os.path.exists(mergedPic) and (int(time.time()) - int(os.path.getmtime(mergedPic))) < 86400:
        print('to early to merge new bing pic of the day')
    else:
        try:
            from PIL import Image
            background = Image.open(downloadPathAndFileName)
            foreground = Image.open(mergePic)
            background.paste(foreground, (0, 0), foreground.convert('RGBA'))
            background = background.convert("P", palette=Image.ADAPTIVE, colors=256)
            background.save(mergedPic, format="PNG", quality=6, optimize=True, progressive=True)
            print('bing pic merged to %s and saved as %s' % (mergePic, mergedPic))
        except Exception as e:
            print(str(e))
            os.system('opkg update; opkg install python3-pillow;opkg install python-pillow')
    return retVal


#for tests outside e2
if __name__ == '__main__':
    CountryCode = 'pl_PL'
    downloadPathAndFileName = '/usr/share/enigma2/BlackHarmony/icons/BingPicOfTheDay.jpg'
    mergePic = '/usr/share/enigma2/BlackHarmony/bg_design/EPGPig.png'
    for myArg in sys.argv:
        if '=' in myArg:
            myArg = myArg.split('=', 1)
            param = myArg[0].strip()
            value = myArg[1].strip()
            if param == 'CountryCode': CountryCode = value
            elif param == 'downloadPathAndFileName': downloadPathAndFileName = value
            elif param == 'mergePic': mergePic = value
    getPicOfTheDay(CountryCode,downloadPathAndFileName,mergePic)
    #with open("/tmp/bing.log", "a") as f: f.write(str(sys.argv))
