#!//usr/bin/python
# -*- coding: utf-8 -*-
#
########## plugin by mbebe licensed under GNU GENERAL PUBLIC LICENSE. Version 2, June 1991 ##########
# minor changes for emukodi j00zek

import ast
import sys, re
from emukodi import xbmcgui, xbmcplugin, xbmcvfs
import time
import requests
from .routing import Plugin as routing_Plugin
from datetime import datetime

from .helper import Helper

base_url = sys.argv[0]
handle = int(sys.argv[1])
helper = Helper(base_url, handle)
plugin = routing_Plugin()


try:
    # Python 3
    from urllib.parse import quote_plus, unquote_plus, quote, unquote,parse_qsl,urlencode
    to_unicode = str
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except:
    # Python 2.7
    from urllib import quote_plus, unquote_plus, quote, unquote,urlencode
    from urlparse import parse_qsl
    to_unicode = unicode

def getTime(x,y):
    if y=='date':
        data='%Y-%m-%d'
    elif y=='hour':
        data='%H:%M'
    return datetime.fromtimestamp(x).strftime(data)
    
def channelList():
    timestamp = int(time.time())
    json_data = {
    'epg_limit_prev': 1,
    'epg_limit_next': 10,
    'epg_current_time': timestamp,
    'need_epg': True,
    'need_list': True,
    'need_categories': False,
    'need_offsets': False,
    'need_hash': False,
    'need_icons': False,
    'need_big_icons': False,}

    url = helper.base_api_url.format('TvService/GetChannels.json')
    headers = {
            'Host': 'api.sweet.tv',
            'user-agent': helper.UA,
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'pl',
            'x-device': '1;22;0;2;'+ helper.version,
            'origin': 'https://sweet.tv',
            'dnt': '1',
            'referer': 'https://sweet.tv/',
            'authorization': helper.get_setting('bearer')
            }
    acx = helper.get_setting('bearer')
    acx2 = helper.get_setting('refresh_token')

    jsdata = helper.request_sess(url, 'post', headers=headers, data = json_data, json=True, json_data = True)
    
    return jsdata
    
    
@plugin.route('/')
def root():
    CreateDatas()
        
    if helper.logged:
        startwt()

    else:
        helper.add_item('[COLOR lightgreen][B]Zaloguj[/COLOR][/B]', plugin.url_for(login),folder=False)
        helper.add_item('[B]Ustawienia[/B]', plugin.url_for(ustawienia),folder=False)

    helper.eod()

def CreateDatas():
    if not helper.uuid:
        import uuid
        uuidx = uuid.uuid4()
        helper.set_setting('uuid',to_unicode(uuidx))
    return
    
@plugin.route('/startwt')    
def startwt():
    helper.add_item('[B]TV[/B]', plugin.url_for(mainpage,id='live'),folder=True)
    helper.add_item('[B]Replay[/B]', plugin.url_for(mainpage,id='replay'),folder=True)
    helper.add_item('[B]Wyloguj[/B]', plugin.url_for(logout),folder=False)
def refreshToken():

    json_data = {
        'device': {
            'type': 'DT_Android_Player',
            'application': {
                'type': 'AT_SWEET_TV_Player',
            },
            'model': helper.UA,
            'firmware': {
                'versionCode': 1,
                'versionString': helper.version,
            },
            'uuid': helper.uuid,
            'supported_drm': {
                'widevine_modular': True,
            },
            'screen_info': {
                'aspectRatio': 6,
                'width': 1366,
                'height': 768,
            },
        },
        'refresh_token': helper.refresh_token,
    }
    jsdata = helper.request_sess(helper.token_url, 'post', headers=helper.headers, data = json_data, json=True, json_data = True)
    if jsdata.get("result", None) == 'OK':

        access_token = jsdata.get("access_token", None)

        helper.set_setting('bearer', 'Bearer '+to_unicode(access_token))

        return True
    else:
        
        return False

@plugin.route('/getEPG/<id>')
def getEPG(id):
    id,dur=id.split('|')
    timestamp = int(time.time())
    json_data = {
        "channels": [
            int(id)
        ],
        "epg_current_time": timestamp,
        "need_big_icons": False,
        "need_categories": False,
        "need_epg": True,
        "need_icons": False,
        "need_list": True,
        "need_offsets": False
    }
    url = 'https://api.sweet.tv/TvService/GetChannels.json'
    headers = {
            'Host': 'api.sweet.tv',
            'user-agent': helper.UA,
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'pl',
            'x-device': '1;22;0;2;'+ helper.version,
            'origin': 'https://sweet.tv',
            'dnt': '1',
            'referer': 'https://sweet.tv/',
            'authorization': helper.get_setting('bearer')
    }
    acx = helper.get_setting('bearer')
    acx2 = helper.get_setting('refresh_token')

    jsdata = helper.request_sess(url, 'post', headers=headers, data = json_data, json=True, json_data = True)
    print(jsdata)
    if jsdata.get("code", None) == 16:
        if jsdata.get("message", '') in ('token is expired', 'Bearer realm="auth"'):
            print('Sweet.tv', 'Odświerzam nieaktualny token logowania')
            helper.set_setting('bearer', '')
            refr = refreshToken()
            if refr:
                mainpage(id)
            else:
                return
    if jsdata.get("status", None) == 'OK':
        progs=jsdata['list'][0]['epg']
        for p in progs:
            now=int(time.time())
            tStart=p.get('time_start',None)
            if p['available']==True and tStart>=now-int(dur)*24*60*60 and tStart<=now:
                pid=str(p.get('id',None))
                tit=p.get('text',None)
                date=getTime(p.get('time_start',None),'date')
                ts=getTime(p.get('time_start',None),'hour')
                te=getTime(p.get('time_stop',None),'hour')
                title='[COLOR=gold]%s[/COLOR] | [B]%s-%s[/B] %s'%(date,ts,te,tit)
                ID=id+'|'+pid
                
                mod = plugin.url_for(playvid, id=ID)
                fold = False
                ispla = True
                imag = p.get('preview_url',None)
                art = {'icon': imag, 'fanart': helper.addon.getAddonInfo('fanart')}
                                              
                info = {'title': title, 'plot':''}
                
                helper.add_item(title, mod, playable=ispla, info=info, art=art, folder=fold, content='videos')    

    helper.eod()
            

@plugin.route('/mainpage/<id>')    
def mainpage(id):
    jsdata=channelList()
    
    if jsdata.get("code", None) == 16:
        if jsdata.get("message", '') in ('token is expired', 'Bearer realm="auth"'):
            print('Sweet.tv', 'Odświerzam nieaktualny token logowania')
            helper.set_setting('bearer', '')
            refr = refreshToken()
            if refr:
                mainpage(id)
            else:
                return
    
    if jsdata.get("status", None) == 'OK':
        for j in jsdata.get('list', []):
            catchup = j.get('catchup',None)
            available = j.get('available',None)
            isShow=False
            if (id=='replay' and catchup and available) or (id=='live' and available):
                isShow=True
            if isShow==True:
                _id = str(j.get('id',None))
                title = j.get('name',None)
                slug = j.get('slug',None)
                epgs = j.get('epg',None)
                epg =''
                if id=='live' and epgs:
                    for e in epgs:
                        if e.get('time_stop',None)>int(time.time()):
                            tit=e.get('text',None)
                            ts=getTime(e.get('time_start',None),'hour')
                            te=getTime(e.get('time_stop',None),'hour')
                            epg+='[B]%s-%s[/B] %s\n'%(ts,te,tit)

                if id=='live':
                    idx = _id+'|null'#+slug
                    mod = plugin.url_for(playvid, id=idx)
                    fold = False
                    ispla = True
                elif id=='replay':
                    dur=str(j.get('catchup_duration',None))
                    idx = _id+'|'+dur
                    mod = plugin.url_for(getEPG, id=idx)
                    fold = True
                    ispla = False
                
                imag = j.get('icon_v2_url',None)
                art = {'icon': imag, 'fanart': helper.addon.getAddonInfo('fanart')}
                     
                info = {'title': title, 'plot':epg}
                
                helper.add_item('[COLOR gold][B]'+title+'[/COLOR][/B]', mod, playable=ispla, info=info, art=art, folder=fold)    

    helper.eod()
    
@plugin.route('/empty')    
def empty():
    return

@plugin.route('/ustawienia')
def ustawienia():
    helper.open_settings()
    helper.refresh()


@plugin.route('/logout')
def logout():
    log_out = helper.dialog_choice('Uwaga','Chcesz się wylogować?',agree='TAK', disagree='NIE')
    if log_out:
        helper.set_setting('bearer', '')    
        helper.set_setting('logged', 'false')
        helper.refresh()
        
@plugin.route('/login')
def login():
    if not helper.username or not helper.password:
        helper.notification('Info', 'Brak danych logowania.\n Wpisz je w ustawieniach')
        helper.set_setting('logged', 'false')

    else:
        print('aqq')
        json_data = {
            'device': {
                'type': 'DT_Android_Player',
                'application': {
                    'type': 'AT_SWEET_TV_Player',
                },
                'model': helper.UA,
                'firmware': {
                    'versionCode': 1,
                    'versionString': helper.version,
                },
                'uuid': helper.uuid,
                'supported_drm': {
                    'widevine_modular': True,
                },
                'screen_info': {
                    'aspectRatio': 6,
                    'width': 1366,
                    'height': 768,
                },
            },
            'email': helper.username,
            'password': helper.password,
        }
        print(json_data)
        jsdata = helper.request_sess(helper.auth_url, 'post', headers=helper.headers, data = json_data, json=True, json_data = True)
        if jsdata.get("result", None) == 'OK':

            access_token = jsdata.get("access_token", None)
            refresh_token = jsdata.get("refresh_token", None)
            helper.set_setting('bearer', 'Bearer '+to_unicode(access_token))
            helper.set_setting('refresh_token', to_unicode(refresh_token))
            helper.set_setting('logged', 'true')

        else:

            info=jsdata.get('result', None)
            helper.notification('Information', info)

            helper.set_setting('logged', 'false')

    helper.refresh()

def loginTV():
    json_data = {
        "code_type": 0,
        "device": {
            "firmware": {
                "versionCode": "3810001",
                "versionString": helper.version
            },
            "is_not_supported_4K": False,
            "mac": helper.get_random_mac(),
            "screen_info": {
                "aspectRatio": "AR_16_9",
                "width": 1920,
                "height": 1080
            },
            "sub_type": "DST_Unknown",
            "supported_drm": {
                "widevine_modular": True
            },
            "type": "DT_SmartTV",
            "system_info": {},
            "application": {
                "type": "AT_SWEET_TV_Player"
            }
        }
    }
    jsdata = helper.request_sess(helper.auth_url, 'post', headers=helper.headers, data = json_data, json=True, json_data = True)
    xbmc.log('jsdata: %s' % str(jsdata), xbmc.LOGWARNING)
    auth_code = jsdata.get("auth_code")
    if jsdata.get("result") != 'OK' or not auth_code:
        helper.notification('Information', 'Błąd logowania')
        helper.set_setting('logged', 'false')
        return
    dialog = xbmcgui.Dialog()
    # show loading dialog
    pDialog = xbmcgui.DialogProgress()
    pDialog.create('sweet.tv', f"Wpisz kod {auth_code} w Moje konto > Moje urządzenia")
    # wait for user to enter code
    jsdata = {"auth_code": auth_code}
    from json import dumps
    json_data = dumps(jsdata, separators=(',', ':'))
    result = None
    headers = {
        **helper.headers,
        'Content-Type': 'application/json',
    }

    time_to_wait=340 
    while not result:
        if pDialog.iscanceled():
            helper.notification('Information', 'Logowanie przerwane')
            helper.set_setting('logged', 'false')
            return
        jsdata = helper.request_sess(helper.check_auth_url, 'post', headers=headers, data = json_data, json=True, json_data = False)
        sys.stderr.write(str(jsdata))
        if jsdata.get("result") == "COMPLETED":
            result = jsdata
        else:
            time.sleep(3)
            time_to_wait -= 3
            if time_to_wait < 0:
                result = {'result': 'Logowanie przerwane'}
                helper.set_setting('logged', 'false')

    if result.get("result") == 'COMPLETED':
        access_token = result.get("access_token")
        refresh_token = result.get("refresh_token")
        helper.set_setting('bearer', 'Bearer '+to_unicode(access_token))
        helper.set_setting('refresh_token', to_unicode(refresh_token))
        helper.set_setting('logged', 'true')
    else:
        info=jsdata.get('result')
        helper.notification('Information', info)
        helper.set_setting('logged', 'false')
    helper.refresh()

@plugin.route('/playvid/<id>')
def playvid(id):
    if not helper.get_setting('logged'):
        xbmcgui.Dialog().notification('Sweet.tv', 'Zaloguj się we wtyczce', xbmcgui.NOTIFICATION_INFO)
        xbmcplugin.setResolvedUrl(helper.handle, False, xbmcgui.ListItem())
    else:
        idx,pid = id.split('|')
        json_data = {
            'without_auth': False,
            'channel_id': int(idx),
            #'accept_scheme': ['HTTP_HLS',],
            'multistream': True,
        }
        vod=False
        if pid!='null':
            json_data.update({'epg_id':int(pid)})
            vod=True
        
        headers = {
                'Host': 'api.sweet.tv',
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36', #helper.UA,
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'pl',
                'x-device': '1;22;0;2;4.7.06', #+ helper.version,
                'origin': 'https://sweet.tv',
                'dnt': '1',
                'referer': 'https://sweet.tv/',
                'authorization': helper.get_setting('bearer')
        }
                
        url = helper.base_api_url.format('TvService/OpenStream.json')
        jsdata = helper.request_sess(url, 'post', headers=headers, data = json_data, json=True, json_data = True)

        if jsdata.get("code", None) == 16:
            print('playvid() jsdata returned:',jsdata)
            if jsdata.get("message", '') in ('token is expired', 'Bearer realm="auth"'):
                print('Sweet.tv', 'Odświerzam nieaktualny token logowania')
                helper.set_setting('bearer', '')
                refr = refreshToken()
                if refr:
                    playvid(id)
                else:
                    return

        if jsdata.get("code", None) == 13:
            xbmcgui.Dialog().notification('Sweet.tv', 'Nagranie niedostępne', xbmcgui.NOTIFICATION_INFO)
            xbmcplugin.setResolvedUrl(helper.handle, False, xbmcgui.ListItem())
        if jsdata.get("result", None) == 'OK':
            print('Sweet.tv', 'Dane z API pobrane poprawnie')
            host = jsdata.get('http_stream', None).get('host', None).get('address', None)
            nt = jsdata.get('http_stream', None).get('url', None)
            stream_url = 'https://'+host+nt
            if jsdata.get('scheme', None)=='HTTP_DASH':
                if jsdata.get('drm_type', None)=='DRM_WIDEVINE':
                    licURL=jsdata.get('license_server', None)
                    hea_lic={
                        'User-Agent':helper.UA,
                        'origin': 'https://sweet.tv',
                        'referer': 'https://sweet.tv/'
                    }
                    lic_url='%s|%s|R{SSM}|'%(licURL,urlencode(hea_lic))
                    DRM='com.widevine.alpha'
                else:
                    lic_url = None
                    DRM = None
                PROTOCOL='mpd'                
                subs =None
            
            elif jsdata.get('scheme', None)=='HTTP_HLS':
                lic_url = None
                mpdurl =''
                DRM = None
                PROTOCOL = 'hls'
                subs =None
            
            if helper.get_setting('playerType')=='ffmpeg' and DRM==None:
                m3u8data = helper.request_sess(stream_url, headers=headers)
                #print('playvid() m3u8data:',m3u8data)
                lines = m3u8data.splitlines()
                for line in lines:
                    if line.startswith('http'):
                        stream_url = line
                #print('playvid() m3u8data stream_url:',stream_url)
                stream_url = stream_url.replace('api.sweet.tv', host)
                #print('playvid() final stream_url:',stream_url)
                helper.ffmpeg_player(stream_url)
            else:
                helper.PlayVid(stream_url, lic_url, PROTOCOL, DRM, flags=False, subs = subs,vod=vod)

@plugin.route('/listM3U')
def listM3U():
    if helper.get_setting('logged'):
        file_name = helper.get_setting('fname')
        path_m3u = helper.get_setting('path_m3u')
        if file_name == '' or path_m3u == '':
            xbmcgui.Dialog().notification('Sweet.tv', 'Podaj nazwę pliku oraz katalog docelowy.', xbmcgui.NOTIFICATION_ERROR)
            return
        xbmcgui.Dialog().notification('Sweet tv', 'Generuję listę M3U.', xbmcgui.NOTIFICATION_INFO)
        data = '#EXTM3U\n'
        dataE2 = '' #j00zek for E2 bouquets
        channels=channelList()
        if channels.get("code", None) == 16:
            if channels.get("message", '') in ('token is expired', 'Bearer realm="auth"'):
                xbmcgui.Dialog().notification('Sweet tv', 'Token już wygasł, próbuję odświerzyć', xbmcgui.NOTIFICATION_INFO)
                helper.set_setting('bearer', '')
                refr = refreshToken()
                if refr:
                    channels=channelList()
                else:
                    xbmcgui.Dialog().notification('Sweet tv', 'Próba odświerzenia tokena nieudana, koniec  :(', xbmcgui.NOTIFICATION_INFO)
                    return
        channelsCount = 0
        if 'list' in channels:
            for c in channels['list']:
                if c.get('available',None):
                    img=c.get('icon_v2_url',None)
                    cName=c.get('name','')
                    cid=str(c.get('id',''))
                    if cid.strip() != '' and cName.strip() != '':
                        channelsCount += 1
                        data += '#EXTINF:0 tvg-id="%s" tvg-logo="%s" group-title="Sweet.tv" ,%s\nplugin://plugin.video.sweettvpl/playvid/%s|null\n' %(cName,img,cName,cid)
                        dataE2 += 'plugin.video.sweettvpl/main.py%3fmode=playtvs&url=' + '%s:%s\n' % (cid, cName) #j00zek for E2 bouquets
            if channelsCount > 0:
                f = xbmcvfs.File(path_m3u + file_name, 'w')
                f.write(data)
                f.close()
                xbmcgui.Dialog().notification('Sweet.tv', 'Wygenerowano listę M3U', xbmcgui.NOTIFICATION_INFO)

                f = xbmcvfs.File(os.path.join(path_m3u, 'iptv.e2b'), 'w') #j00zek for E2 bouquets
                f.write(dataE2)
                f.close()
                xbmcgui.Dialog().notification('Sweet.tv', 'Wygenerowano listę E2B', xbmcgui.NOTIFICATION_INFO)
            else:
                xbmcgui.Dialog().notification('Sweet.tv', 'System zwrócił pustą listę kanałów', xbmcgui.NOTIFICATION_INFO)
            
    else:
        xbmcgui.Dialog().notification('Sweet.tv', 'Zaloguj się we wtyczce', xbmcgui.NOTIFICATION_INFO)

class SweetTV(Helper):
    def __init__(self):
        super().__init__()
        plugin.run()
