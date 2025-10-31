import e2kodi__init__ # aby zainicjowac sciezki i nie musiec zmieniac czegos w kodzie

import os
import sys

import requests
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import re
#import unicodedata
import json
import random, hmac, hashlib, base64, string
import datetime,time
from urllib.parse import urlencode, quote_plus, quote, unquote, parse_qsl

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon(id='plugin.video.tv_smart_go')
PATH=addon.getAddonInfo('path')
PATH_profile=xbmcvfs.translatePath(addon.getAddonInfo('profile'))
if not xbmcvfs.exists(PATH_profile):
    xbmcvfs.mkdir(PATH_profile)
img_empty=PATH+'/resources/images/empty.png'
img_addon=PATH+'icon.png'
fanart=PATH+'/resources/images/fanart.jpg'

apiURL='https://api.tvsmart.pl/'
platform='ANDROID_TV'


def genHea():
    logged=addon.getSetting('logged')
    auth='Bearer' 
    if logged=='true':
        auth+= ' %s'%(addon.getSetting('access_token'))
    
    h={
        'authorization': auth,
        'api-deviceuid': addon.getSetting('device_id'),
        'api-device': 'sdk_google_atv_x86; unknown sdk_google_atv_x86; ANDROID_TV; 8.0.0; unknown; 4.9.30',
        'user-agent': addon.getSetting('device_id'),
        'accept-charset':'UTF-8',
        'accept':'*/*',
        'accept-encoding':'gzip'
    }
    return h

def genParams():
    p={
        'platform':platform,
        'system':addon.getSetting('system')
    }
    return p
    
def code_gen(x):
    base='0123456789abcdef'
    code=''
    for i in range(0,x):
        code+=base[random.randint(0,15)]
    return code
    

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
    
def fromStrToDate(s,f):
    return datetime.datetime(*(time.strptime(s,f)[0:6]))
    
def fromDateToStr(d,f):
    return d.strftime(f)

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
    
def ISAplayer(protocol, stream_url, DRM=False, licKey=None, drm_config={}, hea=None, live=False):
    mimeType={'hls':'application/x-mpegurl','mpd':'application/xml+dash'}
    import inputstreamhelper
    PROTOCOL = protocol
    if DRM:
        DRM = 'com.widevine.alpha'
        is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
    else:
        is_helper = inputstreamhelper.Helper(PROTOCOL)
    if is_helper.check_inputstream():
        play_item = xbmcgui.ListItem(path=stream_url)
        play_item.setMimeType(mimeType[protocol])
        play_item.setContentLookup(False)
        play_item.setProperty('inputstream', is_helper.inputstream_addon)
        play_item.setProperty('IsPlayable', 'true')
        play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
        if DRM:
            kodiVer=xbmc.getInfoLabel('System.BuildVersion')
            if int(kodiVer.split('.')[0])<22:
                play_item.setProperty('inputstream.adaptive.license_type', DRM)
                play_item.setProperty('inputstream.adaptive.license_key', licKey)
            else:
                play_item.setProperty('inputstream.adaptive.drm', json.dumps(drm_config))
        if live: #dotyczy LIVE TV (musi być ze względu na Polsat i TV4 mające rozdziały w manifestach)
            play_item.setProperty('ResumeTime', '43200')
            play_item.setProperty('TotalTime', '1')
        play_item.setProperty('inputstream.adaptive.stream_headers', urlencode(hea))
        play_item.setProperty('inputstream.adaptive.manifest_headers', urlencode(hea)) #K21
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

def directPlayer(stream_url):
    play_item = xbmcgui.ListItem(path=stream_url)
    play_item.setProperty("IsPlayable", "true")
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

def req(t,u,h,p,d={},json=True):
    if t=='get':
        resp=requests.get(u,headers=h,params=p)
    elif t=='post':
        resp=requests.post(u,headers=h,params=p,json=d)
    elif t=='delete':
        resp=requests.delete(u,headers=h,params=p)
    
    if json:
        resp=resp.json()
        if 'message' in resp:
            xbmc.log('@@@Błąd (req): '+resp['message'], level=xbmc.LOGINFO)
            if resp['message'] in ['Unauthenticated.','token contains an invalid number of segments : token contains an invalid number of segments']:
                paralogout()
                xbmcgui.Dialog().notification('TV SMART GO', resp['message'], xbmcgui.NOTIFICATION_INFO)
                return None
    
    return resp
      
def main_menu():
    if addon.getSetting('logged')!='true':
        sources=[
            ['ZALOGUJ','login','DefaultUser.png'],
        ]
    else:
        sources=[
            ['TV na żywo','live','DefaultTVShows.png'],
            ['Archiwum TV','replay','DefaultYear.png'],
            ['VOD','VOD','DefaultAddonVideo.png'],
            ['KIDS','KIDS','DefaultAddonVideo.png'],
            ['Katalog VOD','vod','DefaultAddonVideo.png'],
            ['Wypożyczone VOD','rent_vod','DefaultAddonVideo.png'],
            ['Wyszukiwarka','search','DefaultAddonsSearch.png'],
            ['WYLOGUJ','logout','DefaultUser.png']    
        ]
    for s in sources:        
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': s[2], 'fanart':fanart}
        url = build_url({'mode':s[1]})
        addItemList(url, s[0], setArt)
    xbmcplugin.endOfDirectory(addon_handle)

def login():
    u=addon.getSetting('username')
    p=addon.getSetting('password')
    if p!='' and u!='':
        url=apiURL+'subscriber/login'
        data={
            "agent": "sdk_google_atv_x86",
            "login": u,
            "maker": "unknown",
            "multiAccount": True,
            "os": platform,
            "osVersion": "8.0.0",
            "password": p,
            "uid": addon.getSetting('device_id')
        }
        
        hea={'content-type':'application/json'}
        hea.update(genHea())
        providers={'Vectra':'vectra','Multimedia':'MMPDTV','JAMBOX':'SGT','Elsat':'ofertaT4B1182','tvsmart.pl':'pureott'}
        prov=addon.getSetting('prov')
        paramsURL={
            'platform':platform,
            'system':providers[prov]#'vectra'
        }
        resp=requests.post(url,json=data,headers=hea,params=paramsURL).json()
        if 'message' in resp:
            xbmcgui.Dialog().notification('TV SMART GO', resp['message'], xbmcgui.NOTIFICATION_INFO)
            return
        else:
            addon.setSetting('access_token',resp['token'])
            addon.setSetting('system',resp['system'])
            
            if 'limits' in resp['status']:
                if resp['status']['limits'][0]['name']=='SUBSCRIBER_ASSIGNED_DEVICES_LIMIT_EXCEEDED':
                    xbmc.log('@@@Limit urządzeń: '+resp['status']['limits'][0]['message'], level=xbmc.LOGINFO)
                    toChange = xbmcgui.Dialog().yesno('UWAGA', 'Osiągnięto limit urządzeń. Czy zastąpić któreś z nich?')
                    if toChange:
                        #lista urządzeń
                        url=apiURL+'subscriber/devices/active'
                        hea2=genHea()
                        hea2.update({'authorization':'Bearer '+addon.getSetting('access_token')})
                        params_url={'platform':platform}
                        resp2=requests.get(url,headers=hea2,params=params_url).json()
                        devices=resp2['data']
                        labels=['[B]%s[/B] | Ostatnie logowanie: %s'%(d['device_name'],d['last_login_date']) for d in devices]
                        if 1: #emukodi
                            print('Zarejestrowanee urządzenia:')
                            id = 0
                            for d in devices:
                                print('\t',id, d['device_name'], d['last_login_date'])
                                id += 1
                            print('\nPierwsze zostanie zastąpione')
                        uids=[d['device_id'] for d in devices]
                        
                        #select=xbmcgui.Dialog().select('Urządzenie do usunięcia', labels)
                        select=0 #<< e2kodi: wymuszamy pierwsze urządzenie
                        if select>-1:
                            #zastąpienie urządzenia
                            url=apiURL+'subscriber/device/toggle'
                            
                            if 0: #oryginal
                                deviceName = xbmcgui.Dialog().input('Określ nazwę nowego urządzenia:', type=xbmcgui.INPUT_ALPHANUM)
                                if deviceName=='':
                                    deviceName='AVT_'+code_gen(4)
                            else: #emukodi
                                deviceName='AVT_'+code_gen(4)
                            
                            data={
                                "nameOfNewDevice": deviceName,
                                "uidOfDeviceToDelete": uids[select]
                            }
                            resp3=requests.put(url,headers=hea2,params=params_url,json=data).json()
                            if 'token' in resp3:
                                addon.setSetting('access_token',resp3['token'])
                                addon.setSetting('system',resp3['system'])
                            else:
                                xbmcgui.Dialog().notification('TV SMART GO', 'Błąd przy zastąpieniu urządzenia', xbmcgui.NOTIFICATION_INFO)
                                xbmc.log('@@@Błąd przy zastąpieniu urządzenia: '+str(resp3), level=xbmc.LOGINFO)
                                return
                        else:
                            xbmcgui.Dialog().notification('TV SMART GO', 'Przekroczona liczba urządzeń - nie wybrano urządzenia do usunięcia', xbmcgui.NOTIFICATION_INFO)
                            xbmc.log('@@@Nie wybrano urządzenia do podmiany', level=xbmc.LOGINFO)
                            return
                    else:
                        xbmcgui.Dialog().notification('TV SMART GO', 'Zrezygnowano z podmiany urządzenia', xbmcgui.NOTIFICATION_INFO)
                        xbmc.log('@@@Rezygnacja z  podmiany', level=xbmc.LOGINFO)
                        return
                else:
                    xbmc.log('@@@Błąd logowania - limit urządzeń: '+str(resp), level=xbmc.LOGINFO)
                    return
            
            elif 'deviceName' in resp['status']:
                if resp['status']['deviceName']==None:
                    if 0: #oryginal
                        deviceName = xbmcgui.Dialog().input('Określ nazwę nowego urządzenia:', type=xbmcgui.INPUT_ALPHANUM)
                        if deviceName=='':
                            deviceName='AVT_'+code_gen(4)
                    else: #emukodi
                        deviceName='AVT_'+code_gen(4)
                    url=apiURL+'subscriber/device/name'
                    hea2=genHea()
                    hea2.update({'authorization':'Bearer '+addon.getSetting('access_token')})
                    params_url={'platform':platform}
                    data={
                        "name": deviceName,
                    }
                    resp3=requests.post(url,headers=hea2,params=params_url,json=data).json()
                    xbmc.log('@@@Rej. nazwy nowego urządzenia: '+str(resp), level=xbmc.LOGINFO)
                    if 'token' in resp3:
                        addon.setSetting('access_token',resp3['token'])
                        addon.setSetting('system',resp3['system'])
                
            
            #produkty
            url=apiURL+'subscriber/products/uuids'
            hea=genHea()
            hea.update({'authorization':'Bearer '+addon.getSetting('access_token')})
            resp=requests.get(url,headers=hea,params=genParams()).json()
            if 'data' in resp:
                addon.setSetting('products',str(resp['data']))
            
                addon.setSetting('logged','true')
            else:
                xbmc.log('@@@Błąd - dane produktów: '+str(resp), level=xbmc.LOGINFO)
                return
            
    else:
        xbmcgui.Dialog().notification('TV SMART GO', 'Uzupełnij dane logowania w ustawieniach wtyczki', xbmcgui.NOTIFICATION_INFO)
    
def logout():
    url=apiURL+'subscriber/logout'
    hea=genHea()
    resp=req('post',url,genHea(),{})
    if resp!=None:
        if 'ok' in resp:
            addon.setSetting('products','')
            addon.setSetting('system','')
            addon.setSetting('access_token','')
            addon.setSetting('logged','false')
            xbmcgui.Dialog().notification('TV SMART GO', 'Wylogowano', xbmcgui.NOTIFICATION_INFO)
        else:
            xbmcgui.Dialog().notification('TV SMART GO', 'Błąd wylogowania', xbmcgui.NOTIFICATION_INFO)
            xbmc.log('@@@Błąd wylogowania: '+str(resp), level=xbmc.LOGINFO)
    else:
        toMainMenu()

def paralogout():
    addon.setSetting('products','')
    addon.setSetting('system','')
    addon.setSetting('access_token','')
    addon.setSetting('logged','false')
    xbmcgui.Dialog().notification('TV SMART GO', 'Sesja wygasła - wylogowanie', xbmcgui.NOTIFICATION_INFO)
    xbmc.log('@@@Paralogout', level=xbmc.LOGINFO)
    
def toMainMenu():
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
    xbmc.executebuiltin('Container.Update(plugin://plugin.video.tv_smart_go/,replace)')

def productsUpdate():
    now=int(time.time())
    prodUpdtTime=addon.getSetting('prodUpdtTime')
    if prodUpdtTime=='' or prodUpdtTime==None:
        prodUpdtTime='0'
    if now-int(prodUpdtTime)>=3600 and addon.getSetting('logged')=='true':
        url=apiURL+'subscriber/products/uuids'
        hea=genHea()
        hea.update({'authorization':'Bearer '+addon.getSetting('access_token')})
        resp=req('get',url,hea,genParams())
        if resp!=None:
            if 'data' in resp:
                addon.setSetting('products',str(resp['data']))
                addon.setSetting('prodUpdtTime',str(now))
        else:
            toMainMenu()
            

def epgALL(s,e):
    url=apiURL+'epg'
    paramsURL=genParams()
    paramsURL.update({
        'startDate':s,#20240223000000
        'endDate':e#20240224000000
    })
    resp=req('get',url,genHea(),paramsURL)

    return resp
    
def epgLive(epgData,cid):
    epg=''
    if epgData !=None:
        progs=[c['programs'] for c in epgData if c['channel_uuid']==cid]
        if len(progs)>0:
            for p in progs[0]:
                title=p['title'] if 'title' in p else '...'
                ts=fromDateToStr(fromStrToDate(p['since'],'%Y-%m-%d %H:%M:%S'),'%H:%M')
                te=fromDateToStr(fromStrToDate(p['till'],'%Y-%m-%d %H:%M:%S'),'%H:%M')
                category='[I](%s)[/I]'%(p['category']) if 'category' in p else ''
                    
                epg+='[B]%s - %s[/B] %s %s\n'%(ts,te,title,category)
    
    return epg

def availCheck(p,s):#p: products
    test=False
    for pp in p:
        if pp in s:
            test=True
            break
    return test
        
def channelsGen(genre=None):
    url=apiURL+'products/channel'
    paramsURL=genParams()
    paramsURL.update({
        'offset':'0',
        'limit':'500'
    })

    resp=req('get',url,genHea(),paramsURL)
    if resp!=None:

        sortType=addon.getSetting('sortTV')
        if sortType=='wg nazwy':
            def sortFN(i):
                return i['title']

            resp['data'].sort(key=sortFN,reverse=False)
  
        products=eval(addon.getSetting('products'))
        if genre!=None:
            channels=[c for c in resp['data'] if availCheck(products,c['available_in']) and genre in [str(g['id']) for g in c['genres']]]
        else:
            channels=[c for c in resp['data'] if availCheck(products,c['available_in'])]
    else:
        channels=None
    
    return channels

def chanGenres():
    url=apiURL+'products/genres/channel'
    paramsURL=genParams()
    resp=req('get',url,genHea(),paramsURL)
    if resp!=None:
        saveF(PATH_profile+'chan_genres.txt',str(resp['data']))
        labels=[r['name'] for r in resp['data']]
        labels.insert(0,'Wszystkie')
        select=xbmcgui.Dialog().select('Gatunek', labels)
        if select>-1:
            g='' if select==0 else [str(r['id']) for r in resp['data'] if r['name']==labels[select]][0]
            addon.setSetting('chGenre',g)
        else:
            addon.setSetting('chGenre','')
        xbmc.executebuiltin('Container.Refresh()')
    else:
        toMainMenu()
      
def tvList(t):
    genre=addon.getSetting('chGenre')
    channels=channelsGen() if genre=='' else channelsGen(genre)
    
    if channels!=None:
        
        #filtr wg gatunku
        name='[B]Gatunek: [/B]'
        if genre=='':
            name+='wszystkie'
        else:
            genres=eval(openF(PATH_profile+'chan_genres.txt'))
            name+=[g['name'] for g in genres if g['id']==int(genre)][0]
            
        setArt={'icon':'DefaultGenre.png'}
        URL=build_url({'mode':'chanGenres'})
        addItemList(URL, name, setArt, isF=False, isPla='false')
        
        if t=='live':
            now=datetime.datetime.now()
            ts=fromDateToStr(now,'%Y%m%d%H0000')
            te=fromDateToStr(now+datetime.timedelta(hours=8),'%Y%m%d%H0000')
            epgData=epgALL(ts,te)

        for c in channels:
            cid=c['uuid']
            name=c['title']
            img=c['images']['logo'][0]['url']
            cuTime=c['context']['catch_up_time']
            cu=c['context']['catch_up_active']
            show=True
            
            if t=='live':
                URL=build_url({'mode':'playTV','cid':cid})
                isF=False
                isP='true'
                plot=epgLive(epgData,cid)
                
            elif t=='replay':
                if cu==0:
                    show=False
                URL=build_url({'mode':'calendar','cid':cid,'cu':str(cuTime)})
                isF=True
                isP='false'
                plot=''
            
            if show:
                iL={'title': name,'sorttitle': name,'plot': plot}
                setArt={'thumb': img, 'poster': img, 'banner': '', 'icon': img, 'fanart':fanart}
                addItemList(URL, name, setArt, 'video', iL, isF, isP)
        
        xbmcplugin.endOfDirectory(addon_handle)
        xbmcplugin.addSortMethod(handle=addon_handle,sortMethod=xbmcplugin.SORT_METHOD_TITLE)
    else:
        toMainMenu()

def calendar(cid,cu):
    now=datetime.datetime.now()
    cd=int(int(cu)/(24*60*60))+1
    for i in range(0,cd): 
        date=(now-datetime.timedelta(days=i*1)).strftime('%Y-%m-%d')
        
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': 'DefaultYear.png', 'fanart':fanart}
        url=build_url({'mode':'programList','cid':cid,'date':date,'cu':cu})
        addItemList(url, date, setArt, 'video')
    xbmcplugin.endOfDirectory(addon_handle)

def programList(cid,date,cu):
    d=fromStrToDate(date,'%Y-%m-%d')
    d1=d+datetime.timedelta(days=1)
    s=date.replace('-','')+'000000'
    e=fromDateToStr(d1,'%Y%m%d000000')
    epgData=epgALL(s,e)
    
    progsAr=[c['programs'] for c in epgData if c['channel_uuid']==cid]
    if len(progsAr)>0:
        progs=progsAr[0]
        
        def sortFN(i):
            return i['since']
        progs.sort(key=sortFN,reverse=False)
        for p in progs:
            now=datetime.datetime.now()
            cuTime=now-datetime.timedelta(seconds=int(cu))
            tStart=fromStrToDate(p['since'],'%Y-%m-%d %H:%M:%S')
            tEnd=fromStrToDate(p['till'],'%Y-%m-%d %H:%M:%S')
            if 'catchup' in p:
                if p['catchup'] and tStart<=now and tStart>cuTime:
                    title=p['title'] if 'title' in p else '...'
                    pid=p['uuid']
                    ts=fromDateToStr(tStart,'%H:%M')
                    te=fromDateToStr(tEnd,'%H:%M')
                    titleToList='[B]%s - %s[/B] %s'%(ts,te,title)
                    desc=p['description_short'] if 'description_short' in p else ''
                    genre=[p['category']] if 'category' in p else []
                    country=[p['country']] if 'country' in p else []
                    year=p['date'] if 'date' in p else 0
                    if year==None:
                        year=0
                    rating=str(p['pc_rating']) if 'pc_rating' in p else ''
                    try:
                        img=p['images']['cover'][0]['url']
                    except:
                        img=img_addon
                    
                    iL={'title': title,'sorttitle': title,'mpaa':rating,'plotoutline':desc,'plot': desc,'year':year,'genre':genre,'country':country,'mediatype':'movie'}
                    setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart':fanart}
                    url=build_url({'mode':'playReplay','cid':cid,'pid':pid})
                    addItemList(url, titleToList, setArt, 'video', iL, False, 'true')

    xbmcplugin.setContent(addon_handle, 'videos')    
    xbmcplugin.endOfDirectory(addon_handle)

def playSource(cid,pid=None,live=True,s=None,e=None,vod=False,trailer=False):
    if addon.getSetting('logged')=='true':
        
        #delete last session
        sess=addon.getSetting('videoSessionId')
        if sess!='':
            url=apiURL+'player/videosession/'+sess
            paramsURL=genParams()
            resp=req('delete',url,genHea(),paramsURL)
            if resp!=None:
                xbmc.log('@@@wyrejestrowanie sesji: '+str(resp), level=xbmc.LOGINFO)
            else:
                xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
                toMainMenu()
                return
            
        #session
        url=apiURL+'player/product/'+cid+'/configuration'#c2b8cd8a-395f-4607-8664-e8086d4d9c25/configuration?platform=ANDROID_TV&type=channel'
        paramsURL=genParams()
        paramsURL['type']='channel' if not vod else 'vod'
        if trailer:
            paramsURL['type']='vod'
            paramsURL['videoId']=pid
        if pid!=None and not trailer:
            paramsURL['programId']=pid
        resp=req('get',url,genHea(),paramsURL)
        if resp==None:
            xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
            toMainMenu()
            return
        else:
            if 'videoSession' in resp:
                videoSessionId=resp['videoSession']['videoSessionId']
                addon.setSetting('videoSessionId',videoSessionId)
            
                #data
                url=apiURL+'player/product/'+cid+'/playlist'#c2b8cd8a-395f-4607-8664-e8086d4d9c25/playlist
                paramsURL=genParams()
                paramsURL['videoSessionId']=videoSessionId
                if not vod:
                    paramsURL['type']='LIVE' if pid==None else 'CATCHUP'
                if trailer:
                    paramsURL['type']='channel'
                else:
                    paramsURL['type']='vod'
                resp=req('get',url,genHea(),paramsURL)
                if resp==None:
                    xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
                    toMainMenu()
                    return
                else:
                    xbmc.log('@@@SUBTITLES: '+str(resp['subtitles']), level=xbmc.LOGINFO)
                    xbmc.log('@@@STREAM_DATA: '+str(resp), level=xbmc.LOGINFO)
                    manifest=resp['sources']['DASH'][0]['src']
                    if manifest.startswith('//'):
                        manifest='https:'+manifest
                    
                    if live==False and s!=None and not vod and not trailer: #SC catchup
                        co=int(addon.getSetting('cuOffset'))*60*60
                        ts=int(fromStrToDate(s,'%Y-%m-%dT%H:%M:%S').timestamp())+co
                        te=int(fromStrToDate(e,'%Y-%m-%dT%H:%M:%S').timestamp())+co
                        manifest=manifest.replace('mode=normal','mode=catchup')+'&begin='+str(ts)
                        if int(time.time())>te:
                            manifest+='&end='+str(te)
                        
                    
                    licURL=resp['drm']['WIDEVINE']
                    if licURL.startswith('//'):
                        licURL='https:'+licURL
                    heaLic=genHea()
                    heaLic['Content-Type']=''
                    licKey='%s|%s|R{SSM}|'%(licURL,urlencode(heaLic))
                    #K22
                    drm_config={
                        "com.widevine.alpha": {
                            "license": {
                                "server_url": licURL,
                                "req_headers": urlencode(heaLic)
                            }
                        }
                    }
                    
                    isLive=True if live or (live==False and pid==None and s==None and not vod and not trailer) else False
                    
                    ISAplayer('mpd', manifest, DRM=True, licKey=licKey, drm_config=drm_config, hea=genHea(), live=isLive)
                
            else:
                xbmc.log('@@@błąd ustanowienia sesji: '+str(resp), level=xbmc.LOGINFO)
                info='Nie można ustanowić sesji'
                if 'message' in resp:
                    message=resp['message']
                    if message=='Must be in local':
                        info='Dostępny tylko w sieci operatora'
                    elif message=='Resource not in subscriber products':
                        info='Brak w pakiecie'
                    else:
                        info=message
                xbmcgui.Dialog().notification('TV SMART GO', info, xbmcgui.NOTIFICATION_INFO)
                xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
        
    else:
        xbmcgui.Dialog().notification('TV SMART GO', 'Zaloguj się we wtyczce TV SMART GO', xbmcgui.NOTIFICATION_INFO)


def generate_m3u():
    file_name = addon.getSetting('fname')
    path_m3u = addon.getSetting('path_m3u')
    if file_name == '' or path_m3u == '':
        xbmcgui.Dialog().notification('TV SMART GO', 'Ustaw nazwę pliku oraz katalog docelowy.', xbmcgui.NOTIFICATION_ERROR)
        return
    xbmcgui.Dialog().notification('TV SMART GO', 'Generuję liste M3U.', xbmcgui.NOTIFICATION_INFO)
    data = '#EXTM3U\n'
    dataE2 = '' #j00zek for E2 bouquets
    
    channels=channelsGen()
    if channels!=None:
        for c in channels:
            cid=c['uuid']
            name=c['title']
            img=c['images']['logo'][0]['url']
            cuTime=int(c['context']['catch_up_time']/(24*60*60))
            cu=c['context']['catch_up_active']
            if cu==1:
                data += '#EXTINF:0 tvg-id="%s" tvg-logo="%s" group-title="TV Smart Go" catchup="append" catchup-source="&s={utc:Y-m-dTH:M:S}&e={utcend:Y-m-dTH:M:S}" catchup-days="%s",%s\nplugin://plugin.video.tv_smart_go?mode=tv&cid=%s\n' %(name,img,str(cuTime),name,cid)
                dataE2 += 'plugin.video.tv_smart_go/addon.py%3fmode=tv&cid=' + '%s:%s\n' % (cid, name) #j00zek for E2 bouquets
            else:
                data += '#EXTINF:0 tvg-id="%s" tvg-logo="%s" group-title="TV Smart Go" ,%s\nplugin://plugin.video.tv_smart_go?mode=playTV&cid=%s\n' %(name,img,name,cid)
                dataE2 += 'plugin.video.tv_smart_go/addon.py%3fmode=playTV&cid=' + '%s:%s\n' % (cid, name) #j00zek for E2 bouquets

        f = xbmcvfs.File(os.path.join(path_m3u, file_name), 'w')
        f.write(data)
        f.close()
        xbmcgui.Dialog().notification('TV SMART GO', 'Wygenerowano listę M3U.', xbmcgui.NOTIFICATION_INFO)

        f = xbmcvfs.File(os.path.join(path_m3u, 'iptv.e2b'), 'w') #j00zek for E2 bouquets
        f.write(dataE2)
        f.close()
        xbmcgui.Dialog().notification('TV SMART GO', 'Wygenerowano listę E2B', xbmcgui.NOTIFICATION_INFO)

    else:
        toMainMenu()

def vod_cat():
    items=[
        ['Filmy','vod'],
        ['Seriale','series']
    ]
    for i in items:
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': 'DefaultAddonVideo.png', 'fanart':fanart}
        url=build_url({'mode':'vodList','type':'vod','subtype':i[1],'limit':'100'})
        addItemList(url, i[0], setArt)
        
    xbmcplugin.endOfDirectory(addon_handle)    

def vod(t):
    url=apiURL+'sections/page/'+t
    paramsURL=genParams()
    resp=req('get',url,genHea(),paramsURL)
    if resp!=None:
        for r in resp:
            title=r['name']
            sid=r['id']
            limit=str(r['main_limit'])
            
            setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': 'DefaultAddonVideo.png', 'fanart':fanart}
            url=build_url({'mode':'vodList','type':'section','sid':str(sid),'limit':limit})
            
            addItemList(url, title, setArt)

        xbmcplugin.setContent(addon_handle, 'videos')    
        xbmcplugin.endOfDirectory(addon_handle)
            
    else:
        toMainMenu()

def contDetails(x,t,season=None): #helper
    title=x['title']
    titleOrg=x['title_org'] if 'title_org' in x else ''
    descShort=x['short_desc'] if 'short_desc' in x else ''
    if descShort=='':
        descShort=x['summary_short'] if 'summary_short' in x else ''
    desc=descShort
    rating=str(x['rating']) if 'rating' in x else '' #mpaa
    if 'genres' in x:
        genre=[c['name'] for c in x['genres']] if x['genres']!=None in x else []
    else:
        genre=[]
    year=x['year'] if 'year' in x else 0
    if year==None:
        year=0
    country=[x['country']] if 'country' in x else []#
    provider=[x['provider']] if 'provider' in x else []#
    dur=x['duration'] if 'duration' in x else 0
    actors=[]
    directors=[]
    writers=[]
    
    if 'metadata' in x:
        xx=x['metadata']
        title=xx['title']
        titleOrg=xx['title_org'] if 'title_org' in xx else ''
        actors=xx['actors'] if 'actors' in xx else []
        directors=xx['directors'] if 'directors' in xx else []
        writers=xx['writers'] if 'writers' in xx else []
        year=xx['year'] if 'year' in xx else 0
        rating=str(xx['rating']) if 'rating' in xx else '' #mpaa
        desc=xx['summary_long'] if 'summary_long' in xx else ''
        descShort=xx['summary_short'] if 'summary_short' in xx else ''
        dur=xx['duration'] if 'duration' in xx else 0
        country=xx['country_of_origin'] if 'country_of_origin' in xx else ''#
    
    try:
        rentPeriod=x['prices']['rent']['period']
        rentPrice=x['prices']['rent']['price']/100
        toDesc='[B]Wypożyczalnia: [/B]%s PLN na %s godz.'%(str(rentPrice),str(rentPeriod))
        descShort='%s\n\n%s'%(toDesc,descShort)
        desc='%s\n%s'%(toDesc,desc)
    except:
        pass
    
    try:
        trId=x['previews']['preview'][0]['videoAssetId']
        trailerPath=build_url({'mode':'playTrailer','cid':x['uuid'],'vid':str(trId)})
    except:
        trailerPath=None
        
    if t=='vod':
        type='movie'
    elif t=='series':
        type='tvshow'
    elif t=='season':
        type='season'
    elif t=='episode':
        type='episode'
    else:
        print(t)
        
    iL={'title': title,'originaltitle':titleOrg,'sorttitle': title,'studio':provider,'mpaa':rating,'plotoutline':descShort,'plot': desc,'year':year,'genre':genre,'duration':dur,'director':directors,'country':country,'cast':actors,'writer':writers,'trailer':trailerPath,'mediatype':type}
    
    if t=='season':
        iL['season']=x['number']
    
    if t=='episode':
        iL['season']=int(season)
        iL['episode']=x['number']
    
    return iL

def addVodItem(r): #helper
    if r['type']=='vod':
        conType=r['subtype']
        try:
            img=r['images']['poster'][0]['url']
        except:
            img=img_addon
        vid=r['uuid']
        
        iL=contDetails(r,conType)
        setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart':fanart}
        
        if conType=='vod':
            url=build_url({'mode':'playVOD','vid':vid})
            isF=False
            isP='true'
        
        elif conType=='series':
            url=build_url({'mode':'seasonList','sid':vid})
            isF=True
            isP='false'
        
        title=iL['title']
        if 'available_in' in r:
            if r['available_in']!=None:
                products=eval(addon.getSetting('products'))
                if availCheck(products,r['available_in']):
                    title='[B]%s[/B]'%(title)
        
        addItemList(url, title, setArt, 'video', iL, isF, isP)
    
sortVOD={
    'sortVODtype':{'name':'Sortowanie wg','vals':{'tytuł':'title','data dodania':'created_at','rok produkcji':'year'},'default':'tytuł','currentVal':''},
    'sortVODdir':{'name':'Kier. sortowania','vals':{'rosnąco':'asc','malejąco':'desc'},'default':'rosnąco','currentVal':''}
}

def setSortVOD(f): #helper
    sortData=sortVOD[f]
    v=addon.getSetting(f)
    v=sortData['default'] if v=='' else v
    
    select=xbmcgui.Dialog().select('%s:'%(sortData['name']), list(sortData['vals']))
    if select>-1:
        new_v=list(sortData['vals'])[select]
    else:
        new_v=v

    if new_v!=v:
        addon.setSetting(f,new_v)
        xbmc.executebuiltin('Container.Refresh()')
    
def vodList(sid,limit,p,type,subtype,genre):
    if type=='section':
        url=apiURL+'sections/'+sid+'/content'
    elif type=='vod':
        url=apiURL+'products/vod'
    
    paramsURL=genParams()
    paramsURL['limit']=limit
    pg=int(p)if p!=None else 1
    offset=(pg-1)*int(limit)
    paramsURL['offset']=str(offset)
    if type=='vod':
        if genre!=None:
            paramsURL['genre']=genre
        if subtype!=None:
            paramsURL['subtype']=subtype
        
        #sort        
        for f in sortVOD:
            sortData=sortVOD[f]
            v=addon.getSetting(f)
            sortVOD[f]['currentVal']=sortData['default'] if v=='' else v
        
        if p==None:
            for f in sortVOD:
                sortData=sortVOD[f]
                
                tit='[COLOR=cyan][B]%s: [/B][/COLOR]%s'%(sortData['name'],sortData['currentVal'])
                setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': 'DefaultTags.png', 'fanart':fanart}
                URL=build_url({'mode':'setSortVOD','type':f})
                addItemList(URL, tit, setArt, isF=False)
                
        sT=sortVOD['sortVODtype']['currentVal'] 
        sD=sortVOD['sortVODdir']['currentVal'] 
        paramsURL['order']=sortVOD['sortVODtype']['vals'][sT] 
        paramsURL['orderDir']=sortVOD['sortVODdir']['vals'][sD] 
        
    resp=req('get',url,genHea(),paramsURL)
    if resp!=None:
        for r in resp['data']:
            addVodItem(r)

        #baners,channels
        if len([r for r in resp['data'] if r['type']=='vod'])==0 and p==None:
            for r in resp['data']:
                if r['type']=='channel':
                    cid=r['uuid']
                    name=r['title']
                    img=r['images']['logo'][0]['url']
                                        
                    URL=build_url({'mode':'playTV','cid':cid})
                    setArt={'thumb': img, 'poster': img, 'banner': '', 'icon': img, 'fanart':fanart}
                    addItemList(URL, name, setArt, 'video', isF=False, isPla='true')
                    
                    
                else:
                    title=r['title']
                    urlCont=r['context']['url_mobile']
                    if 'genre=' in urlCont:
                        genreId=r['context']['url_mobile'].split('genre=')[-1]
                        url=build_url({'mode':'vodList','type':'vod','genre':genreId,'limit':'100'})
                    elif '/section/' in urlCont:
                        sectionId=re.compile('/section/([^/]+?)/').findall(urlCont)[0]
                        url=build_url({'mode':'vodList','type':'section','sid':sectionId,'limit':'100'})
                    try:
                        img=r['images']['cover'][0]['url']
                    except:
                        img=img_addon
                    
                    setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart':fanart}
                    addItemList(url, title, setArt)
        
        nextPageTest=False
        if len([r for r in resp['data'] if r['type']=='vod'])==int(limit) and type=='section':
            nextPageTest=True
        if type=='vod':
            if resp['total']==len(resp['data']): #resp['total']>offset+len(resp['data']):
               nextPageTest=True 
        
        if nextPageTest:
            setArt={'icon': img_empty}
            
            sid=sid if sid!=None else ''
            subtype=subtype if subtype!=None else ''
            genre=genre if genre!=None else ''
            
            url=build_url({'mode':'vodList','type':type,'sid':sid,'subtype':subtype,'genre':genre,'limit':limit,'page':str(pg+1)})
            addItemList(url, '[B][COLOR=yellow]>>> następna strona[/COLOR][/B]', setArt, 'video')
        
        xbmcplugin.setContent(addon_handle, 'videos')    
        xbmcplugin.endOfDirectory(addon_handle)
        
    else:
        toMainMenu()
    
def seasonList(sid):
    url=apiURL+'products/series/'+sid
    paramsURL=genParams()
    resp=req('get',url,genHea(),paramsURL)

    if resp!=None:
        for r in resp['seasons']:
            iL=contDetails(r,'season')
            img=resp['images']['poster'][0]['url']
            saveF(PATH_profile+'series_img.txt',img)
            seasNo=str(r['number'])
            
            setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart':fanart}
            url=build_url({'mode':'epList','seasonId':r['uuid'],'seasonNo':seasNo})
            addItemList(url, 'Sezon '+ seasNo, setArt, 'video', iL)
        
        xbmcplugin.setContent(addon_handle, 'videos')    
        xbmcplugin.endOfDirectory(addon_handle)
    else:
        toMainMenu()
        
def epList(sid,n):
    url=apiURL+'products/season/'+sid
    paramsURL=genParams()
    resp=req('get',url,genHea(),paramsURL)
    if resp!=None:
        for r in resp['episodes']:
            iL=contDetails(r,'episode',n)
            img=openF(PATH_profile+'series_img.txt')
            
            setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart':fanart}
            url=build_url({'mode':'playVOD','vid':r['uuid']})
            addItemList(url, iL['title'] , setArt, 'video', iL, False, 'true')
            
        xbmcplugin.setContent(addon_handle, 'videos')    
        xbmcplugin.endOfDirectory(addon_handle)
    
    else:
        toMainMenu()
        
def rent_vod():
    url=apiURL+'subscriber/payments'
    paramsURL=genParams()
    resp=req('get',url,genHea(),paramsURL)
    now=datetime.datetime.now()
    if resp!=None:
        vods=[v for v in resp['data'] if v['product_type']=='vod' and fromStrToDate(v['expiration_date'],'%Y-%m-%d %H:%M:%S')>=now]
        for v in vods:
            title=v['product_title']
            vid=v['product_uuid']
            
            iL={'title': title,'plot':title,'mediatype':'movie'}
            setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': 'DefaultAddonVideo.png', 'fanart':fanart}
            url=build_url({'mode':'playVOD','vid':vid})
            addItemList(url, title, setArt, 'video', iL, False, 'true')

        xbmcplugin.setContent(addon_handle, 'videos')    
        xbmcplugin.endOfDirectory(addon_handle)
        
    else:
        toMainMenu()
        
def searchRes(q,p):
    p=int(p) if p!=None else 1
    limit='100'
    offset=(p-1)*int(limit)
    
    url=apiURL+'products/search'
    paramsURL=genParams()
    paramsURL.update({'q':q,'limit':limit,'offset':str(offset),'language':'pl'})
    resp=req('get',url,genHea(),paramsURL)

    if resp!=None:
        for r in resp['data']:
            addVodItem(r)
            
        if resp['total']>offset+len(resp['data']):
            setArt={'icon': img_empty}
            url=build_url({'mode':'searchRes','q':q,'page':str(p+1)})
            addItemList(url, '[B][COLOR=yellow]>>> następna strona[/COLOR][/B]', setArt, 'video')
        
        xbmcplugin.setContent(addon_handle, 'videos')    
        xbmcplugin.endOfDirectory(addon_handle)
    else:
        toMainMenu()

    
    
 
mode = params.get('mode', None)

if not mode:
    productsUpdate()
    main_menu()
    device_id=addon.getSetting('device_id')
    if device_id=='' or device_id==None:
        addon.setSetting('device_id',code_gen(16))
    
else:
    if mode=='login':
        login()
        toMainMenu()
        
    if mode=='logout':
        logout()
        toMainMenu()
        
    if mode=='live' or mode=='replay':
        tvList(mode)
    
    if mode=='chanGenres':
        chanGenres()
    
    if mode=='calendar':
        cid=params.get('cid')
        cu=params.get('cu')
        calendar(cid,cu)
    
    if mode=='programList':
        cid=params.get('cid')
        date=params.get('date')
        cu=params.get('cu')
        programList(cid,date,cu)
        
    if mode=='playTV':
        cid=params.get('cid')
        playSource(cid,live=True)
    
    if mode=='tv': #z SC
        cid=params.get('cid')
        s=params.get('s')
        e=params.get('e')
        playSource(cid,live=False,s=s,e=e)
    
    if mode=='playReplay':
        cid=params.get('cid')
        pid=params.get('pid')
        playSource(cid,pid,live=False)
    
    if mode=='BUILD_M3U':
        if addon.getSetting('logged')=='true':
            generate_m3u()
        else:
            xbmcgui.Dialog().notification('TV SMART GO', 'Operacja wymaga zalogowania', xbmcgui.NOTIFICATION_INFO)
    
    if mode=='KIDS' or mode=='VOD':
        vod(mode+'_ATV')
    
    if mode=='vod':
        vod_cat()
    
    if mode=='setSortVOD':
        type=params.get('type')
        setSortVOD(type)
    
    if mode=='vodList':
        sid=params.get('sid')
        type=params.get('type')
        subtype=params.get('subtype')
        limit=params.get('limit')
        page=params.get('page')
        genre=params.get('genre')
        vodList(sid,limit,page,type,subtype,genre)
        
    if mode=='seasonList':
        sid=params.get('sid')
        seasonList(sid)
    
    if mode=='epList':
        seasonId=params.get('seasonId')
        seasonNo=params.get('seasonNo')
        epList(seasonId,seasonNo)
        
    if mode=='playTrailer':
        cid=params.get('cid')
        vid=params.get('vid')
        playSource(cid,vid,live=False,trailer=True)
        
    
    if mode=='rent_vod':
        rent_vod()
    
    if mode=='playVOD':
        vid=params.get('vid')
        playSource(vid,live=False,vod=True)
        
    if mode=='search':
        query = xbmcgui.Dialog().input('Szukaj:', type=xbmcgui.INPUT_ALPHANUM)
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
        if query:
            xbmc.executebuiltin('Container.Update(plugin://plugin.video.tv_smart_go/?mode=searchRes&q='+quote(query)+')')
        else:
            xbmc.executebuiltin('Container.Update(plugin://plugin.video.tv_smart_go/,replace)')

    if mode=='searchRes':
        q=params.get('q')
        page=params.get('page')
        searchRes(q,page)
        