# -*- coding: utf-8 -*-
import os
import sys

import requests
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
#import re
#import base64
#import json
import random
import datetime
import time
from urllib.parse import urlencode, quote_plus, quote, unquote, parse_qsl

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon(id='plugin.video.rakuten_tv')
PATH=addon.getAddonInfo('path')
PATH_profile=xbmcvfs.translatePath(addon.getAddonInfo('profile'))
if not xbmcvfs.exists(PATH_profile):
    xbmcvfs.mkdir(PATH_profile)
img_empty=PATH+'/resources/img/empty.png'
fanart='/resources/img/fanart.jpg'

UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
UAandr='Dalvik/2.1.0 (Linux; U; Android 6.0; Lenovo TAB 2 A10-70F Build/MRA58K)'
baseurl='https://www.rakuten.tv/'
apiURL='https://gizmo.rakuten.tv/v3/'

hea={
    'User-Agent':UA,
    'Referer':baseurl,
    'Content-Type':'application/json',
    'Accept':'application/json, text/plain, */*',
    'Accept-Encoding':'gzip, deflate, br',
    'Connection':'keep-alive',
    'Origin':baseurl[:-1],
}

paramsURL={
    'classification_id':'277',
    'device_identifier':'web',
    'device_stream_audio_quality':'2.0',
    'device_stream_hdr_type':'NONE',
    'device_stream_video_quality':'FHD',
    'locale':'pl',
    'market_code':'pl'
}

hea_andr={
    'user-agent':'Rakuten TV/3.25.4 (tv.wuaki; build 3250404; Android SDK 23) 4.8.0 Lenovo Lenovo TAB 2 A10-70F',
    'content-type':'application/json; charset=utf-8',
    'accept-encoding':'gzip'   
}

paramsURLandr={
    'device_identifier':'android',
    'app_version':'3.25.4',
    'classification_id':'277',
    'market_code':'pl'
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

def main_menu():
    sources=[
        ['Darmowe VOD','vod','DefaultAddonVideo.png'],
        ['Kanały TV','tv','DefaultTVShows.png']
    ]
    for s in sources:
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': s[2], 'fanart': fanart}
        url = build_url({'mode':s[1]})
        addItemList(url, s[0], setArt)
    xbmcplugin.endOfDirectory(addon_handle)

def addVODcateg(c): #helper
    try:
        vodCategs=eval(addon.getSetting('vodCategs'))
    except:
        vodCategs={}
    url=apiURL+'lists/'+c
    resp=requests.get(url, headers=hea, params=paramsURL).json()
    try:
        categName=resp['data']['name'].replace('ZA DARMO | ','').replace(' - oglądaj za darmo','')
    except:
        categName=c.replace('-','')    
        
    vodCategs[c]=categName
    addon.setSetting('vodCategs',str(vodCategs))
    return categName

def vod():
    url=apiURL+'skeleton/gardens/free'
    paramsURL.update({'live_channel_support':'true','user_status':'visitor'})
    resp=requests.get(url, headers=hea,params=paramsURL).json()
    for i in resp['data']['lists']:
        if i['type']=='lists':
            contType=i['content_type']
            cid=i['id']

            try:
                vodCategs=eval(addon.getSetting('vodCategs'))
            except:
                vodCategs={}
            categ=vodCategs[cid] if cid in vodCategs else addVODcateg(cid) #cid.replace('-',' ')
                        
            setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': 'DefaultGenre.png', 'fanart': fanart}
            url = build_url({'mode':'vodList','cid':cid,'page':'1'})
            addItemList(url, categ, setArt)
    xbmcplugin.endOfDirectory(addon_handle)        

def vodList(cID,page):
    count=str(addon.getSetting('count'))
    url=apiURL+'lists/'+cID
    if page !='1':
        paramsURL.update({'page':page,'per_page':count})
        url+='/contents'
    else:
        paramsURL.update({'contents[per_page]':count})
    
    resp=requests.get(url, headers=hea, params=paramsURL).json()
    respData=resp['data']['contents']['data'] if page=='1' else resp['data']
    seasons={}
    for i in respData:
        title=i['title']
        desc=i['short_plot']
        years=i['years'] if 'years' in i else None
        year=int(i['year']) if 'year' in i else 0
        dur=i['duration']*60 if 'duration' in i else 0
        genres=[a['name'] for a in i['genres']] if 'genres' in i else []
        cType=i['type']#tv_shows, movies
        cid=i['id'] #f.e: birdman
        img=i['images']['artwork']
        if cType=='movies':
            iL={'title': title,'sorttitle': title,'plot': desc,'year':year,'duration':dur,'genre':genres,'mediatype':'movie'}
            isPlayable='true'
            isFolder=False
            URL=build_url({'mode':'playVOD','cid':cid,'contType':cType})
            CM=True
            cmItems=[('[B]Szczegóły[/B]','RunPlugin(plugin://plugin.video.rakuten_tv?mode=details&cid='+cid+')')]
        elif cType=='tv_shows':
            if years!=None:
                desc+='\nRok prod.:%s'%(years)
            iL={'title': title,'sorttitle': title,'plot': desc,'mediatype':'tvshow'}
            isPlayable='false'
            isFolder=True
            URL=build_url({'mode':'seasonList','cid':cid})
            CM=False
            cmItems=[]
            seasons[cid]=i['seasons']
            
        setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart': fanart}
        addItemList(URL, title, setArt, 'video', iL, isFolder, isPlayable, CM, cmItems)
        
    saveF(PATH_profile+'/seasons.txt',str(seasons))
    
    pageInfo=resp['meta']['pagination'] if page!='1' else None
    nextPageTest=False
    if page=='1' and len(resp['data']['contents']['data'])==int(count):
        nextPageTest=True
    if page!='1' and pageInfo['page']<pageInfo['total_pages']:
        nextPageTest=True
    if nextPageTest:
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': '', 'fanart': fanart}
        url_p = build_url({'mode':'vodList','cid':cID,'page':str(int(page)+1)})
        addItemList(url_p, '[B][COLOR=yellow]>>> Następna strona[/COLOR][/B]', setArt, 'video')
        
    xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)        

def getData(r): #helper
    contData=r['view_options']['private']['streams'][0]
    plot=''
    plot+='[B]Audio: [/B]'+(', ').join([x['name'] for x in contData['audio_languages']])+'\n'
    plot+='[B]Napisy: [/B]'+(', ').join([x['name'] for x in contData['subtitle_languages']])
    return plot

def contData(d,medType=None): #helper
    title=d['title']
    originalTitle=d['original_title'] if 'original_title' in d else ''
    year=d['year'] if 'year' in d else 0
    plotoutline=d['short_plot'] if 'short_plot' in d else ''
    plot=d['plot'] if 'plot' in d else ''
    dur=d['duration']*60 if 'duration' in d else 0
    cast=[a['name'] for a in d['actors']] if 'actors' in d else []
    countries=[a['name'] for a in d['countries']] if 'countries' in d else []
    directors=[a['name'] for a in d['directors']] if 'directors' in d else []
    genres=[a['name'] for a in d['genres']] if 'genres' in d else []
    try:
        mpaa=d['clasification']['name']
    except:
        mpaa=''
    try:
        rating=d['rating']['average']/d['rating']['scale']
    except:
        rating=0
        
    lng=getData(d)
    plot+='\n'+lng
    plotoutline+='\n'+lng
    
    iL={'title': title,'originaltitle':originalTitle,'sorttitle': title,'plot': plot,'plotoutline':plotoutline,'year':year,'duration':dur,'genre':genres,'country':countries,'director':directors,'cast':cast,'mpaa':mpaa,'rating':rating,'mediatype':medType}
    
    return iL

def details(cid):
    url=apiURL+'movies/'+cid
    paramsURL.update({'disable_dash_legacy_packages':'false'})
    resp=requests.get(url, headers=hea, params=paramsURL).json()
    iL=contData(resp['data'])
    plot='[B][COLOR=cyan]%s[/COLOR][/B]'%(iL['title'])
    if iL['originaltitle']!='':
        plot+=' (%s)\n'%(iL['originaltitle'])
    else:
        plot+='\n'
    if iL['year']!=0:
        plot+='[B]Rok prod.:[/B] %s\n'%(str(iL['year']))
    if iL['duration']!=0:
        plot+='[B]Czas:[/B] %s minut\n'%(str(int(iL['duration']/60)))
    if len(iL['genre'])>0:
        plot+='[B]Gatunek:[/B] %s\n'%(', '.join(iL['genre']))
    if len(iL['country'])>0:
        plot+='[B]Kraj:[/B] %s\n'%(', '.join(iL['country']))
    if len(iL['cast'])>0:
        plot+='[B]Obsada:[/B] %s\n'%(', '.join(iL['cast']))
    if len(iL['director'])>0:
        plot+='[B]Reżyseria:[/B] %s\n'%(', '.join(iL['director']))
    if iL['mpaa']!='':
        plot+='[B]Ograniczenia wiekowe:[/B] %s\n'%(iL['mpaa'])
    plot+='[B]Ocena:[/B] %s\n'%(str(iL['rating']))
    
    plot+='\n %s' %(iL['plot'])
        

    if plot=='':
        plot='Brak danych'
    dialog = xbmcgui.Dialog()
    dialog.textviewer('Szczegóły', plot) 

def seasonList(cID):
    seasons=eval(openF(PATH_profile+'/seasons.txt'))[cID]
    for s in seasons:
        title='Sezon '+s['id'].split('-')[-1]

        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': 'DefaultAddonVideo.png', 'fanart': fanart}
        url = build_url({'mode':'episodeList','cid':cID,'sid':s['id']})
        addItemList(url, title, setArt, 'video')
        
    xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)
    
def episodeList(cID,sID):
    url=apiURL+'seasons/'+sID
    paramsURL.update({'disable_dash_legacy_packages':'false'})
    resp=requests.get(url, headers=hea, params=paramsURL).json()
    for i in resp['data']['episodes']:
        title=i['display_name']
        desc=i['short_plot']
        year=int(i['year']) if 'year' in i else 0
        dur=i['duration'] if 'duration' in i else 0
        cType=i['type']#episodes
        cid=i['id'] 
        img=i['images']['artwork']
        
        desc+='\n\n%s'%(getData(i)) #audio,napisy
        
        iL={'title': title,'sorttitle': title,'plot': desc,'year':year,'duration':dur,'mediatype':'episode'}
        setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart': fanart}
        URL=build_url({'mode':'playVOD','cid':cid,'sid':sid,'contType':cType})
        addItemList(URL, title, setArt, 'video', iL, False, 'true')
        
    xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)    
        
    
def playVOD(cid,cType,sid=None):
    if cType=='movies':
        url=apiURL+'movies/'+cid
    elif cType=='episodes':
        url=apiURL+'seasons/'+sid
    paramsURL.update({'disable_dash_legacy_packages':'false'})
    resp=requests.get(url, headers=hea, params=paramsURL).json()
    if cType=='movies':
        contData=resp['data']['view_options']['private']['streams'][0]
    elif cType=='episodes':
        cont=[e for e in resp['data']['episodes'] if e['id']==cid][0]
        contData=cont['view_options']['private']['streams'][0]
        
    audio_label=[x['name'] for x in contData['audio_languages']]
    audio_id=[x['id'] for x in contData['audio_languages']]
    select = xbmcgui.Dialog().select('Źródła', audio_label)
    if select > -1:
        lng=audio_id[select]
    else:
        lng='POL' if 'POL' in audio_label else audio_id[0]
    
    devType=addon.getSetting('devType')
    url=apiURL+'avod/streamings'
    if devType=='windows':
        data={
            "audio_language":lng,
            "audio_quality":"2.0",
            "classification_id":"277",
            "content_id":cid,
            "content_type":cType,
            "device_make":"firefox",
            "device_model":"GENERIC",
            "device_serial":"not implemented",
            "device_stream_video_quality":"HD",
            "device_uid":addon.getSetting('device_uid'),
            "device_year":"1970",
            "gam_correlator":1347161229000771,
            "gdpr_consent_opt_out":"0",
            "gdpr_consent":"CPusOQAPusOQAADABBPLDICsAP_AAH_AAAAAGfMXZCpcBSlgYCpoAIoAKIAUEAAAgiAAABAAAoABCAAAIAQAgAAgIAAAAAAAAAAAIAJAAQAAAAEAAAAAAAAAAAAIIACAAAAAIABAAAAAAAAACAAAAAAAAAAAAAAEAAAAgABAABAAAAAAEDPmKshUuApSwMBQkAEEAFEAKCAAAQRAAAAgAAQAABAAAEAIAQAAQAAAAAAAAAAAAEAEAAAAAAACAAAAAAAAAAAAEAAAAAAAAEAAgAAAAAAAAAAAAAAAAAAAAAAACAAAAQAAgAAgAAAAACAA.YAAAAAAAA4DA",
            "hdr_type":"NONE",
            "ifa_subscriber_id":None,
            "ifa_type":"ppid",
            "player_height":1080,
            "player_width":1920,
            "player":"web:DASH-CENC:WVM",
            "publisher_provided_id":addon.getSetting('publisher_provided_id'),
            "strict_video_quality":False,
            "subtitle_formats":["vtt"],
            "subtitle_language":"MIS",
            "video_type":"stream",
            "support_thumbnails":True,
            "app_bundle":"com.rakutentv.web",
            "app_name":"RakutenTV",
            "url":"rakuten.tv",
        }
        headers=hea
        params=paramsURL
    elif devType=='android':
        if addon.getSetting('device_serial')=='':
            addon.setSetting('device_serial',code_gen(8)+'-'+code_gen(4)+'-'+code_gen(4)+'-'+code_gen(4)+'-'+code_gen(12))
        data={
            "audio_language": lng,
            "audio_quality": "2.0",
            "content_id": cid,
            "content_type": cType,
            "device_serial": addon.getSetting('device_serial'),
            "hdr_type": "NONE",
            "player": "android:DASH-CENC",
            "subtitle_language": "MIS",
            "support_thumbnails": True,
            "video_quality": "HD",#SD
            "video_type": "stream"
        }
        headers=hea_andr
        params=paramsURLandr
    resp=requests.post(url, headers=headers, params=params, json=data).json()
    #print(resp)
    stream_url=resp['data']['stream_infos'][0]['url']
    lic_url=resp['data']['stream_infos'][0]['license_url']
    if devType=='windows':
        UA_player=UA
        lic_hea={
            'User-Agent':UA,
            'Referer':baseurl,
            'Origin':baseurl[:-1],
            'Content-Type':'',
            'Accept-Encoding':'gzip, deflate, br',
            
        }
    elif devType=='android':
        UA_player=UAandr
        lic_hea={
            'User-Agent':UAandr,
            'Accept-Encoding':'gzip',
            'Content-Type':'application/octet-stream',
            'Connection':'Keep-Alive',    
        }
    isDRM=True #TO DO: weryfikacja czy jest DRM
    subActive=False
    subt=[x for x in resp['data']['stream_infos'][0]['all_subtitles'] if x['language']=='POL' and x['format']=='vtt'] #plik z napisami POL
        
    import inputstreamhelper
    PROTOCOL = 'mpd'
    DRM = 'com.widevine.alpha'
    if isDRM:
        is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
    else:
        is_helper = inputstreamhelper.Helper(PROTOCOL)
    if is_helper.check_inputstream():
        play_item = xbmcgui.ListItem(path=stream_url)           
        play_item.setMimeType('application/xml+dash')
        play_item.setContentLookup(False)
        play_item.setProperty('inputstream', is_helper.inputstream_addon)
        play_item.setProperty("IsPlayable", "true")
        play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
        play_item.setProperty('inputstream.adaptive.manifest_headers', 'User-Agent='+UA_player)
        play_item.setProperty('inputstream.adaptive.stream_headers', 'User-Agent='+UA_player)
        if len(subt)>0 and lng!='POL': #napisy (POL) uruchamiają się jeśli nie ma polskiej ścieżki audio
            play_item.setSubtitles([subt[0]['url']])
            subActive=True
        if isDRM:
            play_item.setProperty('inputstream.adaptive.license_type', DRM)
            play_item.setProperty('inputstream.adaptive.license_key', lic_url+'|'+urlencode(lic_hea)+'|R{SSM}|')
                
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
        
        if subActive==True:
            while not xbmc.Player().isPlaying():
                xbmc.sleep(100)
            xbmc.Player().showSubtitles(True)

    
def categsTV():
    url=apiURL+'live_channel_categories'
    resp=requests.get(url, headers=hea, params=paramsURL).json()
    chans={}
    for r in resp['data']:
        chans[r['name']]=r['live_channels']
                
        iL={'title': r['name'],'sorttitle': r['name'],'plot': ''}
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': 'DefaultGenre.png', 'fanart': fanart}
        url = build_url({'mode':'tvList','categ':r['name']})
        addItemList(url, r['name'], setArt, 'video', iL)
    addon.setSetting('channelsByCateg',str(chans))
    xbmcplugin.endOfDirectory(addon_handle)

def getTime(x):
    diff_str=x[-6:]
    y=datetime.datetime(*(time.strptime(x.replace(diff_str,''),'%Y-%m-%dT%H:%M:%S.000')[0:6]))    
    z=y.strftime('%H:%M')
    return y,z

def getEPG(x):
    epg=''
    for p in x:
        tsD,ts=getTime(p['starts_at'])
        teD,te=getTime(p['ends_at'])
        tit=p['title']
        desc=p['description'] if 'description' in p else ''
        
        if teD>datetime.datetime.now():
            epg+='[B]'+ts+' - '+te+' '+tit+'[/B]\n'
            epg+='[I]'+desc+'[/I]\n'
    return epg
    
def tvList(categ):
    now=datetime.datetime.utcnow()
    ts=now-datetime.timedelta(hours=2)
    te=now+datetime.timedelta(hours=12)
    ts_str=ts.strftime('%Y-%m-%dT%H:00:00.000Z')
    te_str=te.strftime('%Y-%m-%dT%H:00:00.000Z')

    url=apiURL+'live_channels'
    paramsURL.update({'epg_ends_at':te_str,'epg_starts_at':ts_str,'page':'1','per_page':'100'})
    channels=eval(addon.getSetting('channelsByCateg'))
    resp=requests.get(url, headers=hea, params=paramsURL).json()
    
    def checkCateg(x,y):
        test=0
        for yy in y:
            if yy['name']==x:
                test=1    
                break
        if test==1:
            return True
        else:
            return False
    
    for r in resp['data']:
        if checkCateg(categ,r['labels']['tags']) or r['id'] in channels[categ]:
            chName=r['title']
            chLogo=r['images']['artwork']
            cid=r['id']
            lang=r['labels']['languages'][0]['id']
            epg=getEPG(r['live_programs'])
            
            iL={'title': chName,'sorttitle': chName,'plot': epg}
            setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': chLogo, 'fanart': chLogo}
            url = build_url({'mode':'playSource','cid':cid,'lang':lang})
            addItemList(url, chName, setArt, 'video', iL, False, 'true')
    xbmcplugin.endOfDirectory(addon_handle)
    xbmcplugin.addSortMethod(handle=addon_handle,sortMethod=xbmcplugin.SORT_METHOD_TITLE)

def playSource(cid,lang):
    #print(u)
    url=apiURL+'avod/streamings'
    paramsURL.update({'disable_dash_legacy_packages':'false'})
    data={
        "audio_language": lang,
        "audio_quality": "2.0",
        "classification_id": "277",
        "content_id": cid,
        "content_type": "live_channels",
        "device_serial": "not implemented",
        "device_stream_video_quality": "HD",
        "device_uid":addon.getSetting('device_uid'),
        "device_year": "1970",
        "gdpr_consent": "CPcM_sAPcM_sAADABBPLCXCsAP_AAH_AAAAAHrsVZCpcBSlgYCpoAIoAKIAUEAAAgiAAABAAAoABCAAAIAQAgAAgIAAAAAAAAAAAIAJAAQAAAAEAAAAAAAAAAAAIIACAAAAAIABAAAAAAAAACAAAAAAAAAAAAAAEAAAAgABAABAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAgZ8xVkKlwFKWBgKGgAggAogBQQAACCIAAAEAACAAAIAAAgBACAACAAAAAAAAAAAAAgAgABAAAAAQAAAAAAAAAAAAggAAAAAAAgAEAAAAAAAAAAAAAAAAAAAAAAAAQAAACAAEAAEAAAAAAQAA.YAAAAAAAA4DA",
        "gdpr_consent_opt_out": "0",
        "hdr_type": "NONE",
        "ifa_subscriber_id": None,
        "player": "web:HLS-NONE:NONE",
        "player_height": 1080,
        "player_width": 1920,
        "publisher_provided_id":addon.getSetting('publisher_provided_id'),
        "strict_video_quality": False,
        "subtitle_formats": [
            "vtt"
        ],
        "subtitle_language": "MIS",
        "video_type": "stream"
    }
    resp=requests.post(url, headers=hea,json=data,params=paramsURL).json()
    url_stream=resp['data']['stream_infos'][0]['url']+'|User-Agent='+UA+'&Referer='+baseurl
    print(url_stream)
    
    if addon.getSetting('tvPlayerType')=='ffmpeg':
        play_item = xbmcgui.ListItem(path=url_stream)
        play_item.setProperty("IsPlayable", "true")
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
    
    else:
        import inputstreamhelper
        PROTOCOL = 'hls'
        is_helper = inputstreamhelper.Helper(PROTOCOL)
        if is_helper.check_inputstream():
            play_item = xbmcgui.ListItem(path=url_stream)
            play_item.setMimeType('application/xml+dash')
            play_item.setContentLookup(False)
            play_item.setProperty('inputstream', is_helper.inputstream_addon)
            play_item.setProperty("IsPlayable", "true")
            play_item.setProperty('inputstream.adaptive.play_timeshift_buffer', 'false')
            play_item.setProperty('inputstream.adaptive.stream_headers', 'User-Agent='+UA)#+'&Referer='+baseurl)
            play_item.setProperty('inputstream.adaptive.manifest_headers', 'User-Agent='+UA)#K21
            play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)    

    
def code_gen(x):
    base='0123456789abcdef'
    code=''
    for i in range(0,x):
        code+=base[random.randint(0,15)]
    return code
    
def create_m3u():
    file_name = addon.getSetting('fname')
    path_m3u = addon.getSetting('path_m3u')
    if file_name == '' or path_m3u == '':
        xbmcgui.Dialog().notification('Rakuten TV', 'Ustaw nazwę pliku oraz katalog docelowy.', xbmcgui.NOTIFICATION_ERROR)
        return
    xbmcgui.Dialog().notification('Rakuten TV', 'Generuję listę M3U.', xbmcgui.NOTIFICATION_INFO)
    data = '#EXTM3U\n'
    
    now=datetime.datetime.utcnow()
    ts=now-datetime.timedelta(hours=2)
    te=now+datetime.timedelta(hours=12)
    ts_str=ts.strftime('%Y-%m-%dT%H:00:00.000Z')
    te_str=te.strftime('%Y-%m-%dT%H:00:00.000Z')

    url=apiURL+'live_channels'
    paramsURL.update({'epg_ends_at':te_str,'epg_starts_at':ts_str,'page':'1','per_page':'200'})
    resp=requests.get(url, headers=hea, params=paramsURL).json()
    for d in resp['data']:
        cid = d['id']
        cName = d['title']
        cLogo = d['images']['artwork']
        lang = d['labels']['languages'][0]['id']
        data += '#EXTINF:0 tvg-id="%s" tvg-logo="%s" group-title="Rakuten TV",%s\nplugin://plugin.video.rakuten_tv?mode=playSource&cid=%s&lang=%s\n' % (cName,cLogo,cName,cid,lang)

    f = xbmcvfs.File(path_m3u + file_name, 'w')
    f.write(data)
    f.close()
    xbmcgui.Dialog().notification('Rakuten TV', 'Wygenerowano listę M3U.', xbmcgui.NOTIFICATION_INFO)

mode = params.get('mode', None)

if not mode:
    if addon.getSetting('device_uid')=='':
        addon.setSetting('device_uid',code_gen(8)+'-'+code_gen(4)+'-'+code_gen(4)+'-'+code_gen(4)+'-'+code_gen(12))
    if addon.getSetting('publisher_provided_id')=='':
        addon.setSetting('publisher_provided_id',code_gen(8)+'-'+code_gen(4)+'-'+code_gen(4)+'-'+code_gen(4)+'-'+code_gen(12))
    main_menu()

else:
    if mode=='vod':
        vod()
    
    if mode=='vodList':
        cid=params.get('cid')
        page=params.get('page')
        vodList(cid,page)

    if mode=='details':
        cid=params.get('cid')
        details(cid)
        
    if mode=='seasonList':
        cid=params.get('cid')
        seasonList(cid)
        
    if mode=='episodeList':
        cid=params.get('cid')
        sid=params.get('sid')
        episodeList(cid,sid)
    
    if mode=='playVOD':
        cid=params.get('cid')
        sid=params.get('sid')
        contType=params.get('contType')
        playVOD(cid,contType,sid)
    
    if mode=='tv':
        categsTV()
        
    if mode=='tvList':
        categ=params.get('categ')
        tvList(categ)    
    
    if mode=='playSource':
        cid=params.get('cid')
        lang=params.get('lang')
        playSource(cid,lang)

    if mode=='create_m3u':
        create_m3u()
