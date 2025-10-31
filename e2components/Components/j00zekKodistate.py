#!/usr/bin/python
#######################################################################
#
#    remote KODI status check script
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
# KODI JSON commands see https://kodi.wiki/view/JSON-RPC_API/v6#List.Fields.All
#
#######################################################################
from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3

#CONSTANTS, default local Kodi with web enabled under default port
KODI_IP = '127.0.0.1'
KODI_PORT = '8080'

AppProperties    = b'{"jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["version", "name"]}, "id": 1 }'
XBMCInfoBool     = b'{"jsonrpc": "2.0", "method": "XBMC.GetInfoBooleans", "params": { "booleans": ["System.ScreenSaverActive ","System.IdleTime(600) "] }, "id": 1}'
GetActivePlayers = b'{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}'
AudioPlayerItem = b'{"jsonrpc": "2.0", "method": "Player.GetItem", "params": {"properties": ["title", "album", "artist", "duration", "thumbnail", "file", "fanart", "streamdetails"], "playerid": 0 }, "id": 0}'
VideoPlayerItem = b'{"jsonrpc": "2.0", "method": "Player.GetItem", "params": {"properties": ["title","album","artist","season","episode","duration","showtitle","tvshowid","thumbnail","file","fanart","streamdetails"],"playerid":1 }, "id": 1}'
VideoPlayerProperties  = b'{"jsonrpc": "2.0", "method": "Player.GetProperties","params":{"playerid":1,"properties":["audiostreams","currentaudiostream","currentsubtitle","currentvideostream","percentage","subtitleenabled","subtitles","videostreams","time","totaltime"]},"id": 1}' 
AudioPlayerProperties  = b'{"jsonrpc": "2.0", "method": "Player.GetProperties","params":{"playerid":0,"properties":["audiostreams","currentaudiostream","currentsubtitle","currentvideostream","percentage","subtitleenabled","subtitles","videostreams"]},"id": 0}' 
GUIProperties    = b'{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["currentwindow", "currentcontrol"]},"id":1}'

import json
try: #py2
    from urllib2 import Request as urllib2_Request, urlopen as urllib2_urlopen
except Exception: #py3
    from urllib.request import Request as urllib2_Request, urlopen as urllib2_urlopen
  
DBG = False

class remoteKODI():
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def getState(self, data):
        url = 'http://%s:%s/jsonrpc' % (self.host, self.port)
        headers = {"Content-Type":"application/json",}
        req = urllib2_Request(url, data, headers)

        try:
            response = urllib2_urlopen(req, timeout=0.3)
            response = response.read()
            response = json.loads(response)
            print(response)
            if 'result' in response and isinstance(response['result'],dict):
                response['result']['isError'] = False
                response['result']['ErrorDescr'] = 'OK-dict' 
            elif 'result' in response and isinstance(response['result'],list):
                if len(response['result']) > 0:
                    response['result'] = response['result'][0]
                    response['result']['isError'] = False
                    response['result']['ErrorDescr'] = 'OK-list[0]'
                else:
                    response = {'result': {'isError': False, 'ErrorDescr': 'OK-empty list'} }
            else:
                response = {'result': {'isError': True, 'ErrorDescr': 'no or empty dict result'} }

        except Exception as e:
            response = {'result': {'isError': True, 'ErrorDescr': str(e).lower()} }
       
        return response['result']

#for tests outside e2 only do NOT use
if __name__ == '__main__':
    kodi = remoteKODI('127.0.0.1', '8080')
    #print(kodi.getState(GetActivePlayers))
    #print(kodi.getState(VideoPlayerItem))
    #print(kodi.getState(VideoPlayerProperties))
    print(kodi.getState(GUIProperties))