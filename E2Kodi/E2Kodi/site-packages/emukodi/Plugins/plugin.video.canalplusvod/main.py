# -*- coding: UTF-8 -*-
import warnings
warnings.filterwarnings("ignore")

#from __future__ import absolute_import
import sys, re, os

from emukodi import xbmcgui
from emukodi import xbmcplugin
from emukodi import xbmcaddon
from emukodi import xbmc
from emukodi import xbmcvfs

try:
    import http.cookiejar
    import urllib.request, urllib.parse, urllib.error
    from urllib.parse import urlencode, quote_plus, quote, unquote, parse_qsl
    LOGNOTICE = xbmc.LOGINFO

except ImportError:
    import cookielib
    import urllib
    import urlparse
    from urllib import urlencode, quote_plus, quote, unquote
    from urlparse import parse_qsl
    LOGNOTICE = xbmc.LOGNOTICE    

import requests
import urllib3
import base64

#try:
#    from urllib3.util.ssl_ import DEFAULT_CIPHERS
#except ImportError:
#    # Defer to system configuration starting with
#    # urllib3 2.0. This will choose the ciphers provided by
#    # Openssl 1.1.1+ or secure system defaults.
#    DEFAULT_CIPHERS = (
#        'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
#        'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:'
#        '!eNULL:!MD5')

requests.packages.urllib3.disable_warnings()

#requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
#try:
#    requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
#except AttributeError:
#    # no pyopenssl support used / needed / available
#    pass
#import ssl
#try:
#    _create_unverified_https_context = ssl._create_unverified_context
#except AttributeError:
#    pass
#else:
#    ssl._create_default_https_context = _create_unverified_https_context

from requests.packages.urllib3.util.ssl_ import create_urllib3_context
class CustomCipherAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers="DEFAULT:!DHE:!SHA1:!SHA256:!SHA384")
        context.set_ecdh_curve("prime256v1")
        kwargs['ssl_context'] = context
        return super(CustomCipherAdapter, self).init_poolmanager(*args, **kwargs)

sess = requests.Session()
sess.mount("https://", CustomCipherAdapter())


import json
import inputstreamhelper
import datetime
import time

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon(id='plugin.video.canalplusvod')

PATH = addon.getAddonInfo('path')
RESOURCES = PATH + '/resources/'

ikona = RESOURCES + '../icon.png'
FANART = RESOURCES + '../fanart.jpg'
sys.path.append( os.path.join( RESOURCES, "lib" ) )

exlink = params.get('url', None)
name = params.get('name', None)
page = params.get('page','')
rys = params.get('image', None)

kukz = ''

TIMEOUT = 15

#sess = requests.Session()
proxyport = addon.getSetting('proxyport')

PATH_profile=xbmcvfs.translatePath(addon.getAddonInfo('profile'))
if not xbmcvfs.exists(PATH_profile):
    xbmcvfs.mkdir(PATH_profile)
    
UAweb='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'

def build_url(query):
    try:
        urlencode = urllib.urlencode(query)
    except:
        urlencode = urllib.parse.urlencode(query)

    return base_url + '?' + urlencode

def add_item(url, name, image, mode, folder=False, IsPlayable=False, infoLabels=False, movie=True, itemcount=1, page=1, fanart=FANART, moviescount=0, contMenu=False, CM=None):
    list_item = xbmcgui.ListItem(label=name)

    if IsPlayable:
        list_item.setProperty("IsPlayable", 'True')

    if not infoLabels:
        infoLabels={'title': name,'plot':name}

    list_item.setInfo(type="video", infoLabels=infoLabels)    
    list_item.setArt({'thumb': image, 'poster': image, 'banner': image, 'fanart': FANART})
    
    if contMenu:
        #cMenu = []
        #cMenu.append((CM))
        cMenu=CM
        list_item.addContextMenuItems(cMenu, replaceItems=False)
    
    ok = xbmcplugin.addDirectoryItem(
        handle = addon_handle,
        url = build_url({'mode': mode, 'url' : url, 'page' : page, 'moviescount' : moviescount,'movie':movie,'name':name,'image':image}),            
        listitem = list_item,
        isFolder = folder)

    return ok
    
def setView(typ):
    if addon.getSetting('auto-view') == 'false':
        xbmcplugin.setContent(addon_handle, 'videos')
    else:
        xbmcplugin.setContent(addon_handle, typ)
    
def home(): #2023-07-21
    if CANALvod().LOGGED != 'true':
        #CANALvod().logowanie()
        add_item('', '[B][COLOR blue]Zaloguj[/COLOR][/B]', ikona, "login", folder=False,fanart=FANART)
    else:
        add_item(CANALvod().mainPage, '[B][COLOR green]Strona Główna[/COLOR][/B]', ikona, "listContent", folder=True, IsPlayable=False, infoLabels=False, fanart=FANART)

        add_item('', '[B][COLOR blue]Kanały TV[/COLOR][/B]', ikona, "listkanaly", folder=True, IsPlayable=False, infoLabels=False, fanart=FANART)
        add_item('', '[B][COLOR blue]VOD[/COLOR][/B]', ikona, "listvodmenu", folder=True, IsPlayable=False, infoLabels=False, fanart=FANART)

        add_item('', '[B][COLOR khaki]Szukaj[/COLOR][/B]', ikona, "szukaj", folder=True, fanart=FANART)
        add_item('', 'Opcje', ikona, "opcje", folder=False, fanart=FANART)
        add_item('', 'Kreator listy M3U', ikona, "kreatorm3u", folder=True, fanart=FANART)
        add_item('', 'Ulubione', ikona, "favList", folder=True, fanart=FANART)#
        add_item('', '[B][COLOR blue]Wyloguj[/COLOR][/B]', ikona, "logout", folder=False,fanart=FANART)

    xbmcplugin.endOfDirectory(addon_handle)

def ListVodMenu():
    add_item(CANALvod().cinemaURL, '[B][COLOR blue]Filmy[/COLOR][/B]', ikona, "listContent", folder=True, IsPlayable=False, infoLabels=False, fanart=FANART)
    add_item(CANALvod().seriesURL, '[B][COLOR blue]Seriale[/COLOR][/B]', ikona, "listContent", folder=True, IsPlayable=False, infoLabels=False, fanart=FANART)
    add_item(CANALvod().kidsURL, '[B][COLOR blue]Dzieci[/COLOR][/B]', ikona, "listContent", folder=True, IsPlayable=False, infoLabels=False, fanart=FANART)
    add_item(CANALvod().lifeURL, '[B][COLOR blue]Lifestyle[/COLOR][/B]', ikona, "listContent", folder=True, IsPlayable=False, infoLabels=False, fanart=FANART)
    #add_item(CANALvod().documentsURL, '[B][COLOR blue]Dokumenty[/COLOR][/B]', ikona, "listContent", folder=True, IsPlayable=False, infoLabels=False, fanart=FANART)
    #add_item(CANALvod().demandURL, '[B][COLOR blue]Kanały na życzenie[/COLOR][/B]', ikona, "listContent", folder=True, IsPlayable=False, infoLabels=False, fanart=FANART)
    add_item(CANALvod().documentsURL, '[B][COLOR blue]Dokumenty[/COLOR][/B]', ikona, "listContent", folder=True, IsPlayable=False, infoLabels=False, fanart=FANART)
    add_item(CANALvod().sportURL, '[B][COLOR blue]Sport[/COLOR][/B]', ikona, "listContent", folder=True, IsPlayable=False, infoLabels=False, fanart=FANART)
    add_item(CANALvod().collectionsURL, '[B][COLOR blue]Kolekcje[/COLOR][/B]', ikona, "listContent", folder=True, IsPlayable=False, infoLabels=False, fanart=FANART)
    add_item(CANALvod().demandURL, '[B][COLOR blue]Kanały na życzenie[/COLOR][/B]', ikona, "listDemand", folder=True, IsPlayable=False, infoLabels=False, fanart=FANART)
    #  setView('videos')
    xbmcplugin.endOfDirectory(addon_handle) 

def ListKanaly():
    items = CANALvod().TVinit()
    if items:
        fold = True
        mud = 'listContent'
        ispla = False
        for item in items:
            if item['typ'] == 'live':
                fold = False
                mud = 'playCANvod'
                ispla = True
            add_item(item['url'], item['title'], item['image'], mud, folder=fold, IsPlayable=ispla, infoLabels={'title':item['title'], 'image': item['image'], 'plot':item['plot']},fanart=FANART)

    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%Y")
    xbmcplugin.endOfDirectory(addon_handle) 

def KreatorM3U():
    import playlist
    dialog = xbmcgui.Dialog()
    addon = xbmcaddon.Addon()
    try:
        profile = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    except:
        profile = xbmc.translatePath(addon.getAddonInfo('profile'))
    fn = dialog.browse(0, "Wskaż lokalizację zapisu listy", profile)
    if fn != "":
        profile = fn
    m3u8 = playlist.Playlist('canalPLUS-VOD')
    count = 1
    items  = CANALvod().TVinit()
    if items:
        fold = True
        mud = 'listContent'
        ispla = False
        for item in items:
            if item['typ'] == 'live':
                fold = False
                mud = 'playCANvod'
                ispla = True
            title = item['title'].lower()

            item['title'] = item['title'].replace("EUROSPORT", "EUROSPORT ")

            grouptitle = "INNE"
            if title.__contains__("canal") | title.__contains__("hbo") | title.__contains__("film") | title.__contains__("kino") | title.__contains__("paramount") | title.__contains__("tnt"):
                grouptitle = "FILM"
            if title.__contains__("serial") | title.__contains__("comedy") | title.__contains__("fox") | title.__contains__("axn") | title.__contains__("sci fi") | title.__contains__("novelas"):
                grouptitle = "SERIAL"
            if title.__contains__("dokument") | title.__contains__("planete") | title.__contains__("national") | title.__contains__("nat geo") | title.__contains__("earth") | title.__contains__("history") | title.__contains__("crime") | title.__contains__("discovery"):
                grouptitle = "DOKUMENT"
            if title.__contains__("lifestyle") | title.__contains__("domo") | title.__contains__("kuchnia") | title.__contains__("brit") | title.__contains__("hgtv") | title.__contains__("style") | title.__contains__("turbo") | title.__contains__("tlc") | title.__eq__("e"):
                grouptitle = "LIFESTYLE"
            if title.__contains__("sport") | title.__contains__("fight") | title.__contains__("+ now") | title.__contains__("event"):
                grouptitle = "SPORT"
            if title.__contains__("info") | title.__contains__("24") | title.__contains__("cnn") | title.__contains__("news") | title.__contains__("welle") | title.__contains__("cnbc") | title.__contains__("biznes"):
                grouptitle = "INFORMACJE"
            if title.__contains__("mtv") | title.__contains__("vh1") | title.__contains__("4fun") | title.__contains__("power") | title.__contains__("nuta"):
                grouptitle = "MUZYKA"
            if title.__contains__("mini") | title.__contains__("cbee") | title.__contains__("disney") | title.__contains__("nick") | title.__contains__("cartoon") | title.__contains__("boomerang") | title.__contains__("teletoon") | title.__contains__("kids"):
                grouptitle = "BAJKI"
            if title.__contains__("tvp 3"):
                grouptitle = "OGÓLNE"
            canalurl = build_url({'name': item['title'],'moviescount': 0,'url': item['url'],'image': item['image'],'movie': True,'mode': mud,'page': page})
            m3u8.addM3UChannel(count, item['title'], item['image'], grouptitle, count, canalurl)
            count += 1
        with open(profile + 'canalPLUS-VOD.m3u8', 'w+', encoding='utf-8') as m3ufile:
            m3ufile.write(m3u8.getM3UList())
        xbmcgui.Dialog().notification('[B]Wykonano[/B]', 'Lista zapisana', xbmcgui.NOTIFICATION_INFO, 8000)
    
def jsonrpc(**kwargs):
    """ Perform JSONRPC calls """
    from json import dumps, loads
    if kwargs.get('id') is None:
        kwargs.update(id=0)
    if kwargs.get('jsonrpc') is None:
        kwargs.update(jsonrpc='2.0')
    return loads(xbmc.executeJSONRPC(dumps(kwargs)))
    
def get_global_setting(setting):
    """ Get a Kodi setting """
    result = jsonrpc(method='Settings.GetSettingValue', params=dict(setting=setting))
    return result.get('result', {}).get('value')
    
def getMaxBand():
    # def get_max_bandwidth(self):
    """ Get the max bandwidth based on Kodi and add-on settings """
    addon_max_bandwidth = int(addon.getSetting('maxband'))
    global_max_bandwidth = int(get_global_setting('network.bandwidth'))
    if addon_max_bandwidth != 0 and global_max_bandwidth != 0:
        return min(addon_max_bandwidth, global_max_bandwidth)
    if addon_max_bandwidth != 0:
        return addon_max_bandwidth
    if global_max_bandwidth != 0:
        return global_max_bandwidth
    return 0
    
def PLAYvodCANAL(urlid):
    CANALvod().RefreshLIVEtoken()
    url,id_ = urlid.split('|')
    
    headers2 = {

        'User-Agent': UAweb,
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,pl;q=0.8',
    }
    
    headers = {

        'Accept': 'application/json, text/plain, */*',
        'User-Agent': UAweb,
        'Origin': 'https://www.canalplus.com',
        'Accept-Language': 'en-US,en;q=0.9,pl;q=0.8',
    }

    response = requests.get(url, headers=headers).text
    if '.wsx?' in url:
        str_url = re.findall('src="([^"]+)"',response)[0]
    else:
        try:
            dt = json.loads(response)
            str_url = dt.get("dvr", None).get('src', None)
        except:
            pre_regex = re.compile(r'<pre>(.*?)</pre>')
            r = pre_regex.search(response)
            msg = r.group(1) if r else response
            xbmcgui.Dialog().ok('Canal+ VOD Error', msg)
            return

    stream_url = requests.get(str_url, headers=headers2).url
    stream_url = re.sub(r'(\?token.+?)$','/manifest',stream_url)
    #xbmc.log('@#@requests: %s' % str(url), LOGNOTICE)
    
    data = quote('{"ServiceRequest":{"InData":{"EpgId":'+id_+',"Mode":"MKPL","LiveToken":"'+ CANALvod().LIVEtoken+'","UserKeyId":"'+CANALvod().DEVICE_ID+'","DeviceKeyId":"'+CANALvod().DEVID+'","ChallengeInfo":"b{SSM}"}}}')
    
    headers3 = {
        'Host': 'secure-webtv.canal-plus.com',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': UAweb,
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://www.canalplus.com',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',

        'Accept-Language': 'en-US,en;q=0.9,pl;q=0.8',
    }
    
    PROTOCOL = 'mpd'
    DRM = 'com.widevine.alpha'

    PROXY_PATH = 'http://127.0.0.1:%s/licensetv='%(proxyport)

    offer_zone = 0
    drm_id = 0

    abtv = "https://secure-webtv.canal-plus.com/WebPortal/ottlivetv/api/V4/zones/cppol/devices/31/apps/1/jobs/GetLicence"
    set_setting('heatv', str(headers3))
    set_setting('lictvurl', str(abtv))

    url = PROXY_PATH + abtv

    LICKEY =  url+"|"+urlencode(headers3)+"|"+data+"|B"

    certificate_data = base64.b64encode(requests.get('https://secure-webtv-static.canal-plus.com/widevine/cert/cert_license_widevine_com.bin').content).decode('utf-8')

    is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
    if is_helper.check_inputstream():
        play_item = xbmcgui.ListItem(path=stream_url)
        play_item.setMimeType('application/dash+xml')
        play_item.setContentLookup(False)
        
        if sys.version_info >= (3,0,0):
            play_item.setProperty('inputstream', is_helper.inputstream_addon)
        else:
            play_item.setProperty('inputstreamaddon', is_helper.inputstream_addon)

        play_item.setProperty("IsPlayable", "true")

        play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
        play_item.setProperty('inputstream.adaptive.manifest_headers', 'User-Agent='+UAweb)
        play_item.setProperty('inputstream.adaptive.stream_headers', 'User-Agent='+UAweb)
        play_item.setProperty('inputstream.adaptive.license_type', DRM)
        play_item.setProperty('inputstream.adaptive.license_key',LICKEY) 

        xbmc.log('AQQ: ==START==', xbmc.LOGWARNING)
        xbmc.log('AQQ: stream_url %r' % stream_url, xbmc.LOGWARNING)
        xbmc.log('AQQ: manifest_type %r' % play_item.getProperty('inputstream.adaptive.manifest_type'), xbmc.LOGWARNING)
        xbmc.log('AQQ: manifest_headers %r' % play_item.getProperty('inputstream.adaptive.manifest_headers'), xbmc.LOGWARNING)
        xbmc.log('AQQ: stream_headers %r' % play_item.getProperty('inputstream.adaptive.stream_headers'), xbmc.LOGWARNING)
        xbmc.log('AQQ: license_type %r' % play_item.getProperty('inputstream.adaptive.license_type'), xbmc.LOGWARNING)
        xbmc.log('AQQ: license_key %r' % play_item.getProperty('inputstream.adaptive.license_key'), xbmc.LOGWARNING)
        open("c:\\Users\\akpar\\AppData\\Roaming\\Kodi\\cplus.log", "a").write('==START==')
        open("c:\\Users\\akpar\\AppData\\Roaming\\Kodi\\cplus.log", "a").write('stream_url %r' % stream_url)
        open("c:\\Users\\akpar\\AppData\\Roaming\\Kodi\\cplus.log", "a").write('manifest_type %r' % play_item.getProperty('inputstream.adaptive.manifest_type'))
        open("c:\\Users\\akpar\\AppData\\Roaming\\Kodi\\cplus.log", "a").write('manifest_headers %r' % play_item.getProperty('inputstream.adaptive.manifest_headers'))
        open("c:\\Users\\akpar\\AppData\\Roaming\\Kodi\\cplus.log", "a").write('stream_headers %r' % play_item.getProperty('inputstream.adaptive.stream_headers'))
        open("c:\\Users\\akpar\\AppData\\Roaming\\Kodi\\cplus.log", "a").write('license_type %r' % play_item.getProperty('inputstream.adaptive.license_type'))
        open("c:\\Users\\akpar\\AppData\\Roaming\\Kodi\\cplus.log", "a").write('license_key %r' % play_item.getProperty('inputstream.adaptive.license_key'))

        if get_setting('drmcert') == 'true':
            play_item.setProperty('inputstream.adaptive.server_certificate',certificate_data)
            xbmc.log('AQQ: server_certificate %r' % play_item.getProperty('inputstream.adaptive.server_certificate'), xbmc.LOGWARNING)

        xbmc.log('AQQ: ==END==', xbmc.LOGWARNING)

        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)    

def PLAYvod2(urlid):
    HAPI_BASE_URL = 'https://secure-gen-hapi.canal-plus.com'
    HAPI_BASE_URL2 = 'https://secure-mycanal-player-pc-ws3.canal-plus.com'

    URL_VIDEO_DATAS = 'https://secure-gen-hapi.canal-plus.com/conso/playset/unit/%s'
    URL_STREAM_DATAS = 'https://secure-gen-hapi.canal-plus.com/conso/view'
    URL_DEVICE_ID = 'https://pass.canal-plus.com/service/HelloJSON.php'

    video_id = urlid.split('|')[-1]
    CANALvod().RefreshPassToken()
    value_pass_token = 'PASS Token="%s"' % quote(CANALvod().PASStoken)

    headers = {
        'User-Agent': UAweb,
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'pl,pl-PL',
        'XX-DOMAIN': 'cppol',
        'XX-OZ': 'cppol',
        'XX-OL': 'pl',
        'XX-SERVICE': 'mycanal',
        'XX-OPERATOR': 'pc',
        'XX-API-VERSION': '3.0',
        'XX-SPYRO-VERSION': '3.0',

        'Authorization': value_pass_token,
        'XX-Profile-Id': '0',
        'XX-DEVICE': 'pc %s' % CANALvod().DEVID,
        'Origin': 'https://www.canalplus.com',
        'Connection': 'keep-alive',}

    URL_VIDEO_DATAS2='https://secure-gen-hapi.canal-plus.com/conso/playset/unit/%s'%(video_id)

    # z chrome
    URL_VIDEO_DATASx = URL_VIDEO_DATAS % video_id
    xbmc.log('@#@URL_VIDEO_DATAS: %s' % str(URL_VIDEO_DATASx), LOGNOTICE)

    value_datas_json = sess.get(URL_VIDEO_DATAS2, headers=headers )
    a = value_datas_json.text

    value_datas_jsonparser = json.loads(value_datas_json.text)

    comMode_value = ''
    contentId_value = ''
    distMode_value = ''
    distTechnology_value = ''
    drmType_value = ''
    functionalType_value = ''
    hash_value = ''
    idKey_value = ''
    quality_value = ''
    if 'available' not in value_datas_jsonparser:
        info=': '+value_datas_jsonparser['message'] if 'message' in value_datas_jsonparser else ''
        xbmcgui.Dialog().notification('Canal+', 'Materiał niedostępny'+info, xbmcgui.NOTIFICATION_INFO)
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
    else:
        for stream_datas in value_datas_jsonparser["available"]:
           # if 'DRM_COMMON_ENCRYPTION' in stream_datas["drmType"]:
            if 'DRM_WIDEVINE' in stream_datas["drmType"]:
                comMode_value = stream_datas['comMode']
                contentId_value = stream_datas['contentId']
                distMode_value = stream_datas['distMode']
                distTechnology_value = stream_datas['distTechnology']
                drmType_value = stream_datas['drmType']
                functionalType_value = stream_datas['functionalType']
                hash_value = stream_datas['hash']
                idKey_value = stream_datas['idKey']
                quality_value = stream_datas['quality']
        
        payload = {
            'comMode': comMode_value,
            'contentId': contentId_value,
            'distMode': distMode_value,
            'distTechnology': distTechnology_value,
            'drmType': drmType_value,
            'functionalType': functionalType_value,
            'hash': hash_value,
            'idKey': idKey_value,
            'quality': quality_value,
            'contentType':distMode_value
        }

        resp_stream_datas = sess.put(URL_STREAM_DATAS, json=payload, headers=headers)
        jsonparser_stream_datas = json.loads(resp_stream_datas.text)
        print(jsonparser_stream_datas)
        if '@medias' not in jsonparser_stream_datas:
            xbmcgui.Dialog().notification('Canal+', 'Materiał niedostępny', xbmcgui.NOTIFICATION_INFO)
            xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
        else:
            resp_real_stream_datas = sess.get(HAPI_BASE_URL + jsonparser_stream_datas['@medias'], headers=headers)
            jsonparser_real_stream_datas = json.loads(resp_real_stream_datas.text)

            stream_urls = jsonparser_real_stream_datas[0]['files']
            for st_url in stream_urls:
                if '.ism' in st_url["distribURL"]:
                    stream_url = st_url["distribURL"] + '/manifest'
                else:
                    continue

            headers2 = {
                'Accept': 'application/json, text/plain, */*',#quote('application/json, text/plain, */*'),
                'Authorization': value_pass_token,
                'Content-Type': 'text/plain',
                'User-Agent': UAweb,##quote('Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0'),
                'XX-DEVICE': 'pc %s' % CANALvod().DEVID,
                'XX-DOMAIN': 'cppol',
                'XX-OPERATOR': 'pc',
                'XX-Profile-Id': '0',
                'XX-SERVICE': 'mycanal',
                'XX-API-VERSION':'3.0',
                'XX-SPYRO-VERSION':'3.0',
                'XX-OL':'pl',
                'XX-DISTMODES':'catchup,live,svod,tvod,posttvod',#quote('catchup,live,svod,tvod,posttvod')
                'Origin':'https://www.canalplus.com'
            }

            PROTOCOL = 'ism'
            DRM = 'com.widevine.alpha'

            is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)

            PROXY_PATH = 'http://127.0.0.1:%s/license=' % (proxyport)
            ab = HAPI_BASE_URL+jsonparser_stream_datas['@licence']+ '?drmConfig=mkpl::true'#&drmType=DRM_WIDEVINE'#'

            set_setting('hea', str(headers2))
            set_setting('licurl', str(ab))
            
            certificate_data = base64.b64encode(requests.get('https://secure-webtv-static.canal-plus.com/widevine/cert/cert_license_widevine_com.bin').content).decode('utf-8')#

            url = PROXY_PATH + ab
            if is_helper.check_inputstream():
                play_item = xbmcgui.ListItem(path=stream_url)

                play_item.setContentLookup(False)
                if sys.version_info >= (3,0,0):
                    play_item.setProperty('inputstream', is_helper.inputstream_addon)
                else:
                    play_item.setProperty('inputstreamaddon', is_helper.inputstream_addon)
                    
                if get_setting('drmcert') == 'true':
                    play_item.setProperty('inputstream.adaptive.server_certificate',certificate_data)
                
                play_item.setProperty("IsPlayable", "true")
                play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
                play_item.setProperty('inputstream.adaptive.manifest_headers', 'User-Agent='+UAweb)
                play_item.setProperty('inputstream.adaptive.stream_headers', 'User-Agent='+UAweb)
                play_item.setProperty('inputstream.adaptive.license_type', DRM)
                play_item.setProperty('inputstream.adaptive.license_key',url + '|%s|b{SSM}|B' % urlencode(headers2) )

            xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

def getInfoLabel(item):
    out={}
    out['plot'] = item['plot'] if item['plot'] else item['title']
    if 'chGroup' in item:
        out['plot']+='\n[I]('+item['chGroup']+')[/I]'
    out['title'] = item['title']

    return out
    
def ListDemand(url):
    items  = CANALvod().getContentDemand(url)
    if items:
        for item in items:
            inflabel = getInfoLabel(item)

            if item['typ'] == 'VoD':
                fold = False
                mud ='playCANvod2'
                ispla = True
            else:
                fold = True
                mud = 'listContent'
                ispla = False
            img1 = item['image'] if item['image'] else ikona
            if not 'objectType=person' in item['url']:
                add_item(item['url'], item['title'], img1, mud, folder=fold, IsPlayable=ispla, infoLabels=inflabel, fanart=FANART)
        if mud != 'listContent':
            setView('movies')

    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%Y")
    xbmcplugin.endOfDirectory(addon_handle) 
    
def getOuts(typ):
    import base64
    filmyout = 'W3sicGxvdCI6ICIiLCAiY29kZSI6ICIiLCAidGl0bGUiOiAiV3N6eXN0a2llIGZpbG15IiwgInVybCI6ICJodHRwczovL2hvZG9yLmNhbmFscGx1cy5wcm8vYXBpL3YyL215Y2FuYWxpbnQvcGFnZS97fS8xMDQ4MTkuanNvbj9wYXJhbXMlNUJkZXRhaWxUeXBlJTVEPWNvbnRlbnRHcmlkJm9iamVjdFR5cGU9bGlzdCZwYXJhbXMlNUJkc3AlNUQ9Z2FiYXJpdExpc3QmcGFyYW1zJTVCc2RtJTVEPXNob3cmdGl0bGVEaXNwbGF5TW9kZT1ub25lJnByZXZpb3VzQ29udGV4dERldGFpbD1pbnRlci10aGVtZS1maWxtLTItY29udGVudHJvdy1uY3BsdXMtb3VhaC1maWxteS1tZW51JnBhcmFtcyU1QnRhYiU1RD0lMkZ3c3p5c3RraWUtZmlsbXklMkZoJTJGbmNwbHVzLW91YWgtZmlsbXktYWxsfG5jcGx1cy1vdWFoLWZpbG15LWFsbCIsICJpbWFnZSI6ICJodHRwczovL3RodW1iLmNhbmFscGx1cy5wcm8vaHR0cC91bnNhZmUve3Jlc29sdXRpb25YWX0vZmlsdGVyczpxdWFsaXR5KDcwKS9uY3BsdXMtY2RuLmNhbmFsLXBsdXMuaW8vcDEvbGlzdC9uY3BsdXMtb3VhaC1maWxteS1hbGwvbmNwbHVzLW91YWgvU1REL3dzenlzdGtpZWZpbG15IiwgInR5cCI6ICJmb2xkZXIifSwgeyJwbG90IjogIiIsICJjb2RlIjogIiIsICJ0aXRsZSI6ICJBa2NqYSIsICJ1cmwiOiAiaHR0cHM6Ly9ob2Rvci5jYW5hbHBsdXMucHJvL2FwaS92Mi9teWNhbmFsaW50L3BhZ2Uve30vMTA0ODE5Lmpzb24/cGFyYW1zJTVCZGV0YWlsVHlwZSU1RD1jb250ZW50R3JpZCZvYmplY3RUeXBlPWxpc3QmcGFyYW1zJTVCZHNwJTVEPWdhYmFyaXRMaXN0JnBhcmFtcyU1QnNkbSU1RD1zaG93JnRpdGxlRGlzcGxheU1vZGU9bm9uZSZwcmV2aW91c0NvbnRleHREZXRhaWw9aW50ZXItdGhlbWUtZmlsbS0yLWNvbnRlbnRyb3ctbmNwbHVzLW91YWgtZmlsbXktbWVudSZwYXJhbXMlNUJ0YWIlNUQ9JTJGYWtjamElMkZoJTJGbmNwbHVzLW91YWgtZmlsbXktYWtjaml8bmNwbHVzLW91YWgtZmlsbXktYWtjamkiLCAiaW1hZ2UiOiAiaHR0cHM6Ly90aHVtYi5jYW5hbHBsdXMucHJvL2h0dHAvdW5zYWZlL3tyZXNvbHV0aW9uWFl9L2ZpbHRlcnM6cXVhbGl0eSg3MCkvbmNwbHVzLWNkbi5jYW5hbC1wbHVzLmlvL3AxL2xpc3QvbmNwbHVzLW91YWgtZmlsbXktYWtjamkvbmNwbHVzLW91YWgvU1REL0FrY2ppIiwgInR5cCI6ICJmb2xkZXIifSwgeyJwbG90IjogIiIsICJjb2RlIjogIiIsICJ0aXRsZSI6ICJQcnp5Z29kb3d5IiwgInVybCI6ICJodHRwczovL2hvZG9yLmNhbmFscGx1cy5wcm8vYXBpL3YyL215Y2FuYWxpbnQvcGFnZS97fS8xMDQ4MTkuanNvbj9wYXJhbXMlNUJkZXRhaWxUeXBlJTVEPWNvbnRlbnRHcmlkJm9iamVjdFR5cGU9bGlzdCZwYXJhbXMlNUJkc3AlNUQ9Z2FiYXJpdExpc3QmcGFyYW1zJTVCc2RtJTVEPXNob3cmdGl0bGVEaXNwbGF5TW9kZT1ub25lJnByZXZpb3VzQ29udGV4dERldGFpbD1pbnRlci10aGVtZS1maWxtLTItY29udGVudHJvdy1uY3BsdXMtb3VhaC1maWxteS1tZW51JnBhcmFtcyU1QnRhYiU1RD0lMkZwcnp5Z29kb3d5JTJGaCUyRm5jcGx1cy1vdWFoLWZpbG15LW1lbnUtcHJ6eWdvZG93eXxuY3BsdXMtb3VhaC1maWxteS1tZW51LXByenlnb2Rvd3kiLCAiaW1hZ2UiOiAiaHR0cHM6Ly90aHVtYi5jYW5hbHBsdXMucHJvL2h0dHAvdW5zYWZlL3tyZXNvbHV0aW9uWFl9L2ZpbHRlcnM6cXVhbGl0eSg3MCkvbmNwbHVzLWNkbi5jYW5hbC1wbHVzLmlvL3AxL2xpc3QvbmNwbHVzLW91YWgtZmlsbXktbWVudS1wcnp5Z29kb3d5L25jcGx1cy1vdWFoL1NURC9Qcnp5Z29kb3d5IiwgInR5cCI6ICJmb2xkZXIifSwgeyJwbG90IjogIiIsICJjb2RlIjogIiIsICJ0aXRsZSI6ICJLb21lZGllIiwgInVybCI6ICJodHRwczovL2hvZG9yLmNhbmFscGx1cy5wcm8vYXBpL3YyL215Y2FuYWxpbnQvcGFnZS97fS8xMDQ4MTkuanNvbj9wYXJhbXMlNUJkZXRhaWxUeXBlJTVEPWNvbnRlbnRHcmlkJm9iamVjdFR5cGU9bGlzdCZwYXJhbXMlNUJkc3AlNUQ9Z2FiYXJpdExpc3QmcGFyYW1zJTVCc2RtJTVEPXNob3cmdGl0bGVEaXNwbGF5TW9kZT1ub25lJnByZXZpb3VzQ29udGV4dERldGFpbD1pbnRlci10aGVtZS1maWxtLTItY29udGVudHJvdy1uY3BsdXMtb3VhaC1maWxteS1tZW51JnBhcmFtcyU1QnRhYiU1RD0lMkZrb21lZGllJTJGaCUyRm5jcGx1cy1vdWFoLWZpbG15LWtvbWVkaWF8bmNwbHVzLW91YWgtZmlsbXkta29tZWRpYSIsICJpbWFnZSI6ICJodHRwczovL3RodW1iLmNhbmFscGx1cy5wcm8vaHR0cC91bnNhZmUve3Jlc29sdXRpb25YWX0vZmlsdGVyczpxdWFsaXR5KDcwKS9uY3BsdXMtY2RuLmNhbmFsLXBsdXMuaW8vcDEvbGlzdC9uY3BsdXMtb3VhaC1maWxteS1rb21lZGlhL25jcGx1cy1vdWFoL1NURC9Lb21lZGlhIiwgInR5cCI6ICJmb2xkZXIifSwgeyJwbG90IjogIiIsICJjb2RlIjogIiIsICJ0aXRsZSI6ICJSb21hbnMiLCAidXJsIjogImh0dHBzOi8vaG9kb3IuY2FuYWxwbHVzLnByby9hcGkvdjIvbXljYW5hbGludC9wYWdlL3t9LzEwNDgxOS5qc29uP3BhcmFtcyU1QmRldGFpbFR5cGUlNUQ9Y29udGVudEdyaWQmb2JqZWN0VHlwZT1saXN0JnBhcmFtcyU1QmRzcCU1RD1nYWJhcml0TGlzdCZwYXJhbXMlNUJzZG0lNUQ9c2hvdyZ0aXRsZURpc3BsYXlNb2RlPW5vbmUmcHJldmlvdXNDb250ZXh0RGV0YWlsPWludGVyLXRoZW1lLWZpbG0tMi1jb250ZW50cm93LW5jcGx1cy1vdWFoLWZpbG15LW1lbnUmcGFyYW1zJTVCdGFiJTVEPSUyRnJvbWFucyUyRmglMkZuY3BsdXMtb3VhaC1maWxteS1yb21hbnN8bmNwbHVzLW91YWgtZmlsbXktcm9tYW5zIiwgImltYWdlIjogImh0dHBzOi8vdGh1bWIuY2FuYWxwbHVzLnByby9odHRwL3Vuc2FmZS97cmVzb2x1dGlvblhZfS9maWx0ZXJzOnF1YWxpdHkoNzApL25jcGx1cy1jZG4uY2FuYWwtcGx1cy5pby9wMS9saXN0L25jcGx1cy1vdWFoLWZpbG15LXJvbWFucy9uY3BsdXMtb3VhaC9TVEQvUm9tYW5zIiwgInR5cCI6ICJmb2xkZXIifSwgeyJwbG90IjogIiIsICJjb2RlIjogIiIsICJ0aXRsZSI6ICJEcmFtYXQiLCAidXJsIjogImh0dHBzOi8vaG9kb3IuY2FuYWxwbHVzLnByby9hcGkvdjIvbXljYW5hbGludC9wYWdlL3t9LzEwNDgxOS5qc29uP3BhcmFtcyU1QmRldGFpbFR5cGUlNUQ9Y29udGVudEdyaWQmb2JqZWN0VHlwZT1saXN0JnBhcmFtcyU1QmRzcCU1RD1nYWJhcml0TGlzdCZwYXJhbXMlNUJzZG0lNUQ9c2hvdyZ0aXRsZURpc3BsYXlNb2RlPW5vbmUmcHJldmlvdXNDb250ZXh0RGV0YWlsPWludGVyLXRoZW1lLWZpbG0tMi1jb250ZW50cm93LW5jcGx1cy1vdWFoLWZpbG15LW1lbnUmcGFyYW1zJTVCdGFiJTVEPSUyRmRyYW1hdCUyRmglMkZuY3BsdXMtb3VhaC1maWxteS1tZW51LWRyYW1hdHxuY3BsdXMtb3VhaC1maWxteS1tZW51LWRyYW1hdCIsICJpbWFnZSI6ICJodHRwczovL3RodW1iLmNhbmFscGx1cy5wcm8vaHR0cC91bnNhZmUve3Jlc29sdXRpb25YWX0vZmlsdGVyczpxdWFsaXR5KDcwKS9uY3BsdXMtY2RuLmNhbmFsLXBsdXMuaW8vcDEvbGlzdC9uY3BsdXMtb3VhaC1maWxteS1tZW51LWRyYW1hdC9uY3BsdXMtb3VhaC9TVEQvRHJhbWF0IiwgInR5cCI6ICJmb2xkZXIifSwgeyJwbG90IjogIiIsICJjb2RlIjogIiIsICJ0aXRsZSI6ICJLb21lZGlvZHJhbWF0IiwgInVybCI6ICJodHRwczovL2hvZG9yLmNhbmFscGx1cy5wcm8vYXBpL3YyL215Y2FuYWxpbnQvcGFnZS97fS8xMDQ4MTkuanNvbj9wYXJhbXMlNUJkZXRhaWxUeXBlJTVEPWNvbnRlbnRHcmlkJm9iamVjdFR5cGU9bGlzdCZwYXJhbXMlNUJkc3AlNUQ9Z2FiYXJpdExpc3QmcGFyYW1zJTVCc2RtJTVEPXNob3cmdGl0bGVEaXNwbGF5TW9kZT1ub25lJnByZXZpb3VzQ29udGV4dERldGFpbD1pbnRlci10aGVtZS1maWxtLTItY29udGVudHJvdy1uY3BsdXMtb3VhaC1maWxteS1tZW51JnBhcmFtcyU1QnRhYiU1RD0lMkZrb21lZGlvZHJhbWF0JTJGaCUyRm5jcGx1cy1vdWFoLWZpbG15LW1lbnUta29tZWRpb2RyYW1hdHxuY3BsdXMtb3VhaC1maWxteS1tZW51LWtvbWVkaW9kcmFtYXQiLCAiaW1hZ2UiOiAiaHR0cHM6Ly90aHVtYi5jYW5hbHBsdXMucHJvL2h0dHAvdW5zYWZlL3tyZXNvbHV0aW9uWFl9L2ZpbHRlcnM6cXVhbGl0eSg3MCkvbmNwbHVzLWNkbi5jYW5hbC1wbHVzLmlvL3AxL2xpc3QvbmNwbHVzLW91YWgtZmlsbXktbWVudS1rb21lZGlvZHJhbWF0L25jcGx1cy1vdWFoL1NURC9Lb21lZGlvZHJhbWF0IiwgInR5cCI6ICJmb2xkZXIifSwgeyJwbG90IjogIiIsICJjb2RlIjogIiIsICJ0aXRsZSI6ICJLcnltaW5hXHUwMTQyICYgVGhyaWxsZXIiLCAidXJsIjogImh0dHBzOi8vaG9kb3IuY2FuYWxwbHVzLnByby9hcGkvdjIvbXljYW5hbGludC9wYWdlL3t9LzEwNDgxOS5qc29uP3BhcmFtcyU1QmRldGFpbFR5cGUlNUQ9Y29udGVudEdyaWQmb2JqZWN0VHlwZT1saXN0JnBhcmFtcyU1QmRzcCU1RD1nYWJhcml0TGlzdCZwYXJhbXMlNUJzZG0lNUQ9c2hvdyZ0aXRsZURpc3BsYXlNb2RlPW5vbmUmcHJldmlvdXNDb250ZXh0RGV0YWlsPWludGVyLXRoZW1lLWZpbG0tMi1jb250ZW50cm93LW5jcGx1cy1vdWFoLWZpbG15LW1lbnUmcGFyYW1zJTVCdGFiJTVEPSUyRmtyeW1pbmFsLXRocmlsbGVyJTJGaCUyRm5jcGx1cy1vdWFoLWZpbG15LWtyeW1pbmFsfG5jcGx1cy1vdWFoLWZpbG15LWtyeW1pbmFsIiwgImltYWdlIjogImh0dHBzOi8vdGh1bWIuY2FuYWxwbHVzLnByby9odHRwL3Vuc2FmZS97cmVzb2x1dGlvblhZfS9maWx0ZXJzOnF1YWxpdHkoNzApL25jcGx1cy1jZG4uY2FuYWwtcGx1cy5pby9wMS9saXN0L25jcGx1cy1vdWFoLWZpbG15LWtyeW1pbmFsL25jcGx1cy1vdWFoL1NURC9UaHJpbGxlciIsICJ0eXAiOiAiZm9sZGVyIn0sIHsicGxvdCI6ICIiLCAiY29kZSI6ICIiLCAidGl0bGUiOiAiT2J5Y3pham93eSIsICJ1cmwiOiAiaHR0cHM6Ly9ob2Rvci5jYW5hbHBsdXMucHJvL2FwaS92Mi9teWNhbmFsaW50L3BhZ2Uve30vMTA0ODE5Lmpzb24/cGFyYW1zJTVCZGV0YWlsVHlwZSU1RD1jb250ZW50R3JpZCZvYmplY3RUeXBlPWxpc3QmcGFyYW1zJTVCZHNwJTVEPWdhYmFyaXRMaXN0JnBhcmFtcyU1QnNkbSU1RD1zaG93JnRpdGxlRGlzcGxheU1vZGU9bm9uZSZwcmV2aW91c0NvbnRleHREZXRhaWw9aW50ZXItdGhlbWUtZmlsbS0yLWNvbnRlbnRyb3ctbmNwbHVzLW91YWgtZmlsbXktbWVudSZwYXJhbXMlNUJ0YWIlNUQ9JTJGb2J5Y3pham93eSUyRmglMkZuY3BsdXMtb3VhaC1maWxteS1tZW51LW9ieWN6YWpvd3l8bmNwbHVzLW91YWgtZmlsbXktbWVudS1vYnljemFqb3d5IiwgImltYWdlIjogImh0dHBzOi8vdGh1bWIuY2FuYWxwbHVzLnByby9odHRwL3Vuc2FmZS97cmVzb2x1dGlvblhZfS9maWx0ZXJzOnF1YWxpdHkoNzApL25jcGx1cy1jZG4uY2FuYWwtcGx1cy5pby9wMS9saXN0L25jcGx1cy1vdWFoLWZpbG15LW1lbnUtb2J5Y3pham93eS9uY3BsdXMtb3VhaC9TVEQvT2J5Y3pham93eSIsICJ0eXAiOiAiZm9sZGVyIn0sIHsicGxvdCI6ICIiLCAiY29kZSI6ICIiLCAidGl0bGUiOiAiRmFtaWxpam55IiwgInVybCI6ICJodHRwczovL2hvZG9yLmNhbmFscGx1cy5wcm8vYXBpL3YyL215Y2FuYWxpbnQvcGFnZS97fS8xMDQ4MTkuanNvbj9wYXJhbXMlNUJkZXRhaWxUeXBlJTVEPWNvbnRlbnRHcmlkJm9iamVjdFR5cGU9bGlzdCZwYXJhbXMlNUJkc3AlNUQ9Z2FiYXJpdExpc3QmcGFyYW1zJTVCc2RtJTVEPXNob3cmdGl0bGVEaXNwbGF5TW9kZT1ub25lJnByZXZpb3VzQ29udGV4dERldGFpbD1pbnRlci10aGVtZS1maWxtLTItY29udGVudHJvdy1uY3BsdXMtb3VhaC1maWxteS1tZW51JnBhcmFtcyU1QnRhYiU1RD0lMkZmYW1pbGlqbnklMkZoJTJGbmNwbHVzLW91YWgtZmlsbXktbWVudS1mYW1pbGlqbnl8bmNwbHVzLW91YWgtZmlsbXktbWVudS1mYW1pbGlqbnkiLCAiaW1hZ2UiOiAiaHR0cHM6Ly90aHVtYi5jYW5hbHBsdXMucHJvL2h0dHAvdW5zYWZlL3tyZXNvbHV0aW9uWFl9L2ZpbHRlcnM6cXVhbGl0eSg3MCkvbmNwbHVzLWNkbi5jYW5hbC1wbHVzLmlvL3AxL2xpc3QvbmNwbHVzLW91YWgtZmlsbXktbWVudS1mYW1pbGlqbnkvbmNwbHVzLW91YWgvU1REL0ZhbWlsaWpueSIsICJ0eXAiOiAiZm9sZGVyIn0sIHsicGxvdCI6ICIiLCAiY29kZSI6ICIiLCAidGl0bGUiOiAiRGxhIGR6aWVjaSIsICJ1cmwiOiAiaHR0cHM6Ly9ob2Rvci5jYW5hbHBsdXMucHJvL2FwaS92Mi9teWNhbmFsaW50L3BhZ2Uve30vMTA0ODE5Lmpzb24/cGFyYW1zJTVCZGV0YWlsVHlwZSU1RD1jb250ZW50R3JpZCZvYmplY3RUeXBlPWxpc3QmcGFyYW1zJTVCZHNwJTVEPWdhYmFyaXRMaXN0JnBhcmFtcyU1QnNkbSU1RD1zaG93JnRpdGxlRGlzcGxheU1vZGU9bm9uZSZwcmV2aW91c0NvbnRleHREZXRhaWw9aW50ZXItdGhlbWUtZmlsbS0yLWNvbnRlbnRyb3ctbmNwbHVzLW91YWgtZmlsbXktbWVudSZwYXJhbXMlNUJ0YWIlNUQ9JTJGZGxhLWR6aWVjaSUyRmglMkZuY3BsdXMtb3VhaC1maWxteS1kemllY2l8bmNwbHVzLW91YWgtZmlsbXktZHppZWNpIiwgImltYWdlIjogImh0dHBzOi8vdGh1bWIuY2FuYWxwbHVzLnByby9odHRwL3Vuc2FmZS97cmVzb2x1dGlvblhZfS9maWx0ZXJzOnF1YWxpdHkoNzApL25jcGx1cy1jZG4uY2FuYWwtcGx1cy5pby9wMS9saXN0L25jcGx1cy1vdWFoLWZpbG15LWR6aWVjaS9uY3BsdXMtb3VhaC9TVEQvRGxhZHppZWNpIiwgInR5cCI6ICJmb2xkZXIifSwgeyJwbG90IjogIiIsICJjb2RlIjogIiIsICJ0aXRsZSI6ICJNdXNpY2FsIiwgInVybCI6ICJodHRwczovL2hvZG9yLmNhbmFscGx1cy5wcm8vYXBpL3YyL215Y2FuYWxpbnQvcGFnZS97fS8xMDQ4MTkuanNvbj9wYXJhbXMlNUJkZXRhaWxUeXBlJTVEPWNvbnRlbnRHcmlkJm9iamVjdFR5cGU9bGlzdCZwYXJhbXMlNUJkc3AlNUQ9Z2FiYXJpdExpc3QmcGFyYW1zJTVCc2RtJTVEPXNob3cmdGl0bGVEaXNwbGF5TW9kZT1ub25lJnByZXZpb3VzQ29udGV4dERldGFpbD1pbnRlci10aGVtZS1maWxtLTItY29udGVudHJvdy1uY3BsdXMtb3VhaC1maWxteS1tZW51JnBhcmFtcyU1QnRhYiU1RD0lMkZtdXNpY2FsJTJGaCUyRm5jcGx1cy1vdWFoLWZpbG15LW1lbnUtbXVzaWNhbHxuY3BsdXMtb3VhaC1maWxteS1tZW51LW11c2ljYWwiLCAiaW1hZ2UiOiAiaHR0cHM6Ly90aHVtYi5jYW5hbHBsdXMucHJvL2h0dHAvdW5zYWZlL3tyZXNvbHV0aW9uWFl9L2ZpbHRlcnM6cXVhbGl0eSg3MCkvbmNwbHVzLWNkbi5jYW5hbC1wbHVzLmlvL3AxL2xpc3QvbmNwbHVzLW91YWgtZmlsbXktbWVudS1tdXNpY2FsL25jcGx1cy1vdWFoL1NURC9NdXNpY2FsIiwgInR5cCI6ICJmb2xkZXIifSwgeyJwbG90IjogIiIsICJjb2RlIjogIiIsICJ0aXRsZSI6ICJEb2t1bWVudCIsICJ1cmwiOiAiaHR0cHM6Ly9ob2Rvci5jYW5hbHBsdXMucHJvL2FwaS92Mi9teWNhbmFsaW50L3BhZ2Uve30vMTA0ODE5Lmpzb24/cGFyYW1zJTVCZGV0YWlsVHlwZSU1RD1jb250ZW50R3JpZCZvYmplY3RUeXBlPWxpc3QmcGFyYW1zJTVCZHNwJTVEPWdhYmFyaXRMaXN0JnBhcmFtcyU1QnNkbSU1RD1zaG93JnRpdGxlRGlzcGxheU1vZGU9bm9uZSZwcmV2aW91c0NvbnRleHREZXRhaWw9aW50ZXItdGhlbWUtZmlsbS0yLWNvbnRlbnRyb3ctbmNwbHVzLW91YWgtZmlsbXktbWVudSZwYXJhbXMlNUJ0YWIlNUQ9JTJGZG9rdW1lbnQlMkZoJTJGbmNwbHVzLW91YWgtZG9rdW1lbnQtZmlsbXl8bmNwbHVzLW91YWgtZG9rdW1lbnQtZmlsbXkiLCAiaW1hZ2UiOiAiaHR0cHM6Ly90aHVtYi5jYW5hbHBsdXMucHJvL2h0dHAvdW5zYWZlL3tyZXNvbHV0aW9uWFl9L2ZpbHRlcnM6cXVhbGl0eSg3MCkvbmNwbHVzLWNkbi5jYW5hbC1wbHVzLmlvL3AxL2xpc3QvbmNwbHVzLW91YWgtZG9rdW1lbnQtZmlsbXkvbmNwbHVzLW91YWgvU1REL0Rva3VtZW50IiwgInR5cCI6ICJmb2xkZXIifSwgeyJwbG90IjogIiIsICJjb2RlIjogIiIsICJ0aXRsZSI6ICJNZWxvZHJhbWF0IiwgInVybCI6ICJodHRwczovL2hvZG9yLmNhbmFscGx1cy5wcm8vYXBpL3YyL215Y2FuYWxpbnQvcGFnZS97fS8xMDQ4MTkuanNvbj9wYXJhbXMlNUJkZXRhaWxUeXBlJTVEPWNvbnRlbnRHcmlkJm9iamVjdFR5cGU9bGlzdCZwYXJhbXMlNUJkc3AlNUQ9Z2FiYXJpdExpc3QmcGFyYW1zJTVCc2RtJTVEPXNob3cmdGl0bGVEaXNwbGF5TW9kZT1ub25lJnByZXZpb3VzQ29udGV4dERldGFpbD1pbnRlci10aGVtZS1maWxtLTItY29udGVudHJvdy1uY3BsdXMtb3VhaC1maWxteS1tZW51JnBhcmFtcyU1QnRhYiU1RD0lMkZtZWxvZHJhbWF0JTJGaCUyRm5jcGx1cy1vdWFoLWZpbG15LW1lbnUtbWVsb2RyYW1hdHxuY3BsdXMtb3VhaC1maWxteS1tZW51LW1lbG9kcmFtYXQiLCAiaW1hZ2UiOiAiaHR0cHM6Ly90aHVtYi5jYW5hbHBsdXMucHJvL2h0dHAvdW5zYWZlL3tyZXNvbHV0aW9uWFl9L2ZpbHRlcnM6cXVhbGl0eSg3MCkvbmNwbHVzLWNkbi5jYW5hbC1wbHVzLmlvL3AxL2xpc3QvbmNwbHVzLW91YWgtZmlsbXktbWVudS1tZWxvZHJhbWF0L25jcGx1cy1vdWFoL1NURC9NZWxvZHJhbWF0IiwgInR5cCI6ICJmb2xkZXIifSwgeyJwbG90IjogIiIsICJjb2RlIjogIiIsICJ0aXRsZSI6ICJCaW9ncmFmaWUiLCAidXJsIjogImh0dHBzOi8vaG9kb3IuY2FuYWxwbHVzLnByby9hcGkvdjIvbXljYW5hbGludC9wYWdlL3t9LzEwNDgxOS5qc29uP3BhcmFtcyU1QmRldGFpbFR5cGUlNUQ9Y29udGVudEdyaWQmb2JqZWN0VHlwZT1saXN0JnBhcmFtcyU1QmRzcCU1RD1nYWJhcml0TGlzdCZwYXJhbXMlNUJzZG0lNUQ9c2hvdyZ0aXRsZURpc3BsYXlNb2RlPW5vbmUmcHJldmlvdXNDb250ZXh0RGV0YWlsPWludGVyLXRoZW1lLWZpbG0tMi1jb250ZW50cm93LW5jcGx1cy1vdWFoLWZpbG15LW1lbnUmcGFyYW1zJTVCdGFiJTVEPSUyRmJpb2dyYWZpZSUyRmglMkZuY3BsdXMtb3VhaC1maWxteS1tZW51LWhpc3Rvcnljem55fG5jcGx1cy1vdWFoLWZpbG15LW1lbnUtaGlzdG9yeWN6bnkiLCAiaW1hZ2UiOiAiaHR0cHM6Ly90aHVtYi5jYW5hbHBsdXMucHJvL2h0dHAvdW5zYWZlL3tyZXNvbHV0aW9uWFl9L2ZpbHRlcnM6cXVhbGl0eSg3MCkvbmNwbHVzLWNkbi5jYW5hbC1wbHVzLmlvL3AxL2xpc3QvbmNwbHVzLW91YWgtZmlsbXktbWVudS1oaXN0b3J5Y3pueS9uY3BsdXMtb3VhaC9TVEQvSGlzdG9yeWN6bnkiLCAidHlwIjogImZvbGRlciJ9LCB7InBsb3QiOiAiIiwgImNvZGUiOiAiIiwgInRpdGxlIjogIlNjaWVuY2UgZmljdGlvbiIsICJ1cmwiOiAiaHR0cHM6Ly9ob2Rvci5jYW5hbHBsdXMucHJvL2FwaS92Mi9teWNhbmFsaW50L3BhZ2Uve30vMTA0ODE5Lmpzb24/cGFyYW1zJTVCZGV0YWlsVHlwZSU1RD1jb250ZW50R3JpZCZvYmplY3RUeXBlPWxpc3QmcGFyYW1zJTVCZHNwJTVEPWdhYmFyaXRMaXN0JnBhcmFtcyU1QnNkbSU1RD1zaG93JnRpdGxlRGlzcGxheU1vZGU9bm9uZSZwcmV2aW91c0NvbnRleHREZXRhaWw9aW50ZXItdGhlbWUtZmlsbS0yLWNvbnRlbnRyb3ctbmNwbHVzLW91YWgtZmlsbXktbWVudSZwYXJhbXMlNUJ0YWIlNUQ9JTJGc2NpZW5jZS1maWN0aW9uJTJGaCUyRm5jcGx1cy1vdWFoLWZpbG15LW1lbnUtc2NpZW5jZWZpY3Rpb258bmNwbHVzLW91YWgtZmlsbXktbWVudS1zY2llbmNlZmljdGlvbiIsICJpbWFnZSI6ICJodHRwczovL3RodW1iLmNhbmFscGx1cy5wcm8vaHR0cC91bnNhZmUve3Jlc29sdXRpb25YWX0vZmlsdGVyczpxdWFsaXR5KDcwKS9uY3BsdXMtY2RuLmNhbmFsLXBsdXMuaW8vcDEvbGlzdC9uY3BsdXMtb3VhaC1maWxteS1tZW51LXNjaWVuY2VmaWN0aW9uL25jcGx1cy1vdWFoL1NURC9zY2llbmNlZmljdGlvbiIsICJ0eXAiOiAiZm9sZGVyIn0sIHsicGxvdCI6ICIiLCAiY29kZSI6ICIiLCAidGl0bGUiOiAiRmFudGFzeSIsICJ1cmwiOiAiaHR0cHM6Ly9ob2Rvci5jYW5hbHBsdXMucHJvL2FwaS92Mi9teWNhbmFsaW50L3BhZ2Uve30vMTA0ODE5Lmpzb24/cGFyYW1zJTVCZGV0YWlsVHlwZSU1RD1jb250ZW50R3JpZCZvYmplY3RUeXBlPWxpc3QmcGFyYW1zJTVCZHNwJTVEPWdhYmFyaXRMaXN0JnBhcmFtcyU1QnNkbSU1RD1zaG93JnRpdGxlRGlzcGxheU1vZGU9bm9uZSZwcmV2aW91c0NvbnRleHREZXRhaWw9aW50ZXItdGhlbWUtZmlsbS0yLWNvbnRlbnRyb3ctbmNwbHVzLW91YWgtZmlsbXktbWVudSZwYXJhbXMlNUJ0YWIlNUQ9JTJGZmFudGFzeSUyRmglMkZuY3BsdXMtb3VhaC1maWxteS1tZW51LWZhbnRhc3l8bmNwbHVzLW91YWgtZmlsbXktbWVudS1mYW50YXN5IiwgImltYWdlIjogImh0dHBzOi8vdGh1bWIuY2FuYWxwbHVzLnByby9odHRwL3Vuc2FmZS97cmVzb2x1dGlvblhZfS9maWx0ZXJzOnF1YWxpdHkoNzApL25jcGx1cy1jZG4uY2FuYWwtcGx1cy5pby9wMS9saXN0L25jcGx1cy1vdWFoLWZpbG15LW1lbnUtZmFudGFzeS9uY3BsdXMtb3VhaC9TVEQvRmFudGFzeSIsICJ0eXAiOiAiZm9sZGVyIn0sIHsicGxvdCI6ICIiLCAiY29kZSI6ICIiLCAidGl0bGUiOiAiV2VzdGVybiIsICJ1cmwiOiAiaHR0cHM6Ly9ob2Rvci5jYW5hbHBsdXMucHJvL2FwaS92Mi9teWNhbmFsaW50L3BhZ2Uve30vMTA0ODE5Lmpzb24/cGFyYW1zJTVCZGV0YWlsVHlwZSU1RD1jb250ZW50R3JpZCZvYmplY3RUeXBlPWxpc3QmcGFyYW1zJTVCZHNwJTVEPWdhYmFyaXRMaXN0JnBhcmFtcyU1QnNkbSU1RD1zaG93JnRpdGxlRGlzcGxheU1vZGU9bm9uZSZwcmV2aW91c0NvbnRleHREZXRhaWw9aW50ZXItdGhlbWUtZmlsbS0yLWNvbnRlbnRyb3ctbmNwbHVzLW91YWgtZmlsbXktbWVudSZwYXJhbXMlNUJ0YWIlNUQ9JTJGd2VzdGVybiUyRmglMkZuY3BsdXMtb3VhaC1maWxteS1tZW51LXdlc3Rlcm58bmNwbHVzLW91YWgtZmlsbXktbWVudS13ZXN0ZXJuIiwgImltYWdlIjogImh0dHBzOi8vdGh1bWIuY2FuYWxwbHVzLnByby9odHRwL3Vuc2FmZS97cmVzb2x1dGlvblhZfS9maWx0ZXJzOnF1YWxpdHkoNzApL25jcGx1cy1jZG4uY2FuYWwtcGx1cy5pby9wMS9saXN0L25jcGx1cy1vdWFoLWZpbG15LW1lbnUtd2VzdGVybi9uY3BsdXMtb3VhaC9TVEQvV2VzdGVybiIsICJ0eXAiOiAiZm9sZGVyIn0sIHsicGxvdCI6ICIiLCAiY29kZSI6ICIiLCAidGl0bGUiOiAiV29qZW5ueSIsICJ1cmwiOiAiaHR0cHM6Ly9ob2Rvci5jYW5hbHBsdXMucHJvL2FwaS92Mi9teWNhbmFsaW50L3BhZ2Uve30vMTA0ODE5Lmpzb24/cGFyYW1zJTVCZGV0YWlsVHlwZSU1RD1jb250ZW50R3JpZCZvYmplY3RUeXBlPWxpc3QmcGFyYW1zJTVCZHNwJTVEPWdhYmFyaXRMaXN0JnBhcmFtcyU1QnNkbSU1RD1zaG93JnRpdGxlRGlzcGxheU1vZGU9bm9uZSZwcmV2aW91c0NvbnRleHREZXRhaWw9aW50ZXItdGhlbWUtZmlsbS0yLWNvbnRlbnRyb3ctbmNwbHVzLW91YWgtZmlsbXktbWVudSZwYXJhbXMlNUJ0YWIlNUQ9JTJGd29qZW5ueSUyRmglMkZuY3BsdXMtb3VhaC1maWxteS1tZW51LXdvamVubnl8bmNwbHVzLW91YWgtZmlsbXktbWVudS13b2plbm55IiwgImltYWdlIjogImh0dHBzOi8vdGh1bWIuY2FuYWxwbHVzLnByby9odHRwL3Vuc2FmZS97cmVzb2x1dGlvblhZfS9maWx0ZXJzOnF1YWxpdHkoNzApL25jcGx1cy1jZG4uY2FuYWwtcGx1cy5pby9wMS9saXN0L25jcGx1cy1vdWFoLWZpbG15LW1lbnUtd29qZW5ueS9uY3BsdXMtb3VhaC9TVEQvd29qZW5ueSIsICJ0eXAiOiAiZm9sZGVyIn0sIHsicGxvdCI6ICIiLCAiY29kZSI6ICIiLCAidGl0bGUiOiAiSG9ycm9yIiwgInVybCI6ICJodHRwczovL2hvZG9yLmNhbmFscGx1cy5wcm8vYXBpL3YyL215Y2FuYWxpbnQvcGFnZS97fS8xMDQ4MTkuanNvbj9wYXJhbXMlNUJkZXRhaWxUeXBlJTVEPWNvbnRlbnRHcmlkJm9iamVjdFR5cGU9bGlzdCZwYXJhbXMlNUJkc3AlNUQ9Z2FiYXJpdExpc3QmcGFyYW1zJTVCc2RtJTVEPXNob3cmdGl0bGVEaXNwbGF5TW9kZT1ub25lJnByZXZpb3VzQ29udGV4dERldGFpbD1pbnRlci10aGVtZS1maWxtLTItY29udGVudHJvdy1uY3BsdXMtb3VhaC1maWxteS1tZW51JnBhcmFtcyU1QnRhYiU1RD0lMkZob3Jyb3IlMkZoJTJGbmNwbHVzLW91YWgtZmlsbXktbWVudS1ob3Jyb3J8bmNwbHVzLW91YWgtZmlsbXktbWVudS1ob3Jyb3IiLCAiaW1hZ2UiOiAiaHR0cHM6Ly90aHVtYi5jYW5hbHBsdXMucHJvL2h0dHAvdW5zYWZlL3tyZXNvbHV0aW9uWFl9L2ZpbHRlcnM6cXVhbGl0eSg3MCkvbmNwbHVzLWNkbi5jYW5hbC1wbHVzLmlvL3AxL2xpc3QvbmNwbHVzLW91YWgtZmlsbXktbWVudS1ob3Jyb3IvbmNwbHVzLW91YWgvU1REL0hvcnJvciIsICJ0eXAiOiAiZm9sZGVyIn1d'
    serout = 'W3sicGxvdCI6ICIiLCAiY29kZSI6ICIiLCAidGl0bGUiOiAiV3N6eXN0a2llIHNlcmlhbGUiLCAidXJsIjogImh0dHBzOi8vaG9kb3IuY2FuYWxwbHVzLnByby9hcGkvdjIvbXljYW5hbGludC9wYWdlL3t9LzEwNTM0NC5qc29uP3BhcmFtcyU1QmRldGFpbFR5cGUlNUQ9Y29udGVudEdyaWQmb2JqZWN0VHlwZT1saXN0JnBhcmFtcyU1QmRzcCU1RD1nYWJhcml0TGlzdCZwYXJhbXMlNUJzZG0lNUQ9c2hvdyZ0aXRsZURpc3BsYXlNb2RlPW5vbmUmcHJldmlvdXNDb250ZXh0RGV0YWlsPWludGVyLXRoZW1lLXNlcmlhbGUtMi1jb250ZW50cm93LW5jcGx1cy1vdWFoLXNlcmlhbGUtbWVudSZwYXJhbXMlNUJ0YWIlNUQ9JTJGd3N6eXN0a2llLXNlcmlhbGUlMkZoJTJGbmNwbHVzLW91YWgtc2VyaWFsZS1hbGx8bmNwbHVzLW91YWgtc2VyaWFsZS1hbGwiLCAiaW1hZ2UiOiAiaHR0cHM6Ly90aHVtYi5jYW5hbHBsdXMucHJvL2h0dHAvdW5zYWZlL3tyZXNvbHV0aW9uWFl9L2ZpbHRlcnM6cXVhbGl0eSg3MCkvbmNwbHVzLWNkbi5jYW5hbC1wbHVzLmlvL3AxL2xpc3QvbmNwbHVzLW91YWgtc2VyaWFsZS1hbGwvbmNwbHVzLW91YWgvU1REL3dzenlzdGtpZXNlcmlhbGUiLCAidHlwIjogImZvbGRlciJ9LCB7InBsb3QiOiAiIiwgImNvZGUiOiAiIiwgInRpdGxlIjogIkNBTkFMKyBPcnlnaW5hbG5lIHByb2R1a2NqZSAiLCAidXJsIjogImh0dHBzOi8vaG9kb3IuY2FuYWxwbHVzLnByby9hcGkvdjIvbXljYW5hbGludC9wYWdlL3t9LzEwNTM0NC5qc29uP3BhcmFtcyU1QmRldGFpbFR5cGUlNUQ9Y29udGVudEdyaWQmb2JqZWN0VHlwZT1saXN0JnBhcmFtcyU1QmRzcCU1RD1nYWJhcml0TGlzdCZwYXJhbXMlNUJzZG0lNUQ9c2hvdyZ0aXRsZURpc3BsYXlNb2RlPW5vbmUmcHJldmlvdXNDb250ZXh0RGV0YWlsPWludGVyLXRoZW1lLXNlcmlhbGUtMi1jb250ZW50cm93LW5jcGx1cy1vdWFoLXNlcmlhbGUtbWVudSZwYXJhbXMlNUJ0YWIlNUQ9JTJGY2FuYWwtb3J5Z2luYWxuZS1wcm9kdWtjamUlMkZoJTJGbmNwbHVzLW91YWgtc2VyaWFsZS1wcm9kdWtjamUtb3J5Z2luYWxuZXxuY3BsdXMtb3VhaC1zZXJpYWxlLXByb2R1a2NqZS1vcnlnaW5hbG5lIiwgImltYWdlIjogImh0dHBzOi8vdGh1bWIuY2FuYWxwbHVzLnByby9odHRwL3Vuc2FmZS97cmVzb2x1dGlvblhZfS9maWx0ZXJzOnF1YWxpdHkoNzApL25jcGx1cy1jZG4uY2FuYWwtcGx1cy5pby9wMS9saXN0L25jcGx1cy1vdWFoLXNlcmlhbGUtcHJvZHVrY2plLW9yeWdpbmFsbmUvbmNwbHVzLW91YWgvU1REL1Byb2R1a2NqZW9yeWdpbmFsbmUiLCAidHlwIjogImZvbGRlciJ9LCB7InBsb3QiOiAiIiwgImNvZGUiOiAiIiwgInRpdGxlIjogIlNlcmlhbGUgb2J5Y3pham93ZSIsICJ1cmwiOiAiaHR0cHM6Ly9ob2Rvci5jYW5hbHBsdXMucHJvL2FwaS92Mi9teWNhbmFsaW50L3BhZ2Uve30vMTA1MzQ0Lmpzb24/cGFyYW1zJTVCZGV0YWlsVHlwZSU1RD1jb250ZW50R3JpZCZvYmplY3RUeXBlPWxpc3QmcGFyYW1zJTVCZHNwJTVEPWdhYmFyaXRMaXN0JnBhcmFtcyU1QnNkbSU1RD1zaG93JnRpdGxlRGlzcGxheU1vZGU9bm9uZSZwcmV2aW91c0NvbnRleHREZXRhaWw9aW50ZXItdGhlbWUtc2VyaWFsZS0yLWNvbnRlbnRyb3ctbmNwbHVzLW91YWgtc2VyaWFsZS1tZW51JnBhcmFtcyU1QnRhYiU1RD0lMkZzZXJpYWxlLW9ieWN6YWpvd2UlMkZoJTJGbmNwbHVzLW91YWgtc2VyaWFsZS1tZW51LW9ieWN6YWpvd2V8bmNwbHVzLW91YWgtc2VyaWFsZS1tZW51LW9ieWN6YWpvd2UiLCAiaW1hZ2UiOiAiaHR0cHM6Ly90aHVtYi5jYW5hbHBsdXMucHJvL2h0dHAvdW5zYWZlL3tyZXNvbHV0aW9uWFl9L2ZpbHRlcnM6cXVhbGl0eSg3MCkvbmNwbHVzLWNkbi5jYW5hbC1wbHVzLmlvL3AxL2xpc3QvbmNwbHVzLW91YWgtc2VyaWFsZS1tZW51LW9ieWN6YWpvd2UvbmNwbHVzLW91YWgvU1RELzYiLCAidHlwIjogImZvbGRlciJ9LCB7InBsb3QiOiAiIiwgImNvZGUiOiAiIiwgInRpdGxlIjogIlNlcmlhbGUga3J5bWluYWxuZSIsICJ1cmwiOiAiaHR0cHM6Ly9ob2Rvci5jYW5hbHBsdXMucHJvL2FwaS92Mi9teWNhbmFsaW50L3BhZ2Uve30vMTA1MzQ0Lmpzb24/cGFyYW1zJTVCZGV0YWlsVHlwZSU1RD1jb250ZW50R3JpZCZvYmplY3RUeXBlPWxpc3QmcGFyYW1zJTVCZHNwJTVEPWdhYmFyaXRMaXN0JnBhcmFtcyU1QnNkbSU1RD1zaG93JnRpdGxlRGlzcGxheU1vZGU9bm9uZSZwcmV2aW91c0NvbnRleHREZXRhaWw9aW50ZXItdGhlbWUtc2VyaWFsZS0yLWNvbnRlbnRyb3ctbmNwbHVzLW91YWgtc2VyaWFsZS1tZW51JnBhcmFtcyU1QnRhYiU1RD0lMkZzZXJpYWxlLWtyeW1pbmFsbmUlMkZoJTJGbmNwbHVzLW91YWgtc2VyaWFsZS1rcnltaW5hbHxuY3BsdXMtb3VhaC1zZXJpYWxlLWtyeW1pbmFsIiwgImltYWdlIjogImh0dHBzOi8vdGh1bWIuY2FuYWxwbHVzLnByby9odHRwL3Vuc2FmZS97cmVzb2x1dGlvblhZfS9maWx0ZXJzOnF1YWxpdHkoNzApL25jcGx1cy1jZG4uY2FuYWwtcGx1cy5pby9wMS9saXN0L25jcGx1cy1vdWFoLXNlcmlhbGUta3J5bWluYWwvbmNwbHVzLW91YWgvU1RELzgiLCAidHlwIjogImZvbGRlciJ9LCB7InBsb3QiOiAiIiwgImNvZGUiOiAiIiwgInRpdGxlIjogIlNlcmlhbGUga29tZWRpb3dlIiwgInVybCI6ICJodHRwczovL2hvZG9yLmNhbmFscGx1cy5wcm8vYXBpL3YyL215Y2FuYWxpbnQvcGFnZS97fS8xMDUzNDQuanNvbj9wYXJhbXMlNUJkZXRhaWxUeXBlJTVEPWNvbnRlbnRHcmlkJm9iamVjdFR5cGU9bGlzdCZwYXJhbXMlNUJkc3AlNUQ9Z2FiYXJpdExpc3QmcGFyYW1zJTVCc2RtJTVEPXNob3cmdGl0bGVEaXNwbGF5TW9kZT1ub25lJnByZXZpb3VzQ29udGV4dERldGFpbD1pbnRlci10aGVtZS1zZXJpYWxlLTItY29udGVudHJvdy1uY3BsdXMtb3VhaC1zZXJpYWxlLW1lbnUmcGFyYW1zJTVCdGFiJTVEPSUyRnNlcmlhbGUta29tZWRpb3dlJTJGaCUyRm5jcGx1cy1vdWFoLXNlcmlhbGUta29tZWRpYXxuY3BsdXMtb3VhaC1zZXJpYWxlLWtvbWVkaWEiLCAiaW1hZ2UiOiAiaHR0cHM6Ly90aHVtYi5jYW5hbHBsdXMucHJvL2h0dHAvdW5zYWZlL3tyZXNvbHV0aW9uWFl9L2ZpbHRlcnM6cXVhbGl0eSg3MCkvbmNwbHVzLWNkbi5jYW5hbC1wbHVzLmlvL3AxL2xpc3QvbmNwbHVzLW91YWgtc2VyaWFsZS1rb21lZGlhL25jcGx1cy1vdWFoL1NURC8zIiwgInR5cCI6ICJmb2xkZXIifSwgeyJwbG90IjogIiIsICJjb2RlIjogIiIsICJ0aXRsZSI6ICJTZXJpYWxlIGFuaW1vd2FuZSIsICJ1cmwiOiAiaHR0cHM6Ly9ob2Rvci5jYW5hbHBsdXMucHJvL2FwaS92Mi9teWNhbmFsaW50L3BhZ2Uve30vMTA1MzQ0Lmpzb24/cGFyYW1zJTVCZGV0YWlsVHlwZSU1RD1jb250ZW50R3JpZCZvYmplY3RUeXBlPWxpc3QmcGFyYW1zJTVCZHNwJTVEPWdhYmFyaXRMaXN0JnBhcmFtcyU1QnNkbSU1RD1zaG93JnRpdGxlRGlzcGxheU1vZGU9bm9uZSZwcmV2aW91c0NvbnRleHREZXRhaWw9aW50ZXItdGhlbWUtc2VyaWFsZS0yLWNvbnRlbnRyb3ctbmNwbHVzLW91YWgtc2VyaWFsZS1tZW51JnBhcmFtcyU1QnRhYiU1RD0lMkZzZXJpYWxlLWFuaW1vd2FuZSUyRmglMkZuY3BsdXMtb3VhaC1zZXJpYWxlLW1lbnUtYW5pbW93YW5lfG5jcGx1cy1vdWFoLXNlcmlhbGUtbWVudS1hbmltb3dhbmUiLCAiaW1hZ2UiOiAiaHR0cHM6Ly90aHVtYi5jYW5hbHBsdXMucHJvL2h0dHAvdW5zYWZlL3tyZXNvbHV0aW9uWFl9L2ZpbHRlcnM6cXVhbGl0eSg3MCkvbmNwbHVzLWNkbi5jYW5hbC1wbHVzLmlvL3AxL2xpc3QvbmNwbHVzLW91YWgtc2VyaWFsZS1tZW51LWFuaW1vd2FuZS9uY3BsdXMtb3VhaC9TVEQvQW5pbW93YW5lIiwgInR5cCI6ICJmb2xkZXIifSwgeyJwbG90IjogIiIsICJjb2RlIjogIiIsICJ0aXRsZSI6ICJTZXJpYWxlIHByenlnb2Rvd2UiLCAidXJsIjogImh0dHBzOi8vaG9kb3IuY2FuYWxwbHVzLnByby9hcGkvdjIvbXljYW5hbGludC9wYWdlL3t9LzEwNTM0NC5qc29uP3BhcmFtcyU1QmRldGFpbFR5cGUlNUQ9Y29udGVudEdyaWQmb2JqZWN0VHlwZT1saXN0JnBhcmFtcyU1QmRzcCU1RD1nYWJhcml0TGlzdCZwYXJhbXMlNUJzZG0lNUQ9c2hvdyZ0aXRsZURpc3BsYXlNb2RlPW5vbmUmcHJldmlvdXNDb250ZXh0RGV0YWlsPWludGVyLXRoZW1lLXNlcmlhbGUtMi1jb250ZW50cm93LW5jcGx1cy1vdWFoLXNlcmlhbGUtbWVudSZwYXJhbXMlNUJ0YWIlNUQ9JTJGc2VyaWFsZS1wcnp5Z29kb3dlJTJGaCUyRm5jcGx1cy1vdWFoLXNlcmlhbGUtbWVudS1wcnp5Z29kb3dlfG5jcGx1cy1vdWFoLXNlcmlhbGUtbWVudS1wcnp5Z29kb3dlIiwgImltYWdlIjogImh0dHBzOi8vdGh1bWIuY2FuYWxwbHVzLnByby9odHRwL3Vuc2FmZS97cmVzb2x1dGlvblhZfS9maWx0ZXJzOnF1YWxpdHkoNzApL25jcGx1cy1jZG4uY2FuYWwtcGx1cy5pby9wMS9saXN0L25jcGx1cy1vdWFoLXNlcmlhbGUtbWVudS1wcnp5Z29kb3dlL25jcGx1cy1vdWFoL1NURC81IiwgInR5cCI6ICJmb2xkZXIifSwgeyJwbG90IjogIiIsICJjb2RlIjogIiIsICJ0aXRsZSI6ICJTZXJpYWxlIGhpc3Rvcnljem5lIiwgInVybCI6ICJodHRwczovL2hvZG9yLmNhbmFscGx1cy5wcm8vYXBpL3YyL215Y2FuYWxpbnQvcGFnZS97fS8xMDUzNDQuanNvbj9wYXJhbXMlNUJkZXRhaWxUeXBlJTVEPWNvbnRlbnRHcmlkJm9iamVjdFR5cGU9bGlzdCZwYXJhbXMlNUJkc3AlNUQ9Z2FiYXJpdExpc3QmcGFyYW1zJTVCc2RtJTVEPXNob3cmdGl0bGVEaXNwbGF5TW9kZT1ub25lJnByZXZpb3VzQ29udGV4dERldGFpbD1pbnRlci10aGVtZS1zZXJpYWxlLTItY29udGVudHJvdy1uY3BsdXMtb3VhaC1zZXJpYWxlLW1lbnUmcGFyYW1zJTVCdGFiJTVEPSUyRnNlcmlhbGUtaGlzdG9yeWN6bmUlMkZoJTJGbmNwbHVzLW91YWgtc2VyaWFsZS1tZW51LWhpc3Rvcnljem55fG5jcGx1cy1vdWFoLXNlcmlhbGUtbWVudS1oaXN0b3J5Y3pueSIsICJpbWFnZSI6ICJodHRwczovL3RodW1iLmNhbmFscGx1cy5wcm8vaHR0cC91bnNhZmUve3Jlc29sdXRpb25YWX0vZmlsdGVyczpxdWFsaXR5KDcwKS9uY3BsdXMtY2RuLmNhbmFsLXBsdXMuaW8vcDEvbGlzdC9uY3BsdXMtb3VhaC1zZXJpYWxlLW1lbnUtaGlzdG9yeWN6bnkvbmNwbHVzLW91YWgvU1REL0hpc3Rvcnljem5lMSIsICJ0eXAiOiAiZm9sZGVyIn0sIHsicGxvdCI6ICIiLCAiY29kZSI6ICIiLCAidGl0bGUiOiAiU2VyaWFsZSBkb2t1bWVudGFsbmUiLCAidXJsIjogImh0dHBzOi8vaG9kb3IuY2FuYWxwbHVzLnByby9hcGkvdjIvbXljYW5hbGludC9wYWdlL3t9LzEwNTM0NC5qc29uP3BhcmFtcyU1QmRldGFpbFR5cGUlNUQ9Y29udGVudEdyaWQmb2JqZWN0VHlwZT1saXN0JnBhcmFtcyU1QmRzcCU1RD1nYWJhcml0TGlzdCZwYXJhbXMlNUJzZG0lNUQ9c2hvdyZ0aXRsZURpc3BsYXlNb2RlPW5vbmUmcHJldmlvdXNDb250ZXh0RGV0YWlsPWludGVyLXRoZW1lLXNlcmlhbGUtMi1jb250ZW50cm93LW5jcGx1cy1vdWFoLXNlcmlhbGUtbWVudSZwYXJhbXMlNUJ0YWIlNUQ9JTJGc2VyaWFsZS1kb2t1bWVudGFsbmUlMkZoJTJGbmNwbHVzLW91YWgtc2VyaWFsZS1kb2t1bWVudGFsbmV8bmNwbHVzLW91YWgtc2VyaWFsZS1kb2t1bWVudGFsbmUiLCAiaW1hZ2UiOiAiaHR0cHM6Ly90aHVtYi5jYW5hbHBsdXMucHJvL2h0dHAvdW5zYWZlL3tyZXNvbHV0aW9uWFl9L2ZpbHRlcnM6cXVhbGl0eSg3MCkvbmNwbHVzLWNkbi5jYW5hbC1wbHVzLmlvL3AxL2xpc3QvbmNwbHVzLW91YWgtc2VyaWFsZS1kb2t1bWVudGFsbmUvbmNwbHVzLW91YWgvU1REL0Rva3VtZW50YWxueSIsICJ0eXAiOiAiZm9sZGVyIn0sIHsicGxvdCI6ICIiLCAiY29kZSI6ICIiLCAidGl0bGUiOiAiU2VyaWFsZSBTY2llbmNlIGZpY3Rpb24iLCAidXJsIjogImh0dHBzOi8vaG9kb3IuY2FuYWxwbHVzLnByby9hcGkvdjIvbXljYW5hbGludC9wYWdlL3t9LzEwNTM0NC5qc29uP3BhcmFtcyU1QmRldGFpbFR5cGUlNUQ9Y29udGVudEdyaWQmb2JqZWN0VHlwZT1saXN0JnBhcmFtcyU1QmRzcCU1RD1nYWJhcml0TGlzdCZwYXJhbXMlNUJzZG0lNUQ9c2hvdyZ0aXRsZURpc3BsYXlNb2RlPW5vbmUmcHJldmlvdXNDb250ZXh0RGV0YWlsPWludGVyLXRoZW1lLXNlcmlhbGUtMi1jb250ZW50cm93LW5jcGx1cy1vdWFoLXNlcmlhbGUtbWVudSZwYXJhbXMlNUJ0YWIlNUQ9JTJGc2VyaWFsZS1zY2llbmNlLWZpY3Rpb24lMkZoJTJGbmNwbHVzLW91YWgtc2VyaWFsZS1zY2lmaXxuY3BsdXMtb3VhaC1zZXJpYWxlLXNjaWZpIiwgImltYWdlIjogImh0dHBzOi8vdGh1bWIuY2FuYWxwbHVzLnByby9odHRwL3Vuc2FmZS97cmVzb2x1dGlvblhZfS9maWx0ZXJzOnF1YWxpdHkoNzApL25jcGx1cy1jZG4uY2FuYWwtcGx1cy5pby9wMS9saXN0L25jcGx1cy1vdWFoLXNlcmlhbGUtc2NpZmkvbmNwbHVzLW91YWgvU1REL3NjaWVuY2VmaWN0aW9uIiwgInR5cCI6ICJmb2xkZXIifV0='

    if typ=='filmy':
        out=json.loads(base64.b64decode(filmyout))
    else:
        out=json.loads(base64.b64decode(serout))

    return out
    
def ListCateg(typ1):
    itemsx = getOuts(typ1)
    for itemx in itemsx:
        img1 = itemx['image'] if itemx['image'] else ikona
    
        urlk,contid = (itemx['url']).split('|')
        urlk = urlk.format(CANALvod().CMStoken)
        
        urlk = urlk.replace('/page/','/contentGrid/')
        urlk = urlk.split('?params')[0]
        urlk = re.sub(r'(\d+\.json)','%s.json'%(str(contid)),urlk)
        inflabel = getInfoLabel(itemx)

        add_item(urlk, PLchar(itemx['title']), img1, 'listContent', folder=True, IsPlayable=False, infoLabels=inflabel, fanart=FANART)
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%Y")
    xbmcplugin.endOfDirectory(addon_handle) 

def ListContent(url):
    
    items, npage  = CANALvod().getContent(url)
    if CANALvod().cinemaURL in url and not '|' in url or CANALvod().seriesURL in url and not '|' in url:
        mud = 'listcateg'
        fold = True

        if CANALvod().cinemaURL in url:
            urlk = 'filmy'
        else:
            urlk = 'seriale'

        ilab = {}
        ilab['plot'] = 'Kategorie'
        ilab['title'] = 'Kategorie'

        add_item(urlk, 'Kategorie', ikona, mud, folder=fold, IsPlayable=False, infoLabels=ilab, fanart=FANART)

    if items:
        for item in items:
            inflabel = getInfoLabel(item)

            if item['typ'] == 'VoD':
                fold = False
                mud = 'playCANvod2'
                ispla = True
            else:
                fold = True
                mud = 'listContent'
                ispla = False
            img1 = item['image'] if item['image'] else ikona
            URL=build_url({'mode': mud, 'url' : item['url'], 'page' : 1, 'moviescount' : 0,'movie':True,'name':item['title'],'image':img1})
            #url, name, image, mode, folder=False, IsPlayable=False, infoLabels=False, movie=True, itemcount=1, page=1, fanart=FANART, moviescount=0, contMenu=False, CM=None
            CM=[]
            CM.append(('[B]Dodaj do ulubionych[/B]','RunPlugin(plugin://plugin.video.canalplusvod?mode=favAdd&url='+quote(URL)+'&title='+quote(item['title'])+'&infoLab='+quote(str(inflabel))+'&img='+quote(img1)+')'))
            if item['typ']=='VoD':
                CM.append(('[B]Szczegóły[/B]','RunPlugin(plugin://plugin.video.canalplusvod?mode=movieDetails&cid='+item['cid']+')'))
            if not 'objectType=person' in item['url']:
                add_item(item['url'], item['title'], img1, mud, folder=fold, IsPlayable=ispla, infoLabels=inflabel, fanart=FANART, contMenu=True, CM=CM)

        if mud != 'listContent':
            setView('movies')
        if npage:
        
            ilab={}
            ilab['plot'] = 'Następna strona'
            ilab['title'] = 'Następna strona'
            add_item(npage[0]['url'], npage[0]['title'], '', 'listContent', folder=True, IsPlayable=False, infoLabels=ilab,fanart=FANART)
            
    xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%Y")
    xbmcplugin.endOfDirectory(addon_handle) 

def movieDetails(cid):#
    url='https://hodor.canalplus.pro/api/v2/mycanalint/detail/%s/okapi/%s.json?detailType=detailPage&objectType=unit&featureToggles=detailV5'%(CANALvod().CMStoken,cid)
    response = getRequests(url, headers=CANALvod().HODORheaders)
    #print(response)
        
    url2=response['detail']['moreInfos']['URLPage']
    response2 = getRequests(url2, headers=CANALvod().HODORheaders)
    #print(response2)
    
    plot=''
    plot+=response2['strates'][0]['summary']['text']+'\n' #opis
    plot+='[B]%s[/B]\n'%(response['detail']['editorialTitle'])
    det=[i['contents'] for i in response2['strates'] if i['type']=='detailedInformation'][0]
    #print(det)
    cntr=[d['values'] for d in det if 'label' in d and (d['label']=='Kraj' or d['label']=='Kraje')][0]
    plot+='[B]Kraj: [/B]%s\n'%('/'.join(cntr))
    plot+='[B]Dostępne do: [/B]%s'%(datetime.datetime.fromtimestamp(response['detail']['availabilityEndDate']/1000).strftime('%Y-%m-%d %H:%M'))
    
    dialog = xbmcgui.Dialog()
    dialog.textviewer('Szczegóły', plot)


def czas(): #do usunięcia
    import datetime
    now = datetime.datetime.now()
    czas = now.strftime('%Y-%m-%dT%H:%M:%SZ')

    from datetime import datetime
    
    try:
        format_date = datetime.strptime(czas, '%Y-%m-%dT%H:%M:%SZ')
    except TypeError:
        format_date = datetime(*(time.strptime(czas, '%Y-%m-%dT%H:%M:%SZ')[0:6]))
        
    def to_timestamp(a_date):
        from datetime import datetime
        
        try:
            import pytz
        except:
            pass

        if a_date.tzinfo:
            epoch = datetime(1970, 1, 1, tzinfo=pytz.UTC)
            diff = a_date.astimezone(pytz.UTC) - epoch
        else:
            epoch = datetime(1970, 1, 1)
            diff = a_date - epoch

        return int(diff.total_seconds())*1000    
        
    tst4 =     to_timestamp(format_date)

    return int(tst4)

def get_addon():
    return addon

def set_setting(key, value):
    return get_addon().setSetting(key, value)
    
def get_setting(key):
    return get_addon().getSetting(key)
    
def dialog_progress():
    return xbmcgui.DialogProgress()
    
def xbmc_sleep(time):
    return xbmc.sleep(time)

def getRequests(url, data="", headers={}, params ={}, allo=None):
    if data:
        if allo:
            content=sess.get(url,headers=headers, data=data, params=params ).url
        else:
            content=sess.post(url,headers=headers,data=data, params=params )
            try:
                content=content.json()
            except:
                content=content.text
    else:
        if allo:
            content=sess.get(url,headers=headers, params=params ).url
        else:
            content=sess.get(url,headers=headers, params=params )
            try:
                content=content.json()
            except:
                content=content.text

    return content

def PLchar(char):
    if type(char) is not str:
        char=char.encode('utf-8')
    char = char.replace('\\u0105','\xc4\x85').replace('\\u0104','\xc4\x84')
    char = char.replace('\\u0107','\xc4\x87').replace('\\u0106','\xc4\x86')
    char = char.replace('\\u0119','\xc4\x99').replace('\\u0118','\xc4\x98')
    char = char.replace('\\u0142','\xc5\x82').replace('\\u0141','\xc5\x81')
    char = char.replace('\\u0144','\xc5\x84').replace('\\u0144','\xc5\x83')
    char = char.replace('\\u00f3','\xc3\xb3').replace('\\u00d3','\xc3\x93')
    char = char.replace('\\u015b','\xc5\x9b').replace('\\u015a','\xc5\x9a')
    char = char.replace('\\u017a','\xc5\xba').replace('\\u0179','\xc5\xb9')
    char = char.replace('\\u017c','\xc5\xbc').replace('\\u017b','\xc5\xbb')
    char = char.replace('&#8217;',"'")
    char = char.replace('&#8211;',"-")  
    char = char.replace('&#8230;',"...")    
    char = char.replace('&#8222;','"').replace('&#8221;','"')   
    char = char.replace('[&hellip;]',"...")
    char = char.replace('&#038;',"&")   
    char = char.replace('&#039;',"'")
    char = char.replace('&quot;','"')
    char = char.replace('&nbsp;',".").replace('&amp;','&')
    return char

#ULUBIONE KODI
def openJSON(u):
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
    
def saveJSON(u,j):
    with open(u, 'w', encoding='utf-8') as f:
        json.dump(j, f, ensure_ascii=False, indent=4)
    
def favList():
    fURL=PATH_profile+'ulubione.json'
    js=openJSON(fURL)
    for j in js:
        URL=j[0]
        if 'playCANvod2' in URL:
            isPlayable='true'
            isFolder=False
        else:
            isPlayable='false'
            isFolder=True

        li=xbmcgui.ListItem(j[1])
        li.setProperty("IsPlayable", isPlayable)
        li.setInfo(type='video', infoLabels=eval(j[2]))
        li.setArt({'thumb': j[3], 'poster': j[3], 'banner': j[3], 'icon': j[3], 'fanart':''})
                
        contMenu = []
        contMenu.append(('[B]Usuń z ulubionych[/B]','RunPlugin(plugin://plugin.video.canalplusvod?mode=favDel&url='+quote(j[0])+')'))
        li.addContextMenuItems(contMenu, replaceItems=False)
        
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=URL, listitem=li, isFolder=isFolder)
    
    xbmcplugin.setContent(addon_handle, 'videos')     
    xbmcplugin.endOfDirectory(addon_handle)

def favDel(c):
    fURL=PATH_profile+'ulubione.json'
    js=openJSON(fURL)
    for i,j in enumerate(js):
        if  j[0]==c:
            del js[i]
    saveJSON(fURL,js)
    xbmc.executebuiltin('Container.Refresh()')

def favAdd(u,t,l,i):
    fURL=PATH_profile+'ulubione.json'
    js=openJSON(fURL)
    duplTest=False
    for j in js:
        if j[0]==u:
            duplTest=True
    if not duplTest:
        js.append([u,t,l,i])
        xbmcgui.Dialog().notification('Canal+ VOD', 'Dodano do ulubionych', xbmcgui.NOTIFICATION_INFO)
    else:
        xbmcgui.Dialog().notification('Canal+ VOD', 'Materiał jest już w ulubionych', xbmcgui.NOTIFICATION_INFO)
    saveJSON(fURL,js)
    

class CANALvod(object):
    def __init__(self):
        self.UAweb='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'      
        self.OAUTH = 'https://logowanie.pl.canalplus.com/login'#'https://dev.canalplus.com/pl/oauth'
        self.CREATE_TOKEN = 'https://pass-api-v2.canal-plus.com/provider/services/pl/public/createToken'

        self.mainLOGINurl = 'https://logowanie.pl.canalplus.com/login'
        self.OAUTH_HEADERS = {
                'User-Agent':self.UAweb,
                'Host': 'dev.canalplus.com',}

        self.HEADERS2 = {
                'User-Agent':self.UAweb,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Referer': 'https://logowanie.pl.canalplus.com/',
                'Upgrade-Insecure-Requests': '1',}

        self.HEADERS3 = {
                'User-Agent':self.UAweb,
                'Host': 'www.canalplus.com',}
                
                
        self.HEADERS4 = {
                'User-Agent':self.UAweb,
                'Host': 'pass.canal-plus.com',}    

        self.PASSheaders = {
            'User-Agent':self.UAweb,
            'Host': 'pass-api-v2.canal-plus.com',
        }
              
        self.HODORheaders = {
            'Host': 'hodor.canalplus.pro',
            'user-agent': 'myCANAL/ 4.6.6 (440010924) - Android/9 - android - SM-J330F',
        }
 
        self.mainPage = "https://hodor.canalplus.pro/api/v2/mycanalint/page/{}/102729.json"

        self.cinemaURL = "https://hodor.canalplus.pro/api/v2/mycanalint/page/{}/102783.json"
        self.seriesURL = "https://hodor.canalplus.pro/api/v2/mycanalint/page/{}/102782.json"
        self.kidsURL = "https://hodor.canalplus.pro/api/v2/mycanalint/page/{}/102826.json"
        self.lifeURL = "https://hodor.canalplus.pro/api/v2/mycanalint/page/{}/109674.json"
        self.demandURL = "https://hodor.canalplus.pro/api/v2/mycanalint/page/{}/102961.json" 
            
        self.searchURL = 'https://hodor.canalplus.pro/api/v2/mycanalint/search/mycanal_channel_discover/{}/query/{}?distmodes=[%22catchup%22,%22svod%22,%22tvod%22]&displayNBOLogo=true'    
        self.documentsURL = "https://hodor.canalplus.pro/api/v2/mycanalint/page/{}/102964.json"
        self.sportURL = "https://hodor.canalplus.pro/api/v2/mycanalint/page/{}/102957.json"
        self.collectionsURL = "https://hodor.canalplus.pro/api/v2/mycanalint/page/{}/109266.json"

        #self.kanalyzyczURL = "https://hodor.canalplus.pro/api/v2/mycanalint/page/{}/102961.json"
            
        self.serkategURL = "https://hodor.canalplus.pro/api/v2/mycanalint/page/{}/105344.json"
        self.serkategURL = "https://hodor.canalplus.pro/api/v2/mycanalint/page/{}/104819.json"
            
        self.CMStoken = get_setting('CMStoken')
            
        self.clientid = get_setting('clientid')
        self.portailId = get_setting('portailId')
        
        self.PASStoken = get_setting('PASStoken')
        self.PASSid = get_setting('PASSid')

        self.MACROel = get_setting('MACROel')
        self.MICROel = get_setting('MICROel')
        self.EPGid = get_setting('EPGid')

        self.LIVEtoken = addon.getSetting('livetoken')
        self.DEVID = addon.getSetting('devid')

        self.DEVICE_ID = '_wjfk1x91l'#addon.getSetting('device_id')
        self.CLIENT_ID = addon.getSetting('client_id')
        self.ID_ = addon.getSetting('id_')
        
        self.LOGIN = addon.getSetting('username')
        self.PASSWORD = addon.getSetting('password')
        self.LOGUJ = addon.getSetting('logowanie')

        self.LOGGED = addon.getSetting('logged')
    
    def createDevideId(self):
        t1=int(time.time()*1000)
        t2=t1+1750493
        self.DEVID = '%s-%s:0:%s-%s'%( str(t1), self.gen_hex_code(12), str(t2), self.gen_hex_code(12))
        set_setting('devid', self.DEVID)
    
    def logowanie(self):
        if not self.DEVID:
            self.createDevideId()
        if get_setting('PASSid'):
            if self.createTokens():
                set_setting('logged','true')
                xbmcgui.Dialog().notification('[B]Info[/B]', 'Zalogowano',ikona, 8000,False)
                xbmc.executebuiltin('Container.Refresh')
            else:
                xbmcgui.Dialog().notification('[B]Błąd[/B]', 'Błąd logowania',ikona, 8000,False)
        else:
            xbmcgui.Dialog().notification('[B]Błąd[/B]', 'Uzupełnij ciasteczka w ustawieniach',ikona, 8000,False)
                
    def createTokens(self):
        url='https://pass-api-v2.canal-plus.com/provider/services/pl/public/createToken'
        data={
            "deviceId": self.DEVID,#"1689953387552-f611dc37c902:0:1689955138045-add2e8e75656",
            "media": "web",
            "noCache": "false",
            "portailId": "vbdTj7eb6aM.",
            "sessionId": '%s-%s'%( str(int(time.time()*1000)), self.gen_hex_code(12)),#,"1689975871876-99ccf2dda43a",
            "passIdType": "pass",
            "vect": "INTERNET",
            "zone": "cppol",
            "passId": get_setting('PASSid')
        }
        hea = {
            'user-agent': self.UAweb,
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.canalplus.com',
            'referer': 'https://www.canalplus.com/',
        }

        resp=sess.post(url,headers=hea,data=data).json()
        if resp['response']['errorCode']==0:
            self.PASStoken = resp['response']['passToken']
            self.PASSid = resp['response']['passId']
            self.MACROel = resp['response']['userData']['macroEligibility']
            self.MICROel = resp['response']['userData']['microEligibility']
            self.EPGid = resp['response']['userData']['epgid_OTT']
               
            set_setting('PASStoken',self.PASStoken)
            set_setting('PASSid',self.PASSid)
            set_setting('MACROel',self.MACROel)
            set_setting('MICROel',self.MICROel)
            set_setting('EPGid',self.EPGid)
            
            params = (
                ('appLocation', 'PL'),
                ('offerZone', 'cppol'),
                ('isActivated', '1'),
                ('collectUserData', '1'),
                ('pdsNormal', '['+self.EPGid+']'),
                ('macros', self.MACROel),
                ('micros', self.MICROel),
                ('isAuthenticated', '1'),
                ('paired', '0'),
            )
            response = getRequests('https://hodor.canalplus.pro/api/v2/mycanalint/authenticate.json/android/4.1', headers=self.HODORheaders, params=params)

            self.CMStoken = response['token']
            set_setting('CMStoken', self.CMStoken)
            
            result=True
        else:
            result=False
        
        return result
    
        
#        a = self.PASStoken
#        v = self.PASSid
#    
#        c = self.MACROel
#        d = self.MICROel
#        e = self.EPGid

#        if self.LOGGED == 'true':
#            if self.LOGIN and self.PASSWORD and self.LOGUJ == 'true':
#                import time
#                ts = int(time.time())*100
#                a = str(ts)
#                b = str(czas())
#                if not self.DEVID:
#                    self.DEVID = '%s-%s'%( b, self.gen_hex_code(12))
#            
#                headers = {
#                    #'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
#                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
#                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
#                    'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
#                    'Accept-Encoding':'gzip, deflate, br',
#                    'Host':'logowanie.pl.canalplus.com',
#                    #'DNT': '1',
#                    'Connection': 'keep-alive',
#                    'Upgrade-Insecure-Requests': '1',
#                    'Sec-Fetch-Dest':'document',
#                    'Sec-Fetch-Mode':'navigate',
#                    'Sec-Fetch-Site':'none',
#                    'Sec-Fetch-User':'?1',
#                    'Referer':''
#                }
#                #cookies={}
#            
#                cookies={
#                    '_abck':addon.getSetting('abck_cookie')
#                }
#            
#                response = sess.get('https://logowanie.pl.canalplus.com/login', headers=headers, cookies=cookies, verify=False)
#            
#                for c in response.cookies:
#                    cookies.update({c.name:c.value})
#            
#                execution = re.findall('execution" value="([^"]+)',response.text)#[0]
#                if execution:
#                    execution = execution[0]
#                    #print(execution)
#                    headers = {
#                        'Host': 'logowanie.pl.canalplus.com',
#                        #'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
#                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
#                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#                        'accept-language': 'pl,en-US;q=0.7,en;q=0.3',
#                        'content-type': 'application/x-www-form-urlencoded',
#                        'origin': 'https://logowanie.pl.canalplus.com',
#                        'referer': response.url,
#                        'upgrade-insecure-requests': '1',
#                        'te': 'trailers',
#                    }
#                
#                    data = 'username=' + quote(self.LOGIN) + '&password=' + quote(self.PASSWORD) + '&execution=' + quote(execution) + '&_eventId=submit&geolocation='
#                
#                    response = sess.post(self.mainLOGINurl, headers=headers, cookies=cookies, data=data, verify=False)
#                    for c in response.cookies:
#                        cookies.update({c.name:c.value})#.replace('~-1~','~0~',1)
#                    adres = re.findall('login-url\' href="([^"]+)',response.text,re.DOTALL)
#                    if not adres or adres[0]=='#':
#                        xbmcgui.Dialog().notification('[B]Błąd[/B]', 'Niepoprawne dane logowania',ikona, 8000,False)
#                        add_item('', '[B][COLOR blue]Zaloguj[/COLOR][/B]', ikona, "login", folder=False,fanart=FANART)
#                        return False
#                    adres = adres[0].replace('&amp;','&') if adres else ''
#                    for c in response.cookies:
#                        cookies.update({c.name:c.value})
#                    response = sess.get(adres, headers=self.HEADERS2,cookies=cookies,verify=False)
#                    a1 = response.url
#                    ac = response.cookies

#                    try:
#                        self.PASSid = ac.get('passId',None)
#                        self.PASStoken = ac.get('p_pass_token',None)
#                        self.CMStoken = ac.get('tokenCMS',None)
#                    except:
#                        pass

#                    a11 = self.PASSid
#                    a22 = self.PASStoken
#                    a33 = self.CMStoken
#                
#                    authresponse = re.findall('window\.__data\s*=\s*({.*?});.*?window.REACT_QUERY_STATE',response.text,re.DOTALL)#authresponse = re.findall('window\.__data\s*=\s*({.*?});.*?window.app_config',response.text,re.DOTALL)
#                
#                    data = json.loads(authresponse[0])
#                    data = data.get('user',None)

#                    self.MACROel = data.get("macroEligibility",None)
#                    self.MICROel = data.get("microEligibility",None)
#                    self.EPGid = data.get('epgidOTT',None)
#                    set_setting('PASSid', a11)
#                    set_setting('PASStoken', a22)
#                    set_setting('MACROel', self.MACROel)
#                    set_setting('MICROel', self.MICROel)
#                    set_setting('EPGid', self.EPGid)

#                    params = (
#                        ('appLocation', 'PL'),
#                        ('offerZone', 'cppol'),
#                        ('isActivated', '1'),
#                        ('collectUserData', '1'),
#                        ('pdsNormal', '['+self.EPGid+']'),
#                        ('macros', self.MACROel),
#                        ('micros', self.MICROel),
#                        ('isAuthenticated', '1'),
#                        ('paired', '0'),
#                    )

#                    response = getRequests('https://hodor.canalplus.pro/api/v2/mycanalint/authenticate.json/android/4.1', headers=self.HODORheaders, params=params)
#                    self.CMStoken = response['token']
#                    set_setting('CMStoken', self.CMStoken)
#                
#                    URL_DEVICE_ID = 'https://pass.canal-plus.com/service/HelloJSON.php'
#                
#                    header_device_id = {
#                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
#                        'referer':'https://secure-player.canal-plus.com/one/prod/v2/',
#                        'Cookie': 'p_pass_token='+self.PASStoken+'&passId='+self.PASStoken
#                    }
#                
#                    resp_device_id = sess.get(URL_DEVICE_ID, headers=header_device_id,verify=False )
#    
#                    self.DEVICE_ID = re.compile('').findall(resp_device_id.text)[0]

#                    set_setting('device_id', self.DEVICE_ID)
#                
#                    LOGGED = 'true'
#                    set_setting('logged', LOGGED)
#                    xbmcgui.Dialog().notification('[B]Ok.[/B]', 'Zalogowano poprawnie.',ikona, 8000, False)

#                else:
#                    set_setting('PASSid', self.PASSid)
#                    set_setting('PASStoken', self.PASStoken)
#                    xbmcgui.Dialog().notification('[B]Błąd[/B]', 'Niepoprawne dane logowania',ikona, 8000,False)
#                    add_item('', '[B][COLOR blue]Zaloguj[/COLOR][/B]', ikona, "login", folder=False, fanart=FANART)
#            else:
#                xbmcgui.Dialog().notification('[B]Błąd[/B]', 'Brak danych logowania.',ikona, 8000, False)

#        elif self.LOGGED != 'true':
#            add_item('', '[B][COLOR blue]Zaloguj[/COLOR][/B]', ikona, "login", folder=False, fanart=FANART)
#        return True

    def gen_hex_code(self, myrange=6):
        import random
        return ''.join([random.choice('0123456789abcdef') for x in range(myrange)])
        
    def czs(self, czas, trwa):
        import datetime
        dif=datetime.datetime.now()-datetime.datetime.utcnow()
        try:
            format_date=datetime.datetime.strptime(czas, '%Y-%m-%dT%H:%M:%S.%fZ')
        except TypeError:
            format_date=datetime.datetime(*(time.strptime(czas, '%Y-%m-%dT%H:%M:%S.%fZ')[0:6]))

        format_date = format_date+ dif#datetime.timedelta(hours=2)
        tstampnow = int('{:0}'.format(int(time.mktime(format_date.timetuple()))))
        durat = tstampnow+(int(trwa)/1000)
        dt_object = datetime.datetime.fromtimestamp(durat)
        pocz = format_date.strftime("%H:%M")
        koniec =  dt_object.strftime("%H:%M")
        
        return pocz,koniec,durat
        
    def getch(self, ch):
        out = {}
        fff = ''
        for event_ in ch['events']:
            starttime = event_["timecodes"][0]["start"]
            try:
                duration = event_["timecodes"][0]["duration"] 
            except:
                duration = 0

            pocz, koniec, durat = self.czs(starttime, duration)
            if int(time.time())<durat:
                fff += '%s - %s %s [CR]'%(pocz,koniec, PLchar(event_["title"]))
                out['title'] = fff

        return out
        
    def epgLive(self):
        headers = {
            'Host': 'secure-webtv-static.canal-plus.com',
            'User-Agent': self.UAweb,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        
        out = {}
        epgresponse = requests.get('https://secure-webtv-static.canal-plus.com/metadata/cppol/all/v2.2/globalchannels.json',headers=headers).json()
        for channel in epgresponse['channels']:
            id_ = str(channel['id'])
            out[id_] = self.getch(channel) 

        return out    

    def TVinit(self):
        self.RefreshPassToken()
        headers = {
            'User-Agent': 'myCANAL/4.6.6(440010924) - Android/9 - android - SM-J330F',
            'Content-Type': 'application/json; charset=utf-8',
            'Host': 'secure-mobiletv.canal-plus.com',
        }
        
        headers = {
            'User-Agent': self.UAweb,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
            'Content-Type': 'application/json;charset=utf-8',
            'Origin': 'https://www.canalplus.com',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Referer': 'https://www.canalplus.com/',}
                
        ptok = get_setting('PASStoken')#split('PL=')[-1]
        data ={"ServiceRequest":{"InData":{"PassData":{"Id":0,"Token":ptok},"UserKeyId":self.DEVICE_ID,"DeviceKeyId":self.DEVID,"PDSData":{"GroupTypes":"1;4"}}}}

        data = json.dumps(data)
        epgs = self.epgLive()

        urlk='https://secure-webtv.canal-plus.com/WebPortal/ottlivetv/api/V4/zones/cppol/devices/3/apps/1/jobs/InitLiveTV'

        response = sess.post(urlk, headers=headers, data=data ).json()

        outdata = response["ServiceResponse"]["OutData"]
        self.LIVEtoken = outdata["LiveToken"]
        set_setting('livetoken', self.LIVEtoken)
        grupy = outdata["PDS"]["ChannelsGroups"]["ChannelsGroup"]
        out = []
        for grupa in grupy:
            channels = grupa["Channels"]
            for channel in channels:
                epgid_ = channel["EpgId"]
                try:
                    plot = epgs[str(epgid_)]['title']
                except:
                    plot = ''

                tytul_ = channel["Name"]
                urllogo_ = channel["LogoUrl"]

                urlpage_ = channel["WSXUrl"]
                urlpage_= urlpage_+'|'+ epgid_
                out.append({"title": PLchar(tytul_), "url": urlpage_,'image':urllogo_, "code": '', "plot": plot,'typ':'live'})

        return out
        
    def RefreshLIVEtoken(self):
        
        self.RefreshPassToken()
        headers = {
            'User-Agent': 'myCANAL/4.6.6(440010924) - Android/9 - android - SM-J330F',
            'Content-Type': 'application/json; charset=utf-8',
            'Host': 'secure-mobiletv.canal-plus.com',
        }
        
        headers = {
            'User-Agent': self.UAweb,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
            'Content-Type': 'application/json;charset=utf-8',
            'Origin': 'https://www.canalplus.com',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Referer': 'https://www.canalplus.com/',}
        
        ptok = get_setting('PASStoken')#split('PL=')[-1]
        
        data ={"ServiceRequest":{"InData":{"PassData":{"Id":0,"Token":ptok},"UserKeyId":self.DEVICE_ID,"DeviceKeyId":self.DEVID,"PDSData":{"GroupTypes":"1;4"}}}}

        data = json.dumps(data)

        urlk='https://secure-webtv.canal-plus.com/WebPortal/ottlivetv/api/V4/zones/cppol/devices/3/apps/1/jobs/InitLiveTV'

        response = sess.post(urlk, headers=headers, data=data ).json()

        outdata = response["ServiceResponse"]["OutData"]
        self.LIVEtoken = outdata["LiveToken"]
        set_setting('livetoken', self.LIVEtoken)

        return

    def RefreshPassToken(self):
        self.createTokens()
        
        
    def getContentDemand(self,url):
        out = []
        h1 = {
            'Host': 'hodor.canalplus.pro',
            'user-agent': self.UAweb,
            'accept': '*/*',
            'accept-language': 'pl,en-US;q=0.7,en;q=0.3',
            'origin': 'https://www.canalplus.com',
            'te': 'trailers'
        }

        response = getRequests(url.format(self.CMStoken), headers=h1)
        if 'strates' in response:
            strates = response['strates']
            for strate in strates:
                for content in strate["contents"]:
                    urlpage_ = content['onClick']['URLPage']
                    try:
                        tytul_  = content['onClick']["displayName"]
                    except:
                        tytul_  = content["altImage"]
                    contentID_ = content["contentID"]
                    
                    urllogo_ = content.get('URLImage', "")
                    if urllogo_ == "":
                        urllogo_ = content.get('URLLogoChannel', "")
                        if urllogo_ == "": 
                            urllogo_ = ""
                    
                    urllogo_ = urllogo_.replace('{imageQualityPercentage}','70')
                    urlpage_ = urlpage_+'|'+ contentID_
                    out.append({"title": PLchar(tytul_), "url": urlpage_,'image':urllogo_, "code": '', "plot": '','typ':'cdn'})

        return out

    def getContent(self,url):
        out = []
        npout = []
        typ2 = ''

        if '|' in url:
            url,typ2 = url.split('|')

        if '/query/' in url:
            response = getRequests(url, headers=self.HODORheaders)        
        else:
            response = getRequests(url.format(self.CMStoken), headers=self.HODORheaders)
        

        if 'strates' in response:
            strates = response['strates']

            try:
                boa = response['currentPage']['BOName']
            except:
                boa = ''
            #xbmc.log('@#@boa: %s' % str(boa), LOGNOTICE)
            #xbmc.log('@#@typ2: %s' % str(typ2), LOGNOTICE)
            for strate in strates:

                if 'title' in strate or boa=='Miłość pod choinkę' or boa=='Świąteczna przygoda' or boa=='Święta dla najmłodszych' or boa=='Świąteczne gotowanie' or boa=='Magiczne święta' or boa == 'Channels' or boa == 'Premiery C&I' or boa == 'CANAL+ KIDS' or boa == 'SERIES Fun' or boa == 'AMC' or boa == 'SCI FI' or boa == 'Sundance' or boa == 'Kino TV' or boa == 'Food network' or boa == 'National Geographic' or boa == 'Polsat Explore' or boa == 'Polsat Explore' or boa == 'Polsat History' or boa == 'Polsat Nature' or boa == 'Discovery channel' or boa == 'E! ENTERTAINMENT' or boa == 'Kino Polska' or boa == 'FOX' or boa == 'Romance TV' or boa == '13 ulica' or boa == 'AXN' or boa == 'Warner Tv' or boa == 'Eurosport' or boa == 'Fightklub' or boa == 'Motowizja' or boa == 'Cartoon Network' or boa == 'Boomerang' or boa == 'Disney Channel' or boa == 'Disney Junior' or boa == 'Nickelodeon' or boa == 'Baby TV':
                    if strate['strateMode'] =='standard': 
                        if not typ2:
                            if boa == 'Channels':
                                tytul_ = '    Na życzenie'
                            else:
                                tytul_ = strate['title']

                            if 'button' in strate:
                                urlpage_ = strate['button']['onClick']['URLPage']
                                typ = 'cdn'
                                urlpage_ = urlpage_+'|'+ typ
                            else:
                                if 'contextDetail' in  strate['context']:
                                    typ = strate['context']['contextDetail']
                                    urlpage_ = url+'|'+ typ
                                else:#kategoria ze strony głównej ma podkategorie
                                    typ=strate['context']['context_list_title']
                                    urlpage_ = url+'|'+ typ
                                   
                            out.append({"title": PLchar(tytul_), "url": urlpage_,'image':'', "code": '', "plot": '','typ':typ})
                        
                        else:
                            if 'contextDetail' in strate['context']:
                                if strate['context']['contextDetail'] == typ2 or typ2 == 'cdn':
                                    contents = strate['contents']
                                    for content in contents:
                                        try:
                                            if content['type'] == "image":
                                                continue    
                                        except:
                                            xbmc.log("NOT A TYPE")

                                        try:
                                            tytul_ = content['title']    
                                        except:
                                            tytul_ = content['onClick']['BOName']

                                        contentID = content['contentID']

                                        urllogo_ = content.get('URLImage', "")
                                        if urllogo_ == "":
                                            urllogo_ = content.get('URLLogoChannel', "")
                                            if urllogo_ == "": 
                                                urllogo_ = ""

                                        urllogo_ = urllogo_.replace('{imageQualityPercentage}','70')
                                        urlpage_ = content['onClick']['URLPage']
                                        typ = content['type']
                                        urlpage_ = urlpage_+'|'+ contentID
                                        if 'subtitle' in content:
                                            tytul_+=' [COLOR lightgreen]%s[/COLOR]'%(content['subtitle'])

                                        out.append({"title": PLchar(tytul_), "url": urlpage_,'image':urllogo_, "code": '', "plot": '','typ':typ, 'cid':contentID})

                                elif strate['context']['contextType'] == 'edito': 
                                    if typ2=='41415' or typ2=='41416' or typ2=='41417' or typ2=='41418' or typ2=='41419' or typ2=='70047' or typ2=='70046' or typ2=='70048' or typ2=='70074' or typ2=='70073' or typ2=='70072' or typ2=='70012' or typ2=='70015' or typ2=='70032' or typ2=='70056' or typ2=='70086' or typ2=='70019' or typ2=='70040' or typ2=='70020' or typ2=='70022' or typ2=='70066' or typ2=='70067' or typ2=='70081' or typ2=='70007' or typ2=='70008' or typ2=='70009' or typ2=='70010' or typ2=='70013' or typ2=='70014' or typ2=='70071' or typ2=='70075' or typ2=='70078' or typ2=='70080' or typ2=='70085' or typ2=='70089' or typ2=='70130' or typ2=='24376' or typ2=='70025' or typ2== '70028' or typ2== '70126' or typ2=='70125' or typ2=='70027' or typ2=='70024' or typ2=='70023' or typ2=='70008' or typ2=='70001' or typ2=='70002' or typ2=='70003' or typ2=='70043' or typ2=='70042' or typ2=='70008' or typ2=='70009' or typ2=='70011' or typ2=='70007' or typ2=='70010' or typ2=='70016' or typ2=='70017' or typ2=='70026' or typ2=='70029' or typ2=='70030': #105007.json' in url or '104796.json' in url or '105158.json' in url or '105162.json':
                                        contents = strate['contents']
                                        for content in contents:
                                            try:
                                                tytul_ = content['title']    
                                            except:
                                                tytul_ = content['onClick']['BOName']
                                        
                                            contentID = content['contentID']

                                            urllogo_ = content.get('URLImage', "")
                                            if urllogo_ == "":
                                                urllogo_ = content.get('URLLogoChannel', "")
                                                if urllogo_ == "": 
                                                    urllogo_ = ""
                                        
                                            urllogo_ = urllogo_.replace('{imageQualityPercentage}','70')
                                            urlpage_ = content['onClick']['URLPage']
                                            typ = content['type']
                                            urlpage_ = urlpage_+'|'+ contentID
                                            if 'subtitle' in content:
                                                tytul_+=' [COLOR lightgreen]%s[/COLOR]'%(content['subtitle'])

                                            out.append({"title": PLchar(tytul_), "url": urlpage_,'image':urllogo_, "code": '', "plot": '','typ':typ, 'cid':contentID})
                                else:
                                    continue
                            else:
                                if strate['context']['context_list_title'] == typ2:#lista podkategorii dla kategorri strony głównej
                                    contents = strate['contents']
                                    for content in contents:
                                        try:
                                            tytul_ = content['title']    
                                        except:
                                            tytul_ = content['onClick']['displayName']
                                        
                                        contentID = content['contentID']

                                        urllogo_ = content.get('URLImage', "")
                                        if urllogo_ == "":
                                            urllogo_ = content.get('URLLogoChannel', "")
                                            if urllogo_ == "": 
                                                urllogo_ = ""
                                        
                                        urllogo_ = urllogo_.replace('{imageQualityPercentage}','70')
                                        urlpage_ = content['onClick']['URLPage']
                                        typ = content['type']
                                        urlpage_ = urlpage_+'|'+ contentID
                                        if 'subtitle' in content:
                                             tytul_+=' [COLOR lightgreen]%s[/COLOR]'%(content['subtitle'])

                                        out.append({"title": PLchar(tytul_), "url": urlpage_,'image':urllogo_, "code": '', "plot": '','typ':'', 'cid':contentID})
                                        

                    
                    else:
                        continue
                #elif  boa == 'BBC Player':
                #                    strate = if 
        elif 'currentPage' in response:
            if 'contents' in response:
                contents = response['contents']
                for content in contents:
                    tytul_ = content['title']    
                    contentID = content['contentID']

                    urllogo_ = content.get('URLImage', "")
                    if urllogo_ == "":
                        urllogo_ = content.get('URLLogoChannel', "")
                        if urllogo_ == "": 
                            urllogo_ = ""

                    urllogo_ = urllogo_.replace('{imageQualityPercentage}','70')
                    urlpage_ = content['onClick']['URLPage']
                    typ = content['type']
                    urlpage_ = urlpage_+'|'+ contentID
                    chGroup=content['altLogoChannel'] if 'altLogoChannel' in content else ''
                    if 'subtitle' in content:

                        if 'Odcinek' in content['subtitle'] or 'Sezon' in content['subtitle']:
                            tytul_+=' [COLOR lightgreen]%s[/COLOR]' % (content['subtitle'])

                    out.append({"title": PLchar(tytul_), "url": urlpage_,'image':urllogo_, "code": '', "plot": '','typ':typ,'cid':contentID,'chGroup':chGroup})
                
            elif 'detail' in response and not 'episodes' in response:
                detail = response['detail']
                information = detail['informations']
                if 'seasons' in detail:
                    seasons = detail['seasons']

                    for sezon in seasons:
                        try:
                            tytul_ = sezon['title']    
                        except:
                            tytul_ = sezon['onClick']['displayName']   

                        contentID = sezon['contentID']
                        if 'URLImage' in information:
                            urllogo_ = information['URLImage']
                        elif 'URLLogoChannel' in sezon:
                            urllogo_ = information['URLLogoChannel']
                        else:
                            continue

                        try:
                            plot = information['summary']
                        except:
                            plot = ''

                        urllogo_ = urllogo_.replace('{imageQualityPercentage}','70')
                        urlpage_ = sezon['onClick']['URLPage']
                        try:
                            typ = sezon['type']
                        except:
                            typ = ''
                        urlpage_ = urlpage_+'|'+ contentID

                        out.append({"title": PLchar(tytul_), "url": urlpage_,'image':urllogo_, "code": '', "plot": plot,'typ':typ,'cid':contentID})

            elif 'episodes' in response:
                detail = response['detail']
                information = detail['informations']

                contents = response['episodes']['contents']
                for content in contents:
                    tytul_ = content['title']    
                    contentID = content['contentID']

                    urllogo_ = content.get('URLImage', "")
                    if urllogo_ == "":
                        urllogo_ = content.get('URLLogoChannel', "")
                        if urllogo_ == "": 
                            urllogo_ = ""

                    try:
                        plot = content['summary']+'\n'
                    except:
                        plot=''
                    try:
                        plot+='[B]'+content['contentAvailability']['availabilities']['stream']['label']+'[/B]\n'
                        plot+='[B]do: '+datetime.datetime.fromtimestamp(content['contentAvailability']['availabilities']['download']['availabilityEndDate']/1000).strftime('%Y-%m-%d %H:%M')+'[/B]'
                    except:
                        pass
                    try:
                        maintitle = information['title']
                    except:
                        maintitle=''

                    urllogo_ = urllogo_.replace('{imageQualityPercentage}','70')
                    urlpage_ = content['URLPage']
                    try:
                        typ = content['type']
                    except:
                        typ = 'VoD'
                    urlpage_ = urlpage_+'|'+ contentID
                    tytul_ = '%s - [COLOR lightgreen]%s[/COLOR]' % (maintitle,tytul_)

                    out.append({"title": PLchar(tytul_), "url": urlpage_,'image':urllogo_, "code": '', "plot": plot,'typ':typ,'cid':contentID})
                if response['episodes']['paging']['hasNextPage']:
                    urlp2 = response['episodes']['paging']['URLPage']
                    npout.append({"title": 'Następna strona', "url": urlp2+'|'+typ2})

            if 'paging' in response and not npout:
                if response['paging']['hasNextPage']:
                    urlp2 = response['paging']['URLPage']
                    npout.append({"title": 'Następna strona', "url": urlp2+'|'+typ2})
        
        return out, npout   
 
        
if __name__ == '__main__':

    mode = params.get('mode', None)

    if not mode:
        home()
        xbmcplugin.endOfDirectory(addon_handle)     

    elif mode=='search':
        if CANALvod().LOGGED == 'true':
            query = xbmcgui.Dialog().input(u'Szukaj..., Podaj tytuł filmu', type=xbmcgui.INPUT_ALPHANUM)
            if query:   
                PLAYERPL().ListSearch(query.replace(' ','+'))
            else:
                pass
        else:
            xbmcgui.Dialog().notification('[B]Uwaga[/B]', 'Nie jesteś zalogowany.', xbmcgui.NOTIFICATION_INFO, 6000, False)

    elif mode=='login':
        CANALvod().logowanie()
        
    elif mode=='loginTV':
        xbmcgui.Dialog().notification('NP - sorki', xbmcgui.NOTIFICATION_INFO, 6000, False)
        
    elif mode=='logout':
        yes = xbmcgui.Dialog().yesno("[COLOR orange]Uwaga[/COLOR]", 'Czy na pewno chcesz się wylogować?', yeslabel='TAK', nolabel='NIE')
        if yes:
            set_setting('sesstoken', '')
            set_setting('sessexpir', '')
            set_setting('sessexpir', '')
            set_setting('logged', 'false')
            CANALvod().LOGGED = addon.getSetting('logged')
            
            CANALvod().SESSTOKEN = addon.getSetting('sesstoken')
            CANALvod().SESSEXPIR = addon.getSetting('sessexpir')
            CANALvod().SESSKEY= addon.getSetting('sesskey')
            
            set_setting('device_id', '')
            set_setting('client_id', '')
            set_setting('id_', '')     
            set_setting('PASStoken', '')   
            set_setting('PASSid', '') 
            set_setting('CMStoken', '') 
        
            xbmc.executebuiltin('Container.Refresh') 
    
    elif mode == 'listContent':
        ListContent(exlink)
     
    elif mode == 'listDemand':
        ListDemand(exlink)
        
    elif mode == 'listcateg':
        ListCateg(exlink)
 
    elif mode == 'szukaj':
        if CANALvod().LOGGED == 'true':
            query = xbmcgui.Dialog().input(u'Szukaj, Podaj tytuł...', type=xbmcgui.INPUT_ALPHANUM)
            if query:   
                query=quote(query)
                urlquery = (CANALvod().searchURL).format(CANALvod().CMStoken,query)
                ListContent( urlquery)
        else:
            xbmcgui.Dialog().notification('[B]Uwaga[/B]', 'Nie jesteś zalogowany.',xbmcgui.NOTIFICATION_INFO, 6000, False)

    elif mode == 'opcje':
        addon.openSettings()   

    elif mode == 'listkanaly':
        ListKanaly()
        
    elif mode == 'kreatorm3u':
        KreatorM3U()
        
    elif mode =='playCANvod':
        PLAYvodCANAL(exlink)
        
    elif mode =='listvodmenu':
        ListVodMenu()
        
    elif mode =='playCANvod2':
        PLAYvod2(exlink)
        
    elif mode =='movieDetails':#
        cid=params.get('cid')
        movieDetails(cid)
        
    #FAV
    if mode=='favList':
        favList()
        
    if mode=='favDel':
        u=params.get('url')
        favDel(u)
        
    if mode=='favAdd':
        u=params.get('url')
        t=params.get('title')
        l=params.get('infoLab')
        i=params.get('img')
        favAdd(u,t,l,i)
        
    if mode=='expFav':
        expFav()
        
    if mode=='impFav':
        impFav()


        