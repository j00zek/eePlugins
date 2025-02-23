# -*- coding: utf-8 -*-
import os
import sys

import requests
from emukodi import xbmc
from emukodi import xbmcgui
from emukodi import xbmcplugin
from emukodi import xbmcaddon
from emukodi import xbmcvfs
import re
import json
from html import unescape
from urllib.parse import urlencode, quote_plus, quote, unquote, parse_qsl

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon(id='plugin.video.interia_tv')
PATH=addon.getAddonInfo('path')
img_empty=PATH+'/resources/img/empty.png'
fanart=PATH+'/resources/img/fanart.jpg'
PATH_profile=xbmcvfs.translatePath(addon.getAddonInfo('profile'))
if not xbmcvfs.exists(PATH_profile):
    xbmcvfs.mkdir(PATH_profile)

baseurl='https://www.interia.tv/'
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'

hea={
    'User-Agent':UA,
}

def build_url(query):
    return base_url + '?' + urlencode(query)

def addItemList(url, name, setArt, medType=False, infoLab={}, isF=True, isPla='false', contMenu=False, cmItems=[]):
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
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=isF)

def main_menu():
    resp=requests.get(baseurl[:-1],headers=hea).text
    resp1=resp.split('\"nav-wrapper\"')[1].split('</nav>')[0].split('</a>')
    menu_main=[]
    menu_sub=[]
    
    def testMenu(x):
        result=False
        for m in menu_main:
            if m[1] in x:
                result=True
        return result
             
    for r in resp1:
        if 'href=' in r:
            link=re.compile('href=\"([^\"]+?)\"').findall(r)[0]
            name=re.compile('span>([^<]+?)</span').findall(r)[0]
            if link!='/':
                if not testMenu(link):
                    menu_main.append([name,link])
                else:
                    menu_sub.append([name,link])
    
    addon.setSetting('menu_sub',str(menu_sub))
    for m in menu_main:
        testSub=False
        for ms in menu_sub:
            if m[1] in ms[1]:
                testSub=True
        MODE='menu_sub' if testSub else 'contList'
        
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': 'DefaultAddonVideo.png', 'fanart':fanart}
        url = build_url({'mode':MODE,'link':m[1]})
        addItemList(url, m[0], setArt, 'video')

    xbmcplugin.endOfDirectory(addon_handle)
    
def menu_sub(l):
    menu_sub=eval(addon.getSetting('menu_sub'))
    menu_sub.append(['Wszystkie',l])
    for m in menu_sub:
        if l in m[1]:
            setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': 'DefaultAddonVideo.png', 'fanart':fanart}
            url = build_url({'mode':'contList','link':m[1]})
            addItemList(url, m[0], setArt, 'video')

    xbmcplugin.endOfDirectory(addon_handle)
    
def contList(l):
    url=baseurl[:-1]+l
    resp=requests.get(url,headers=hea).text
    resp1=resp.split('<ul class=\"brief-list-items\">')[1].split('</ul>')[0].split('</li>')
    for r in resp1:
        if 'brief-title-link' in r:
            link=re.compile('href=\"([^\"]+?)\"').findall(r)[0]
            img,title=re.compile('<img.*src=\"([^\"]+?)\".*alt=\"([^\"]+?)\"').findall(r)[0]
            count=re.compile('stat count\">([^<]+?)<').findall(r)
            if len(count)>0:
                count=count[0]
                plot=count
                MODE='epList'
                isPlayable='false'
                isFolder=True
            else:
                count=None
                plot=unescape(title)
                MODE='playVid'
                isPlayable='true'
                isFolder=False
            img=img.split('-C')[0]+'-C303.jpg'
            
            iL={'plot':plot}
            setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart':fanart}
            url = build_url({'mode':MODE,'link':link})
            addItemList(url, unescape(title), setArt, 'video', iL, isFolder, isPlayable)
    
    resp2=resp.split('<div class=\"pagination\">')[1].split('</div>')[0]
    if 'class=\"next\"' in resp2:
        nextURL=re.compile('next\"><a href=\"([^\"]+?)\"').findall(resp2)[0]
        
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_empty, 'fanart':fanart}
        url = build_url({'mode':'contList','link':nextURL})
        addItemList(url, '[B][COLOR=yellow]>>> następna strona[/COLOR][/B]', setArt, 'video')
    
    xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)

def epList(l):
    url=baseurl[:-1]+l
    resp=requests.get(url,headers=hea).text
    try:
        resp1=resp.split('<section class=\"album-navigator\">')[1].split('</section>')[0].split('</li>')
        lastvID=''
        cnt=0
        for r in resp1:
            if 'brief-play' in r:
                link=re.compile('href=\"([^\"]+?)\"').findall(r)[0]
                img,title=re.compile('<img.*src=\"([^\"]+?)\".*alt=\"([^\"]+?)\"').findall(r)[0]
                desc=re.compile('album-video-desc\">([^<]+?)<').findall(r)[0]
                lastvID=re.compile('vId,([^,]+?),').findall(r)[0]
                #items.append([unescape(title),link,img,desc])
                img=img.split('-C')[0]+'-C303.jpg'
                cnt+=1
                
                iL={'plot':unescape(desc)}
                setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart':fanart}
                url = build_url({'mode':'playVid','link':link})
                addItemList(url, unescape(title), setArt, 'video', iL, False, 'true')
                
        if lastvID!='' and cnt==20:
            url=baseurl+'getRecomendations2?id='+lastvID+'&output=jsonp&el=itv-player&nsp=ATTACHMENTS&isEmbed=0'
            resp=requests.get(url,headers=hea).text
            if '\"url\"' in resp:
                nextURL=re.compile('\"url\":\"([^\"]+?)\"').findall(resp)[0].replace('\\','').replace('//www.interia.tv','')
                
                setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_empty, 'fanart':fanart}
                url = build_url({'mode':'epList','link':nextURL})
                addItemList(url, '[B][COLOR=yellow]>>> następna strona[/COLOR][/B]', setArt, 'video')
    
    except:
        resp2=resp.split('<section class=\"video-single\"')[1].split('</section>')[0]
        link=re.compile('url\" href=\"([^\"]+?)\"').findall(resp2)[0].replace(baseurl[:-1],'')
        title=re.compile('name\" content=\"([^\"]+?)\"').findall(resp2)[0]
        desc=re.compile('description\" content=\"([^\"]+?)\"').findall(resp2)[0]
        img=re.compile('thumbnailUrl\" href=\"([^\"]+?)\"').findall(resp2)[0]
        
        iL={'plot':unescape(desc)}
        setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart':fanart}
        url = build_url({'mode':'playVid','link':link})
        addItemList(url, unescape(title), setArt, 'video', iL, False, 'true')
        
    xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)

def playVid(l):
    stream_url=''
    stream_type=''
    url=baseurl[:-1]+l
    resp=requests.get(url,headers=hea).text
    link=re.compile('embedURL\" href=\"([^\"]+?)\"').findall(resp)[0] #uwaga pełny URL !!!
    hea.update({'referer':url})
    resp_emb=requests.get(link,headers=hea).text
    sources=re.compile('src\":(.*),\"data\"').findall(resp_emb)[0]
    sourcesJSON=json.loads(sources)
    qualities=list(sourcesJSON.keys())
    select = xbmcgui.Dialog().select('Źródła', qualities)
    if len(qualities)>0:
        if select > -1:
            stream_url=sourcesJSON[qualities[select]][0]['src']
            stream_type=sourcesJSON[qualities[select]][0]['type']
        else:
            stream_url=sourcesJSON[qualities[0]][0]['src']
            stream_type=sourcesJSON[qualities[0]][0]['type']
    
    print(stream_url)
    print(stream_type)
    if stream_url!='':
        stream_url+='|User-Agent='+UA+'&Referer='+baseurl
        play_item = xbmcgui.ListItem(path=stream_url)
        play_item.setProperty("IsPlayable", "true")
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
    else:
        xbmcgui.Dialog().notification('Interia.tv', 'Brak źródła', xbmcgui.NOTIFICATION_INFO)
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())

    
mode = params.get('mode', None)

if not mode:
    main_menu()
else:
    if mode=='menu_sub':
        link=params.get('link')
        menu_sub(link)
    
    if mode=='contList':
        link=params.get('link')
        contList(link)
        
    if mode=='epList':
        link=params.get('link')
        epList(link)
        
    if mode=='playVid':
        link=params.get('link')
        playVid(link)
