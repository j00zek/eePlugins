import json

import sys, io, os
import calendar
from datetime import datetime, timedelta
import time
import collections

import resources.lib.iso8601
import requests
from urllib.parse import quote, unquote

from emukodi import xbmc
from emukodi import xbmcgui
from emukodi import xbmcvfs
from emukodi import xbmcaddon
from emukodi import xbmcplugin

from resources.lib.brotlipython import brotlidec


def resp_text(resp):
    """Return decoded response text."""
    if resp and resp.headers.get('content-encoding') == 'br':
        out = []
        # terrible implementation but it's pure Python
        return brotlidec(resp.content, out).decode('utf-8')
    response_content = resp.text

    return response_content.replace("\'",'"')

class Helper:
    def __init__(self, base_url=None, handle=None):
        self.base_url = base_url
        self.handle = handle
        self.addon = xbmcaddon.Addon('plugin.video.sweettvpl')
        self.addon_name = self.addon.getAddonInfo('id')
        self.addon_version = self.addon.getAddonInfo('version')
        self.datapath = self.translate_path(self.get_path('profile'))
        
        self.art = {'icon': self.addon.getAddonInfo('icon'),
                    'fanart': self.addon.getAddonInfo('fanart'),
                }
        
        
        
        self.proxyport = self.get_setting('proxyport')

        try:
            self.kukis = self.load_file(self.datapath+'kukis', isJSON=True)
        except:
            self.kukis = {}
            
        self._sess = None
        self.kuk = {}

        # API
        
        self.base_api_url = 'https://api.sweet.tv/{}'#SigninService/Email.json'  'https://kanalsportowy.pl/api/{}'
       # self.main_page = self.base_api_url.format('products/sections/main')

        if 0:
            self.auth_url = self.base_api_url.format('SigninService/Email.json')
        else:
            self.auth_url = self.base_api_url.format('SigninService/Start.json')
            self.check_auth_url = self.base_api_url.format('SigninService/GetStatus.json')
        self.token_url = self.base_api_url.format('AuthenticationService/Token.json')
        self.UA ='Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0'
        self.version = '4.7.06'
        self.params = {}
        

        self.username = self.get_setting('username')
        self.password = self.get_setting('password')
        self.subtitles = self.get_setting('subtitles')

            
       # self.API_CorrelationId = self.get_setting('CorrelationId')
        self.uuid = self.get_setting('uuid')
        self.bearer = self.get_setting('bearer')
        self.refresh_token = self.get_setting('refresh_token')
        self.logged = self.get_setting('logged')

        self.headers = {
            'Host': 'api.sweet.tv',
            'user-agent': self.UA,
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'pl',
            'x-device': '1;22;0;2;'+ self.version,
            'origin': 'https://sweet.tv',
            'dnt': '1',
            'referer': 'https://sweet.tv/',
        }
        if  self.bearer:
            self.headers.update({'authorization': self.bearer})

    @property
    def sess(self):
        if self._sess is None:
            self._sess = requests.Session()
            if self.kukis:
                self._sess.cookies.update(self.kukis)
                
                
                self._sess.cookies.update(self.kuk)

        return self._sess    

    def input_dialog(self, text, typ=None):
        typ = xbmcgui.INPUT_ALPHANUM if not typ else typ
        return xbmcgui.Dialog().input(text, type=typ)
        
    def get_path(self ,data):    
        return self.addon.getAddonInfo(data)
        
    def translate_path(self ,data):
        try:
            return xbmcvfs.translatePath(data)
        except:
            return xbmc.translatePath(data).decode('utf-8')
            
    def save_file(self, file, data, isJSON=False):
        with io.open(file, 'w', encoding="utf-8") as f:
            if isJSON == True:
                str_ = json.dumps(data,indent=4, sort_keys=True,separators=(',', ': '), ensure_ascii=False)
                f.write(str(str_))
            else:
                f.write(data)

    def load_file(self, file, isJSON=False):

        if not os.path.isfile(file):
            return None
    
        with io.open(file, 'r', encoding='utf-8') as f:
            if isJSON == True:
                return json.load(f, object_pairs_hook=collections.OrderedDict)
            else:
                return f.read() 

        
    def get_setting(self, setting_id):
        setting = xbmcaddon.Addon(self.addon_name).getSetting(setting_id)
        if setting == 'true':
            return True
        elif setting == 'false':
            return False
        else:
            return setting
    
    def set_setting(self, key, value):
        return xbmcaddon.Addon(self.addon_name).setSetting(key, value)
        
        
    def open_settings(self):
        xbmcaddon.Addon(self.addon_name).openSettings()

    def sleep(self, time):
        return xbmc.sleep(int(time))
    
    def dialog_select(self, heading, label):
        return xbmcgui.Dialog().select(heading,label)
        
    def dialog_multiselect(self, heading, label):
        return xbmcgui.Dialog().dialog_multiselect(heading,label)
        
    def dialog_choice(self, heading, message, agree, disagree):
        return xbmcgui.Dialog().yesno(heading, message, yeslabel=agree, nolabel=disagree)
        
        
    def add_item(self, title, url, playable=False, info=None, art=None, content=None, folder=True, contextmenu = None):

        list_item = xbmcgui.ListItem(label=title)
        if playable:
            list_item.setProperty('IsPlayable', 'true')
            folder = False
        if art:
            list_item.setArt(art)
        else:
            art = {
                'icon': self.addon.getAddonInfo('icon'),
                'fanart': self.addon.getAddonInfo('fanart')
            }
            list_item.setArt(art)
        if info:
            list_item.setInfo('Video', info)
        if content:
            xbmcplugin.setContent(self.handle, content)
        if contextmenu:
            list_item.addContextMenuItems(contextmenu, replaceItems=True)
        xbmcplugin.addDirectoryItem(self.handle, url, list_item, isFolder=folder)

    def eod(self, cache=True):
        xbmcplugin.endOfDirectory(self.handle, cacheToDisc=cache)

    def refresh(self):
        return xbmc.executebuiltin('Container.Refresh()')
        
    def update(self,func=''):
        return xbmc.executebuiltin('Container.Refresh(%s)'%func)
        
    def updatex(self,func=''):
        return xbmc.executebuiltin('Container.Update(%s)'%func)

    def update(self,func=''):
        return xbmc.executebuiltin('Container.Refresh(%s)'%func)
        
    def runplugin(self,func=''):
        return xbmc.executebuiltin('RunPlugin(%s))'%func)
        
    def notification(self, heading, message):
        xbmcgui.Dialog().notification(heading, message, time=3000)
        xbmc.log('\t!!!!!! Dodaj urządzenie kodem [%s] na stronie https://sweet.tv/pl/cabinet' % message, xbmc.LOGWARNING)

    def get_random_mac(self):
        return ':'.join(['%02x'%x for x in os.urandom(6)])

    def request_sess(self, url, method='get', data={}, headers={}, cookies={}, params = {}, result=True, json=False, allow=True , json_data = False):
        params = params if params else self.params
        if method == 'get':
            resp = self.sess.get(url, headers=headers, cookies=cookies, timeout=30, params = params, verify=False, allow_redirects=allow)
        elif method == 'post':
            if json_data:
                resp = self.sess.post(url, headers=headers, json=data, cookies=cookies, timeout=30, params = params, verify=False, allow_redirects=allow)
            else:
                resp = self.sess.post(url, headers=headers, data=data, cookies=cookies, timeout=30, params = params, verify=False, allow_redirects=allow)
        elif method == 'delete':
            resp = self.sess.delete(url, headers=headers, cookies=cookies, timeout=30, params = params, verify=False, allow_redirects=allow)
        if result:
            return resp.json() if json else resp_text(resp)
        else:
            return resp
            

    def PlayVid (self, mpdurl, lic_url='', PROTOCOL='', DRM='', certificate = '', flags=True, subs = None, vod=False):
        xbmc.log('AQQ: mpdurl=%s, lic_url=%s,PROTOCOL=%s,DRM=%s, certificate=%s' % (mpdurl,lic_url, PROTOCOL,DRM,certificate), xbmc.LOGWARNING)
        from inputstreamhelper import Helper
        play_item = xbmcgui.ListItem(path=mpdurl)
        if subs:
            play_item.setSubtitles(subs)
        if PROTOCOL:

            is_helper = Helper(PROTOCOL, drm=DRM)
            if is_helper.check_inputstream():
                if sys.version_info >= (3,0,0):
                    play_item.setProperty('inputstream', is_helper.inputstream_addon)
                else:
                    play_item.setProperty('inputstreamaddon', is_helper.inputstream_addon)
                if 'mpd' in PROTOCOL:
                    play_item.setMimeType('application/xml+dash')
                else:
                    play_item.setMimeType('application/vnd.apple.mpegurl')
                play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
                play_item.setProperty('inputstream.adaptive.manifest_headers', 'User-Agent='+quote(self.UA)+'&Referer='+quote('https://sweet.tv/'))
                play_item.setProperty('inputstream.adaptive.stream_headers', 'User-Agent='+quote(self.UA)+'&Referer='+quote('https://sweet.tv/'))
                if vod==True:
                    play_item.setProperty('ResumeTime', '1')
                    play_item.setProperty('TotalTime', '1')

                if DRM and lic_url:
                    play_item.setProperty('inputstream.adaptive.license_type', DRM)
                    play_item.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
                    play_item.setProperty('inputstream.adaptive.license_key', lic_url)
                    if certificate:
                        play_item.setProperty('inputstream.adaptive.server_certificate', certificate)
                if flags:
                    play_item.setProperty('inputstream.adaptive.license_flags', "persistent_storage")
                play_item.setContentLookup(False)
                
                xbmc.log('AQQ: inputstream: %s' % is_helper.inputstream_addon, xbmc.LOGWARNING)
                xbmc.log('AQQ: inputstream.adaptive.manifest_type: %s' % PROTOCOL, xbmc.LOGWARNING)
                xbmc.log('AQQ: inputstream.adaptive.manifest_headers: %s' % 'User-Agent='+quote(self.UA)+'&Referer='+quote('https://sweet.tv/'), xbmc.LOGWARNING)
                xbmc.log('AQQ: inputstream.adaptive.stream_headers: %s' % 'User-Agent='+quote(self.UA)+'&Referer='+quote('https://sweet.tv/'), xbmc.LOGWARNING)
                
                xbmc.log('AQQ: inputstream.adaptive.license_type: %s' % DRM, xbmc.LOGWARNING)
                xbmc.log('AQQ: inputstream.adaptive.license_key: %s' % play_item.getProperty('inputstream.adaptive.license_key'), xbmc.LOGWARNING)
                xbmc.log('AQQ: inputstream.adaptive.license_type: %s' % DRM, xbmc.LOGWARNING)

        xbmcplugin.setResolvedUrl(self.handle, True, listitem=play_item)
        
    def ffmpeg_player(self, stream_url):
        
        sURL=stream_url+'|User-Agent='+quote(self.UA)+'&Referer='+quote('https://sweet.tv/')
        play_item = xbmcgui.ListItem(path=sURL)
        xbmcplugin.setResolvedUrl(self.handle, True, listitem=play_item)
    
    def formatTime(self, czas, format):
        try:
            formated = datetime.strptime(czas, format) 
        except TypeError:
            formated = datetime(*(time.strptime(czas, format)[0:6]))
        formatedx = (formated).strftime('%H:%M')
        return formatedx

    def getCorrectTime(self, czas):
        try:
            current_date_temp = datetime.strptime(czas, "%Y-%m-%dT%H:%M:%SZ") #'2022-04-16T12:30:00Z'
        except TypeError:
            current_date_temp = datetime(*(time.strptime(czas, "%Y-%m-%dT%H:%M:%SZ")[0:6]))
        datastart = (current_date_temp + timedelta(hours=+2)).strftime('%H:%M')
        return datastart
        
    def timeNow(self, czas = False):
        now=datetime.utcnow()+timedelta(hours=2)
    
        czas=now.strftime('%Y-%m-%d')
    
        try:
            format_date=datetime.strptime(czas, '%Y-%m-%d')
        except TypeError:
            format_date=datetime(*(time.strptime(czas, '%Y-%m-%d')[0:6]))    
        if czas:
            return '&since={}T00%3A00%2B0200&till={}T23%3A59%2B0200'.format(czas,czas)# '&since='+2022-10-09T00:00+0200&till=2022-10-09T23%3A59%2B0200czas
        else:
            return format_date
        
        
    def CreateDays(self):
        dzis=self.timeNow()
        timestampdzis = calendar.timegm(dzis.timetuple())
        tydzien = int(timestampdzis)- 2627424
        out=[]
        for i in range(int(timestampdzis),tydzien,-86400):
            x = datetime.utcfromtimestamp(i)

            dzien = (x.strftime('%d.%m'))
            a1 = x.strftime("%Y.%d.%m")

            try:
                current_date_temp = datetime.strptime(a1, "%Y.%d.%m")
            except TypeError:
                current_date_temp = datetime(*(time.strptime(a1, "%Y.%d.%m")[0:6]))
            datastart = (current_date_temp + timedelta(days=-1)).strftime('%Y-%m-%dT')

            dataend = (current_date_temp).strftime('%Y-%m-%dT')
            dod ='&start_after_time='+datastart+'22%3A00%3A00.000Z&start_before_time='+dataend+'22%3A00%3A00.000Z'

            dnitygodnia = ("poniedziałek","wtorek","środa","czwartek","piątek","sobota","niedziela")
            
            day = x.weekday()
    
            dzientyg = dnitygodnia[day]
    
            out.append({'dzien':dzientyg+ ' '+dzien,'dodane':str(dod)}) 
            
        return out         

    def string_to_date(self, string, string_format):
        s_tuple = tuple([int(x) for x in string[:10].split('-')]) + tuple([int(x) for x in string[11:].split(':')])
        s_to_datetime = datetime(*s_tuple).strftime(string_format)
        return s_to_datetime

    def parse_datetime(self, iso8601_string, localize=False):
        """Parse ISO8601 string to datetime object."""
        datetime_obj = iso8601.parse_date(iso8601_string)
        if localize:
            return self.utc_to_local(datetime_obj)
        else:
            return datetime_obj

    def to_timestamp(self, a_date):
        if a_date.tzinfo:
            epoch = datetime(1970, 1, 1, tzinfo=pytz.UTC)
            diff = a_date.astimezone(pytz.UTC) - epoch
        else:
            epoch = datetime(1970, 1, 1)
            diff = a_date - epoch
        return int(diff.total_seconds())*1000
    

    @staticmethod
    def utc_to_local(utc_dt):
        # get integer timestamp to avoid precision lost
        timestamp = calendar.timegm(utc_dt.timetuple())
        local_dt = datetime.fromtimestamp(timestamp)
        assert utc_dt.resolution >= timedelta(microseconds=1)
        return local_dt.replace(microsecond=utc_dt.microsecond)
