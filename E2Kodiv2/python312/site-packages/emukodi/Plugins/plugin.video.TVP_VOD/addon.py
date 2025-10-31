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
import random
import math
import datetime
import time

from urllib.parse import urlencode, quote_plus, quote, unquote, parse_qsl
#from ttml2ssa import Ttml2SsaAddon

from resources.lib.base import b
from resources.lib.tvpExt import tvpExt
from resources.lib.tvp_go import tvpGo
from resources.lib.favExt import favExt

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
base=b(base_url,addon_handle)

params = dict(parse_qsl(sys.argv[2][1:]))
addon = base.addon
PATH=addon.getAddonInfo('path')
PATH_profile=base.PATH_profile
img_path=PATH+'/resources/images/'
img_empty=img_path+'empty.png'
fanart=img_path+'fanart.jpg'

baseurl=base.baseurl
platform=base.platform#'SMART_TV'#ANDROID

apiVOD=base.apiVOD#'https://vod.tvp.pl/api/'

mainCategs=[    
    ['Strona główna','','mainPage','tvp_vod.png','OverlayUnwatched.png'],
    ['Na żywo (TV)','','lives','tvp_vod.png','DefaultTVShows.png'],
    ['Archiwum TV [I](test)[/I]','','archive','tvp_vod.png','DefaultYear.png'],
    ['Seriale','18','categList','tvp_vod.png','DefaultAddonVideo.png'],
    ['Filmy','136','categList','tvp_vod.png','DefaultAddonVideo.png'],
    ['Programy','88','categList','tvp_vod.png','DefaultAddonVideo.png'],
    ['Dokumenty','163','categList','tvp_vod.png','DefaultAddonVideo.png'],
    ['Dla dzieci','24','categList','tvp_vod.png','DefaultAddonVideo.png'],
    ['Teatr','202','categList','tvp_vod.png','DefaultAddonVideo.png'],
    ['News','205','categList','tvp_vod.png','DefaultAddonVideo.png'],
    ['[B]Inne serwisy TVP[/B]','','others','tvp.png','DefaultAddonContextItem.png'],
    ['ULUBIONE: VOD','','favList','tvp_vod.png','DefaultMusicRecentlyAdded.png'],
    ['WYSZUKIWARKA','','search','tvp_vod.png','DefaultAddonsSearch.png']
]

othersMenu=[
    ['TVP GO+','','tvpgo','tvp_go.png','tvp_go.png'],
    ['Transmisje TVP SPORT','','tvp_sport','tvp_sport.png','tvp_sport.png'],
    ['Materiały video TVP SPORT','','tvp_sport_video','tvp_sport.png','tvp_sport.png'],
    ['TVP INFO','','tvp_info','tvp_info_2.png','tvp_info_2.png'],
    #['Programy TVP INFO','','tvp_info_progs','tvp_info.png',''],
    ['Programy TVP3 (Regiony)','','tvp3','tvp3.png','tvp3.png'],
    ['Rekonstrukcja cyfrowa','','rc','rc.png','rc.png'],
    ['ULUBIONE: inne serwisy TVP','','favExtList','tvp.png','DefaultMusicRecentlyAdded.png'],
]

hea=base.hea

tvp_ext=tvpExt(addon.getSetting('livePlayerType'),addon.getSetting('epCount'),addon.getSetting('streamTvProtocol'))###
tvp_go=tvpGo(addon.getSetting('livePlayerType'),addon.getSetting('streamTvProtocol'),addon.getSetting('cuOffset')) ###
fav_ext=favExt()

def openF(u):
    try:
        f=open(u,'r',encoding = 'utf-8')
    except:
        f=open(u,'w+',encoding = 'utf-8')
    cont=f.read()
    f.close()
    return cont
    
def saveF(u,t):
    with open(u, 'w', encoding='utf-8') as f:
        f.write(t)

def logIn():
    kod = addon.getSetting('LoginCode')
    if kod == '':
        kod=xbmcgui.Dialog().input(u'Najpierw wpisz kod ze strony [B]https://vod.tvp.pl/logowanie-tv[/B] do pola LoginCode', type=xbmcgui.INPUT_ALPHANUM)#from: vod.tvp.pl/logowanie-tv
        return
    elif kod == '-':
        kod=xbmcgui.Dialog().input(u'Najpierw wpisz poprawny kod ze strony [B]https://vod.tvp.pl/logowanie-tv[/B] do pola LoginCode', type=xbmcgui.INPUT_ALPHANUM)#from: vod.tvp.pl/logowanie-tv
        return
    if kod:
        url=apiVOD+'subscribers/sso/tvp/login?code='+kod+'&lang=pl&platform='+platform
        #hea.update({'API-CorrelationID':addon.getSetting('CorrelationID'),'API-DeviceUid':addon.getSetting('DeviceUid')})
        hea=base.heaGen()
        data={
            "auth": {
                "app": "tvp",
                "type": "SSO",
                "value": ""
            },
            "rememberMe": True
        }
        resp=requests.post(url,headers=hea,json=data).json()
        if 'token' not in resp:
            xbmcgui.Dialog().notification('TVP VOD', 'Nieudane logowanie', xbmcgui.NOTIFICATION_INFO)
            xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
            addon.setSetting('LoginCode', '-')
        else:
            addon.setSetting('API_Authentication',resp['token'])
            addon.setSetting('API_ProfileUid',resp['profiles'][0]['uid'])#logowanie na profil podstawowy (domyślnie)
            addon.setSetting('logged','true')
    else:
        xbmcgui.Dialog().notification('TVP VOD', 'Nie wpisano kodu', xbmcgui.NOTIFICATION_INFO)
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
        
        
def logOut():
    url=apiVOD+'subscribers/logout?lang=pl&platform='+platform
    hea=base.heaGen()
    resp=requests.post(url,headers=hea)
    addon.setSetting('API_Authentication','')
    addon.setSetting('API_ProfileUid','')
    addon.setSetting('logged','false')

def vodProfiles():
    hea=base.heaGen()
    url=apiVOD+'subscribers/detail?lang=pl&platform='+platform
    resp=requests.get(url,headers=hea).json()
    if 'code' in resp:
        if resp['code']=='AUTHENTICATION_REQUIRED':
            paraLogOut()
    else:
        for p in resp['profiles']:
            if p['uid']==addon.getSetting('API_ProfileUid'):
                profileName=p['name']+ '[COLOR=yellow] (zalogowany)[/COLOR]'
                isUsed='true'
            else:
                profileName=p['name']
                isUsed='false'
           
            iL={}
            setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_empty, 'fanart':fanart}
            url = base.build_url({'mode':'changeProfile','uid':p['uid'],'used':isUsed})
            base.addItemList(url, profileName, setArt, 'video', iL, False, 'false')
        xbmcplugin.endOfDirectory(addon_handle)
    
def changeProfile(uid,used):
    if used == 'false':
        addon.setSetting('API_ProfileUid',uid)
        xbmc.executebuiltin('Container.Refresh()')

def userInfo():
    info='[B]Status[/B]: Niezalogowany'
    if addon.getSetting('logged')=='true':
        hea=base.heaGen()
        url=apiVOD+'subscribers/detail?lang=pl&platform='+platform
        resp=requests.get(url,headers=hea).json()
        if 'code' in resp:
            if resp['code']=='AUTHENTICATION_REQUIRED':
                paraLogOut()
        else:
            info='[B]Status[/B]: zalogowany\n'
            info+='[B]Użytkownik[/B]: %s\n'%(resp['email'])
            packets='brak' if resp['status']['packetsNames']==None else ' | '.join(resp['status']['packetsNames'])
            info+='[B]Pakiety[/B]: %s\n'%(packets)
            if 'crossBorderValidTill' in resp:
                try:
                    tillDate=locTime(resp['crossBorderValidTill'])
                except:
                    tillDate=None
                if tillDate!=None:
                    info+='[B]Ważność subskrypcji[/B]: %s\n'%(tillDate)
                    
    dialog = xbmcgui.Dialog()
    dialog.textviewer('Dane konta', info)

def locTime(x): #nowy
    y=datetime.datetime(*(time.strptime(x,'%Y-%m-%dT%H:%M:%S%z')[0:6]))
    z=y.strftime('%Y-%m-%d %H:%M')
    return z
       
def main_menu():
    global mainCategs
    
    if addon.getSetting('othServ')=='true':
        mainCategs.pop(10)
        mainCategs=othersMenu+mainCategs
    
    if addon.getSetting('logged')=='true':
        mainCategs.append(['Moja lista','','myList','tvp_vod.png','DefaultMusicPlaylists.png'])
        mainCategs.append(['Profile','','vodProfiles','tvp_vod.png','DefaultUser.png'])
        mainCategs.append(['Wyloguj','','logOut','tvp_vod.png','DefaultUser.png'])
    else:
        mainCategs.append(['Zaloguj','','logIn','tvp_vod.png','DefaultUser.png'])
    for s in mainCategs:
        mode=s[2]
        
        setArt={'thumb': '', 'poster': img_path+s[3], 'banner': '', 'icon': s[4], 'fanart':fanart}
        url = base.build_url({'mode':mode,'mainCateg':s[1]})
        base.addItemList(url, s[0], setArt)
    xbmcplugin.endOfDirectory(addon_handle)

def others():
    for s in othersMenu:
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_path+s[3], 'fanart':fanart}
        url = base.build_url({'mode':s[2]})
        base.addItemList(url, s[0], setArt)
    xbmcplugin.endOfDirectory(addon_handle)

def mainPage():
    hea=base.heaGen()
    url=apiVOD+'products/sections/main?elementsLimit=100&lang=pl&platform='+platform
    resp=requests.get(url,headers=hea).json()
    for c in resp:
        if c['showTitle']==True:            
            setArt={'thumb': '', 'poster': img_path+'tvp_vod.png', 'banner': '', 'icon': 'OverlayUnwatched.png', 'fanart':fanart}
            url = base.build_url({'mode':'mainPageCateg','categID':str(c['id'])})
            base.addItemList(url, c['title'], setArt)
    xbmcplugin.endOfDirectory(addon_handle)
    
def mainPageCateg(mpc):
    hea=base.heaGen()
    url=apiVOD+'products/sections/main?elementsLimit=100&lang=pl&platform='+platform
    resp=requests.get(url,headers=hea).json()
    for r in resp:
        if r['id']==int(mpc):
            if r['title']=='KONTYNUUJ OGLĄDANIE':
                VODmyList('watched')
            else:
                for rr in r['elements']:
                    addContToList(rr['item'])
    
    xbmcplugin.endOfDirectory(addon_handle)       
    
def sectionList(cid):
    hea=base.heaGen()
    url=apiVOD+'products/sections/'+cid+'?elementsLimit=30&lang=pl&maxResults=30&platform='+platform
    resp=requests.get(url,headers=hea).json()
    for r in resp['elements']:
        addContToList(r['item'])
    xbmcplugin.endOfDirectory(addon_handle)
                
def addContToList(r,myList=None,playTime=None):
    cid=str(r['id'])
    name=r['title']
    type=r['type']
    img=getImg(r['images'])

    iL,availLabel=detCont(r)
    mod=''
    isPlayable='false'
    isFolder=True
    if type=='SERIAL':
        mod='sezonList'
        URL = base.build_url({'mode':mod,'cid':cid,'title':name})
    if type=='VOD':
        name=titleWithTill(availLabel,name)
        mod='playVid'
        URL = base.build_url({'mode':mod,'eid':cid})
        isPlayable='true'
        isFolder=False
    if type=='EPISODE':
        name=r['season']['serial']['title']+' | '+name
        name=titleWithTill(availLabel,name)
        mod='playVid'
        URL = base.build_url({'mode':mod,'eid':cid})
        isPlayable='true'
        isFolder=False
    if type=='SECTION':
        mod='sectionList'
        URL = base.build_url({'mode':mod,'cid':cid})
    if type=='BANNER':#do weryfikacji
        if 'webUrl' in r:
            cid=r['webUrl'].split(',')[-1]
            if 'collections' in r['webUrl']:
                mod='sectionList'
                URL = base.build_url({'mode':mod,'cid':cid})
            elif '/programy' in r['webUrl'] or '/seriale' in r['webUrl']:
                mod='sezonList'
                URL = base.build_url({'mode':mod,'cid':cid,'title':name})
            elif '/filmy' in r['webUrl'] or '/teatr' in r['webUrl']:
                name=titleWithTill(availLabel,name)
                mod='playVid'
                URL = base.build_url({'mode':mod,'eid':cid})
                isPlayable='true'
                isFolder=False
            else:
                URL = base.build_url({'mode':'mainPage'})
    
    if 'displaySchedules' in r:
        if len(r['displaySchedules'])>0:
            if (type=='SERIAL' or type=='VOD' or type=='EPISODE') and r['displaySchedules'][0]['type']=='SOON':
                isPlayable='false'
                isFolder=False
    
    if type=='LIVE':
        mod='playLive'
        URL = base.build_url({'mode':mod,'cid':cid})
        plot=''
        isPlayable='true'
        isFolder=False
    
    setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart':img}
    
    contMenu=False
    cmItems=[]
    if type=='VOD' or type=='SERIAL' or type=='EPISODE':
        contMenu=True
        #if type!='EPISODE':
        cmItems.append(('[B]Dodaj do ulubionych[/B]','RunPlugin(plugin://plugin.video.TVP_VOD?mode=favAdd&url='+quote(URL)+'&name='+quote(name)+'&art='+quote(str(setArt))+'&iL='+quote(str(iL))+'&cid='+cid+')'))
        cmItems.append(('[B]Szczegóły[/B]','RunPlugin(plugin://plugin.video.TVP_VOD?mode=showDet&eid='+cid+')'))
    
    if type=='VOD' or type=='SERIAL':
        cmItems.append(('[B]Trailer[/B]','RunPlugin(plugin://plugin.video.TVP_VOD?mode=trailer&eid='+cid+')'))
    
    if addon.getSetting('synchKontOgl')=='true':
        if myList==None and (type=='VOD' or type=='SERIAL' or type=='EPISODE'):
            cmItems.append(('[B]Dodaj do Mojej Listy (app)[/B]','RunPlugin(plugin://plugin.video.TVP_VOD?mode=myListAdd&cid='+cid+')'))
        elif myList!=None: #(type=='VOD' or type=='SERIAL' or type=='LIVE') and 
            cmItems.append(('[B]Usuń z Mojej Listy (app)[/B]','RunPlugin(plugin://plugin.video.TVP_VOD?mode=myListDel&cid='+cid+'&type='+myList+')'))
    
    if type!='LIVE':
        xbmcplugin.setContent(addon_handle, 'videos')
    
    if myList=='WATCHED':
        pathFile=URL
        totalTime=r['duration']*60

        request={
            "jsonrpc": "2.0", 
            "method": "Files.SetFileDetails", 
            "params": {
                "file": pathFile, 
                "media": "video", 
                "resume": {
                    "position":playTime, 
                    "total": totalTime
                }
            },
            "id":"1"
        }
            
        results = json.loads(xbmc.executeJSONRPC(json.dumps(request)))
                
    base.addItemList(URL, name, setArt, 'video', iL, isFolder, isPlayable, contMenu, cmItems)

def categList(mc):
    hea=base.heaGen()
    url=apiVOD+'items/categories?mainCategoryId='+mc+'&lang=pl&platform='+platform
    resp=requests.get(url,headers=hea).json()
    arCateg=[['[B]Wszystkie[/B]','all']]
    for c in resp:
        arCateg.append([c['name'],c['id']])
    for ac in arCateg:
        setArt={'thumb': '', 'poster': img_path+'tvp_vod.png', 'banner': '', 'icon': 'OverlayUnwatched.png', 'fanart':fanart}
        url = base.build_url({'mode':'contList','mainCateg':mc,'Categ':str(ac[1]),'page':'1'})
        base.addItemList(url, ac[0], setArt)
    xbmcplugin.endOfDirectory(addon_handle)

def getImg(x):
    img='https://vod.tvp.pl/static/images/no-image.jpg'
    for i in x:
        if i=='16x9':
            if len(x['16x9'])>0:
                if 'templateUrl' in x['16x9'][0] or 'url' in x['16x9'][0]:
                    img=x['16x9'][0]['templateUrl'] if 'templateUrl' in x['16x9'][0] else x['16x9'][0]['url']
                    img=img.format(width=480,height=268).replace(' ','')
    if img.startswith('//'):
        img='https:'+img
    return img

def titleWithTill(d,t):#data dostępności w tytule
    title=t
    if 'LAST_BELL' in d:
        title=t+' [COLOR=yellow]/do: '+d.split('|')[1]+'/[/COLOR]'
    if 'SOON' in d:
        title='[COLOR=gray]%s[/COLOR]'%(title)
    '''
    tillPeriod=int(addon.getSetting('tillPeriod'))
    if 'Dostępny do: ' in d:
        till=re.compile('Dostępny do: (.*)').findall(d.replace('[/B]',''))[0]
        now=datetime.datetime.now()
        if (datetime.datetime(*(time.strptime(till,'%Y-%m-%d %H:%M')[0:6]))-now).days<=tillPeriod:
            title=t+' [COLOR=yellow]/do: '+till+'/[/COLOR]'
    '''
    return title        

sortMeths=['Domyślnie','Ostatnio dodane','Najstarsze','Najnowsze','A-Z','Z-A']

def setSortMeth(): #helper
    sortName=addon.getSetting('sortContent')
    st=sortName if sortName!='' else 'Domyślnie'
    select=xbmcgui.Dialog().select('Typ sortowania:', sortMeths)
    if select>-1:
        new_st=sortMeths[select]
    else:
        new_st=st
    
    if new_st!=st:
        addon.setSetting('sortContent',new_st)
        xbmc.executebuiltin('Container.Refresh()')

def contList(mc,c,pg):
    cnt=25
    p=int(pg)
    start=(p-1)*cnt
    hea=base.heaGen()
    sortName=addon.getSetting('sortContent')
    st=sortName if sortName!='' else 'Domyślnie'
    sortMeth={'Domyślnie':'&sort=createdAt&order=desc','Ostatnio dodane':'&sort=createdAt&order=desc','Najstarsze':'&sort=year&order=asc','Najnowsze':'&sort=year&order=desc','A-Z':'&sort=title&order=asc','Z-A':'&sort=title&order=desc',}
    sortParam=sortMeth[sortName]
    
    #sortowanie
    if p==1:
        tit='[COLOR=cyan][B]Sortowanie: [/B][/COLOR]%s'%(st)
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_empty, 'fanart':fanart}
        URL = base.build_url({'mode':'setSortMeth'})
        base.addItemList(URL, tit, setArt, isF=False)
        
    if c=='all':
        url=apiVOD+'products/vods?=&firstResult='+str(start)+'&maxResults='+str(cnt)+'&mainCategoryId[]='+mc+sortParam+'&lang=pl&platform='+platform
    else:
        url=apiVOD+'products/vods?=&firstResult='+str(start)+'&maxResults='+str(cnt)+'&mainCategoryId[]='+mc+'&categoryId[]='+c+sortParam+'&lang=pl&platform='+platform
    resp=requests.get(url,headers=hea).json()
    total=resp['meta']['totalCount']
    
    for r in resp['items']:
        addContToList(r)

    if p<math.ceil(total/cnt):
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_empty, 'fanart':fanart}
        url = base.build_url({'mode':'contList','mainCateg':mc,'Categ':c,'page':str(p+1)})
        base.addItemList(url, '[COLOR=cyan][B]>>> Następna strona[/B][/COLOR]', setArt)
    
    xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)
    
def sezonList(cid,tit):
    hea=base.heaGen()
    url=apiVOD+'products/vods/serials/'+cid+'/seasons?lang=pl&platform='+platform
    resp=requests.get(url,headers=hea).json()
    if len(resp)==1: #jeden sezon
        sezId=str(resp[0]['id'])
        episodeList(cid,sezId,tit,'1','yes')
    else:
        for r in resp:
            sez_id=str(r['id'])
            sez_name=r['title']
            
            iL={'title': '','sorttitle': '','plot': tit}
            setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': '', 'fanart':fanart}
            url = base.build_url({'mode':'episodeList','cid':cid,'sezId':sez_id,'title':tit,'init':'yes','page':'1'})
            base.addItemList(url, sez_name, setArt, 'video', iL)
        
        xbmcplugin.setContent(addon_handle, 'videos')
        xbmcplugin.endOfDirectory(addon_handle)
       
def episodeList(cid,sezId,tit,pg,init):
    #cnt=25
    cnt=int(addon.getSetting('epCount'))
    p=int(pg)
    if init=='yes':
        hea=base.heaGen()
        url=apiVOD+'products/vods/serials/'+cid+'/seasons/'+sezId+'/episodes?lang=pl&platform='+platform
        resp=requests.get(url,headers=hea).json()#list
        #rev_resp=list(reversed(resp))
        saveF(PATH_profile+'episodes.txt',str(resp))
    
    resp=eval(openF(PATH_profile+'episodes.txt'))
    total=len(resp)
    start=cnt*(p-1)
    stop=min(cnt*(p-1)+cnt,total)
    for i in range(start,stop):
        r=resp[i]
        addContToList(r)
        
    if p<math.ceil(total/cnt):
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_empty, 'fanart':fanart}
        url = base.build_url({'mode':'episodeList','init':'no','cid':cid,'sezId':sezId,'title':tit,'page':str(p+1)})
        base.addItemList(url, '[B]>>> Następna strona[/B]', setArt, 'video')
        
    xbmcplugin.setContent(addon_handle, 'videos')
    
    xbmcplugin.endOfDirectory(addon_handle)
    xbmcplugin.addSortMethod(handle=addon_handle,sortMethod=xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
    #xbmcplugin.addSortMethod(handle=addon_handle,sortMethod=xbmcplugin.SORT_METHOD_PLAYLIST_ORDER)

def trailer(eid):
    trailer_url=''
    hea=base.heaGen()
    url=apiVOD+'products/vods/'+eid+'?lang=pl&platform='+platform
    resp=requests.get(url,headers=hea).json()
    if 'trailer' in resp:
        if resp['trailer']:
            url=apiVOD+'products/'+eid+'/videos/playlist?=&videoType=TRAILER&lang=PL&platform='+platform
            resp=requests.get(url,headers=hea).json()
            try:
                trailer_url=resp['sources']['MP4'][0]['src']
            except:
                trailer_url=''
    
    if trailer_url !='':
        #base.directPlayer(trailer_url)
        trailer_url+='|User-Agent='+base.UA
        xbmc.Player().play(trailer_url)
    else:
        xbmcgui.Dialog().notification('TVP VOD', 'Trailer niedostępny', xbmcgui.NOTIFICATION_INFO)

def showDet(eid):#menu kont
    hea=base.heaGen()
    url=apiVOD+'products/vods/'+eid+'?lang=pl&platform='+platform
    resp=requests.get(url,headers=hea).json()
    if 'code' in resp:
        if resp['code']=='ITEM_NOT_AVAILABLE':
            plot='Materiał niedostępny'
        else:
            plot='brak danych'
    else:
        iL,availLabel=detCont(resp)
        
        plot='[B]Rok prod:[/B] %s\n'%(str(iL['year']))
        plot+='[B]Kraj:[/B] %s\n'%(', '.join(iL['country']))
        plot+='[B]Gatunek:[/B] %s\n'%(', '.join(iL['genre']))
        plot+='[B]Czas:[/B] %s min.\n'%(str(int(iL['duration']/60)))
        plot+='[B]Ograniczenia wiekowe:[/B] %s lat\n'%(str(iL['mpaa']))
        if len(iL['cast'])>0:
            plot+='[B]Obsada:[/B] %s\n'%(', '.join(iL['cast']))
        if len(iL['director'])>0:
            plot+='[B]Reżyseria:[/B] %s\n'%(', '.join(iL['director']))
        if len(iL['writer'])>0:
            plot+='[B]Scenariusz:[/B] %s\n'%(', '.join(iL['writer']))
        plot+=iL['plot']
    
    dialog = xbmcgui.Dialog()
    dialog.textviewer('Szczegóły', plot)

def playVid(eid,videoType='MOVIE',b=None,e=None):
    hea=base.heaGen()
    if videoType=='MOVIE':
        url=apiVOD+'products/vods/'+eid+'?lang=pl&platform='+platform
        resp=requests.get(url,headers=hea).json()
        iL,availLabel=detCont(resp)
    
    url=apiVOD+'products/'+eid+'/videos/playlist?platform='+platform+'&videoType='+videoType
    resp=requests.get(url,headers=hea).json()
    #print(resp)
    if 'code' in resp:
        if resp['code']=='ITEM_NOT_PAID':
            xbmcgui.Dialog().notification('TVP VOD', 'Materiał płatny', xbmcgui.NOTIFICATION_INFO)
            xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
    else:    
        url_stream=''
        protocol=''
        drm=False
        urlLic=''
        
        toHeaLic=hea
        toHeaLic.update({'API-CorrelationID':'smarttv_'+base.code_gen(32),'Content-Type':''})
        heaLic=urlencode(toHeaLic)
        
        if 'sources' in resp:
            if 'drm' in resp:
                url_stream=resp['sources']['DASH'][0]['src']
                protocol='mpd'
                drm=True
                urlLic=resp['drm']['WIDEVINE']['src']
                #K22
                drm_config={
                    "com.widevine.alpha": {
                        "license": {
                            "server_url": urlLic,
                            "req_headers": heaLic
                        }
                    }
                }
            else:
  
                if videoType=='LIVE': #na żywo -> kanały TV
                    streamType=addon.getSetting('streamTvProtocol')#HLS,DASH
                    url_stream=resp['sources'][streamType][0]['src']
                    protocol=tvp_go.protocols[streamType]
                elif 'HLS' in resp['sources']:
                    url_stream=resp['sources']['HLS'][0]['src']
                    protocol='hls'
                elif 'DASH' in resp['sources']:
                    url_stream=resp['sources']['DASH'][0]['src']
                    protocol='mpd'    
                    
        
        subtOn=False
        sbt_src=subt_gen_ABO(resp)
        if addon.getSetting('askSubt')=='true' and len(sbt_src)>0:
            ok=xbmcgui.Dialog().yesno("Napisy", 'Dostępne są napisy. Chcesz je włączyć?')
            if ok:
                subtOn=True
        
        if url_stream !='':
            if not (b==None and e==None):
                url_stream+='?begin='+b+'&end='+e
            xbmc.log('@@@stream_url: '+url_stream, level=xbmc.LOGINFO)
            if addon.getSetting('livePlayerType')=='ffmpeg' and videoType=='LIVE' and b==None:
                #base.directPlayer(url_stream)
                base.ISffmpegPlayer(protocol,url_stream)
            else: 
                if protocol=='hls' and videoType=='LIVE':
                    proxyport = addon.getSetting('proxyport')
                    url_stream='http://127.0.0.1:%s/MANIFEST='%(str(proxyport))+url_stream
                
                import inputstreamhelper
                PROTOCOL = protocol
                DRM = 'com.widevine.alpha'
                is_helper = inputstreamhelper.Helper(PROTOCOL,DRM)
                if is_helper.check_inputstream():
                    play_item = xbmcgui.ListItem(path=url_stream)
                    play_item.setMimeType('application/xml+dash')
                    if videoType=='MOVIE':
                        play_item.setInfo('video',infoLabels=iL)
                    play_item.setContentLookup(False)
                    play_item.setProperty('inputstream', is_helper.inputstream_addon)
                    play_item.setProperty("IsPlayable", "true")
                    play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
                    play_item.setProperty('inputstream.adaptive.stream_headers','User-Agent='+base.UA+'&Referer='+baseurl)
                    play_item.setProperty('inputstream.adaptive.manifest_headers','User-Agent='+base.UA+'&Referer='+baseurl)#K21
                    play_item.setSubtitles(sbt_src)
                    if drm==True:
                        kodiVer=xbmc.getInfoLabel('System.BuildVersion')
                        if int(kodiVer.split('.')[0])<22:
                            play_item.setProperty("inputstream.adaptive.license_type", DRM)
                            play_item.setProperty("inputstream.adaptive.license_key", '%s|%s|R{SSM}|'%(urlLic,heaLic))
                        else:
                            play_item.setProperty("inputstream.adaptive.drm", json.dumps(drm_config))
                      
                    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
                    
                    if subtOn:
                        #włączenie napisów gdy są w materiale
                        if len(sbt_src)>0:
                            while not xbmc.Player().isPlaying():
                                xbmc.sleep(100)
                            xbmc.Player().showSubtitles(True)
                
        else:
            xbmcgui.Dialog().notification('TVP VOD', 'Błąd odtwarzania', xbmcgui.NOTIFICATION_INFO)
            xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())

def subt_gen_ABO(d):#tablica z linkami do plików z napisami (format .ssa)
    subt=[]
    if 0: # j00zek 'subtitles' in d:
        if len(d['subtitles'])!=0:
            for n,i in enumerate(d['subtitles']):
                urlSubt=i['url']
                resp=requests.get(urlSubt)
                ttml = Ttml2SsaAddon()
                ttml.parse_ttml_from_string(resp.text)
                ttml.write2file(PATH_profile+'subt_'+str(n)+'.ssa')
                subt.append(PATH_profile+'subt_'+str(n)+'.ssa')
    return subt
    
def search():
    qry=xbmcgui.Dialog().input(u'Szukaj (przynajmniej 3 znaki):', type=xbmcgui.INPUT_ALPHANUM)
    if qry:
        types={'VOD':'','SERIAL':'','EPISODE':''}
        hea=base.heaGen()
        for t in list(types.keys()):
            u=apiVOD+'products/vods/search/'+t+'?lang=pl&platform='+platform+'&keyword='+qry
            resp=requests.get(u,headers=hea).json()['items']
            types[t]=str(len(resp))
            saveF('%ssearch%s.txt'%(PATH_profile,t),str(resp))
        
        s=[
            ['Filmy'+' ('+types['VOD']+')','searchVOD'],
            ['Seriale'+' ('+types['SERIAL']+')','searchSERIAL'],
            ['Odcinki'+' ('+types['EPISODE']+')','searchEPISODE']
        ]
        
        for ss in s:
            setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': 'DefaultAddonsSearch.png', 'fanart':fanart}
            url = base.build_url({'mode':'searchRes','cat':ss[1]})
            base.addItemList(url, ss[0], setArt, 'video')

        xbmcplugin.endOfDirectory(addon_handle)
    else:
        main_menu()

def detCont(x): #poprawione
    
    title=x['season']['serial']['title'] if x['type']=='EPISODE' else x['title'] 
    rating=str(x['rating']) if 'rating' in x else ''
    ep=x['number'] if x['type']=='EPISODE' else None
    seas=x['season']['number'] if x['type']=='EPISODE' else None
    descShort=cleanText(x['lead']) if 'lead' in x else ''
    desc=cleanText(x['description']) if 'description' in x else ''
    desc=descShort if desc=='' else desc
    descShort=desc if descShort=='' else descShort
    dur=x['duration'] if 'duration' in x else 0
    year=x['year'] if 'year' in x else 0
    country=[c['name'] for c in x['countries']] if 'countries' in x else []
    actors=[c['name'] for c in x['actors']] if 'actors' in x else []
    directors=[c['name'] for c in x['directors']] if 'directors' in x else []
    scriptwriters=[c['name'] for c in x['scriptwriters']] if 'scriptwriters' in x else []
    genre=[c['name'] for c in x['genres']] if 'genres' in x else []
    
    #dostępność
    avail=''
    availLabel=''
    if 'displaySchedules' in x:
        if x['displaySchedules'][0]['type']!='SOON':
            if 'payable' in x:
                if x['payable']:
                    avail+='Płatny\n'
                else:
                    avail+='Bezpłatny\n'
            if 'since' in x:
                avail+='[B]Data publikacji: [/B]'+x['since'].split('T')[0]+'\n'
            if x['displaySchedules'][0]['type']=='PREMIERE':
                if 'till' in x['displaySchedules'][0]:
                    avail+='[B]Dostępny do: [/B]'+x['displaySchedules'][0]['till'].split('T')[0]+'\n'
                avail+='[COLOR=yellow]PRAPREMIERA[/COLOR]\n'
            else:
                if 'till' in x:
                    avail+='[B]Dostępny do: [/B]'+x['till'].split('T')[0]+'\n'
                if x['displaySchedules'][0]['type']=='LAST_BELL':
                    availLabel='LAST_BELL|'+locTime(x['displaySchedules'][0]['till'])
                    avail+='[COLOR=yellow]OSTATNIA SZANSA[/COLOR]\n'
        else:
            availLabel='SOON'
            avail+='[COLOR=yellow]WKRÓTCE[/COLOR]\n'
            avail+='[B]Dostępny od: [/B]'+x['displaySchedules'][0]['till'].split('T')[0]+'\n'
            if 'payableSince' in x:
                if x['displaySchedules'][0]['till'].split('T')[0]==x['payableSince'].split('T')[0] :
                    avail+='Płatny\n'
                else:
                    avail+='Bezpłatny\n'
            else:
                avail+='Bezpłatny\n'
    
    else:
        if 'till' in x and x['type'] in ['EPISODE','VOD']:
            te=locTime(x['till'])
            avail+='[B]Dostępny do: [/B]'+te+'\n'
            
            now=datetime.datetime.now()
            if (datetime.datetime(*(time.strptime(te,'%Y-%m-%d %H:%M')[0:6]))-now).days<=int(addon.getSetting('tillPeriod')):
                availLabel='LAST_BELL|'+te
                avail+='[COLOR=yellow]OSTATNIA SZANSA[/COLOR]\n'
    
    descShort=avail+descShort
    desc=avail+desc
    iL={}
    if x['type']=='EPISODE':
        iL={'title': title,'sorttitle': title,'mpaa':rating,'plotoutline':descShort,'plot': desc,'year':year,'genre':genre,'duration':dur,'director':directors,'country':country,'cast':actors,'writer':scriptwriters,'season':seas,'episode':ep,'mediatype':'episode'}
    elif x['type'] in ['VOD','SERIAL']:
        iL={'title': title,'sorttitle': title,'mpaa':rating,'plotoutline':descShort,'plot': desc,'year':year,'genre':genre,'duration':dur,'director':directors,'country':country,'cast':actors,'writer':scriptwriters,'mediatype':'movie'}
        if x['type']=='SERIAL':
            iL['mediatype']='tvshow'
    else:
        iL={'plot':title}
    #print(iL)
    return iL,availLabel

def searchRes(c):
    res=eval(openF('%s%s.txt'%(PATH_profile,c)))
    for r in res:
        addContToList(r)
       
    xbmcplugin.setContent(addon_handle, 'videos')    
    xbmcplugin.endOfDirectory(addon_handle)    

# LIVE + artchiwum TV (VOD)
def lives():
    hea=base.heaGen()
    url=apiVOD+'products/lives?maxResults=0&lang=pl&platform='+platform
    resp=requests.get(url,headers=hea).json()
    
    IDs=[str(i['id']) for i in resp['items']]
    now=datetime.datetime.now()
    since=now.astimezone().strftime('%Y-%m-%dT%H:00%z')
    till=now.astimezone().strftime('%Y-%m-%dT%H:59%z')
    urlEPG=apiVOD+'products/lives/programmes?liveId[]=%s&since=%s&till=%s&lang=pl&platform=%s' %('&liveId[]='.join(IDs),quote(since),quote(till),platform)
    respEPG=requests.get(urlEPG,headers=hea).json()
    
    for r in resp['items']:
        img=r['images']['16x9'][0]['templateUrl'].format(width=512,height=0).replace(' ','')#['url']
        if img.startswith('//'):
            img='https:'+img
        def gTime(x):
            return datetime.datetime(*(time.strptime(x,'%Y-%m-%dT%H:%M:%S%z')[0:6]))
        try:
            EPGdata=[e for e in respEPG if e['live']['id']==r['id'] and gTime(e['since'])<now and gTime(e['till'])>now][0]
            st=gTime(EPGdata['since']).strftime('%H:%M')
            et=gTime(EPGdata['till']).strftime('%H:%M')
            desc=EPGdata['description'] if 'description' in EPGdata else ''
            plot='[B]%s-%s[/B] %s\n[I]%s[/I]'%(st,et,EPGdata['title'],desc)
        except:
            plot=''
                
        iL={'title': '','sorttitle': '','plot': plot}
        setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart':fanart}
        url = base.build_url({'mode':'playLive','cid':str(r['id'])})
        base.addItemList(url, r['title'], setArt, 'video', iL, False, 'true')
    xbmcplugin.endOfDirectory(addon_handle)

catchup_st=[399697,399698,399699,399700,399701,399702,399703,399704,399721,399722,399723,399724,399732,399740,399741,399742,399743,399745,399746,399747,399748,399749,399750,399751,399752,399753,399754,399755]#,957438,957439]
   
def archive():
    catchup_st=[399697,399698,399699,399700,399701,399702,399703,399704,399721,399722,399723,399724,399732,399740,399741,399742,399743,399745,399746,399747,399748,399749,399750,399751,399752,399753,399754,399755]#,957438,957439]
    hea=base.heaGen()
    url=apiVOD+'products/lives?maxResults=0&lang=pl&platform='+platform
    resp=requests.get(url,headers=hea).json()
    for r in resp['items']:
        if r['id'] in catchup_st:
            catch='y'
        else:
            catch='n'
            
        img=r['images']['16x9'][0]['url']
        if img.startswith('//'):
            img='https:'+img
                            
        setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart':fanart}
        url = base.build_url({'mode':'arch_calendar','cid':str(r['id']),'catch':catch})
        base.addItemList(url, r['title'], setArt)
    xbmcplugin.endOfDirectory(addon_handle)

'''
def archive(): #type=RECORDING lub CATCHUP #nie wdrożono w serwisie
    hea=base.heaGen()
    url=apiVOD+'products/lives?maxResults=0&lang=pl&platform='+platform
    resp=requests.get(url,headers=hea).json()
    for r in resp['items']:            
        img=r['images']['16x9'][0]['url']
        if img.startswith('//'):
            img='https:'+img
                            
        setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart':fanart}
        url = base.build_url({'mode':'arch_calendar','cid':str(r['id'])})
        base.addItemList(url, r['title'], setArt)
    xbmcplugin.endOfDirectory(addon_handle)
'''

def arch_calendar(cid,catch):
    today=datetime.datetime.now()
    ar_date=[]
    i=0
    replayPeriod='7'
    while i<=int(replayPeriod):#7
        day=(today-datetime.timedelta(days=i)).strftime('%Y-%m-%d')
        ar_date.append(day)
        i=i+1

    for d in ar_date:
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': 'DefaultYear.png', 'fanart': fanart}
        url = base.build_url({'mode':'arch_programs','date':d,'cid':cid,'catch':catch})
        #url = base.build_url({'mode':'arch_programs','date':d,'cid':cid,'catch':catch}) #type=RECORDING lub CATCHUP
        base.addItemList(url, d, setArt, 'video')
    xbmcplugin.endOfDirectory(addon_handle)

'''
def arch_programs(d,cid): #type=RECORDING lub CATCHUP #nie wdrożono w serwisie
    z=datetime.datetime.now().astimezone().strftime('%z')
    since=d+'T00:00'+z
    till=d+'T23:59'+z
    urlEPG=apiVOD+'products/lives/programmes?liveId[]=%s&since=%s&till=%s&lang=pl&platform=%s' %(cid,quote(since),quote(till),platform)
    respEPG=requests.get(urlEPG,headers=hea).json()
    def sortFN(i):
        return i['since']
    respEPG.sort(key=sortFN,reverse=False)
    
    def gTime(x):
        return datetime.datetime(*(time.strptime(x,'%Y-%m-%dT%H:%M:%S%z')[0:6]))
    now=datetime.datetime.now()
    
    for r in respEPG:
        if gTime(r['since'])<now and gTime(r['till'])>now-datetime.timedelta(days=7) and 'programRecordingId' in r: #'externalRecordingUid' in r
            pid=str(r['programRecordingId'])#str(r['externalRecordingUid'])
            title=r['title']
            st=gTime(r['since']).strftime('%H:%M')
            et=gTime(r['till']).strftime('%H:%M')
            tit='[B]%s[/B] %s'%(st,title)
            desc=r['description'] if 'description' in r else ''

            img=r['images']['16x9'][0]['url'] if 'images' in r else img_empty
            if img.startswith('//'):
                img='https:'+img
                    
            iL={'title': '','sorttitle': '','plot': desc}
            setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart':fanart}
            url = base.build_url({'mode':'playArch','pid':pid})
            base.addItemList(url, tit, setArt, 'video', iL, False, 'true')
    
    xbmcplugin.setContent(addon_handle, 'videos') 
    xbmcplugin.endOfDirectory(addon_handle)
'''

def arch_programs(d,cid,catch):
    z=datetime.datetime.now().astimezone().strftime('%z')
    since=d+'T00:00'+z
    till=d+'T23:59'+z
    urlEPG=apiVOD+'products/lives/programmes?liveId[]=%s&since=%s&till=%s&lang=pl&platform=%s' %(cid,quote(since),quote(till),platform)
    respEPG=requests.get(urlEPG,headers=hea).json()
    #print(respEPG)
    def sortFN(i):
        return i['since']
    respEPG.sort(key=sortFN,reverse=False)
    
    def gTime(x):
        return datetime.datetime(*(time.strptime(x,'%Y-%m-%dT%H:%M:%S%z')[0:6]))
        
    def toUTC(x,delta=0):
        ts=(datetime.datetime(*(time.strptime(x,'%Y-%m-%dT%H:%M:%S%z')[0:6]))+datetime.timedelta(seconds=delta)).timestamp()
        return datetime.datetime.utcfromtimestamp(ts).strftime('%Y%m%dT%H%M%S')
    
    now=datetime.datetime.now()
    
    for r in respEPG:
        if gTime(r['since'])<now and gTime(r['till'])>now-datetime.timedelta(days=7) and 'programRecordingId' in r: #'externalRecordingUid' in r
            title=r['title']
            st=gTime(r['since']).strftime('%H:%M')
            et=gTime(r['till']).strftime('%H:%M')
            tit='[B]%s[/B] %s'%(st,title)
            desc=r['description'] if 'description' in r else ''

            img=r['images']['16x9'][0]['url'] if 'images' in r else img_empty
            if img.startswith('//'):
                img='https:'+img
            
            if catch=='y':
                begin=toUTC(r['since'])
                end=toUTC(r['till'],30*60)
                URL=base.build_url({'mode':'playArch','cid':cid,'begin':begin,'end':end})
                show=True
            else:
                if 'relatedVod' in r:
                    vid=str(r['relatedVod']['id'])
                    URL=base.build_url({'mode':'playArch','vid':vid})
                    desc+='\n[B]Źródło: [/B]VOD'
                    show=True
                elif 'externalRecordingUid' in r:
                    pid=r['externalRecordingUid']
                    URL=base.build_url({'mode':'playArch','pid':pid})
                    desc+='\n[B]Źródło: [/B]VOD ext'
                    show=True
                else:
                    show=False
            if show:                
                iL={'title': '','sorttitle': '','plot': desc}
                setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart':fanart}
                base.addItemList(URL, tit, setArt, 'video', iL, False, 'true')
    
    xbmcplugin.setContent(addon_handle, 'videos') 
    xbmcplugin.endOfDirectory(addon_handle)
    
def playArchExt(pid): #'externalRecordingUid' z EPG
    url_stream=''
    url='https://token-java-v2.tvp.pl/tokenizer/token/'+pid
    h={
        'User-Agent':base.UA
    }
    resp=requests.get(url,headers=h).json()
    if 'formats' in resp and resp['formats']!=None:
        
        streamType=addon.getSetting('streamTvProtocol')#HLS,DASH
        mimeType=tvp_go.mimeTypes[streamType]
        protocol=tvp_go.protocols[streamType]
        
        urls=[f for f in resp['formats'] if f['mimeType']==mimeType]
        url_stream=urls[0]['url']
        
        if url_stream !='':
            
            if protocol=='hls':
                proxyport = addon.getSetting('proxyport')
                url_stream='http://127.0.0.1:%s/MANIFEST='%(str(proxyport))+url_stream
            
            import inputstreamhelper
            PROTOCOL = protocol
            is_helper = inputstreamhelper.Helper(PROTOCOL)
            if is_helper.check_inputstream():
                play_item = xbmcgui.ListItem(path=url_stream)
                play_item.setMimeType('application/xml+dash')
                play_item.setContentLookup(False)
                play_item.setProperty('inputstream', is_helper.inputstream_addon)
                play_item.setProperty("IsPlayable", "true")
                play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
                play_item.setProperty('inputstream.adaptive.stream_headers','User-Agent='+base.UA)
                play_item.setProperty('inputstream.adaptive.manifest_headers','User-Agent='+base.UA)#K21

                #play_item.setSubtitles(sbt_src)
                '''
                if drm==True:
                    play_item.setProperty("inputstream.adaptive.license_type", 'com.widevine.alpha')
                    play_item.setProperty("inputstream.adaptive.license_key", urlLic+'|'+heaLic+'|R{SSM}|')
                '''  
                xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
                
                '''
                #włączenie napisów gdy są w materiale
                if len(sbt_src)>0:
                    while not xbmc.Player().isPlaying():
                        xbmc.sleep(100)
                    xbmc.Player().showSubtitles(True)
                '''
        else:
            xbmcgui.Dialog().notification('TVP VOD', 'Błąd odtwarzania', xbmcgui.NOTIFICATION_INFO)
            xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
    else:
        xbmcgui.Dialog().notification('TVP VOD', 'Brak źródła', xbmcgui.NOTIFICATION_INFO)
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())

def playLiveSC(cid,s,e):
    def toTmp(x):
        y=datetime.datetime(*(time.strptime(x,'%Y%m%dT%H%M%S')[0:6]))
        offset=int(addon.getSetting('cuOffset'))
        z=(y+datetime.timedelta(hours=offset)).strftime('%Y%m%dT%H%M%S')
        
        return z
        
    if s!=None and e!=None:
        ts=toTmp(s)
        te=toTmp(e)
        playVid(cid,'LIVE',ts,te)
    else:
        playVid(cid,'LIVE')
        
def M3U_live():
    file_name = addon.getSetting('fname_vod')
    path_m3u = addon.getSetting('path_m3u_vod')
    print(path_m3u)
    if file_name == '' or path_m3u == '':
        xbmcgui.Dialog().notification('TVP_VOD', 'Ustaw nazwę pliku oraz katalog docelowy', xbmcgui.NOTIFICATION_ERROR)
        return
    xbmcgui.Dialog().notification('TVP_VOD', 'Generuję listę M3U', xbmcgui.NOTIFICATION_INFO)
    data = '#EXTM3U\n'
    dataE2 = '' #j00zek for E2 bouquets
    
    hea=base.heaGen()
    url=apiVOD+'products/lives?maxResults=0&lang=pl&platform='+platform
    resp=requests.get(url,headers=hea).json()
    for r in resp['items']:
        cid=str(r['id'])
        cName = r['title']
        cLogo = r['images']['16x9'][0]['templateUrl'].format(width=512,height=0).replace(' ','')
        if cLogo.startswith('//'):
            cLogo='https:'+cLogo
        
        if int(cid) not in catchup_st:
            data += '#EXTINF:0 tvg-id="%s" tvg-logo="%s" group-title="TVP_VOD",%s\nplugin://plugin.video.TVP_VOD?mode=playLive&cid=%s\n' % (cName,cLogo,cName,cid)
            dataE2 += 'plugin.video.TVP_VOD/addon.py%3fmode=playLive&cid=' + '%s:%s\n' % (cid, cName) #j00zek for E2 bouquets
        else:
            data += '#EXTINF:0 tvg-id="%s" tvg-logo="%s" group-title="TVP_VOD" catchup="append" catchup-source="&s={utc:YmdTHMS}&e={utcend:YmdTHMS}" catchup-days="7" catchup-correction="0.0",%s\nplugin://plugin.video.TVP_VOD?mode=playLiveSC&cid=%s\n' % (cName,cLogo,cName,cid)
            dataE2 += 'plugin.video.TVP_VOD/addon.py%3fmode=playLiveSC&cid=' + '%s:%s\n' % (cid, cName) #j00zek for E2 bouquets

    f = xbmcvfs.File(os.path.join(path_m3u, file_name), 'w')
    f.write(data)
    f.close()
    xbmcgui.Dialog().notification('TVP_VOD', 'Wygenerowano listę M3U.', xbmcgui.NOTIFICATION_INFO)

    f = xbmcvfs.File(os.path.join(path_m3u, 'iptv.e2b'), 'w') #j00zek for E2 bouquets
    f.write(dataE2)
    f.close()
    xbmcgui.Dialog().notification('TVP_VOD', 'Wygenerowano listę E2B', xbmcgui.NOTIFICATION_INFO)

        
#ULUBIONE KODI
    
def favList():
    fURL=PATH_profile+'ulubioneVOD.json'
    js=base.openJSON(fURL)
    for j in js:
        isPlayable='false'
        isFolder=True
        URL=j[0]
        if 'playVid' in j[0]:
            isPlayable='true'
            isFolder=False
        
        contMenu=True
        cmItems=[
            ('[B]Usuń z ulubionych[/B]','RunPlugin(plugin://plugin.video.TVP_VOD?mode=favDel&url='+quote(j[0])+')'),
            ('[B]Szczegóły[/B]','RunPlugin(plugin://plugin.video.TVP_VOD?mode=showDet&eid='+j[4]+')')
        ]
        
        iL=eval(j[3])
        setArt=eval(j[2])
        base.addItemList(URL, j[1], setArt, 'video', iL, isFolder, isPlayable, contMenu, cmItems)
    
    xbmcplugin.setContent(addon_handle, 'videos')     
    xbmcplugin.endOfDirectory(addon_handle)

def favDel(u):
    fURL=PATH_profile+'ulubioneVOD.json'
    js=base.openJSON(fURL)
    for i,j in enumerate(js):
        if  j[0]==u:
            del js[i]
    base.saveJSON(fURL,js)
    xbmc.executebuiltin('Container.Refresh()')

def favAdd(u,n,a,il,c):
    fURL=PATH_profile+'ulubioneVOD.json'
    js=base.openJSON(fURL)
    duplTest=False
    for j in js:
        if j[0]==u:
            duplTest=True
    if not duplTest:
        js.append([u,n,a,il,c])
        xbmcgui.Dialog().notification('TVP VOD', 'Dodano do ulubionych', xbmcgui.NOTIFICATION_INFO)
    else:
        xbmcgui.Dialog().notification('TVP VOD', 'Materiał jest już w ulubionych', xbmcgui.NOTIFICATION_INFO)
    base.saveJSON(fURL,js)

def paraLogOut():
    addon.setSetting('API_Authentication','')
    addon.setSetting('API_ProfileUid','')
    addon.setSetting('logged','false')
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
    #xbmcgui.Dialog().notification('TVP_VOD', 'Wylogowanie przez zewnętrzną aplikację', xbmcgui.NOTIFICATION_INFO)
    xbmc.executebuiltin('Container.Update(plugin://plugin.video.TVP_VOD/,replace)')

#Moja lista/Kontynuacja (z apki VOD)
   
def myList():
    items=[
        ['Ulubione','favVODList','FAVOURITE','tvp_vod.png'],
        ['Kontynuuj oglądanie','VODwatched','WATCHED','tvp_vod.png']
    ]
    for s in items:    
        setArt={'thumb': '', 'poster': img_path+s[3], 'banner': '', 'icon': 'OverlayUnwatched.png', 'fanart':fanart}
        url = base.build_url({'mode':s[1],'categ':s[2]})
        base.addItemList(url, s[0], setArt)
    xbmcplugin.endOfDirectory(addon_handle)
        
def VODmyList(contType):
    hea=base.heaGen()
    url=apiVOD+'subscribers/bookmarks?type='+contType+'&lang=pl&platform='+platform
    resp=requests.get(url,headers=hea).json()
    if 'code' in resp:
        if resp['code']=='AUTHENTICATION_REQUIRED':
            paraLogOut()
    else:
        for r in resp['items']:
            playTime=r['playTime'] if contType=='WATCHED' else None
            addContToList(r['item'],myList=contType,playTime=playTime)
            
        xbmcplugin.setContent(addon_handle, 'videos') 
        xbmcplugin.endOfDirectory(addon_handle)


def myListAdd(c):
    if addon.getSetting('synchKontOgl')=='true':
        hea=base.heaGen()
        url=apiVOD+'subscribers/bookmarks?type=FAVOURITE&lang=pl&platform='+platform
        data={
            'itemId':int(c)
        }
        resp=requests.post(url,headers=hea,json=data)
        if resp.status_code==204:
            xbmcgui.Dialog().notification('TVP VOD', 'Dodano do ulobionych (app)', xbmcgui.NOTIFICATION_INFO)
            xbmc.executebuiltin('Container.Refresh()')
    else:
        xbmcgui.Dialog().notification('TVP_VOD', 'Synchronizacja z aplikacją wyłączona.', xbmcgui.NOTIFICATION_INFO)
        
def myListDel(c,t):
    if addon.getSetting('synchKontOgl')=='true':
        hea=base.heaGen()
        url=apiVOD+'subscribers/bookmarks?type='+t+'&itemId[]='+c+'&lang=pl&platform='+platform
        resp=requests.delete(url,headers=hea)
        if resp.status_code==204:
            xbmcgui.Dialog().notification('TVP VOD', 'Usunięto z listy Kontynuuj oglądanie', xbmcgui.NOTIFICATION_INFO)
            xbmc.executebuiltin('Container.Refresh()')
    else:
        xbmcgui.Dialog().notification('TVP_VOD', 'Synchronizacja z aplikacją wyłączona.', xbmcgui.NOTIFICATION_INFO)


def age_verify(): #nie wykorzystywane
    pin=xbmcgui.Dialog().numeric(heading='Wpisz PIN (domyślny: 1234):', type=0, defaultt='')
    if pin:
        hea=base.heaGen()
        url=apiVOD+'subscribers/adult/pin?lang=pl&platform='+platform
        data={
            "pin": str(pin)
        }
        resp=requests.post(url,headers=hea,json=data)
    else:
        xbmcgui.Dialog().notification('TVP VOD', 'Nie wpisano PIN-u', xbmcgui.NOTIFICATION_INFO)
        
def cleanText(t):
    toDel=['<p>','</p>','<strong>','</strong>','&nbsp;']
    for d in toDel:
        t=t.replace(d,'')
    t=t.replace('<br>',' ')
    t=re.sub('<([^<]+?)>','',t)
    return t
    
def expFav(File):
    from shutil import copy2, copyfile
    fURL=PATH_profile+File+'.json'
    targetPATH=xbmcgui.Dialog().browse(0, 'Wybierz lokalizację docelową', '', '', enableMultiple = False)
    #copy2(fURL,targetPATH)
    copyfile(fURL, targetPATH+File+'.json')
    xbmcgui.Dialog().notification('TVP_VOD', 'Plik zapisany', xbmcgui.NOTIFICATION_INFO)
    
def impFav(File):
    from shutil import copy2,copyfile
    fURL=PATH_profile+File+'.json'
    sourcePATH=xbmcgui.Dialog().browse(1, 'Wybierz plik', '', '.json', enableMultiple = False)
    copyfile(sourcePATH,fURL)
    #copy2(sourcePATH,fURL)
    xbmcgui.Dialog().notification('TVP_VOD', 'Plik zapisany', xbmcgui.NOTIFICATION_INFO)
    
mode = params.get('mode', None)

if not mode:
    if addon.getSetting('DeviceUid')=='':
        #getSerialID()
        addon.setSetting('DeviceUid',base.code_gen(32))
    main_menu()
else:
    if mode=='logIn':
        logIn()
        if addon.getSetting('logged')=='true':
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
            xbmc.executebuiltin('Container.Update(plugin://plugin.video.TVP_VOD/,replace)')
            #main_menu()
    
    if mode=='logOut':
        logOut()
        if addon.getSetting('logged')=='false':
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
            xbmc.executebuiltin('Container.Update(plugin://plugin.video.TVP_VOD/,replace)')
            #main_menu()
    
    if mode=='userInfo':
        userInfo()
    
    if mode=='vodProfiles':
        vodProfiles()
        
    if mode=='changeProfile':
        uid=params.get('uid')
        used=params.get('used')
        changeProfile(uid,used)
    
    if mode=='others':
        others()
    
    if mode=='mainPage':
        mainPage()
    
    if mode=='mainPageCateg':
        mpc=params.get('categID')
        mainPageCateg(mpc)
        
    if mode=='sectionList':
        cid=params.get('cid')
        sectionList(cid)
        
    if mode=='categList':
        mc=params.get('mainCateg')
        categList(mc)
        
    if mode=='contList':
        mc=params.get('mainCateg')
        c=params.get('Categ')
        pg=params.get('page')
        contList(mc,c,pg)
    
    if mode=='setSortMeth':
        setSortMeth()
    
    if mode=='sezonList':
        cid=params.get('cid')
        tit=params.get('title')
        sezonList(cid,tit)
    
    if mode=='episodeList':
        cid=params.get('cid')
        sezId=params.get('sezId')
        tit=params.get('title')
        pg=params.get('page')
        init=params.get('init')
        episodeList(cid,sezId,tit,pg,init)
    
    if mode=='showDet':
        eid=params.get('eid')
        showDet(eid)
        
    if mode=='trailer':
        eid=params.get('eid')
        trailer(eid)

    if mode=='playVid':
        eid=params.get('eid')
        playVid(eid)
        
    if mode=='favList':
        favList()
        
    if mode=='favDel':
        url=params.get('url')
        favDel(url)
        
    if mode=='favAdd':
        url=params.get('url')
        name=params.get('name')
        art=params.get('art')
        iL=params.get('iL')
        cid=params.get('cid')
        favAdd(url,name,art,iL,cid)
    
    if mode=='search':
        search()
        
    if mode=='searchRes':
        c=params.get('cat')
        searchRes(c)

    if mode=='myList':
        myList()
    
    if mode=='favVODList' or mode=='VODwatched':
        categ=params.get('categ')
        VODmyList(categ)
    

    if mode=='myListAdd':
        cid=params.get('cid')
        myListAdd(cid)
        
    if mode=='myListDel':
        cid=params.get('cid')
        type=params.get('type')
        myListDel(cid,type)
    
    if mode=='age_verify':
        age_verify()
    
    #liveTV VOD    
    if mode=='lives':
        lives()

    if mode=='playLive':
        cid=params.get('cid')
        playVid(cid,'LIVE')
    
    if mode=='M3U_live':
        M3U_live()
    
    #archiwumTV VOD
    if mode=='archive':
        archive()
        
    if mode=='arch_calendar':
        cid=params.get('cid')
        catch=params.get('catch') 
        #arch_calendar(cid)#type=RECORDING
        arch_calendar(cid,catch)
        
    if mode=='arch_programs':
        cid=params.get('cid')
        date=params.get('date')
        catch=params.get('catch')
        #arch_programs(date,cid) #type=RECORDING
        arch_programs(date,cid,catch)
        
    if mode=='playArch':
        cid=params.get('cid')
        pid=params.get('pid')
        vid=params.get('vid')
        b=params.get('begin')
        e=params.get('end')
        if cid!=None:
            playVid(cid,'LIVE',b,e)
        elif pid!=None:
            playArchExt(pid)
        elif vid!=None:
            playVid(vid)
        
        #playVid(pid,False,'RECORDING')###dla type=RECORDING - jeszcze nieobsługiwane
    
    if mode=='playLiveSC':
        cid=params.get('cid')
        s=params.get('s')
        e=params.get('e')
        playLiveSC(cid,s,e)
       
    if mode=='expFav':
        expFav('ulubioneVOD')
        
    if mode=='impFav':
        impFav('ulubioneVOD')
    
    #TVP INFO, TVP3 Regiony   
    if mode=='playProg':
        aid=params.get('asset_id')
        tvp_ext.playProg(aid)
    
    if mode=='tvp3':
        tvp_ext.regionyList()
    
    if mode=='progCategs':
        aid=params.get('asset_id')
        tvp_ext.progCategs(aid)
        
    if mode=='progList':
        aid=params.get('asset_id')
        all=params.get('all')
        tvp_ext.progList(aid,all)
    
    if mode=='vidDir':
        aid=params.get('asset_id')
        tvp_ext.vidDir(aid)
    
    if mode=='epList':
        aid=params.get('asset_id')
        p=params.get('page')
        tvp_ext.epList(aid,p)
    '''
    if mode=='tvp_info_progs':
        #from resources.lib.tvpExt import progList
        tvp_ext.progList('191888')
    '''
    
    if mode=='rc':
        tvp_ext.itemCategs('35470692')
    
    #TVP INFO (new api)
    
    if mode=='tvp_info':
        tvp_ext.videoList('tvp_info','72048318','1')
    
    if mode=='videoList':
        portal=params.get('portal')
        cid=params.get('cid')
        page=params.get('page')
        tvp_ext.videoList(portal,cid,page)
    
    
    #TVPGO (telewizja)
    if mode=='tvpgo':
        tvp_go.menuTV()
    
    if mode=='liveTV':
        tvp_go.channels_gen()
    
    if mode=='replayTV':
        tvp_go.replayChannelsGen()
        
    if mode=='playLiveTV':
        chCode=params.get('chCode')
        chID=params.get('chID')
        s=params.get('s')
        e=params.get('e')
        tvp_go.PlayStream(chCode,chID,s,e)
        
    if mode=='replayTVdate':
        chCode=params.get('chCode')
        tvp_go.replayCalendarGen(chCode)
    
    if mode=='replayTVprogs':
        chCode=params.get('chCode')
        d=params.get('date')
        tvp_go.replayProgramsGen(chCode,d)
    
    if mode=='playReplayTV':
        chCode=params.get('chCode')
        progID=params.get('progID')
        #pp=addon.getSetting('playerProtocol')
        tvp_go.PlayProgram(chCode,progID)#pp
        
    if mode=='EPG':
        stCode=params.get('stCode')
        tvp_go.getEPG(stCode)
        
    if mode=='BUILD_M3U':
        file_name = addon.getSetting('fname_go')
        path_m3u = addon.getSetting('path_m3u_go')
        tvp_go.generate_m3u(file_name,path_m3u)
    
    #
    if mode=='listTV':
        tvp_go.listTV()
        
    if mode=='calendar':
        code=params.get('code')
        cid=params.get('cid')
        catchup=params.get('catchup')
        tvp_go.calendar(code,cid,catchup)  
    
    if mode=='programs':
        d=params.get('date')
        code=params.get('code')
        cid=params.get('cid')
        catchup=params.get('catchup')
        tvp_go.programs(d,code,cid,catchup)
    
    if mode=='playReplay':
        b=params.get('begin')
        e=params.get('end')
        cid=params.get('cid')
        catchup=params.get('catchup')
        tvp_go.playReplay(cid,b,e,catchup)
    
    if mode=='noSource':
        pass
        
    #TVP SPORT    
    if mode=='tvp_sport':
        tvp_ext.sportTrans()
    
    if mode=='playSportLive':
        aId=params.get('asset_id')
        ts=params.get('timeStart')
        te=params.get('timeEnd')
        pla=params.get('playable')
        tvp_ext.playSportLive(aId,ts,te,pla)
        
    if mode=='tvp_sport_video':
        tvp_ext.categsListSport('tvp_sport','548369')
    
    if mode=='categsListSport':
        portal=params.get('portal')
        cid=params.get('cid')
        subMain=params.get('subMain')
        tvp_ext.categsListSport(portal,cid,subMain)
        
    if mode=='videoListSport':
        portal=params.get('portal')
        cid=params.get('cid')
        page=params.get('page')
        count=params.get('count')
        tvp_ext.videoListSport(portal,cid,page,count)
    
    #Fav Ext
    if mode=='favExtList':
        fav_ext.favExtList()
        
    if mode=='favExtDel':
        u=params.get('url')
        fav_ext.favExtDel(u)
        
    if mode=='favExtAdd':
        u=params.get('url')
        t=params.get('title')
        l=params.get('infoLab')
        i=params.get('img')
        fav_ext.favExtAdd(u,t,l,i)
        
    if mode=='expExtFav':
        expFav('ulubione_ext')
        
    if mode=='impExtFav':
        impFav('ulubione_ext')
