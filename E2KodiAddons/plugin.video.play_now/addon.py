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
import base64
import json
import random
import time
import datetime
import math
from urllib.parse import urlencode, quote_plus, quote, unquote, parse_qsl


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon(id='plugin.video.play_now')

PATH=addon.getAddonInfo('path')
PATH_profile=xbmcvfs.translatePath(addon.getAddonInfo('profile'))
if not xbmcvfs.exists(PATH_profile):
    xbmcvfs.mkdir(PATH_profile)
img_empty=PATH+'/resources/img/empty.png'
fanart=PATH+'/resources/img/fanart.jpg'

#UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
baseurl='https://playnow.pl/'
apiURL='https://playnow.pl/api/v2/'
platform='BROWSER'

def heaGen():
    HEA={
        'referer':baseurl,
        'User-Agent':UA,
        'API-DeviceInfo':'Firefox 115.0 on Windows 10 64-bit;Windows;10;Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0;3.28.4-web',
        'API-DeviceUid':addon.getSetting('uid'),
        'API-SN':addon.getSetting('uid'),
        'API-CorrelationId':'%s-%s-%s-%s-%s'%(code_gen(8),code_gen(4),code_gen(4),code_gen(4),code_gen(12)),
        'Origin':baseurl[:-1]
    }
    return HEA

def cookiesGen():
    cookies={
        'rememberMe':addon.getSetting('rememberMe'),
        'uid':addon.getSetting('uid'),
        'JSESSIONID':addon.getSetting('JSESSIONID'),
    }
    return cookies

def paramsGen():
    p={
        'platform':platform,
        'tenant':addon.getSetting('tenant')
    }
    return p

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

def code_gen(x):
    base='0123456789abcdef'
    code=''
    for i in range(0,x):
        code+=base[random.randint(0,15)]
    return code
    
    
def main_menu():
    items=[]
    if addon.getSetting('logged')=='true':
        #refresh()
        items=[
            ['Kanały TV','tvList','DefaultTVShows.png'],
            ['Archiwum programów','replay','DefaultYear.png'],
            ['Wyloguj','logOut','DefaultUser.png']
        ]
    else:
        items=[
            ['Zaloguj','logIn','DefaultUser.png']
        ]
    for i in items:
        setArt={'icon': i[2],'fanart':fanart}
        url = build_url({'mode':i[1]})
        addItemList(url, i[0], setArt)
    xbmcplugin.endOfDirectory(addon_handle)   

def logIn():
    phone=addon.getSetting('phone')
    if phone!='':
        url=apiURL+'subscribers/login/url?type=BROWSER&redirectUri=https://playnow.pl/logowanie&platform='+platform
        hea_=heaGen()
        cookies={'uid':addon.getSetting('uid')}
        resp=requests.get(url,headers=hea_,cookies=cookies).json()
        
        #url='https://oauth.play.pl/oauth/authorize?layout=auto&response_type=code&client_id=ATDSLOGIN&display=ipcheck link&scope=oauth/*&redirect_uri=http://www.tv.play.pl/logowanie'
        url=resp['url']
        hea={
            'User-Agent':UA
        }
        resp=requests.get(url,headers=hea,allow_redirects=False)
        cookies=dict(resp.cookies)
        addon.setSetting('cook_auth',str(cookies))
        #print(cookies)
        resp=requests.get(url,headers=hea,cookies=cookies)
        
        data='_csrf=%s&msisdn=%s&_eventId_submit=&_eventId_submit='%(cookies['XSRF-TOKEN'],addon.getSetting('phone'))
        #print(data)
        hea={
            'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'origin':'https://oauth.play.pl',
            'User-Agent':UA,
            'Content-Type':'application/x-www-form-urlencoded'
        }
        url_auth='https://oauth.play.pl/login?execution=e1s1'
        resp=requests.post(url_auth,headers=hea,data=data,cookies=cookies)
        if 'Kliknij link' in resp.text:
            setArt={'icon': 'DefaultUser.png','fanart':fanart}
            url = build_url({'mode':'logInCont'})
            addItemList(url, 'Kontynuuj logowanie po autoryzacji via SMS', setArt)
            xbmcplugin.endOfDirectory(addon_handle)
        else:
            xbmcplugin.endOfDirectory(addon_handle)#do poprawy
    else:
        xbmcgui.Dialog().notification('Play Now', 'Uzupełnij nr telefonu lub nr zarządzania usługą w ustawieniach.', xbmcgui.NOTIFICATION_INFO)
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
        
def logInCont():
    cookies=eval(addon.getSetting('cook_auth'))
    url='https://oauth.play.pl/login?execution=e1s2'
    hea={
        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'origin':'https://oauth.play.pl',
        'User-Agent':UA,
        'Content-Type':'application/x-www-form-urlencoded'
    }
    data='_csrf=%s&_eventId_submit='%(cookies['XSRF-TOKEN'])
    resp=requests.post(url,headers=hea,data=data,cookies=cookies,allow_redirects=False)    
    if 'location' not in resp.headers:
        xbmc.log('@@@Brak przekierowania', level=xbmc.LOGINFO)
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
    elif 'execution' in resp.headers['location']:#dodać mechanizm powtórzenia weryfikacji (ileś tam razy)
        xbmc.log('@@@Jest przekierowanie z execution, ale nie załapało SMS-a', level=xbmc.LOGINFO)
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
    elif 'authorize?' in resp.headers['location']: #https://oauth.play.pl/oauth/authorize?layout=auto&response_type=code&client_id=ATDSLOGIN&display=ipcheck link&scope=oauth/*&redirect_uri=https://playnow.pl/logowanie
        hea={
            'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'referer':'https://oauth.play.pl/login?execution=e1s2',
            'User-Agent':UA,
            'Connection':'keep-alive',
            'Accept-Language':'pl,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding':'gzip, deflate, br',
            'Content-Type':'',
            'Sec-Fetch-Dest':'document',
            'Sec-Fetch-Mode':'navigate',
            'Sec-Fetch-Site':'same-origin',
            'Upgrade-Insecure-Requests':'1',
            'Host':'oauth.play.pl'
            
        }
        resp1=requests.get(resp.headers['location'],headers=hea,cookies=cookies,allow_redirects=False)
        url_login=resp1.headers['location'] #https://playnow.pl/logowanie?code=ny8vkgzhxwysgnu
        cooks={
            'uid':addon.getSetting('uid')
        }
        hea={
            'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'referer':'https://oauth.play.pl/',
            'User-Agent':UA,
        }
        respLogin=requests.get(url_login,headers=hea,cookies=cooks)
        
        hea_=heaGen()
        hea_.update({'Referer':url_login})
        data={
            'code':url_login.split('code=')[-1],
            'redirectUri':'https://playnow.pl/logowanie'
        }
        url=apiURL+'subscribers/login/play?platform='+platform
        resp=requests.post(url,json=data,headers=hea,cookies=cooks)
        addon.setSetting('rememberMe',dict(resp.cookies)['rememberMe'])
        addon.setSetting('JSESSIONID',dict(resp.cookies)['JSESSIONID'])
        respJSON=resp.json()
        if 'token' in respJSON:
            addon.setSetting('token',respJSON['token'])
            products()
            addon.setSetting('logged','true')
        else:
            xbmcgui.Dialog().notification('Play Now', 'Nieokreslony błąd logowania', xbmcgui.NOTIFICATION_INFO)
            xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())

def products():
    hea_=heaGen()
    cookies=cookiesGen()
    url=apiURL+'subscribers/products?platform='+platform
    resp=requests.get(url,headers=hea_,cookies=cookies).json()
    if 'message' in resp:
        if resp['message']=='authentication.required':
            return False
    else:
        priceStrategyIds=resp['priceStrategyIds']
        availableProductIds=resp['availableProductIds']
        tenant=resp['tenant']
        addon.setSetting('priceStrategyIds',str(priceStrategyIds))
        addon.setSetting('availableProductIds',str(availableProductIds))
        addon.setSetting('tenant',str(tenant))
        
        return True
    
def logOut():
    hea_=heaGen()
    cookies=cookiesGen()
    hea_.update({'Accept':'application/json, text/plain, */*'})
    url=apiURL+'subscribers/logout?platform='+platform
    resp=requests.post(url,headers=hea_,cookies=cookies)

    #if 'rememberMe' in dict(resp.cookies):
    if resp.status_code==200:
        try:
            url='https://oauth.play.pl/logout.do?continue=https://playnow.pl&client_id=ATDSLOGIN'
            hea={
                'User-Agent':UA,
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Referer':baseurl,
            }
            resp=requests.get(url,headers=hea)
            addon.setSetting('logged','false')
            addon.setSetting('rememberMe','')
            addon.setSetting('JSESSIONID','')
            addon.setSetting('cook_auth','')
            addon.setSetting('token','')
            addon.setSetting('priceStrategyIds','')
            addon.setSetting('availableProductIds','')
            addon.setSetting('tenant','')
        except:
            xbmcgui.Dialog().notification('Play Now', 'Nie wylogowano (e2)', xbmcgui.NOTIFICATION_INFO)
            xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())        
        
    else:
        xbmcgui.Dialog().notification('Play Now', 'Nie wylogowano (e1)', xbmcgui.NOTIFICATION_INFO)
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
        

def req(t,u,h,c,p=None,d={},j=True):
    if t=='get':
        resp=requests.get(u,headers=h,cookies=c,params=p)
    elif t=='post':
        resp=requests.post(u,headers=h,cookies=c,params=p,json=d)
    cookiesIn=dict(resp.cookies)
    c=['JSESSIONID','rememberMe']
    for cc in c:
        if cc in cookiesIn:
            addon.setSetting(cc,cookiesIn[cc])
            xbmc.log('@@@Odświeżono cookies: '+cc, level=xbmc.LOGINFO)
            #xbmcgui.Dialog().notification('Play Now', "Odświeżono cookies: "+cc, xbmcgui.NOTIFICATION_INFO)
    if j:
        resp=resp.json()
    return resp
    
      
def getEPG(cid,ts,te):
    
    def getStrTime(x):
        return datetime.datetime.fromtimestamp(x).astimezone().strftime('%Y-%m-%dT%H:%M%z')
    
    since=getStrTime(ts)
    till=getStrTime(te)
    
    hea_=heaGen()
    hea_.update({'Sync-With-Server':'true'})
    cookies=cookiesGen()
    tenant=addon.getSetting('tenant')
    url=apiURL+	'products/lives/epgs'
    par=paramsGen()
    par.update({
        'liveId[]':cid,
        'since':since,
        'till':till,
    })
    resp=req('get',url,hea_,cookies,par)

    return resp

def EPGinfo(cid):
    now=int(time.time())
    epg=getEPG(cid,now,now+12*60*60)
    plot=''
    for e in epg:
        title=e['title']
        since=e['since'].split(' ')[-1][:-3]
        till=e['till'].split(' ')[-1][:-3]
        plot+='[B]%s - %s[/B] %s\n'%(since,till,title)
    
    if plot=='':
        plot='Brak danych EPG'
    dialog = xbmcgui.Dialog()
    dialog.textviewer('EPG', plot)     

    
def channels():
    url=apiURL+'products/lives'
    resp=req('get',url,heaGen(),cookiesGen(),paramsGen())
    chans=[]
    for c in resp:
        if c['liveType']=='LIVE':
            chName=c['title']
            cid=c['id']
            if 'timeshiftDuration' in c:
                tsDur=c['timeshiftDuration']
            else:
                tsDur=0
            if 'catchUpAvailable' in c or addon.getSetting('cuAll')=='true':
                cu=True
            else:
                cu=False
            try:
                img=c['logos']['L1x1_cl'][0]['url']
            except:
                img=img_empty
            chans.append([chName,cid,img,tsDur,cu])
    
    return chans
        
def tvList(t):
    chans=channels()
    for c in chans:
        if t=='live' or (t=='replay' and c[4]):
            img='https:'+c[2] if c[2].startswith('//') else c[2]
            name=c[0]
            cid=c[1]

            if t=='live':
                isPlayable='true'
                isFolder=False
                url=build_url({'mode':'playSource','cid':cid,'tsDur':str(c[3])})
                plot='EPG dostępne z poziomu menu kontekstowego'
                contMenu=True
                cmItems=[
                    ('[B]EPG[/B]','RunPlugin(plugin://plugin.video.play_now?mode=EPGinfo&cid='+str(cid)+')')
                ]
                
            elif t=='replay':
                isPlayable='false'
                isFolder=True
                url=build_url({'mode':'calendar','cid':cid})
                plot=''
                contMenu=False
                cmItems=[]
                        
            setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart': img}
            iL={'title': name,'sorttitle': name,'plot': plot}
            addItemList(url, name, setArt, 'video', iL, isF=isFolder, isPla=isPlayable, contMenu=contMenu, cmItems=cmItems)
    
    xbmcplugin.endOfDirectory(addon_handle)
    xbmcplugin.addSortMethod(handle=addon_handle,sortMethod=xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.addSortMethod(handle=addon_handle,sortMethod=xbmcplugin.SORT_METHOD_TITLE)

def calendar(cid):
    days=7 #sprawdzić ile dni catchup
    now=datetime.datetime.now()
    for i in range(0,days+1):
        date=(now-datetime.timedelta(days=i*1)).strftime('%Y-%m-%d')
       
        setArt={'icon': 'DefaultYear.png','fanart':fanart}
        url=build_url({'mode':'programList','cid':cid,'date':date})
        addItemList(url, date, setArt)
        
    xbmcplugin.endOfDirectory(addon_handle)

def programList(cid,d):
    now=time.time()
    ts=datetime.datetime(*(time.strptime(d, "%Y-%m-%d")[0:6])).timestamp()
    if ts<now-7*24*60*60: #do spr
        ts=now-7*24*60*60 #do spr
    te=(datetime.datetime(*(time.strptime(d, "%Y-%m-%d")[0:6]))+datetime.timedelta(days=1)).timestamp()
    if te>now:
        te=now
    epg=getEPG(cid,int(ts),int(te))
    for e in epg:
        pid=str(e['id'])
        title=e['title']
        since=e['since'].split(' ')[-1][:-3]
        till=e['till'].split(' ')[-1][:-3]
        name='[B]%s - %s[/B] %s'%(since,till,title)
        desc=e['description'] if 'description' in e else ''
        try:
            img=e['covers']['L16x9'][0]['url']
        except:
            img=img_empty
        #tStart=int(datetime.datetime(*(time.strptime(e['since'], "%Y-%m-%d %H:%M:%S")[0:6])).timestamp()*1000)-int(datetime.datetime(*(time.strptime('2001-01-01 01:00:00', "%Y-%m-%d %H:%M:%S")[0:6])).timestamp()*1000)

        setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart': fanart}
        iL={'title': title,'sorttitle': title,'plot': desc}
        url=build_url({'mode':'playReplay','pid':pid})
        addItemList(url, name, setArt, 'video', iL, isF=False, isPla='true')
    
    xbmcplugin.endOfDirectory(addon_handle)
    
def playSource(c,tsDur,contType='LIVE',ts=None,te=None):
    url=apiURL+'products/'+c+'/player/configuration?type='+contType+'&platform='+platform
    resp=req('get',url,heaGen(),cookiesGen())
    if 'message' in resp:
        xbmcgui.Dialog().notification('Play Now', 'Usługa niedostępna: '+resp['message'], xbmcgui.NOTIFICATION_INFO)
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
    else:
        vidSess=resp['videoSession']['videoSessionId']
        
        url=apiURL+'products/'+c+'/playlist?type='+contType+'&version=3&videoSessionId='+vidSess+'&drmMultikey=false&platform='+platform
        resp=req('get',url,heaGen(),cookiesGen())
        print(resp)
        try:
            s_url=resp['sources']['DASH'][0]['src']
            xbmc.log('@@@STREAM_URL: '+s_url, level=xbmc.LOGINFO)
                       
            if ts !=None: #catchup SC
                base=datetime.datetime(*(time.strptime('2001-01-01 01:00', "%Y-%m-%d %H:%M")[0:6])).timestamp()
                tstart=int(int(ts)-base-60)*1000 #-1min
                tend=int(int(te)-base+5*60)*1000 #+5min
                if '?' not in s_url:
                    stream_url=s_url+'?startTime='+str(tstart)+'&stopTime='+str(tend)
                else:
                    stream_url=s_url+'&startTime='+str(tstart)+'&stopTime='+str(tend)
                if int(te)>=int(time.time()):
                    diff=(int(time.time())-int(ts))*1000
                    if '?' not in s_url:
                        stream_url=s_url+'?dvr='+str(diff)
                    else:
                        stream_url=s_url+'&dvr='+str(diff)
            else:
                stream_url=s_url
                if contType=='LIVE': #timeshift
                    stream_url+='&dvr=7200000'

            
            if stream_url.startswith('//'):
                stream_url='https:'+stream_url
            
            
            if 'WIDEVINE' in resp['drm']:
                licURL=resp['drm']['WIDEVINE']['src']
                cookies=cookiesGen()
                heaLic={
                    'User-Agent':UA,
                    'Referer':baseurl,
                    'Origin':baseurl[:-1],
                    'Cookie':'; '.join([str(x) + '=' + str(y) for x, y in cookies.items()]),
                    'content-type':''
                }
                lic='%s|%s|%s|'%(licURL,urlencode(heaLic),'R{SSM}')
            else:
                licURL=''
                heaLic=''
                lic=''
                
        except:
            stream_url=None
        print(stream_url)
        
        if stream_url!=None:
            import inputstreamhelper
            PROTOCOL = 'mpd'
            is_helper = inputstreamhelper.Helper(PROTOCOL)
            if is_helper.check_inputstream():
                play_item = xbmcgui.ListItem(path=stream_url)
                play_item.setMimeType('application/xml+dash')
                play_item.setContentLookup(False)
                play_item.setProperty('inputstream', is_helper.inputstream_addon)
                play_item.setProperty("IsPlayable", "true")
                play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
                play_item.setProperty('inputstream.adaptive.stream_headers', 'User-Agent='+UA)
                play_item.setProperty('inputstream.adaptive.manifest_headers', 'User-Agent='+UA)
                if contType=='EPG_ITEM' or ts!=None:
                    play_item.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
                    play_item.setProperty('ResumeTime', '1')
                    play_item.setProperty('TotalTime', '1')
                if licURL!='':
                    play_item.setProperty("inputstream.adaptive.license_type", 'com.widevine.alpha')
                    play_item.setProperty('inputstream.adaptive.license_key',lic)
                              
                xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

        else:
            xbmcgui.Dialog().notification('Play Now', 'Brak źródła', xbmcgui.NOTIFICATION_INFO)
            xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
    

def listM3U():
    file_name = addon.getSetting('fname')
    path_m3u = addon.getSetting('path_m3u')
    if file_name == '' or path_m3u == '':
        xbmcgui.Dialog().notification('Play Now', 'Podaj nazwę pliku oraz katalog docelowy.', xbmcgui.NOTIFICATION_ERROR)
        return
    xbmcgui.Dialog().notification('Play Now', 'Generuję listę M3U.', xbmcgui.NOTIFICATION_INFO)
    chans=channels()
    if chans !=False:
        data = '#EXTM3U\n'
        for c in chans:
            name=c[0]
            img='https:'+c[2] if c[2].startswith('//') else c[2]
            
            cid=c[1]
            if c[3]!=0: #CATCHUP SC
                cuDur='7'
                data += '#EXTINF:0 tvg-id="%s" tvg-logo="%s" group-title="PlayNow" catchup="append" catchup-source="&s={utc:Ymd_HMS}&e={utcend:Ymd_HMS}" catchup-days="%s" catchup-correction="0.0",%s\nplugin://plugin.video.play_now?mode=playSource&cid=%s\n' %(name,img,cuDur,name,cid)

            else:
                data += '#EXTINF:0 tvg-id="%s" tvg-logo="%s" group-title="Play Now" ,%s\nplugin://plugin.video.play_now?mode=playSource&cid=%s\n' %(name,img,name,cid)
        
        f = xbmcvfs.File(path_m3u + file_name, 'w')
        f.write(data)
        f.close()
        xbmcgui.Dialog().notification('Play Now', 'Wygenerowano listę M3U', xbmcgui.NOTIFICATION_INFO)
    else:
        xbmcgui.Dialog().notification('Play Now', 'Błąd przy generowaniu listy M3U', xbmcgui.NOTIFICATION_INFO)
   

mode = params.get('mode', None)

if not mode:
    if addon.getSetting('uid')=='' or addon.getSetting('uid')==None:
        addon.setSetting('uid',code_gen(32))
    if addon.getSetting('logged')=='true':
        main_menu()

    else:
        main_menu()
else:
    if mode=='logIn':#
        logIn()
    
    if mode=='logInCont':#
        logInCont()
        if addon.getSetting('logged')=='true':
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
            xbmc.executebuiltin('Container.Update(plugin://plugin.video.play_now/,replace)')
    
    if mode=='logOut':
        logOut()
        if addon.getSetting('logged')=='false':
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
            xbmc.executebuiltin('Container.Update(plugin://plugin.video.play_now/,replace)')
    
    if mode=='tvList':
        tvList('live')
    
    if mode=='replay':
        tvList('replay')
        
    if mode=='calendar':
        cid=params.get('cid')
        calendar(cid)
        
    if mode=='programList':
        cid=params.get('cid')
        date=params.get('date')
        programList(cid,date)
        
    if mode=='playReplay':
        pid=params.get('pid')
        playSource(pid,'0','EPG_ITEM')
        
    if mode=='EPGinfo':
        cid=params.get('cid')
        EPGinfo(cid)
        
    if mode=='playSource':
        if addon.getSetting('logged')=='true':
            cid=params.get('cid')
            tsDur=params.get('tsDur')
            ts=None
            te=None
            s=params.get('s')
            e=params.get('e')
            if s!=None and e!=None:
                co=int(addon.getSetting('cuOffset'))
                ts=str(int((datetime.datetime(*(time.strptime(s, "%Y%m%d_%H%M%S")[0:6]))+datetime.timedelta(hours=co)).timestamp()))
                te=str(int((datetime.datetime(*(time.strptime(e, "%Y%m%d_%H%M%S")[0:6]))+datetime.timedelta(hours=co)).timestamp()))            
            playSource(cid,tsDur,'LIVE',ts,te)
        else:
            xbmcgui.Dialog().notification('Play Now', 'Wymagane logowanie we wtyczce', xbmcgui.NOTIFICATION_INFO)
            
    if mode=='listM3U':
        if addon.getSetting('logged')=='true':
            listM3U()
        else:
            xbmcgui.Dialog().notification('Play Now', 'Operacja wymaga zalogowania', xbmcgui.NOTIFICATION_INFO)
            