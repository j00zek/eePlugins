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
#import json
import random, hmac, hashlib, base64, string
import datetime,time
from urllib.parse import urlencode, quote_plus, quote, unquote, parse_qsl

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon(id='plugin.video.jambox')
PATH=addon.getAddonInfo('path')
img_empty=PATH+'/resources/img/empty.png'
fanart=PATH+'/resources/img/fanart.jpg'

baseurl='https://go.jambox.pl/'
apiURL='https://api.sgtsa.pl/'

UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
heaMAIN={
    'User-Agent':UA,
    'Referer':baseurl,
    'Origin':baseurl[:-1],
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
    
def ISAplayer(protocol, stream_url, DRM=False, licKey=None, cert=None):
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
        play_item.setProperty("IsPlayable", "true")
        play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
        if DRM:
            play_item.setProperty("inputstream.adaptive.license_type", DRM)
            play_item.setProperty('inputstream.adaptive.server_certificate', cert)
            play_item.setProperty("inputstream.adaptive.license_key", licKey)        
        play_item.setProperty('inputstream.adaptive.stream_headers', 'User-Agent='+UA+'&Referer='+baseurl+'&Origin='+baseurl[:-1]+'&Accept=*/*')
        play_item.setProperty('inputstream.adaptive.manifest_headers', 'User-Agent='+UA+'&Referer='+baseurl+'&Origin='+baseurl[:-1]+'&Accept=*/*') #K21
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

def directPlayer(stream_url):
    play_item = xbmcgui.ListItem(path=stream_url)
    play_item.setProperty("IsPlayable", "true")
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

def sign_string(key, to_sign):
    signed_hmac_sha256 = hmac.HMAC(key.encode(), to_sign.encode(), hashlib.sha256)
    digest = signed_hmac_sha256.hexdigest()
    return base64.b64encode(digest.encode()).decode()

def random_string(length):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

def genAuthHea(e):
    n=random_string(22)
    t=30*int(int(1000*time.time())/30000)
    HmacSeed=addon.getSetting('HmacSeed')
    h=sign_string(HmacSeed,n+e+str(t))
    hea={
        'X-Auth':h,
        'X-Nonce':n,
        'X-Device-Id':addon.getSetting('X_Device_Id'),
        'X-Device-Type':'other',
        'X-Impersonate':addon.getSetting('X_Impersonate')
    }
    return hea
        
def main_menu():
    if addon.getSetting('logged')=='false':
        sources=[
            ['ZALOGUJ','login',False,'DefaultUser.png'],
        ]
    else:
        sources=[
            ['TV na żywo','tvList',True,'DefaultTVShows.png'],
            ['WYLOGUJ','logout',False,'DefaultUser.png']    
        ]
    for s in sources:        
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': s[3], 'fanart':fanart}
        url = build_url({'mode':s[1]})
        addItemList(url, s[0], setArt)
    xbmcplugin.endOfDirectory(addon_handle)

def login():
    u=addon.getSetting('username')
    p=addon.getSetting('password')
    if p!='' and u!='':
        url=apiURL+'v1/auth/login'
        data={
            "username":u,
            "password":p
        }
        hea1={'X-Time':str(int(time.time()))}
        hea={**heaMAIN,**hea1}
        resp=requests.post(url,json=data,headers=hea).json()
        if 'message' in resp:
            xbmcgui.Dialog().notification('JAMBOX GO', resp['message'], xbmcgui.NOTIFICATION_INFO)
        else:
            addon.setSetting('X_Device_Id',resp['id'])
            addon.setSetting('HmacSeed',resp['seed'])
            addon.setSetting('X_Impersonate',resp['devices'][0]['id'])
            addon.setSetting('logged','true')
            url=apiURL+'v1/auth/prolong'
            data={}
            hea1=genAuthHea('v1/auth/prolong')
            hea={**heaMAIN,**hea1}
            resp=requests.post(url,json=data,headers=hea)        
    else:
        xbmcgui.Dialog().notification('JAMBOX GO', 'Uzupełnij dane logowania w ustawieniach wtyczki', xbmcgui.NOTIFICATION_INFO)
    
def logout():
    addon.setSetting('X_Device_Id','')
    addon.setSetting('HmacSeed','')
    addon.setSetting('X_Impersonate','')
    addon.setSetting('token','')
    addon.setSetting('logged','false')


def EPG_data(eid):
    url=apiURL+'v1/epg/current/'+eid
    hea1=genAuthHea('v1/epg/current/'+eid)
    hea={**heaMAIN,**hea1}
    resp=requests.get(url,headers=hea).json()
    return resp
    
def epg(eid):
    epgData=EPG_data(eid)
    plot=''
    for e in epgData:
        name=e['name']
        ts=datetime.datetime.fromtimestamp(e['start']).strftime('%H:%M')
        te=datetime.datetime.fromtimestamp(e['end']).strftime('%H:%M')
        plot+='[B]%s-%s[/B] %s \n'%(ts,te,name)
    
    dialog = xbmcgui.Dialog()
    if plot!='':
        dialog.textviewer('EPG', plot)
    else:
        dialog.textviewer('EPG', 'Brak danych')

def epgALL():
    url=apiURL+'v1/epg/all'
    hea1=genAuthHea('v1/epg/all')
    hea={**heaMAIN,**hea1}
    resp=requests.get(url,headers=hea).json()
    return resp
        
def channelsGen():
    url=apiURL+'v1/asset'
    hea1=genAuthHea('v1/asset')
    hea={**heaMAIN,**hea1}
    hea.update({'accept':'application/json, text/plain, */*'})
    resp=requests.get(url,headers=hea).json()
   
    chans=[]
    cids=[]
    for r in resp:
        if r['sgtid'] not in cids:
            if r['entitled']:
                cids.append(r['sgtid'])
                chans.append(r)
    return chans
  
def tvList():
    channels=channelsGen()
    epg=epgALL()
    for c in channels:
        if len(c['alternate_id'])>0 or ('url' in c and len(c['url']))>0:
            cid=c['sgtid']
            img='https://static.sgtsa.pl/channels/logos/%s.png'%(str(cid))
            plot=''           
            contMenu = True
            cmItems=[('[B]EPG[/B]','RunPlugin(plugin://plugin.video.jambox?mode=epg&eid='+str(cid)+')')]
            epgData=epg[str(cid)] if str(cid) in epg else None
            if epgData !=None:
                if 'name' in epgData:
                    plot='[B]TERAZ: [/B][COLOR=yellow]%s[/COLOR]\n'%(epgData['name'])
                if 'description' in epgData:
                    plot+='[I]%s[/I]\n'%(epgData['description']) 

            iL={'title': c['name'],'sorttitle': c['name'],'plot': plot}
            setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart':fanart}
            url = build_url({'mode':'playTV','cid':str(cid)})
            addItemList(url, c['name'], setArt, 'video', iL, False, 'true', contMenu, cmItems)
    xbmcplugin.endOfDirectory(addon_handle)
    xbmcplugin.addSortMethod(handle=addon_handle,sortMethod=xbmcplugin.SORT_METHOD_TITLE)

def playTV(cid):
    if addon.getSetting('logged')=='true':
        channels=channelsGen()
        cData=[c for c in channels if str(c['sgtid'])==cid][0]
        #token
        url=apiURL+'v1/ott/token'
        hea1=genAuthHea('v1/ott/token')
        hea={**heaMAIN,**hea1}
        resp=requests.get(url,headers=hea).json()
        token=resp['token']
        addon.setSetting('token',token)
        
        if 'vectra_uuid' in cData['alternate_id'] and cData['alternate_id']['vectra_uuid']!='':
            #DASH
            x='v1/ott/dash/'+cData['alternate_id']['vectra_uuid']
            url=apiURL+x
            hea1=genAuthHea(x)
            hea={**heaMAIN,**hea1}
            resp=requests.get(url,headers=hea).json()
            xbmc.log('@@@stream_data_DASH: '+str(resp), level=xbmc.LOGINFO)
            url_stream=resp['url']
            licURL=apiURL+resp['license']
            hea1=genAuthHea(resp['license'])
            heaLIC={**heaMAIN,**hea1}
            licKey='%s|%s|R{SSM}|'%(licURL,urlencode(heaLIC))
            ISAplayer('mpd', url_stream, DRM=True, licKey=licKey, cert=None)
            
        else:
            #HLS                
            stream_url='%s?token=%s&hash=%s'%(cData['url']['hlsAac'],quote(addon.getSetting('token')),quote(addon.getSetting('X_Device_Id')))
            xbmc.log('@@@stream url: '+stream_url, level=xbmc.LOGINFO)
            ISAplayer('hls', stream_url, DRM=False, licKey=None, cert=None)
        
        
    else:
        xbmcgui.Dialog().notification('JAMBOX GO', 'Zaloguj się we wtyczce JAMBOX GO', xbmcgui.NOTIFICATION_INFO)
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())

def generate_m3u():
    file_name = addon.getSetting('fname')
    path_m3u = addon.getSetting('path_m3u')
    if file_name == '' or path_m3u == '':
        xbmcgui.Dialog().notification('JAMBOX GO', 'Ustaw nazwę pliku oraz katalog docelowy.', xbmcgui.NOTIFICATION_ERROR)
        return
    xbmcgui.Dialog().notification('JAMBOX GO', 'Generuję liste M3U.', xbmcgui.NOTIFICATION_INFO)
    data = '#EXTM3U\n'
    dataE2 = '' #j00zek for E2 bouquets
    channels=channelsGen()
    for c in channels:
        if len(c['alternate_id'])>0 or ('url' in c and len(c['url']))>0:
            cid = c['sgtid']
            cName = c['name']
            cLogo = 'https://static.sgtsa.pl/channels/logos/%s.png'%(str(cid))
            data += '#EXTINF:0 tvg-id="%s" tvg-logo="%s",%s\nplugin://plugin.video.jambox/?mode=playTV&cid=%s\n' % (cName,cLogo,cName,cid)
            dataE2 += 'plugin.video.jambox/addon.py%3fmode=playTV&cid=' + '%s:%s\n' % (cid, cName) #j00zek for E2 bouquets

    #f = xbmcvfs.File(path_m3u + file_name, 'w')
    #f.write(data)
    #f.close()
    #xbmcgui.Dialog().notification('JAMBOX GO', 'Wygenerowano listę M3U.', xbmcgui.NOTIFICATION_INFO)

    f = xbmcvfs.File(os.path.join(path_m3u, 'iptv.e2b'), 'w') #j00zek for E2 bouquets
    f.write(dataE2)
    f.close()
    xbmcgui.Dialog().notification('TV SMART GO', 'Wygenerowano listę E2B', xbmcgui.NOTIFICATION_INFO)

    
mode = params.get('mode', None)

if not mode:
    main_menu()
else:
    if mode=='login':
        login()
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
        xbmc.executebuiltin('Container.Update(plugin://plugin.video.jambox/,replace)')

    if mode=='logout':
        logout()
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
        xbmc.executebuiltin('Container.Update(plugin://plugin.video.jambox/,replace)')
        
    if mode=='tvList':
        tvList()
    
    if mode=='epg':
        eid=params.get('eid')
        epg(eid)
    
    if mode=='playTV':
        cid=params.get('cid')
        playTV(cid)   
    
    if mode=='BUILD_M3U':
        generate_m3u()      
        