#!//usr/bin/python
# -*- coding: utf-8 -*-
#
########## plugin.video.playerMB. by mbebe licensed under GNU GENERAL PUBLIC LICENSE. Version 2, June 1991 ##########
# minor changes for emukodi j00zek

import sys, re, os
import time
import io
from collections import namedtuple
from contextlib import contextmanager
from datetime import date, datetime, timedelta

if sys.version_info >= (3, 0):
    from urllib.parse import parse_qs, parse_qsl, urlencode, quote_plus, unquote_plus
    import http.cookiejar as cookielib

    # pickle is faster for Python3
    import pickle

    def save_ints(path, seq):
        with open(path, 'wb') as f:
            pickle.dump(seq, f, pickle.HIGHEST_PROTOCOL)

    def load_ints(path):
        with open(path, 'rb') as f:
            return pickle.load(f)

    basestring = str
    unicode = str
    xrange = range

from threading import Thread
import requests
from requests.exceptions import SSLError
import urllib3  # already used by "requests"
from urllib3.exceptions import MaxRetryError, SSLError as SSLError3
from certifi import where
from emukodi import xbmcgui
from emukodi import xbmcplugin
from emukodi import xbmcaddon
from emukodi import xbmc, xbmcvfs
import json
import inputstreamhelper

from emukodi.resources.lib.udata import AddonUserData
# from resources.lib.tools import U, uclean, NN, fragdict 


MetaDane = namedtuple('MetaDane', 'tytul opis foto sezon epizod fanart thumb landscape poster allowed')
MetaDane.__new__.__defaults__ = 5*(None,)
MetaDane.art = property(lambda self: {k: v for k in 'fanart thumb landscape poster'.split()
                                      for v in (getattr(self, k),) if v})

ExLink = namedtuple('ExLink', 'gid slug mode a1 a2')
ExLink.__new__.__defaults__ = 3*(None,)
ExLink.new = classmethod(lambda cls, exlink: cls(*exlink.split(':')[:5]))
# slug = "eurosport", mode = "schedule"
ExLink.beginTimestamp = property(lambda self: self.a1)
ExLink.endTimestamp = property(lambda self: self.a2)

ImageRule = namedtuple('ImageRule', 'width height quality')
ImageRule.ratio = property(lambda self: self.width / self.height)


class NotPlayable(Exception):
    """Item is not playable."""
    @property
    def message(self):
        return self.args[0] if self.args else ''


UA = 'okhttp/3.3.1 Android'
# UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0'
PF = 'ANDROID_TV'
# PF = 'BROWSER

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon('plugin.video.playermb')

PATH = addon.getAddonInfo('path')
try:
    DATAPATH = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
except:
    DATAPATH = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')
CACHEPATH = os.path.join(DATAPATH, 'cache')

RESOURCES = os.path.join(PATH, 'resources')
COOKIEFILE = os.path.join(DATAPATH, 'player.cookie')
SUBTITLEFILE = os.path.join(DATAPATH, 'temp.sub')
M3UFILE = addon.getSetting('m3u_fname')
M3UPATH = addon.getSetting('m3u_path')
MEDIA = os.path.join(RESOURCES, 'media')

ADDON_ICON = os.path.join(RESOURCES, '../icon.png')
FANART = os.path.join(RESOURCES, '../fanart.jpg')
sys.path.append(os.path.join(RESOURCES, 'lib'))

HISTORY_SIZE = 50

addon_data = AddonUserData(os.path.join(DATAPATH, 'data.json'))
kukz = ''

slug_blacklist = {
    'pobierz-i-ogladaj-offline',
}

kanalydata = [
    {"id": 97, "name": "dla dzieci"},
    {"id": 142, "name": "sport"},
    {"id": 143, "name": "programy"},
    {"id": 144, "name": "filmy"},
    {"id": 145, "name": "seriale"},
    {"id": 146, "name": "informacje"}
]

menudata = [
    {'url': 1, 'slug': 'seriale-online', 'title': 'Seriale'},
    {'url': 2, 'slug': 'programy-online', 'title': 'Programy'},
    {'url': 3, 'slug': 'filmy-online', 'title': 'Filmy'},
    {'url': 4, 'slug': 'bajki-dla-dzieci', 'title': 'Dla dzieci'},
    {'url': 5, 'slug': 'strefa-sport', 'title': 'Sport'},
    {'url': 24, 'slug': 'eurosport', 'title': 'Eurosport'},
    {'url': 7, 'slug': 'canal-plus', 'title': 'CANAL+'},
    {'url': 8, 'slug': 'hbo', 'title': 'HBO'},
    {'url': 17, 'slug': 'live', 'title': 'Kanały TV'},
    {'url': 21, 'slug': 'motortrend', 'title': 'MotorTrend'},
    {'url': 22, 'slug': 'hotel-paradise', 'title': 'Hotel Paradise'},
    {'url': 23, 'slug': 'discovery-plus', 'title': 'Discovery+'}
]

serialemenu = {
    "1": [{"id":7,"name":"Bajki","externalId":11},{"id":8,"name":"Obyczajowy","externalId":12},{"id":9,"name":"Komedia","externalId":13},{"id":10,"name":"Sensacyjny","externalId":14},{"id":11,"name":"Dokumentalny","externalId":16},{"id":17,"name":"Thriller","externalId":31},{"id":18,"name":"Horror","externalId":32},{"id":19,"name":"Dramat","externalId":33},{"id":20,"name":"Science Fiction","externalId":34},{"id":22,"name":"Familijny","externalId":36},{"id":26,"name":"Inne","externalId":41},{"id":30,"name":"Akcja","externalId":50},{"id":31,"name":"Animowany","externalId":51},{"id":32,"name":"Biograficzny","externalId":52},{"id":34,"name":"Fantasy","externalId":54},{"id":35,"name":"Historyczny","externalId":55},{"id":36,"name":"Kostiumowy","externalId":56},{"id":37,"name":"Kryminalny","externalId":57},{"id":38,"name":"Melodramat","externalId":58},{"id":39,"name":"Musical","externalId":59},{"id":40,"name":"Przygodowy","externalId":60},{"id":41,"name":"Psychologiczny","externalId":61},{"id":42,"name":"Western","externalId":62},{"id":43,"name":"Wojenny","externalId":63},{"id":46,"name":"Komediodramat","externalId":66},{"id":47,"name":"Telenowela","externalId":67},{"id":52,"name":"Programy edukacyjne","externalId":72},{"id":53,"name":"Filmy animowane","externalId":73}],
    "2":[{"id":1,"name":"Rozrywka","externalId":5},{"id":2,"name":"Poradniki","externalId":6},{"id":3,"name":"Kuchnia","externalId":7},{"id":4,"name":"Zdrowie i Uroda","externalId":8},{"id":5,"name":"Talk-show","externalId":9},{"id":6,"name":"Motoryzacja","externalId":10},{"id":7,"name":"Bajki","externalId":11},{"id":8,"name":"Obyczajowy","externalId":12},{"id":11,"name":"Dokumentalny","externalId":16},{"id":12,"name":"Informacje","externalId":18},{"id":13,"name":"Podróże i Przyroda","externalId":19},{"id":14,"name":"Dokument i Reportaż","externalId":20},{"id":23,"name":"Motorsport","externalId":38},{"id":26,"name":"Inne","externalId":41},{"id":27,"name":"Muzyka","externalId":42},{"id":29,"name":"Dom i Ogród","externalId":48},{"id":31,"name":"Animowany","externalId":51},{"id":32,"name":"Biograficzny","externalId":52},{"id":48,"name":"Hobby","externalId":68},{"id":49,"name":"Kultura","externalId":69},{"id":50,"name":"Moda","externalId":70},{"id":51,"name":"Popularno-naukowe","externalId":71},{"id":52,"name":"Programy edukacyjne","externalId":72},{"id":53,"name":"Filmy animowane","externalId":73}],
    "5":[{"id":6,"name":"Motoryzacja","externalId":10},{"id":12,"name":"Informacje","externalId":18},{"id":23,"name":"Motorsport","externalId":38},{"id":24,"name":"Piłka nożna","externalId":39},{"id":25,"name":"Sporty ekstremalne","externalId":40},{"id":26,"name":"Inne","externalId":41},{"id":59,"name":"Sporty zimowe","externalId":79}],
    "22":[{"id":1,"name":"Rozrywka","externalId":5}],
    "21":[{"id":1,"name":"Rozrywka","externalId":5},{"id":2,"name":"Poradniki","externalId":6},{"id":6,"name":"Motoryzacja","externalId":10},{"id":13,"name":"Podróże i Przyroda","externalId":19},{"id":14,"name":"Dokument i Reportaż","externalId":20},{"id":23,"name":"Motorsport","externalId":38},{"id":48,"name":"Hobby","externalId":68},{"id":49,"name":"Kultura","externalId":69}],
    "7":[{"id":45,"name":"Dokument","externalId":65},{"id":60,"name":"Film","externalId":80},{"id":61,"name":"Serial","externalId":81},{"id":62,"name":"Sport","externalId":82},{"id":63,"name":"Dla dzieci","externalId":83}],
    "8":[{"id":45,"name":"Dokument","externalId":65},{"id":60,"name":"Film","externalId":80},{"id":61,"name":"Serial","externalId":81},{"id":63,"name":"Dla dzieci","externalId":83},{"id":64,"name":"Disney","externalId":84},{"id":65,"name":"Styl życia","externalId":85}],
    "17":[{"id":97,"name":"dla dzieci"},{"id":142,"name":"sport"},{"id":143,"name":"programy"},{"id":144,"name":"filmy"},{"id":145,"name":"seriale"},{"id":146,"name":"informacje"}],
    "3":[{"id":1,"name":"Rozrywka","externalId":5},{"id":3,"name":"Kuchnia","externalId":7},{"id":7,"name":"Bajki","externalId":11},{"id":8,"name":"Obyczajowy","externalId":12},{"id":9,"name":"Komedia","externalId":13},{"id":10,"name":"Sensacyjny","externalId":14},{"id":11,"name":"Dokumentalny","externalId":16},{"id":14,"name":"Dokument i Reportaż","externalId":20},{"id":16,"name":"Piosenki","externalId":30},{"id":17,"name":"Thriller","externalId":31},{"id":18,"name":"Horror","externalId":32},{"id":19,"name":"Dramat","externalId":33},{"id":20,"name":"Science Fiction","externalId":34},{"id":22,"name":"Familijny","externalId":36},{"id":26,"name":"Inne","externalId":41},{"id":30,"name":"Akcja","externalId":50},{"id":31,"name":"Animowany","externalId":51},{"id":32,"name":"Biograficzny","externalId":52},{"id":33,"name":"Erotyczny","externalId":53},{"id":34,"name":"Fantasy","externalId":54},{"id":35,"name":"Historyczny","externalId":55},{"id":36,"name":"Kostiumowy","externalId":56},{"id":37,"name":"Kryminalny","externalId":57},{"id":38,"name":"Melodramat","externalId":58},{"id":39,"name":"Musical","externalId":59},{"id":40,"name":"Przygodowy","externalId":60},{"id":41,"name":"Psychologiczny","externalId":61},{"id":42,"name":"Western","externalId":62},{"id":43,"name":"Wojenny","externalId":63},{"id":44,"name":"Filmy na życzenie","externalId":64},{"id":53,"name":"Filmy animowane","externalId":73}],
    "4":[{"id":7,"name":"Bajki","externalId":11},{"id":9,"name":"Komedia","externalId":13},{"id":10,"name":"Sensacyjny","externalId":14},{"id":16,"name":"Piosenki","externalId":30},{"id":22,"name":"Familijny","externalId":36},{"id":26,"name":"Inne","externalId":41},{"id":30,"name":"Akcja","externalId":50},{"id":31,"name":"Animowany","externalId":51},{"id":34,"name":"Fantasy","externalId":54},{"id":39,"name":"Musical","externalId":59},{"id":40,"name":"Przygodowy","externalId":60},{"id":44,"name":"Filmy na życzenie","externalId":64},{"id":52,"name":"Programy edukacyjne","externalId":72},{"id":53,"name":"Filmy animowane","externalId":73}],
    "23":[{"id":1,"name":"Rozrywka","externalId":5},{"id":2,"name":"Poradniki","externalId":6},{"id":3,"name":"Kuchnia","externalId":7},{"id":4,"name":"Zdrowie i Uroda","externalId":8},{"id":6,"name":"Motoryzacja","externalId":10},{"id":11,"name":"Dokumentalny","externalId":16},{"id":13,"name":"Podróże i Przyroda","externalId":19},{"id":14,"name":"Dokument i Reportaże","externalId":20},{"id":26,"name":"Inne","externalId":41},{"id":29,"name":"Dom i Ogród","externalId":48},{"id":48,"name":"Hobby","externalId":68},{"id":49,"name":"Kultura","externalId":69},{"id":50,"name":"Moda","externalId":70},{"id":51,"name":"Popularno-naukowe","externalId":71}],
}


TIMEOUT = 15

sess = requests.Session()
sess.cookies = cookielib.LWPCookieJar(COOKIEFILE)


def get_bool(key):
    return addon.getSetting(key).lower() == 'true'


def set_bool(key, value):
    return addon.setSetting(key, 'true' if value else 'false')


# URL to test: https://wrong.host.badssl.com
class GlobalOptions(object):
    """Global options."""

    def __init__(self):
        self._session_level = 0
        self.verify_ssl = get_bool('verify_ssl')
        self.use_urllib3 = get_bool('use_urllib3')
        self.ssl_dialog_launched = get_bool('ssl_dialog_launched')

    def ssl_dialog(self, using_urllib3=False):
        if self.ssl_dialog_launched and self._session_level == 0:
            return
        using_urllib3 = bool(using_urllib3)
        options = [u'Wyłącz weryfikację SSL', u'Bez zmian']
        if using_urllib3:
            options.insert(0, u'Użyj wolniejszego połączenia (zalecane)')
        num = xbmcgui.Dialog().select(u'Problem z połączeniem SSL, co teraz?', options)
        if using_urllib3:
            # getRequests3() error
            if num == 0:  # Użyj wolniejszego połączenia
                self.use_urllib3 = False
            elif num == 1:  # Wyłącz weryfikację SSL
                self.verify_ssl = False
        else:
            # getRequests() error
            if num == 0:  # Wyłącz weryfikację SSL
                self.verify_ssl = False
        set_bool('use_urllib3', self.use_urllib3)
        set_bool('verify_ssl', self.verify_ssl)
        set_bool('ssl_dialog_launched', True)
        self.ssl_dialog_launched = True

    def __enter__(self):
        self._session_level += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session_level -= 1


goptions = GlobalOptions()


def media(name, fallback=None):
    """Returns full path to media file."""
    path = os.path.join(MEDIA, name)
    if fallback and not os.path.exists(path):
        return fallback
    return path


def build_url(query):
    query = deunicode_params(query)
    return base_url + '?' + urlencode(query)


def add_item(url, name, image, mode, folder=False, isPlayable=False, infoLabels=None, movie=True,
             itemcount=1, page=None, fanart=None, moviescount=0, properties=None, thumb=None,
             contextmenu=None, art=None, linkdata=None, fallback_image=ADDON_ICON,
             label2=None):
    list_item = xbmcgui.ListItem(label=name)
    if label2 is not None:
        list_item.setLabel2(label2)
    if isPlayable:
        list_item.setProperty("isPlayable", 'true')
    if not infoLabels:
        infoLabels = {'title': name, 'plot': name}
    list_item.setInfo(type="video", infoLabels=infoLabels)
    if not image:
        image = fallback_image
    if image and image.startswith('//'):
        image = 'https:' + image
    art = {} if art is None else dict(art)
    if fanart:
        art['fanart'] = fanart
    if thumb:
        art['thumb'] = fanart
    art.setdefault('thumb', image)
    art.setdefault('poster', image)
    art.setdefault('banner', art.get('landscape', image))
    art.setdefault('fanart', FANART)
    art.setdefault('landscape', image)
    art = {k: 'https:' + v if v and v.startswith('//') else v for k, v in art.items()}
    list_item.setArt(art)
    if properties:
        list_item.setProperties(properties)
    if contextmenu:
        list_item.addContextMenuItems(contextmenu, replaceItems=False)
    # link data used to build link,to support old one
    linkdata = {} if linkdata is None else dict(linkdata)
    if page is not None:
        linkdata['page'] = page
    linkdata['mode'] = mode
    linkdata['url'] = url
    # add item
    ok = xbmcplugin.addDirectoryItem(
        handle=addon_handle,
        url=build_url(linkdata),
        listitem=list_item,
        isFolder=folder)
    return ok


def setView(typ):
    if addon.getSetting('auto-view') == 'false':
        xbmcplugin.setContent(addon_handle, 'videos')
    else:
        xbmcplugin.setContent(addon_handle, typ)


def getmenu():
    for menu in menudata:
        mud="listcateg"
        if menu['slug']=='live':
            mud='listcateg'
        add_item(str(menu['url'])+':'+menu['slug'], menu['title'], ADDON_ICON, mud, folder=True)


def remove_html_tags(text, nice=True):
    """Remove html tags from a string"""
    if nice:
        if re.match(r'^<table .*<td [^>]+$', text, re.DOTALL):
            return ''  # remove player.pl lead fackup
        text = re.sub(r'<p\b[^>]*?>\s*</p>|<br/?>', '\n', text, 0, re.DOTALL)
    return re.sub('<.*?>', '', text, 0, re.DOTALL)


def home():
    playerpl = PLAYERPL()
    playerpl.sprawdzenie1()
    playerpl.sprawdzenie2()
    add_item('', '[B][COLOR khaki]Ulubione[/COLOR][/B]', ADDON_ICON, "favors", folder=True)
    if playerpl.auto_categories:
        playerpl.root()
    else:
        getmenu()
    add_item('', 'Kolekcje', ADDON_ICON, "collect", folder=True)
    add_item('', '[B][COLOR khaki]Szukaj[/COLOR][/B]', ADDON_ICON, "search", folder=True)
    add_item('', '[B][COLOR blue]Opcje[/COLOR][/B]', ADDON_ICON, "opcje", folder=False)
    if playerpl.LOGGED == 'true':
        add_item('', '[B][COLOR blue]Wyloguj[/COLOR][/B]', ADDON_ICON, "logout", folder=False)
    setView('addons')
    # xbmcplugin.setContent(addon_handle, 'tvshows')
    xbmcplugin.endOfDirectory(addon_handle)


def get_addon():
    return addon


def set_setting(key, value):
    return get_addon().setSetting(key, value)


def dialog_progress():
    return xbmcgui.DialogProgress()


def xbmc_sleep(time):
    return xbmc.sleep(time)


def deunicode_params(params):
    if sys.version_info < (3,) and isinstance(params, dict):
        def encode(s):
            return s.encode('utf-8') if isinstance(s, unicode) else s
        params = {encode(k): encode(v) for k, v in params.items()}
    return params


def _getRequests(url, data=None, headers=None, params=None):
    xbmc.log('PLAYER.PL: getRequests(%r, data=%r, headers=%r, params=%r)'
             % (url, data, headers, params), xbmc.LOGDEBUG)
    params = deunicode_params(params)
    if data:
        if headers.get('Content-Type', '').startswith('application/json'):
            content = sess.post(url, headers=headers, json=data, params=params, verify=goptions.verify_ssl)
        else:
            content = sess.post(url, headers=headers, data=data, params=params, verify=goptions.verify_ssl)
    else:
        content = sess.get(url, headers=headers, params=params, verify=goptions.verify_ssl)
    return content.json()


def _getRequests3(url, data=None, headers=None, params=None):
    # urllib3 seems to be faster in some cases
    xbmc.log('PLAYER.PL: getRequests3(%r, data=%r, headers=%r, params=%r)'
             % (url, data, headers, params), xbmc.LOGDEBUG)
    if params:
        params = deunicode_params(params)
        encoded_args = urlencode(params)
        url += '&' if '?' in url else '?'
        url += encoded_args
    pool_kwargs = {}
    if goptions.verify_ssl is False:
        pool_kwargs['cert_reqs'] = 'CERT_NONE'
    elif goptions.verify_ssl is True:
        pool_kwargs['ca_certs'] = where()
    http = urllib3.PoolManager(**pool_kwargs)
    if data:
        if headers.get('Content-Type', '').startswith('application/json'):
            data = json.dumps(data).encode('utf-8')
        resp = http.request('POST', url, headers=headers, body=data)
    else:
        resp = http.request('GET', url, headers=headers)
    text = resp.data.decode('utf-8')
    return json.loads(text)


def getRequests(url, data=None, headers=None, params=None):
    try:
        return _getRequests(url, data=data, headers=headers, params=params)
    except SSLError:
        goptions.ssl_dialog()
    return _getRequests(url, data=data, headers=headers, params=params)


def getRequests3(url, data=None, headers=None, params=None):
    if not goptions.use_urllib3:
        # force use requests
        return getRequests(url, data=data, headers=headers, params=params)
    try:
        return _getRequests3(url, data=data, headers=headers, params=params)
    except MaxRetryError as exc:
        if not isinstance(exc.reason, SSLError3):
            raise
        with goptions:
            goptions.ssl_dialog(using_urllib3=True)
            if not goptions.use_urllib3:
                return getRequests(url, data=data, headers=headers, params=params)
    return _getRequests3(url, data=data, headers=headers, params=params)


class ThreadCall(Thread):
    """
    Async call. Create thread for func(*args, **kwargs), should be started.
    Result will be in thread.result after therad.join() call.
    """

    def __init__(self, func, *args, **kwargs):
        super(ThreadCall, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = None

    def run(self):
        self.result = self.func(*self.args, **self.kwargs)

    @classmethod
    def started(cls, func, *args, **kwargs):
        th = cls(func, *args, **kwargs)
        th.start()
        return th


def idle():

    if float(xbmcaddon.Addon('xbmc.addon').getAddonInfo('version')[:4]) > 17.6:
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
    else:
        xbmc.executebuiltin('Dialog.Close(busydialog)')


def busy():

    if float(xbmcaddon.Addon('xbmc.addon').getAddonInfo('version')[:4]) > 17.6:
        xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
    else:
        xbmc.executebuiltin('ActivateWindow(busydialog)')


def PLchar(*args, **kwargs):
    sep = kwargs.pop('sep', ' ')
    if kwargs:
        raise TypeError('Unexpected keywoard arguemnt(s): %s' % ' '.join(kwargs.keys()))
    out = ''
    for i, char in enumerate(args):
        if type(char) is not str:
            char = char.encode('utf-8')
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
        if i:
            out += sep
        out += char
    return out


def historyLoad():
    return addon_data.get('history.items', [])


def historyAdd(entry):
    if not isinstance(entry, unicode):
        entry = entry.decode('utf-8')
    history = historyLoad()
    history.insert(0, entry)
    addon_data.set('history.items', history[:HISTORY_SIZE])


def historyDel(entry):
    if not isinstance(entry, unicode):
        entry = entry.decode('utf-8')
    history = [item for item in historyLoad() if item != entry]
    addon_data.set('history.items', history[:HISTORY_SIZE])


def historyClear():
    addon_data.remove('history.items')


def generate_m3u(override=True):
    if not M3UFILE or not M3UPATH:
        xbmcgui.Dialog().notification('Player', 'Ustaw nazwe pliku oraz katalog docelowy.', xbmcgui.NOTIFICATION_ERROR)
        return
    playerpl = PLAYERPL()
    playerpl.refreshTokenTVN()
    if playerpl.LOGGED != 'true':
        xbmcgui.Dialog().notification('Player', 'Przed wygenerowaniem listy należy się zalogować!', xbmcgui.NOTIFICATION_ERROR)
        return
    xbmcgui.Dialog().notification('Player', 'Generuje liste M3U.', xbmcgui.NOTIFICATION_INFO)
    data = '#EXTM3U\n' if override else '\n'
    dataE2 = '' #j00zek for E2 bouquets
    tvList = playerpl.getTvList()
    for item in tvList:
        if playerpl.is_allowed(item):
            id = item['id']
            title = item['title']
            img = item['images']['pc'][0]['mainUrl']
            img = 'https:' + img if img.startswith('//') else img
            data += '#EXTINF:-1 tvg-logo="%s",%s\n%s?mode=playm3u&channelid=%s\n' % (img, title, base_url, id)
            dataE2 += 'plugin.video.playermb/main.py%3fmode=playm3u&channelid=' + '%s:%s\n' % (id, title) #j00zek for E2 bouquets
    openMode = 'w' if override else 'a'
    with io.open(M3UPATH + M3UFILE, mode=openMode, encoding="utf-8") as f:
        f.write(data)
    xbmcgui.Dialog().notification('Player', 'Wygenerowano liste M3U.', xbmcgui.NOTIFICATION_INFO)
    
    f = xbmcvfs.File(os.path.join(path_m3u, 'iptv.e2b'), 'w') #j00zek for E2 bouquets
    f.write(dataE2)
    f.close()
    xbmcgui.Dialog().notification('Player', 'Wygenerowano listę E2B', xbmcgui.NOTIFICATION_INFO)


class CountSubfolders(object):
    """Count subfolders (avaliable items in sections) with statement object."""

    def __init__(self, plugin, data, loader, kwargs):
        self.plugin = plugin
        self.data = data
        self.loader = loader
        self.kwargs = kwargs
        self._count = None

    @property
    def count(self):
        """Returns avaliable item count in section by section id."""
        if self._count is None:
            def convert(data):
                if isinstance(data, dict):  # better is Mapping than dict, but not in this code
                    return sum(1 for item in data.get('items', data) if self.plugin.is_allowed(item))
                return data

            # self.plugin.refreshTokenTVN()
            xbmc.log('PLAYER.PL: count folder start', xbmc.LOGDEBUG)
            threads = {item['id']: ThreadCall.started(self.loader, item, **self.kwargs)
                       for item in self.data}
            xbmc.log('PLAYER.PL: count folder prepared', xbmc.LOGDEBUG)
            for th in threads.values():
                th.join()
            xbmc.log('PLAYER.PL: count folder joined', xbmc.LOGDEBUG)
            self._count = {sid: convert(thread.result) for sid, thread in threads.items()}
            xbmc.log('PLAYER.PL: count folder catch data: %r' % self._count, xbmc.LOGDEBUG)
        return self._count

    def title(self, item, title, info=None):
        """Change title name (and title in info if not None)."""
        if self.plugin.skip_unaviable:
            count = self.count.get(item['id'], 0)
            if count:
                fmt = u'{title} [COLOR gray]({count})[/COLOR]'
            else:
                fmt = u'{title} [COLOR gray]([COLOR red]brak[/COLOR])[/COLOR]'
            title = fmt.format(title=title, count=count)
            if info is not None:
                info['title'] = title  # K19 uses infoLabels["title"] with SORT_METHOD_TITLE
        return title


class PLAYERPL(object):

    MaxMax = 10000

    def __init__(self):
        xbmc.log('PLAYERPL().__init__{} %r' % '', xbmc.LOGWARNING)
        self._mylist = None

        self.api_base = 'https://player.pl/playerapi/'
        self.login_api = 'https://konto.tvn.pl/oauth/'

        self.GETTOKEN = self.login_api + 'tvn-reverse-onetime-code/create'
        self.POSTTOKEN = self.login_api + 'token'
        self.SUBSCRIBER = self.api_base + 'subscriber/login/token'
        self.SUBSCRIBERDETAIL = self.api_base + 'subscriber/detail'
        self.JINFO = self.api_base + 'info'
        self.TRANSLATE = self.api_base + 'item/translate'
        self.KATEGORIE = self.api_base + 'item/category/list'
        self.GATUNKI_KATEGORII = self.api_base + 'item/category/{cid}/genre/list'

        self.PRODUCTVODLIST = self.api_base + 'product/vod/list'
        self.PRODUCTLIVELIST = self.api_base + 'product/live/list'
        self.SECTIONLIST = self.api_base + 'product/section/list'
        self.SECTION_CONTENT = self.api_base + 'product/section/{sid}'

        self.PARAMS = {'4K': 'true', 'platform': PF}

        self.HEADERS3 = {
            'Host': 'konto.tvn.pl',
            'user-agent': UA,
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }

        self.ACCESS_TOKEN = addon.getSetting('access_token')
        self.USER_PUB = addon.getSetting('user_pub')
        self.USER_HASH = addon.getSetting('user_hash')
        self.REFRESH_TOKEN = addon.getSetting('refresh_token')
        self.DEVICE_ID = addon.getSetting('device_id')
        self.TOKEN = addon.getSetting('token')
        self.MAKER = addon.getSetting('maker_id')
        self.USAGENT = addon.getSetting('usagent_id')
        self.USAGENTVER = addon.getSetting('usagentver_id')
        self.SELECTED_PROFILE = addon.getSetting('selected_profile')
        self.SELECTED_PROFILE_ID = addon.getSetting('selected_profile_id')
        self.ENABLE_SUBS = addon.getSetting('subtitles')
        self.SUBS_DEFAULT = addon.getSetting('subtitles_lang_default')
        self.LOGGED = addon.getSetting('logged')

        self.update_headers2()

        self.MYLIST_CACHE_TIMEOUT = 3 * 3600  # cache valid time for mylist: 3h
        self.skip_unaviable = get_bool('avaliable_only')
        self.auto_categories = get_bool('auto_categories')
        self.categories_without_genres = addon.getSetting('categories_without_genres').split(',')
        self.fix_api = get_bool('fix_api')
        self.remove_duplicates = get_bool('remove_duplicates')
        self.partial_size = int(addon.getSetting('partial_size') or 1000)
        # self.force_media_resize = get_bool('self.force_media_fanart')
        self.force_media_resize = True
        self.force_media_rules = {
            'smart_tv:mainUrl': ImageRule(1280, 720, 85),
            'pc:mainUrl':       ImageRule(1280, 720, 85),
            'vertical:mainUrl': ImageRule(864, 1154, 85),
        }
        self.force_media_quality = 85
        self.logo_tags = {  # extra tag like "E1" in Eurosport taken from "pc" logo id
            2824: 'E',
            2831: 'E1',
            2838: 'E2',
        }
        self._precessed_vid_list = set()
        self.dywiz = '–'
        self.hard_separator = ' '
        self.hide_soon = get_bool('hide_soon')
        self.week_days = (u'poniedziałek', u'wtorek', u'środa', u'czwartek', u'piątek', u'sobota', u'niedziela')
        self.days_ago = int(addon.getSetting('days_ago') or 31)
        if not self.days_ago:
            self.days_ago = 31
        self.days_ahead = int(addon.getSetting('days_ahead'))

        self.all_items_title = '[B]Wszystkie[/B]'

    def params(self, maxResults=False, **kwargs):
        """
        Get default query params. Extend self.PARAMS.

        maxResults : bool or int
            False to skip, Ftrue for auto or integer
        kwargs : dict(str, any)
            Extra pamars appended to result
        """
        params = dict(self.PARAMS)
        if maxResults or isinstance(maxResults, int):
            if maxResults is True:
                maxResults = self.MaxMax if self.skip_unaviable else self.partial_size
            params['maxResults'] = maxResults or 0
            params['firstResult'] = 0
        params.update(kwargs)
        return params

    def update_headers2(self):
        self.HEADERS2 = {
            'Authorization': 'Basic',
            'API-DeviceInfo': '%s;%s;Android;9;%s;1.0.38(62);' % (
                self.USAGENT, self.USAGENTVER, self.MAKER),
            'API-DeviceUid': self.DEVICE_ID,
            'User-Agent': UA,
            'Host': 'player.pl',
            'X-NewRelic-ID': 'VQEOV1JbABABV1ZaBgMDUFU=',
            'API-Authentication': self.ACCESS_TOKEN,
            'API-SubscriberHash': self.USER_HASH,
            'API-SubscriberPub': self.USER_PUB,
            'API-ProfileUid': self.SELECTED_PROFILE_ID,
        }

    def get_meta_data(self, data):
        if not data.get('active', True):
            return MetaDane('', '', '', None, None)
        tytul = data['title']
        if data.get('uhd'):
            tytul = '%s [4K]' % (tytul or '')
        opis = data.get("description")
        if not opis:
            opis = data.get("lead")
        if opis:
            opis = remove_html_tags(opis).strip()
        images = {}
        # See: https://kodi.wiki/view/Artwork_types
        # New art images must be added to MetaDane
        for prop, inames in {'foto':      [('smart_tv', 'mainUrl'), ('pc', 'mainUrl')],
                             'fanart':    [('smart_tv', 'mainUrl'), ('pc', 'mainUrl')],
                             'thumb':     [('smart_tv', 'miniUrl'), ('mobile', 'miniUrl'),
                                           ('pc', 'miniUrl'), ('pc', 'mainUrl')],
                             'poster':    [('vertical', 'mainUrl'), ('pc', 'mainUrl')],
                             'landscape': [('smart_tv', 'mainUrl'), ('pc', 'mainUrl')],
                             }.items():
            for iname, uname in inames:
                try:
                    images[prop] = data['images'][iname][0][uname]
                except (KeyError, IndexError):
                    pass
                else:
                    if self.force_media_resize:
                        iurl, _, iparams = images[prop].partition('?')
                        iparams = dict(parse_qsl(iparams))
                        if iparams.get('dstw', '').isdigit() and iparams.get('dstw', '').isdigit():
                            rule = self.force_media_rules.get('%s:%s' % (iname, uname))
                            if not rule and iparams.get('srcw', '').isdigit() and iparams.get('srcw', '').isdigit():
                                rule = ImageRule(int(iparams['srcw']), int(iparams['srch']),
                                                 self.force_media_quality)
                            if rule:
                                w, h = int(iparams['dstw']), int(iparams['dsth'])
                                dst_ratio = w / h if h else 1.
                                rule_ration = rule.width / rule.height if rule.height else 1.
                                if w != rule.width:
                                    iparams['dstw'] = rule.width
                                    if -.1 < dst_ratio - rule_ration < .1:
                                        # very close to preffered ratio, use rule.height directly
                                        iparams['dsth'] = rule.height
                                    else:
                                        # far away from preffered ratio, count new height
                                        iparams['dsth'] = h * rule.width // (w or 1)
                                iparams['quality'] = rule.quality
                            else:
                                iparams['quality'] = self.force_media_quality
                            images[prop] = '%s?%s' % (iurl, urlencode(iparams))
                        elif iparams.get('w', '').isdigit() and 'i.eurosport.com' in iurl:
                            rule = self.force_media_rules.get('%s:%s' % (iname, uname))
                            if rule:
                                w = int(iparams['w'])
                                if w < rule.width:
                                    iparams['w'] = (rule.width + 9) // 10 * 10  # MUST be / 10  (nnn0)
                                    images[prop] = '%s?%s' % (iurl, urlencode(iparams))
                    break
            else:
                xbmc.log('PLAYER.PL: no image %s (%s) in %r' % (prop, inames, data.get('images')), xbmc.LOGINFO)
                images[prop] = None
        try:
            logo = self.logo_tags[data['logo']['images']['pc'][0]['id']]
        except (KeyError, IndexError):
            pass
        else:
            tytul = '%s | %s' % (tytul, logo)
            opis = '[B]%s[/B] | %s' % (logo, opis or '')
        sezon = bool(data.get('showSeasonNumber')) or data.get('type') == 'SERIAL'
        epizod = bool(data.get("showEpisodeNumber"))
        allowed = self.is_allowed(data)
        return MetaDane(tytul, opis, sezon=sezon, epizod=epizod, allowed=allowed, **images)

    def createDatas(self):

        def gen_hex_code(myrange=6):
            import random
            return ''.join([random.choice('0123456789abcdef') for x in xrange(myrange)])


        def uniq_usagent():
            usagent_id = ''

            if addon.getSetting('usagent_id'):
                usagent_id = addon.getSetting('usagent_id')
            else:
                usagent_id = '2e520525f3'+ gen_hex_code(6)
            set_setting('usagent_id', usagent_id)
            return usagent_id


        def uniq_usagentver():
            usagentver_id = ''

            if addon.getSetting('usagentver_id'):
                usagentver_id = addon.getSetting('usagentver_id')
            else:
                usagentver_id = '2e520525f2'+ gen_hex_code(6)
            set_setting('usagentver_id', usagentver_id)
            return usagentver_id

        def uniq_maker():
            maker_id = ''

            if addon.getSetting('maker_id'):
                maker_id = addon.getSetting('maker_id')
            else:
                maker_id = gen_hex_code(16)
            set_setting('maker_id', maker_id)
            return maker_id

        def uniq_id():
            device_id = ''

            if addon.getSetting('device_id'):
                device_id = addon.getSetting('device_id')
            else:
                device_id = gen_hex_code(16)
            set_setting('device_id', device_id)
            return device_id
        self.DEVICE_ID =uniq_id()
        self.MAKER = uniq_maker()
        self.USAGENT = uniq_usagent()
        self.USAGENTVER = uniq_usagentver()
        return

    def sprawdzenie1(self):
        xbmc.log('PLAYERPL().sprawdzenie1() %r' % '', xbmc.LOGWARNING)
        if not self.DEVICE_ID or not self.MAKER or not self.USAGENT or not self.USAGENTVER:
            self.createDatas()
        if not self.REFRESH_TOKEN and self.LOGGED == 'true':
            self.remove_mylist()
            POST_DATA = 'scope=/pub-api/user/me&client_id=Player_TV_Android_28d3dcc063672068'
            data = getRequests(self.GETTOKEN, data = POST_DATA, headers=self.HEADERS3)
            kod = data.get('code')
            dg = dialog_progress()
            dg.create('Uwaga','Przepisz kod: [B]%s[/B]\n Na stronie https://player.pl/zaloguj-tv' % kod)
            xbmc.log('\t!!!!!! Przepisz kod: [%s] na stronie https://player.pl/zaloguj-tv' % kod, xbmc.LOGWARNING)

            time_to_wait=340
            secs = 0
            increment = 100 // time_to_wait
            cancelled = False
            b= 'acces_denied'
            while secs <= time_to_wait:
                if (dg.iscanceled()): cancelled = True; break
                if secs != 0: xbmc_sleep(3000)
                secs_left = time_to_wait - secs
                if secs_left == 0: percent = 100
                else: percent = int((secs / time_to_wait) * 100)
                POST_DATA = 'grant_type=tvn_reverse_onetime_code&code=%s&client_id=Player_TV_Android_28d3dcc063672068'%kod
                data = getRequests(self.POSTTOKEN, data=POST_DATA, headers=self.HEADERS3)
                token_type = data.get("token_type",None)
                errory = data.get('error',None)
                if token_type == 'bearer': break
                secs += 1


                dg.update(percent)
                secs += 1
            dg.close()

            if not cancelled:
                self.ACCESS_TOKEN = data.get('access_token',None)
                self.USER_PUB = data.get('user_pub',None)
                self.USER_HASH = data.get('user_hash',None)
                self.REFRESH_TOKEN = data.get('refresh_token',None)

                set_setting('access_token', self.ACCESS_TOKEN)
                set_setting('user_pub', self.USER_PUB)
                set_setting('user_hash', self.USER_HASH)
                set_setting('refresh_token', self.REFRESH_TOKEN)

    def sprawdzenie2(self):

        if self.REFRESH_TOKEN:

            PARAMS = {'4K': 'true','platform': PF}
            self.HEADERS2['Content-Type'] =  'application/json; charset=UTF-8'

            POST_DATA = {"agent":self.USAGENT,"agentVersion":self.USAGENTVER,"appVersion":"1.0.38(62)","maker":self.MAKER,"os":"Android","osVersion":"9","token":self.ACCESS_TOKEN,"uid":self.DEVICE_ID}
            data = getRequests(self.SUBSCRIBER, data = POST_DATA, headers=self.HEADERS2,params=PARAMS)


            self.SELECTED_PROFILE = data.get('profile',{}).get('name',None)
            self.SELECTED_PROFILE_ID = data.get('profile',{}).get('externalUid',None)

            self.HEADERS2['API-ProfileUid'] =  self.SELECTED_PROFILE_ID


            set_setting('selected_profile_id', self.SELECTED_PROFILE_ID)
            set_setting('selected_profile', self.SELECTED_PROFILE)
        if self.LOGGED != 'true':
            add_item('', '[B][COLOR blue]Zaloguj[/COLOR][/B]', ADDON_ICON, "login", folder=False)

    def getTranslate(self,id_):
        PARAMS = {'4K': 'true', 'platform': PF, 'id': id_}
        data = getRequests(self.TRANSLATE, headers=self.HEADERS2, params=PARAMS)
        return data

    def getPlaylist(self, id_):
        self.refreshTokenTVN()
        data = self.getTranslate(str(id_))
        rodzaj = "LIVE" if data.get("type_", "MOVIE") == "LIVE" else "MOVIE"

        HEADERSz = {
            'Authorization': 'Basic',
            # 'API-DeviceInfo': '%s;%s;Android;9;%s;1.0.38(62);'%(self.USAGENT, self.USAGENTVER, self.MAKER ),
            'API-Authentication': self.ACCESS_TOKEN,
            'API-DeviceUid': self.DEVICE_ID,
            'API-SubscriberHash': self.USER_HASH,
            'API-SubscriberPub': self.USER_PUB,
            'API-ProfileUid': self.SELECTED_PROFILE_ID,
            'User-Agent': 'okhttp/3.3.1 Android',
            'Host': 'player.pl',
            'X-NewRelic-ID': 'VQEOV1JbABABV1ZaBgMDUFU=',
        }
        urlk = 'https://player.pl/playerapi/product/%s/player/configuration' % id_
        data = getRequests(urlk, headers=HEADERSz, params=self.params(type=rodzaj))

        try:
            vidsesid = data["videoSession"]["videoSessionId"]
            # prolongvidses = data["prolongVideoSessionUrl"]
        except Exception:
            vidsesid = False

        PARAMS = {'type': rodzaj, 'platform': PF}
        data = getRequests(self.api_base+'item/%s/playlist' % id_, headers=HEADERSz, params=PARAMS)

        if not data:
            urlk = 'https://player.pl/playerapi/item/%s/playlist' % id_
            PARAMS = {'type': rodzaj, 'platform': UA, 'videoSessionId': vidsesid}
            data = getRequests(urlk, headers=HEADERSz, PARAMS=PARAMS)

        xbmc.log('PLAYER.PL: getPlaylist(%r): data: %r' % (id_, data), xbmc.LOGDEBUG)
        code = data.get('code')
        try:
            vid = data['movie']
        except KeyError:
            if code == 'ITEM_NOT_PAID':
                raise NotPlayable('Brak w pakiecie')
            raise
        outsub = []
        try:
            subs = vid['video']['subtitles']
            for lan, sub in subs.items():
                lang = sub['label']

                srcsub = sub['src']
                outsub.append({'lang': lang, 'url': srcsub})
        except Exception:
            pass

        protect = vid['video']['protections']
        if 'widevine' in protect:
            tshiftl = vid.get('video', {}).get('time_shift', {}).get('total_length', 0)
            if tshiftl > 0:
                src += '&dvr=' + str(tshiftl * 1000 + 1000)
            widev = protect['widevine']['src']
            if vidsesid:
                widev += '&videoSessionId=%s' % vidsesid
            src = vid['video']['sources']['dash']['url']
            xbmc.log('PLAYER.PL: widevine src: %r' % (src), xbmc.LOGWARNING)
        else:
            src = vid['video']['sources']['hls']['url']
            # start = vid.get('time_shift', {}).get('start')
            src += '&dvr=86400000'  # one day, @m1992 found hte limit: 262139999
            widev = 'hls'
            xbmc.log('PLAYER.PL: hls src: %r' % (src), xbmc.LOGWARNING)
        return src, widev, outsub

    def refreshTokenTVN(self):
        POST_DATA = 'grant_type=refresh_token&refresh_token=%s&client_id=Player_TV_Android_28d3dcc063672068'%self.REFRESH_TOKEN
        data = getRequests(self.POSTTOKEN,data = POST_DATA, headers=self.HEADERS3)
        if data.get('error_description') == 'Token is still valid.':
            return
        self.ACCESS_TOKEN = data.get('access_token')
        self.USER_PUB = data.get('user_pub')
        self.USER_HASH = data.get('user_hash')
        self.REFRESH_TOKEN = data.get('refresh_token')
        set_setting('access_token', self.ACCESS_TOKEN)
        set_setting('user_pub', self.USER_PUB)
        set_setting('user_hash', self.USER_HASH)
        set_setting('refresh_token', self.REFRESH_TOKEN)
        self.update_headers2()
        return data

    def playvid(self, id):
        def download_subtitles():
            if subt:
                r = requests.get(subt)
                with open(SUBTITLEFILE, 'wb') as f:
                    f.write(r.content)
                play_item.setSubtitles([SUBTITLEFILE])

        try:
            stream_url, license_url, subtitles = self.getPlaylist(str(id))
        except NotPlayable as exc:
            xbmcgui.Dialog().notification('PlayerMB', exc.message, xbmcgui.NOTIFICATION_ERROR)
            xbmc.log('PLAYER.PL: play error: %s' % exc.message, xbmc.LOGERROR)
            return
        subt = ''
        if subtitles and self.ENABLE_SUBS == 'true':
            t = [x.get('lang') for x in subtitles]
            u = [x.get('url') for x in subtitles]
            al = "subtitles"
            if len(subtitles) > 1:
                if self.SUBS_DEFAULT != '' and self.SUBS_DEFAULT in t:
                    subt = next((x for x in subtitles if x.get('lang') == self.SUBS_DEFAULT), None).get('url')
                else:
                    select = xbmcgui.Dialog().select(al, t)
                    if select > -1:
                        subt = u[select]
                        addon.setSetting(id='subtitles_lang_default', value=str(t[select]))
                    else:
                        subt = ''
            else:
                subt = u[0]

        if license_url == 'hls':
            from inputstreamhelper import Helper
            stream_proto = license_url
            is_helper = Helper(stream_proto)
            if is_helper.check_inputstream():
                play_item = xbmcgui.ListItem(path=stream_url)
                # if stream.mime is not None:
                #     play_item.setMimeType(stream.mime)
                play_item.setContentLookup(False)
                play_item.setProperty('inputstream', is_helper.inputstream_addon)
                play_item.setProperty("IsPlayable", "true")
                play_item.setProperty('inputstream.adaptive.manifest_type', stream_proto)
            else:
                play_item = xbmcgui.ListItem(path=stream_url)
        elif license_url:
            # DRM
            import inputstreamhelper

            PROTOCOL = 'mpd'
            DRM = 'com.widevine.alpha'

            str_url = stream_url

            HEADERSz = {
                'User-Agent': UA,
            }

            is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
            if not is_helper.check_inputstream():
                xbmc.log('PLAYER.PL: InputStream filed for %r' % license_url, xbmc.LOGWARNING)
            play_item = xbmcgui.ListItem(path=str_url)
            xbmc.log('AQQ: str_url %r' % str_url, xbmc.LOGWARNING)
            play_item.setContentLookup(False)
            download_subtitles()

            if sys.version_info >= (3, 0):
                play_item.setProperty('inputstream', is_helper.inputstream_addon)
            else:
                play_item.setProperty('inputstreamaddon', is_helper.inputstream_addon)
            play_item.setMimeType('application/xml+dash')
            play_item.setContentLookup(False)
            play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
            xbmc.log('AQQ: PROTOCOL %r' % PROTOCOL, xbmc.LOGWARNING)
            play_item.setProperty('inputstream.adaptive.license_type', DRM)
            xbmc.log('AQQ: DRM %r' % DRM, xbmc.LOGWARNING)
            if 'dvr' in str_url:
                play_item.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
            play_item.setProperty('inputstream.adaptive.license_key', license_url+'|Content-Type=|R{SSM}|')
            xbmc.log('AQQ: license_url %r' % license_url, xbmc.LOGWARNING)
            play_item.setProperty('inputstream.adaptive.license_flags', "persistent_storage")
            play_item.setProperty('inputstream.adaptive.stream_headers', urlencode(HEADERSz))
            xbmc.log('AQQ: stream_headers %r' % HEADERSz, xbmc.LOGWARNING)
        else:
            # no DRM
            play_item = xbmcgui.ListItem(path=stream_url)
            download_subtitles()
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

    def slug_data(self, idslug, maxResults=True, plOnly=False, sort='createdAt', params=None):
        xbmc.log('PLAYER.PL: slug %s started' % idslug, xbmc.LOGDEBUG)
        gid, slug = idslug.split(':')
        PARAMS = self.params(maxResults=maxResults)
        PARAMS['category[]'] = slug
        PARAMS['sort'] = sort
        PARAMS['order'] = 'desc'
        if gid:
            PARAMS['genreId[]'] = gid
        if plOnly:
            PARAMS['vodFilter[]'] = 'POLISH'
        if params:
            PARAMS.update(params)
        urlk = self.PRODUCTVODLIST
        data = getRequests3(urlk, headers=self.HEADERS2, params=PARAMS)
        xbmc.log('PLAYER.PL: slug %s done' % idslug, xbmc.LOGDEBUG)
        return data

    def async_slug_data(self, idslug, maxResults=True, plOnly=False):
        thread = ThreadCall(self.slug_data, idslug, maxResults=maxResults, plOnly=plOnly)
        thread.start()
        return thread

    def get_mylist(self):
        xbmc.log('PLAYER.PL: mylist started', xbmc.LOGDEBUG)
        data = getRequests3('https://player.pl/playerapi/subscriber/product/available/list?4K=true&platform=ANDROID_TV',
                            headers=self.HEADERS2, params={})
        xbmc.log('PLAYER.PL: mylist done', xbmc.LOGDEBUG)
        return set(data)

    @property
    def mylist_cache_path(self):
        return os.path.join(CACHEPATH, 'mylist')

    def save_mylist(self, mylist=None):
        path = self.mylist_cache_path
        if mylist is None:
            mylist = self.get_mylist()
        try:
            os.makedirs(CACHEPATH)
        except OSError:
            pass  # exists
        save_ints(path, mylist)

    def load_mylist(self, auto_cache=True):
        path = self.mylist_cache_path
        try:
            if time.time() - os.stat(path).st_mtime < self.MYLIST_CACHE_TIMEOUT:
                return set(load_ints(path))
        except OSError:
            pass
        except Exception as exc:
            xbmc.log('PLAYER.PL: Can not load mylist from %r: %r' % (path, exc), xbmc.LOGWARNING)
            self.remove_mylist()
        mylist = self.get_mylist()
        if auto_cache:
            try:
                self.save_mylist(mylist)
            except OSError:
                xbmc.log('PLAYER.PL: Can not save mylist to %r' % path, xbmc.LOGWARNING)
        return mylist

    def remove_mylist(self):
        path = self.mylist_cache_path
        if os.path.exists(path):
            try:
                os.unlink(path)
            except Exception as exc:
                xbmc.log('PLAYER.PL: Can not remove mylist cache %r: %r' % (path, exc),
                         xbmc.LOGWARNING)

    @property
    def mylist(self):
        if self._mylist is None:
            self._mylist = self.load_mylist()
        return self._mylist

    @mylist.deleter
    def mylist(self):
        self.remove_mylist()

    @contextmanager
    def count_subfolders(self, data, loader, **kwargs):
        """Count subfolders (avaliable items in sections) with statement."""
        count = CountSubfolders(self, data, loader, kwargs)
        try:
            yield count
        finally:
            del count

    def is_allowed(self, vod):
        """Check if item (video, folder) is avaliable in current pay plan."""
        return (
            # not have to pay and not on ncPlus, it's means free
            not (vod.get('payable') or vod.get('ncPlus'))
            # or it's on myslit, it's means it is in pay plan
            or vod.get('id') in self.mylist)

    def add_media_item(self, mud, vid, meta=None, prefix=None, suffix=None, folder=False, isPlayable=None,
                       vod=None, linkdata=None, label2=None, info=None):
        """
        Add default media item to xbmc.list.
        if `isPlayable` is None (default) it's forced to `not folder`,
        because folder is not playable.
        """
        if vid in self._precessed_vid_list:
            xbmc.log(u'PLAYER.PL: item %s (%r) already processed' % (vid, meta.tytul), xbmc.LOGDEBUG)
            if self.remove_duplicates:
                return
        if meta is None and vod is not None:
            meta = self.get_meta_data(vod)
        if meta is None:
            meta = MetaDane('', '', '', '', '')  # tytul opis foto sezon epizod
        allowed = (meta and meta.allowed is True) or vid in self.mylist
        if allowed or not self.skip_unaviable:
            no_playable = not (mud or '').strip() or meta.sezon
            if no_playable or not allowed:
                isPlayable = False
                # folder = True
            elif isPlayable is None:
                isPlayable = not folder
            if suffix is None:
                suffix = u''
                if (no_playable and not folder) or not allowed:
                    # auto suffix for non-playable video
                    suffix += u' - [COLOR khaki]([I]brak w pakiecie[/I])[/COLOR]'
                sched = vod and vod.get('displaySchedules')
                if sched and sched[0].get('type') == 'SOON':
                    suffix += u' [COLOR gray] [LIGHT] (od %s)[/LIGHT][/COLOR]' % sched[0]['till'][:-3]
            suffix = suffix or ''
            title = PLchar(prefix or '', meta.tytul, suffix, sep='')
            descr = PLchar(meta.opis or meta.tytul, suffix, sep='\n')
            info = {
                'title': title,
                'plot': descr,
                'plotoutline': descr,
            }
            if info:
                info.update(info)
            add_item(str(vid), title, meta.foto or ADDON_ICON, mud,
                     folder=folder, isPlayable=isPlayable, infoLabels=info, art=meta.art,
                     linkdata=linkdata, label2=label2)
            self._precessed_vid_list.add(vid)

    def process_list(self, vod_list, subitem=None):
        # WIP !!!
        """
        Process list of VOD items.
        Check if playable or serial. Add items to Kodi list.
        """
        for vod in vod_list:
            if subitem:
                vod = vod[subitem]
            vid = vod['id']
            meta = self.get_meta_data(vod)
            mud, fold = ' ', None
            if vod['type'] == 'SERIAL':
                mud = 'listcategSerial'
                fold = True
            elif vod['type'] == 'SECTION':
                add_item('%s:' % vid, meta.tytul, meta.foto, mode='section_list', folder=True, isPlayable=False)
                continue
            else:
                mud = 'playvid'
                fold = False
            self.add_media_item(mud, vid, meta, folder=fold, vod=vod)

    def process_vod_list(self, vod_list, subitem=None):
        """
        Process list of VOD items.
        Check if playable or serial. Add items to Kodi list.
        """
        for vod in vod_list:
            if subitem:
                vod = vod[subitem]
            vid = vod['id']
            meta = self.get_meta_data(vod)
            mud, fold = ' ', None
            if vod['type'] == 'SERIAL':
                mud = 'listcategSerial'
                fold = True
            elif vod['type'] == 'SECTION':
                add_item('%s:' % vid, meta.tytul, meta.foto, mode='section_list', folder=True, isPlayable=False)
                continue
            else:
                mud = 'playvid'
                fold = False
            self.add_media_item(mud, vid, meta, folder=fold, vod=vod)

    def section_list(self, exlink):
        ex = ExLink.new(exlink)
        url = self.SECTION_CONTENT.format(sid=ex.gid)
        data = getRequests(url, headers=self.HEADERS2, params=self.params())
        self.process_vod_list(data['items'])
        setView('tvshows')
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)

    def listCollection(self):
        def load_subfolders(item):
            urlk = 'https://player.pl/playerapi/product/section/%s' % item['id']
            return getRequests(urlk, headers=self.HEADERS2, params=self.params(maxResults=True))

        self.refreshTokenTVN()
        data = getRequests(self.SECTIONLIST,
                           headers=self.HEADERS2, params=self.params(maxResults=True, order='asc'))
        mud = "listcollectContent"
        with self.count_subfolders(data, load_subfolders) as count:
            for i, vod in enumerate(data):
                vid = vod['id']
                slug = vod['slug']
                meta = self.get_meta_data(vod)
                info = {
                    'title': PLchar(meta.tytul),
                    'plot': PLchar(meta.opis or meta.tytul),
                }
                name = count.title(vod, meta.tytul, info)
                add_item(str(vid)+':'+str(slug), name, meta.foto, mud, folder=True,
                         infoLabels=info, art=meta.art)
        setView('movies')
        xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE, label2Mask="%R, %Y, %P")
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)

    def listFavorites(self):
        self.refreshTokenTVN()

        data = getRequests('https://player.pl/playerapi/subscriber/bookmark',
                           headers=self.HEADERS2, params=self.params(type='FAVOURITE'))
        try:
            self.process_vod_list(data['items'], subitem='item')
            setView('tvshows')
            # xbmcplugin.setContent(addon_handle, 'tvshows')
            xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE, label2Mask="%R, %Y, %P")
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
        except:
            raise  # skip fallback
            # Falback: Kodi Favorites
            xbmc.executebuiltin("ActivateWindow(10134)")

    def listSearch(self, query):
        self.refreshTokenTVN()
        PARAMS = self.params(keyword=query, maxResults=self.MaxMax)

        urlk = 'https://player.pl/playerapi/product/live/search'
        lives = getRequests(urlk, headers=self.HEADERS2, params=PARAMS)
        xbmc.log('PLAYER.PL: listSearch(%r): params=%r, #live=%r' % (query, PARAMS, len(lives.get('items', []))),
                 xbmc.LOGDEBUG)
        lives = lives['items']
        # -- commented out, it does do nothing   (rysson)
        # if len(lives)>0:
        #     for live in lives:
        #         ac=''
        urlk = 'https://player.pl/playerapi/product/vod/search'
        data = getRequests(urlk, headers=self.HEADERS2, params=PARAMS)
        xbmc.log('PLAYER.PL: listSearch(%r): params=%r, #vod=%r' % (query, PARAMS, len(data.get('items', []))),
                 xbmc.LOGDEBUG)
        self.process_vod_list(data['items'])
        # setView('tvshows')
        xbmcplugin.setContent(addon_handle, 'videos')
        xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE, label2Mask="%R, %Y, %P")
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)

    def listEpizody(self, tytsezid):
        idmain, idsezon = tytsezid.split(':')
        self.refreshTokenTVN()

        urlk = 'https://player.pl/playerapi/product/vod/serial/%s/season/%s/episode/list' % (idmain, idsezon)

        epizody = getRequests(urlk, headers=self.HEADERS2, params=self.PARAMS)
        for vod in epizody:
            vid = vod['id']
            meta = self.get_meta_data(vod)
            epiz = vod["episode"]
            sez = (vod["season"]["number"])
            tyt = PLchar((vod["season"]["serial"]["title"]))
            if 'fakty-' in vod.get('shareUrl', ''):
                tytul = PLchar(tyt, self.dywiz, vod['title'])
            else:
                tytul = '%s %s S%02dE%02d' % (tyt, PLchar(self.dywiz), sez, epiz)
            if vod.get('title'):
                tytul += PLchar('', self.dywiz, vod['title'].strip())
            meta = meta._replace(tytul=tytul)
            self.add_media_item('playvid', vid, meta, folder=False, vod=vod)
        setView('episodes')
        # xbmcplugin.setContent(addon_handle, 'episodes')
        xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE, label2Mask="%R, %Y, %P")
        xbmcplugin.endOfDirectory(addon_handle)

    def getSezony(self, id, tytul, opis, foto, typ):
        self.refreshTokenTVN()
        urlk = 'https://player.pl/playerapi/product/vod/serial/%s/season/list' % id
        out = []
        sezony = getRequests(urlk, headers=self.HEADERS2, params=self.PARAMS)
        for sezon in sezony:
            seas = str(sezon['number'])
            urlid = '%s:%s' % (id, sezon['id'])
            title = '%s - Sezon %s' % (tytul, seas)
            if not typ:
                seas = str(sezon["display"])
                title = '%s / %s' % (tytul, seas)
            out.append({'title': PLchar(title), 'url': urlid, 'img': foto, 'plot': PLchar(opis)})
        return out

    def listCategSerial(self, id):
        self.refreshTokenTVN()
        urlk = 'https://player.pl/playerapi/product/vod/serial/%s' % id
        data = getRequests(urlk, headers=self.HEADERS2, params=self.PARAMS)
        meta = self.get_meta_data(data)
        typ = True
        if meta.sezon or meta.epizod:
            if not meta.sezon:
                typ = False
            items = self.getSezony(id, meta.tytul, meta.opis, meta.foto, typ)
            for f in items:
                add_item(name=f.get('title'), url=f.get('url'), mode='listEpizody', image=f.get('img'),
                         folder=True, infoLabels=f)
        setView('seasons')
        # xbmcplugin.setContent(addon_handle, 'episodes')
        xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE, label2Mask="%R, %Y, %P")
        xbmcplugin.endOfDirectory(addon_handle)

    def listCollectContent(self, idslug):
        self.refreshTokenTVN()
        vid, slug = idslug.split(':')
        urlk = 'https://player.pl/playerapi/product/section/%s' % (vid)
        data = getRequests(urlk, headers=self.HEADERS2, params=self.params(maxResults=True))
        self.process_vod_list(data['items'])
        setView('movies')
        # xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE,
                                 label2Mask="%R, %Y, %P")
        xbmcplugin.endOfDirectory(addon_handle)

    def listCategContent(self, idslug):
        self.refreshTokenTVN()
        gid, slug = idslug.split(':')
        if slug == 'live':
            dane = self.getTvs(genre=gid)
            for f in dane:
                add_item(name=f.get('title'), url=f.get('url'), mode='playvid', image=f.get('img', FANART),
                         folder=False, isPlayable=True, infoLabels=f)
        else:
            data = self.slug_data(idslug, maxResults=True if gid else self.MaxMax)
            data = data['items']
            if self.hide_soon and slug == 'eurosport':
                data = self.skip_soon_vod_iter(data)
            self.process_vod_list(data)
            setView('tvshows')
            # xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
            xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE, label2Mask="%R, %Y, %P")
        xbmcplugin.endOfDirectory(addon_handle)

    def getTvList(self, genre=None):
        self.refreshTokenTVN()
        urlk = 'https://player.pl/playerapi/product/live/list'
        reqargs = {}
        if genre:
            reqargs['genreId[]'] = str(genre)
        data = getRequests(urlk, headers=self.HEADERS2, params=self.params(**reqargs))
        return data

    def getTvs(self, genre=None):
        data = self.getTvList(genre)
        out = []
        for dd in data:
            vid = dd['id']
            tyt = PLchar(dd['title'])
            foto = dd['images']['pc'][0]['mainUrl']
            foto = 'https:' + foto if foto.startswith('//') else foto
            # urlid = '%s:%s'%(vid,'kanal')  # mbebe
            urlid = vid  # kszaq
            opis = dd.get('lead', '')
            allowed = self.is_allowed(dd)
            if not allowed:
                tyt += ' - [I][COLOR khaki](brak w pakiecie)[/COLOR][/I]'
            if allowed or not self.skip_unaviable:
                out.append({'title': tyt, 'url': urlid, 'img': foto, 'plot': PLchar(opis)})
                xbmc.log('PLAYER.PL: title "%s", url="%s"' % (tyt,urlid), xbmc.LOGWARNING)
        return out

    def listCateg(self, idslug):
        getRequests(url=self.KATEGORIE, headers=self.HEADERS2, params=self.params())
        gid, slug = idslug.split(':')
        if slug == 'live':
            data = self.getTvs()
            for f in data:
                add_item(name=f.get('title'), url=f.get('url'), mode='playvid', image=f.get('img'),
                         folder=False, isPlayable=True, infoLabels=f)
        else:
            def load_subfolders(item):
                return self.slug_data('%s:%s' % (item['id'], slug))
            try:
                data = serialemenu[gid]
            except KeyError:
                data = getRequests(url='https://player.pl/playerapi/item/category/%s/genre/list' % gid,
                                   headers=self.HEADERS2, params=self.params())
            with self.count_subfolders(data, load_subfolders) as count:
                if self.skip_unaviable:
                    data.append({'id': '', 'name': self.all_items_title, '_props_': {'SpecialSort': 'top'}})
                for f in data:
                    name = f['name']
                    urlk = '%s:%s' % (f['id'], slug)
                    count.title(f, name)
                    image = media('genre/%s.png' % f['id'], fallback=ADDON_ICON)
                    add_item(urlk, name, image, mode='listcategContent', folder=True, isPlayable=False,
                             properties=f.get('_props_'))

        xbmc.log('PLAYER.PL: folder items done', xbmc.LOGWARNING)
        setView('tvshows')
        xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE,
                                 label2Mask="%R, %Y, %P")
        xbmcplugin.endOfDirectory(addon_handle)
        xbmc.log('PLAYER.PL: folder done, skip=%s' % self.skip_unaviable, xbmc.LOGWARNING)

    @property
    def category_tree(self):
        self.refreshTokenTVN()
        return getRequests(url=self.KATEGORIE, headers=self.HEADERS2, params=self.params())

    def root(self):
        """Get ROOT folder (main menu)."""
        # add_item('17:live', 'TV', ADDON_ICON, 'listcateg', folder=True)
        self.category_list()

    def category_list(self, exlink=None):
        """Get root categories (main menu)."""
        category_tree = self.category_tree
        catimages = {}
        for item in category_tree:
            image = (item.get('images', {}).get('pc') or [{}])[0].get('mainUrl')
            if image:
                catimages[item['slug']] = image
        for item in category_tree:
            if item.get('genres') and item['slug'] not in slug_blacklist:
                cid = item['id']
                slug = item['slug']
                name = item['name']
                image = catimages.get(slug)
                url = '%s:%s' % (cid, slug)
                if slug == 'eurosport':  # special case
                    add_item(url, name, image=image, mode='eurosport', folder=True)
                elif slug in self.categories_without_genres:
                    add_item(':%s' % slug, name, image=image, mode='listcategContent', folder=True, isPlayable=False)
                else:
                    add_item(url, name, image=image, mode='category_genre_list', folder=True)

    def xxx_content(self, exlink=None):
        """Get ROOT content ???"""
        self.refreshTokenTVN()
        data = getRequests('https://player.pl/playerapi/document/menu-category/content',
                           headers=self.HEADERS2, params=self.params())

    def category_genre_list(self, exlink):
        """Get ROOT folder content (main menu)."""
        def load_subfolders(item):
            gid = item['id']
            return self.slug_data('%s:%s' % (gid, slug), maxResults=True if gid else self.MaxMax)

        try:
            cid, slug = exlink.split(':', 1)
            cid = int(cid)
        except ValueError:
            raise ValueError('cannot get integer id in category_genre_list(%r)' % exlink)
        # mylist = self.mylist
        try:
            category = next(cat for cat in self.category_tree if cat['id'] == cid)
        except StopIteration:
            raise ValueError('cennot find category in category_genre_list(%r)' % exlink)
        genres = category['genres']
        with self.count_subfolders(genres, load_subfolders) as count:
            if len(genres) > 1:
                genres.append({'id': '', 'name': self.all_items_title, '_props_': {'SpecialSort': 'top'}})
            for item in genres:
                xbmc.log('PLAYER.PL: category_genre_list: %s: %r' % (type(item), item), xbmc.LOGDEBUG)
                name = item['name']
                url = '%s:%s' % (item['id'], slug)
                name = count.title(item, name)
                # image = media('genre/%s.png' % item['id'], fallback=ADDON_ICON)
                add_item(url, name, image=None, mode='listcategContent', folder=True, isPlayable=False,
                         properties=item.get('_props_'))  # , fallback_image=None)
        setView('genres')
        xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE,
                                 label2Mask="%R, %Y, %P")
        xbmcplugin.endOfDirectory(addon_handle, succeeded=True, cacheToDisc=False)

    def skip_soon_vod_iter(self, lst):
        return (vod for vod in lst if (vod.get('displaySchedules') or [{}])[0].get('type') != 'SOON')

    def eurosport(self, exlink):
        """Home mode for Eurosport. `exlink` is GID:SLUG[:MODE[:ARG]...]"""
        ex = ExLink.new(exlink)
        handler = getattr(self, 'eurosport_%s' % (ex.mode or 'home'), None)
        if handler:
            handler(exlink)

    def eurosport_home(self, exlink):
        ex = ExLink.new(exlink)
        top = {'SpecialSort': 'top'}
        add_item(':%s:schedule' % ex.slug, 'Transmisje sportowe wg daty i godziny', ADDON_ICON,
                 ex.slug, folder=True, fanart=FANART, properties=top)
        add_item(':%s:genre' % ex.slug, 'Transmisje sportowe wg dyscypliny', ADDON_ICON,
                 ex.slug, folder=True, fanart=FANART, properties=top)
        add_item(':%s' % ex.slug, 'Archiwum wszystkich transmisji', ADDON_ICON,
                 "listcategContent", folder=True, fanart=FANART, properties=top)
        data = getRequests3('%s/%s' % (self.SECTIONLIST, ex.slug), headers=self.HEADERS2, params=self.params())
        for item in self.skip_soon_vod_iter(data):
            gid = item['id']
            slug = item['slug']
            try:
                foto = item['images']['pc'][0]['mainUrl']
                foto = 'https:' + foto if foto.startswith('//') else foto
            except Exception:
                foto = ADDON_ICON
            tytul = PLchar(item["title"].capitalize())
            add_item('%s:%s' % (gid, slug), tytul, foto, "listcollectContent", folder=True, fanart=FANART)
        setView('movies')
        # xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE,
        #                          label2Mask="%R, %Y, %P")
        xbmcplugin.endOfDirectory(addon_handle, succeeded=True, cacheToDisc=False)

    def eurosport_schedule(self, exlink):
        ex = ExLink.new(exlink)
        # Wyswietla menu z datami z ostatnich 7 dni (gdy wybrano transmisje wg daty i godziny)
        for i in range(- self.days_ahead, self.days_ago + 1):
            today = datetime.combine(date.today(), datetime.min.time())
            day = today - timedelta(days=i)
            beginTimestamp = int(1000 * time.mktime(day.timetuple()))
            endTimestamp = beginTimestamp + 1000 * 24 * 3600
            name = '%s, %s' % (day.strftime('%Y-%m-%d'), self.week_days[day.weekday()])
            if i == 0:
                name += u'[COLOR gray]   (dzisiaj)[/COLOR]'
            add_item('%s:%s:time:%s:%s' % (ex.gid, ex.slug, beginTimestamp, endTimestamp), name,
                     ADDON_ICON, ex.slug, folder=True, fanart=FANART)
        setView('movies')
        xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.endOfDirectory(addon_handle, succeeded=True, cacheToDisc=False)

    def eurosport_time(self, exlink):
        def hhmm(s):
            return s.partition(' ')[2].rpartition(':')[0]

        ex = ExLink.new(exlink)
        data = self.slug_data('%s:%s' % (ex.gid, ex.slug), maxResults=0, sort='airingSince', params={
            'airingSince': str(ex.beginTimestamp),
            'airingTill': str(ex.endTimestamp)
        })
        myList = self.mylist
        xbmc.log('PLAYER.PL: ++++++ %r' % data, xbmc.LOGWARNING)
        for vod in data['items']:
            # if 1:#( ( 'displaySchedules' in item ) and ( len(item['displaySchedules']) > 0 ) and ( item['displaySchedules'][0]['type'] != 'SOON' ) ):
            #     dod=''
            #     fold = False
            #     playk =True
            #     mud = 'playvid'
            #     if item["payable"]:
            #         if item['id'] not in myList:
            #             dod=' - [I][COLOR khaki](brak w pakiecie)[/COLOR][/I]'
            #             playk =False
            #             mud = '   '
            #     time_str = '[%s-%s]%s' % (hhmm(item['airingSince']), hhmm(item['airingTill']), self.hard_separator)
            #     name = PLchar(time_str, item['title'], dod, sep='')
            #     add_item(str(item['id']), name, ADDON_ICON, mud, folder=fold,isPlayable=playk,fanart=FANART)
            info = {}
            if 'duration' in vod:
                info['duration'] = vod['duration']
            self.add_media_item('playvid', vod['id'], vod=vod, prefix=self.times_prefix(vod), info=info)
        setView('tvshows')
        xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE,
                                 label2Mask="%R, %Y, %P")
        xbmcplugin.endOfDirectory(addon_handle, succeeded=True, cacheToDisc=False)

    def eurosport_genre(self, exlink):
        EUROSPORT_CID = 24  # TODO: remove it !!!
        ex = ExLink.new(exlink)
        data = getRequests3(self.GATUNKI_KATEGORII.format(cid=EUROSPORT_CID), headers=self.HEADERS2, params=self.params())
        for genre in data:
            gid, name = genre['id'], genre['name']
            add_item('%s:%s:list' % (gid, ex.slug), PLchar(name.capitalize()), ADDON_ICON, ex.slug, folder=True,
                     fanart=FANART)
        setView('tvshows')
        xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE,
                                 label2Mask="%R, %Y, %P")
        xbmcplugin.endOfDirectory(addon_handle, succeeded=True, cacheToDisc=False)

    def eurosport_list(self, exlink):
        ex = ExLink.new(exlink)
        data = self.slug_data('%s:%s' % (ex.gid, ex.slug), maxResults=0, sort='airingSince')
        data = data['items']
        if self.hide_soon:
            data = self.skip_soon_vod_iter(data)
        for vod in data:
            info = {}
            if 'duration' in vod:
                info['duration'] = vod['duration']
            self.add_media_item('playvid', vod['id'], vod=vod, prefix=self.datetime_prefix(vod), info=info)
        setView('tvshows')
        # xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.endOfDirectory(addon_handle, succeeded=True, cacheToDisc=False)

    def datetime_prefix(self, vod):
        since = vod.get('since', '--:--')
        since = vod.get('displaySchedules', [{}])[0].get('since', since)
        since = vod.get('airingSince', since)
        return '[%s]%s' % (since.rpartition(':')[0], self.hard_separator)

    def times_prefix(self, vod):
        def hhmm(s):
            return s.partition(' ')[2].rpartition(':')[0]

        since = vod.get('since', '--:--')
        since = vod.get('displaySchedules', [{}])[0].get('since', since)
        since = vod.get('airingSince', since)
        till = vod.get('till', '--:--')
        till = vod.get('displaySchedules', [{}])[0].get('till', till)
        till = vod.get('airingTill', till)
        return '[%s-%s]%s' % (hhmm(since), hhmm(till), self.hard_separator)


def addon_settings(name=None, **kwargs):
    xbmc.log('PLAYER.PL: addon_settings(%r, %r)' % (name, kwargs), xbmc.LOGWARNING)
    if name == 'categories_without_genres':
        Category = namedtuple('Category', 'name slug on')
        playerpl = PLAYERPL()
        categories = [Category(item['name'], item['slug'], item['slug'] in playerpl.categories_without_genres)
                      for item in playerpl.category_tree
                      if item.get('genres') and item['slug'] not in slug_blacklist]
        dialog = xbmcgui.Dialog()
        ret = dialog.multiselect("Kategorie bez podziału na gatunki",
                                 [c.name for c in categories],
                                 preselect=[i for i, c in enumerate(categories) if c.on])
        if ret is not None:
            addon.setSetting('categories_without_genres', ','.join(c.slug for i, c in enumerate(categories)
                                                                   if i in ret))


if __name__ == '__main__':

    exlink = params.get('url')
    mode = params.get('mode')
    name = 'plugin.video.playermb'
    xbmc.log('PLAYER.PL: ENTER: mode=%r, name=%r, exlink=%r' % (mode, name, exlink),
             xbmc.LOGWARNING)

    if not mode:
        home()

    elif mode == "content":
        PLAYERPL().content()

    elif mode == "listcateg":
        PLAYERPL().listCateg(exlink)

    elif mode == "listcategContent":
        PLAYERPL().listCategContent(exlink)

    elif mode == "listcategSerial":
        PLAYERPL().listCategSerial(exlink)

    elif mode == "listEpizody":
        PLAYERPL().listEpizody(exlink)

    elif mode == 'search.it':
        if exlink:
            PLAYERPL().listSearch(exlink)

    elif mode == 'search':
        add_item('', '[COLOR khaki][B]Nowe szukanie[/B][/COLOR]', image=None, mode='search.new',
                 folder=True)
        for entry in historyLoad():
            if entry:
                contextmenu = [
                    (u'Usuń', 'Container.Update(%s)'
                     % build_url({'mode': 'search.remove', 'url': entry})),
                    (u'Usuń całą historię', 'Container.Update(%s)'
                     % build_url({'mode': 'search.remove_all'})),
                ]
                add_item(entry, entry, image=None, mode='search.it', contextmenu=contextmenu,
                         folder=True)
        xbmcplugin.endOfDirectory(addon_handle, succeeded=True, cacheToDisc=False)

    elif mode == 'search.new':
        query = xbmcgui.Dialog().input(u'Szukaj, podaj tytuł filmu', type=xbmcgui.INPUT_ALPHANUM)
        if query:
            historyAdd(query)
            try:
                PLAYERPL().listSearch(query)
            except Exception:
                addon_data.save(indent=2)  # save new search even if exception raised
                raise
    elif mode == 'search.remove':
        historyDel(exlink)
        xbmc.executebuiltin('Container.Refresh(%s)' % build_url({'mode': 'search'}))
        xbmcplugin.endOfDirectory(addon_handle, succeeded=True, cacheToDisc=False)

    elif mode == 'search.remove_all':
        historyClear()
        xbmc.executebuiltin('Container.Refresh(%s)' % build_url({'mode': 'search'}))
        xbmcplugin.endOfDirectory(addon_handle, succeeded=True, cacheToDisc=False)

    elif mode == 'favors':
        PLAYERPL().listFavorites()

    elif mode == "collect":
        PLAYERPL().listCollection()

    elif mode == "listcollectContent":
        PLAYERPL().listCollectContent(exlink)

    elif mode == 'playvid':
        PLAYERPL().playvid(exlink)

    elif mode == 'playm3u':
        PLAYERPL().playvid(params.get('channelid'))

    elif mode == 'buildm3u':
        generate_m3u(override=True)

    elif mode == 'appendm3u':
        generate_m3u(override=False)

    elif mode == 'settings':
        addon_settings(**params)

    elif mode == 'login':
        set_setting('logged', 'true')
        PLAYERPL().LOGGED = addon.getSetting('logged')
        xbmc.executebuiltin('Container.Refresh()')

    elif mode == 'opcje':
        addon.openSettings()
        xbmc.executebuiltin('Container.Refresh()')

    elif mode == 'logout':
        yes = xbmcgui.Dialog().yesno("[COLOR orange]Uwaga[/COLOR]", 'Wylogowanie spowoduje konieczność ponownego wpisania kodu na stronie.[CR]Jesteś pewien?',yeslabel='TAK', nolabel='NIE')
        print(yes)
        if yes:
            set_setting('refresh_token', '')
            set_setting('logged', 'false')
            PLAYERPL().REFRESH_TOKEN = addon.getSetting('refresh_token')
            PLAYERPL().LOGGED = addon.getSetting('logged')
            xbmc.executebuiltin('Container.Refresh()')

    else:
        # auto bind
        playerpl = PLAYERPL()
        if hasattr(playerpl, mode):
            getattr(playerpl, mode)(exlink)

addon_data.save(indent=2)
