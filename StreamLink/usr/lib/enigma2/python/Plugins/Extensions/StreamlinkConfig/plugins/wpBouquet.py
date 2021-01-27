# -*- coding: utf-8 -*-
#
#   Based on Kodi plugin.video.pilot.wp by c0d34fun licensed under GNU GENERAL PUBLIC LICENSE. Version 2, June 1991
#   Coded by j00zek
#
# ADDED by j00zek

import sys
import os

from wpConfig import headers
from wpConfig import params #'login_url', 'main_url', 'video_url', 'close_stream_url'
from wpConfig import data
from wpConfig import getCookie, saveCookie

def _generate_E2bouquet():
    def doLog(txt, append = 'a' ):
        print txt
        open("/tmp/wpBouquet.log", append).write(txt + '\n')
      
    doLog('', 'w')
    if file_name == '':
        doLog('Ustaw nazwę pliku docelowego!')
        return

    #login
    StoredCookie = getCookie()
    if not StoredCookie:
        StoredCookie = _login()
        if not StoredCookie:
            doLog('Nieudane logowanie. Sprawdź login i hasło w ustawieniach wtyczki.')
            return

    #get channels list
    import requests
    headers.update({'Cookie': StoredCookie})
    response = requests.get(
            params['main_url'],
            verify=False,
            headers=headers,
          ).json()
    
    channelsList = response.get('data', [])

    #generate bouquet
    from channelsMappings import name2serviceDict, name2service4wpDict, name2nameDict
    from datetime import date

    doLog('Generuje bukiet dla %s ...' % frameWork)
    open("/tmp/wpBouquet.log", "a").write('Generuje bukiet dla %s ...\n' % frameWork)
    data = '#NAME PILOT.WP.PL aktualizacja %s\n' % date.today().strftime("%d-%m-%Y")
    for item in channelsList:
        #print item
        if item.get('access_status', '') != 'unsubscribed':
            id = item.get('id', None)
            title = item.get('name', '').strip()
            lcaseTitle = title.lower().replace(' ','')
            standardReference = '%s:0:1:0:0:0:0:0:0:0' % frameWork
            #mapowanie bezpośrednie zdefiniowane dla wp
            ServiceID = name2service4wpDict.get(title , standardReference)
            if ServiceID.startswith(standardReference):
                ServiceID = name2serviceDict.get(name2nameDict.get(lcaseTitle, lcaseTitle) , standardReference)
            #mapowanie po znalezionych kanalach w bukietach
                if ServiceID.startswith(standardReference):
                    doLog("\t- Brak mapowania referencji kanału  %s (%s) dla EPG" % (title, lcaseTitle))
            if not ServiceID.startswith(frameWork):
                ServiceIDlist = ServiceID.split(':')
                ServiceIDlist[0] = frameWork
                ServiceID = ':'.join(ServiceIDlist)
            data += '#SERVICE %s:%s%s%s:%s\n' % (ServiceID, streamlinkURL, params['video_url'].replace(':','%3a') , id, title)
            data += '#DESCRIPTION %s\n' % (title)

    with open(file_name, 'w') as f:
        f.write(data.encode('utf-8'))
        f.close()

    doLog('Wygenerowano bukiet do pliku %s' % file_name)
    f = open('/etc/enigma2/bouquets.tv','r').read()
    if not os.path.basename(file_name) in f:
        doLog('Dodano bukiet do listy')
        if not f.endswith('\n'):
            f += '\n'
        f += '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "%s" ORDER BY bouquet\n' % os.path.basename(file_name)
        open('/etc/enigma2/bouquets.tv','w').write(f)

def _login():
    def cookiesToString(cookies):
        try:
            return "; ".join([str(x) + "=" + str(y) for x, y in cookies.get_dict().items()])
        except Exception as e:
            print str(e)
        return None
      
    import requests
        
    response = requests.post(
            params['login_url'],
            json=data,
            verify=False,
            headers=headers
        )

    meta = response.json().get('_meta', None)
    if meta is not None:
        if meta.get('error', {}).get('name', None) is not None:
            return None
        
    saveCookie(cookiesToString(response.cookies))
    return getCookie()

if __name__ == '__main__':
    if len(sys.argv) >=5:
        file_name = sys.argv[1]
        #print 'filename' , file_name
        #print path + file_name
        data['login'] = sys.argv[2]
        #print 'username' , data['login']
        data['password'] = sys.argv[3]
        #print 'password' , data['password']
        streamlinkURL = 'http%%3a//127.0.0.1%%3a%s/' % sys.argv[4]
        frameWork = sys.argv[5]
        #print frameWork
        _generate_E2bouquet()
    elif len(sys.argv) == 2 and sys.argv[1] == 'checkLogin':
        if _login():
            print 'Zalogowano poprawnie\n\n'
        else:
            print 'Nieudane logowanie. Sprawdź login i hasło w ustawieniach wtyczki.\n\n'

# ORGINAL code for reference plugin.video.pilot.wp-0.1.3
"""
import sys
import os
from urlparse import parse_qsl
import urllib
import emukodi.xbmc as xbmc
import emukodi.xbmcgui as xbmcgui
import emukodi.xbmcplugin as xbmcplugin
import emukodi.xbmcaddon as xbmcaddon
import emukodi.xbmcvfs as xbmcvfs

#constants
base_url = '' #sys.argv[0]
addon_handle = 0 #int(sys.argv[1])
params = {} #dict(parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon(id='plugin.video.pilot.wp')

login_url = 'https://pilot.wp.pl/api/v1/user_auth/login'
main_url = 'https://pilot.wp.pl/api/v1/channels/list?device=androidtv'
video_url = 'https://pilot.wp.pl/api/v1/channel/'
close_stream_url = 'https://pilot.wp.pl/api/v1/channels/close'

headers = {
    'user-agent': 'ExoMedia 4.3.0 (43000) / Android 8.0.0 / foster_e',
    'accept': 'application/json',
    'x-version': 'pl.videostar|3.25.0|Android|26|foster_e',
    'content-type': 'application/json; charset=UTF-8'
}

username = addon.getSetting('username')
password = addon.getSetting('password')
file_name = addon.getSetting('fname')
path = addon.getSetting('path')
#sessionid = params.get('sessionid', '')

#addonInfo = xbmcaddon.Addon().getAddonInfo
dataPath = '/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig' #xbmc.translatePath(addonInfo('profile')).decode('utf-8')
cacheFile = os.path.join(dataPath, 'WPConfigCache.db')


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def add_item(name, image, is_folder, is_playble, payload, plot=''):
    list_item = xbmcgui.ListItem(label=name)

    if is_playble:
        list_item.setProperty("IsPlayable", 'true')
    else:
        list_item.setProperty("IsPlayable", 'false')

    list_item.setInfo(type='video', infoLabels={
                      'title': name, 'sorttitle': name, 'plot': plot})
    list_item.setArt({'thumb': image, 'poster': image, 'banner': image})
    xbmcplugin.addDirectoryItem(
        handle=addon_handle,
        url=build_url(payload),
        listitem=list_item,
        isFolder=is_folder
    )


def saveToDB(table_name, value):
    import sqlite3
    import os
    if os.path.exists(cacheFile):
        os.remove(cacheFile)
    else:
        print('File does not exists')
    conn = sqlite3.connect(cacheFile, detect_types=sqlite3.PARSE_DECLTYPES,
                           cached_statements=20000)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS Cache(%s TEXT)' % table_name)
    c.execute("INSERT INTO Cache('%s') VALUES ('%s')" % (table_name, value))
    conn.commit()
    c.close()

def readFromDB():
    import sqlite3
    conn = sqlite3.connect(cacheFile, detect_types=sqlite3.PARSE_DECLTYPES,
                           cached_statements=20000)
    c = conn.cursor()
    c.execute("SELECT * FROM Cache")
    for row in c:
        if row:
            c.close()
            return row[0]

def cookiesToString(cookies):
    try:
        return "; ".join([str(x) + "=" + str(y) for x, y in cookies.get_dict().items()])
    except Exception as e:
        print (e)
        return ''

def login():
    if len(password) > 0 and len(username) > 0:
        data = {'device': 'AndroidTV', 'login': username, 'password': password}

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
        return cookiesToString(response.cookies)

    else:
        xbmcgui.Dialog().notification('Nieudane logowanie', 'Sprawdź login i hasło w ustawieniach wtyczki.',
                                      xbmcgui.NOTIFICATION_ERROR, 5000)
        return ''

def stream_url(video_id, retry=False):
    cookies = readFromDB()
    if not sessionid or len(video_id) == 0:
        return ''

    url = video_url + video_id
    data = {'format_id': '2', 'device_type': 'android'}

    headers.update({'Cookie': cookies})
    response = requests.get(
        url,
        params=data,
        verify=False,
        headers=headers,
    ).json()

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

    if len(manifest) == 0:
        return
    manifest = manifest + '|user-agent=' + headers['user-agent']
    play_item = xbmcgui.ListItem(path=manifest)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item) 
    
def channels():
    if not sessionid:
        return []
    cookies = readFromDB()
    headers.update({'Cookie': cookies})
    response = requests.get(
        main_url,
        verify=False,
        headers=headers,
    ).json()

    return response.get('data', [])

def generate_m3u():
    if not sessionid:
        return

    if file_name == '' or path == '':
        xbmcgui.Dialog().notification('WP Pilot', 'Ustaw nazwe pliku oraz katalog docelowy.',
                                      xbmcgui.NOTIFICATION_ERROR)
        return

    xbmcgui.Dialog().notification('WP Pilot', 'Generuje liste M3U.',
                                  xbmcgui.NOTIFICATION_INFO)
    data = '#EXTM3U\n'

    for item in channels():
        if item.get('access_status', '') != 'unsubscribed':
            id = item.get('id', None)
            title = item.get('name', '')
            data += '#EXTINF:-1,%s\nplugin://plugin.video.pilot.wp?action=PLAY&channel=%s\n' % (
                title, id)

    f = xbmcvfs.File(path + file_name, 'w')
    f.write(data.encode('utf-8'))
    f.close()

    xbmcgui.Dialog().notification('WP Pilot', 'Wygenerowano liste M3U.', xbmcgui.NOTIFICATION_INFO)

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
            id = params.get('id', '')
            play(id)


if __name__ == '__main__':
    route()  
"""
