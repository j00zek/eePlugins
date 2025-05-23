# -*- coding: utf-8 -*-
#import os
#import sys

from emukodi import xbmc
from emukodi import xbmcgui#
from emukodi import xbmcplugin#
from emukodi import xbmcaddon
from emukodi import xbmcvfs

from urllib.parse import urlencode, quote_plus, quote, unquote, parse_qsl
import random
import json

class b:
    def __init__(self, base_url=None, addon_handle=None):
        self.base_url=base_url
        self.addon_handle=addon_handle
        self.UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
        self.baseurl='https://apps.vod.tvp.pl/'
        self.hea={
            'User-Agent':self.UA,
            'Referer':self.baseurl,
            'X-Redge-VOD':'true',
            'API-DeviceInfo':'HbbTV;2.0.1 (ETSI 1.4.1);Chrome +DRM Samsung;Chrome +DRM Samsung;HbbTV;2.0.3'
        }
        self.apiVOD='https://vod.tvp.pl/api/'
        self.platform='SMART_TV'#ANDROID
        
        self.addon=xbmcaddon.Addon(id='plugin.video.TVP_VOD')
        self.PATH_profile=xbmcvfs.translatePath(self.addon.getAddonInfo('profile'))
        if not xbmcvfs.exists(self.PATH_profile):
            xbmcvfs.mkdir(self.PATH_profile)
            
    def build_url(self, query):
        return self.base_url + '?' + urlencode(query)

    def addItemList(self, url, name, setArt, medType=False, infoLab={}, isF=True, isPla='false', contMenu=False, cmItems=[]):
        li=xbmcgui.ListItem(name)
        li.setProperty("IsPlayable", isPla)
        if medType:
            kodiVer=xbmc.getInfoLabel('System.BuildVersion')
            if kodiVer.startswith('19.'):
                li.setInfo(type=medType, infoLabels=infoLab)
            else:
                types={'video':'getVideoInfoTag','music':'getMusicInfoTag'}
                if medType!=False:
                    setMedType=getattr(li,types[medType])
                    vi=setMedType()
                
                    labels={
                        'year':'setYear', #int
                        'episode':'setEpisode', #int
                        'season':'setSeason', #int
                        'rating':'setRating', #float
                        'mpaa':'setMpaa',
                        'plot':'setPlot',
                        'plotoutline':'setPlotOutline',
                        'title':'setTitle',
                        'originaltitle':'setOriginalTitle',
                        'sorttitle':'setSortTitle',
                        'genre':'setGenres', #list
                        'country':'setCountries', #list
                        'director':'setDirectors', #list
                        'studio':'setStudios', #list
                        'writer':'setWriters',#list
                        'duration':'setDuration', #int (in sec)
                        'tag':'setTags', #list
                        'trailer':'setTrailer', #str (path)
                        'mediatype':'setMediaType',
                        'cast':'setCast', #list        
                    }
                    
                    if 'cast' in infoLab:
                        if infoLab['cast']!=None:
                            cast=[xbmc.Actor(c) for c in infoLab['cast']]
                            infoLab['cast']=cast
                            
                    for i in list(infoLab):
                        if i in list(labels):
                            setLab=getattr(vi,labels[i])
                            setLab(infoLab[i])
        li.setArt(setArt) 
        if contMenu:
            li.addContextMenuItems(cmItems, replaceItems=False)
        xbmcplugin.addDirectoryItem(handle=self.addon_handle, url=url, listitem=li, isFolder=isF)
        
    def code_gen(self,x):
        base='0123456789abcdef'
        code=''
        for i in range(0,x):
            code+=base[random.randint(0,15)]
        return code
        
    def heaGen(self):
        CorrelationID='smarttv_'+self.code_gen(32)
        hea=self.hea
        hea.update({'API-CorrelationID':CorrelationID,'API-DeviceUid':self.addon.getSetting('DeviceUid')})
        if self.addon.getSetting('logged')=='true':
            hea.update({'API-Authentication':self.addon.getSetting('API_Authentication'),'API-ProfileUid':self.addon.getSetting('API_ProfileUid')})
        return hea
        
    def directPlayer(self,stream_url):
        stream_url+='|User-Agent='+self.UA
        play_item = xbmcgui.ListItem(path=stream_url)
        xbmcplugin.setResolvedUrl(self.addon_handle, True, listitem=play_item)
        
    def ISffmpegPlayer(self,protocol,stream_url):
        mimeTypes={'hls':'application/x-mpegURL','mpd':'application/xml+dash'}
        stream_url+='|User-Agent='+self.UA
        
        play_item = xbmcgui.ListItem(path=stream_url) 
        play_item.setMimeType(mimeTypes[protocol])
        play_item.setProperty('inputstream', 'inputstream.ffmpegdirect')
        play_item.setProperty('inputstream.ffmpegdirect.is_realtime_stream', 'true')
        if self.addon.getSetting('ffmpegTimeshift')=='true':
            play_item.setProperty('inputstream.ffmpegdirect.stream_mode', 'timeshift')
        play_item.setProperty('inputstream.ffmpegdirect.manifest_type', protocol)
        
        xbmcplugin.setResolvedUrl(self.addon_handle, True, listitem=play_item)
        
    def openJSON(self,u):
        try:
            f=open(u,'r',encoding = 'utf-8')
        except:
            f=open(u,'w+',encoding = 'utf-8')
        cont=f.read()
        f.close()
        try:
            js=eval(cont)
        except:
            js=[]
        return js
        
    def saveJSON(self,u,j):
        with open(u, 'w', encoding='utf-8') as f:
            json.dump(j, f, ensure_ascii=False, indent=4)
