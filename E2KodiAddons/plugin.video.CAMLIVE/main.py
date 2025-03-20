# -*- coding: UTF-8 -*-
import sys
import urllib

try:
    import urllib.parse as urllib
except:
    pass

from emukodi import xbmc
from emukodi import xbmcgui
from emukodi import xbmcplugin
import re
import requests
import codecs
import dom_parser

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

s = requests.Session()

def parseDOM(html, name='', attrs=None, ret=False):
    if attrs:
        attrs = dict((key, re.compile(value + ('$' if value else ''))) for key, value in attrs.items())
    results = dom_parser.parse_dom(html, name, attrs, ret)
    if ret:
        results = [result.attrs[ret.lower()] for result in results]
    else:
        results = [result.content for result in results]
    return results

def CATEGORIES():
    addDir('Plaża i morze', 'https://www.webcamera.pl/kategoria,plaze-i-morze', 3, 'search.jpg', '', True)
    addDir('Miasta', 'https://www.webcamera.pl/kategoria,miasta', 3, 'search.jpg', '', True)
    addDir('Stacje Narciarskie', 'https://www.webcamera.pl/kategoria,stacje-narciarskie', 3, 'search.jpg', '', True)
    addDir('Inne', 'https://www.webcamera.pl/kategoria,inne', 3, 'search.jpg', '', True)


def addDir(name, url, mode, iconimage, thumb, isFolder=True, total=1):
    u = sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode) + '&name=' + urllib.quote_plus(name)
    liz = xbmcgui.ListItem(name)
    url = thumb
    liz.setArt({
        'thumb': iconimage,
        'icon': 'DefaultFolder.png',
        'fanart': url})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder, totalItems=total)
    return ok


def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if params[len(params) - 1] == '/':
            pass
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param


params = get_params()
url = None
name = None
mode = None
iconimage = None

try:
    url = urllib.unquote_plus(params['url'])
except:
    pass
try:
    name = urllib.unquote_plus(params['name'])
except:
    pass
try:
    mode = int(params['mode'])
except:
    pass
try:
    iconimage = urllib.unquote_plus(params['iconimage'])
except:
    pass

if mode == 3:
    url = urllib.unquote_plus(params['url'])
    response = s.get(url, verify=False)
    response.encoding = 'utf-8'
    content = response.text
    result = parseDOM(content, 'div', {
        'id': 'inline-camera-listing'})
    tytuly = parseDOM(result, 'a', ret='title')
    zdjecia = parseDOM(result, 'source', ret='data-srcset')
    linki = parseDOM(result, 'a', ret='href')
    for id in range(0, len(linki)):
        try:
            tytul = tytuly[id].replace("Przejdź do kamery ", "").replace("NOWOŚĆ", "").replace("Nowość", "")
            link = linki[id]
            test = link[8::].split('.')[0]
            try:
                zdjecie = [x for x in zdjecia if link[8::].split('.')[0] in x][0]
            except:
                zdjecie = ''
            tytul2 = re.findall(r"//(.*?)\.", link)[0].replace("-", " ")
            addDir(str(tytul2).title(), str(link), 10, str(zdjecie), str(zdjecie), isFolder=False)
        except:
            continue

if mode == None or url == None or len(url) < 1:
    CATEGORIES()

elif mode == 10:
    hdr = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'}
    url = urllib.unquote_plus(params['url'])
    response = s.get(url, headers=hdr, verify=False)
    response.encoding = 'utf-8'
    content = response.text
    linki = parseDOM(content, 'link', ret='href')
    link = ''
    for item in linki:
        if 'player' in item and 'html' in item:
            link = item
    response = s.get(linki[0], headers=hdr, verify=False)
    response.encoding = 'utf-8'
    content = response.text
    video_link = re.findall(r'video_src\":\"(.*?)\"', content)[0].replace("\\", "")
    enc = codecs.getencoder("rot-13")
    video_link = enc(video_link)[0]
    xbmc.Player().play(str(video_link))

xbmcplugin.setContent(int(sys.argv[1]), 'movies')
xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_TITLE)
xbmcplugin.endOfDirectory(int(sys.argv[1]))


