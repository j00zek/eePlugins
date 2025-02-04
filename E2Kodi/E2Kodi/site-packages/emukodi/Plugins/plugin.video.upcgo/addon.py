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
from urllib.parse import urlencode, quote_plus, quote, unquote, parse_qsl

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon(id='plugin.video.upcgo')
PATH=addon.getAddonInfo('path')
PATH_profile=xbmcvfs.translatePath(addon.getAddonInfo('profile'))
img_empty=PATH+'resources/img/empty.png'
img_tick=PATH+'resources/img/tick.png'
fanart=PATH+'resources/img/fanart.jpg'
img_addon=PATH+'icon.png'
file_name = addon.getSetting('fname')
path_m3u = addon.getSetting('path_m3u')


baseurl='https://www.upctv.pl/'
apiURL='https://spark-prod-pl.gnp.cloud.upctv.pl/'
EPGapiURL='https://staticqbr-prod-pl.gnp.cloud.upctv.pl/pol/web/epg-service-lite/pl/pl/events/segments/'
IMGapiURL='https://staticqbr-prod-pl.gnp.cloud.upctv.pl/image-service/intent'
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'

def build_url(query):
    return base_url + '?' + urlencode(query)

def addItemList(url, name, setArt, medType=False, infoLab={}, isF=True, isPla='false', contMenu=False, cmItems=[]):
    li=xbmcgui.ListItem(name)
    li.setProperty("IsPlayable", isPla)
    if medType:
        kodiVer=xbmc.getInfoLabel('System.BuildVersion')
        if 1: #j00zek to satisfy emukodi kodiVer.startswith('19.'):
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
    
def openJSON(u):
    try:
        f=open(u,'r',encoding = 'utf-8')
    except:
        f=open(u,'w+',encoding = 'utf-8')
    cont=f.read()
    f.close()
    try:
        js=json.loads(cont)
    except:
        js=[]
    return js
    
def saveJSON(u,j):
    with open(u, 'w', encoding='utf-8') as f:
        json.dump(j, f, ensure_ascii=False, indent=4)

def accessToken_refresh(): #rozważyć w zamian funkcję weryfikującą odpowiedź zapytania -> accessToken_refresh() byłby stosowany w razie odpowiedzi 401
    def accTknRefr():
        hea={
            'User-Agent':UA,
            'Referer':baseurl,
        }
        data={
            'refreshToken':addon.getSetting('x_refresh_token'),
            'username':addon.getSetting('x_oesp_username')
        }
        cookies={
            'ACCESSTOKEN':addon.getSetting('accessToken'),
            'CLAIMSTOKEN':addon.getSetting('CLAIMSTOKEN')
        }
        url=apiURL+'auth-service/v1/authorization/refresh'
        resp=requests.post(url,headers=hea,cookies=cookies,json=data).json()
        return resp
    
    resp=accTknRefr()
    if 'error' in resp:
        logOut()
        logIn()
        print('refreshToken wygasł->PRZELOGOWANIE')
        resp_new=accTknRefr()
        if 'error' in resp_new:
            xbmcgui.Dialog().notification('UPC GO', 'Błąd: (Refresh AccTkn) '+resp_new['error']['message'], xbmcgui.NOTIFICATION_INFO)
            xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
        else:
            addon.setSetting('accessToken',resp_new['accessToken'])
            addon.setSetting('x_refresh_token',resp_new['refreshToken'])
            return resp_new['accessToken']
    else:
        addon.setSetting('accessToken',resp['accessToken'])
        addon.setSetting('x_refresh_token',resp['refreshToken'])
        return resp['accessToken']

def claimsToken_refresh():
    claimstoken=addon.getSetting('CLAIMSTOKEN')
    start=addon.getSetting('claimsToken_start')
    if start=='':
        start='0'
    now=int(time.time())
    if now-int(start)>=24*60*60:
        url=apiURL+'pol/web/personalization-service/v1/customer/'+addon.getSetting('x_cus')+'?with=profiles,devices&advertisementDeviceId='+addon.getSetting('advertisementDeviceId')
        hea={
            'User-Agent':UA,
            'Referer':baseurl,
            #'X-cus':addon.getSetting('x_cus'),
            'x-go-dev':addon.getSetting('x_go_dev'),
            'X-OESP-Username':addon.getSetting('x_oesp_username')
        }
        cookies={
            'ACCESSTOKEN':addon.getSetting('accessToken')#accessToken_refresh()
        }
        resp=requests.get(url,headers=hea,cookies=cookies)
        resp_cooks=dict(resp.cookies)
        if 'CLAIMSTOKEN' in resp_cooks:
            claimstoken=resp_cooks['CLAIMSTOKEN']
            addon.setSetting('CLAIMSTOKEN',claimstoken)
            addon.setSetting('claimsToken_start',str(now))
            print('CLAIMSTOKEN refresh')
    
    return claimstoken
    
def getCookies():
    c={
        'ACCESSTOKEN':accessToken_refresh(),
        'CLAIMSTOKEN':claimsToken_refresh()
    }
    return c

def home():
    addon.setSetting('proxy','false') #było true
    addon.setSetting('proxyReplay','false') #było true
    status=addon.getSetting('status')
    if status=='loggedIn':
        items=[
            ['Telewizja','menu_tv','DefaultTVShows.png'],
            ['Radio','radio','DefaultMusicSongs.png'],
            ['VOD','vod_categ','DefaultAddonVideo.png'],
            ['Wyszukiwarka VOD','search_vod','DefaultAddonsSearch.png'],
            ['Wyloguj','logOut','DefaultUser.png']
        ]
    else:
        items=[
            ['Zaloguj','logIn','DefaultUser.png']
        ]

    for i in items:
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': i[2], 'fanart':fanart}
        url = build_url({'mode':i[1]})
        addItemList(url, i[0], setArt)
    xbmcplugin.endOfDirectory(addon_handle)

def menu_tv():
    if addon.getSetting('isReplay')=='true':
        items=[
            ['Kanały na żywo','liveTV','DefaultTVShows.png'],
            ['Kanały na żywo wg kategorii','categTV','DefaultTVShows.png'],
            ['Replay TV','replayTV','DefaultYear.png'],
            ['Wyszukiwarka Replay TV','search_replayTV','DefaultAddonsSearch.png']
        ]
    else:
        items=[
            ['Kanały na żywo','liveTV','DefaultTVShows.png'],
            ['Kanały na żywo wg kategorii','categTV','DefaultTVShows.png']
        ]
    for i in items:
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': i[2], 'fanart':fanart}
        url = build_url({'mode':i[1]})
        addItemList(url, i[0], setArt)
    xbmcplugin.endOfDirectory(addon_handle)

def logIn():
    if addon.getSetting('x_go_dev')=='':
        print('Generuję GUID urządzenia')
        addon.setSetting('x_go_dev',code_gen(8)+'-'+code_gen(4)+'-'+code_gen(4)+'-'+code_gen(4)+'-'+code_gen(12))
        addon.setSetting('x_drm_device_id',code_gen(64)) #spr czy nie jest stały
        addon.setSetting('x_tracking_id',code_gen(64))
        addon.setSetting('advertisementDeviceId',code_gen(8)+'-'+code_gen(4)+'-'+code_gen(4)+'-'+code_gen(4)+'-'+code_gen(12)) #NEW
    if addon.getSetting('username')!='' and addon.getSetting('password')!='':
        hea={
            'User-Agent':UA,
            'Referer':baseurl,
            'X-Device-Code':'web',
            'x-go-dev':addon.getSetting('x_go_dev'),
            'X-Profile':'anonymous'
        }
        data={
            "password": addon.getSetting('password'),
            #"stayLoggedIn": False,
            "username": addon.getSetting('username')
        }
        url=apiURL+'auth-service/v1/authorization'
        resp=requests.post(url,headers=hea,json=data).json()
        if 'username' not in resp:
            if 'error' in resp:
                print('ok')
                if resp['error']['message']=='Invalid credentials':
                    xbmcgui.Dialog().notification('UPC GO', 'Błędne dane logowania', xbmcgui.NOTIFICATION_INFO)
                elif resp['error']['message']=='Blacklisted':
                    xbmcgui.Dialog().notification('UPC GO', 'Dostęp zablokowany (np. z powodu braku płatności)', xbmcgui.NOTIFICATION_INFO)
                else:
                    xbmcgui.Dialog().notification('UPC GO', 'Błąd: '+resp['error']['message'], xbmcgui.NOTIFICATION_INFO)

        else:
            addon.setSetting('status','loggedIn')
            addon.setSetting('x_cus',resp['householdId'])
            addon.setSetting('x_oesp_username',resp['username'])
            addon.setSetting('x_refresh_token',resp['refreshToken'])
            addon.setSetting('accessToken',resp['accessToken'])

            url1=apiURL+'pol/web/personalization-service/v1/customer/'+addon.getSetting('x_cus')+'?with=profiles,devices&advertisementDeviceId='+addon.getSetting('advertisementDeviceId')
            hea={
                'User-Agent':UA,
                'Referer':baseurl,
                #'X-cus':addon.getSetting('x_cus'),
                'x-go-dev':addon.getSetting('x_go_dev'),
                'X-OESP-Username':addon.getSetting('x_oesp_username')
            }
            cookies={
                'ACCESSTOKEN':addon.getSetting('accessToken')#accessToken_refresh()
            }
            resp1=requests.get(url1,headers=hea,cookies=cookies)
            resp1_cooks=dict(resp1.cookies)
            resp1=resp1.json()
            addon.setSetting('cityId',str(resp1['cityId']))
            if 'assignedDevices' in resp1:
                addon.setSetting('x_profile',resp1['assignedDevices'][0]['defaultProfileId'])
                addon.setSetting('CLAIMSTOKEN',resp1_cooks['CLAIMSTOKEN']) #NEW
                addon.setSetting('claimsToken_start',str(int(time.time())))#NEW
            else:
                addon.setSetting('x_profile','anonymous')
                xbmcgui.Dialog().notification('UPC GO', 'Brak usługi UPC TV GO w umowie', xbmcgui.NOTIFICATION_INFO)

            #weryfikacja usługi ReplayTV w pakiecie
            url=apiURL+'pol/web/purchase-service/v2/customers/'+addon.getSetting('x_cus')+'/entitlements'
            hea={
                'User-Agent':UA,
                'Referer':baseurl,
                'X-cus':addon.getSetting('x_cus'),
                'x-go-dev':addon.getSetting('x_go_dev'),
                'X-OESP-Username':addon.getSetting('x_oesp_username'),
                'X-Profile':addon.getSetting('x_profile')
            }
            cookies={
                'ACCESSTOKEN':addon.getSetting('accessToken'),#accessToken_refresh()
                'CLAIMSTOKEN':addon.getSetting('CLAIMSTOKEN')
            }
            resp=requests.get(url,headers=hea,cookies=cookies).json()
            addon.setSetting('pakiet',str(resp['features']))
            '''
            if 'replaytv' in resp['features'] or 'TVOD' in resp['features']:
                addon.setSetting('isReplay','true')
            else:
                addon.setSetting('isReplay','false')
            '''
            addon.setSetting('isReplay','true')

    else:
        xbmcgui.Dialog().notification('UPC GO', 'Podaj login i hasło w Ustawieniach', xbmcgui.NOTIFICATION_INFO)

def channels_gen():#
    x_cus=addon.getSetting('x_cus')
    x_go_dev=addon.getSetting('x_go_dev')
    x_oesp_username=addon.getSetting('x_oesp_username')
    x_profile=addon.getSetting('x_profile')

    #pakiety
    url=apiURL+'pol/web/purchase-service/v2/customers/'+x_cus+'/entitlements'
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
        'X-cus':x_cus,
        'x-go-dev':x_go_dev,
        'X-OESP-Username':x_oesp_username,
        'X-Profile':x_profile
    }
    cookies=getCookies()
    resp=requests.get(url,headers=hea,cookies=cookies).json()
    addon.setSetting('x_entitlements_token',resp['token'])
    ent=[]
    for r in resp['entitlements']:
        ent.append(r['id'])

    def check_ent(x,y):
        c=False
        for yy in y:
            if yy in x:
                c=True
                break
        return c

    #lista kanałów
    cityId=addon.getSetting('cityId')
    url=apiURL+'pol/web/linear-service/v2/channels?cityId='+cityId+'&language=pl&productClass=Orion-DASH'
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
        'x-go-dev':x_go_dev,
        'X-OESP-Username':x_oesp_username,
        'X-Profile':x_profile
    }

    cookies=getCookies()
    
    resp=requests.get(url,headers=hea).json()
    channels=[]
    for r in resp:
        if r['locator']!=None:
            if 'dubel' not in r['id'] and check_ent(ent,r['linearProducts']):
                name=r['name']
                lcn=r['logicalChannelNumber']
                cid=r['id']
                logo=r['logo']['focused']
                if 'genre' in r:
                    categ=r['genre'][0]
                else:
                    categ='Inne'
                loc=r['locator']
                rd=0
                if 'replayProducts' in r:
                    durReplay=[]
                    for d in r['replayProducts']:
                        durReplay.append(d['replayDuration'])
                        if len(durReplay)>0:
                            rd=max(durReplay)
                channels.append([name,lcn,cid,logo,categ,loc,rd])

    fURL=PATH_profile+'channels.json'
    saveJSON(fURL,channels)

def getSchedule(): #EPG
    #d_utc=datetime.datetime.utcnow() #j00zek deprecated
    d_utc=datetime.datetime.now(datetime.UTC)
    ymd=d_utc.strftime('%Y%m%d')
    H=int(d_utc.strftime('%H'))
    partDay=6*int(H/6)

    epgData={}#
    i=1
    while i<=5:
        url=EPGapiURL+ymd+addZero(partDay)+'0000'
        hea={
            'User-Agent':UA,
            'Referer':baseurl
        }
        resp=requests.get(url,headers=hea).json()
        for e in resp['entries']:
            if e['channelId'] not in epgData:
                epgData[e['channelId']]=[]
            if 'events' in e:
                for ee in e['events']:
                    now=int(time.time())
                    if ee['endTime']>=now:
                        ts=datetime.datetime.fromtimestamp(ee['startTime']).strftime('%H:%M')
                        te=datetime.datetime.fromtimestamp(ee['endTime']).strftime('%H:%M')
                        if 'title' in ee:
                            title=ee['title']
                        else:
                            title='b/d'
                        test_dupl=0
                        for p in epgData[e['channelId']]:
                            if p[0]==ts and p[1]==te and p[2]==title:
                                test_dupl=1
                                break
                        if test_dupl==0:
                            epgData[e['channelId']].append([ts,te,title])
        i+=1
        partDay=partDay+6
        if partDay==24:
            partDay=0
            ymd=(datetime.datetime(*(time.strptime(ymd,'%Y%m%d')[0:6]))+datetime.timedelta(days=1)).strftime('%Y%m%d')

    return epgData

def listTV(m):
    if m=='liveTV':
        Mode='playLiveTV'
        isPlayable='true'
        isFolder=False
    elif m=='replayTV':
        Mode='calendar'
        isPlayable='false'
        isFolder=True
    channels_gen()

    fURL=PATH_profile+'channels.json'
    chns=openJSON(fURL)
    epg=''
    if addon.getSetting('epg')=='true' and m=='liveTV':
        epg=getSchedule()
    for c in chns:
        if ((m=='liveTV') or (m=='replayTV' and c[6]>0)):
            plot=''
            if epg!='' and c[2] in epg:
                for e in epg[c[2]]:
                   plot+='[B]'+e[0]+'[/B]  '+e[2]+'\n'

            iL={'title': c[0],'sorttitle': c[0],'plot': plot}
            setArt={'thumb': c[3], 'poster': c[3], 'banner': c[3], 'icon': c[3], 'fanart':c[3]}
            url = build_url({'mode':Mode,'chID':c[2],'repDur':str(c[6])})
            addItemList(url, c[0], setArt, 'video', iL, isFolder, isPlayable)
    
    xbmcplugin.addSortMethod(handle=addon_handle,sortMethod=xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.addSortMethod(handle=addon_handle,sortMethod=xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.endOfDirectory(addon_handle)
    
def addZero(x): #
    if x<=9:
        return '0'+str(x)
    else:
        return str(x)

def urlEPG(t): #url do EPG dla timestamp (podział wg czasu GMT!!!)
    d=time.gmtime(t)
    date=str(d[0])+addZero(d[1])+addZero(d[2])
    return EPGapiURL+date+addZero(6*int(d[3]/6))+'0000'

def getCrid(chID):#ID event (programu/audycji)
    now=int(time.time())
    hea={
        'User-Agent':UA,
        'Referer':baseurl
    }
    resp=requests.get(urlEPG(now),headers=hea).json()
    id_prog=''
    for e in resp['entries']:
        if e['channelId']==chID:
            for p in e['events']:
                if now>=p['startTime'] and now<=p['endTime']:
                    id_prog=p['id']
                    break
    return id_prog

def schemeIdUri_gen(u):#
    hea={
        'User-Agent':UA,
        'Referer':baseurl
    }
    resp=requests.get(u,headers=hea).text
    try:
        uuid=re.compile('schemeIdUri=\"urn:uuid:([^\"]+?)\">').findall(resp)[0]
    except:
        uuid=re.compile('schemeIdUri=\"urn:uuid:([^\"]+?)\" cenc:').findall(resp)[0]
    return uuid

def tsURL(): #NEW
    now=datetime.datetime.now()
    ms=now.astimezone().strftime('%f')
    ms=str(int(int(ms)/1000))
    tz=now.astimezone().strftime('%z')
    tz=tz[:-2]+':'+tz[-2:]
    s=now.astimezone().strftime('%Y-%m-%dT%H:%M:%S.'+ms+tz)
    return s

def getStreamToken(cID):#
    if addon.getSetting('x_streaming_token')!='': #wyrejestrowanie ostatnio użytego tokena (x-streaming-token)
        killStreamToken()
    x_cus=addon.getSetting('x_cus')
    x_profile=addon.getSetting('x_profile')
    crid=getCrid(cID)
    url=apiURL+'pol/web/session-service/session/v2/web-desktop/customers/'+x_cus+'/live?channelId='+cID+'&eventId='+crid+'&assetType=Orion-DASH&profileId='+x_profile+'&liveContentTimestamp='+quote(tsURL())
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
        #'X-Drm-Device-Id':addon.getSetting('x_drm_device_id'),
        'X-Entitlements-Token':addon.getSetting('x_entitlements_token'),
        'x-go-dev':addon.getSetting('x_go_dev'),
        'X-OESP-Username':addon.getSetting('x_oesp_username'),
        'X-Profile':x_profile,
        'x-ui-language':'pl'
    }
    cookies=getCookies()
    resp=requests.post(url,headers=hea,cookies=cookies)
    respp=resp.content.decode('UTF-8')
    if 'error' in respp: #2022-10-14
        if '\"statusCode\":1111' in respp: #niedostępne poza siecią UPC
            xbmcgui.Dialog().notification('UPC GO', 'Kanał niedostępny poza siecią UPC.', xbmcgui.NOTIFICATION_INFO)
        return False
    else:
        if 'x-streaming-token' in resp.headers:#2022-11-25
            strTkn=resp.headers['x-streaming-token']
            addon.setSetting('x_streaming_token',strTkn)
            addon.setSetting('x_str_tkn_start',str(int(time.time())))
            print('upcgo.addon TKN_STR_ODŚWIERZONY')
            return strTkn, resp.json()['drmContentId']
        else:
            print('upcgo.addon BŁĄ OWŚWIERZANIA TKN_STR')
            return False#2022-11-25

def killStreamToken():
    tkn=addon.getSetting('x_streaming_token')
    url=apiURL+'pol/web/session-manager/license/token'
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
        'X-cus':addon.getSetting('x_cus'),
        'x-go-dev':addon.getSetting('x_go_dev'),
        'X-OESP-Username':addon.getSetting('x_oesp_username'),
        'X-Profile':addon.getSetting('x_profile'),
        'x-streaming-token':tkn
    }
    cookies=getCookies()
    resp=requests.delete(url,headers=hea,cookies=cookies)
    addon.setSetting('x_streaming_token','')
    print('upcgo.addon TKN_STR_SKASOWANY')

def playLiveTV(cid):
    addon.setSetting('streamType','livetv')
    
    fURL=PATH_profile+'channels.json'
    chns=openJSON(fURL)
    url_mpd='' #"http://wp1-obc12-live-pl-prod.prod.cdn.dmdsdp.com/dash/AXN_HD/manifest.mpd"
    for c in chns:
        if c[2]==cid:
            url_mpd=c[5]
            break
    stmtkn=getStreamToken(cid)
    if stmtkn==False:
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
    else:
        vxttoken,drmContentId = stmtkn
        url_mpd_tkn=url_mpd.replace('/manifest.mpd',';vxttoken='+vxttoken+'/manifest.mpd')

        url_lic=apiURL+'pol/web/session-manager/license?ContentId='+drmContentId
        cookies=getCookies()
        cookie='; '.join([str(x) + '=' + str(y) for x, y in cookies.items()])
        
        hea={
            'User-Agent':UA,
            'Referer':baseurl,
            'deviceName':'Firefox',
            'X-cus':addon.getSetting('x_cus'),
            'x-drm-schemeId':schemeIdUri_gen(url_mpd_tkn),
            'x-go-dev':addon.getSetting('x_go_dev'),
            'X-OESP-Username':addon.getSetting('x_oesp_username'),
            'X-Profile':addon.getSetting('x_profile'),
            'x-streaming-token':vxttoken,
            'content-type':'',
            'cookie':cookie
        }
        #addon.setSetting('hea_lic',str(hea))
        #hea_lic= '&'.join(['%s=%s' % (name, value) for (name, value) in hea.items()])
        hea_lic=urlencode(hea)

        lickey=url_lic+'|'+hea_lic+'|R{SSM}|'

        proxyport = addon.getSetting("proxyport")
        #proxy_lic='http://127.0.0.1:%s/licensetv='%(proxyport)
        proxy_mpd='http://127.0.0.1:%s/MANIFEST='%(proxyport)

        if addon.getSetting('proxy')=='true':
            stream_url=proxy_mpd+url_mpd_tkn
        else:
            stream_url=url_mpd_tkn
            print('BEZ_PROXY')

        import inputstreamhelper
        PROTOCOL = 'mpd'
        DRM = 'com.widevine.alpha'
        is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
        if is_helper.check_inputstream():
            play_item = xbmcgui.ListItem(path=stream_url)
            play_item.setMimeType('application/xml+dash')
            play_item.setContentLookup(False)
            play_item.setProperty('inputstream', is_helper.inputstream_addon)
            play_item.setProperty("IsPlayable", "true")
            play_item.setProperty('inputstream.adaptive.stream_headers', 'User-Agent='+UA)
            play_item.setProperty('inputstream.adaptive.manifest_headers', 'User-Agent='+UA)
            play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
            play_item.setProperty("inputstream.adaptive.license_type", DRM)
            play_item.setProperty("inputstream.adaptive.license_key", lickey)

        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

def calendar(cId,rd):
    repDur=int(int(rd)/(60*60*24))+1
    for i in range(0,repDur):
        date=(datetime.datetime.now() - datetime.timedelta(days=i*1)).strftime('%Y%m%d')
        title=date[:4]+'-'+date[4:6]+'-'+date[6:8]

        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': 'DefaultYear.png', 'fanart':fanart}
        url = build_url({'mode':'replayEPG','chID':cId,'date':str(date),'repDur':rd})
        addItemList(url, title, setArt, 'video')
    xbmcplugin.endOfDirectory(addon_handle)

def isReplay(x):#
    if 'hasReplayTV' not in x:
        return True
    else:
        if x['hasReplayTV']==True:
            return True
        else:
            return False

def getEPG(d,c,rd): #d=yyyymmdd
    now_utc=datetime.datetime.utcnow()
    now_loc=datetime.datetime.now()
    difTime=(now_loc-now_utc).total_seconds()

    d_utc=datetime.datetime(*(time.strptime(d, '%Y%m%d')[0:6]))+datetime.timedelta(seconds=-int(difTime)) #START EPG
    repDur=time.mktime((now_loc-datetime.timedelta(seconds=int(rd))).timetuple())

    ymd=d_utc.strftime('%Y%m%d')
    H=int(d_utc.strftime('%H'))
    partDay=6*int(H/6)

    epgData=[]
    i=1
    while i<=5:
        url=EPGapiURL+ymd+addZero(partDay)+'0000'
        hea={
            'User-Agent':UA,
            'Referer':baseurl
        }
        resp=requests.get(url,headers=hea).json()
        day=d[6:8]

        for e in resp['entries']:
            if e['channelId']==c:
                for ee in e['events']:
                    now=int(time.time())
                    if ee['startTime']<now and datetime.datetime.fromtimestamp(ee['startTime']).strftime('%d')==day and ee['startTime']>=repDur:
                        if isReplay(ee) or (now>=ee['startTime'] and now<=ee['endTime']):
                            #if ee['replayAvailabilityEnd']>now:
                            if True: #TO DO wprowadzić zawężenie wyników do zachowujących warunek jak wyżej (ale uwaga nie wszystkie wpisy mają parametr 'replayAvailabilityEnd'
                                ts=ee['startTime']
                                te=ee['endTime']
                                if 'title' in ee:
                                    title=ee['title']
                                else:
                                    title='b/d'
                                progID=ee['id']
                                test_dupl=0
                                for p in epgData:
                                    if progID in p:
                                        test_dupl=1
                                        break
                                if test_dupl==0:
                                    epgData.append([ts,te,title,progID])
                break
        i+=1
        partDay=partDay+6
        if partDay==24:
            partDay=0
            ymd=(datetime.datetime(*(time.strptime(ymd,'%Y%m%d')[0:6]))+datetime.timedelta(days=1)).strftime('%Y%m%d')

    return epgData

def replaySC(cid,ts,rd):#2024-01-03
    date=ts.split('_')[0] #format WE: %Y%m%d_%H:%M:%S
    co=int(addon.getSetting('cuOffset'))
    tsTMP=int((datetime.datetime(*(time.strptime(ts, "%Y%m%d_%H:%M:%S")[0:6]))+datetime.timedelta(hours=co)).timestamp())
    epg_data=getEPG(date,cid,rd)
    prog=[p for p in epg_data if p[0]==tsTMP]
    if len(prog)>0:
        playReplayTV(prog[0][3],'replay')
    else:
        xbmcgui.Dialog().notification('UPC GO', 'Nagranie niedostępne', xbmcgui.NOTIFICATION_INFO)
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())

def replayEPG(cid,date,rd):#2022-12-23
    epg_data=getEPG(date,cid,rd) #ts(timestamp),te(timestamp),title,progID
    progIDs=[]
    for ee in epg_data:
        if ee[3] not in progIDs:
            progIDs.append(ee[3])
    imgs=getProgImg(progIDs)
    for e in epg_data:
        if addon.getSetting('directPlay')=='true':
            isPlayable='true'
            isFolder=False
            plot='Szczegóły dostępne z poziomu menu kontekstowego'
            URL=build_url({'mode':'playReplayTV','progID':e[3],'contType':'replay'})
        else:
            isPlayable='false'
            isFolder=True
            plot=''
            URL=build_url({'mode':'replayItem','progID':e[3]})
        
        title='[B]'+datetime.datetime.fromtimestamp(e[0]).strftime('%H:%M')+'-'+datetime.datetime.fromtimestamp(e[1]).strftime('%H:%M')+'[/B] '+e[2]
        img=img_addon
        if e[3] in imgs:
            img=imgs[e[3]]

        if addon.getSetting('directPlay')=='true':
            cm=True
            cmItems=[('[B]Szczegóły[/B]','RunPlugin(plugin://plugin.video.upcgo?mode=replayDetails&progID='+quote(e[3])+')')]
        else:
            cm=False
            cmItems=[]
        iL={'title': '','sorttitle': '','plot': plot}
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img, 'fanart':fanart}
        addItemList(URL, title, setArt, 'video', iL, isFolder, isPlayable, cm, cmItems)
    
    if addon.getSetting('directPlay')=='true':
        xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)

def getProgImg(x):#2022-12-23
    pict={}
    k=0
    for i in range(0,int(len(x)/8)+1):
        jbody=[]
        for k in range(0,8):
            count=i*8+k
            if count==len(x):
                break
            else:
                cid=x[count]
                jbody.append({"id":cid,"intents":['posterTile']})
        #print(jbody[0])
        u=IMGapiURL
        params={
            'jsonBody':json.dumps(jbody)
        }
        hea={
            'User-Agent':UA,
            'Referer':baseurl
        }
        resp_pic=requests.get(u,params=params,headers=hea).json()
        #print(resp_pic)
        for p in resp_pic:
            pict[p['id']]=p['intents'][0]['url']
    return pict

def repDet(prog_id):#2022-12-23
    url=apiURL+'pol/web/linear-service/v2/replayEvent/'+prog_id+'?returnLinearContent=true&language=pl'
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
        'X-OESP-Username':addon.getSetting('x_oesp_username'),
        'X-Profile':addon.getSetting('x_profile'),
        'x-tracking-id':addon.getSetting('x_tracking_id')
    }
    
    cookies=getCookies()
    
    resp=requests.get(url,headers=hea).json()
    plot=''
    plot+='[B]'+resp['title']+'[/B]\n'
    if 'longDescription' in resp:
        plot+='[B]Opis: [/B]'+resp['longDescription']+'\n'
    if 'seasonNumber' in resp:
        plot+='[B]Sezon: [/B]'+str(resp['seasonNumber'])+'\n'
    if 'episodeNumber' in resp:
        plot+='[B]Odcinek: [/B]'+str(resp['episodeNumber'])+'\n'
    if 'productionDate' in resp:
        plot+='[B]Data prod.: [/B]'+str(resp['productionDate'])+'\n'
    if 'countryOfOrigin' in resp:
        plot+='[B]Kraj prod.: [/B]'+resp['countryOfOrigin']+'\n'
    if 'genres' in resp:
        genres=''
        for g in resp['genres']:
            genres+=g+' | '
        plot+='[B]Gatunek: [/B]'+ genres[:-3]
    return plot,resp['title']

def replayDetails(prog_id):#2022-12-23
    plot,title=repDet(prog_id)
    if plot=='':
        plot='Brak informacji'
    dialog = xbmcgui.Dialog()
    dialog.textviewer('Szczegóły', plot)

def replayItem(prog_id):
    plot,title=repDet(prog_id)
    progIDs=[prog_id]
    img=getProgImg(progIDs)[prog_id]
    
    iL={'title': title,'sorttitle': '','plot': plot}
    setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': 'img_empty', 'fanart':img}
    url = build_url({'mode':'playReplayTV','progID':prog_id,'contType':'replay'})
    addItemList(url, '..: Oglądaj :..', setArt, 'video', iL, False, 'true')
    
    xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)

def playReplayTV(prog_id,c):
    if c=='replay':
        cnt='replay?eventId='
    elif c== 'vod':
        cnt='vod?contentId='
    addon.setSetting('streamType','replaytv')
    if addon.getSetting('x_streaming_token')!='': #wyrejestrowanie ostatnio użytego tokena (x-streaming-token)
        killStreamToken()
    url=apiURL+'pol/web/session-service/session/v2/web-desktop/customers/'+addon.getSetting('x_cus')+'/'+cnt+prog_id+'&abrType=BR-AVC-DASH&profileId='+addon.getSetting('x_profile')
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
        'X-cus':addon.getSetting('x_cus'),
        #'X-Drm-Device-Id':addon.getSetting('x_drm_device_id'),
        'X-Entitlements-Token':addon.getSetting('x_entitlements_token'),
        'x-go-dev':addon.getSetting('x_go_dev'),
        'X-OESP-Username':addon.getSetting('x_oesp_username'),
        'X-Profile':addon.getSetting('x_profile'),
        'x-tracking-id':addon.getSetting('x_tracking_id')
    }
    cookies=getCookies()
    resp=requests.post(url,headers=hea,cookies=cookies)
    if resp.status_code==200:
        strTkn=resp.headers['x-streaming-token']
        addon.setSetting('x_streaming_token',strTkn)
        addon.setSetting('x_str_tkn_start',str(int(time.time())))
        resp=resp.json()
        url_mpd=resp['url'] #http://wp1-pod2-replay-vxtoken-pl-prod.prod.cdn.dmdsdp.com/sdash/LIVE$BBC_HD/index.mpd/Manifest?device=BR-AVC-DASH&start=2022-06-13T11%3A33%3A00Z&end=2022-06-13T12%3A30%3A00Z
        drmContentId=resp['drmContentId']

        vxttoken=addon.getSetting('x_streaming_token')
        url_mpd_tkn=url_mpd.replace('sdash','sdash;vxttoken='+vxttoken)

        url_lic=apiURL+'pol/web/session-manager/license?ContentId='+drmContentId
        cookies=getCookies()
        cookie='; '.join([str(x) + '=' + str(y) for x, y in cookies.items()])
        hea_lic={
            'User-Agent':UA,
            'Referer':baseurl,
            'deviceName':'Firefox',
            'X-cus':addon.getSetting('x_cus'),
            'x-drm-schemeId':schemeIdUri_gen(url_mpd_tkn),
            'x-go-dev':addon.getSetting('x_go_dev'),
            'X-OESP-Username':addon.getSetting('x_oesp_username'),
            'X-Profile':addon.getSetting('x_profile'),
            'x-streaming-token':vxttoken,
            'x-tracking-id':addon.getSetting('x_tracking_id'),
            'content-type':'',
            'cookie':cookie
        }
        #addon.setSetting('hea_lic',str(hea_lic))
        #hea_LIC= '&'.join(['%s=%s' % (name, value) for (name, value) in hea_lic.items()])
        hea_LIC=urlencode(hea_lic)

        lickey=url_lic+'|'+hea_LIC+'|R{SSM}|'

        proxyport = addon.getSetting("proxyport")
        #proxy_lic='http://127.0.0.1:%s/licensetv='%(proxyport)
        proxy_mpd='http://127.0.0.1:%s/MANIFEST='%(proxyport)

        if addon.getSetting('proxyReplay')=='true':
            stream_url=proxy_mpd+url_mpd_tkn
        else:
            stream_url=url_mpd_tkn
            print('BEZ_PROXY')

        addon.setSetting('startPlaying',str(int(time.time())))#czas rozpoczęcia odtwarzania

        import inputstreamhelper
        PROTOCOL = 'mpd'
        DRM = 'com.widevine.alpha'
        is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
        if is_helper.check_inputstream():
            play_item = xbmcgui.ListItem(path=stream_url)
            play_item.setMimeType('application/xml+dash')
            play_item.setContentLookup(False)
            play_item.setProperty('inputstream', is_helper.inputstream_addon)
            play_item.setProperty("IsPlayable", "true")
            play_item.setProperty('inputstream.adaptive.play_timeshift_buffer', 'true')
            play_item.setProperty('inputstream.adaptive.stream_headers', 'User-Agent='+UA)
            play_item.setProperty('inputstream.adaptive.manifest_headers', 'User-Agent='+UA)
            play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
            play_item.setProperty("inputstream.adaptive.license_type", DRM)
            play_item.setProperty("inputstream.adaptive.license_key", lickey)#proxy_lic+lickey

        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
    else:
        if 'ErrorCode=Unauthorized' in resp.text: #vod poza pakietem
            xbmcgui.Dialog().notification('UPC GO', 'Usługa niedostępna w twoim pakiecie.', xbmcgui.NOTIFICATION_INFO)
        elif 'has no entitlements for the replay' in resp.text: #program poza okresem replayTV TYMCZASOWO DO SPRAWDZENIA !!!!
            xbmcgui.Dialog().notification('UPC GO', 'Materiał nieobjęty ReplayTV (upływ okresu usługi).', xbmcgui.NOTIFICATION_INFO)
        #print(resp.text)
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())

def entitlementsToken():#
    x_cus=addon.getSetting('x_cus')
    x_go_dev=addon.getSetting('x_go_dev')
    x_oesp_username=addon.getSetting('x_oesp_username')
    x_profile=addon.getSetting('x_profile')

    #pakiety
    url=apiURL+'pol/web/purchase-service/v2/customers/'+x_cus+'/entitlements'
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
        'X-cus':x_cus,
        'x-go-dev':x_go_dev,
        'X-OESP-Username':x_oesp_username,
        'X-Profile':x_profile
    }
    cookies=getCookies()
    resp=requests.get(url,headers=hea,cookies=cookies).json()
    addon.setSetting('x_entitlements_token',resp['token'])

def vod_categ(): #Główne menu VOD -> MY Prime, Seriale, Odkrywaj, Dla dzieci, Kanały na Żądanie
    entitlementsToken()
    url=apiURL+'pol/web/vod-service/v3/structure/TV180?language=pl&fallbackRootId=omw_hzn4_vod&maxRes=HD&excludeAdult=true&manu=vod&featureFlags=client_Mobile&entityVersion=1'#vodstructure/.... co tutaj dać np. omw_hzn4_vod
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
        'X-Entitlements-Token':addon.getSetting('x_entitlements_token'),
        'x-go-dev':addon.getSetting('x_go_dev'),
        'X-OESP-Username':addon.getSetting('x_oesp_username'),
        'X-Profile':addon.getSetting('x_profile'),
        'x-tracking-id':addon.getSetting('x_tracking_id')
    }
    cookies=getCookies()
    resp=requests.get(url,headers=hea,cookies=cookies).json()
    for r in resp['screens']:
        title=r['title']
        contId=r['id']

        setArt={'thumb': '', 'poster': img_addon, 'banner': '', 'icon': img_tick, 'fanart':fanart}
        url = build_url({'mode':'vod_subcateg','contId':contId})
        addItemList(url, title, setArt, 'video')
    xbmcplugin.endOfDirectory(addon_handle)

def vod_subcateg(contId): #Podkategorie VOD
    x_profile=addon.getSetting('x_profile')
    cityId=addon.getSetting('cityId')
    url=apiURL+'pol/web/vod-service/v3/collections-screen/'+contId+'?language=pl&profileId='+x_profile+'&optIn=false&sharedProfile=true&maxRes=4K&cityId='+cityId+'&includeExternalProvider=ALL&excludeAdult=true&featureFlags=client_Mobile&entityVersion=1'
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
        'X-Entitlements-Token':addon.getSetting('x_entitlements_token'),
        'x-go-dev':addon.getSetting('x_go_dev'),
        'X-OESP-Username':addon.getSetting('x_oesp_username'),
        'X-Profile':addon.getSetting('x_profile'),
        'x-tracking-id':addon.getSetting('x_tracking_id')
    }
    cookies=getCookies()
    resp=requests.get(url,headers=hea,cookies=cookies).json()
    for r in resp['collections']:
        if r['collectionLayout']=='GridCollection':
            title=r['title']
            link=r['id']
                       
            setArt={'thumb': '', 'poster': img_addon, 'banner': '', 'icon': img_tick, 'fanart':fanart}
            url = build_url({'mode':'vod_items','contId':link,'startCount':'1'})
            addItemList(url, title, setArt, 'video')
    xbmcplugin.endOfDirectory(addon_handle)

def getPic(x,y):# y="posterTile"/"episodeStill"
    pict={}
    k=0
    for i in range(0,int(len(x)/8)+1):
        jbody=[]
        for k in range(0,8):
            count=i*8+k
            if count==len(x):
                break
            else:
                try:
                    cid=x[count]['id']
                except:
                    cid=x['id']
                jbody.append({"id":cid,"intents":[y]})
        #print(jbody[0])
        u=IMGapiURL
        params={
            'jsonBody':json.dumps(jbody)
        }
        resp_pic=requests.get(u,params=params).json()
        #print(resp_pic)
        for p in resp_pic:
            pict[p['id']]=p['intents'][0]['url']
    return pict

def vod_items(contId,p):#lista Seriale/Filmy
    x_profile=addon.getSetting('x_profile')
    cityId=addon.getSetting('cityId')
    sorttype='popularity' # TODO wybór w settingsach
    url=apiURL+'pol/web/vod-service/v3/grid-screen/'+contId+'?language=pl&profileId='+x_profile+'&sortType='+sorttype+'&sortDirection=descending&pagingOffset='+p+'&maxRes=4K&cityId='+cityId+'&goDownloadable=false&onlyGoPlayable=true&excludeAdult=true' #&includeExternalProvider=omw_hzn4_vod
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
        'X-Entitlements-Token':addon.getSetting('x_entitlements_token'),
        'x-go-dev':addon.getSetting('x_go_dev'),
        'X-OESP-Username':addon.getSetting('x_oesp_username'),
        'X-Profile':addon.getSetting('x_profile'),
        'x-tracking-id':addon.getSetting('x_tracking_id')
    }
    cookies=getCookies()
    resp=requests.get(url,headers=hea,cookies=cookies).json()
    totalCount=resp['totalCount']
    count=49
    if 'items' in resp:
        pictures=getPic(resp['items'],"posterTile")
        for r in resp['items']:
            if 'price' not in r: #bez filmów za dodatkową opłatą oraz bez materiałów dostępnych tylko na dekoderach
                if r['id'] in pictures:
                    img=pictures[r['id']]
                else:
                    img=img_addon
                link=r['id']
                if 'brandingProviderId' in r:
                    provider=r['brandingProviderId']
                else:
                    provider='nobrandingprovider'
                title=r['title']
                isPlayable='false'
                isFolder=True
                if r['type']=='ASSET':
                    contType=' [FILM]'
                    if addon.getSetting('directPlay')=='true':
                        Mode='playDirectVOD'
                        isPlayable='true'
                        isFolder=False
                    else:
                        Mode='vod_film'
                elif r['type']=='SERIES':
                    contType=' [SERIAL]'
                    Mode='vod_serial'
                title_plus='[B]'+title+'[/B] '+contType
                plot=''
                if 'duration' in r:
                    H=int(r['duration']/3600)
                    M=addZero(int((r['duration']/3600-H)*60))
                    plot+='[B]Czas: [/B]'+str(H)+':'+M+'\n'
                if 'ageRating' in r:
                    plot+='[B]Kat. wiekowa: [/B]'+str(r['ageRating'])+'\n'
                
                if addon.getSetting('directPlay')=='true' and r['type']=='ASSET':
                    cm=True
                    cmItems=[('[B]Szczegóły[/B]','RunPlugin(plugin://plugin.video.upcgo?mode=vodDetails&contId='+quote(link)+'&prov='+quote(provider)+')')]
                else:
                    cm=False
                    cmItems=[]
                
                iL={'title': title_plus,'sorttitle': '','plot': plot}
                setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img, 'fanart':img}
                url = build_url({'mode':Mode,'contId':link,'prov':provider})
                addItemList(url, title_plus, setArt, 'video', iL, isFolder, isPlayable, cm, cmItems)

        if int(p)+count<totalCount:
            setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_empty, 'fanart':fanart}
            url = build_url({'mode':'vod_items','contId':contId,'startCount':str(int(p)+count)})
            addItemList(url, '[I]>>> Następna strona[/I]', setArt, 'video')
            
    if addon.getSetting('directPlay')=='true':
        xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)

def vodDet(contId,prov):#2022-12-23
    x_profile=addon.getSetting('x_profile')
    cityId=addon.getSetting('cityId')
    url=apiURL+'pol/web/vod-service/v3/details-screen/'+contId+'?language=pl&profileId='+x_profile+'&maxRes=4K&cityId='+cityId+'&includeExternalProvider=ALL&brandingProviderId='+prov #brak: '&includeExternalProvider=ALL&brandingProviderId='+prov 
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
        'X-Entitlements-Token':addon.getSetting('x_entitlements_token'),
        'x-go-dev':addon.getSetting('x_go_dev'),
        'X-OESP-Username':addon.getSetting('x_oesp_username'),
        'X-Profile':addon.getSetting('x_profile'),
        'x-tracking-id':addon.getSetting('x_tracking_id')
    }
    cookies=getCookies()
    resp=requests.get(url,headers=hea,cookies=cookies).json()
    title=resp['title']
    plot=''
    if 'duration' in resp:
        H=int(resp['duration']/3600)
        M=addZero(int((resp['duration']/3600-H)*60))
        plot+='[B]Czas: [/B]'+str(H)+':'+M+'\n'
    if 'ageRating' in resp:
        plot+='[B]Kat. wiekowa: [/B]'+str(resp['ageRating'])+'\n'
    if 'genres' in resp:
        genres=''
        for g in resp['genres']:
            genres+=g+'/'
        plot+='[B]Gatunek: [/B]'+genres[:-1]+'\n'
    if 'longSynopsis' in resp:
        plot+='[B]Opis: [/B]'+resp['longSynopsis']+'\n'
    if 'prodYear' in resp:
        plot+='[B]Rok prod.: [/B]'+resp['prodYear']+'\n'
    if 'goPlayable' in resp:
        if not resp['goPlayable']:
            plot+='[COLOR=yellow]Niedostępne - tylko na dekoderach[/COLOR]\n'
    
    link=resp['instances'][0]['id']
    for ii in resp['instances']:
        if 'OTT' in ii['id']:
            link=ii['id']
            break

    pictures=getPic(resp,"posterTile")
    if resp['id'] in pictures:
        img=pictures[resp['id']]
    else:
        img=img_addon
        
    return title,plot,img,link

def playDirectVOD(contId,prov):#2022-12-23
    title,plot,img,link=vodDet(contId,prov)
    playReplayTV(link,'vod')
    
def vodDetails(contId,prov):#2022-12-23
    title,plot,img,link=vodDet(contId,prov)
    if plot=='':
        plot='Brak informacji'
    dialog = xbmcgui.Dialog()
    dialog.textviewer('Szczegóły', plot)

def vod_film(contId,prov): #szczegóły filmu/odcinka serialu ---> odtwarzanie
    title,plot,img,link=vodDet(contId,prov)
    
    iL={'title': title,'sorttitle': '','plot': plot}
    setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img, 'fanart':img}
    url = build_url({'mode':'playReplayTV','progID':link,'contType':'vod'})
    addItemList(url, '<<<OGLĄDAJ>>>', setArt, 'video', iL, False, 'true')
    
    xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)

def vod_serial(contId): #lista sezonów
    x_profile=addon.getSetting('x_profile')
    cityId=addon.getSetting('cityId')
    url=apiURL+'pol/web/picker-service/v2/episodePicker?profileId='+x_profile+'&seriesCrid='+contId+'&country=pl&language=pl&maxRes=4K&cityId='+cityId+'&replayOptedInTime=0&includeExternalProvider=ALL&mergingOn=true' #brak: &includeExternalProvider=ALL
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
        'X-Entitlements-Token':addon.getSetting('x_entitlements_token'),
        'x-go-dev':addon.getSetting('x_go_dev'),
        'X-OESP-Username':addon.getSetting('x_oesp_username'),
        'X-Profile':addon.getSetting('x_profile'),
        'x-tracking-id':addon.getSetting('x_tracking_id')
    }
    cookies=getCookies()
    resp=requests.get(url,headers=hea,cookies=cookies).json()
    pictures=getPic(resp['seasons'],"posterTile")
    for i,s in enumerate(resp['seasons']):
        if s['id'] in pictures:
            img=pictures[s['id']]
        else:
            img=img_addon
        title=s['title']
        plot=''
        if 'totalEpisodes' in s:
            plot+='[B]Ilość odcinków: [/B]'+str(s['totalEpisodes'])+'\n'
                
        iL={'title': title,'sorttitle': '','plot': plot}
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img, 'fanart':img}
        url = build_url({'mode':'vod_episodes','contId':contId,'sezId':str(i)})
        addItemList(url, title, setArt, 'video', iL)
    xbmcplugin.endOfDirectory(addon_handle)

def vod_episodes(contId,s): #lista odcinków danego sezonu
    x_profile=addon.getSetting('x_profile')
    cityId=addon.getSetting('cityId')
    url=apiURL+'pol/web/picker-service/v2/episodePicker?profileId='+x_profile+'&seriesCrid='+contId+'&country=pl&language=pl&maxRes=4K&cityId='+cityId+'&replayOptedInTime=0&includeExternalProvider=ALL&mergingOn=true' #brak: &includeExternalProvider=ALL
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
        'X-Entitlements-Token':addon.getSetting('x_entitlements_token'),
        'x-go-dev':addon.getSetting('x_go_dev'),
        'X-OESP-Username':addon.getSetting('x_oesp_username'),
        'X-Profile':addon.getSetting('x_profile'),
        'x-tracking-id':addon.getSetting('x_tracking_id')
    }
    cookies=getCookies()
    resp=requests.get(url,headers=hea,cookies=cookies).json()
    pictures=getPic(resp['seasons'][int(s)]['episodes'],"episodeStill")
    for e in resp['seasons'][int(s)]['episodes']:
        if e['id'] in pictures:
            img=pictures[e['id']]
        else:
            img=img_addon
        link=e['id']
        title=e['title']
        plot=''
        if 'episode' in e:
            plot+='[B]Odcinek: [/B]'+str(e['episode'])+'\n'
            title+=' (odc. '+str(e['episode'])+')'
        if 'synopsis' in e:
            plot+='[B]Opis: [/B]'+e['synopsis']+'\n'
        prov='nobrandingprovider'
        if 'source' in e:
            if 'brandingProviderId' in e['source']:
                prov=e['source']['brandingProviderId']
            if 'duration' in e['source']:
                H=int(e['source']['duration']/3600)
                M=addZero(int((e['source']['duration']/3600-H)*60))
                plot+='[B]Czas: [/B]'+str(H)+':'+M+'\n'
            if 'isGoPlayable' in e['source']:
                if not e['source']['isGoPlayable']:
                    plot+='[COLOR=yellow]Niedostępne - tylko na dekoderach[/COLOR]\n'
        Mode='vod_film'
        isFolder=True
        isPlayable='false'
        if addon.getSetting('directPlay')=='true':
            Mode='playDirectVOD'
            isFolder=False
            isPlayable='true'
                
        if addon.getSetting('directPlay')=='true':
            cm=True
            cmItems=[('[B]Szczegóły[/B]','RunPlugin(plugin://plugin.video.upcgo?mode=vodDetails&contId='+quote(link)+'&prov='+quote(prov)+')')]
        else:
            cm=False
            cmItems=[]
        
        iL={'title': title,'sorttitle': '','plot': plot}
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img, 'fanart':img}
        url = build_url({'mode':Mode,'contId':link,'prov':prov})
        addItemList(url, title, setArt, 'video', iL, isFolder, isPlayable, cm, cmItems)
    if addon.getSetting('directPlay')=='true':
        xbmcplugin.setContent(addon_handle, 'videos')    
    xbmcplugin.endOfDirectory(addon_handle)

def categTV():
    channels_gen()

    fURL=PATH_profile+'channels.json'
    chns=openJSON(fURL)
    categs=[]
    for c in chns:
        if c[4] not in categs:
            categs.append(c[4])
    for cg in categs:        
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_addon, 'fanart':fanart}
        url = build_url({'mode':'listTVbyCategs','ctg':cg})
        addItemList(url, cg, setArt)
    xbmcplugin.endOfDirectory(addon_handle)

def listTVbyCategs(ctg):
    channels_gen()

    fURL=PATH_profile+'channels.json'
    chns=openJSON(fURL)
    epg=''
    if addon.getSetting('epg')=='true':
        epg=getSchedule()
    for c in chns:
        if c[4]==ctg:
            plot=''
            if epg!='' and c[2] in epg:
                for e in epg[c[2]]:
                   plot+='[B]'+e[0]+'-'+e[1]+'[/B] '+e[2]+'\n'
            
            iL={'title': c[0],'sorttitle': c[0],'plot': plot}
            setArt={'thumb': c[3], 'poster': c[3], 'banner': c[3], 'icon': c[3], 'fanart':c[3]}
            url = build_url({'mode':'playLiveTV','chID':c[2]})
            addItemList(url, c[0], setArt, 'video', iL, False, 'true')
    xbmcplugin.endOfDirectory(addon_handle)
    xbmcplugin.addSortMethod(handle=addon_handle,sortMethod=xbmcplugin.SORT_METHOD_TITLE)

def search_vod(q):
    query=quote(q.lower())
    entitlementsToken()
    x_profile=addon.getSetting('x_profile')
    cityId=addon.getSetting('cityId')
    url=apiURL+'pol/web/discovery-service/v3/search/contents?profileId='+x_profile+'&sharedProfile=true&includeDetails=true&replayOptedInTime=0&cityId='+cityId+'&clientType=209&contentSourceId=1&contentSourceId=2&contentSourceId=3&contentSourceId=101&contentSourceId=102&searchTerm='+query+'&queryLanguage=pl&startResults=0&maxResults=100&includeNotEntitled=true&maxRes=4K&mergingOn=true&includeExternalProvider=ALL&isGoPlayable=true'
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
        'X-cus':addon.getSetting('x_cus'),
        'X-Entitlements-Token':addon.getSetting('x_entitlements_token'),
        'x-go-dev':addon.getSetting('x_go_dev'),
        'X-Profile':addon.getSetting('x_profile'),
    }
    cookies=getCookies()
    resp=requests.get(url,headers=hea,cookies=cookies).json()
    for r in resp['results']:
        if 'contentType' in r:
            if r['contentType']=='vod':
                if r['productType']!='Transaction':
                    cid=r['id']
                    title='[B]'+r['name'] + ' [/B][FILM]'
                    if 'associatedPicture' in r:
                        img=r['associatedPicture']
                    else:
                        img=img_addon
                    plot=''
                    if 'duration' in r:
                        H=int(r['duration']/3600)
                        M=addZero(int((r['duration']/3600-H)*60))
                        plot+='[B]Czas: [/B]'+str(H)+':'+M+'\n'
                    if 'ageRating' in r:
                        plot+='[B]Kat. wiekowa: [/B]'+str(r['ageRating'])+'\n'
                    
                    isPlayable='true'
                    isFolder=False
                    if addon.getSetting('directPlay')=='true':
                        Mode='playDirectVOD'
                        isPlayable='true'
                        isFolder=False
                    else:
                        Mode='vod_film'
                    
                    if addon.getSetting('directPlay')=='true':
                        cm=True
                        cmItems=[('[B]Szczegóły[/B]','RunPlugin(plugin://plugin.video.upcgo?mode=vodDetails&contId='+quote(cid)+'&prov=nobrandingprovider)')]
                    else:    
                        cm=False
                        cmItems=[]
                    
                    iL={'title': title,'sorttitle': '','plot': plot}
                    setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img, 'fanart':img}
                    url = build_url({'mode':Mode,'contId':cid,'prov':'nobrandingprovider'})
                    addItemList(url, title, setArt, 'video', iL, isFolder, isPlayable, cm, cmItems)

        elif 'seriesContentType' in r:
            if r['seriesContentType']=='VOD':
                cid=r['id']
                title='[B]'+r['name'] + ' [/B][SERIAL]'
                if 'associatedPicture' in r:
                    img=r['associatedPicture']
                else:
                    img=img_addon
                plot=''
                if 'seasonCount' in r:
                    plot+='[B]Ilość sezonów: [/B]'+str(r['seasonCount'])+'\n'
                if 'episodeCount' in r:
                    plot+='[B]Ilość odcinków: [/B]'+str(r['episodeCount'])+'\n'
                if 'specialsCount' in r:
                    if r['specialsCount']>0:
                        plot+='[B]Odcinki specjalne: [/B]'+str(r['specialsCount'])+'\n'
                
                iL={'title': title,'sorttitle': '','plot': plot}
                setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img, 'fanart':img}
                url = build_url({'mode':'vod_serial','contId':cid,'prov':'nobrandingprovider'})
                addItemList(url, title, setArt, 'video', iL)
    
    if addon.getSetting('directPlay')=='true':
        xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)

def search_replayTV(q):
    def chns(x):
        cs=[]
        for xx in x:
            cs.append(xx['id'])
        return cs
    now=int(time.time())
    te=now+7*24*60*60 #do weryfikacji
    ts=now-7*24*60*60
    query=quote(q.lower())
    entitlementsToken()
    x_profile=addon.getSetting('x_profile')
    cityId=addon.getSetting('cityId')
    url=apiURL+'pol/web/discovery-service/v3/search/contents?profileId='+x_profile+'&sharedProfile=true&includeDetails=true&replayOptedInTime=0&cityId='+cityId+'&clientType=209&contentSourceId=1&contentSourceId=2&contentSourceId=3&contentSourceId=101&contentSourceId=102&searchTerm='+query+'&queryLanguage=pl&startResults=0&maxResults=100&includeNotEntitled=true&filterTimeWindowStart='+str(ts)+'&filterTimeWindowEnd='+str(te)+'&maxRes=4K&mergingOn=true&includeExternalProvider=ALL'
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
        'X-cus':addon.getSetting('x_cus'),
        'X-Entitlements-Token':addon.getSetting('x_entitlements_token'),
        'x-go-dev':addon.getSetting('x_go_dev'),
        'X-Profile':addon.getSetting('x_profile'),
    }
    cookies=getCookies()
    resp=requests.get(url,headers=hea,cookies=cookies).json()
    for r in resp['results']:
        if 'seriesContentType' in r:
            if r['seriesContentType']=='Linear':
                if r['groupType']=='series':
                    cid=r['id']
                    title='[B]'+r['name'] + ' [/B][SERIAL]'
                    if 'associatedPicture' in r:
                        img=r['associatedPicture']
                    else:
                        img=img_addon
                    plot=''
                    if 'seasonCount' in r:
                        plot+='[B]Ilość sezonów: [/B]'+str(r['seasonCount'])+'\n'
                    if 'episodeCount' in r:
                        plot+='[B]Ilość odcinków: [/B]'+str(r['episodeCount'])+'\n'
                    if 'specialsCount' in r:
                        if r['specialsCount']>0:
                            plot+='[B]Odcinki specjalne: [/B]'+str(r['specialsCount'])+'\n'
                    chans=chns(r['channels'])
                    
                    iL={'title': title,'sorttitle': '','plot': plot}
                    setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img, 'fanart':img}
                    url = build_url({'mode':'seaRes_serial','contId':cid,'chans':chans})
                    addItemList(url, title, setArt, 'video', iL)

                if r['groupType']=='multisource':
                    cid=r['id']
                    title='[B]'+r['name'] + ' [/B][FILM]'
                    if 'associatedPicture' in r:
                        img=r['associatedPicture']
                    else:
                        img=img_addon
                    plot=''
                    if 'duration' in r:
                        H=int(r['duration']/3600)
                        M=addZero(int((r['duration']/3600-H)*60))
                        plot+='[B]Czas: [/B]'+str(H)+':'+M+'\n'
                    if 'ageRating' in r:
                        plot+='[B]Kat. wiekowa: [/B]'+str(r['ageRating'])+'\n'
                    chans=chns(r['channels'])

                    iL={'title': title,'sorttitle': '','plot': plot}
                    setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img, 'fanart':img}
                    url = build_url({'mode':'seaRes_film','contId':cid,'title':r['name']})
                    addItemList(url, title, setArt, 'video', iL)

        if 'contentType' in r:
            if r['contentType']=='replay':
                cid=r['id']
                title='[B]'+r['name'] + ' [/B][FILM]'
                if 'associatedPicture' in r:
                    img=r['associatedPicture']
                else:
                    img=img_addon
                plot=''
                if 'duration' in r:
                    H=int(r['duration']/3600)
                    M=addZero(int((r['duration']/3600-H)*60))
                    plot+='[B]Czas: [/B]'+str(H)+':'+M+'\n'
                if 'ageRating' in r:
                    plot+='[B]Kat. wiekowa: [/B]'+str(r['ageRating'])+'\n'
                chanName=r['channel']['channelName']
                dateBroadUTC=datetime.datetime(*(time.strptime(r['startTime'], '%Y-%m-%dT%H:%M:%SZ')[0:7]))
                dateBroadLocal=dateBroadUTC.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None).strftime('%Y-%m-%d %H:%M')
                if 'eventReplay' in r:
                    if int(time.time())<=r['eventReplay']['replayAvailabilityEnd'] and r['eventReplay']['isGoPlayable']==True:
                        if addon.getSetting('directPlay')=='true':
                            isPlayable='true'
                            isFolder=False
                            #plot='Szczegóły dostępne z poziomu menu kontekstowego'
                            URL=build_url({'mode':'playReplayTV','progID':cid,'contType':'replay'})
                        else:
                            isPlayable='false'
                            isFolder=True
                            #plot=''
                            URL=build_url({'mode':'replayItem','progID':cid})
                        
                        titleLong=title + ' | ' + dateBroadLocal + ' | ' + chanName                       
                        if addon.getSetting('directPlay')=='true':
                            cm=True
                            cmItems=[('[B]Szczegóły[/B]','RunPlugin(plugin://plugin.video.upcgo?mode=replayDetails&progID='+quote(cid)+')')]
                        else:
                            cm=False
                            cmItems=[]
                        
                        iL={'title': title,'sorttitle': '','plot': plot}
                        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img, 'fanart':img}
                        addItemList(URL, titleLong, setArt, 'video', iL, isFolder, isPlayable, cm, cmItems)
    
    if addon.getSetting('directPlay')=='true':
        xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)

def chanCheck(x,y):
    test=False
    for xx in x:
        if xx[2]==y:
            test=True
            break
    return test
def getRepDur(x,y):
    for xx in x:
        if xx[2]==y:
            return xx[6]
            break
def getChanName(x,y):
    for xx in x:
        if xx[2]==y:
            return xx[0]
            break

def seaRes_serial(contId,chans):
    x_profile=addon.getSetting('x_profile')
    cityId=addon.getSetting('cityId')

    chns=eval(chans)
    #channels_gen()
    #channels=eval(addon.getSetting('channels'))
    fURL=PATH_profile+'channels.json'
    channels=openJSON(fURL)

    eList=[]
    for c in chns:
        if chanCheck(channels,c):

            url=apiURL+'pol/web/picker-service/v2/episodePicker?profileId='+x_profile+'&seriesCrid='+contId+'&country=pl&language=pl&maxRes=4K&cityId='+cityId+'&replayOptedInTime=0&channelId='+c+'&includeExternalProvider=ALL&mergingOn=true'
            hea={
                'User-Agent':UA,
                'Referer':baseurl,
                'X-cus':addon.getSetting('x_cus'),
                'X-Entitlements-Token':addon.getSetting('x_entitlements_token'),
                'x-go-dev':addon.getSetting('x_go_dev'),
                'X-Profile':addon.getSetting('x_profile'),
            }
            cookies=getCookies()
            resp=requests.get(url,headers=hea,cookies=cookies).json()
            title=resp['title']
            chanName=getChanName(channels,c)
            genres=''
            if 'genres' in resp:
                for g in resp['genres']:
                    genres+= g + ' | '
                if genres !='':
                    genres= '[B]Gatunek: [/B]'+genres[:-3]
            def episodeAppend(x,y,sNo=''):
                for e in x: #x - lista odcinków (episodes/specials)
                    plot=''
                    if sNo !='':
                        plot+='[B]Sezon: [/B]'+str(sNo)+'\n'
                    if 'episode' in e:
                        plot+='[B]Odcinek: [/B]'+str(e['episode'])+'\n'
                    if 'synopsis' in e:
                        plot+='[B]Opis: [/B]'+str(e['synopsis'])+'\n'
                    progId=''
                    date=''
                    if 'source' in e:
                        progId=e['source']['eventId']
                        if 'broadcastDate' in e['source']:
                            date=e['source']['broadcastDate']
                        dur=0
                        if 'duration' in e['source']:
                            dur=e['source']['duration']
                            H=int(e['source']['duration']/3600)
                            M=addZero(int((e['source']['duration']/3600-H)*60))
                            plot+='[B]Czas: [/B]'+str(H)+':'+M+'\n'
                        if 'eventReplay' in e['source']:
                            if e['source']['eventReplay']['isGoPlayable']==True and date!='':
                                dateNowUTC=datetime.datetime.utcnow()
                                dateBroadUTC=datetime.datetime(*(time.strptime(date, '%Y-%m-%dT%H:%M:%SZ')[0:7]))
                                timeFromBroad = dateNowUTC-dateBroadUTC
                                if timeFromBroad.seconds<=getRepDur(channels,c) and dateNowUTC>=dateBroadUTC:
                                    y.append([title,genres,plot,progId,date,chanName])#

            if 'seasons' in resp:
                for s in resp['seasons']:
                    if 'episodes' in s:
                        sNo=''
                        if 'season' in s:
                            sNo=s['season']
                        episodeAppend(s['episodes'],eList,sNo)
            if 'episodes' in resp:
                episodeAppend(resp['episodes'],eList)
            if 'specials' in resp:
                episodeAppend(resp['specials'],eList)
    for l in eList:
        title='[B]'+l[0]+'[/B]'
        dateBroadUTC=datetime.datetime(*(time.strptime(l[4], '%Y-%m-%dT%H:%M:%SZ')[0:7]))
        dateBroadLocal=dateBroadUTC.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None).strftime('%Y-%m-%d %H:%M')
        title+=' | '+dateBroadLocal + ' | ' + l[5]
        plot=l[2]+l[1]
        
        if addon.getSetting('directPlay')=='true':
            isPlayable='true'
            isFolder=False
            URL=build_url({'mode':'playReplayTV','progID':l[3],'contType':'replay'})
        else:
            isPlayable='false'
            isFolder=True
            URL=build_url({'mode':'replayItem','progID':l[3]})
        
        if addon.getSetting('directPlay')=='true':
            cm=True
            cmItems=[('[B]Szczegóły[/B]','RunPlugin(plugin://plugin.video.upcgo?mode=replayDetails&progID='+quote(l[3])+')')]
        else:
            cm=False
            cmItems=[]
        
        iL={'title': '','sorttitle': '','plot': plot}
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_tick, 'fanart':fanart}
        addItemList(URL, title, setArt, 'video', iL, isFolder, isPlayable, cm, cmItems)
    
    if addon.getSetting('directPlay')=='true':
        xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)

def seaRes_film(contId,tit):
    x_profile=addon.getSetting('x_profile')
    cityId=addon.getSetting('cityId')
    url=apiURL+'pol/web/picker-service/v1/titleAlsoAvailableOn?profileId='+x_profile+'&language=pl&country=pl&titleId='+contId+'&maxRes=4K&cityId='+cityId+'&includeExternalProvider=ALL&mergingOn=true'
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
        'X-cus':addon.getSetting('x_cus'),
        'X-Entitlements-Token':addon.getSetting('x_entitlements_token'),
        'x-go-dev':addon.getSetting('x_go_dev'),
        'X-Profile':addon.getSetting('x_profile'),
    }
    cookies=getCookies()
    #channels_gen()
    #channels=eval(addon.getSetting('channels'))
    fURL=PATH_profile+'channels.json'
    channels=openJSON(fURL)
    resp=requests.get(url,headers=hea,cookies=cookies).json()
    iList=[]
    if len(resp['sources'])>0:
        for s in resp['sources']:
            chID=s['source']['channel']['channelId']
            if chanCheck(channels,chID):
                chanName=s['source']['channel']['channelName']
                progId=s['source']['eventId']
                date=''
                if 'broadcastDate' in s['source']:
                    date=s['source']['broadcastDate']
                dur=0
                if 'duration' in s['source']:
                    dur=s['source']['duration']
                if 'eventReplay' in s['source']:
                    if s['source']['eventReplay']['isGoPlayable']==True and date!='':
                        dateNowUTC=datetime.datetime.utcnow()
                        dateBroadUTC=datetime.datetime(*(time.strptime(date, '%Y-%m-%dT%H:%M:%SZ')[0:7]))
                        timeFromBroad = dateNowUTC-dateBroadUTC
                        if timeFromBroad.seconds<=getRepDur(channels,chID) and dateNowUTC>=dateBroadUTC:
                            iList.append([tit,progId,date,chanName])#

        for l in iList:
            title='[B]'+l[0]+'[/B]'
            dateBroadUTC=datetime.datetime(*(time.strptime(l[2], '%Y-%m-%dT%H:%M:%SZ')[0:7]))
            dateBroadLocal=dateBroadUTC.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None).strftime('%Y-%m-%d %H:%M')
            title+=' | '+dateBroadLocal + ' | ' + l[3]
            
            if addon.getSetting('directPlay')=='true':
                isPlayable='true'
                isFolder=False
                URL=build_url({'mode':'playReplayTV','progID':l[1],'contType':'replay'})
            else:
                isPlayable='false'
                isFolder=True
                URL=build_url({'mode':'replayItem','progID':l[1]})
                        
            if addon.getSetting('directPlay')=='true':
                cm=True
                cmItems=[('[B]Szczegóły[/B]','RunPlugin(plugin://plugin.video.upcgo?mode=replayDetails&progID='+quote(l[1])+')')]
            else:
                cm=False
                cm=[]
            
            iL={'title': '','sorttitle': '','plot': ''}
            setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_tick, 'fanart':fanart}
            addItemList(URL, title, setArt, 'video', iL, isFolder, isPlayable, cm, cmItems)

    if addon.getSetting('directPlay')=='true':
        xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)

def radio():#2022-12-28
    x_cus=addon.getSetting('x_cus')
    x_go_dev=addon.getSetting('x_go_dev')
    x_oesp_username=addon.getSetting('x_oesp_username')
    x_profile=addon.getSetting('x_profile')

    #lista kanałów
    cityId=addon.getSetting('cityId')
    url=apiURL+'pol/web/linear-service/v2/channels?cityId='+cityId+'&language=pl&productClass=Orion-DASH'
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
        'x-go-dev':x_go_dev,
        'X-OESP-Username':x_oesp_username,
        'X-Profile':x_profile
    }
    cookies=getCookies()
    resp=requests.get(url,headers=hea,cookies=cookies).json()
    channels=[]
    for r in resp:
        if r['logicalChannelNumber']>=950:
            name=r['name']
            lcn=r['logicalChannelNumber']
            cid=r['id']
            logo=r['logo']['focused']
            channels.append([name,lcn,cid,logo])
    epg=''
    if addon.getSetting('epg')=='true':
        epg=getSchedule()
    for c in channels:
        plot=''
        if epg!='' and c[2] in epg:
            for e in epg[c[2]]:
                plot+='[B]'+e[0]+'[/B]  '+e[2]+'\n'

        li=xbmcgui.ListItem(c[0])
        li.setProperty("IsPlayable", 'true')
        li.setInfo(type='video', infoLabels={'title': c[0],'sorttitle': c[0],'plot': plot})
        li.setArt({'thumb': c[3], 'poster': c[3], 'banner': c[3], 'icon': c[3], 'fanart':c[3]})
        url = build_url({'mode':'radioPlay','chID':c[2]})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(addon_handle)
    xbmcplugin.addSortMethod(handle=addon_handle,sortMethod=xbmcplugin.SORT_METHOD_TITLE)

def radioPlay(cid):
    strims={
        'Polskie_Radio_Jedynka':'http://mp3.polskieradio.pl:8810/pr1_mp3',
        'Polskie_Radio_Dwojka':'http://mp3.polskieradio.pl:8812/pr2_mp3',
        'Polskie_Radio_Trojka':'http://mp3.polskieradio.pl:8814/pr3_mp3',
        'Polskie_Radio_Czworka':'http://mp3.polskieradio.pl:8826/pr24_mp3',
        'RMF_FM':'http://rmfstream9.interia.pl:8000/rmf_fm',
        'RMF_Classic':'http://rmfstream9.interia.pl:8000/rmf_classic',
        'RMF_Maxxx':'http://rmfstream9.interia.pl:8000/rmf_maxxx',
        'Radio_ZET':'http://zt01.cdn.eurozet.pl/zet-net.mp3',
        'Antyradio':'http://ant.cdn.eurozet.pl/ant-waw.mp3',
        'Radio_ZET_Chilli':'http://chi.cdn.eurozet.pl/chi-net.mp3',
        'Muzo_fm':'http://n16a-eu.rcs.revma.com:80/1nnezw8qz7zuv',
        'TOK_FM':'http://radiostream.pl/tuba10-1.mp3',
        'Radio_ZET_Gold':'http://ml.cdn.eurozet.pl/mel-net.mp3',
        'VOX_FM':'http://ic1.smcdn.pl/3990-1.mp3',
        'ESKA_Rock':'http://ic1.smcdn.pl/5380-1.mp3',
        'KOLOR_103_FM':'http://n03.radiojar.com:80/xt0cf1v8938uv',
        'Radio_Zlote_Przeboje':'http://radiostream.pl/tuba8936-1.mp3',
        'Radio_ESKA':'http://ic1.smcdn.pl/2380-1.mp3',
        'Radio_Wawa':'http://ic1.smcdn.pl/1380-1.mp3'   
    }
    if cid in strims:
        stream_url=strims[cid]
        play_item = xbmcgui.ListItem(path=stream_url)
        play_item.setProperty("IsPlayable", "true")
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
    else:
        xbmcgui.Dialog().notification('UPC GO', 'Brak źródła.', xbmcgui.NOTIFICATION_INFO)
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())

def logOut():
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
        'X-OESP-Username':addon.getSetting('x_oesp_username'),
        'X-Profile':addon.getSetting('x_profile'),
        'X-Refresh-Token':addon.getSetting('x_refresh_token')
    }
    url=apiURL+'auth-service/v1/authorization'
    resp=requests.delete(url,headers=hea)

    addon.setSetting('status','loggedOut')
    addon.setSetting('x_cus','')
    addon.setSetting('x_oesp_username','')
    addon.setSetting('cityId','')
    addon.setSetting('x_profile','')
    addon.setSetting('x_refresh_token','')
    addon.setSetting('accessToken','')
    addon.setSetting('x_entitlements_token','')
    addon.setSetting('x_streaming_token','')
    addon.setSetting('x_str_tkn_start','')
    addon.setSetting('streamType','')
    addon.setSetting('isReplay','')
    addon.setSetting('startPlaying','')
    addon.setSetting('claimsToken_start','')
    addon.setSetting('CLAIMSTOKEN','')
    

def generate_m3u():#
    if file_name == '' or path_m3u == '':
        xbmcgui.Dialog().notification('UPC GO', 'Podaj nazwę pliku oraz katalog docelowy.', xbmcgui.NOTIFICATION_ERROR)
        return
    xbmcgui.Dialog().notification('UPC GO', 'Generuję liste M3U.', xbmcgui.NOTIFICATION_INFO)
    data = '#EXTM3U\n'
    dataE2 = '' #j00zek for E2 bouquets
    channels_gen()
    fURL=PATH_profile+'channels.json'
    channels=openJSON(fURL)
    for c in channels:
        channelID = c[2]
        channelName = c[0]
        channelLogo = c[3]
        rd=c[6]
        days=int(rd/(24*60*60))
        if rd!=0 and addon.getSetting('isReplay')=='true':
            data += '#EXTINF:0 tvg-id="%s" tvg-logo="%s" catchup="default" catchup-source="plugin://plugin.video.upcgo?mode=replaySC&cid=%s&ts={utc:Ymd_H:M:S}&rd=%s" catchup-days="%s",%s\nplugin://plugin.video.upcgo?mode=playChanList&cid=%s\n' % (channelName,channelLogo,channelID,str(rd),str(days),channelName,channelID)
        else:
            data += '#EXTINF:0 tvg-id="%s" tvg-logo="%s",%s\nplugin://plugin.video.upcgo?mode=playChanList&cid=%s\n' % (channelName,channelLogo,channelName,channelID)
            dataE2 += 'plugin.video.upcgo/addon.py?mode=playChanList&cid=' + '%s:%s\n' % (channelID, channelName) #j00zek for E2 bouquets

    f = xbmcvfs.File(path_m3u + file_name, 'w')
    f.write(data)
    f.close()
    xbmcgui.Dialog().notification('UPC GO', 'Wygenerowano listę M3U.', xbmcgui.NOTIFICATION_INFO)
    
    f = xbmcvfs.File(os.path.join(path_m3u, 'iptv.e2b'), 'w') #j00zek for E2 bouquets
    f.write(dataE2)
    f.close()
    xbmcgui.Dialog().notification('UPC GO', 'Wygenerowano listę E2B', xbmcgui.NOTIFICATION_INFO)

mode = params.get('mode', None)

if not mode:
    home()
else:
    if mode=='logIn':
        logIn()
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
        if addon.getSetting('status')=='loggedIn':
            xbmc.executebuiltin('Container.Refresh()')

    if mode=='logOut':
        logOut()
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
        xbmc.executebuiltin('Container.Refresh()')

    if mode=='menu_tv':
        menu_tv()

    if mode=='replayTV':
        listTV(mode)

    if mode=='liveTV':
        listTV(mode)

    if mode=='playLiveTV':
        c=params.get('chID')
        playLiveTV(c)

    if mode=='playvid':
        c=params.get('url')
        playLiveTV(c)

    if mode=='calendar':
        c=params.get('chID')
        rd=params.get('repDur')
        calendar(c,rd)

    if mode=='replayEPG':
        c=params.get('chID')
        d=params.get('date')
        rd=params.get('repDur')
        replayEPG(c,d,rd)

    if mode=='replayItem':
        prog_id=params.get('progID')
        replayItem(prog_id)
        
    if mode=='replayDetails':#2022-12-23
        prog_id=params.get('progID')
        replayDetails(prog_id)

    if mode=='playReplayTV':
        prog_id=params.get('progID')
        contType=params.get('contType')
        playReplayTV(prog_id,contType)

    if mode=='vod_categ':
        vod_categ()

    if mode=='vod_subcateg':
        contId=params.get('contId')
        vod_subcateg(contId)

    if mode=='vod_items':
        contId=params.get('contId')
        p=params.get('startCount')
        vod_items(contId,p)
        
    if mode=='playDirectVOD':#2022-12-23
        contId=params.get('contId')
        prov=params.get('prov')
        playDirectVOD(contId,prov)
    
    if mode=='vodDetails':#2022-12-23
        contId=params.get('contId')
        prov=params.get('prov')
        vodDetails(contId,prov)
        
    if mode=='vod_film':
        contId=params.get('contId')
        prov=params.get('prov')
        vod_film(contId,prov)

    if mode=='vod_serial':
        contId=params.get('contId')
        vod_serial(contId)

    if mode=='vod_episodes':
        contId=params.get('contId')
        s=params.get('sezId')
        vod_episodes(contId,s)

    if mode=='categTV':
        categTV()

    if mode=='listTVbyCategs':
        ctg=params.get('ctg')
        listTVbyCategs(ctg)

    if mode=='search_vod':
        query = xbmcgui.Dialog().input('Szukaj:', type=xbmcgui.INPUT_ALPHANUM)
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
        if query:
            xbmc.executebuiltin('Container.Update(plugin://plugin.video.upcgo/?mode=searchRes_vod&q='+query+')')
        else:
            xbmc.executebuiltin('Container.Update(plugin://plugin.video.upcgo/,replace)')

    if mode=='search_replayTV':
        query = xbmcgui.Dialog().input('Szukaj:', type=xbmcgui.INPUT_ALPHANUM)
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
        if query:
            xbmc.executebuiltin('Container.Update(plugin://plugin.video.upcgo/?mode=searchRes_replayTV&q='+query+')')
        else:
            xbmc.executebuiltin('Container.Update(plugin://plugin.video.upcgo/,replace)')
    
    if mode=='searchRes_replayTV':
        q=params.get('q')
        search_replayTV(q)
    
    if mode=='searchRes_vod':
        q=params.get('q')
        search_vod(q)
    
    if mode=='seaRes_serial':
        contId=params.get('contId')
        chans=params.get('chans')
        seaRes_serial(contId,chans)

    if mode=='seaRes_film':
        contId=params.get('contId')
        title=params.get('title')
        seaRes_film(contId,title)

    if mode=='playChanList': #play from M3U list
        cid=params.get('cid')
        if addon.getSetting('status')=='loggedIn':
            channels_gen()
            playLiveTV(cid)
        else:
            xbmcgui.Dialog().notification('UPC GO', 'Zaloguj się we wtyczce UPC GO', xbmcgui.NOTIFICATION_INFO)

    if mode=='BUILD_M3U':
        if addon.getSetting('status')=='loggedIn':
            generate_m3u()
        else:
            xbmcgui.Dialog().notification('UPC GO', 'Akcja wymaga zalogowania', xbmcgui.NOTIFICATION_INFO)
    
    if mode=='radio':#2022-12-28
        radio()
        
    if mode=='radioPlay':#2022-12-28
        c=params.get('chID')
        radioPlay(c)
    
    if mode=='replaySC': #2024-01-03 (catchup SC)
        if addon.getSetting('status')=='loggedIn':
            cid=params.get('cid')
            ts=params.get('ts')
            rd=params.get('rd')
            replaySC(cid,ts,rd)
        else:
            xbmcgui.Dialog().notification('UPC GO', 'Zaloguj się we wtyczce UPC GO', xbmcgui.NOTIFICATION_INFO)