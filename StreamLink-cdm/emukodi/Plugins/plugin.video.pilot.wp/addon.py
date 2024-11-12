# -*- coding: utf-8 -*-
import json
import os
import sys

try:
    import urllib.parse as urllib
except:
    pass
import urllib
import requests
from emukodi import xbmcgui
from emukodi import xbmcplugin
from emukodi import xbmcaddon
#from emukodi import xbmc
from emukodi import xbmcvfs
import urllib3
from urllib import parse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from urllib.request import Request as urllib_request, urlopen as urllib_urlopen

#>>> zeby rozwiazac problem error 449
from requests.adapters import HTTPAdapter
import ssl

try:
    from urllib3.util import create_urllib3_context  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover
    # urllib3 <2.0.0 compat import
    from urllib3.util.ssl_ import create_urllib3_context

class SSLContextAdapter(HTTPAdapter):
    # noinspection PyMethodMayBeStatic
    def get_ssl_context(self) -> ssl.SSLContext:
        ctx = create_urllib3_context()
        ctx.load_default_certs()

        # disable weak digest ciphers by default
        ciphers = ":".join(cipher["name"] for cipher in ctx.get_ciphers())
        ciphers += ":!SHA1"
        ctx.set_ciphers(ciphers)

        return ctx

    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = self.get_ssl_context()
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs["ssl_context"] = self.poolmanager.connection_pool_kw["ssl_context"]
        return super().proxy_manager_for(*args, **kwargs)

    def send(self, *args, verify=True, **kwargs):
        # Always update the `check_hostname` and `verify_mode` attributes of our custom `SSLContext` before sending a request:
        # If `verify` is `False`, then `requests` will set `cert_reqs=ssl.CERT_NONE` on the `HTTPSConnectionPool` object,
        # which leads to `SSLContext` incompatibilities later on in `urllib3.connection._ssl_wrap_socket_and_match_hostname()`
        # due to the default values of our `SSLContext`, namely `check_hostname=True` and `verify_mode=ssl.CERT_REQUIRED`.
        if ssl_context := self.poolmanager.connection_pool_kw.get("ssl_context"):  # pragma: no branch
            ssl_context.check_hostname = bool(verify)
            ssl_context.verify_mode = ssl.CERT_NONE if not verify else ssl.CERT_REQUIRED
        return super().send(*args, verify=verify, **kwargs)

class WPplAdapter(SSLContextAdapter):
    def get_ssl_context(self):
        ctx = super().get_ssl_context()
        ctx.check_hostname = False
        ctx.options &= ~ssl.OP_NO_TICKET
        ctx.options &= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1

        return ctx
#<<<

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(parse.parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon(id='plugin.video.pilot.wp')

login_url = 'https://pilot.wp.pl/api/v1/user_auth/login?device_type=android_tv'
main_url = 'https://pilot.wp.pl/api/v1/channels/list?device_type=android_tv'
video_url = 'https://pilot.wp.pl/api/v1/channel/'
close_stream_url = 'https://pilot.wp.pl/api/v1/channels/close?device_type=android_tv'

headers = {
    'user-agent': 'ExoMedia 4.3.0 (43000) / Android 8.0.0 / foster_e',
    'accept': 'application/json',
    'x-version': 'pl.videostar|3.53.0-gms|Android|26|foster_e',
    'content-type': 'application/json; charset=UTF-8'
}

username = addon.getSetting('username')
password = addon.getSetting('password')
file_name = addon.getSetting('fname')
netviapisessid = addon.getSetting('netviapisessid')
netviapisessval = addon.getSetting('netviapisessval')
remote_cookies = addon.getSetting('remote_cookies')
mode = addon.getSetting('mode')
path = addon.getSetting('path')
sessionid = params.get('sessionid', '')

addonInfo = addon.getAddonInfo
dataPath = '/etc/streamlink/pilot.wp/' #xbmcvfs.translatePath(addonInfo('profile'))
cacheFile = os.path.join(dataPath, 'cache.db')


def build_url(query):
    return base_url + '?' + urllib.parse.urlencode(query)


def add_item(name, image, is_folder, is_playable, payload, plot=''):
    list_item = xbmcgui.ListItem(label=name)

    if is_playable:
        list_item.setProperty("IsPlayable", 'true')
    else:
        list_item.setProperty("IsPlayable", 'false')

    list_item.setInfo(type='video', infoLabels={
        'title': name,
        'sorttitle': name,
        'plot': plot})
    list_item.setArt({
        'thumb': image,
        'poster': image,
        'banner': image})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=build_url(payload), listitem=list_item, isFolder=is_folder)


def saveToDB(table_name, value):
    import sqlite3
    import os
    if os.path.exists(cacheFile):
        #print('Zapisuję do:', cacheFile)
        os.remove(cacheFile)
    else:
        print('File does not exists')
    conn = sqlite3.connect(cacheFile, detect_types=sqlite3.PARSE_DECLTYPES, cached_statements=20000)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS Cache(%s TEXT)' % table_name)
    c.execute("INSERT INTO Cache('%s') VALUES ('%s')" % (table_name, value))
    conn.commit()
    c.close()


def readFromDB():
    import sqlite3
    conn = sqlite3.connect(cacheFile, detect_types=sqlite3.PARSE_DECLTYPES, cached_statements=20000)
    c = conn.cursor()
    c.execute("SELECT * FROM Cache")
    for row in c:
        if row:
            c.close()
            return row[0]


def cookiesToString(cookies):
    try:
        return "; ".join([str(x) + "=" + str(y) for x, y in cookies.items()])
    except Exception as e:
        print('exception: ' + e)
        return ''


def login():
    if mode == "0":
        if len(password) > 0 and len(username) > 0:
            data = {'device': 'android_tv',
                    'login': username,
                    'password': password}

            if 0: #j00zek: nie dziala
                response = requests.post(
                    login_url,
                    json=data,
                    verify=False,
                    headers=headers
                )

                meta = response.json().get('_meta', None)
                if meta is not None:
                    if meta.get('error', {}).get('name', None) is not None:
                        xbmcgui.Dialog().notification('Nieudane logowanie', 'Sprawdź login i hasło w ustawieniach wtyczki.',
                                                  xbmcgui.NOTIFICATION_ERROR, 5000)
                        return ''
                saveToDB('wppilot_cache', cookiesToString(response.cookies))
            else:
                dataPost = json.dumps(data).encode()
                req = urllib_request(login_url, dataPost, headers)
                response = urllib_urlopen(req)
                response_data = response.read().decode()
                response_info = str(response.info())
                response.close()
                #print(response_data)
                #print(response_info)
                netviapisessid = ''
                netviapisessval = ''
                for item in response_info.split('\n'):
                    if item.startswith('set-cookie'):
                        if item.find('netviapisessid=') > 0:
                            netviapisessid = item.split('netviapisessid=')[1].split(';')[0]
                            addon.setSetting('netviapisessid',netviapisessid)
                        elif item.find('netviapisessval=') > 0:
                            netviapisessval = item.split('netviapisessval=')[1].split(';')[0]
                            addon.setSetting('netviapisessval',netviapisessval)
            
                if len(netviapisessval) > 0 and len(netviapisessid) > 0:
                    cookies = {'netviapisessid': netviapisessid, 'netviapisessval': netviapisessval}
                    saveToDB('wppilot_cache', cookiesToString(cookies))
            return cookiesToString(cookies)

        else:
            xbmcgui.Dialog().notification('Nieudane logowanie', 'Sprawdź login i hasło w ustawieniach wtyczki.',
                                          xbmcgui.NOTIFICATION_ERROR, 5000)
            return ''
    else:
        netviapisessid = addon.getSetting('netviapisessid')
        netviapisessval = addon.getSetting('netviapisessval')
        if len(netviapisessval) > 0 and len(netviapisessid) > 0:
            cookies = {'netviapisessid': netviapisessid, 'netviapisessval': netviapisessval}
            saveToDB('wppilot_cache', cookiesToString(cookies))
            return cookiesToString(cookies)

        elif len(remote_cookies) > 0:
            cookies_from_url = requests.get(remote_cookies, verify=False, timeout=10).text
            cookies = json.loads(cookies_from_url)
            saveToDB('wppilot_cache', cookiesToString(cookies))
            return cookiesToString(cookies)
        else:
            xbmcgui.Dialog().notification('WP Pilot', 'Uzupełnij ciasteczka w ustawieniach wtyczki',
                                          xbmcgui.NOTIFICATION_ERROR)
            return ''


def stream_url(video_id, retry=False):
    cookies = readFromDB()
    if not sessionid or len(video_id) == 0:
        return ''

    url = video_url + video_id + '?format_id=2&device_type=android_tv'
    data = {'format_id': '2', 'device_type': 'android_tv'}

    session = requests.Session()
    session.mount("https://pilot.wp.pl/", WPplAdapter())
    if 1: #j00zek, ie dziala
        headers.update({'Cookie': cookies})
        response = session.get(
            url,
            params=data,
            verify=False,
            headers=headers,
        ).json()
        #print('response:',response)
        meta = response.get('_meta', None)
        if meta is not None:
            token = meta.get('error', {}).get('info', {}).get('stream_token', None)
            if token is not None:
                json = {'channelId': video_id, 't': token}
                response = requests.post(
                    close_stream_url,
                    json=json,
                    verify=False,
                    headers=headers
                ).json()
                if response.get('data', {}).get('status', '') == 'ok' and not retry:
                    return stream_url(video_id, True)
                else:
                    return
    if 'hls@live:abr' in response[u'data'][u'stream_channel'][u'streams'][0][u'type']:
        return response[u'data'][u'stream_channel'][u'streams'][0][u'url'][0]
    else:
        return response[u'data'][u'stream_channel'][u'streams'][1][u'url'][0]


def play(id):
    manifest = stream_url(id)
    #print('manifest:', manifest)
    #print('headers:', headers)
    if len(manifest) == 0:
        return
    manifest = manifest + '|user-agent=' + headers['user-agent']
    play_item = xbmcgui.ListItem(path=manifest)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)


def channels():
    if not sessionid:
        return []
    cookies = readFromDB()
    if 0: #j00zek, ie dziala
        headers.update({
            'Cookie': cookies})
        response = requests.get(main_url, verify=False, headers=headers, ).json()
        return response.get('data', [])
    else:
        req = urllib_request(main_url)
        req.add_header('Cookie', cookies)
        response = urllib_urlopen(req)
        response_data = response.read().decode()
        response.close()
        channelsList = json.loads(response_data).get('data', [])
        return channelsList
    


def home():
    if not sessionid:
        return
    for item in channels():
        if item.get('access_status', '') != 'unsubscribed':
            title = item.get('name', '')
            icon = item.get('thumbnail_mobile', '')
            id = item.get('id', None)
            add_item(title, icon, False, True, {
                'mode': 'play',
                'channelid': id,
                'sessionid': sessionid})

    xbmcplugin.endOfDirectory(addon_handle)


def generate_m3u():
    global sessionid
    if not sessionid:
        sessionid = login()
    if file_name == '' or path == '':
        xbmcgui.Dialog().notification('WP Pilot', 'Ustaw nazwe pliku oraz katalog docelowy.',
                                      xbmcgui.NOTIFICATION_ERROR)
        return
    xbmcgui.Dialog().notification('WP Pilot', 'Generuje liste M3U.', xbmcgui.NOTIFICATION_INFO)
    data = '#EXTM3U\n'
    dataE2 = '' #j00zek for E2 bouquets
    for item in channels():
        if item.get('access_status', '') != 'unsubscribed':
            channelid = item.get('id', None)
            title = item.get('name', '')
            data += '#EXTINF:-1,%s\nplugin://plugin.video.pilot.wp?action=PLAY&channel=%s\n' % (title, channelid)
            dataE2 += 'plugin.video.pilot.wp/addon.py%3faction=PLAY&channel=' + '%s:%s\n' % (channelid, title) #j00zek for E2 bouquets

    f = xbmcvfs.File(os.path.join(addon.getSetting('path_m3u'), addon.getSetting('m3u_filename')), 'w')
    f.write(data)
    f.close()
    xbmcgui.Dialog().notification('WP Pilot', 'Wygenerowano liste M3U.', xbmcgui.NOTIFICATION_INFO)
    
    f = xbmcvfs.File(os.path.join(addon.getSetting('path_m3u'), 'iptv.e2b'), 'w') #j00zek for E2 bouquets
    f.write(dataE2)
    f.close()
    xbmcgui.Dialog().notification('WP Pilot', 'Wygenerowano listę E2B', xbmcgui.NOTIFICATION_INFO)


def route():
    global sessionid
    if not sessionid:
        sessionid = login()
    mode = params.get('mode', None)
    action = params.get('action', '')
    if action == 'BUILD_M3U':
        generate_m3u()
    elif action == 'PLAY':
        id = params.get('channel', '')
        play(id)
    else:
        if not mode:
            home()
        elif mode == 'play':
            id = params.get('channelid', '')
            play(id)


if __name__ == '__main__':
    route()
