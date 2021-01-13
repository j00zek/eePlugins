# -*- coding: utf-8 -*-
import urllib2
import json
import re
from time import localtime, strftime
import urllib
import cookielib
import xbmcgui
import xbmcaddon
import xbmc

addon        = xbmcaddon.Addon()
BRAMKA = 'https://proxiak.eu'
COOKIEFILE = ''
channel_id = '35939513&mime_type=video/mp4'
VIDEO_LINK = 'http://www.tvp.pl/pub/stat/videofileinfo?video_id='
TOKENIZER_URL = 'http://www.tvp.pl/shared/cdn/tokenizer_v2.php?object_id='
SESS_URL= 'http://tvpstream.vod.tvp.pl/sess/tvplayer.php?object_id='
TIMEOUT = 10
UA = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'

ant_lab = ('Wszystkie anteny', 'TVP ABC', 'TVP Info', 'TVP HD', 'TVP 1 HD', 'TVP 2 HD', 'TVP Kultura', 'TVP Historia', 'TVP Rozrywka', 'TVP Seriale', 'TVP ABC', 'TVP Info', 'TVP HD', 'TVP 1 HD', 'TVP 2 HD', 'TVP Kultura', 'TVP Historia', 'TVP Rozrywka', 'TVP Seriale')

ant_val = ('?antena=','?antena=ABC', '?antena=INF', '?antena=KHSH', '?antena=T1D', '?antena=T2D', '?antena=T5D', '?antena=TKH', '?antena=TRO', '?antena=TRS', '?antena=ABC', '?antena=INF', '?antena=KHSH', '?antena=T1D', '?antena=T2D', '?antena=T5D', '?antena=TKH', '?antena=TRO', '?antena=TRS')

def getVideoUrl(url,proxy={},timeout=TIMEOUT):
    if proxy:
        urllib2.install_opener(
            urllib2.build_opener(
                urllib2.ProxyHandler(proxy)
            )
        )
    req = urllib2.Request(url)
    req.add_header('User-Agent', UA)
    try:
        response = urllib2.urlopen(req,timeout=timeout)
        link = response.read()
        response.close()
    except:
        link='{}'
    return link

def getVideoUrl2(url,proxy={},timeout=TIMEOUT,cookiess=None):
	if proxy:
		urllib2.install_opener(
			urllib2.build_opener(
				urllib2.ProxyHandler(proxy)
			)
		)
	req = urllib2.Request(url)
	if cookiess:
		req.add_header('User-Agent', UA)
		req.add_header('Cookie', cookiess)
	else:
		req.add_header('User-Agent', UA)	
	try:
		response = urllib2.urlopen(req,timeout=timeout)
		link = response.read()
		response.close()
	except:
		link='{}'
	return link	
	
	
def getVideoUrlh(url,header={}):
    link='{}'
    global COOKIEFILE
    try:
        if not COOKIEFILE:
            req = urllib2.Request(BRAMKA,data=None,headers={'User-Agent': UA,'Upgrade-Insecure-Requests':1})
            response = urllib2.urlopen(req,timeout=TIMEOUT)
            cookies=response.headers.get('set-cookie',' ').split(' ')[0]
            response.close()
            COOKIEFILE = cookies
        else:
            cookies=COOKIEFILE

        data = 'u=%s&b=221&f=norefer'%urllib.quote_plus(url)
        vurl = BRAMKA+'/includes/process.php?action=update'
        headers={'User-Agent': UA,'Upgrade-Insecure-Requests':1,'Cookie':cookies}
        headers.update(header)
        req = urllib2.Request(vurl,data,headers)
        response = urllib2.urlopen(req,timeout=TIMEOUT)
        link=response.read()

        if 'sslagree' in link:
            vurl = BRAMKA+'/includes/process.php?action=sslagree'
            req = urllib2.Request(vurl,data,headers)
            response = urllib2.urlopen(req,timeout=TIMEOUT)
            link=response.read()
        response.close()
        print 'GATE in USE'
    except:
        print 'GATE in USE ERROR'
        link='{}'
    return link
#def logowanie():
	
def getProxy(url):
    try:
        content ='http://bramka.proxy.net.pl/index.php?q=%s&hl=0'%urllib.quote_plus(url)
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36','Upgrade-Insecure-Requests':1,
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'}
        req = urllib2.Request(content,None,headers)
        response = urllib2.urlopen(req,timeout=TIMEOUT)
        link=response.read()
        response.close()
        print 'GATE2 in USE'
    except:
        print 'GATE in USE ERROR'
        link=''
    return link

def getFormat(link):
    formats = re.compile('({"mimeType":"vide.*?})',re.DOTALL).findall(link)
    out = '{"formats":[%s]}'%','.join(formats) if formats else ''
    return out

def getProxies():
	import requests
	header={'User-Agent': UA}
	content=requests.get('http://www.idcloak.com/proxylist/free-proxy-list-poland.html',headers=header,timeout=30,verify=False).content
	speed = re.compile('<div style="width:\d+%" title="(\d+)%"></div>').findall(content)
	trs = re.compile('<td>(http[s]*)</td><td>(\d+)</td><td>(.*?)</td>',re.DOTALL).findall(content)
	proxies=[{x[0]: '%s:%s'%(x[2],x[1])} for x in trs]
	return proxies

def getProxiesccc():
	import requests
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
		'Connection': 'keep-alive',
		'Referer': 'https://proxyscrape.com/free-proxy-list',
		'Upgrade-Insecure-Requests': '1',
	}
	
	params = (
		('request', 'getproxies'),
		('proxytype', 'http'),
		('timeout', '10000'),
		('country', 'PL'),
		('ssl', 'all'),
		('anonymity', 'all'),
	)
	
	response = requests.get('https://api.proxyscrape.com/', headers=headers, params=params).text
	linie = response.splitlines()
	linie = response.splitlines()
	proxies=['%s'%(x) for x in linie]
	return proxies
	
	
	
def vodTVP_getApiQuery(parent_id,count=10):	
    listing_url = 'http://www.api.v3.tvp.pl/shared/listing.php?dump=json'
    url = listing_url + '&direct=true&count=%d&parent_id=%s'% (count,parent_id)
    response = urllib2.urlopen(url)
    js = json.loads(response.read())
    response.close()
    return js

def getDuration(seconds):
    try:
        seconds=int(seconds)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h>0:
            out = "%d:%02d:%02d" % (h, m, s)
        else:
            out = "%02d:%02d" % (h, m, s)
    except:
        out=''
    return out

def _getPlayable(episode):
    E={}
    E['filename'] = str(episode.get('_id',''))
    if 'video/mp4' in (episode.get('videoFormatMimes') or []):
        E['filename'] = E['filename']+'&mime_type=video/mp4'
    E['fanart'] = vodTVP_getImage(episode,['image_16x9','image'])
    E['img'] = vodTVP_getImage(episode,['image'])
    E['tvshowtitle'] =''
    if episode.get('website_title',None):
        E['tvshowtitle'] =  episode.get('website_title','').encode('utf-8')
    E['title']=''
    if episode.get('website_title',None):
        E['title'] =  episode.get('website_title','').encode('utf-8') + ', '
    E['title'] += episode.get('title','').encode('utf-8')
    E['originaltitle'] = episode.get('original_title','').encode('utf-8')
    E['plot'] =  episode.get('description_root','').encode('utf-8')
    E['aired'] =  episode.get('publication_start_dt','').encode('utf-8')
    release_date = episode.get('release_date','')
    release_date_sec = release_date.get('sec','') if release_date else ''
    E['duration'] = episode.get('duration',0)
   # E['code']=getDuration(E['duration']) if episode.get('duration',0) else ''
    if release_date_sec:
        E['aired'] =  strftime("%d.%m.%Y", localtime(release_date_sec))
        E['code'] =  E['aired']
        E['plot'] += '\n\nPublikacja: %s'%E['aired']
    else:
        E['aired']= '?'
    E['premiered']=E.get('aired','')
    E['plot'] += '\n\n%s'%E.get('originaltitle','') if E.get('originaltitle','') else ''
    return E

def vodTVP_przegapiles(uid = '', dat = '', lab = ''):
    episodes = []
    data = []
    data.append({'data': '', 'label': 'Wszystkie daty' })
    id = ''

    if dat:
        url = 'https://vod.tvp.pl/przegapiles-w-tv'+uid+'&data='+dat
        content = getVideoUrl(url)
        wc = re.compile('<main class="strefa-abo__container strefa-abo__container--main">(.*?)</main>',re.DOTALL).findall(content)

        for pi in wc:
            d_val = dat
            d_lab = lab
            data.append({'data': d_val, 'label': d_lab })
            ids = [(a.start(), a.end()) for a in re.finditer('<div class="strefa-abo__item ', pi,re.IGNORECASE)]
            ids.append( (-1,-1) )

            for i in range(len(ids[:-1])):
                wc = pi[ ids[i][1]:ids[i+1][0] ]
                tid = re.findall('<a href="/video/(.*?)" class="strefa-abo__item-link">',wc)

                if tid:
                    sid = tid[0].split(",")
                    id = sid[2]

                wt = re.compile('<h3 class="strefa-abo__title">(.*?)</h3>',re.DOTALL).findall(wc)
                wo = re.compile('<h4 class="strefa-abo__sub-title">(.*?)</h4>',re.DOTALL).findall(wc)
                imgalt = re.compile('<img src="(.*?)" alt="" class="strefa-abo__img',re.DOTALL).findall(wc)
                imgalt = imgalt[0] if imgalt else ''

                if id and wt:
                    imgalt = 'https:'+imgalt if imgalt.startswith('//') else imgalt
                    title = wt[0].strip()
                    title += ' '+wo[0].strip() if wo else ''
                    episodes.append({'id': id, 'img': imgalt, 'title': title})

    else:
        url = 'https://vod.tvp.pl/przegapiles-w-tv'+uid
        content = getVideoUrl(url)
        wc = re.compile('<section class="aerialsTwo slider-with-tv-stations" data-source-id="">(.*?)</section>',re.DOTALL).findall(content)

        for pi in wc:
            sc = re.findall('<a href="/przegapiles-w-tv\?data=(.*?)">(.*?)<',pi)
            d_val = sc[0][0].split("&")
            d_lab = sc[0][1].strip()
            data.append({'data': d_val[0], 'label': d_lab })
            ids = [(a.start(), a.end()) for a in re.finditer('<div class="item js-metki" data-', pi,re.IGNORECASE)]
            ids.append( (-1,-1) )

            for i in range(len(ids[:-1])):
                wc = pi[ ids[i][1]:ids[i+1][0] ]
                id = re.findall('id="(\d+)"',wc)
                wt = re.compile('<h2 class="">(.*?)</h2>',re.DOTALL).findall(wc)
                wo = re.compile('<h3 class="metki-description metki-description--aerial">(.*?)</h3>',re.DOTALL).findall(wc)
                imgalt = re.compile('data-lazy="(.*?)" alt=',re.DOTALL).findall(wc)
                imgalt = imgalt[0] if imgalt else ''

                if id and wt:
                    imgalt = 'https:'+imgalt if imgalt.startswith('//') else imgalt
                    title = wt[0].strip()
                    title += ' '+wo[0].strip() if wo else ''
                    episodes.append({'id': id[0], 'img': imgalt, 'title': title})

    return (episodes, data)
	
def getRealStream(mo):
	import requests
	locat=requests.get(mo,allow_redirects=False)
	locat=locat.headers['Location']
	return locat

def logowanie():
	username = addon.getSetting('username')
	password = addon.getSetting('password')	
	import requests
	sess=requests.Session()
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
		'Referer': 'https://www.tvp.pl/sess/user-2.0/login.php',
		'Content-Type': 'application/x-www-form-urlencoded',
		'Connection': 'keep-alive',
		'Upgrade-Insecure-Requests': '1',
	}
	data = {
	'action': 'login',
	'ref': 'L3Nlc3MvdXNlci0yLjAvYWNjb3VudC5waHA=',
	'email': username,
	'password': password
	}	

	response = sess.post('https://www.tvp.pl/sess/user-2.0/login.php', headers=headers, data=data,allow_redirects=False)	
	my_cookies = requests.utils.dict_from_cookiejar(response.cookies)
	found = ['%s=%s' % (name, value) for (name, value) in my_cookies.items()]
	kukz= ';'.join(found)	
	html=sess.get('https://www.tvp.pl/sess/user-2.0/account.php').content
	if 'account.php?action=sign-out' in html:
		logged=True
	else:
		logged=False
	headers44 = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
		'Accept': '*/*',
		'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
		'Connection': 'keep-alive',
	}		

	hea= '&'.join(['%s=%s' % (name, value) for (name, value) in headers44.items()])		
	kuk='|'+hea+'&Cookie='+kukz+'|R{SSM}|'
	addon.setSetting('kukhead',kuk)	
	
	return kukz,logged
def vodTVP_GetStreamTokenizer(channel_id='35959537&mime_type=video/mp4',proxy={},timeout=TIMEOUT,bramka=False):
	video_url=''
	content='{}'
	if bramka:
		content=getVideoUrlh(TOKENIZER_URL+ channel_id)
		content=getFormat(content)
		#print ('getUrl_GATE(TOKENIZER_URL+ )',channel_id,content)
		if not content or 'material_niedostepny' in content:
			content = getProxy(TOKENIZER_URL+ channel_id)
			content = getFormat(content)
			if not content or 'material_niedostepny' in content:
				content = getProxy(SESS_URL+ channel_id)
				print('vodTVP_GetStreamTokenizer: getUrl_GATE2',SESS_URL+ channel_id)
				src = re.compile("0:{src:'(.*?)'", re.DOTALL).findall(content)
				wv = re.compile('"widevine":"(https.+?)"', re.DOTALL).findall(content)
				wv = wv[0].replace('\\','') if wv else ''
				if src:
					video_url = src[0]
					if wv: video_url +="|"+wv
					content='{}'
	else:
			
		content=getVideoUrl(TOKENIZER_URL+ channel_id,proxy,timeout)
		if 'material_niedostepny' in content:
			return "http://s.v3.tvp.pl/files/player/video/material_niedostepny.mp4"
		if "NO_PREMIUM_ACCESS" in content:
			usern = addon.getSetting('username')
			passw = addon.getSetting('password')	
			logowac = addon.getSetting('logowanie')
	
			if usern and passw and logowac == 'true':
			#	kukizy,logged=logowanie(usern,passw,TOKENIZER_URL+ channel_id)
				kukizy,logged=logowanie()				
				if logged:
					content=getVideoUrl2(TOKENIZER_URL+ channel_id,proxy,timeout,kukizy)
				else:
					s = xbmcgui.Dialog().ok('[COLOR red]Niepoprawne dane logowania[/COLOR]','Sprawdź wpisane dane.')	
					return ''	
			else:
				s = xbmcgui.Dialog().ok('[COLOR red]Materiał premium[/COLOR]','Wymaga zalogowania.')	
				return ''
		content = getFormat(content)
		if not content:
		
			import time
			SESS_URL2='https://vod.tvp.pl/sess/TVPlayer2/api.php?id='#46058522&@method=getTvpConfig&@callback=__tp2JSONP2477T1580075016675
			cdjs = '&@method=getTvpConfig&@callback=__tp2JSONP2477T'+str(int(time.time()))
			content = getVideoUrl(SESS_URL2+channel_id+cdjs,proxy,timeout)
			src = re.compile("0:{src:'(.*?)'", re.DOTALL).findall(content)
			wv = re.compile('"widevine":"(https.+?)"', re.DOTALL).findall(content)
			wv = wv[0].replace('\\','') if wv else ''
			if src:
				video_url = src[0]
				content='{}'
				if wv: video_url +="|"+wv
				
				

			else:
				content = getVideoUrl(SESS_URL+channel_id,proxy,timeout)
				src = re.compile("0:{src:'(.*?)'", re.DOTALL).findall(content)
				wv = re.compile('"widevine":"(https.+?)"', re.DOTALL).findall(content)
				wv = wv[0].replace('\\','') if wv else ''
				if src:
					video_url = src[0]
					content='{}'
					if wv: video_url +="|"+wv
					
					
	try:
		js = json.loads(content)
	except:
		js={}
	if js.has_key('formats'):
		formats = js.get('formats')
		if isinstance(formats,list):
			video_url=[]
			for one in formats:
				if 'application/vnd.ms-ss' in one.get('mimeType',''):
					continue
				elif '//sdt-thi' in one.get('url','') or '//sdt-epi' in one.get('url',''):
					continue
				totalBitrate =  one.get('totalBitrate','')/100
				quality = 'SD'
				if    2000 < totalBitrate <= 5000  : quality = 'SD'
				elif  5000 < totalBitrate <= 10000 : quality = '720p'
				elif 10000 < totalBitrate <= 20000 : quality = '1080p'
				elif 20000 < totalBitrate <= 30000 : quality = '2K'
				elif totalBitrate >= 30000 : quality = '4K'
				label = 'Bitrate %d Type:'%totalBitrate + one.get('mimeType','').split('/')[-1]
				video_url.append({'title':label,'url':one.get('url',''),'bitrate':totalBitrate})
			video_url = sorted(video_url, key=lambda k: k['bitrate'])
		else:
			if '//sdt-thi' in one.get('url','') or '//sdt-epi' in one.get('url',''):
				video_url=''
			else:
				video_url = formats.get('url','')
	return video_url

def vodTVP_GetStreamUrl(channel_id = '35665108', proxy = {}, timeout = TIMEOUT, pgate = False):
	video_url = vodTVP_GetStreamTokenizer(channel_id, proxy, timeout, pgate)
	if len(video_url) > 0:
		return video_url
	js = json.loads(getVideoUrl(VIDEO_LINK+ channel_id,proxy,timeout))
	if js.has_key('video_url'):
		return js.get('video_url')
	else:
		js = json.loads(getVideoUrl(VIDEO_LINK+ channel_id.split('&')[0],proxy,timeout))
		if js.has_key('copy_of_object_id'):
			channel_id = js.get('copy_of_object_id') + '&mime_type'+ js.get('mime_type','video/mp4')
			video_url = vodTVP_GetStreamTokenizer(channel_id,proxy,timeout)
			return video_url
		elif js.has_key('video_url'):
			return js.get('video_url')
	
	return ''

def vodTVP_getImage(item,img_keys=['image_16x9','image']):
    urlImage = 'http://s.v3.tvp.pl/images/%s/%s/%s/uid_%s_width_%d_gs_0.jpg'
    iconUrl=''
    for key in img_keys:
        if key in item:
            iconFile = item[key][0].get('file_name',None)
            iconWidth = item[key][0].get('width',None)
            if iconFile and iconWidth:
                iconUrl = urlImage %(iconFile[0],iconFile[1],iconFile[2],iconFile[:-4],iconWidth)
            break
    return iconUrl

def vodTVP_root(parent_id='1785454'):
    pout=[
          {'id': 4934948, 'img': '', 'title': 'Programy'},
          {'id': 1649941, 'img': '', 'title': 'Seriale'},
          {'id': 1627183, 'img': '', 'title': 'Filmy Fabularne'},
          {'id': 4190012, 'img': '', 'title': 'Filmy Dokumentalne'},
          {'id': 30904391,'img': '', 'title': 'Dla Dzieci'},
          {'id': 30904461,'img': 'http://s.v3.tvp.pl/images/7/e/8/uid_7e818fc5ed6f1976a960e2e5530430361495531885925_width_800_gs_0.jpg', 'title': 'Informacje'},
          {'id': 4934956,'img': 'http://s.v3.tvp.pl/images/2/4/7/uid_24702a1b5e7aec85d0ef57b51c4163071495540462603_width_800_gs_0.jpg', 'title': 'Publicystyka'},
          {'id': 4190017, 'img': '', 'title': 'Retro'},
          {'id': 6442748, 'img': '', 'title': 'Polecane'} ,
          {'id': 35561705, 'img': '', 'title': 'Rekonstrukcja Filmowa'} ,
        ]
    return pout

def getRegional():
    out=[{'id': 459028,'img': 'http://s.tvp.pl/files/tvpregionalna/newgfx/logo/bialystok.png','title': u'Bia\u0142ystok'},
        {'id': 458968,'img': 'http://s.tvp.pl/files/tvpregionalna/newgfx/logo/bydgoszcz.png','title': u'Bydgoszcz'},
        {'id': 272459,'img': 'http://s.tvp.pl/files/tvpregionalna/newgfx/logo/gdansk.png','title': u'Gda\u0144sk'},
        {'id': 459184,'img': 'http://s.tvp.pl/files/tvpregionalna/newgfx/logo/gorzow.png','title': u'Gorz\xf3w Wlkp.'},
        {'id': 459149,'img': 'http://s.tvp.pl/files/tvpregionalna/newgfx/logo/katowice.png','title': u'Katowice'},
        {'id': 459175,'img': 'http://s.tvp.pl/files/tvpregionalna/newgfx/logo/kielce.png','title': u'Kielce'},
      # {'id': 554276,'img': 'http://s.tvp.pl/files/tvpregionalna/newgfx/logo/krakow.png','title': u'Krak\xf3w'}, #38960924
        {'id': 38960924,'img': 'http://s.tvp.pl/files/tvpregionalna/newgfx/logo/krakow.png','title': u'Krak\xf3w'}, #38960924
        {'id': 459226,'img': 'http://s.tvp.pl/files/tvpregionalna/newgfx/logo/lublin.png','title': u'Lublin'},
        {'id': 459145,'img': 'http://s.tvp.pl/files/tvpregionalna/newgfx/logo/lodz.png','title': u'\u0141\xf3d\u017a'},
        {'id': 623642,'img': 'http://s.tvp.pl/files/tvpregionalna/newgfx/logo/olsztyn.png','title': u'Olsztyn'},
        {'id': 1194632,'img': 'http://s.tvp.pl/files/tvpregionalna/newgfx/logo/opole.png','title': u'Opole'},
        {'id': 459083,'img': 'http://s.tvp.pl/files/tvpregionalna/newgfx/logo/poznan.png','title': u'Pozna\u0144'},
        {'id': 459133,'img': 'http://s.tvp.pl/files/tvpregionalna/newgfx/logo/rzeszow.png','title': u'Rzesz\xf3w'},
        {'id': 1277569,'img': 'http://s.tvp.pl/files/tvpregionalna/newgfx/logo/szczecin.png','title': u'Szczecin'},
        {'id': 459190, 'img': 'http://s.tvp.pl/files/tvpregionalna/newgfx/logo/warszawa.png', 'title': u'Warszawa'},
        {'id': 553964,'img': 'http://s.tvp.pl/files/tvpregionalna/newgfx/logo/wroclaw.png','title': u'Wroc\u0142aw'}]
    return out

def vodTVPapi(parent_id=34932047,js=1,Count=500):
    js=int(js)
    Count=int(Count)
    wc=vodTVP_getApiQuery(parent_id,Count)
    lk=False
    if wc.get('total_count',Count) > Count:
        lk = {'title':'[COLOR gold] >> następne %d / %d >>[/COLOR]'%(Count*js,wc.get('total_count',Count)),'id':parent_id,'page':int(js)+1,'img':''}
        if js>1:
            cnt = Count*js
            wc=vodTVP_getApiQuery(parent_id,cnt)
    items = wc.pop('items')
    lista_katalogow=[]
    lista_pozycji=[]
    if int(js)>1 and len(items) > Count: items = items[(js-1)*Count :]
    lp=False
    if wc.get('found_any'):
        for item in items:
            if len(item.get('videoFormatMimes',[])):
                vi=_getPlayable(item)
                if vi.get('filename',''):
                    lista_pozycji.append(vi)
            elif item.get('playable',False):
                vi=_getPlayable(item)
                if vi.get('filename',''):
                    vi['filename']=str(item.get('asset_id',''))
                    lista_pozycji.append(vi)
            else:	
                title= item.get('title','').encode('utf-8')
                #mid=item.get('_id','') #asset
                mid=item.get('asset_id','') #asset
                if title.lower() == 'wideo' and mid:
                    lp=mid
                    break
                if item['url'].startswith('http'):
                    imgalt= vodTVP_getImage(item,['image','image_4x3'])
                    lista_katalogow.append({'img':imgalt,'title':title,'id':mid})
    if lp:
        (lista_katalogow,lista_pozycji) = vodTVPapi(lp,js,Count)
    if lk:
        lista_katalogow =[lk]
    return (lista_katalogow,lista_pozycji)

def m3u_quality(url):
    out=[url]
    if url and url.endswith('.m3u8'):
        rptxt = re.search('/(\w+)\.m3u8',url)
        rptxt = rptxt.group(1) if rptxt else 'manifest'
        content = getVideoUrl(url)
        content=content.replace('\n','||')
		
        matches=re.compile('RESOLUTION=(.+?)\|\|(.+?m3u8)').findall(content)	
        match=matches[-1][1]
        return match		
   #     #matches=re.compile('RESOLUTION=(.*?)\r\n(QualityLevels\(.*\)/manifest\(format=m3u8-aapl\))').findall(content)
   #     if matches:
   #         out=[{'title':'auto','url':url}]
   #         for title, part in matches:
   #             one={'title':title,'url':url.replace('manifest',part)}
   #             out.append(one)
   # return out
