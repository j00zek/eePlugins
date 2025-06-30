# -*- coding: utf-8 -*-
"""
####################################################################### 
#
#   This script resolves issue with freezing E2 in case of network problems and speeds-up everything
#   Coded by j00zek (c)2020-2022
#     
####################################################################### 
"""
# chyba nie jest potrzebne from __future__ import absolute_import #zmiana strategii ladowania modulow w py2 z relative na absolute jak w py3
import sys

unicode = str
from urllib.request import urlretrieve as urllib_urlretrieve
from urllib.parse import unquote as urllib_unquote, quote as urllib_quote

import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

try:
    import requests
except Exception:
    if sys.platform != 'win32':
        exec('opkg install python3-requests')

import io, json, gettext, os, re, sys, time, threading, urllib, requests, traceback

try: 
    from mappings import * #laduje poprawnie przy uruchomieniu z konsoli
except:
    from Plugins.Extensions.MSNweather.MSNcomponents.mappings import * #laduje poprawnie przy imporcie przez inny skrypt
  
from datetime import datetime, timedelta, date
#from twisted.web.client import getPage, downloadPage
from xml.etree.cElementTree import fromstring as cet_fromstring
if sys.platform != 'win32':
    if not '/usr/lib/enigma2/python' in sys.path:
        sys.path.append('/usr/lib/enigma2/python')
    if not '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/' in sys.path:
        sys.path.append('/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/')

try: #ladowanie w e2
    from Components.j00zekSunCalculations import Sun
    from Components.j00zekMoonCalculations import phase, get_julian_datetime, phase_string
except Exception: #miejsce dla kodi
    pass

def IMGtoICON(imgFileName, skytext, currentInt, sunsetInt=None, sunriseInt=None, fcode = ''):
    global paramsDict
    #print(skytext, utfTOansi(skytext))
    retICON = ''
    foundBy = '?'
      
    if sunsetInt is None:
        sunsetInt = int(paramsDict['sunset']['TZhr'])
        sunriseInt = int(paramsDict['sunrise']['TZhr'])
        
    if currentInt >= sunriseInt and currentInt <= sunsetInt:
        DayOrNight = 'D'
    else:
        DayOrNight = 'N'

    if not skytext is None and skytext != '':
        retICON = skytext2skycode(utfTOansi(skytext))
        if retICON != '':
            foundBy = 'S'
            if '|' in retICON:
                retICON = retICON.split('|')
                if DayOrNight == 'D':
                    retICON = retICON[0]
                else:
                    retICON = retICON[1]
    
    if retICON == '' and fcode != '': # mapowanie przez kod foreca
        fcode = fcode.lower()
        if fcode.endswith('.png'):
            retICON = iconsMap.get(fcode, '')
        else:
            retICON = iconsMap.get( '%s.png' % fcode, '')
    
    if retICON == '': # mapowanie przez ikone MSN
        imgFileName = os.path.basename(imgFileName)
        retICON = iconsMap.get(utfTOansi(imgFileName), '')
        if retICON == '':
            print('Brakuje ikony dla skytext=%s, utfTOansi(skytext)=%s, imgFileName=%s' % (skytext, utfTOansi(skytext), os.path.basename(imgFileName)))
        else:
            foundBy = 'F'
    
    if os.path.exists('/hdd/MSN_icons_mappings.csv'):
        csvFile = '/hdd/MSN_icons_mappings.csv'
    else:
        csvFile = '/tmp/.MSNdata/MSN_icons_mappings.csv'
        if not os.path.exists(csvFile):
            with open(csvFile, 'w') as f: # for statistics header: msn_icon,D/N,sky_icon,skytext
                f.write('msn_icon\tD/N\tfoundBy\tsky_icon\tfcode\tskytext\n')
                f.close()
    lineToAppend = '%s\t%s\t%s\t%s\t%s\t%s' % (os.path.basename(imgFileName),DayOrNight,foundBy,retICON,fcode,utfTOansi(skytext))
    with open(csvFile, 'r+') as f: # for statistics header: msn_icon,D/N,sky_icon,skytext
        for line in f:
            if line.strip() == lineToAppend:
                lineToAppend = ''
                break
        if lineToAppend != '':
            f.write('%s\n' % lineToAppend)
        f.close()
    return retICON


def utfTOansi(text):
    text = text.replace(' ', '').replace('Ś', 's').replace('ś', 's').replace('ł', 'l').strip()
    text = text.replace('ę', 'e').replace('ć', 'c').replace('ó', 'o').strip().replace('ż', 'z').strip()
    text = text.replace('ö', 'oe').replace('Ü', 'Ue')
    return text.lower()


def decodeHTML(text):
    text = text.replace('%lf', '. ').replace('&#243;', 'ó')
    text = text.replace('&#176;', '°').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&apos;', "'").replace('&#65282;', '"').replace('&#xFF02;', '"')
    text = text.replace('&#228;', 'ä').replace('&#196;', 'Ă').replace('&#246;', 'ö').replace('&#214;', 'Ö').replace('&#252;', 'ü').replace('&#220;', 'Ü').replace('&#223;', 'ß')
    return text


def localeInit(lang, langPath):
    try:
        lang = lang[:2]
        os.environ['LANGUAGE'] = lang
        gettext.bindtextdomain('MSNweather', langPath)
        gettext.bindtextdomain('skytext2skycode', langPath)
        gettext.bindtextdomain('airQuality', langPath)
    except Exception as e:
        print('EXCEPTION in localeInit ', str(e))

def param2name(txt):
    txtL = txt.lower()
    retVal = gettext.dgettext('airQuality', txtL)
    if retVal == txtL:
        return txt.upper()
    else:
        return retVal

def _(txt):
    return gettext.dgettext('MSNweather', txt)

def skytext2skycode(skytext):
    retVal = gettext.dgettext('skytext2skycode', skytext)
    if retVal == skytext:
        return ''
    else:
        return retVal

def findInContent(ContentString, reFindString):
    retTxt = ''
    FC = re.findall(reFindString, ContentString, re.S)
    if FC:
        for i in FC:
            retTxt += i

    return retTxt

def getList(retList, ContentString, reFindString):
    FC = re.findall(reFindString, ContentString, re.S)
    if FC:
        for i in FC:
            retList.append(i)
    return retList

def getListItem(itemID, ContentString, reFindString):
        mList = getList([], ContentString, reFindString)
        if len(mList) > 0 and len(mList) > itemID:
            return mList[0]
        else:
            return ''
    
def downloadWebPage(webURL, webFileName, HEADERS={}):
    DBG = False
    if DBG:
        print("downloadWebPage\twebURL = '%s'\n\t\t\t\t\t\twebFileName = '%s',\n\t\t\t\t\t\tlen(HEADER)='%s'" % (webURL, webFileName, len(HEADERS)))
    try:
        if len(HEADERS) == 0:
        #Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:88.0) Gecko/20100101 Firefox/88.0
        #Exceeded 30 redirects
            #used previously: Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:54.0) Gecko/20100101 Firefox/54.0
            #Mozilla/5.0 (Android 7.0; Mobile; rv:54.0) Gecko/54.0 Firefox/54.0
            #Mozilla/5.0 (Windows Phone 10.0; Android 6.0.1; Microsoft; Lumia 950) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Mobile Safari/537.36 Edge/15.14977

            HEADERS = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:88.0) Gecko/20100101 Firefox/88.0', 
                        'Accept-Charset': 'utf-8', 
                        'Content-Type': 'text/html; charset=utf-8'
                      }
        if webFileName in ('motionBurze','SmogTok'):
            resp = requests.get(webURL, headers=HEADERS, timeout=7, verify=False)
        else:
            resp = requests.get(webURL, headers=HEADERS, timeout=7)
        webContent = resp.content
        webHeader = resp.headers
        if webFileName != 'motionBurze' and not webFileName.endswith('.png'):
            try:
                webContent =  urllib_unquote(webContent)
            except Exception:
                webContent =  urllib_unquote(webContent.decode('utf-8'))
            webContent = decodeHTML(webContent)
    except Exception as e:
        print("EXCEPTION '%s' in downloadWebPage() for %s" % (str(e), webURL) )
        webContent = ''

    if webContent != '':
        if webFileName == 'data_msn.web':
            analyze_data_msn(webContent)
        elif webFileName == 'ForecaMeteogram':
            foreca(webContent)
        elif webFileName.startswith('Fmeteo_'):
            ForecaMeteo(webContent, webFileName)
        elif webFileName == 'motionBurze':
            motionBurze(webContent)
        elif webFileName == 'looko2':
            looko2(webContent)
        elif webFileName == 'GiosInfo':
            GiosInfo(webContent)
        elif webFileName == 'Gios':
            Gios(webContent)
        elif webFileName == 'Blebox':
            Blebox(webContent)
        elif webFileName == 'OpenSense':
            OpenSense(webContent)
        elif webFileName == 'SmogTok':
            smogTok(webContent)
        elif webFileName == 'data_thingSpeak.xml':
            thingSpeakCallback(webContent)
        elif webFileName == 'data_msn.xml':
            xmlCallback(webContent)
        elif webFileName.startswith('msn_api'):
            msn_api(webContent, webFileName)
        elif webFileName.startswith('airlyData_') and webFileName.endswith('.json'):
            dictTMP = json.loads(webContent)
            dictTMP['RateLimit-Limit-minute'] = webHeader.get('X-RateLimit-Limit-minute', '')
            dictTMP['RateLimit-Remaining-minute'] = webHeader.get('X-RateLimit-Remaining-minute', '')
            dictTMP['RateLimit-Limit-day'] = webHeader.get('X-RateLimit-Limit-day', '')
            dictTMP['RateLimit-Remaining-day'] = webHeader.get('X-RateLimit-Remaining-day', '')
            paramsDict['airlyData.json'] = dictTMP
            saveJsonDict(webFileName, dictTMP, False, paramsDict['DEBUG'])
        elif webFileName.startswith('airlyInfo_') and webFileName.endswith('.json'):
            dictTMP = json.loads(webContent)
            saveJsonDict(webFileName, dictTMP, True, True)
        elif webFileName.endswith('.json'):
            dictTMP = json.loads(webContent)
            saveJsonDict(webFileName, dictTMP, False, paramsDict['DEBUG'])
        else:
            if not webFileName.startswith('/'):
                webFileName = os.path.join(paramsDict['tmpFolder'], webFileName)
            if webFileName.endswith('.png'):
                with open(webFileName, 'wb') as (f):
                    f.write(webContent)
            else:
                with open(webFileName, 'w') as (f):
                    f.write(webContent)


def saveFile(fileNameWithPath, fileContent):
    try:
        open(fileNameWithPath, 'w').write(fileContent)
    except Exception as e:
        print("EXCEPTION '%s' saving '%s'" % (str(e), fileNameWithPath) )   

def webToDict(webContent, webFileName, DBG):
    try:
        dictTMP = json.loads(webContent)
        if DBG == True:
            saveJsonDict('%s.json' % webFileName, dictTMP, doSort=True, pushSave=True)
    except Exception as e:
        dictTMP = {}
    return dictTMP
    

def saveJsonDict(fileName, jsonDict, doSort=True, pushSave=False):
    DBG = False
    paramsDict[fileName] = jsonDict
    if pushSave == True or pushSave == 'True' or paramsDict['DEBUG'] == 'True':
        if DBG:
            print('saveJsonDict(%s)' % os.path.join(paramsDict['tmpFolder'], fileName))
        with io.open(os.path.join(paramsDict['tmpFolder'], fileName), 'w', encoding='utf8') as (outfile):
            json_data = json.dumps(jsonDict, indent=4, sort_keys=True, ensure_ascii=False)
            outfile.write(unicode(json_data))


def readJson(fileName):
    fileName = os.path.join(paramsDict['tmpFolder'], fileName)
    retDict = {}
    if os.path.exists(fileName):
        with open(fileName, 'r') as (json_file):
            data = json_file.read()
            json_file.close()
            retDict = json.loads(data)
    return retDict


def initThread(webURL, webFileName, HEADER=[]):
    global threads
    x = threading.Thread(name=webFileName, target=downloadWebPage, args=(webURL, webFileName, HEADER))
    threads.append(x)
    x.start()


def ISO3339toDATETIME(ISO3339time, offset=0):
    defDBG = False
    try:
        systemTZ = datetime.now().hour - datetime.utcnow().hour
        Y = int(ISO3339time[:4])
        M = int(ISO3339time[5:7])
        D = int(ISO3339time[8:10])
        h = int(ISO3339time[11:13])
        m = int(ISO3339time[14:16])
        DateTimeObject = datetime(Y, M, D, h, m)
        date = DateTimeObject.strftime('%d/%m/%Y')
        time = DateTimeObject.strftime('%H:%M')
        if ISO3339time.endswith('z') or ISO3339time.endswith('Z'): #czas podany w UTC
            timeOffset = 0
        elif ISO3339time[-6:-5] in ['+','-']:
            timeOffset = int(ISO3339time[-6:-3])
        else:
            timeOffset = systemTZ
        if systemTZ != timeOffset:
            DateTimeObject = DateTimeObject + timedelta(hours=systemTZ - timeOffset)
            date = DateTimeObject.strftime('%d/%m/%Y')
            time = DateTimeObject.strftime('%H:%M')
        if defDBG: print('\t ISO3339toDATETIME(%s) > systemTZ=%s, timeOffset=%s >>> localDate=%s, localTime=%s' %(ISO3339time, systemTZ, timeOffset, date, time ))
    except Exception as e:
        print("EXCEPTION in ISO3339toDATETIME('%s'): %s" % (ISO3339time, str(e)))
    return (date, time, DateTimeObject)


def manageCurrenDataWeatherItem(doUpdate=False, keyName=None, colorCode=None, inList=False, name=None, source=None, val=None, units=None, valInfo=None, longName=None):
    defDBG = False
    if defDBG:
        print('manageCurrenDataWeatherItem >>>')
    if keyName is None or keyName == '':
        print('manageCurrenDataWeatherItem. keyName is None')
        return
    currentDict = paramsDict['dictWeather']['currentData']
    keyDict = currentDict.get(keyName, {})
    if doUpdate == True or len(keyDict) == 0:
        if colorCode is None:
            colorCode = keyDict.get('colorCode', '')
        if name is None or name == '':
            name = _(keyDict.get('name', keyName))
        if source is None:
            source = keyDict.get('source', 'unknown')
        if val is None:
            val = keyDict.get('val', '')
        if units is None:
            units = keyDict.get('units', '')
        if keyName == 'pressure':
            if units == '':
                units = 'hPa'
        elif keyName in ('humidity', 'rel. humidity'):
            if units == '':
                units = '%'
        elif keyName in ('temperature', 'feelslike'):
            if units == '':
                units = '°' + paramsDict['degreetype']
            colorCode = Temperature2strColor(val)
        elif keyName in ('pm1', 'pm10', 'pm25', 'pm2.5', 'o3', 'no2', 'so2', 'c6h6'):
            if units == '':
                units = 'µg/m3'
            colorCode, Info = airQualityInfo(keyName, val)
            if Info == '':
                valInfo = colorCode + val + units
            else:
                valInfo = colorCode + _(Info)
        elif keyName == 'co':
            #GIOS Wyniki pomiarów wszystkich zanieczyszczeń  udostępnianych poprzez API wyświetlane są w jednostce μg/m3 
            #(również wyniki pomiarów CO - tlenku węgla, dla którego wyniki pomiarów prezentowane na mapie bieżących 
            #danych pomiarowych portalu Jakość Powietrza oraz w aplikacji mobilnej "Jakość Powietrza w Polsce" przeliczone są na mg/m3)
            if units == '':
                units = 'mg/m3'
            colorCode, Info = airQualityInfo(keyName, float(val) / 1000)
            if Info == '':
                valInfo = colorCode + val + units
            else:
                valInfo = colorCode + _(Info)
        if valInfo is None or valInfo == '' or valInfo == val:
            valInfo = colorCode + val + units
        if keyName == 'observationtime':
            if name is None or name == '':
                name = _('MSN sync time')
            if int(val[:2]) > int(time.strftime('%H', time.localtime(int(time.time())))):
                tmph = int(val[:2]) - 1
                if tmph < 10:
                    val = '0%s:%s' % (tmph, val[3:])
                else:
                    val = '%s:%s' % (tmph, val[3:])
            tmpTxt = datetime.now()
            paramsDict['dictWeather']['currentData']['observationtime'] = {'name': name, 'date': str(tmpTxt.strftime('%d/%m/%Y')), 'time': val, 'datetime': str(tmpTxt.strftime('%d/%m/%Y') + ' ' + val)}
        elif longName is None:
            paramsDict['dictWeather']['currentData'][keyName] = {'colorCode': colorCode, 'inList': inList, 'name': name, 'source': source, 'val': val, 'valInfo': valInfo, 'units': units}
        else:
            paramsDict['dictWeather']['currentData'][keyName] = {'colorCode': colorCode, 'inList': inList, 'name': name, 'source': source, 'val': val, 
               'valInfo': valInfo, 'units': units, 'longName': longName}
        
        if defDBG:
            print("manageCurrenDataWeatherItem. paramsDict['dictWeather']['currentData'][%s]= %s" % (keyName, paramsDict['dictWeather']['currentData'][keyName]))
    return

def calculateSun():
    try:
        sun = Sun()
        paramsDict['sunset'] = sun.getSunsetTime(float(paramsDict['geolongitude']), float(paramsDict['geolatitude']))
        paramsDict['sunrise'] = sun.getSunriseTime(paramsDict['geolongitude'], paramsDict['geolatitude'])
        paramsDict['dictWeather']['currentData']['sun'] = {'sunset': paramsDict['sunset'], 'sunrise': paramsDict['sunrise']}
        dayLengthDict = sun.getDayLength(float(paramsDict['geolongitude']), float(paramsDict['geolatitude']))
        DayDiffTimesDict = sun.getDayDiffTimes(float(paramsDict['geolongitude']), float(paramsDict['geolatitude']))
        paramsDict['dictWeather']['currentData']['sun']['dayLength'] = {'dec': dayLengthDict['DayLengthDec'], 'time': dayLengthDict['dayLength'], 
           'dec2shortest': DayDiffTimesDict['diffToShortestDec'], 
           'time2shortest': DayDiffTimesDict['diffToShortest'], 
           'dec2longest': DayDiffTimesDict['diffToLongestDec'], 
           'time2longest': DayDiffTimesDict['diffToLongest']}
    except Exception as e:
        print("\t\tException in ['dictWeather']['currentData']['sun'] branch: %s" % str(e))

def calculateMoon():
    try:
        paramsDict['dictWeather']['currentData']['moon'] = phase(get_julian_datetime(datetime.now()))
        val = str(round(paramsDict['dictWeather']['currentData']['moon']['illuminated'] * 100, 1)) + '%'
        paramsDict['dictWeather']['currentData']['moon']['illuminated_percentage'] = val
        valInfo = phase_string(paramsDict['dictWeather']['currentData']['moon']['phase'])
        paramsDict['dictWeather']['currentData']['moon']['phase_name'] = _(valInfo)
        import suncalc
        paramsDict['moonTimes'] = suncalc.getMoonTimes(datetime.now(),  float(paramsDict['geolatitude']), float(paramsDict['geolongitude']) )
        val = paramsDict['moonTimes']['moonrise']
        valUTC = paramsDict['moonTimes']['moonriseUTC']
        paramsDict['dictWeather']['currentData']['moon']['moonrise'] = { "TZhr": val.hour, "UTChr": valUTC.hour,
                "TZtime": val.strftime('%H:%M'), "UTCtime": valUTC.strftime('%H:%M'),
                "min": val.minute, 
                }
        val = paramsDict['moonTimes']['moonset']
        valUTC = paramsDict['moonTimes']['moonsetUTC']
        paramsDict['dictWeather']['currentData']['moon']['moonset'] = {"TZhr": val.hour, "UTChr": valUTC.hour,
                "TZtime": val.strftime('%H:%M'), "UTCtime": valUTC.strftime('%H:%M'),
                "min": val.minute, 
                }
    except Exception as e:
        print("\t\tException in ['dictWeather']['currentData']['moon'] branch: %s" % str(e))


def buildHistogram():
    defDBG = False
    print('\tbuildHistogram(%s) >>>' % paramsDict['Histogram'])
    if paramsDict['Histogram'] == 'True':
        myFile = os.path.join(paramsDict['pluginPath'], 'histograms.data')
        currTime = int(time.time())
        currData = paramsDict['dictWeather'].get('currentData', None)
        if currData is not None:
            if defDBG:
                print('\tlen(currData)=%s' % len(currData))
            record = '%s|%s|%s=%s|%s=%s|%s=%s|%s=%s|currTemp=%s|skyCode=%s|observationtime=%s|iconFilename=%s|winddir=%s' % (
             currTime, time.strftime('%d%H', time.localtime(currTime)),
             currData['feelslike']['name'], currData['feelslike']['val'].strip(),
             currData['wind_speed']['name'], currData['wind_speed']['val'].strip(),
             currData['pressure']['name'], currData['pressure']['val'].strip(),
             currData['humidity']['name'], currData['humidity']['val'].strip(),
             currData['temperature']['val'], currData['skycode']['val'].strip(),
             currData['observationtime']['time'], currData['iconfilename']['val'].strip(),
             currData['wind_dir']['val'].strip())
            if defDBG:
                print('\t storing current data for histogram in %s' % myFile)
            if defDBG:
                print('\t\t%s' % record)
            data = []
            if os.path.exists(myFile):
                with open(myFile, 'r') as (f):
                    for line in f:
                        if len(line.strip()) > 0:
                            if len(line.split('|')) > 2:
                                try:
                                    storedTime = int(line.split('|')[0])
                                    if storedTime > currTime - 172800:
                                        data.append(line.strip())
                                except Exception:
                                    pass

                    f.close()
            data.append(record)
            with open(myFile, 'w') as (f):
                f.write(('\n').join(data))
                f.close()
    if defDBG:
        print('buildHistogram  <<<')
    return

def foreca(webContent):
    defDBG = True
    if defDBG: print('thread.foreca >>>')
    try:
        ids = re.findall("id: '(.*?)'", webContent, re.S)
        loc_id = str(ids[0])
        URL = 'https://www.foreca.net/meteogram.php?loc_id=%s&amp;mglang=%s&amp;units=metric&amp;tf=24h' % (loc_id, paramsDict['language'][:2])
        if defDBG:
            print("thread.foreca() URL='%s'" % URL)
        HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:54.0) Gecko/20100101 Firefox/54.0', 'Accept-Language': paramsDict['language']}
        downloadWebPage(URL, os.path.join(paramsDict['pluginPath'], 'icons', 'meteogram.png'), HEADERS)
    except Exception as e:
        print('EXCEPTION in thread.foreca() %s' % str(e))

def ForecaMeteo(webContent, webFileName):
    print('thread.ForecaMeteo(%s) >>>' % webFileName)
    DBG = False
    #wstepne wyciecie smieci
    FC = findInContent(webContent, '<section id="pageContent">.*<footer>')
    if DBG == True:
        saveFile('%s.FC' % os.path.join(paramsDict['tmpFolder'], webFileName), str(FC).replace('><div','>\n<div'))
    paramsDict['%s.FC' % webFileName] = FC


def analyze_ForecaMeteo(webFileName):
    print('\tanalyze_ForecaMeteo(%s) >>>' % webFileName)
    DBGnow = False
    DBGhourly = False
    DBGdaily = False
    FC = paramsDict.get('%s.FC' % webFileName, 'NO data for %s' % webFileName)
    if webFileName == 'Fmeteo_10-day-forecast':
        paramsDict['Fmeteo_10-day-forecast'] = {}
        cutContent = findInContent(FC, '<div class="dayContainer">(.*?)<div class="explainer">')
        if DBGdaily == True:
            saveFile(os.path.join(paramsDict['tmpFolder'], 'Fmeteo_10-day-forecast.CC'), cutContent.replace('><div','>\n<div'))
        if len(cutContent) < 1:
            print('\t\t analyze_ForecaMeteo > nie znaleziono danych dziennych !!!!!!')
        else:
            Lines = getList([], cutContent, '<div class="day">(.*?)</span></div></div></div></div></a></div>')
            if DBGdaily:
                open(os.path.join(paramsDict['tmpFolder'], 'Fmeteo_10-day-forecast.cutContent'), 'w').write('DAILY LINES:\n')
                for line in Lines:
                    open(os.path.join(paramsDict['tmpFolder'], 'Fmeteo_10-day-forecast.cutContent'), 'a').write('!!!!!!!!!!!!!!!!!!! LINE:\n' + str(line) + '\n')

            for Line in Lines:
                tmpList = getList([], Line, r'.*hourly\?day=([0-9]*).*class="weekday">(.*)<\/div>.*dataContainer.*class="([^"]*).*class="date">([0-9\.]*)<.*class="symb" src="([^"]*).*alt="([^"]*).*class="temp">.*temp_c">([^&]*).*class="temp">.*temp_c">([^&]*).*class="wind".*src="[^"]*/([^"]*).*alt="([^"]*).*wind_kmh"><em>([^<]*).*wind_kmh"><em>')
                if len(tmpList) > 0:
                    tmpList = tmpList[0]
                if DBGdaily:
                    open(os.path.join(paramsDict['tmpFolder'], 'Fmeteo_10-day-forecast.cutContent'), 'a').write('\nZnaleziono dane: ')
                    for tmpitem in tmpList:
                        open(os.path.join(paramsDict['tmpFolder'], 'Fmeteo_10-day-forecast.cutContent'), 'a').write('"%s"\t' % str(tmpitem))
                #tmpList zawiera
                #Id  Dzien tygodnia pogoda   dzien  ikona pogody                       opis pogody  Temp Max   Temp min    ikona wiatru kierunek predkosc km/h
                # "0"   "pt."       "sunny"      "8.10" "/public/images/symbols/d000.svg"       "Pogodnie"       "+14"      "+5"             "w90.svg"     "E"     "14"
                
                id = tmpList[0]
                dataEmptymsg = '' #tmpList[2]
                ariaLabel = '' # tmpList[3]
                weekday = tmpList[1].replace('.','')
                monthday = tmpList[3].split('.')[0]
                Month = tmpList[3].split('.')[1]
                imgurl = 'https://www.foreca.com/' + tmpList[4]
                if tmpList[5] == "Pochmurnie i niewielkie opady deszcz":
                   skytext = "Pochmurnie i niewielkie opady deszczu"
                else:
                    skytext = _(tmpList[5])
                data_icon = '' # tmpList[8]
                rainprecip = '' # tmpList[9]
                temp_high = tmpList[6].replace('+','') + '°'
                temp_low = tmpList[7].replace('+','') + '°'
                imgfilename = os.path.basename(imgurl).replace('.svg','.png')
                skycode = iconsMap.get(imgfilename, '').replace('.png','')
                imgfilename =  '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/%s' % imgfilename
                if skycode == '':
                    skycode = IMGtoICON(imgfilename, skytext, 12).replace('.png','')
                iconfilename = '%s%s.png' % (paramsDict['iconPath'], skycode)
                
                dataDetailDict = {'id':             id,
                                  'weekday':        weekday,
                                  'shortweather':   tmpList[2],
                                  'day':            monthday,
                                  'weathericon':    tmpList[4],
                                  'skytext':        skytext,
                                  'tempmax':        tmpList[6],
                                  'tempmin':        tmpList[7],
                                  'windicon':       tmpList[8],
                                  'windDir':        tmpList[9],
                                  'windSpeed':      tmpList[10] + ' km/h',
                                }

                dicthourly = {'times': paramsDict.get('Fmeteo_hourly_day_%s' % id + 'timesList',[]) ,
                              'precipitations': paramsDict.get('Fmeteo_hourly_day_%s' % id + 'precipitationsList',[]),
                              'skyCodes': paramsDict.get('Fmeteo_hourly_day_%s' % id + 'skyCodesList',[]),
                              'skyImages': paramsDict.get('Fmeteo_hourly_day_%s' % id + 'skyImagesList',[]),
                              'skyTexts': paramsDict.get('Fmeteo_hourly_day_%s' % id + 'skyTextsList',[]),
                              'temperatures': paramsDict.get('Fmeteo_hourly_day_%s' % id + 'temperaturesList',[]),
                              'wind': paramsDict.get('Fmeteo_hourly_day_%s' % id + 'windList',[]),
                              'windDir': paramsDict.get('Fmeteo_hourly_day_%s' % id + 'windDirList',[]),
                             }

                paramsDict['Fmeteo_10-day-forecast']['Record=%s' % id] = {'day': weekday, 'forecast': ariaLabel, 
                   'weekday': weekday, 
                   'monthday': monthday, 
                   'imgurl':  '', #imgurl, 
                   'skytext': skytext, 
                   'data_icon': data_icon, 
                   'temp_high': temp_high, 
                   'temp_low': temp_low, 
                   'rainprecip': rainprecip, 
                   'skycode': skycode, 
                   'imgfilename': imgfilename, 
                   'iconfilename': iconfilename, 
                   'dictdetalis': dataDetailDict, 
                   'dicthourly': dicthourly,
                   'summary': str('%s/ %s/ %s\n%s' % (temp_high, temp_low, rainprecip, skytext)),
                   'date_summary': str('%s. %s %s' % (weekday, monthday, Month)),
                   'dataEmptymsg': dataEmptymsg}

            if DBGdaily == True: saveJsonDict('Fmeteo_10-day-forecast.json', paramsDict['Fmeteo_10-day-forecast'], False, True)
    elif webFileName.startswith('Fmeteo_hourly_day_'):
        paramsDict[webFileName] = {}
        cutContent = findInContent(FC, '<div class="hourContainer">(.*?)<div class="explainer">')
        cutContent = cutContent.replace('<div class="hour last">','<div class="hour">')#zmiana dla ostatniej godziny dla podzialu
        cutContent = cutContent.replace('<div class="hour">', '<ENDHOURCLASS><div><div class="hour">') #znacznik konca dla latwiejszego podzialu
        cutContent += '<ENDHOURCLASS>' #i na koncu danych
        if DBGhourly == True:
            saveFile(os.path.join(paramsDict['tmpFolder'], '%s.CC' % webFileName), cutContent.replace('><div','>\n<div'))
        if len(cutContent) < 1:
            print('\t\t nie znaleziono danych dla %s !!!!!!' % webFileName)
        else:
            Lines = getList([], cutContent, '<div class="hour">(.*?)<ENDHOURCLASS>')
            if DBGhourly:
                open(os.path.join(paramsDict['tmpFolder'], '%s.Lines' % webFileName), 'w').write('HOURLY LINES:\n')
                for line in Lines:
                    open(os.path.join(paramsDict['tmpFolder'], '%s.Lines' % webFileName), 'a').write('!!!!!!!!!!!!!!!!!!! LINE:\n' + str(line) + '\n')
            id = 0
            maxRainPrecip = 0
            avgRainPrecip = 0

            paramsDict[webFileName + 'timesList'] = []
            paramsDict[webFileName + 'precipitationsList'] = []
            paramsDict[webFileName + 'skyCodesList'] = []
            paramsDict[webFileName + 'skyImagesList'] = []
            paramsDict[webFileName + 'skyTextsList'] = []
            paramsDict[webFileName + 'temperaturesList'] = []
            paramsDict[webFileName + 'windList'] = []
            paramsDict[webFileName + 'windDirList'] = []

            for Line in Lines:
                tmpList = getList([], Line, '.*<span class="value time time_24h">([0-9]*).*class="symb"><img src="([^"]*).*alt="([^"]*).*class="value temp temp_c [a-z]*">([^<]*).*feelsLike.*<span class="value temp temp_c">([^<]*).*class="humidity">([^<]*).*<span class="value rain rain_mm">.*[Pp]recip[^>]*([^<]*).*<div class="wind"><img src="([^"]*).*alt="([^"]*).*<span class="value wind wind_kmh">([^<]*).*[Pp]recip[^>]*>(.*)<.span>')
                if len(tmpList) == 0:
                    open(os.path.join(paramsDict['tmpFolder'], '%s.NotParsedLine' % webFileName), 'a').write('!!!!!!!!!!!!!!!!!!! LINE:\n' + str(line) + '\n')
                    break
                else:
                    tmpList = tmpList[0]
                if DBGhourly:
                    open(os.path.join(paramsDict['tmpFolder'], '%s.Lines' % webFileName), 'a').write('\nZnaleziono dane: ')
                    for tmpitem in tmpList:
                        open(os.path.join(paramsDict['tmpFolder'], '%s.Lines' % webFileName), 'a').write('"%s"\t' % str(tmpitem))
                #tmpList zawiera 
                #time_24h symbol_pogody nazwa_pogody temp_c warm feelsLike humidity rain_mm wind_arrow wind_direction wind_kmh rain_precip
                dataHourlyDict = {'time_24h':       tmpList[0],
                                  'symbol_pogody':  tmpList[1].replace('.svg','.png').replace('/public/images/symbols/','/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/'),
                                  'nazwa_pogody':   _(tmpList[2]),
                                  'temp_c warm':    tmpList[3],
                                  'feelsLike':      tmpList[4],
                                  'humidity':       tmpList[5],
                                  'rain_mm':        tmpList[6],
                                  'wind_arrow':     tmpList[7].replace('.svg','.png').replace('/public/images/symbols/','/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/'),
                                  'wind_direction': tmpList[8],
                                  'wind_kmh':       tmpList[9],
                                  'rain_precip':    tmpList[10],
                                }
                try:
                    ltime = tmpList[0]
                    #print(ltime)
                    skytext = tmpList[2]
                    imgurl = 'https://www.foreca.com/' + tmpList[1]

                    imgfilename = os.path.basename(imgurl).replace('.svg','.png')
                    skycode = iconsMap.get(imgfilename, '').replace('.png','')
                    imgfilename =  '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/%s' % imgfilename
                    if skycode == '':
                        skycode = IMGtoICON(imgfilename, skytext, int(ltime)).replace('.png','')
                    iconfilename = '%s%s.png' % (paramsDict['iconPath'], skycode)

                    temperature = tmpList[3].replace('+','') + '°'
                    rainprecip = str(re.findall('([0-9]+)', tmpList[10])[0]) #sama wartosc
                    try:
                        tmpRP = int(rainprecip)
                        #print(tmpRP)
                        if maxRainPrecip < tmpRP:
                            maxRainPrecip = tmpRP
                        if avgRainPrecip == 0:
                            avgRainPrecip = tmpRP
                        else:
                            avgRainPrecip = (avgRainPrecip + tmpRP) / 2
                    except Exception as e:
                        print('Exception', str(e))
                    paramsDict[webFileName]['Record=%s' % id] = {'time': ltime, 'skytext': skytext, 'imgurl': '', #imgurl, 
                        'temperature': temperature, 'rainprecip': rainprecip + '%', 'skycode': skycode, 
                        'imgfilename': imgfilename, 'iconfilename': iconfilename,
                        'dicthourly':  dataHourlyDict, #to chwilowo dodane bo nie pamietam jak to wygladalo w msnweb
                        'summary':     str('%s\n\n\n%s\nTemp. %s\nOpady %s' % (ltime, skytext, temperature, rainprecip))
                        }

                    if paramsDict['FmeteoRainPrecip'] == 'maxRainPrecip':
                        paramsDict['dailyRainPrecip-' + webFileName[-1:]] = '<' + str(maxRainPrecip) + '%'
                    else:
                        paramsDict['dailyRainPrecip-' + webFileName[-1:]] = str(avgRainPrecip) + '%'
                    id += 1
                
                    paramsDict[webFileName + 'timesList'].append(ltime)
                    paramsDict[webFileName + 'precipitationsList'].append(rainprecip)
                    paramsDict[webFileName + 'skyCodesList'].append(skycode)
                    paramsDict[webFileName + 'skyImagesList'].append(iconfilename)
                    paramsDict[webFileName + 'skyTextsList'].append(skytext)
                    paramsDict[webFileName + 'temperaturesList'].append(tmpList[3].replace('+',''))
                    paramsDict[webFileName + 'windList'].append(tmpList[9].replace(' kmh',''))
                    paramsDict[webFileName + 'windDirList'].append(tmpList[8])

                except Exception as e:
                    if DBGhourly:
                        print('\t\tException analyzing %s: %s' % ( webFileName, str(e)))
            if DBGhourly == True: saveJsonDict('%s.json' % webFileName, paramsDict[webFileName], False, True)
            return
    elif webFileName == 'Fmeteo_today':
        paramsDict[webFileName] = {}
        cutContent = findInContent(FC, '<div class="row">(.*?)<div class="dayrow">')
        cutContent4Observations = findInContent(FC, '<div class="observationsContainer">(.*?)<div class="explainer">')
        cutContent4Observations = cutContent4Observations.replace('<div class="location">','<endloc>\n<div class="location">') + '<endloc>'
        
        #czasami niektore lokalizacje niemaja opisu, wybieramy taką ktora go ma
        cutObservation = ''
        idx = 0
        while idx < len(cutContent4Observations):
            cutObservation = getList([],cutContent4Observations, '<div class="locationName">(.*?)<endloc>')[idx]
            if getListItem(0, cutObservation, '<div class="symbolText">([^<]*)') != '':
                break
            idx += 1
            
        if DBGnow == True:
            saveFile(os.path.join(paramsDict['tmpFolder'], '%s.CC' % webFileName), '%s\n\nOBSERVATIONS:\n\n%s\nSELECTED:\n%s' %(cutContent.replace('><div','>\n<div'), 
                                                                                                       cutContent4Observations.replace('><div','>\n<div'),
                                                                                                       cutObservation
                                                                                                       )
                    )
        if len(cutContent) < 1:
            print('\t\t nie znaleziono danych dla %s !!!!!!' % webFileName)
        else:
            if 1: #skytext
                keyName = 'skytext'
                source = 'foreca'
                doUpdate = False
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                name = _('Current information')
                val = _(getListItem(0, cutObservation, '<div class="symbolText">([^<]*)'))
                if val == '':
                    if DBGnow == True: print('skytext nie znaleziony w pierwszej lokalizacji, sprawdzam pozostale')
                    val = getListItem(0, cutContent4Observations, '<div class="symbolText">([^<][^<]*)')
                if val != '':
                    valInfo = colorCode + val + units
                    manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #feelslike
                keyName = 'feelslike'
                source = 'foreca'
                doUpdate = False
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                inList = True
                units = '°' + paramsDict['degreetype']
                val = getListItem(0, cutObservation, '<p class="feelsLike">.*class="value temp temp_c">[+]*([-0-9]*)')
                if val != '--' and val != '':
                    colorCode = Temperature2strColor(val)
                    valInfo = colorCode + val + units
                    name = getListItem(0, cutObservation, 'div class="rightData"><p class="feelsLike">([^<]*)')
                    name = name.strip().replace('emperatura', 'emp.').replace('emperature', 'emp.').replace('emperatur', 'emp.').replace('Odczuwalna temp.','Temp. odczuwalna')
                    manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #wind_speed
                keyName = 'wind_speed'
                source = 'foreca'
                doUpdate = False
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                inList = True
                name = _('wind')
                val = getListItem(0, cutObservation, '<span class="value wind wind_kmh">([0-9]+)')
                if val != '':
                    units = 'km/h'
                    valInfo = None
                    manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #wind_dir
                keyName = 'wind_dir'
                source = 'foreca'
                doUpdate = False
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                name = _('Wind direction')
                val = getListItem(0, cutObservation, '<div class="wind">.*.svg".*alt="([^"]*)')
                if val != '':
                    valInfo = getWindIconName(val)
                    manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #pressure
                keyName = 'pressure'
                source = 'foreca'
                doUpdate = False
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                inList = True
                name = _('Pressure')
                val = getListItem(0, cutObservation, '<span class="value pres pres_hpa">([0-9]*)')
                if val != '':
                    units = 'hPa'
                    valInfo = colorCode + val + units
                    manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #visibility
                keyName = 'visibility'
                source = 'foreca'
                doUpdate = False
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                inList = True
                name = getListItem(0, cutObservation, '<p class="visibility">([^<]*)').strip()
                val = getListItem(0, cutObservation, '<p class="visibility">.*class="value vis vis_km">([0-9]*)')
                if val != '':
                    units = getListItem(0, cutObservation, '<p class="visibility">.*class="value vis vis_km">[0-9]*[ ]*([^<]*)')
                    if units == 'm' and val.isdigit():
                        val = int(val)
                        if val >= 10000:
                            units = 'km'
                            val = val / 1000
                        elif val >= 1000:
                            units = 'km'
                            val = round(val / 1000.0, 1)
                            if int(val) == val:
                                val = int(val)
                    valInfo = colorCode + str(val) + units
                    manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #humidity
                keyName = 'humidity'
                source = 'foreca'
                doUpdate = False
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                inList = True
                name = getListItem(0, cutObservation, 'class="humidity">([^<]*)').strip()
                val = getListItem(0, cutObservation, 'class="humidity">.*<span class="value">([0-9]*)')
                if val != '':
                    units = '%'
                    valInfo = colorCode + val + units
                    manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #dew_point_temp
                keyName = 'dew_point_temp'
                source = 'foreca'
                doUpdate = False
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                inList = True
                units = '°' + paramsDict['degreetype']
                val = getListItem(0, cutObservation, '<p class="dewpoint">.*class="value temp temp_c">[+]*([-0-9]*).*class="humidity">')
                if val != '':
                    colorCode = Temperature2strColor(val)
                    valInfo = colorCode + val + units
                    name = getListItem(0, cutObservation, '<p class="dewpoint">([^<]*)')
                    name = name.strip()
                    manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #observationtime
                keyName = 'observationtime'
                source = 'foreca'
                doUpdate = False
                colorCode = ''
                inList = False
                name =  'Foreca sync time'
                val = getListItem(0, cutObservation, 'time time_24h">([^<]*)')
                if val == '':
                    tmpTxt = datetime.now()
                    val = str(tmpTxt.strftime('%d/%m/%Y %H:%M'))
                valInfo = val
                units = ''
                manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #observationpoint
                keyName = 'observationpoint'
                source = 'foreca'
                doUpdate = False
                colorCode = ''
                inList = False
                name =  'Foreca observation point'
                val = getListItem(0, cutObservation, '<p>([^<]*)')
                valInfo = val
                units = ''
                manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #skycode
                keyName = 'skycode'
                source = 'foreca'
                doUpdate = False
                colorCode = ''
                inList = False
                name =  'skycode'
                val = getListItem(0, cutObservation, 'images/symbols/([^"]*)').replace('.svg','.png')
                val = iconsMap.get(val, '').replace('.png','')
                if val == '':
                    val = _(getListItem(0, cutObservation, '<div class="symbolText">([^<]*)'))
                    val = IMGtoICON('NA', val, 12).replace('.png','')
                valInfo = val
                units = ''
                manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #iconfilename
                keyName = 'iconfilename'
                source = 'foreca'
                doUpdate = False
                colorCode = ''
                inList = False
                name =  'iconfilename'
                val = getListItem(0, cutObservation, 'images/symbols/([^"]*)').replace('.svg','.png')
                val = '%s%s' % (paramsDict['iconPath'], iconsMap.get(val, ''))
                valInfo = val
                units = ''
                manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
                #imgurl = 'https://www.foreca.com/' + tmpList[4]
                #imgfilename =  '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/' + os.path.basename(imgurl).replace('.svg','.png')
    else:
        print(FC)

def looko2(webContent):
    defDBG = False
    if defDBG:
        print('thread.looko2() >>>')
        open(os.path.join(paramsDict['tmpFolder'], 'looko2.webContent'), 'w').write(str(webContent))
    dictFC = {}
    webCOLOR = findInContent(webContent, '<td width=[0-9]+[%]* style="background:(#[^;]*?);"><\\/td>')
    FC = findInContent(webContent, '<table>(.*?)id="NodeDailyChart"')
    if len(FC) < 10:
        print('thread.looko2() >>> zwrócona strona jest niepoprawna, na pewno czujnik działa?')
    else:
        try:
            observationpoint = findInContent(FC, 'id="NodeDescription"> <h4>(.*?)</div> </h4></td>')
            observationpoint = observationpoint.replace('LOOKO2', '').replace('_', ' ')
            if defDBG:
                print('thread.looko2() observationpoint = "%s"' % observationpoint)
            dictFC['observationpoint'] = observationpoint
            datetime = findInContent(FC, '<\\/h6><h6>.*: (.*?)<\\/h6>')
            if defDBG:
                print('thread.looko2() datetime = "%s"' % datetime)
            dictFC['observationtime'] = {'datetime': datetime, 'date': datetime.split(' ')[0], 
                'time': datetime.split(' ')[1]}
            dictFC['advice'] = findInContent(FC, '<\\/div><\\/P>[\n]?[ ]*<P>[\n]?[ ]*(.*?)<\\/P>').strip()
            dictFC['info'] = findInContent(FC, '<P><div>[\n]?[ ]*(.*?)[ ]*<BR>').strip()
            dictFC['infoFull'] = dictFC['info']
            dictFC['info'] = re.sub('<img.*>', ' ', dictFC['info'])
            dictFC['color'] = webCOLOR
            sensorsList = re.findall('class="col-sm-4".*<H4>([a-zA-Z0-9\\.]*?)<\\/H4><BR>([0-9]+) ', FC)
            if defDBG:
                print('thread.looko2() sensorsList = "%s"' % str(sensorsList))
            if sensorsList is not None:
                for sensor in sensorsList:
                    dictFC[sensor[0]] = sensor[1]

            saveJsonDict('dictLooko2.json', dictFC, doSort=True, pushSave=defDBG)
        except Exception as e:
            dictFC = {}
            print('EXCEPTION in looko2(): %s' % str(e))

    paramsDict['dictLooko2'] = dictFC
    return


def GiosInfo(webContent):
    defDBG = False
    if defDBG: print('thread.GiosInfo() >>>')
    try:
        dictTMP = json.loads(webContent)
        for inst in dictTMP:
            myID = str(inst['id'])
            if myID == paramsDict['airGiosID']:
                paramsDict['dictGiosInstallation'] = inst
                break

        saveJsonDict('giosInfo_%s.json' % paramsDict['currEntryID'], paramsDict['dictGiosInstallation'], doSort=True, pushSave=defDBG)
    except Exception as e:
        print('thread.GiosInfo() EXCEPTION:', str(e))


def Gios(webContent):
    defDBG = False
    print('thread.Gios() >>>')
    try:
        dictTMP = json.loads(webContent)
        paramsDict['dictGiosSensors'] = dictTMP
        saveJsonDict('dictGiosSensors.json', dictTMP, doSort=True, pushSave=defDBG)
    except Exception as e:
        paramsDict['dictGiosSensors'] = {}
        return

    paramsDict['dictGios'] = {}
    addSensorsDict = True
    for item in dictTMP:
        if defDBG: print(item)
        if str(item['stationId']) == paramsDict['airGiosID']:
            sensorID = item['id']

            HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:54.0) Gecko/20100101 Firefox/54.0', 'Accept-Charset': 'utf-8'}
            resp = requests.get('http://api.gios.gov.pl/pjp-api/rest/data/getData/%s' % sensorID, headers=HEADERS, timeout=5)
            webContent = resp.content
            retData = json.loads(webContent)
            if defDBG: print(retData)
            sensorName = retData['key']
            for idx in [0, 1, 2, 3, 4]:
                if defDBG: print(idx)
                #czasami czujnik nie ma danych historycznych
                try:
                    observationTime = retData['values'][idx]['date'] 
                    value = retData['values'][idx]['value']
                except Exception:
                    value = None
                if value is not None:
                    if addSensorsDict:
                        paramsDict['dictGios']['sensors'] = {}
                        addSensorsDict = False
                    break

            if value is not None:
                paramsDict['dictGios']['sensors'][sensorName] = value
                paramsDict['dictGios']['observationtime'] = {'datetime': observationTime, 'date': observationTime.split(' ')[0], 
                                                             'time': observationTime.split(' ')[1]}

    saveJsonDict('dictGiosData.json', paramsDict['dictGios'], doSort=True, pushSave=defDBG)
    return


def Blebox(webContent):
    defDBG = False
    if defDBG: print('thread.Blebox() >>>')
    try:
        dictTMP = json.loads(webContent)
        tmpTxt = datetime.now()
        dictTMP['observationtime'] = {'name': _('Blebox sync time'), 'date': str(tmpTxt.strftime('%d/%m/%Y')), 'time': str(tmpTxt.strftime('%H:%M')), 
           'datetime': str(tmpTxt.strftime('%d/%m/%Y %H:%M')), 
           'inList': False}
        paramsDict['dictBlebox'] = dictTMP
        saveJsonDict('dictBlebox.json', dictTMP, doSort=True, pushSave=defDBG)
    except Exception as e:
        paramsDict['dictBlebox'] = {}
        open(os.path.join(paramsDict['tmpFolder'], 'dictBlebox.WC'), 'w').write(webContent)


def OpenSense(webContent):
    defDBG = False
    if defDBG: print('thread.OpenSense() >>>')
    try:
        dictTMP = json.loads(webContent)
        paramsDict['dictOpenSense'] = dictTMP
        saveJsonDict('dictOpenSense.json', dictTMP, doSort=True, pushSave=defDBG)
    except Exception as e:
        paramsDict['dictOpenSense'] = {}
        open(os.path.join(paramsDict['tmpFolder'], 'dictOpenSense.WC'), 'w').write(webContent)


def smogTok(webContent):
    defDBG = False
    print('thread.smogTok() >>>')
    try:
        dictTMP = json.loads(webContent)
        paramsDict['dictSmogTok'] = dictTMP
        if defDBG == True: saveJsonDict('dictSmogTok.json', dictTMP, doSort=True, pushSave=defDBG)
    except Exception as e:
        paramsDict['dictSmogTok'] = {}
        open(os.path.join(paramsDict['tmpFolder'], 'dictSmogTok.WC'), 'w').write(webContent)


def motionBurze(webContent):
    print('thread.motionBurze(HistoryPeriod: %s) >>>\n' % paramsDict['HistoryPeriod'] )
    currDateTime = str(time.strftime('%Y%m%d%H%M', time.localtime()))
    currEpocTime = int(time.time())
    try:
        with open(os.path.join(paramsDict['pluginPath'], 'icons', 'storms_%s.png' % currDateTime), 'wb') as (f):
            f.write(webContent)
    except Exception:
        pass

    try:
        HistoryPeriod = int(paramsDict['HistoryPeriod'])
    except Exception as e:
        HistoryPeriod = 43200

    for f in os.listdir(os.path.join(paramsDict['pluginPath'], 'icons')):
        if f.startswith('storms_') and f.endswith('.png'):
            dirFile = os.path.join(paramsDict['pluginPath'], 'icons', f)
            if os.path.isfile(dirFile) and os.stat(dirFile).st_mtime < currEpocTime - HistoryPeriod:
                try:
                    os.remove(dirFile)
                except Exception:
                    pass


def thingSpeakCallback(xmlstring):
    DBG = False
    print('thread.thingSpeakCallback() >>>')
    if DBG:
        open(os.path.join(paramsDict['tmpFolder'], 'thingSpeakCallback.webContent'), 'w').write('%s\n' % xmlstring)
    thingSpeakItems = {}
    try:
        root = cet_fromstring(xmlstring)
        for childs in root:
            if DBG:
                print('\titem= %s' % childs.tag)
            if childs.tag in ('name', 'description'):
                thingSpeakItems[childs.tag] = childs.text
            elif childs.tag.startswith('field'):
                if DBG:
                    print("\tchilds.tag.startswith('field'):")
                tmpName = '%sName' % childs.tag
                thingSpeakItems[tmpName] = childs.text
                tmpTXT = childs.text.lower().replace(' ', '').replace('.', '').replace(',', '')
                if DBG:
                    print('\t tmpTXT = ', "'%s'" % tmpTXT)
                if tmpTXT.find('pm') >= 0 and tmpTXT.find('25') >= 0:
                    if DBG:
                        print('\t', 'tmpTXT.find(pm) and tmpTXT.find(25):')
                    thingSpeakItems['PM2.5'] = childs.tag
                    thingSpeakItems['PM2.5Name'] = childs.text
                elif tmpTXT.find('pm') >= 0 and tmpTXT.find('10') >= 0:
                    if DBG:
                        print('\t', 'tmpTXT.find(pm) and tmpTXT.find(10):')
                    thingSpeakItems['PM10'] = childs.tag
                    thingSpeakItems['PM10Name'] = childs.text
                elif tmpTXT.find('pm') and tmpTXT.find('1'):
                    thingSpeakItems['PM1'] = childs.tag
                    thingSpeakItems['PM1Name'] = childs.text
            elif childs.tag == 'feeds':
                for feeds in childs:
                    if DBG:
                        print('\tfeeds= ', '%s' % feeds.tag)
                    if feeds.tag == 'feed':
                        for feed in feeds:
                            if DBG:
                                print('\tfeed= ', '%s' % feed.tag)
                            if feed.tag == 'created-at':
                                thingSpeakItems['ObservationTime'] = feed.text
                            elif feed.tag.startswith('field'):
                                tmpName = '%sValue' % feed.tag
                                thingSpeakItems[tmpName] = feed.text
                                if feed.tag == thingSpeakItems.get('PM2.5', '?!?!?!?'):
                                    thingSpeakItems['PM2.5Value'] = feed.text
                                elif feed.tag == thingSpeakItems.get('PM10', '?!?!?!?'):
                                    thingSpeakItems['PM10Value'] = feed.text
                                elif feed.tag == thingSpeakItems.get('PM1', '?!?!?!?'):
                                    thingSpeakItems['PM1Value'] = feed.text

    except Exception as e:
        thingSpeakItems = {}
        thingSpeakItems['name'] = 'xml error'
        thingSpeakItems['description'] = str(e)
        print('\tEXCEPTION', str(e))

    paramsDict['thingSpeakItems'] = thingSpeakItems
    saveJsonDict('dictThingSpeak.json', thingSpeakItems, True, paramsDict['DEBUG'])


def xmlCallback(xmlstring):
    defDBG = False
    print('thread.xmlCallback() >>>')
    root = cet_fromstring(xmlstring)
    index = 0
    degreetype = 'C'
    errorMessage = ''
    currentWeather = {}
    dailyWeather = {}
    dailyRecordID = 0
    if defDBG:
        print('\t', ' root childs:')
    for childs in root:
        if defDBG:
            print('root childs:', childs.tag)
        if childs.tag == 'weather':
            errorMessage = childs.attrib.get('errormessage')
            if errorMessage:
                currentWeather['errormessage'] = errorMessage
                break
            currentWeather['degreetype'] = childs.attrib.get('degreetype')
            currentWeather['imagerelativeurl'] = '%slaw/' % childs.attrib.get('imagerelativeurl')
            currentWeather['url'] = childs.attrib.get('url')
        for items in childs:
            if defDBG:
                print('items.tag', items.tag)
            if items.tag == 'current':
                currentWeather['temperature'] = items.attrib.get('temperature')
                currentWeather['skytext'] = items.attrib.get('skytext')
                currentWeather['humidity'] = items.attrib.get('humidity')
                currentWeather['wind_speed'] = items.attrib.get('winddisplay')
                currentWeather['wind_dir'] = items.attrib.get('winddisplay')
                currentWeather['observationtime'] = items.attrib.get('observationtime')
                currentWeather['observationpoint'] = items.attrib.get('observationpoint')
                currentWeather['feelslike'] = items.attrib.get('feelslike')
                currentWeather['skycode'] = '%s%s' % (items.attrib.get('skycode'), paramsDict['iconExtension'])
                currentWeather['code'] = items.attrib.get('skycode')
                currentWeather['iconFilename'] = '%s%s' % (paramsDict['iconPath'], currentWeather['skycode'])
            if items.tag == 'forecast':
                forecastDate = int(items.attrib.get('date').replace('-', ''))
                currentDate = int(datetime.now().strftime('%Y%m%d'))
                if defDBG:
                    print('dailyWeather', str(forecastDate))
                if forecastDate >= currentDate:
                    skytext = items.attrib.get('skytextday')
                    skycode = items.attrib.get('skycodeday')
                    iconfilename = '%s%s.png' % (paramsDict['iconPath'], skycode)
                    imgfilename = iconsMap.get('%s.png' % skycode, '')
                    if imgfilename != '':
                        imgfilename = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/%s' % imgfilename
                    temp_low = items.attrib.get('low') + '°'
                    temp_high = items.attrib.get('high') + '°'
                    rainprecip = items.attrib.get('precip') + '%'
                    forecast = _('Forecast for %s: maximum temperature %s, minimum temperature %s, rain probability %s') % (items.attrib.get('day'),
                     temp_high, temp_low, rainprecip)
                    dailyWeather['Record=%s' % dailyRecordID] = {'temp_low': temp_low, 
                       'temp_high': temp_high, 
                       'skycode': skycode, 
                       'skytext': skytext, 
                       'date': items.attrib.get('date'), 
                       'day': items.attrib.get('day'), 
                       'weekday': items.attrib.get('shortday').replace('.',''), 
                       'rainprecip': rainprecip, 
                       'iconfilename': iconfilename, 
                       'imgfilename': imgfilename, 
                       'forecast': forecast, 
                       'imgurl': '', 
                       'monthday': items.attrib.get('date')[-2:]}
                    dailyRecordID += 1

    paramsDict['currentXMLweather'] = currentWeather
    paramsDict['dailyXMLweather'] = dailyWeather
    xmlDict = {'currentWeather': currentWeather, 'dailyWeather': dailyWeather}
    saveJsonDict('dictXMLweather.json', xmlDict, paramsDict['DEBUG'])
    if defDBG:
        print('xmlCallback() <<<')

def analyze_data_msn(webContent, reportMissingIcons=True, Lang=''):
    DBGnow = False
    DBGhourly = False
    DBGdaily = False
    if DBGnow or DBGhourly or DBGdaily:
        print('thread.analyze_data_msn >>>')
        open(os.path.join(paramsDict['tmpFolder'], 'analyze_data_msn.webContent'), 'w').write(webContent)
    if os.path.exists(os.path.join(paramsDict['tmpFolder'], 'analyze_data_msn.cutContent')):
        os.remove(os.path.join(paramsDict['tmpFolder'], 'analyze_data_msn.cutContent'))

    reportMissingIcons = True
    missingIcons = ''
    if reportMissingIcons and os.path.exists(os.path.join(paramsDict['tmpFolder'], 'MissingMappings.log')):
        missingIcons = open(os.path.join(paramsDict['tmpFolder'], 'MissingMappings.log'), 'r').read()
    if DBGnow: print('thread.analyze_data_msn.currentData >>>')
    val = paramsDict['degreetype']
    paramsDict['dictWeather']['currentData']['degreetype'] = str(val)

    colorCode = ''
    inList = False
    name = ''
    val = ''
    valInfo = ''
    units = ''
    name = 'Alert'
    try:
        cutContent = findInContent(webContent, '<div class="alerts y" >(.*?)</div>')
        if len(cutContent) < 1:
            if DBGnow: print('thread.analyze_data_msn > nie znaleziono danych o ostrzezeniach !!!!!!')
        else:
            tmpList = getList([], cutContent, '<h2>(.*?)<span.*alertTime">(.*?)<\\/span>[ ]*')
            if DBGnow:
                open(os.path.join(paramsDict['tmpFolder'], 'analyze_data_msn.cutContent'), 'a').write('cutContent(<div class="alerts y" >(.*?)</div>):\n\t' + cutContent + '\ntmpList:\n\t' + str(tmpList))
            if len(tmpList) > 0:
                tmpList = tmpList[0]
                val = tmpList[0].strip()
                for aColor in ['Żółty', 'Czerwony']:
                    if aColor in val:
                        colorCode = clr[aColor]
                        val = val.replace(aColor, '').strip()

                if val != '' and len(tmpList) > 1:
                    valInfo = colorCode + val + ' ' + tmpList[1].strip()
            paramsDict['dictWeather']['currentData']['alert'] = {'colorCode': '', 'inList': inList, 'name': False, 'source': 'EXCEPTION', 'val': '', 'valInfo': ''}
    except Exception as e:
        print("\t\t!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Exception in ['dictWeather']['currentData']['alert'] branch: %s" % str(e))

    if DBGnow:
        print("thread.analyze_data_msn.currentData >>> dictWeather['currentData']['temperature']")
    cutContent = findInContent(webContent, '<div class="current-info">(.*?)</div>')
    if len(cutContent) < 1:
        if DBGnow:
            print('\t\tanalyze_data_msn > nie znaleziono danych o obecnej temperaturze !!!!!!')
    else:
        if DBGnow:
            open(os.path.join(paramsDict['tmpFolder'], 'analyze_data_msn.cutContent'), 'a').write('cutContent(<div class="current-info">(.*?)</div>):\n\t' + cutContent)
        keyName = 'temperature'
        source = 'msnweb'
        doUpdate = True
        colorCode = ''
        inList = False
        name = ''
        val = ''
        valInfo = ''
        units = ''
        name = _('Temperature')
        units = '°' + paramsDict['degreetype']
        val = getListItem(0, cutContent, 'class="current".*>(.*?)</span>')
        val = str(re.findall('[+-]?[0-9]+', val)[0])
        colorCode = Temperature2strColor(val)
        valInfo = colorCode + val + units
        manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
    cutContent = findInContent(webContent, '<div class="weather-info">(.*?</div>.*?)</div>')
    if DBGnow:
        open(os.path.join(paramsDict['tmpFolder'], 'analyze_data_msn.cutContent'), 'a').write('cutContent(<div class="weather-info">(.*?)</div>(.*?)</div>):\n\t' + cutContent)
    if len(cutContent) < 1:
        if DBGnow: print('\t\tanalyze_data_msn > nie znaleziono danych obecnych !!!!!!')
    else:
        keyName = 'skytext'
        source = 'msnweb'
        doUpdate = True
        colorCode = ''
        inList = False
        name = ''
        val = ''
        valInfo = ''
        units = ''
        name = _('Current information')
        val = getListItem(0, cutContent, '<span>(.*?)</span>.*<ul>')
        valInfo = colorCode + val + units
        manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
        tmpList = getList([], cutContent, '<li><span>(.*?)</span>(.*?)</li>')
        keyName = 'feelslike'
        source = 'msnweb'
        doUpdate = True
        colorCode = ''
        inList = False
        name = ''
        val = ''
        valInfo = ''
        units = ''
        inList = True
        units = '°' + paramsDict['degreetype']
        val = str(re.findall('[+-]?[0-9]+', tmpList[0][1])[0])
        colorCode = Temperature2strColor(val)
        valInfo = colorCode + val + units
        name = tmpList[0][0].replace('Temperatura', 'Temp.').replace('Temperature', 'Temp.').replace('Temperatur', 'Temp.')
        manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
        keyName = 'wind_speed'
        source = 'msnweb'
        doUpdate = True
        colorCode = ''
        inList = False
        name = ''
        val = ''
        valInfo = ''
        units = ''
        inList = True
        name = tmpList[1][0]
        val = str(re.findall('[+-]?[0-9]+', tmpList[1][1])[0])
        units = 'km/h'
        valInfo = None
        manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
        keyName = 'wind_dir'
        source = 'msnweb'
        doUpdate = True
        colorCode = ''
        inList = False
        name = ''
        val = ''
        valInfo = ''
        units = ''
        name = _('Wind direction')
        val = getListItem(0, cutContent, 'winddir.*>(.*?)</div>')
        valInfo = getWindIconName(val)
        manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
        getWindIconName
        keyName = 'pressure'
        source = 'msnweb'
        doUpdate = True
        colorCode = ''
        inList = False
        name = ''
        val = ''
        valInfo = ''
        units = ''
        inList = True
        name = tmpList[2][0]
        val = str(re.findall('[+-]?[0-9]+', tmpList[2][1])[0])
        units = 'hPa'
        valInfo = colorCode + val + units
        manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
        keyName = 'visibility'
        source = 'msnweb'
        doUpdate = True
        colorCode = ''
        inList = False
        name = ''
        val = ''
        valInfo = ''
        units = ''
        inList = True
        name = tmpList[3][0]
        val = str(re.findall('[+-]?[0-9]+', tmpList[3][1])[0])
        units = tmpList[3][1].split(val)[1].strip()
        valInfo = colorCode + val + units
        manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
        keyName = 'humidity'
        source = 'msnweb'
        doUpdate = True
        colorCode = ''
        inList = False
        name = ''
        val = ''
        valInfo = ''
        units = ''
        inList = True
        name = tmpList[4][0]
        val = str(int(filter(str.isdigit, tmpList[4][1])))
        units = '%'
        valInfo = colorCode + val + units
        manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
        keyName = 'dew_point_temp'
        source = 'msnweb'
        doUpdate = True
        colorCode = ''
        inList = False
        name = ''
        val = ''
        valInfo = ''
        units = ''
        inList = True
        units = '°' + paramsDict['degreetype']
        val = str(re.findall('[+-]?[0-9]+', tmpList[5][1])[0])
        colorCode = Temperature2strColor(val)
        valInfo = colorCode + val + units
        name = tmpList[5][0]
        name = name.replace('Temperatura', 'Temp.').replace('Temperature', 'Temp.').replace('Temperatur', 'Temp.')
        manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
        val = IMGtoICON('noDescription', paramsDict['dictWeather']['currentData']['skytext']['val'], int(datetime.now().strftime('%H')))
        paramsDict['dictWeather']['currentData']['skycode'] = {'val': val, 'name': val, 'valInfo': val, 'inList': False}
        val = '%s%s' % (paramsDict['iconPath'], paramsDict['dictWeather']['currentData']['skycode']['val'])
        paramsDict['dictWeather']['currentData']['iconfilename'] = {'val': val, 'name': val, 'valInfo': val, 'inList': False}
        val = paramsDict['dictWeather']['currentData']['skycode']['val'].replace('.png', '')
        paramsDict['dictWeather']['currentData']['code'] = {'val': val, 'name': val, 'valInfo': val, 'inList': False}
        paramsDict['dictWeather']['currentData']['observationpoint'] = {'val': paramsDict['city'], 'name': 'Observation point', 'valInfo': paramsDict['weatherSearchFullName'], 'inList': False}
        tmpTxt = datetime.now()
        paramsDict['dictWeather']['currentData']['observationtime'] = {'name': _('MSN sync time'), 'date': str(tmpTxt.strftime('%d/%m/%Y')), 'time': str(tmpTxt.strftime('%H:%M:%S')), 'datetime': str(tmpTxt.strftime('%d/%m/%Y %H:%M:%S')), 
           'inList': False}
    cutContent = findInContent(webContent, '<div class="dailydetails" (.*?)</ul>')
    if DBGhourly:
        open(os.path.join(paramsDict['tmpFolder'], 'analyze_data_msn.cutContent'), 'a').write('cutContent(<div class="dailydetails" (.*?)</ul>):\n\t' + cutContent)
    if len(cutContent) < 1:
        if DBGnow: print('\t\t', 'analyze_data_msn > nie znaleziono danych godzinowych !!!!!!')
    else:
        paramsDict['dictWeather']['hourlyData']['title'] = _('Hourly')
        Lines = getList([], cutContent, '<li>(.*?)</li>')
        if DBGhourly:
            open(os.path.join(paramsDict['tmpFolder'], 'analyze_data_msn.cutContent'), 'a').write('getList():\n\t' + str(Lines))
        id = 0
        for Line in Lines:
            tmpList = getList([], Line, 'class="time">(.*?)<.*alt="(.*?)".*src="(.*?)".*class="temp">(.*?)<.*class="precipicn"><span>(.*?)<')
            ltime = tmpList[0][0]
            skytext = tmpList[0][1]
            imgurl = tmpList[0][2].strip()
            imgfilename = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/%s' % str(re.findall('entityid\\/([a-zA-Z0-9]+\\.img)', tmpList[0][2])[0])
            imgfilename = imgfilename[:-4] + '.png'
            skycode = iconsMap.get(utfTOansi(tmpList[0][1]), '')
            iconfilename = '%s%s' % (paramsDict['iconPath'], IMGtoICON(imgfilename, skytext, 12))
            paramsDict['dictWeather']['hourlyData']['Record=%s' % id] = {'time': ltime, 'skytext': skytext, 'imgurl': '', #imgurl, 
               'temperature': tmpList[0][3], 'rainprecip': tmpList[0][4], 'skycode': skycode, 
               'imgfilename': imgfilename, 'iconfilename': iconfilename}
            id += 1
            if not os.path.exists(imgfilename):
                if imgurl[:4] != 'http':
                    imgurl = 'http:' + imgurl
                print('\t%s does not exist. Downloading from %s' % (imgfilename, imgurl))
                urllib_urlretrieve(imgurl, imgfilename)

        cutContent = findInContent(webContent, '<section id="df" class="df" [ ]?data-aop="DailyForecast"(.*?)</section>')
        if DBGdaily:
            open(os.path.join(paramsDict['tmpFolder'], 'analyze_data_msn.cutContent'), 'a').write('cutContent(<section id="df" class="df" [ ]?data-aop="DailyForecast"(.*?)</section>):\n\t' + cutContent)
        if len(cutContent) < 1:
            print('thread.analyze_data_msn > nie znaleziono danych dziennych !!!!!!')
        else:
            print('thread.analyze_data_msn.dailyData >>>')
            paramsDict['dictWeather']['dailyData']['title'] = _('Daily')
            Lines = getList([], cutContent, '<li  data-aop=(.*?)</li>')
            if DBGdaily:
                open(os.path.join(paramsDict['tmpFolder'], 'analyze_data_msn.cutContent'), 'a').write('\nDAILY LINES:\n')
                for line in Lines:
                    open(os.path.join(paramsDict['tmpFolder'], 'analyze_data_msn.cutContent'), 'a').write('!!!!!!!!!!!!!!!!!!! LINE:\n' + str(line) + '\n')

            id = 0
            for Line in Lines:
                tmpList = getList([], Line, 'data-detail="(.*}?)".*data-hourly="(.*}?)".*data-emptymsg="(.*?)".*aria-label="(.*?)".*>.*<span>(.*?)<.*<span>(.*?)<.*src="(.*?)"*alt="(.*?)".*data-icon="(.*?)".*>(.*?)</span>.*<p>(.*?)</p>.*>(.*?)</p>')
                if len(tmpList) > 0:
                    tmpList = tmpList[0]
                if DBGdaily:
                    open(os.path.join(paramsDict['tmpFolder'], 'analyze_data_msn.cutContent'), 'a').write('\nFOUND LIST:\n')
                    for tmpitem in tmpList:
                        open(os.path.join(paramsDict['tmpFolder'], 'analyze_data_msn.cutContent'), 'a').write('$$$$$$$$$$$$$$$$$$$$$ ITEM:\n' + str(tmpitem) + '\n')

                try:
                    dataDetailDict = json.loads(tmpList[0])
                except Exception as e:
                    dataDetailDict = {}
                    print('thread.analyze_data_msn dataDetailDict Exception:' + str(e))

                try:
                    dataHourlyDict = json.loads(tmpList[1])
                except Exception as e:
                    dataHourlyDict = {}
                    print('thread.analyze_data_msn dataHourlyDict Exception:' + str(e))

                dataEmptymsg = tmpList[2]
                ariaLabel = tmpList[3]
                weekday = tmpList[4]
                monthday = tmpList[5]
                imgurl = tmpList[6]
                skytext = tmpList[7]
                data_icon = tmpList[8]
                rainprecip = tmpList[9]
                temp_high = tmpList[10]
                temp_low = tmpList[11]
                imgfilename = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/%s' % str(re.findall('entityid\\/([a-zA-Z0-9]+\\.img)', imgurl)[0])
                imgfilename = imgfilename[:-4] + '.png'
                if not os.path.exists(imgfilename):
                    if imgurl[:4] != 'http':
                        imgurl = 'http:' + imgurl
                    print('\t%s does not exist. Downloading from %s' % (imgfilename, imgurl))
                    urllib_urlretrieve(imgurl, imgfilename)
                skycode = iconsMap.get(utfTOansi(skytext), '')
                iconfilename = '%s%s' % (paramsDict['iconPath'], IMGtoICON(imgfilename, skytext, 12))
                paramsDict['dictWeather']['dailyData']['Record=%s' % id] = {'day': weekday, 'forecast': ariaLabel, 
                   'weekday': weekday, 
                   'monthday': monthday, 
                   'imgurl': '' , #imgurl, 
                   'skytext': skytext, 
                   'data_icon': data_icon, 
                   'temp_high': temp_high, 
                   'temp_low': temp_low, 
                   'rainprecip': rainprecip, 
                   'skycode': skycode, 
                   'imgfilename': imgfilename, 
                   'iconfilename': iconfilename, 
                   'dictdetalis': dataDetailDict, 
                   'dicthourly': dataHourlyDict, 
                   'dataEmptymsg': dataEmptymsg}
                id += 1

    saveJsonDict(paramsDict['dictWeatherfile'], paramsDict['dictWeather'], False, True)
    return

def msn_api(webContent, webFileName):
    DBGoverview = True
    DBGdailyforecast = True
    DBGhourlytrend = True
    DBGdailytrend = True
    dataType = webFileName[8:]
    print('thread.msn_api(%s) >>>' % dataType)
    dataDict = webToDict(webContent, 'MSN%s' % dataType, False)
    if len(dataDict) == 0:
        print('dataDict empty, exiting')
        return
    try:
        if dataType == 'overview':
            overviewDict = dataDict.get('value',[{}])[0]
            if len(overviewDict) == 0: 
                print('overviewDict value not found')
                return
            unitsDict = overviewDict.get('units', {})
            paramsDict['dictWeather']['currentData']['degreetype'] = str(paramsDict['degreetype'])
            keyName = 'N/A'
            #sourceDict = overviewDict['responses'][0]['source']
            overviewDict = overviewDict['responses'][0]['weather'][0]
            currentDict = overviewDict['current']
            if 1: #alerty
                keyName = 'alerts'
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                alertsDict = overviewDict.get('alerts', [])
                if len(alertsDict) > 0:
                    alertsDict = alertsDict[0]
                    val = alertsDict.get('title', '')
                    for aColor in ['Żółty', 'Czerwony', 'Yellow', 'Red']:
                        if aColor in alertsDict.get('severity', '') or aColor in alertsDict.get('level', ''):
                            colorCode = clr[aColor]
                    valInfo = colorCode + alertsDict.get('desc', alertsDict.get('safetyGuide', ''))
                paramsDict['dictWeather']['currentData']['alert'] = {'colorCode': colorCode, 'inList': inList, 'name': keyName, 'source': 'MSNAPI', 'val': val, 'valInfo': valInfo}
            if 1: #skytext
                keyName = 'skytext'
                source = 'MSNAPI'
                doUpdate = True
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                name = _('Current information')
                val = currentDict.get('cap', '')
                valInfo = colorCode + val + units
                manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #temperature
                keyName = 'temperature'
                source = 'MSNAPI'
                doUpdate = True
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                inList = False
                units = unitsDict.get('temperature', '°' + paramsDict['degreetype'])
                val = str(int(overviewDict['current']['temp']))
                colorCode = Temperature2strColor(val)
                valInfo = colorCode + val + units
                name = _("Temp.")
                manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #feelslike
                keyName = 'feelslike'
                source = 'MSNAPI'
                doUpdate = True
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                inList = True
                units = unitsDict.get('temperature', '°' + paramsDict['degreetype'])
                val = str(int(overviewDict['current']['feels']))
                colorCode = Temperature2strColor(val)
                valInfo = colorCode + val + units
                name = _("Feels like")
                manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #wind_speed
                keyName = 'wind_speed'
                source = 'MSNAPI'
                doUpdate = True
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                inList = True
                name = _('Wind')
                val = str(int(currentDict.get('windSpd', 0)))
                if int(val) > 0:
                    units = unitsDict.get('speed', 'km/h')
                    valInfo = None
                    manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #wind_gust
                keyName = 'wind_gust'
                source = 'MSNAPI'
                doUpdate = True
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                inList = True
                name = _('Wind gust')
                val = str(int(overviewDict['current']['windGust']))
                units = unitsDict.get('speed', 'km/h')
                valInfo = None
                if int(overviewDict['current']['windGust']) > int(overviewDict['current']['windSpd']):
                    manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #wind_dir
                keyName = 'wind_dir'
                source = 'MSNAPI'
                doUpdate = True
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                name = _('Wind direction')
                val = str(int(overviewDict['current']['windDir']))
                valInfo = getWindIconName(val)
                manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #pressure
                keyName = 'pressure'
                source = 'MSNAPI'
                doUpdate = True
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                inList = True
                name = _('Pressure')
                val = str(int(overviewDict['current']['baro']))
                units = unitsDict.get('pressure', 'hPa').replace('mbar','hPa')
                valInfo = colorCode + val + units
                manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #visibility
                keyName = 'visibility'
                source = 'MSNAPI'
                doUpdate = True
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                inList = True
                name = _('Visibility')
                val = str(int(overviewDict['current']['vis']))
                units = unitsDict.get('distance')
                valInfo = colorCode + val + units
                manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #humidity
                keyName = 'humidity'
                source = 'MSNAPI'
                doUpdate = True
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                inList = True
                name = _('Humidity')
                val = str(int(overviewDict['current']['rh']))
                units = unitsDict.get('humidity', '%')
                valInfo = colorCode + val + units
                manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #cloud_cover
                keyName = 'cloud_cover'
                source = 'MSNAPI'
                doUpdate = True
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                inList = True
                name = _('Cloud cover')
                val = str(int(overviewDict['current']['cloudCover']))
                units = unitsDict.get('cloudCover', '%')
                valInfo = colorCode + val + units
                manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 0: #water_temp  
                keyName = 'water_temp'
                source = 'MSNAPI'
                doUpdate = True
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                inList = True
                units = unitsDict.get('temperature', '°' + paramsDict['degreetype'])
                val = str(int(overviewDict['current']['waterTemp']))
                colorCode = Temperature2strColor(val)
                valInfo = colorCode + val + units
                name = _("Water temp.")
                manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #dew_point_temp  
                keyName = 'dew_point_temp'
                source = 'MSNAPI'
                doUpdate = True
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                inList = True
                units = unitsDict.get('temperature', '°' + paramsDict['degreetype'])
                val = str(int(overviewDict['current']['dewPt']))
                colorCode = Temperature2strColor(val)
                valInfo = colorCode + val + units
                name = _("Dew point temp.")
                manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #uv_info  
                keyName = 'uv_info'
                source = 'MSNAPI'
                doUpdate = True
                colorCode = ''
                inList = False
                name = ''
                val = ''
                valInfo = ''
                units = ''
                inList = True
                val = str(overviewDict['current']['uv'])
                valInfo = colorCode + str(overviewDict['current']['uvDesc']) + units
                name = _("UV")
                manageCurrenDataWeatherItem(doUpdate, keyName, colorCode, inList, name, source, val, units, valInfo)
            if 1: #skycode
                keyName = 'skycode'
                val = IMGtoICON('noDescription', paramsDict['dictWeather']['currentData']['skytext']['val'], int(datetime.now().strftime('%H')), fcode = currentDict.get('symbol', ''))
                paramsDict['dictWeather']['currentData'][keyName] = {'val': val, 'name': val, 'valInfo': val, 'inList': False}
            if 1: #iconfilename
                keyName = 'iconfilename'
                val = '%s%s' % (paramsDict['iconPath'], paramsDict['dictWeather']['currentData']['skycode']['val'])
                paramsDict['dictWeather']['currentData'][keyName] = {'val': val, 'name': val, 'valInfo': val, 'inList': False}
            if 1: #code
                keyName = 'code'
                val = paramsDict['dictWeather']['currentData']['skycode']['val'].replace('.png', '')
                paramsDict['dictWeather']['currentData'][keyName] = {'val': val, 'name': val, 'valInfo': val, 'inList': False}
            if 1: #observationpoint, observationtime pressure  overviewDict['current']['']
                keyName = 'observationpoint'
                val = dataDict['value'][0]['responses'][0]['source']['location']['Name']
                paramsDict['dictWeather']['currentData'][keyName] = {'val': val, 'name': 'Observation point', 'valInfo': paramsDict['weatherSearchFullName'], 'inList': False}
                keyName = 'observationtime'
                val = ISO3339toDATETIME(overviewDict['current']['created'],0)
                paramsDict['dictWeather']['currentData'][keyName] = {'name': _('MSN sync time'), 'date': val[0], 'time': val[1], 'datetime': '%s %s' % (val[0],val[1]), 'inList': False}
            if 1: #aqi airquality (https://www.eea.europa.eu/)
                if currentDict.get('primaryPollutant', '') != '':
                    source = 'MSNAPI'
                    doUpdate = True
                    inList = True
                    name = currentDict['primaryPollutant'].split(' ')[0].replace('Ozone','O3').replace('NO₂','NO2')
                    val = int(round(float(currentDict['primaryPollutant'].split(' ')[1]),0))
                    units = currentDict['primaryPollutant'].split(' ')[2]
                    longname = param2name(name)
                    keyName = name.replace('.','').lower()
                    colorCode, Info = airQualityInfo(keyName, val)
                    if Info == '':
                        valInfo = colorCode + str(val) + units
                    else:
                        valInfo = colorCode + _(Info)
                    manageCurrenDataWeatherItem(doUpdate=True, keyName=keyName, colorCode=colorCode, inList=inList, name=_(name), source=source, val=str(val), units=units, valInfo=valInfo, longName=longname)
                    val = int(currentDict.get('aqi', ''))
                    colorCode = ''
                    valInfo = '%s%s' % (colorCode, val)
                    paramsDict['dictWeather']['currentData']['airIndex'] = {'colorCode': colorCode, 
                                                                            'level': currentDict.get('aqiSeverity', ''), 
                                                                            'name': 'EEA_aqi', 
                                                                            'iconfilename': '', 
                                                                            'info': '', 
                                                                            'advice': '', 
                                                                            'val': str(val), 
                                                                            'valInfo': valInfo, 
                                                                            'source': 'MSNAPI'}


            ##### Forecast godzinny #####
            keyName='Forecast godzinny'
            HourID = 0
            for dayID in [0 , 1]:
                dailyDict = overviewDict['forecast']['days'][dayID]['hourly']
                paramsDict['dictWeather']['hourlyData']['title'] = _('Hourly')
                for Line in dailyDict:
                    #print(dayID,HourID)
                    ltime = ISO3339toDATETIME(Line['valid'],0)[1].split(':')[0]
                    #print(Line['valid'])
                    skytext = Line['cap']
                    imgurl = Line['urlIcon']
                    imgfilename = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/%s' % os.path.basename(imgurl).replace('.img','.png')
                    if not os.path.exists(imgfilename):
                        if imgurl[:4] != 'http':
                            imgurl = 'http:' + imgurl
                        print('\t%s does not exist. Downloading from %s' % (imgfilename, imgurl))
                        urllib_urlretrieve(imgurl, imgfilename)
                    skycode = IMGtoICON(imgfilename, skytext, int(ltime), fcode = Line.get('symbol', '')).replace('.png','')
                    iconfilename = '%s%s.png' % (paramsDict['iconPath'], skycode)
                    temperature = str(int(Line['temp'])) + "°"
                    rainprecip = str(int(Line['precip'])) + "%"
                    summary = str(_('%s\n\n\n%s\nTemp. %s\nRain %s') % (ltime, skytext, temperature, rainprecip))
                    paramsDict['dictWeather']['hourlyData']['Record=%s' % HourID] = {'time': ltime, 'skytext': skytext, 'imgurl': imgurl, 
                                                                             'temperature': temperature, 'rainprecip': rainprecip, 'skycode': skycode, 
                                                                             'imgfilename': imgfilename, 'iconfilename': iconfilename, 'summary': summary}
                    paramsDict['dictWeather']['iconsData'][Line['icon']] = iconfilename
                    HourID += 1
                    if HourID >= 24:
                        break
            ##### Forecast dzienny #####
            keyName='Forecast dzienny'
            id = 0
            for dailyDict in overviewDict['forecast']['days']:
                dataEmptymsg = ''
                ariaLabel = ''
                data_icon = ''
                dataDetailDict = {}
                dataHourlyDict = {}
                imgurl = dailyDict['daily']['iconUrl']
                dictDate = ISO3339toDATETIME(dailyDict['daily']['valid'])[2]
                try: overviewDict['forecast']['days'][id]['daily']['valid'] = dictDate.strftime("%Y-%m-%dT%H:%M")
                except Exception: pass
                weekday = _(dictDate.strftime("%a"))
                monthday = dictDate.strftime("%d")
                Month = _(dictDate.strftime("%b"))
                date_summary = str('%s. %s %s' % (weekday, monthday, Month))
                skytext = dailyDict['daily']['pvdrCap']
                if skytext == '':
                    try:
                        skytext = dailyDict['daily']['day']['pvdrCap']
                    except Exception:
                        print('MSNAPI: Exception in getting skytext for %s' % dailyDict['daily'])
                rainprecip = str(int(dailyDict['daily']['precip'])) + "%"
                temp_high = str(int(dailyDict['daily']['tempHi'])) + "°"
                temp_low = str(int(dailyDict['daily']['tempLo'])) + "°"
                imgfilename = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/%s' % os.path.basename(imgurl).replace('.img','.png')
                if not os.path.exists(imgfilename):
                    if imgurl[:4] != 'http':
                        imgurl = 'http:' + imgurl
                    print('\t%s does not exist. Downloading from %s' % (imgfilename, imgurl))
                    urllib_urlretrieve(imgurl, imgfilename)
                try:
                    fcode = dailyDict['daily']['day']['symbol']
                except Exception:
                    fcode = ''
                skycode = IMGtoICON(imgfilename, skytext, 12, fcode = fcode).replace('.png','')
                iconfilename = '%s%s.png' % (paramsDict['iconPath'], skycode)
                summary = str('%s/ %s/ %s\n%s' % (temp_high, temp_low, rainprecip, skytext))
                paramsDict['dictWeather']['dailyData']['Record=%s' % id] = {'day': weekday, 'forecast': ariaLabel, 
                                                                            'weekday': weekday, 
                                                                            'monthday': monthday, 
                                                                            'imgurl': imgurl, 
                                                                            'skytext': skytext, 
                                                                            'data_icon': data_icon, 
                                                                            'temp_high': temp_high, 
                                                                            'temp_low': temp_low, 
                                                                            'rainprecip': rainprecip, 
                                                                            'skycode': skycode, 
                                                                            'imgfilename': imgfilename, 
                                                                            'iconfilename': iconfilename, 
                                                                            'dictdetalis': dataDetailDict, 
                                                                            'dicthourly': dataHourlyDict, 
                                                                            'dataEmptymsg': dataEmptymsg,
                                                                            'date_summary': date_summary,
                                                                            'summary': summary
                                                                            }
                paramsDict['dictWeather']['iconsData'][dailyDict['daily']['icon']] = iconfilename
                id += 1
            if DBGoverview:
                saveJsonDict('dictMSNweather_%s_%s.json' %(dataType,paramsDict['currEntryID']), dataDict, False, True)
        else:
            if dataType == 'dailyforecast':
                try:
                    tmpDict = dataDict['value'][0]['responses'][0]['weather'][0]['days']
                    id = 0
                    for dayDict in tmpDict:
                        dictDate = ISO3339toDATETIME(dayDict['daily']['valid'])[2]
                        dataDict['value'][0]['responses'][0]['weather'][0]['days'][id]['daily']['valid'] = dictDate.strftime("%Y-%m-%dT%H:%M")
                        #except Exception: pass
                        id += 1
                        imgurl = dayDict['daily']['iconUrl']
                        imgfilename = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/%s' % os.path.basename(imgurl).replace('.img','.png')
                        skytext = dayDict['daily']['pvdrCap']
                        if skytext == '':
                            try: skytext = dayDict['daily']['day']['pvdrCap']
                            except Exception: print('MSNAPI: Exception in getting skytext for %s' % dayDict['daily'])
                        try:
                            fcode = dayDict['daily']['day']['symbol']
                        except Exception:
                            fcode = ''
                        skycode = IMGtoICON(imgfilename, skytext, 12, fcode = fcode).replace('.png','')
                        iconfilename = '%s%s.png' % (paramsDict['iconPath'], skycode)
                        paramsDict['dictWeather']['iconsData'][dayDict['daily']['icon']] = iconfilename
                except Exception as e:
                    print(str(e))
            elif dataType == 'hourlytrend':
                try:
                    tmpDict = dataDict['value'][0]['responses'][0]['weather'][0]['days']
                    for dayDict in tmpDict:
                        hourlyList = dayDict['hourly']
                        for hourDict in hourlyList:
                            imgurl = hourDict['urlIcon']
                            imgfilename = '/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/icons/%s' % os.path.basename(imgurl).replace('.img','.png')
                            skytext = hourDict['pvdrCap']
                            try:
                                fcode = hourDict['symbol']
                            except Exception:
                                fcode = ''
                            skycode = IMGtoICON(imgfilename, skytext, 12, fcode = fcode).replace('.png','')
                            iconfilename = '%s%s.png' % (paramsDict['iconPath'], skycode)
                            paramsDict['dictWeather']['iconsData'][hourDict['icon']] = iconfilename
                except Exception as e:
                    print(str(e))
            elif dataType == 'dailytrend':
                try:
                    tmpDict = dataDict['value'][0]['weather'][0]['days']
                except Exception:
                    pass
            saveJsonDict('dictMSNweather_%s_%s.json' %(dataType,paramsDict['currEntryID']), dataDict, False, True)

        saveJsonDict(paramsDict['dictWeatherfile'], paramsDict['dictWeather'], False, True)
        
    except Exception as e:
        print('\tmsn_api() EXCEPTION analysing %s/%s:' % (dataType,keyName), str(e))
        print(traceback.format_exc())
        saveJsonDict('dictMSNweather_%s_%s.json' %(dataType,paramsDict['currEntryID']), dataDict, False, True)
    
        
#################################################################################################################
#################################################################################################################
#################################################################################################################
#################################################################################################################

def mainProc():
    if 1:
        if len(sys.argv) - 1 == 0:
            print('ERROR - NO arguments provided !!!')
            sys.exit(1)
        global paramsDict, threads
        threads = list()
        paramsDict = {}
        print('\tArguments (%s):' % (len(sys.argv) - 1))
        for myArg in sys.argv:
            if '=' in myArg:
                myArg = myArg.replace("'","") # workarround for KODI
                myArg = myArg.split('=', 1)
                param = myArg[0].strip()
                value = myArg[1].strip()
                paramsDict[param] = value
                if 'API' in param:
                    if len(paramsDict[param]) > 9:
                        print("\t\t%s = '%s...%s'" % (param, paramsDict[param][:3], paramsDict[param][-3:]))
                    elif len(paramsDict[param]) > 5:
                        print("\t\t%s = '%s...%s'" % (param, paramsDict[param][:1], paramsDict[param][-1:]))
                    elif len(paramsDict[param]) == 0:
                        print("\t\t%s = ''" % param)
                    else:
                        print("\t\t%s = '*****'" % param)
                else:
                    print("\t\t%s = '%s'" % (param, paramsDict[param]))
                #exec("%s = '%s'" % (param, value))

        try:
            localeInit(paramsDict['language'], os.path.join(paramsDict['pluginPath'], 'locale'))
        except Exception as e:
            print('localeInit(paramsDict[language]) EXCEPTION ' + str(e))

        paramsDict['dictWeather'] = {'currentData': {}, 'hourlyData': {}, 'dailyData': {}, 'iconsData': defaultIconsData}
        try:
            paramsDict['dictWeather']['currentData']['geo'] = {'latitude': float(paramsDict['geolatitude']), 'longitude': float(paramsDict['geolongitude'])}
        except Exception:
            paramsDict['dictWeather']['currentData']['geo'] = {}
        paramsDict['dictWeatherfile'] = 'dictWeather_%s.json' % paramsDict['currEntryID']
        if datetime.now().year < 2023:
            print('\tData nie ustawiona, synchonizacja z ntp.nask.pl...')
            os.system('ntpdate -bs ntp.nask.pl')
        if paramsDict['entryType'] == 'client' and paramsDict['mainEntryADDR'] != '0.0.0.0':
            try:
                urllib_urlretrieve('ftp://%s:%s@%s/tmp/.MSNdata/JSONfiles.list' % (paramsDict['mainEntryUSER'], paramsDict['mainEntryPASS'], paramsDict['mainEntryADDR']), 
                                                                                   os.path.join(paramsDict['tmpFolder'], 'JSONfiles.list'))
                print('\tdownioaded JSONfiles.list from main system...')
            except Exception as e:
                print('EXCEPTION downioading JSONfiles.list from main system: %s' % str(e))
                try:
                    print('\tdownioading dictWeather_%s.json from main system...' % paramsDict['currEntryID'])
                    urllib_urlretrieve('ftp://%s:%s@%s/tmp/.MSNdata/dictWeather_%s.json' % (paramsDict['mainEntryUSER'], paramsDict['mainEntryPASS'],
                                                                                            paramsDict['mainEntryADDR'], paramsDict['mainEntryID']), 
                                                                                            os.path.join(paramsDict['tmpFolder'], 'dictWeather_%s.json' % paramsDict['currEntryID']))
                    paramsDict['weatherSearchFullName'] = ''
                    paramsDict['airThingSpeakChannelID'] = ''
                    paramsDict['airlyAPIKEY'] = ''
                    paramsDict['airlyID'] = ''
                    paramsDict['airLooko2ID'] = ''
                    paramsDict['airSmogTokID'] = ''
                except Exception as e:
                    saveJsonDict(paramsDict['dictWeatherfile'], paramsDict['dictWeather'], False, True)
                    print('EXCEPTION downioading dictWeather_X.json from main system: %s' % str(e))
            if os.path.exists(os.path.join(paramsDict['tmpFolder'], 'JSONfiles.list')):
                filesToDownload = open(os.path.join(paramsDict['tmpFolder'], 'JSONfiles.list'), 'r').readlines()
                for jsonFile in filesToDownload:
                    jsonFile = jsonFile.strip()
                    try:
                        urllib_urlretrieve('ftp://%s:%s@%s/tmp/.MSNdata/%s' % (paramsDict['mainEntryUSER'], paramsDict['mainEntryPASS'], paramsDict['mainEntryADDR'], jsonFile), 
                                                                                           os.path.join(paramsDict['tmpFolder'], jsonFile))
                        print('\tdownioaded %s from main system...' % jsonFile)
                    except Exception as e:
                        print('EXCEPTION downloading %s: %s' % (jsonFile, str(e)))
                try:
                    urllib_urlretrieve('ftp://%s:%s@%s/usr/lib/enigma2/python/Plugins/Extensions/MSNweather/histograms.data' % (paramsDict['mainEntryUSER'], paramsDict['mainEntryPASS'], paramsDict['mainEntryADDR']), 
                                                                                   os.path.join(paramsDict['pluginPath'], 'histograms.data'))
                    print('\tdownioaded histograms.data from main system...')
                except Exception as e:
                    print('EXCEPTION downioading histograms.data from main system: %s' % str(e))
            quit()
        else:
            nowTime = int(time.time())
            try:
                if os.path.exists(os.path.join(paramsDict['tmpFolder'], paramsDict['dictWeatherfile'])):
                    fileTime = round(os.stat(os.path.join(paramsDict['tmpFolder'], paramsDict['dictWeatherfile'])).st_mtime)
                    deltaMins = int((nowTime - fileTime) / 60)
                    if deltaMins >= 10 and datetime.utcfromtimestamp(nowTime).hour != datetime.utcfromtimestamp(fileTime).hour:
                        print('\t%s modified %s mins ago, refreshing...' % (paramsDict['dictWeatherfile'], deltaMins))
                    elif paramsDict['DEBUG'] == 'True':
                        print('\tDEBUG enabled, refreshing...')
                    else:
                        print('\t%s modified %s mins ago, nothing to refresh' % (paramsDict['dictWeatherfile'], deltaMins))
                        quit()
                else:
                    print('\t"%s" does not exists, refreshing...' % os.path.join(paramsDict['tmpFolder'], paramsDict['dictWeatherfile']))
            except Exception as e:
                print('EXCEPTION in __main__ last update analysis: ', str(e))

            if paramsDict['currEntryID'] == '0':
                paramsDict['Histogram'] = 'True'
            if paramsDict['weatherSearchFullName'] != '':
                if not paramsDict['locationcode'].startswith('loc='):
                    url = 'http://weather.service.msn.com/data.aspx?src=windows&weadegreetype=%s&culture=%s&wealocations=%s' % (paramsDict['degreetype'], paramsDict['language'], urllib_quote(paramsDict['locationcode']))
                    initThread(url, 'data_msn.xml')
                calculateSun()
                calculateMoon()
                if paramsDict['msnAPIKEY'] == '':
                    paramsDict['msnAPIKEY'] = 'j5i4gDqHL6nGYwx5wi5kRhXjtf2c5qgFX9fzfk0TOo' #'0QfOX3Vn51YCzitbLaRkTTBadtWpgTN8NZLW0C1SEM'
                if paramsDict['geolatitude'] != '' and paramsDict['geolongitude'] != '' and paramsDict['geolatitude'] != 'auto' and paramsDict['geolongitude'] != 'auto':
                    cf = os.path.join(paramsDict['tmpFolder'], 'dictMSNweather_calendar_%s.json' % paramsDict['currEntryID'])
                    if not os.path.exists(cf): print("\tDownoading Monthly data")
                    elif int((nowTime - round(os.stat(cf).st_mtime)) /3600) > 1 and datetime.now().hour == 0: print("\tUpdating Monthly data")
                    else:
                        print("\tMonthly data up-2-date(last update %s hours ago)" % int((nowTime - round(os.stat(cf).st_mtime)) /3600))
                        cf = ''
                    if 0: #dzialalo do konca 2024 cf != '':
                        currDate = datetime.now()
                        startDate = currDate.strftime('%Y-%m-%d')
                        endDate = currDate + timedelta(days = 180)
                        endDate = endDate.replace(day=1)
                        endDate = endDate - timedelta(days=1)
                        endDate = endDate.strftime('%Y-%m-%d')
                        url = 'https://api.msn.com/weather/calendar?apiKey=%s&locale=%s&region=%s&lon=%s&lat=%s&units=%s&startDate=%s&endDate=%s' % (paramsDict['msnAPIKEY'], 
                                                                                                                                                     paramsDict['language'], 
                                                                                                                                                     paramsDict['language'][-2], 
                                                                                                                                                     paramsDict['geolongitude'],
                                                                                                                                                     paramsDict['geolatitude'], 
                                                                                                                                                     paramsDict['degreetype'],
                                                                                                                                                     startDate,
                                                                                                                                                     endDate
                                                                                                                                                    )
                        print(url)
                        initThread(url, 'msn_api.calendar')
                    if 1: #cf != '':
                        currDate = datetime.now()
                        startDate = currDate.strftime('%Y%m%d')
                        endDate = currDate + timedelta(days = 180)
                        endDate = endDate.replace(day=1)
                        endDate = endDate - timedelta(days=1)
                        endDate = endDate.strftime('%Y%m%d')
                        url = 'https://api.msn.com/weather/weathertrends?apiKey=' + paramsDict['msnAPIKEY']
                        url += '&locale='+ paramsDict['language'] + '&region=' + paramsDict['language'][-2:]
                        url += '&lon='+ paramsDict['geolongitude'] + '&lat=' + paramsDict['geolatitude']
                        url += '&units=' + paramsDict['degreetype']
                        url += '&startDate=' + startDate + '&endDate=' + endDate
                        #print('URL-weathertrends:', url)
                        initThread(url, 'msn_api.weathertrends')
                    for dataType in ('current', 'overview','dailyforecast','hourlytrend','dailytrend'):
                        url = 'https://api.msn.com/weather/' + dataType
                        url += '?apiKey=' + paramsDict['msnAPIKEY']
                        url += '&locale='+ paramsDict['language'] + '&region=' + paramsDict['language'][-2:]
                        url += '&lon='+ paramsDict['geolongitude'] + '&lat=' + paramsDict['geolatitude']
                        url += '&units=' + paramsDict['degreetype']
                        url += '&days=10'
                        initThread(url, 'msn_api.%s' % dataType)
                #else: #stare niedzialajace juz
                #    url = 'https://www.msn.com/%s/weather?culture=%s&weadegreetype=%s&form=PRWLAS&q=%s' % (language, language, degreetype, urllib_quote(paramsDict['weatherSearchFullName']))
                #    initThread(url, 'data_msn.web')
                
            if paramsDict['airThingSpeakChannelID'] != '':
                url = 'https://thingspeak.com/channels/%s/feeds.xml?average=10&results=1' % paramsDict['airThingSpeakChannelID']
                initThread(url, 'data_thingSpeak.xml')
            if paramsDict['Fcity'] == '':
                if os.path.exists(os.path.join(paramsDict['pluginPath'], 'icons', 'meteogram.png')):
                    os.remove(os.path.join(paramsDict['pluginPath'], 'icons', 'meteogram.png'))
            else:
                url = 'https://www.foreca.net/%s?lang=%s&units=metric&tf=24h' % (paramsDict['Fcity'], paramsDict['language'][:2])
                initThread(url, 'ForecaMeteogram')
            if paramsDict['Fmeteo'] != '':
                HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:54.0) Gecko/20100101 Firefox/54.0'}
                urls = []
                if paramsDict['language'] == 'pl-PL' and not paramsDict['Fmeteo'].startswith('pl/'):
                    paramsDict['Fmeteo'] = 'pl/' + paramsDict['Fmeteo']
                elif paramsDict['language'][:2] == 'de' and not paramsDict['Fmeteo'].startswith('de/'):
                    paramsDict['Fmeteo'] = 'de/' + paramsDict['Fmeteo']
                elif paramsDict['Fmeteo'][2:3] != '/':
                    paramsDict['Fmeteo'] = paramsDict['language'][:2] + '/' + paramsDict['Fmeteo']
                urls.append(('https://www.foreca.com/%s' % paramsDict['Fmeteo'], 'Fmeteo_today'))
                urls.append(('https://www.foreca.com/%s/10-day-forecast' % paramsDict['Fmeteo'], 'Fmeteo_10-day-forecast'))
                urls.append(('https://www.foreca.com/%s/hourly?day=0' % paramsDict['Fmeteo'], 'Fmeteo_hourly_day_0'))
                urls.append(('https://www.foreca.com/%s/hourly?day=1' % paramsDict['Fmeteo'], 'Fmeteo_hourly_day_1'))
                urls.append(('https://www.foreca.com/%s/hourly?day=2' % paramsDict['Fmeteo'], 'Fmeteo_hourly_day_2'))
                urls.append(('https://www.foreca.com/%s/hourly?day=3' % paramsDict['Fmeteo'], 'Fmeteo_hourly_day_3'))
                urls.append(('https://www.foreca.com/%s/hourly?day=4' % paramsDict['Fmeteo'], 'Fmeteo_hourly_day_4'))
                urls.append(('https://www.foreca.com/%s/hourly?day=5' % paramsDict['Fmeteo'], 'Fmeteo_hourly_day_5'))
                urls.append(('https://www.foreca.com/%s/hourly?day=6' % paramsDict['Fmeteo'], 'Fmeteo_hourly_day_6'))
                urls.append(('https://www.foreca.com/%s/hourly?day=7' % paramsDict['Fmeteo'], 'Fmeteo_hourly_day_7'))
                urls.append(('https://www.foreca.com/%s/hourly?day=8' % paramsDict['Fmeteo'], 'Fmeteo_hourly_day_8'))
                urls.append(('https://www.foreca.com/%s/hourly?day=9' % paramsDict['Fmeteo'], 'Fmeteo_hourly_day_9'))
                for url in urls:
                    initThread(url[0], url[1], HEADERS)
                
            if paramsDict['language'] == 'pl-PL':
                img = 'image_b_pl.png'
            else:
                if paramsDict['language'] == 'de-DE':
                    img = 'image_b_de.png'
                else:
                    img = 'image_b_eu.png'
            url = 'http://images.blitzortung.org/Images/%s' % img
            initThread(url, 'motionBurze')
            if paramsDict['airlyAPIKEY'] != '' and paramsDict['airlyID'] != '':
                HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:54.0) Gecko/20100101 Firefox/54.0', 'Accept': 'application/json', 'apikey': paramsDict['airlyAPIKEY']}
                if paramsDict['language'] == 'pl-PL':
                    HEADERS['Accept-Language'] = 'pl'
                urls = [
                     (
                      'https://airapi.airly.eu/v2/measurements/installation?includeWind=true&indexType=AIRLY_CAQI&installationId=%s' % paramsDict['airlyID'], 'airlyData_%s.json' % paramsDict['currEntryID'])]
                if not os.path.exists(os.path.join(paramsDict['tmpFolder'], 'airlyInfo_%s.json' % paramsDict['currEntryID'])):
                    urls.append(('https://airapi.airly.eu/v2/installations/%s' % paramsDict['airlyID'], 'airlyInfo_%s.json' % paramsDict['currEntryID']))
                else:
                    paramsDict['airlyInfo_%s.json' % paramsDict['currEntryID']] = readJson('airlyInfo_%s.json' % paramsDict['currEntryID'])
                for url in urls:
                    initThread(url[0], url[1], HEADERS)

            if paramsDict['airLooko2ID'] != '':
                url = 'http://looko2.com/tracker.php?lan=&search=%s' % paramsDict['airLooko2ID']
                initThread(url, 'looko2')
            if paramsDict['airGiosID'] != '':
                url = 'http://api.gios.gov.pl/pjp-api/rest/station/sensors/%s' % paramsDict['airGiosID']
                initThread(url, 'Gios')
                if not os.path.exists(os.path.join(paramsDict['tmpFolder'], 'giosInfo_%s.json' % paramsDict['currEntryID'])):
                    url = 'http://api.gios.gov.pl/pjp-api/rest/station/findAll'
                    initThread(url, 'GiosInfo')
                else:
                    paramsDict['giosInfo_%s.json' % paramsDict['currEntryID']] = readJson('giosInfo_%s.json' % paramsDict['currEntryID'])
            if paramsDict['airBleboxID'] != '':
                url = 'https://api.sensors.blebox.eu/api/air/device/%s' % paramsDict['airBleboxID']
                initThread(url, 'Blebox')
            if paramsDict['airOpenSenseID'] != '':
                HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:54.0) Gecko/20100101 Firefox/54.0', 'Accept': 'application/json', 'Accept-Language': 'pl'}
                url = 'https://api.opensensemap.org/boxes/%s' % paramsDict['airOpenSenseID']
                initThread(url, 'OpenSense', HEADERS)
            if paramsDict['airSmogTokID'] != '':
                HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:54.0) Gecko/20100101 Firefox/54.0', 'Accept': 'application/json', 'Accept-Language': 'pl'}
                url = 'https://smogtok.com/apprest/probedata/%s' % paramsDict['airSmogTokID']
                initThread(url, 'SmogTok')
            
            #czekamy na zakonczenie watkow
            for index, thread in enumerate(threads):
                thread.join(10)
            
            #jak sie same nie skonczyly to im pomagamy
            for index, thread in enumerate(threads):
                if thread.is_alive():
                    try:
                        thread.terminate()
                    except Exception:
                        pass
            
            time.sleep(0.3)
            #a jak sa nadal ubijamy
            for index, thread in enumerate(threads):
                if thread.is_alive():
                    try:
                        thread.kill()
                    except Exception:
                        pass
                    
            print('\t==================================================')
            print('\twszystkie watki zakonczone, lacze wszystko do kupy')
            print('\t==================================================')
            print('\tDane z API/WEB: currentData=%s\n\t\tdailyData=%s\n\t\thourlyData=%s' % (len(paramsDict['dictWeather']['currentData']),len(paramsDict['dictWeather']['dailyData']),len(paramsDict['dictWeather']['hourlyData'])))
            if len(paramsDict['dictWeather']['currentData']) > 9 and len(paramsDict['dictWeather']['dailyData']) >= 10 and len(paramsDict['dictWeather']['hourlyData']) >= 24:
                useForecaDicts = False
            else:
                #analiza danych z foreca
                if paramsDict['Fmeteo'] != '':
                    for jsonToAnalyze in ['Fmeteo_today', 'Fmeteo_hourly_day_0', 'Fmeteo_hourly_day_1',
                                          'Fmeteo_hourly_day_2', 'Fmeteo_hourly_day_3', 'Fmeteo_hourly_day_4', 'Fmeteo_hourly_day_5',
                                          'Fmeteo_hourly_day_6', 'Fmeteo_hourly_day_7', 'Fmeteo_hourly_day_8', 'Fmeteo_hourly_day_9',
                                          'Fmeteo_10-day-forecast',]:
                        analyze_ForecaMeteo(jsonToAnalyze)
                    useForecaDicts = True
            try:
                xmlDict = paramsDict['currentXMLweather']
                print('\tuzupelniam currentData danymi z xml-a, jesli czegos brakuje')
                manageCurrenDataWeatherItem(doUpdate=False, keyName='temperature', source='msnxml', val=xmlDict.get('temperature', ''), units='°' + paramsDict['degreetype'])
                manageCurrenDataWeatherItem(doUpdate=False, keyName='skytext', colorCode='', inList=False, name='', source='msnxml', val=xmlDict.get('skytext', ''), units='')
                manageCurrenDataWeatherItem(doUpdate=False, keyName='skycode', colorCode='', inList=False, name='', source='msnxml', val=xmlDict.get('skycode', ''), units='')
                manageCurrenDataWeatherItem(doUpdate=False, keyName='iconfilename', colorCode='', inList=False, name='', source='msnxml', val=xmlDict.get('iconFilename', ''), units='')
                manageCurrenDataWeatherItem(doUpdate=False, keyName='observationtime', colorCode='', inList=False, name='', source='msnxml', val=xmlDict.get('observationtime', ''), units='')
                manageCurrenDataWeatherItem(doUpdate=False, keyName='observationpoint', colorCode='', inList=False, name='', source='msnxml', val=xmlDict.get('observationpoint', ''), units='')
                manageCurrenDataWeatherItem(doUpdate=False, keyName='feelslike', colorCode='', inList=True, name='', source='msnxml', val=xmlDict.get('feelslike', ''), units='°' + paramsDict['degreetype'])
                manageCurrenDataWeatherItem(doUpdate=False, keyName='humidity', colorCode='', inList=True, name='', source='msnxml', val=xmlDict.get('humidity', ''), units='%')
                manageCurrenDataWeatherItem(doUpdate=False, keyName='wind_speed', colorCode='', inList=True, name=_('wind'), source='msnxml', val=str(re.findall('[+-]?[0-9]+', xmlDict.get('wind_speed', ''))[0]), units='km/h')
                manageCurrenDataWeatherItem(doUpdate=False, keyName='wind_dir', colorCode='', inList=True, name='', source='msnxml', val='?', units='')
                saveJsonDict(paramsDict['dictWeatherfile'], paramsDict['dictWeather'], False, True)
            except Exception:
                pass
            #dane dziennie z foreca
            if useForecaDicts == True and len(paramsDict['Fmeteo_10-day-forecast']) > 0:
                tmpDict = paramsDict['dictWeather']['dailyData']
                print('\tuzupelniam dailyData danymi z Foreca')
                minRecord = len(tmpDict)
                idx = 0
                for item in paramsDict['Fmeteo_10-day-forecast']:
                    if idx >= minRecord:
                        paramsDict['dictWeather']['dailyData'][item] = paramsDict['Fmeteo_10-day-forecast'][item]
                        paramsDict['dictWeather']['dailyData'][item]['rainprecip'] = paramsDict['dailyRainPrecip-%s' % idx]
                    idx += 1
            #saveJsonDict(paramsDict['dictWeatherfile'], paramsDict['dictWeather'], False, True)
            
            #dane dzienne z xml-a
            if len(paramsDict['dictWeather']['dailyData']) == 0:
                print('\tuzupelniam dailyData danymi z xml-a')
                paramsDict['dictWeather']['dailyData'] = paramsDict['dailyXMLweather']
            
            saveJsonDict(paramsDict['dictWeatherfile'], paramsDict['dictWeather'], False, True)

            #dane godzinne z foreca
            if useForecaDicts == True and len(paramsDict['Fmeteo_hourly_day_0']) > 0 and len(paramsDict['Fmeteo_hourly_day_1']) > 0:
                idx = 0
                print('\tuzupelniam hourlyData danymi z Fmeteo_hourly_day_X')
                paramsDict['dictWeather']['hourlyData']['title'] = _('Hourly')
                while idx < 24:
                    if idx < len(paramsDict['Fmeteo_hourly_day_0']):
                        paramsDict['dictWeather']['hourlyData']["Record=%s" % idx ] = paramsDict['Fmeteo_hourly_day_0']["Record=%s" % idx]
                    else:
                        paramsDict['dictWeather']['hourlyData']["Record=%s" % idx ] = paramsDict['Fmeteo_hourly_day_1']["Record=%s" % (idx - len(paramsDict['Fmeteo_hourly_day_0']))]
                    idx += 1
                
            saveJsonDict(paramsDict['dictWeatherfile'], paramsDict['dictWeather'], False, True)

            def useArly(override):
                if paramsDict['airlyAPIKEY'] != '' and paramsDict['airlyID'] != '' and len(paramsDict.get('airlyData.json','')) > 0:
                    airlyData = paramsDict['airlyData.json']
                    if len(airlyData) == 0:
                        print('\tbrak danych airly, opuszczam.')
                        return
                    elif airlyData.get('message', '') == 'UNAUTHORIZED':
                        print(_('\twrong Airly API key, exiting.'))
                        return
                    elif airlyData.get('errorCode', '') != '':
                        print('\t%s' % airlyData.get('message', airlyData.get('errorCode')))
                        return
                    elif str(airlyData.get('current', {}).get('fromDateTime', ''))[:10] != str(datetime.now().strftime('%Y-%m-%d')):
                        print(_('\tAirly data outdated, exiting.'))
                        return
                    paramsDict['dictWeather']['currentData']['airlyobservationpoint'] = paramsDict[('airlyInfo_%s.json' % paramsDict['currEntryID'])]['address']
                    print('\tladowanie danych airly...')
                    date, time, DateTimeObject = ISO3339toDATETIME(airlyData['current']['fromDateTime'], 1)
                    paramsDict['dictWeather']['currentData']['airlyobservationtime'] = {'name': _('Airly sync time'), 'date': str(date), 'time': str(time), 'datetime': '%s %s' % (str(date), str(time)), 
                       'inList': False}
                    name = _(airlyData['current']['indexes'][0]['name'])
                    colorCode = airlyData['current']['indexes'][0]['color']
                    colorCode = Hex2strColor(int(colorCode.replace('#', '0x00'), 16))
                    info = _(airlyData['current']['indexes'][0]['description'])
                    if 'not available' in info.lower():
                        info = ''
                        colorCode = ''
                    else:
                        if info.endswith('.'):
                            info = info[:-1]
                        info = colorCode + info
                        level = airlyData['current']['indexes'][0]['level']
                        iconfilename = os.path.join(paramsDict['pluginPath'], 'icons', 'Airly_IDX_%s.png' % level)
                        advice = _(airlyData['current']['indexes'][0]['advice'])
                        if advice is None:
                            advice = ''
                        val = airlyData['current']['indexes'][0]['value']
                        if val is None:
                            val = '?'
                        else:
                            val = str(int(round(float(val))))
                        valInfo = '%s%s' % (colorCode, val)
                        paramsDict['dictWeather']['currentData']['airIndex'] = {'colorCode': colorCode, 'level': level, 
                           'name': name, 
                           'iconfilename': iconfilename, 
                           'info': info, 
                           'advice': advice, 
                           'val': val, 
                           'valInfo': valInfo, 
                           'source': 'airly'}
                        paramsDict['dictWeather']['currentData']['airlyLimitsDaily'] = airlyData.get('RateLimit-Limit-day', '')
                        paramsDict['dictWeather']['currentData']['airlyLimitsDailyRemaining'] = airlyData.get('RateLimit-Remaining-day', '')
                        paramsDict['dictWeather']['currentData']['airlyLimitsMinutelly'] = airlyData.get('RateLimit-Limit-minute', '')
                        paramsDict['dictWeather']['currentData']['airlyLimitsMinutellyRemaining'] = airlyData.get('RateLimit-Remaining-minute', '')
                        valuesList = airlyData['current']['values']
                        for val in valuesList:
                            colorCode = ''
                            name = val['name']
                            lname = name.lower()
                            name = name.replace('PM25', 'PM2.5')
                            longname = param2name(name)
                            val = str(int(round(val['value'])))
                            valInfo = None
                            units = None
                            if lname in ('wind_bearing', 'temperature'):
                                inList = False
                            else:
                                inList = True
                            manageCurrenDataWeatherItem(doUpdate=override, keyName=lname, colorCode=colorCode, inList=inList, name=_(name), source='airly', val=val, units=units, valInfo=valInfo, longName=longname)

                return


            def useTS(override):
                if paramsDict['airThingSpeakChannelID'] != '' and len(paramsDict.get('thingSpeakItems','')) > 0:
                    tsDict = paramsDict['thingSpeakItems']
                    if str(tsDict.get('ObservationTime', ''))[:10] != str(datetime.now().strftime('%Y-%m-%d')):
                        print(_('\toutdated THINGSPEAK data (%s), exiting.') % str(tsDict.get('ObservationTime', ''))[:10])
                        return
                    print(_('\tloadingTHINGSPEAK data...'))
                    paramsDict['dictWeather']['currentData']['tsobservationpoint'] = {'val': tsDict['name'], 'valInfo': tsDict['description']}
                    date, time, DateTimeObject = ISO3339toDATETIME(tsDict['ObservationTime'])
                    paramsDict['dictWeather']['currentData']['tsobservationtime'] = {'name': _('TS sync time'), 'date': str(date), 'time': str(time), 'datetime': '%s %s' % (str(date), str(time)), 'inList': False}
                    for key in tsDict:
                        if key.startswith('PM') and not key.endswith('Name') and not key.endswith('Value'):
                            colorCode = ''
                            valInfo = None
                            units = None
                            inList = True
                            name = key
                            lname = name.replace('PM2.5', 'PM25').lower()
                            val = tsDict[(key + 'Value')]
                            longname = param2name(name)
                            manageCurrenDataWeatherItem(doUpdate=override, keyName=lname, colorCode=colorCode, inList=inList, name=_(name), source='TS', val=val, units=units, valInfo=valInfo, longName=longname)

                return


            def useLookO2(override):
                if paramsDict['airLooko2ID'] != '' and len(paramsDict.get('dictLooko2','')) > 0:
                    tmpDict = paramsDict['dictLooko2']
                    if str(tmpDict.get('observationtime', {}).get('date', '')) != str(datetime.now().strftime('%Y-%m-%d')):
                        print('\tnieaktualne dane LookO2 (%s), opuszczam.' % str(tmpDict.get('date', '')))
                        return
                    print('\tladowanie danych LookO2...')
                    paramsDict['dictWeather']['currentData']['o2observationpoint'] = {'val': tmpDict['observationpoint'], 'valInfo': ''}
                    paramsDict['dictWeather']['currentData']['o2observationtime'] = {'name': _('O2 sync time'), 'date': tmpDict['observationtime']['date'], 
                       'time': tmpDict['observationtime']['time'], 
                       'datetime': tmpDict['observationtime']['datetime'], 
                       'inList': False}
                    advice = tmpDict['advice']
                    info = tmpDict['info']
                    colorCode = tmpDict['color']
                    colorCode = Hex2strColor(int(colorCode.replace('#', '0x00'), 16))
                    name = 'LOOKO2_IDX'
                    val = int(re.findall('[+-]?[0-9]+', info)[0])
                    if val == 0:
                        level = 'VERY_LOW'
                    else:
                        if val == 1:
                            level = 'LOW'
                        elif val == 2:
                            level = 'MEDIUM'
                        elif val == 3:
                            level = 'HIGH'
                        elif val == 4:
                            level = 'VERY_HIGH'
                        else:
                            level = 'EXTREME'
                    iconfilename = os.path.join(paramsDict['pluginPath'], 'icons', 'looko2_IDX_%s.png' % level)
                    valInfo = '%s%s' % (colorCode, val)
                    if override == True:
                        paramsDict['dictWeather']['currentData']['airIndex'] = {'colorCode': colorCode, 'level': level, 'name': name, 
                               'iconfilename': iconfilename, 
                               'info': info, 
                               'advice': advice, 
                               'val': str(val), 
                               'valInfo': valInfo, 
                               'source': 'Looko2'}
                    for key in tmpDict:
                        if key.startswith('PM'):
                            colorCode = ''
                            valInfo = None
                            units = None
                            inList = True
                            name = key
                            lname = name.replace('PM2.5', 'PM25').lower()
                            val = tmpDict[key]
                            longname = param2name(name)
                            manageCurrenDataWeatherItem(doUpdate=override, keyName=lname, colorCode=colorCode, inList=inList, name=_(name), source='Looko2', val=val, units=units, valInfo=valInfo, longName=longname)
                return


            def useGios(override):
                if paramsDict['airGiosID'] != '' and len(paramsDict.get('dictGios','')) > 0:
                    print('\tladowanie danych Gios do manipulacji...')
                    tmpDict = paramsDict['dictGios']
                    airIndex = 0
                    airCLR = ''
                    for key in tmpDict['sensors']:
                        colorCode = ''
                        valInfo = None
                        #GIOS Wyniki pomiarów wszystkich zanieczyszczeń  udostępnianych poprzez API wyświetlane są w jednostce μg/m3 również wyniki pomiarów CO - tlenku węgla
                        #(również wyniki pomiarów CO - tlenku węgla, dla którego wyniki pomiarów prezentowane na mapie bieżących 
                        #danych pomiarowych portalu Jakość Powietrza oraz w aplikacji mobilnej "Jakość Powietrza w Polsce" przeliczone są na mg/m3)
                        inList = True
                        name = key
                        lname = name.replace('PM2.5', 'PM25').lower()
                        if lname == 'co':
                            units = 'mg/m3'
                            val = round(float(tmpDict['sensors'][key]) / 1000 , 2)
                        else:
                            units = 'μg/m3'
                            val = int(round(tmpDict['sensors'][key]))
                        valCLR, valIDX = airQualityInfo(lname, val, retLevel=True)
                        if valIDX > airIndex:
                            airIndex = valIDX
                            airCLR = valCLR
                        longname = param2name(name)
                        manageCurrenDataWeatherItem(doUpdate=override, keyName=lname, colorCode=colorCode, inList=inList, name=_(name), source='GIOŚ', val=str(val), units=units, valInfo=valInfo, longName=longname)

                    paramsDict['dictWeather']['currentData']['giosobservationpoint'] = paramsDict[('giosInfo_%s.json' % paramsDict['currEntryID'])]
                    paramsDict['dictWeather']['currentData']['giosobservationtime'] = {'name': _('GIOS sync time'), 'date': tmpDict['observationtime']['date'], 
                       'time': tmpDict['observationtime']['time'], 
                       'datetime': tmpDict['observationtime']['datetime'], 
                       'inList': False}
                    advice = ''
                    info = 'Indeks Jakości Powietrza %s' % airIndex
                    name = 'GIOS_IDX'
                    if airIndex == 0:
                        level = 'VERY_GOOD'
                    elif airIndex == 1:
                        level = 'GOOD'
                    elif airIndex == 2:
                        level = 'MODERATE'
                    elif airIndex == 3:
                        level = 'ACCEPTABLE'
                    elif airIndex == 4:
                        level = 'BAD'
                    else:
                        level = 'VERY_BAD'
                    iconfilename = os.path.join(paramsDict['pluginPath'], 'icons','gios_IDX_%s.png' % level)
                    valInfo = '%s%s' % (airCLR, airIndex)
                    if override == True:
                        paramsDict['dictWeather']['currentData']['airIndex'] = {'colorCode': airCLR, 'level': level, 'name': name, 
                           'iconfilename': iconfilename, 
                           'info': info, 
                           'advice': advice, 
                           'val': str(airIndex), 
                           'valInfo': valInfo, 
                           'source': 'GIOŚ'}
                return


            def useBlebox(override):
                if paramsDict['airBleboxID'] != '' and len(paramsDict.get('dictBlebox','')) > 0:
                    print('\tladowanie danych Blebox do manipulacji...')
                    tmpDict = paramsDict['dictBlebox']
                    name = tmpDict['name']
                    if name is None:
                        name = '%s/%s' % (round(tmpDict['geolocation']['lat'], 1), round(tmpDict['geolocation']['lon'], 1))
                    paramsDict['dictWeather']['currentData']['bleboxobservationpoint'] = name
                    paramsDict['dictWeather']['currentData']['bleboxobservationtime'] = tmpDict['observationtime']
                    advice = ''
                    airIndex = tmpDict['airQualityLevel']
                    info = 'Indeks Jakości Powietrza %s' % airIndex
                    name = 'Blebox_IDX'
                    if airIndex == 0:
                        level = 'VERY_GOOD'
                    else:
                        if airIndex == 1:
                            level = 'GOOD'
                        elif airIndex == 2:
                            level = 'MODERATE'
                        elif airIndex == 3:
                            level = 'ACCEPTABLE'
                        elif airIndex == 4:
                            level = 'BAD'
                        else:
                            level = 'VERY_BAD'
                    airCLR = clr[level]
                    iconfilename = os.path.join(paramsDict['pluginPath'], 'icons', 'blebox_IDX_%s.png' % level)
                    valInfo = '%s%s' % (airCLR, airIndex)
                    if override == True:
                        paramsDict['dictWeather']['currentData']['airIndex'] = {'colorCode': airCLR, 'level': level, 'name': name, 
                               'iconfilename': iconfilename, 
                               'info': info, 
                               'advice': advice, 
                               'val': str(airIndex), 
                               'valInfo': valInfo, 
                               'source': 'Blebox'}
                    for idx in tmpDict['sensors']:
                        colorCode = ''
                        valInfo = None
                        units = None
                        inList = True
                        name = idx['type']
                        lname = name.replace('2.5', '25').lower()
                        val = int(round(idx['value']))
                        longname = param2name(name)
                        manageCurrenDataWeatherItem(doUpdate=override, keyName=lname, colorCode=colorCode, inList=inList, name=_(name), source='Blebox', val=str(val), units=units, valInfo=valInfo, longName=longname)
                return


            def useOpenSense(override):
                if paramsDict['airOpenSenseID'] != '' and len(paramsDict.get('dictOpenSense','')) > 0:
                    tmpDict = paramsDict['dictOpenSense']
                    if str(tmpDict['lastMeasurementAt'][:10]) != str(datetime.now().strftime('%Y-%m-%d')):
                        print('\tnieaktualne dane OpenSense (%s), opuszczam.' % str(tmpDict['lastMeasurementAt'][:10]))
                        return
                    print('\tladowanie danych OpenSense do manipulacji...')
                    date, time, DateTimeObject = ISO3339toDATETIME(tmpDict['lastMeasurementAt'], 1)
                    paramsDict['dictWeather']['currentData']['openSenseobservationtime'] = {'name': _('openSense sync time'), 'date': str(date), 
                       'time': str(time), 
                       'datetime': '%s %s' % (str(date), str(time)), 
                       'inList': False}
                    paramsDict['dictWeather']['currentData']['openSenseobservationpoint'] = tmpDict['name']
                    airIndex = 0
                    airCLR = ''
                    for sensorDict in tmpDict['sensors']:
                        colorCode = ''
                        valInfo = None
                        units = None
                        longname = None
                        name = sensorDict['title'].replace('Luftfeuchte', 'humidity').replace('Luftdruck', 'Pressure')
                        lname = name.lower()
                        lname = lname.replace('2.5', '25').replace('temperatur', 'temperature').replace('luftfeuchte', 'humidity')
                        lname = lname.replace('luftdruck', 'pressure')
                        if sensorDict['unit'] == 'Pa':
                            val = int(round(float(sensorDict['lastMeasurement']['value']) / 100))
                        else:
                            val = int(round(float(sensorDict['lastMeasurement']['value'])))
                        if lname in ('pressure', 'humidity', 'rel. humidity'):
                            inList = True
                        elif lname in ('temperature', ):
                            inList = False
                        elif lname in ('pm10', 'pm25', 'pm1', 'o3', 'no2', 'c6h6'):
                            inList = True
                            valCLR, valIDX = airQualityInfo(lname, val, retLevel=True)
                            if valIDX > airIndex:
                                airIndex = valIDX
                                airCLR = valCLR
                            longname = param2name(name)
                        else:
                            inList = False
                        manageCurrenDataWeatherItem(doUpdate=override, keyName=lname, colorCode=colorCode, inList=inList, name=_(name), source='OpenSense', val=str(val), units=units, valInfo=valInfo, longName=longname)

                    advice = ''
                    info = 'Indeks Jakości Powietrza %s' % airIndex
                    name = 'OpenSense_IDX'
                    if airIndex == 0:
                        level = 'VERY_GOOD'
                    elif airIndex == 1:
                        level = 'GOOD'
                    elif airIndex == 2:
                        level = 'MODERATE'
                    elif airIndex == 3:
                        level = 'ACCEPTABLE'
                    elif airIndex == 4:
                        level = 'BAD'
                    else:
                        level = 'VERY_BAD'
                    iconfilename = os.path.join(paramsDict['pluginPath'], 'icons', 'openSense_IDX_%s.png' % level)
                    valInfo = '%s%s' % (airCLR, airIndex)
                    if override == True:
                        paramsDict['dictWeather']['currentData']['airIndex'] = {'colorCode': airCLR, 'level': level, 'name': name, 
                           'iconfilename': iconfilename, 
                           'info': info, 
                           'advice': advice, 
                           'val': str(airIndex), 
                           'valInfo': valInfo, 
                           'source': 'OpenSense'}
                return

            def useSmogTok(override):
                if paramsDict['airSmogTokID'] != '' and len(paramsDict.get('dictSmogTok','')) > 0:
                    tmpDict = paramsDict['dictSmogTok']
                    if str(tmpDict['DT'][:10]) != str(datetime.now().strftime('%Y-%m-%d')):
                        print('\tnieaktualne dane SmogTOK (%s), opuszczam.' % str(tmpDict['DT'][:10]))
                        return
                    print('\tladowanie danych SmogTOK do manipulacji...')
                    date = tmpDict['DT'][:10]
                    time = tmpDict['DT'][11:16]
                    paramsDict['dictWeather']['currentData']['smogTokobservationtime'] = {'name': _('smogTok sync time'), 'date': str(date), 
                       'time': str(time), 
                       'datetime': '%s %s' % (str(date), str(time)), 
                       'inList': False}
                    paramsDict['dictWeather']['currentData']['smogTokobservationpoint'] = tmpDict['NAME']
                    airIndex = 0
                    airCLR = ''
                    advice = ''
                    airIndex = tmpDict['IJP']
                    info = 'Indeks Jakości Powietrza %s' % airIndex
                    name = 'smogTok_IDX'
                    if airIndex == 0:
                        level = 'VERY_GOOD'
                    else:
                        if airIndex == 1:
                            level = 'GOOD'
                        elif airIndex == 2:
                            level = 'MODERATE'
                        elif airIndex == 3:
                            level = 'ACCEPTABLE'
                        elif airIndex == 4:
                            level = 'BAD'
                        else:
                            level = 'VERY_BAD'
                    airCLR = clr[level]
                    iconfilename = os.path.join(paramsDict['pluginPath'], 'icons', 'smogtok_IDX_%s.png' % level)
                    valInfo = '%s%s' % (airCLR, airIndex)
                    if override == True:
                        paramsDict['dictWeather']['currentData']['airIndex'] = {'colorCode': airCLR, 'level': level, 'name': name, 
                               'iconfilename': iconfilename, 
                               'info': info, 
                               'advice': advice, 
                               'val': str(airIndex), 
                               'valInfo': valInfo, 
                               'source': 'smogTok'}
                    for idx in tmpDict['REGS']:
                        colorCode = ''
                        valInfo = None
                        units = None
                        inList = True
                        name = idx['REGNAME']
                        lname = name.replace(',', '.').replace(' ', '').replace('2.5', '25').lower()
                        if name   == 'PM 0,1':
                            lname = 'pm1'
                            name  = 'PM1'
                            units = 'µg/m3'
                            inList = True
                        elif name == 'PM 2,5':
                            lname = 'pm25'
                            name  = 'PM2.5'
                            units = 'µg/m3'
                            inList = True
                        elif name == 'PM 10':
                            lname = 'pm10'
                            name  = 'PM10'
                            units = 'µg/m3'
                            inList = True
                        elif name == 'Wilgotność':
                            lname = 'humidity'
                            #name  = ''
                            units = '%'
                            inList = True
                        elif name == 'Ciśnienie':
                            lname = 'pressure'
                            #name  = ''
                            units = 'hPa'
                            inList = True
                        elif name.startswith('Temp'):
                            lname = 'temperature'
                            #name  = ''
                            units = '°C'
                            inList = False
                        
                        val = int(round(idx['VALUE']))
                        longname = param2name(name)
                        manageCurrenDataWeatherItem(doUpdate=override, keyName=lname, colorCode=colorCode, inList=inList, name=_(name), source='smogTok', val=str(val), units=units, valInfo=valInfo, longName=longname)


            if paramsDict['SensorsPriority'].startswith('/'):
                paramsDict['SensorsPriority'] = open(paramsDict['SensorsPriority'], 'r').readline().strip()
            SensorsPriorities = paramsDict['SensorsPriority'].split(',')
            if SensorsPriorities[0] == 'MSN':
                overrideMSN = False
            else:
                overrideMSN = True
                SensorsPriorities.reverse()
            for sensor in SensorsPriorities:
                if sensor == 'MSN':
                    pass
                elif sensor == 'TS':
                    useTS(override=overrideMSN)
                elif sensor == 'Airly':
                    useArly(override=overrideMSN)
                elif sensor == 'LO2':
                    useLookO2(override=overrideMSN)
                elif sensor == 'GIOS':
                    useGios(override=overrideMSN)
                elif sensor == 'BleBox':
                    useBlebox(override=overrideMSN)
                elif sensor == 'OpenSense':
                    useOpenSense(override=overrideMSN)
                elif sensor == 'SmogTok':
                    useSmogTok(override=overrideMSN)

        print('\taktualizacja danych activeSource...')
        tmpDict = paramsDict['dictWeather']['currentData']
        activeSources = []
        for key in tmpDict:
            val = tmpDict[key]
            if isinstance(val, dict):
                source = val.get('source', '')
                src = source.replace('msnweb', 'MSN').replace('msnxml', 'MSN').replace('MSNAPI', 'MSN')
                if src != '' and src not in activeSources:
                    activeSources.append(src)

    names = ''
    observationpoints = ''
    observationtimes = ''
    if len(activeSources) > 0:
        idx = 0
        while idx < len(activeSources):
            name = activeSources[idx]
            names += name
            if name in ('MSN', 'foreca'):
                observationpoints += '%s: %s' % (name, tmpDict['observationpoint']['val'])
                observationtimes += '%s: %s' % (name, tmpDict['observationtime']['time'][:5])
            elif name == 'airly':
                observationpoints += '%s: %s %s' % (name, tmpDict['airlyobservationpoint']['displayAddress1'], tmpDict['airlyobservationpoint']['displayAddress2'])
                observationtimes += '%s: %s' % (name, tmpDict['airlyobservationtime']['time'])
            elif name == 'Looko2':
                observationpoints += '%s: %s' % (name, tmpDict['o2observationpoint']['val'])
                observationtimes += '%s: %s' % (name, tmpDict['o2observationtime']['time'][:5])
            elif name == 'GIOŚ':
                observationpoints += '%s: %s' % (name, tmpDict['giosobservationpoint']['stationName'])
                observationtimes += '%s: %s' % (name, tmpDict['giosobservationtime']['time'][:5])
            elif name == 'Blebox':
                observationpoints += '%s: %s' % (name, tmpDict['bleboxobservationpoint'])
                observationtimes += '%s: %s' % (name, tmpDict['bleboxobservationtime']['time'][:5])
            elif name == 'OpenSense':
                observationpoints += '%s: %s' % (name, tmpDict['openSenseobservationpoint'])
                observationtimes += '%s: %s' % (name, tmpDict['openSenseobservationtime']['time'][:5])
            elif name == 'smogTok':
                observationpoints += '%s: %s' % (name, tmpDict['smogTokobservationpoint'])
                observationtimes += '%s: %s' % (name, tmpDict['smogTokobservationtime']['time'][:5])
            if idx < len(activeSources) - 1:
                names += ', '
                observationpoints += ', '
                observationtimes += ', '
            idx += 1

    paramsDict['dictWeather']['currentData']['activeSources'] = {'names': names, 'observationpoints': observationpoints, 'observationpointsInfo': _('Punkty pomiarowe %s') % observationpoints, 
       'observationtimes': observationtimes, 
       'observationtimesInfo': _('Zaktualizowano %s') % observationtimes}
    print('\tzapisywanie danych')
    saveJsonDict(paramsDict['dictWeatherfile'], paramsDict['dictWeather'], False, True)
    buildHistogram()
    JSONfiles = ''
    nowTime = int(time.time())
    for myfile in os.listdir(paramsDict['tmpFolder']):
        if myfile.endswith('.json') and os.path.isfile(os.path.join(paramsDict['tmpFolder'], myfile)):
            if not myfile.startswith('airlyInfo') and not myfile.startswith('giosInfo'):
                fileTime = round(os.stat(os.path.join(paramsDict['tmpFolder'], myfile)).st_mtime)
                deltaMins = int((nowTime - fileTime) / 60)
                if deltaMins > 800:
                    os.remove(os.path.join(paramsDict['tmpFolder'], myfile))
                    continue
            JSONfiles += myfile + '\n'
    if len(JSONfiles) > 5:
        open(os.path.join(paramsDict['tmpFolder'], 'JSONfiles.list'), "w").write(JSONfiles)
    
if __name__ == '__main__':
    print('\n####################################\n__name__ >>>')
    mainProc()
    print('__name__ <<<')
