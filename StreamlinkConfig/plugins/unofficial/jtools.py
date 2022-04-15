#!/usr/bin/python
# j00zek 2020-2022

import os
os.environ["XDG_CONFIG_HOME"] = "/etc" #aby config streamlinka dzialal

def clearCache(): #zawsze dobrze oczyscic przed uruchomieniem os.system aby nie bylo GS-a
    with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")

def killSRVprocess(KeepPID):
    CMDs = []
    CMDs.append("[ `ps -ef|grep -v grep|grep -c ffmpeg` -gt 0 ] && (ps -ef|grep -v grep|grep ffmpeg|awk '{print $2}'|xargs kill)")
    #ubicie streamlinksrv ale tylko starego
    CMDs.append("if [ `ps -ef|grep -v grep|grep -v %s|grep -c streamlinksrv` -gt 0 ];then" % KeepPID)
    CMDs.append("     (ps -ef|grep -v grep|grep -v %s|grep streamlinksrv|awk '{print $2}'|xargs kill)" % KeepPID)
    CMDs.append('fi')
    os.system('\n'.join(CMDs))

def cleanCMD(forceKill = True): #czyszczenie smieci
    clearCache()
    CMDs = []
    if forceKill == True:
        CMDs.append("[ `ps -ef|grep -v grep|grep -c ffmpeg` -gt 0 ] && (ps -ef|grep -v grep|grep ffmpeg|awk '{print $2}'|xargs kill)")
    CMDs.append('if [ `ps -ef|grep -v grep|grep -c ffmpeg` -eq 0 ];then')
    CMDs.append(' rm -f /tmp/ffmpeg-*')
    CMDs.append(' rm -f /tmp/streamlinkpipe-*')
    CMDs.append('fi')
    CMDs.append('killall hlsdl 2>/dev/null')
    CMDs.append('[ -e /tmp/stream.ts ] && rm -f /tmp/stream.ts')
    CMDs.append("find /tmp/ -maxdepth 1 -mmin +180 -name 'streamlinkpipe-*' -exec rm -- '{}' \;")
    os.system('\n'.join(CMDs))

#config stored in E2 settings file
import urllib2, base64 #for remoteE2
import time
    
from streamlink.e2config import getE2config

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
                if os.path.exists(logPath + '/streamlinksrv.log'):
                    os.system('rm -f /%s/streamlinksrv.log' % logPath)
    return retVal
    
def GetLogFileName():
    return getE2config('logPath', '/tmp') + '/streamlinksrv.log'
    
remoteE2standbyCMD = None

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
