import e2kodi__init__ # aby zainicjowac sciezki i nie musiec zmieniac czegos w kodzie

import sys,re,os
PY3 = sys.version_info >= (3,0,0)
# For Python 3.0 and later
from urllib.parse import urlencode, parse_qsl
from resources.lib.cmf3 import parseDOM

#import json

import requests
from emukodi import xbmcgui
from emukodi import xbmcplugin
from emukodi import xbmcaddon
from emukodi import xbmc, xbmcvfs

import resolveurl

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon(id='plugin.video.dokumentalnenet')

PATH            = addon.getAddonInfo('path')
try:
    DATAPATH        = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
except:
    DATAPATH        = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')
	
RESOURCES       = PATH+'/resources/'

FANART=RESOURCES+'../fanart.jpg'

exlink = params.get('url', None)
name= params.get('name', None)
page = params.get('page','')
mcount= params.get('moviescount', None)
movie= params.get('movie', None)
rys= params.get('image', None)

main_url='https://dokumentalne.net'

TIMEOUT=15
sess  = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',}

def build_url(query):
    return base_url + '?' + urlencode(query)

def add_item(url, name, image, mode, folder=False, IsPlayable=False, infoLabels=False, movie=True,itemcount=1, page=1,fanart=FANART,moviescount=0):
	list_item = xbmcgui.ListItem(label=name)

	if IsPlayable:
		list_item.setProperty("IsPlayable", 'True')
	if not infoLabels:
		infoLabels={'title': name,'plot':name}
	list_item.setInfo(type="video", infoLabels=infoLabels)	
	if not fanart:
		fanart=FANART
	list_item.setArt({'thumb': image, 'poster': image, 'banner': image, 'fanart': fanart})
	ok=xbmcplugin.addDirectoryItem(
		handle=addon_handle,
		url = build_url({'mode': mode, 'url' : url, 'page' : page, 'moviescount' : moviescount,'movie':movie,'name':name,'image':image}),			
		listitem=list_item,
		isFolder=folder)
	xbmcplugin.addSortMethod(addon_handle, sortMethod=xbmcplugin.SORT_METHOD_NONE, label2Mask = "%R, %P")
	return ok

def home():
	add_item('/najnowsze-filmy/', '[B]Najnowsze[/B]', 'DefaultMovies.png', 'listfilmy', folder=True)
	add_item('/category/hd-filmy/', '[B]Filmy HD[/B]', 'DefaultMovies.png', 'listfilmy', folder=True)
	add_item('/category/wszystkie-filmy/', '[B]Wszystkie[/B]', 'DefaultMovies.png', 'listfilmy', folder=True)
	add_item('', '[B]Kategorie[/B]', 'DefaultRecentlyAddedMovies.png', 'gatunek', folder=True)
	add_item('', '[B][COLOR violet]Szukaj[/COLOR][/B]', 'DefaultAddonsSearch.png', "listSearch", folder=True)
	
def ListFilmy(url,pg):
	pg = int(pg)
	links,pagin  = getFilmy(url,pg)
	if links:
		items = len(links)
		fold=False
		mud='playFilmy'
		for f in links:
			add_item(name=f.get('title'), url=f.get('href'), mode=mud, image=f.get('img'), folder=fold, IsPlayable=True,infoLabels=f, itemcount=items)	
		if pagin:
			for f in pagin:	
				add_item(name=f.get('title'), url=f.get('href'), mode='listfilmy', image=f.get('img'), folder=True,page=f.get('page'))	
		xbmcplugin.endOfDirectory(addon_handle)	
def usun (data):
	#import CommonFunctions
	#common = CommonFunctions
	data = re.sub('<[^<]+?>', '', data)
	#data = common.stripTags(data)
	return data
def getFilmy(url,pg):
	if  'page/' in url:
		url = re.sub(r'\/page/\d+', '/page/%d'%pg,   url)  
	else:
		if '?s=' in url:
			str='/page/%d/'%pg
			url = str+url
		else:
			url = url+'page/%d'%pg
	out=[]
	npout=[]

	
	html = sess.get(main_url+url, headers=headers,verify=False).content
	if PY3:
		html = html.decode(encoding='utf-8', errors='strict')
	try:
		result = parseDOM(html, 'div', attrs={'class':'body-content'})[0]
	except:
		result = html
	links = parseDOM(result, 'div', attrs={'class':'entry-content'})

	for link in links:
		href = parseDOM(link,'a',ret='href')[0]
		img = parseDOM(link,'img',ret='src')
		img = img [0] if img else ''
		tyt = parseDOM(link,'a',ret='title')[0]
		opis = parseDOM(link, 'div', attrs={'class':'excerpt sub-lineheight'})
		opis = usun(opis[0]) if opis else tyt
		out.append({'title':PLchar(tyt),'href':PLchar(href),'img':PLchar(img),'plot':PLchar(opis)})
	if 'class="nextpostslink"' in html: 
		npout.append({'title':'Następna strona','href':url,'img':RESOURCES+'nextpage.png','plot':'','page':pg+1}) 
	return out,npout
def PlayFilmy(url):
	html = sess.get(url, headers=headers,verify=False).content
	if PY3:
		html = html.decode(encoding='utf-8', errors='strict')
	player = parseDOM(html, 'div', attrs={'id':'player-embed'})[0]
	src = parseDOM(player,'iframe',ret='src')

	if src:
		src = 'https:'+src[0] if src[0].startswith('//') else src[0]
		try:
			stream_url = resolveurl.resolve(src)
		except:
			stream_url=''
		if stream_url:
			xbmcplugin.setResolvedUrl(addon_handle, True, xbmcgui.ListItem(path=stream_url))
		else:
			xbmcgui.Dialog().notification('[B]Błąd[/B]', 'Brak linku.',xbmcgui.NOTIFICATION_INFO, 8000,False)	
	else:
		xbmcgui.Dialog().notification('[B]Błąd[/B]', 'Brak linku.',xbmcgui.NOTIFICATION_INFO, 8000,False)	

def ListSearch():
	d = xbmcgui.Dialog().input(u'Szukaj...', type=xbmcgui.INPUT_ALPHANUM)
	if d:
		href = '?s='+d
		ListFilmy(href,1)

def PLchar(char):
	if type(char) is not str:
		char = char if PY3 else char.encode('utf-8')
		#char=char.encode('utf-8')
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
	char = char.replace('&#8222;','"').replace('&#8221;','"').replace('&#8220;','"')
	char = char.replace('[&hellip;]',"...")
	char = char.replace('&#038;',"&")	
	char = char.replace('&#039;',"'")
	char = char.replace('&quot;','"').replace('&oacute;','ó').replace('&rsquo;',"'")
	char = char.replace('&nbsp;',".").replace('&amp;','&').replace('&eacute;','e')
	
	return char	
	
def getGatunek():
	out=[]
	html = sess.get(main_url, headers=headers,verify=False).content
	if PY3:
		html = html.decode(encoding='utf-8', errors='strict')
	cc=re.findall('<a href="https://dokumentalne.net([^"]+)" title="([^"]+)">.+?</a>.+?<span class="tt-number">(.+?)</span>',html,re.DOTALL)
	for href,dane,il in cc:
		nazw = '%s %s'%(dane,il)
		out.append((nazw, href))
	return out
	
def router(paramstring):
	params = dict(parse_qsl(paramstring))
	
	if params:
		mode = params.get('mode', None)
		
		if mode == 'listfilmy':
			ListFilmy(exlink,page)	

		elif mode == 'playFilmy':	
			PlayFilmy(exlink)
			
		elif mode == 'gatunek':

			data = getGatunek()
			if data:
				label = [x[0].strip() for x in data]
				url = [x[1].strip() for x in data]
				sel = xbmcgui.Dialog().select('Wybierz kategorię',label)
				if sel>-1:
					ListFilmy(url[sel],1)	

		elif mode == 'listSearch':
			ListSearch()			

	else:
		home()
		xbmcplugin.endOfDirectory(addon_handle)	
if __name__ == '__main__':
    router(sys.argv[2][1:])
