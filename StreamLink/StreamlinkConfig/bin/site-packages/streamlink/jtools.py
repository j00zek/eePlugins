#!/usr/bin/python
# j00zek 2020-2022

try:
    from streamlink.e2config import getE2config
except Exception:
    from e2config import getE2config

import base64, os, sys, time, warnings

os.environ["XDG_CONFIG_HOME"] = "/etc" #aby config streamlinka dzialal
PyMajorVersion = sys.version_info.major
   
if PyMajorVersion >= 3:
    unicode = str
    from urllib.request import urlretrieve as urllib_urlretrieve
    from urllib.parse import unquote as urllib_unquote, quote as urllib_quote
else: #py2
    from urllib import urlretrieve as urllib_urlretrieve, unquote as urllib_unquote, quote as urllib_quote

warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    
remoteE2standbyCMD = None

def clearCache(): #zawsze dobrze oczyscic przed uruchomieniem os.system aby nie bylo GS-a
    with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")

def killSRVprocess(KeepPID):
    CMDs = []
    CMDs.append("[ `ps -ef|grep -v grep|grep -c ffmpeg` -gt 0 ] && (ps -ef|grep -v grep|grep ffmpeg|awk '{print $2}'|xargs kill)")
    #ubicie streamlinkSRV ale tylko starego
    CMDs.append("if [ `ps -ef|grep -v grep|grep -v %s|grep -c streamlinkSRV` -gt 0 ];then" % KeepPID)
    CMDs.append("     (ps -ef|grep -v grep|grep -v %s|grep streamlinkSRV|awk '{print $2}'|xargs kill)" % KeepPID)
    CMDs.append('fi')
    os.system('\n'.join(CMDs))

def cleanCMD(forceKill = True, KeepPID = 0): #czyszczenie smieci
    clearCache()
    CMDs = []
    CMDs.append(r'/usr/bin/killall exteplayer3 2>/dev/null') #close external player when used
    CMDs.append(r'/usr/bin/killall -9 exteplayer3 2>/dev/null') #close external player when used
    if KeepPID != 0:
        CMDs.append(r"[ `ps -ef|grep -v grep|grep -v %s|grep -c exteplayer3` -gt 0 ] && (ps -ef|grep -v grep|grep -v %s|grep exteplayer3|awk '{print $2}'|xargs kill)" % (KeepPID,KeepPID))
    if forceKill == True:
        CMDs.append(r"[ `ps -ef|grep -v grep|grep -c ffmpeg` -gt 0 ] && (ps -ef|grep -v grep|grep ffmpeg|awk '{print $2}'|xargs kill)")
    CMDs.append(r"kill `netstat -peanut|grep 8808|grep -oE 'LISTEN[ ]+[0-9]+'|grep -oE '[0-9]+'` 2>/dev/null")
    CMDs.append(r'killall hlsdl 2>/dev/null')
    CMDs.append(r'if [ `ps -ef|grep -v grep|grep -c ffmpeg` -eq 0 ];then')
    CMDs.append(r' rm -f /tmp/ffmpeg-*')
    CMDs.append(r' rm -f /tmp/streamlinkpipe-*')
    CMDs.append(r'fi')
    CMDs.append(r'if [ -e /var/run/processPID.pid ];then pid=`cat /var/run/processPID.pid`;[ -e /proc/$pid ] && kill $pid || rm -f /var/run/processPID.pid;fi')
    CMDs.append(r'[ -e /tmp/stream.ts ] && rm -f /tmp/stream.ts')
    CMDs.append(r"find /tmp/ -maxdepth 1 -mmin +180 -name 'streamlinkpipe-*' -exec rm -- '{}' \;")
    os.system('\n'.join(CMDs))

def GetSRVmode():
    return getE2config('SRVmode', 'serviceapp')

def GetDRMmode():
    return getE2config('type', 'serviceapp')

def GetBufferPath():
    return getE2config('bufferPath', '/tmp')

def GetuseCLI():
    return getE2config('useCLI', 'n')

def GetPortNumber():
    return getE2config('PortNumber', 8088) # change it to 88 for livestreamersrv compatibility

def GetLogLevel():
    return getE2config('logLevel', "info") # "critical", "error", "warning", "info", "debug", "trace" or "none"
#logging module Levels Numeric value
#           CRITICAL        50
#           ERROR           40
#           WARNING         30
#           INFO            20
#           DEBUG           10
#           NOTSET          0

def LogToFile():
    retVal = getE2config('logToFile', False)
    if retVal == False or getE2config('ClearLogFile', True) == True:
            for logPath in ('/home/root','/tmp','/hdd'):
                if os.path.exists(logPath + '/streamlinkSRV.log'):
                    os.system('rm -f /%s/streamlinkSRV.log' % logPath)
    return retVal
    
def GetLogFileName():
    return getE2config('logPath', '/tmp') + '/streamlinkSRV.log'


def decodeHTML(text):
    text = text.replace('%lf', '. ').replace('&#243;', 'ó')
    text = text.replace('&#176;', '°').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&apos;', "'").replace('&#65282;', '"').replace('&#xFF02;', '"')
    text = text.replace('&#228;', 'ä').replace('&#196;', 'Ă').replace('&#246;', 'ö').replace('&#214;', 'Ö').replace('&#252;', 'ü').replace('&#220;', 'Ü').replace('&#223;', 'ß')
    return text

def downloadWebPage(webURL, doUnquote = False , HEADERS={}):
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
        resp = requests.get(webURL, headers=HEADERS, timeout=5)
        webContent = resp.content
        webHeader = resp.headers
        if doUnquote == True:
            webContent =  urllib_unquote(webContent)
            webContent = decodeHTML(webContent)
    except Exception as e:
        print("EXCEPTION '%s' in downloadWebPage() for %s" % (str(e), webURL) )
        webContent = ''

    return webContent

def remoteE2( url = '' ):
    global remoteE2standbyCMD
    if url.startswith('remoteE2/'):
        remoteE2standbyCMD = None
        retURL = ''
        remoteE2address  = getE2config('remoteE2address' , '192.168.1.8')
        remoteE2port     = getE2config('remoteE2port'    , '8001')
        remoteE2username = getE2config('remoteE2username', 'root')
        remoteE2password = getE2config('remoteE2password', 'root')
        remoteE2zap      = getE2config('remoteE2zap'     , True)
        remoteE2wakeup   = getE2config('remoteE2wakeup' , True)
        base64string = base64.b64encode('%s:%s' % (remoteE2username, remoteE2password))
        if remoteE2wakeup == True:
            #sprawdzenie stanu e2
            try:
                request = urllib2.Request('http://%s/web/powerstate'% remoteE2address)
                LOGGER.debug("request : {}", str(request))
                request.add_header("Authorization", "Basic %s" % base64string)   
                response = urllib2.urlopen(request).read()
                LOGGER.debug("response : {}", str(response))
            except Exception as e:
                LOGGER.error("Exception : {}", str(e))
                return '/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/streams/offline.mp4'
            #pobudka e2
            if '<e2instandby>' in str(response) and 'true' in str(response):
                try:
                    request = urllib2.Request('http://%s/web/powerstate?newstate=4'% remoteE2address)
                    LOGGER.info("request wakeup: {}", str(request))
                    request.add_header("Authorization", "Basic %s" % base64string)   
                    response = urllib2.urlopen(request).read()
                    LOGGER.debug("response : {}", str(response))
                    #prepare standby script
                    remoteE2standbyCMD = urllib2.Request('http://%s/web/powerstate?newstate=5'% remoteE2address)
                    remoteE2standbyCMD.add_header("Authorization", "Basic %s" % base64string)
                    LOGGER.debug("response : {}", str(response))
                except Exception as e:
                    LOGGER.error("Exception : {}", str(e))
                    return '/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/streams/offline.mp4'
            else:
                LOGGER.info("tuner running: {}")
        #generate URL e.g. http://192.168.1.8:8001/1:0:1:3DD0:640:13E:820000:0:0:0
        url = url[9:].replace('-',':')
        if remoteE2zap == True:
            try:
                request = urllib2.Request('http://%s/web/zap?sRef=%s'% (remoteE2address, url))
                LOGGER.info("request zap to: {}", str(request))
                request.add_header("Authorization", "Basic %s" % base64string)   
                response = urllib2.urlopen(request).read()
                LOGGER.debug("response : {}", str(response))
            except Exception as e:
                LOGGER.error("Exception : {}", str(e))
                return '/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/streams/offline.mp4'
        time.sleep(1)
        return 'http://%s:%s/%s' % ( remoteE2address , remoteE2port , url )
    elif not remoteE2standbyCMD is None:
        LOGGER.info("request standby:")
        try:
            response = urllib2.urlopen(remoteE2standbyCMD).read()
            LOGGER.debug("response : {}", str(response))
        except Exception as e:
            LOGGER.error("Exception : {}", str(e))
    else:
        LOGGER.info("Unknown option or something wrong (url = '%s', remoteE2standbyCMD = '%s'" % (url , str(remoteE2standbyCMD)))
    return
