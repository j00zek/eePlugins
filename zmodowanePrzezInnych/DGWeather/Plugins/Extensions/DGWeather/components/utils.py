# zawiera komponenty wapolne skopiowane z DGWeather2.py
# w wiekszosci sekcja #j00zek >>>

import io, json, os, re, requests, sys, time, traceback, urllib

log = True
e2log = True
logFolder = "/tmp/dgWeather" # oddzialny katalog do logowania zeby wszystko co zwiazane z wtyczka bylo w jednym miejscu
if not os.path.exists(logFolder):
    os.mkdir(logFolder)
logFile = os.path.join(logFolder, "dgWeather.log")

skinPath = '/usr/lib/enigma2/python/Plugins/Extensions/DGWeather/skin/'

def write_log(svalue):
    if log:
        t = time.localtime()
        logtime = '%02d:%02d:%02d' % (t.tm_hour, t.tm_min, t.tm_sec)
        dgWeather_log = open(logFile, 'a')
        dgWeather_log.write(str(logtime) + ' - ' + str(svalue) + '\n')
        dgWeather_log.close()
    if e2log:
        print(svalue)

def Exc_log(svalue=''): #taka konstrukcja zwraca nie tylko bąd ale też gdzie konkretnie wystąpił. Jak w logu e2
    full_exc = traceback.format_exc()
    write_log(full_exc)

PyMajorVersion = sys.version_info.major

if PyMajorVersion >= 3:
    unicode = str
    urllib_unquote = urllib.parse.unquote
else:
    urllib_unquote = urllib.unquote
    
def downloadWebPage(webURL, HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:54.0) Gecko/20100101 Firefox/54.0', 'Accept-Charset': 'utf-8'}):
    def decodeHTML(text):
        text = text.replace('&#243;', str('ó'))
        text = text.replace('&#176;', '°').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
        text = text.replace('&#228;', 'ä').replace('&#196;', 'Ă').replace('&#246;', 'ö').replace('&#214;', 'Ö').replace('&#252;', 'ü').replace('&#220;', 'Ü').replace('&#223;', 'ß')
        return text
    write_log('downloadWebPage: ' + str(webURL))
    try:
        resp = requests.get(webURL, headers=HEADERS, timeout=5)
        webContent = resp.content
        webContent = urllib_unquote(webContent)
        webContent = decodeHTML(webContent)
        return webContent
    except Exception as e:
        Exc_log("EXCEPTION '%s' in downloadWebPage() for %s" % (str(e), webURL))
        return None
    
def fileTimeStamp(fileName):
    filePathName = os.path.join(logFolder,fileName)
    if os.path.exists(filePathName):
        return round(os.stat(filePathName).st_mtime)
    else:
        return 0
        
def saveJsonDict(fileName, jsonDict):
#    write_log("saveJsonDict(%s)" % os.path.join(logFolder,fileName))
    with io.open(os.path.join(logFolder,fileName), 'w', encoding='utf8') as (outfile):
        json_data = json.dumps(jsonDict, indent=4, sort_keys=True, ensure_ascii=False)
        outfile.write(unicode(json_data))

def LoadJsonDict(fileName, retDictIfError = {}):
    filePathName = os.path.join(logFolder,fileName)
    if os.path.exists(filePathName):
        try:
            with open(filePathName) as json_data:
                #write_log("LoadJsonDict(%s)" % os.path.join(logFolder,fileName))
                return(json.load(json_data))
        except Exception as e:
            Exc_log("EXCEPTION '%s' in LoadJsonDict() for %s" % (str(e), fileName))
            return retDictIfError
    else:
        return retDictIfError
        
def reLoadJsonDict(fileName, lastDict, DiffSeconds = 60 ):
    filePathName = os.path.join(logFolder,fileName)
    LastTimeStamp = (int(time.time()) - DiffSeconds)
    if os.path.exists(filePathName) and fileTimeStamp(fileName) > LastTimeStamp:
        try:
            with open(filePathName) as json_data:
                #write_log("reLoadJsonDict(%s)" % filePathName)
                return(json.load(json_data))
        except Exception as e:
            Exc_log("EXCEPTION '%s' in reLoadJsonDict() for %s" % (str(e), fileName))
            return lastDict
    else:
        return lastDict

def loadskin(filename):
    skin = None
    with open(os.path.join(skinPath, filename), 'r') as f:
        skin = f.read()
        f.close()
    return skin
