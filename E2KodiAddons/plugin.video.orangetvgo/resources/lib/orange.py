# coding: UTF-8
import ast
import sys, re

import requests
import routing
from emukodi import xbmc
from emukodi import xbmcvfs
from .helper import Helper
from .encryption import generate_encoded_pin
from urllib.parse import parse_qsl

base_url = sys.argv[0]
handle = int(sys.argv[1])
helper = Helper(base_url, handle)
plugin = routing.Plugin()

try:
    # Python 3
    from urllib.parse import quote_plus, unquote_plus, quote, unquote,parse_qsl
    to_unicode = str
except:
    # Python 2.7
    from urllib import quote_plus, unquote_plus, quote, unquote
    from urlparse import parse_qsl
    to_unicode = unicode

from datetime import datetime, timedelta
import time
import json    
    
@plugin.route('/')
def root():
    dod, logged = loguj()
    if not logged:

        helper.add_item('[COLOR lightgreen][B]Zaloguj[/COLOR][/B]', plugin.url_for(loguj),folder=False)
        helper.add_item('[COLOR lightgreen][B]Dane logowania[/COLOR][/B]', plugin.url_for(ustawienia),folder=False)
    else:
        helper.add_item('Zalogowany jako: '+dod, plugin.url_for(empty), info={'plot':dod},folder=False)
        helper.add_item('Telewizja', plugin.url_for(listtv),folder=True)
        helper.add_item('VOD', plugin.url_for(listvodcat),folder=True)

    helper.eod()
    
@plugin.route('/empty/')
def empty():
    return
    
@plugin.route('/resetSession/<id>')
def resetSession(id):
    headers = {
        'Host': helper.host,
        'User-Agent': helper.UA,
        'Accept': 'application/vnd.orangeott.v1+json',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Content-Type': 'application/vnd.orangeott.v1+json',
        'X-Country-Code': 'pl',
        'Origin': 'https://tvgo.orange.pl',
        'DNT': '1',
        'Referer': 'https://tvgo.orange.pl/live/stream/{}'.format(id),
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }
    headers.update(helper.extra_hea())
    jsdata = helper.request_sess((helper.chan_session_url).format(id), 'delete', headers=headers,result=False)
    return 


def getEpgs():

    import calendar
    dzis=helper.timeNow(sek=True)
    dzis2=helper.timeNow(sek=False)
    timestampdzis = calendar.timegm(dzis.timetuple())
    timestampdzis2 = calendar.timegm(dzis2.timetuple())
    try:
        del helper.headers['Content-Type']
    except:
        pass
    helper.headers.update({'Accept': 'application/vnd.orangeott.v3+json'})
    helper.headers.update(helper.extra_hea())
    url = helper.api_url.format('epg/epg?hhTech=&deviceCat=otg&chosen-day='+str(timestampdzis2))
    jsdata = helper.request_sess(url, 'get', headers=helper.headers,result=False)

    return jsdata, timestampdzis
try:

    epg, tstamp = getEpgs()
except:
    epg = ''
    tstamp =''
    
def getPlot(id):

    plot=''
    for epgx in ((epg).json()).get("epg", None):
        if id in epgx.get("channelExternalId", None):

            pokolei = sorted((epgx.get('schedule', None)), key=lambda items: items['startDate'])
            for sch in epgx.get('schedule', None):
                endDate = sch.get('endDate', None)
                if int(tstamp)<endDate:
                    
                    endDate = datetime.fromtimestamp(endDate).strftime('%H:%M')
                    startDate = datetime.fromtimestamp(sch.get('startDate', None)).strftime('%H:%M') 
                    pr =  sch.get('name', None)
                    plot+= '[COLOR khaki]%s - %s[/COLOR] : %s [CR]'%(startDate, endDate, pr)
    return plot    
    
    
    
    
@plugin.route('/listtv')    
def listtv():
    try:
        del helper.headers['Content-Type']
    except:
        pass
    
    helper.headers.update({'Accept': 'application/vnd.orangeott.v4+json','Expires':'0','Referer':'https://tvgo.orange.pl/channels'})
    helper.headers.update(helper.extra_hea())
    jsdata = helper.request_sess(helper.api_url.format('live/channel-list?hhTech=ftth&deviceCat=otg'), 'get', headers=helper.headers, json=True)#hhTech=iptv
    
    channelList = jsdata.get("channelList",None)
    for ch in channelList:
        id = ch.get("channelExtId",None)
        title = ch.get("name",None)
        img = ch.get("logoSignature",None)
        img = helper.api_url.format('resource/image/')+img
    
        plot = getPlot(id)
        
        
        isSubscribed = ch.get("isSubscribed",None)
        if not isSubscribed:
            continue
        keczup = ch.get("playFeatures",None).get("otg",None).get("isCatchUp",None)
        dod = ' [COLOR gold](+)[/COLOR]' if keczup else ''
        HOME=ch.get('isHomeZoneRestricted',None)
        dod1=' [COLOR khaki][HOME][/COLOR]' if HOME else ''
        tytul = title+dod+dod1

        mod = plugin.url_for(playtv, id)
        fold = False
        ispla = True
        if keczup:

            mod = plugin.url_for(listkeczup, id)
            fold = True
            ispla = False

        info = {'title': tytul, 'plot':plot}
        art = {'icon': img, 'fanart': helper.addon.getAddonInfo('fanart')}
        helper.add_item(tytul, mod, playable=ispla, info=info, art=art)  

    if channelList:
        helper.eod()
        
        
        
def CreateBlad2(id):

    headers = {
        'Host': helper.host,
        'User-Agent': helper.UA,
        'Accept': 'application/vnd.orangeott.v1+json',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Content-Type': 'application/vnd.orangeott.v1+json',
        'X-Country-Code': 'pl',
        'Origin': 'https://tvgo.orange.pl',
        'DNT': '1',
        'Referer': 'https://tvgo.orange.pl/live/stream/{}'.format(id),
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'OtvDeviceInfo2': helper.OtvDeviceInfo2,
    }
    
    headers.update(helper.extra_hea())
    jsdata = helper.request_sess((helper.chan_session_url).format(id), 'delete', headers=headers, result=False)

    acx=jsdata.text
    helper.sleep(3000)    
    if 'erminal is not registered' in jsdata.text:
        headers = {
            'Host': helper.host,
            'User-Agent': helper.UA,
            'Accept': 'application/vnd.orangeott.v3+json',
            'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
            'Content-Type': 'application/vnd.orangeott.v1+json',
            'OtvDeviceInfo2': helper.OtvDeviceInfo2,
            'X-Country-Code': 'pl',
            'Origin': 'https://tvgo.orange.pl',
            'DNT': '1',
            'Referer': 'https://tvgo.orange.pl/live/stream/{}'.format(id),
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',}
        headers.update(helper.extra_hea())
        data = {"name":"FIREFOX","serialNumber":"FIREFOX_WEB_TERMINAL_1"+helper.householdExtId,"deviceType":"web_otf","deviceManufacture":"web","deviceModel":"web"}
        
        jsdata = helper.request_sess('https://tvgo.orange.pl/gpapi/user/terminals', 'post', data=data, headers=headers, result=False, json_data = True)
        avb=jsdata.text

        if jsdata.status_code == 201:
            helper.save_file(file=helper.datapath+'kukis', data=(helper._sess.cookies).get_dict(), isJSON=True) 
            url = (helper.chan_url).format(id)
            if '|' in id:
                id,subid = id.split('|')
                url = ('https://tvgo.orange.pl/gpapi/live/channel/{0}/{1}/catchup?deviceCat=otg').format(id,subid)
                
                
            headers = {
                'Host': helper.host,
                'User-Agent': helper.UA,
                'Accept': 'application/vnd.orangeott.v2+json',
                'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
                'OtvDeviceInfo2': helper.OtvDeviceInfo2,
                'X-Country-Code': 'pl',
                'DNT': '1',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',}
            helper.sleep(3000)            
            headers.update(helper.extra_hea())
            jsdata = helper.request_sess(url, 'get', headers=headers,result=False)

            
            
            helper.save_file(file=helper.datapath+'kukis', data=(helper._sess.cookies).get_dict(), isJSON=True) 
    else:
        url = (helper.chan_url).format(id)
        if '|' in id:
            id,subid = id.split('|')
            url = ('https://tvgo.orange.pl/gpapi/live/channel/{0}/{1}/catchup?deviceCat=otg').format(id,subid)
            
            
        headers = {
            'Host': helper.host,
            'User-Agent': helper.UA,
            'Accept': 'application/vnd.orangeott.v2+json',
            'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
            'OtvDeviceInfo2': helper.OtvDeviceInfo2,
            'X-Country-Code': 'pl',
            'DNT': '1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',}
    
        headers.update(helper.extra_hea())
        jsdata = helper.request_sess(url, 'get', headers=headers,result=False)
        helper.save_file(file=helper.datapath+'kukis', data=(helper._sess.cookies).get_dict(), isJSON=True) 

    if jsdata.status_code == 401:
        headers = {
            'Host': helper.host,
            'User-Agent': helper.UA,
            'Accept': 'application/vnd.orangeott.v3+json',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
            'Content-Type': 'application/vnd.orangeott.v1+json',
            'OtvDeviceInfo2': helper.OtvDeviceInfo2,
            'X-Country-Code': 'pl',
            'Origin': 'https://tvgo.orange.pl',
            'Referer':  'https://tvgo.orange.pl/live/stream/{}'.format(id),
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }
            
            
        headers.update(helper.extra_hea())
        
        data = {"name":"FIREFOX","serialNumber":"FIREFOX_WEB_TERMINAL_1"+helper.householdExtId,"deviceType":"web_otf","deviceManufacture":"web","deviceModel":"web"}
        jsdata = helper.request_sess('https://tvgo.orange.pl/gpapi/user/terminals', 'post', data=data, headers=headers,result=False, json_data = True)
        helper.save_file(file=helper.datapath+'kukis', data=(helper._sess.cookies).get_dict(), isJSON=True)

    try:
        ab = jsdata.json()
    except:
        ab =jsdata.text
    return ab
    

    
@plugin.route('/listkeczup/<id>')    
def listkeczup(id):    

    program = xbmc.getInfoLabel("ListItem.Title")
    if program:
        helper.set_setting('program', str(program))
    else:
        program = helper.get_setting('program')
    program = program.replace('(+)','(na żywo)')

    img = xbmc.getInfoLabel("ListItem.Icon")    
    if img:
        helper.set_setting('img', str(img))
    else:
        img = helper.get_setting('img')
    plot = getPlot(id)

    mod = plugin.url_for(playtv, id)

    ispla = True

    info = {'title': program, 'plot':plot}
    art = {'icon': img, 'fanart': helper.addon.getAddonInfo('fanart')}
    helper.add_item(program, mod, playable=ispla, info=info, art=art)  
    
    
    
    out = helper.CreateDays()
    for x in out:
        uid = id+'|'+str(x.get('tstamp',None))
        mod = plugin.url_for(listekczup2, uid)

        ispla = False
        info = {'title': x.get('dzien',None), 'plot':x.get('dzien',None)}
        art = {'icon': img, 'fanart': helper.addon.getAddonInfo('fanart')}
        helper.add_item(x.get('dzien',None), mod, playable=ispla, info=info, art=art)  
    helper.eod()        

@plugin.route('/listekczup2/<idts>')    
def listekczup2(idts):

    try:
        del helper.headers['Content-Type']
    except:
        pass
    id,tstampx = idts.split('|')
    helper.headers.update({'Accept': 'application/vnd.orangeott.v3+json'})
    helper.headers.update(helper.extra_hea())
    url = helper.api_url.format('epg/epg?hhTech=&deviceCat=otg&chosen-day='+str(tstampx))
    jsdata = helper.request_sess(url, 'get', headers=helper.headers,result=False)

    for epgx in (jsdata.json()).get("epg",None):
        if id in epgx.get("channelExternalId",None):

            schedules = epgx.get('schedule', None)
            for sch in schedules:
                if not 'isCatchUpDisabled' in sch:
                    startDate = sch.get("startDate", None)
                    endDate = sch.get("endDate", None)

                    imagePath = sch.get("imagePath", None)
                    poster = helper.main_url+imagePath if imagePath else ''
                    name = sch.get("name", None)
                    referenceProgramId = sch.get("referenceProgramId", None)
                    if int(tstamp)>sch.get("startDate", None):
                        czasod = datetime.fromtimestamp(sch.get("startDate", None)).strftime('%H:%M')
                        czasdo = datetime.fromtimestamp(sch.get("endDate", None)).strftime('%H:%M')
                        uid = id+'|'+referenceProgramId
                        tit = '[COLOR khaki]%s - %s[/COLOR] %s'%(czasod, czasdo, name)
                        
                        
                        mod = plugin.url_for(playtv, uid)
                        ispla = True
                        info = {'title': tit, 'plot':tit}
                        art = {'icon': poster, 'fanart': helper.addon.getAddonInfo('fanart')}
                        helper.add_item(tit, mod, playable=ispla, info=info, art=art)  
    helper.eod()

@plugin.route('/playtv/<id>')    
def playtv(id):

    jsdata = CreateBlad2(id)

    if not 'errCode' in jsdata:
        casToken = jsdata.get('casToken',None)
        streamUrl = jsdata.get('streamUrl',None) 
    
        license_url = 'https://tvgo.orange.pl/RTEFacade_RIGHTV/widevinedrm?token='+quote(casToken)
        mpdurl = streamUrl.split('&maxrate=')[0].replace('bpk-service=LIVE&','').replace('bpk-service=CUP&','')#streamUrl.split('?bpk-ser')[0]
        
        #catchup SC
        params = dict(parse_qsl(sys.argv[2][1:]))
        if 'ts' in params and 'te' in params:
            ts=datetime(*(time.strptime(params['ts'], "%Y-%m-%d %H:%M:%S")[0:6])).timestamp()
            te=datetime(*(time.strptime(params['te'], "%Y-%m-%d %H:%M:%S")[0:6])).timestamp()
                   
            mpdurl+='&begin=%s&end=%s'%(str(int(ts)),str(int(te)))
        
        PROTOCOL = 'mpd'
        DRM = 'com.widevine.alpha'
        cookies = helper.cookies_string(helper.kukis)
    
        proxyport = helper.get_setting('proxyport')
        dt='User-agent='+quote(helper.UA)+"&Cookie="+cookies
    
        lic_url = license_url+'|'+dt+'|R{SSM}|'
        proxy_lic='http://127.0.0.1:%s/licensetv='%(proxyport)+lic_url

        subs=[]
        helper.PlayVid(mpdurl, lic_url, PROTOCOL, DRM, flags=False, subs = subs)
    else:
        helper.notification('[B]Uwaga[/B]', '[B]'+jsdata.get('errMsg',None)+'[/B]') 


@plugin.route('/listvodcat')    
def listvodcat():

    mod = plugin.url_for(listvodsubcat, quote_plus('https://tvgo.orange.pl/gpapi/vod/movie-dir-list?deviceCat=otg'))

    ispla = False
    info = {'title': 'Podkategorie', 'plot':'Podkategorie'}
    art = {'icon': helper.addon.getAddonInfo('icon'), 'fanart': helper.addon.getAddonInfo('fanart')}
    helper.add_item('Podkategorie', mod, playable=ispla, info=info, art=art)  

    try:
        del helper.headers['Content-Type']
    except:
        pass

    helper.headers.update({'Accept': 'application/vnd.orangeott.v3+json'})
    helper.headers.update(helper.extra_hea())
    jsdata = helper.request_sess(helper.api_url.format('vod/root-content?deviceCat=otg'), 'get', headers=helper.headers, json=True, result=True)

    voddirlists = jsdata.get('vodDirList', None)
    for vlist in voddirlists:
        externalId = vlist.get("externalId", None)
        title = vlist.get("name", None)

        mod = plugin.url_for(listcontent, str(externalId))

        ispla = False
        info = {'title': title, 'plot':title}
        art = {'icon': helper.addon.getAddonInfo('icon'), 'fanart': helper.addon.getAddonInfo('fanart')}
        helper.add_item(title, mod, playable=ispla, info=info, art=art) 

    helper.headers.update({'Accept': 'application/vnd.orangeott.v2+json',"Cache-Control": "no-cache","Pragma": "no-cache"})
    helper.headers.update(helper.extra_hea())                 
    jsdata = helper.request_sess(helper.api_url.format('vod/packages?deviceCat=otg'), 'get', headers=helper.headers, json=True, result=True)

    packages = jsdata.get('packages', None)
    out=[]
    for pkg in packages:
        definition = pkg.get('definition', None)
        title = pkg.get('name', None)
        coverImagePath = pkg.get('coverImagePath', None)
        poster = helper.main_url+coverImagePath
        externalId = pkg.get('externalId', None)
        
        packageType = pkg.get('packageType', None)
        
        serviceName = pkg.get('serviceName', None)
        
        desc = pkg.get('desc', None)
        uid = "{}|{}|{}".format(externalId, packageType, serviceName)
        if packageType == 'SVOD':
            mod = plugin.url_for(listcontent, str(uid))

            ispla = False
            info = {'title': title, 'plot':title}
            art = {'icon': poster, 'fanart': helper.addon.getAddonInfo('fanart')}
            helper.add_item(title, mod, playable=ispla, info=info, art=art) 

        else:
            out.append({"title": title, 'url':str(uid), 'image':poster, 'plot': desc})
    for x in out:
    
        mod = plugin.url_for(listcontent, str(x.get("url",None)))

        ispla = False
        info = {'title': x.get("title",None), 'plot':x.get("plot",None)}
        art = {'icon': x.get("image",None), 'fanart': helper.addon.getAddonInfo('fanart')}
        helper.add_item(x.get("title",None), mod, playable=ispla, info=info, art=art) 

    if voddirlists or packages:
    
        helper.eod()
        
        
        
@plugin.route('/listcontent/<idt>')
def listcontent(idt):
    try:
        del helper.headers['Content-Type']
    except:
        pass
    
    if '|' in idt:
        id,tt,xx = idt.split('|')
    else:
        id = idt
    helper.headers.update({'Accept': 'application/vnd.orangeott.v3+json'})
    helper.headers.update(helper.extra_hea())
    url = helper.api_url.format('vod/dir/')+str(id)+'?deviceCat=otg'
    jsdata = helper.request_sess(url, 'get', headers=helper.headers, json=True, result=True)

    vodDirList = jsdata.get('vodDirList', None)
    vodList = jsdata.get('vodList', None)
    if vodDirList:
        for vodR in vodDirList:
            title = vodR.get('name', None)
            vodListx = vodR.get('vodList', None)
            poster =''
            if vodListx:
                poster = vodListx[0].get('bannerImage', None)
                description = vodListx[0].get('description', None)
                uid = quote(json.dumps(vodListx))
                
                mod = plugin.url_for(listsubdir, str(uid))

                ispla = False
                info = {'title': title, 'plot':description}
                art = {'icon': poster, 'fanart': helper.addon.getAddonInfo('fanart')}
                helper.add_item(title, mod, playable=ispla, info=info, art=art) 

    elif vodList:
        CreateVodList(vodList)
    if vodList or vodDirList:
        helper.setContent('videos')    
        helper.eod()    

def CreateVodList(vodList):
    for vodL in vodList:
        assetExternalId = vodL.get('assetExternalId', None)
        genres = vodL.get('genres', None)
        kateg = ','.join([x.strip() for x in genres]) if genres else ''
        description = vodL.get('description', None)
        description = description if description else ''
        title = vodL.get('name', None) 
        year = vodL.get('year', None) 
        duration = vodL.get('duration', None) 
        duration = int (duration)/1000 if duration else '0'
        coverImagePath = vodL.get('coverImageVerticalPath', None) 
        poster = helper.main_url+coverImagePath

        videoId =  ''
        packageType =  ''
        externalId =  ''
        parentVodPackageId =  ''
        versions = vodL.get('versions', None) 
        trailer = vodL.get('trailer', None) 
        
        
        
        if versions:
            videoId =  versions[0].get('videoId', None)
            packageType =  versions[0].get('packageType', None)
            externalId =  versions[0].get('externalId', None)
            parentVodPackageId =  versions[0].get('parentVodPackageId', None)

        uid = "{}|{}|{}".format(assetExternalId, videoId, externalId)
    
        mod = plugin.url_for(playvid, str(uid))

        ispla = True
        info = {'title': '[COLOR gold]'+title+'[/COLOR]', 'plot': description, 'year': year, 'genre': kateg, 'duration': int(duration)}
        art = {'icon': poster, 'fanart': helper.addon.getAddonInfo('fanart')}
        helper.add_item('[COLOR gold]'+title+'[/COLOR]', mod, playable=ispla, info=info, art=art) 
        if trailer:

            title2 = "     -[COLOR lightgreen][I]"+ title + ' (trailer)[/COLOR][/I]'
            uid2 = helper.api_url.format('vod/video/trailer/')+str(assetExternalId)+'?device-type=web_otf&auto-buy=false&deviceCat=otg' 
            
            mod = plugin.url_for(playvid, quote_plus(str(uid2)))

            ispla = True
            info = {'title': title2, 'plot': description, 'year': year, 'genre': kateg, 'duration': int(duration)}
            art = {'icon': poster, 'fanart': helper.addon.getAddonInfo('fanart')}
            helper.add_item(title2, mod, playable=ispla, info=info, art=art) 

    return
@plugin.route('/playvid/<id>')    
def playvid(id):
    id = unquote_plus(id)
    try:
        del self.headers['Content-Type']
    except:
        pass
    
    if 'http' in id:
        del helper.headers['Accept']

        helper.headers.update({"Cache-Control": "no-cache","Pragma": "no-cache"})
        helper.headers.update(helper.extra_hea())
        mpdurl = id
        jsdata = helper.request_sess(mpdurl, 'get', headers=helper.headers, json=True, result=True)

    else:
        helper.headers.update({'Accept': 'application/vnd.orangeott.v2+json'})
        
        hd = {
        'User-Agent': helper.UA,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Connection': 'keep-alive'}
        hd.update(helper.extra_hea())
        x,x1,id = id.split('|')
        mpdurl = helper.api_url.format('vod/play-info/')+id+'?device-type=web_otf&auto-buy=false&deviceCat=otg'

        jsdata = helper.request_sess(mpdurl, 'get', headers=hd, json=True, result=True)

    if 'errCode' in jsdata:
        if 'not registered' in (jsdata.get('errMsg', None)).lower():
            CreateTerminal()
            try:
                del helper.headers['Content-Type']
            except:
                pass
            jsdata = helper.request_sess(mpdurl, 'get', headers=hd, json=True, result=True)    
            if 'no valid ticket' in (jsdata.get('errMsg', None)).lower():
                helper.notification('[B]Uwaga[/B]', '[B]Brak dostępu do materiału[/B]')

                sys.exit(0)

        elif 'no valid ticket' in (jsdata.get('errMsg', None)).lower():
            helper.notification('[B]Uwaga[/B]', '[B]Brak dostępu do materiału[/B]')

            sys.exit(0)
            
    mpdurl = jsdata.get('url', None) 
    lic_url=''
    DRM= ''
    
    if 'playReadyToken' in jsdata:
        casToken = jsdata.get('playReadyToken')
    
        license_url ='https://tvgo.orange.pl/RTEFacade_RIGHTV/widevinedrm?token='+quote(casToken)
        DRM = 'com.widevine.alpha'
        lic_url = license_url+'|Content-Type=|R{SSM}|'
    subs =[]
    PROTOCOL='mpd'
    helper.PlayVid(mpdurl, lic_url, PROTOCOL, DRM, flags=False, subs = subs)

def CreateTerminal():
    helper.headers.update({'Accept': 'application/vnd.orangeott.v3+json', 'Content-Type': 'application/vnd.orangeott.v1+json'})
    helper.headers.update(helper.extra_hea())
    data = {"name":"FIREFOX","serialNumber":"FIREFOX_WEB_TERMINAL_1"+helper.householdExtId,"deviceType":"web_otf","deviceManufacture":"web","deviceModel":"web"}
    jsdata = helper.request_sess('https://tvgo.orange.pl/gpapi/user/terminals', 'post', data=data, headers=helper.headers, result=False, json_data = True)
    helper.save_file(file=helper.datapath+'kukis', data=(helper._sess.cookies).get_dict(), isJSON=True) 
    return


@plugin.route('/listsubdir/<url>')    
def listsubdir(jsdata):

    vods = json.loads(unquote(jsdata))
    CreateVodList(vods)
    return
@plugin.route('/listvodsubcat/<url>')    
def listvodsubcat(url):
    url = unquote_plus(url)
    
    try:
        del helper.headers['Content-Type']
    except:
        pass
    helper.headers.update({'Accept': 'application/vnd.orangeott.v3+json'})
    helper.headers.update(helper.extra_hea())
    jsdata = helper.request_sess(url, 'get', headers=helper.headers, json=True, result=True)

    vodCategoriesList = jsdata.get('vodCategoriesList', None)
    for vdlist in vodCategoriesList:
        vodDirList = vdlist.get('vodDirList', None)
        for vdir in vodDirList:
            
            externalId = vdir.get("externalId", None)
            title = vdir.get("name", None)
            mode = 'listcontent'
            coverImagePath = vdir.get("coverImagePath", None)
            poster = helper.main_url+coverImagePath
            mod = plugin.url_for(listcontent, str(externalId))

            ispla = False
            info = {'title': title, 'plot':title}
            art = {'icon': poster, 'fanart': helper.addon.getAddonInfo('fanart')}
            helper.add_item(title, mod, playable=ispla, info=info, art=art) 

    helper.setContent('videos')    
    helper.eod()        
    
    
    
    return
@plugin.route('/loguj')    
def loguj():

    ok = False
    
    if helper.login and helper.password:

        code = helper.password
        if re.match(r'^[A-Z]', helper.login):
            code = generate_encoded_pin(code)
        
        data = {"login":helper.login,"password":code}
        helper.headers.update({
            'Accept': 'application/json;ver1',
            'Content-Type': 'application/json;ver1',
            'Referer':'https://tvgo.orange.pl/',
            'Accept-Encoding':'gzip, deflate, br',
            'Connection':'keep-alive',
        })
        helper.headers.update(helper.extra_hea())
        
        
        jsdata = helper.request_sess(helper.subscrlogin, 'post', headers=helper.headers, data= data, json=True, json_data = True, allow=False)
        if not "errCode" in jsdata:

            #helper.set_setting('currentProfileId',jsdata.get('userInfo',None).get('currentProfileId',None))
            #helper.set_setting('householdExtId',jsdata.get('householdInfo',None).get('householdExtId',None))
            helper.set_setting('refreshToken',jsdata.get('refreshToken',None))

            helper.save_file(file=helper.datapath+'kukis', data=(helper._sess.cookies).get_dict(), isJSON=True)
            
            #user info
            url='https://tvgo.orange.pl/gpapi/user/info?deviceCat=otg'
            helper.headers.update({'Accept': 'application/vnd.orangeott.v5+json','Content-Type': '' })
            helper.headers.update(helper.extra_hea())
            jsdata = helper.request_sess(url, 'get', headers=helper.headers, json=True)
            xbmc.log('@@@Profile: '+str(jsdata), level=xbmc.LOGINFO)
            helper.set_setting('currentProfileId',jsdata.get('userInfo',None).get('currentProfileId',None))
            helper.set_setting('householdExtId',jsdata.get('householdInfo',None).get('householdExtId',None))
            
            '''
            #profile
            helper.headers.update({'Accept': 'application/vnd.orangeott.v1+json','Content-Type': 'application/vnd.orangeott.v1+json' })
            data={'profileId':helper.get_setting('currentProfileId')}
            jsdata = helper.request_sess(helper.profile_url, 'post', headers=helper.headers, data= data, json_data = True)
            helper.save_file(file=helper.datapath+'kukis', data=(helper._sess.cookies).get_dict(), isJSON=True)
            '''
            return helper.login, True
    
        else:
            helper.notification('[B]Uwaga[/B]', '[B]Błąd logowania[/B]') 
           # helper.open_settings()
           # helper.refresh()
            return None,False
    else:
        helper.notification('[B]Uwaga[/B]', '[B]Brak danych logowania[/B]') 
        #helper.open_settings()
        #helper.refresh()
        return None,False


@plugin.route('/ustawienia')
def ustawienia():
    helper.open_settings()
    helper.refresh()


@plugin.route('/logout')
def logout():
    log_out = helper.dialog_choice('Uwaga','Chcesz się wylogować?',agree='TAK', disagree='NIE')
    if log_out:
        helper.save_file(file=helper.datapath+'kukis', data={}, isJSON=True)    
        helper.set_setting('logged', 'false')
        helper.refresh()

@plugin.route('/listM3U')
def listM3U():
    file_name = helper.get_setting('fname')
    path_m3u = helper.addon.getSetting('path_m3u')
    if file_name == '' or path_m3u == '':
        helper.notification('Orange TV GO', 'Podaj nazwę pliku oraz katalog docelowy.')
        return
    helper.notification('Orange TV GO', 'Generuję listę M3U.')
    data = '#EXTM3U\n'
    
    try:
        del helper.headers['Content-Type']
    except:
        pass
    
    helper.headers.update({'Accept': 'application/vnd.orangeott.v4+json','Expires':'0','Referer':'https://tvgo.orange.pl/channels'})
    helper.headers.update(helper.extra_hea())
    jsdata = helper.request_sess(helper.api_url.format('live/channel-list?hhTech=ftth&deviceCat=otg'), 'get', headers=helper.headers, json=True)#hhTech=iptv
    
    channelList = jsdata.get("channelList",None)
    for ch in channelList:
        id = ch.get("channelExtId",None)
        title = ch.get("name",None)
        img = ch.get("logoSignature",None)
        img = helper.api_url.format('resource/image/')+img
            
        isSubscribed = ch.get("isSubscribed",None)
        if not isSubscribed:
            continue
        keczup = ch.get("playFeatures",None).get("otg",None).get("isCatchUp",None)
        if keczup:
            data += '#EXTINF:0 tvg-id="%s" tvg-logo="%s" group-title="Orange TV GO" catchup="append" catchup-source="?ts={utc:Y-m-d H:M:S}&te={utcend:Y-m-d H:M:S}" catchup-days="7" ,%s\nplugin://plugin.video.orangetvgo/playtv/%s\n' %(title,img,title,id)
        else:
            data += '#EXTINF:0 tvg-id="%s" tvg-logo="%s" group-title="Orange TV GO",%s\nplugin://plugin.video.orangetvgo/playtv/%s\n' %(title,img,title,id)
        
        f = xbmcvfs.File(path_m3u + file_name, 'w')
        f.write(data)
        f.close()
        helper.notification('Orange TV GO', 'Wygenerowano listę M3U')
    

class OrangeGo(Helper):
    def __init__(self):
        super().__init__()
        plugin.run()
