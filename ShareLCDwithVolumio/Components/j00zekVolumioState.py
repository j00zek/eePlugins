#!/usr/bin/python
# -*- coding: utf-8 -*- 
#######################################################################
#
#    Volumio status check script
#    Coded by j00zek (c)2021
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

import json
import urllib, urllib2
import requests
import os

DBG = True
DebugFile='/tmp/j00zekVolumioState.log'

def saveToLog(textString):
    import io
    with io.open(DebugFile, 'a', encoding='utf8') as outfile:
        outfile.write(unicode(textString))
        outfile.close()

def decodeHTML(text):
    text = text.replace('&#243;','ó')
    text = text.replace('&#176;','°').replace("&lt;", "<").replace("&gt;", ">").replace("&quot;",'"')
    text = text.replace('&#228;','ä').replace('&#196;','Ă').replace('&#246;','ö').replace('&#214;','Ö').replace('&#252;','ü').replace('&#220;','Ü').replace('&#223;','ß')
    #text = text.replace('\xc5\x9a','Ś')
    return text

Gurl = None
GstateDict = {}
#if DBG: GstateDict = {u'consume': True, u'stream': False, u'mute': False, u'random': None, u'channels': 2, u'duration': 148, u'samplerate': 44.100000000000001, u'seek': 5507, u'disableVolumeControl': False, u'album': u'A Night At The Odeon', u'bitdepth': u'32 bit', u'service': u'tidal', u'title': u'Bohemian Rhapsody', u'trackType': u'tidal', u'albumart': u'https://resources.tidal.com/images/d6638177/6251/46f7/9845/0e9bf6d0190b/640x640.jpg', u'volatile': False, u'status': u'play', u'repeat': None, u'volume': 34, u'repeatSingle': False, u'bitrate': u'320 Kbps', u'updatedb': False, u'artist': u'Queen', u'uri': u'tidal://song/53735515', u'position': 3}

class getJSON():
    
    def __init__(self):
        return

    def deleteAlbumart(self, filename):
        if os.path.exists(filename): os.remove(filename)
        
    def getState(self):
        return GstateDict
        
    def refreshState(self, host, port, getCover):
        global Gurl, GstateDict, GalbumartFile
        currAlbumartFile = GstateDict.get('albumpic', '')
        if os.path.exists(DebugFile): os.remove(DebugFile)
        
        if Gurl is None:
            if port == '80':
                Gurl = 'http://%s' % host
            else:
                Gurl = 'http://%s:%s' % (host, port)
            
        try:
            HEADERS={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:54.0) Gecko/20100101 Firefox/54.0', 
                         'Accept-Charset': 'utf-8',
                         'Content-Type': 'text/html; charset=utf-8'
                        }
            resp = requests.get(Gurl + '/api/v1/getState', headers=HEADERS, timeout=1)
            webContent = resp.content
            webContent = urllib.unquote(webContent)
            webContent = decodeHTML(webContent)
            if DBG: saveToLog('##### webContent #####\n%s\n######################\n' % webContent)
            tempDict = json.loads(webContent)
            GstateDict = tempDict.copy()
        except Exception as e:
            GstateDict['service'] = 'ERROR DOWNLOADING'
            GstateDict[u'status'] = 'ERROR'
            import random
            if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/ShareLCDwithVolumio/_offline_4_test.json'):
                try:
                    with open('/usr/lib/enigma2/python/Plugins/Extensions/ShareLCDwithVolumio/_offline_4_test.json', 'r') as json_file:
                        data = json_file.read().decode('utf-8')
                        json_file.close()
                        GstateDict = json.loads(data)    
                except Exception as ee:
                    saveToLog('##### json.loads Exception #####\n%s\n######################\n' % str(ee))
            GstateDict['EXCEPTIONINFO'] = 'For %s EXCEPTION:\n%s' % (Gurl + '/api/v1/getState', str(e))
            GstateDict['duration'] = 148
            GstateDict['seek'] = random.randint(1000, 140 * 1000)
            saveToLog('##### webContent Exception #####\n%s\n######################\n' % str(e))
            
        if DBG: saveToLog('##### JSON #####\n%s\n######################\n' % json.dumps(GstateDict, indent=4, sort_keys=True, ensure_ascii=False))
       
        if getCover:
            try:
                albumartURL = GstateDict.get('albumart', '')
                if albumartURL.startswith('/albumart?'):
                    albumartURL = Gurl + albumartURL
                if albumartURL != '' and albumartURL[:4] == 'http':
                    albumartEXT = albumartURL[-4:]
                    if albumartEXT in ['.jpg','.png']:
                        albumartFile = GstateDict.get('album', '').encode('ascii','ignore').replace(' ','')
                        albumartFile = '/tmp/volumio-%s%s' % (albumartFile, albumartEXT)
                        GstateDict['albumpic'] = albumartFile
                        if not os.path.exists(albumartFile):
                            self.deleteAlbumart(currAlbumartFile)
                            resp = requests.get(albumartURL, headers=HEADERS, timeout=1)
                            webContent = resp.content
                            with open(albumartFile, "w") as f:
                                f.write(webContent)
                                f.close()
            except Exception as e:
                saveToLog('##### getCover Exception #####\n%s\n######################\n' % str(e))

#for tests outside e2 only do NOT use
if __name__ == '__main__': 
    myJSON = getJSON()
    myJSON.refreshState('192.168.178.101', '80', True)
    print myJSON.getState()
