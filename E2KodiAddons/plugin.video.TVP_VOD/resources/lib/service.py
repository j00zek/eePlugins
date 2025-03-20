# -*- coding: utf-8 -*-

from xbmc import Monitor, Player, getInfoLabel
from serverHTTP import Proxy
from emukodi import xbmc
import time, datetime
import random
import json
from emukodi import xbmcaddon
import requests
from urllib.parse import urlencode, quote_plus, quote, unquote, parse_qsl
from .base import b

base=b()
addon = base.addon
baseurl=base.baseurl
platform=base.platform#'SMART_TV'#ANDROID
apiVOD=base.apiVOD
hea=base.hea


class BackgroundService(Monitor):
    """ Background service code """

    def __init__(self):
        Monitor.__init__(self)
        self._player = PlayerMonitor()
        self._proxy_thread = None

    def run(self):
        """ Background loop for maintenance tasks """
        addon.setSetting('proxyport', None)
        self._proxy_thread = Proxy.start()
        
        while not self.abortRequested():

            # Stop when abort requested
            if self.waitForAbort(10):
                break
        
        # Wait for the proxy thread to stop
        if self._proxy_thread and self._proxy_thread.is_alive():
            Proxy.stop()
        
class PlayerMonitor(Player):
    """ A custom Player object to check subtitles """
    
    def __init__(self):
        """ Initialises a custom Player object """
        self.__listen = False

        self.__path = None
        self.__timeplay =0
        self.__totalTime=0
        Player.__init__(self)
        
    def markWatchStatus():
        pass
        
    def onPlayBackStarted(self):  
        """ Will be called when Kodi player starts """
        self.__path = getInfoLabel('Player.FilenameAndPath')
        
        if not self.__path.startswith('plugin://plugin.video.TVP_VOD/?mode=playVid'):
            self.__listen = False
            return
        #xbmc.log('start odtwarzania', level=xbmc.LOGINFO)    
        self.__listen = True
                
        while self.__listen and self.isPlaying():
            if self.isPlaying():
                self.__timeplay=self.getTime()
                self.__totalTime=self.getTotalTime()
            time.sleep(2)
        
    def onPlayBackEnded(self):  
        """ Will be called when [Kodi] stops playing a file """
        if not self.__listen:
            return
        xbmc.log('koniec odtwarzaniax', level=xbmc.LOGINFO)
        #xbmc.log(self.__path, level=xbmc.LOGINFO)
        if addon.getSetting('logged')=='true' and addon.getSetting('synchKontOgl')=='true':
            hea=base.heaGen()
            eid=dict(parse_qsl(self.__path.split('?')[-1]))['eid']
            
            #usunięcie z kontynuuj
            url=apiVOD+'subscribers/bookmarks?type=WATCHED&itemId[]='+eid+'&lang=pl&platform='+platform
            resp=requests.delete(url,headers=hea)
            if resp.status_code==204:
                xbmc.log('@@@Usunięto z kontynuuj', level=xbmc.LOGINFO)
            
            #dodanie następnego odcinka sezonu (jeśli jest) do kontynnuj
            url=apiVOD+'products/vods/'+eid+'?lang=pl&platform='+platform
            resp=requests.get(url,headers=hea).json()
            if resp['type_']=='EPISODE':
                sezonID=str(resp['season']['id'])
                serialID=str(resp['season']['serial']['id'])
                sortType=resp['season']['serial']['sortType']
                url_seas=apiVOD+'products/vods/serials/'+serialID+'/seasons/'+sezonID+'/episodes?lang=pl&platform='+platform
                resp_seas=requests.get(url_seas,headers=hea).json()
                for i,e in enumerate(resp_seas):
                    if e['id']==int(eid):
                        try:
                            ii=i-1 if sortType=='DESC' else i+1
                            if ii>=0:
                                new_eid=resp_seas[ii]['id']
                                if resp_seas[ii]['displaySchedules'][0]['type']!='SOON':
                                    url_new=apiVOD+'subscribers/bookmarks?type=WATCHED&lang=pl&platform='+platform
                                    data={
                                        "itemId": new_eid,
                                        "playTime": 1
                                    }
                                    resp_new=requests.post(url_new,headers=hea,json=data)
                                    if resp_new.status_code==204:
                                        xbmc.log('@@@Przesłano nowy odcinek na serwer', level=xbmc.LOGINFO)
                        except:
                            pass
            #status
            if 'playVid' in self.__path and 'TVP_VOD' in self.__path:
                pathFile='plugin://plugin.video.TVP_VOD/?mode=playVid&eid='+eid
                totalTime=int(self.__totalTime)
                now=int(time.time())
                lastplayed=datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H:%M:%S')
                request={
                        "jsonrpc": "2.0", 
                        "method": "Files.SetFileDetails", 
                        "params": {
                            "file": pathFile, 
                            "media": "video", 
                            "playcount": 1,
                            "lastplayed":lastplayed,
                            "resume": {
                                "position":0, 
                                "total": 0
                            }
                        },
                        "id":"1"
                }
                results = json.loads(xbmc.executeJSONRPC(json.dumps(request)))
                #print(results)
                
                xbmc.executebuiltin('Container.Refresh()')
                
            req={"jsonrpc": "2.0", "params": {"media": "video","file": pathFile, "properties": ["resume","playcount"]}, "method": "Files.GetFileDetails", "id": "1"}
            results = json.loads(xbmc.executeJSONRPC(json.dumps(req)))
            #print(results)
            
              
            
    def onPlayBackStopped(self):  
        """ Will be called when [user] stops Kodi playing a file """
        if not self.__listen:
            return
        xbmc.log('@@@Odtwarzanie przerwane - STOP', level=xbmc.LOGINFO)
        #xbmc.log(self.__path, level=xbmc.LOGINFO)
        #xbmc.log(str(self.__timeplay), level=xbmc.LOGINFO)
        #xbmc.log(str(self.__totalTime), level=xbmc.LOGINFO)
        if addon.getSetting('logged')=='true' and addon.getSetting('synchKontOgl')=='true':
            hea=base.heaGen()
            eid=dict(parse_qsl(self.__path.split('?')[-1]))['eid']
            timePlay=int(self.__timeplay)
            totalTime=int(self.__totalTime)
            url=apiVOD+'subscribers/bookmarks?type=WATCHED&lang=pl&platform='+platform
            data={
                "itemId": int(eid),
                "playTime": timePlay
            }
            resp=requests.post(url,headers=hea,json=data)
            if resp.status_code==204:
                xbmc.log('@@@Przesłano playTime na serwer', level=xbmc.LOGINFO)
            
            #status
            pathFile='plugin://plugin.video.TVP_VOD/?mode=playVid&eid='+eid
            if totalTime>0 and 'playVid' in self.__path and 'TVP_VOD' in self.__path:
                request={
                    "jsonrpc": "2.0", 
                    "method": "Files.SetFileDetails", 
                    "params": {
                        "file": pathFile, 
                        "media": "video", 
                        "resume": {
                            "position":timePlay, 
                            "total": totalTime
                        }
                    },
                    "id":"1"
                }
                results = json.loads(xbmc.executeJSONRPC(json.dumps(request)))
                
                xbmc.executebuiltin('Container.Refresh()') 
            
            req={"jsonrpc": "2.0", "params": {"media": "video","file": pathFile, "properties": ["resume","playcount"]}, "method": "Files.GetFileDetails", "id": "1"}
            results = json.loads(xbmc.executeJSONRPC(json.dumps(req)))
            #print(results)
                
def run():
    """ Run the BackgroundService """
    BackgroundService().run()
