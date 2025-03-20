# -*- coding: utf-8 -*-
import os
import sys

import requests
from emukodi import xbmc
from emukodi import xbmcgui
from emukodi import xbmcplugin
from emukodi import xbmcaddon
from emukodi import xbmcvfs
import re
import base64
import json
#import random
import time
import datetime
#from html import unescape
from urllib.parse import urlencode, quote_plus, quote, unquote, parse_qsl
#import hashlib

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon(id='plugin.video.eurovisionsport')
PATH=addon.getAddonInfo('path')
PATH_profile=xbmcvfs.translatePath(addon.getAddonInfo('profile'))
if not xbmcvfs.exists(PATH_profile):
    xbmcvfs.mkdir(PATH_profile)
img_empty=PATH+'/resources/img/empty.png'
img_addon=PATH+'resources/img/icon_transp.png'
fanart=PATH+'/resources/img/fanart.jpg'

UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'
baseurl='https://eurovisionsport.com/'
apiURL='https://api.evsports.opentv.com/'


hea={
    'User-Agent':UA,
    'Referer':baseurl,
    'Origin':baseurl[:-1]
}

def heaGen():
    tokens=eval(addon.getSetting('tokens'))
    h={
        'Authorization':'Bearer '+tokens['access_token'],
        'Accept':'application/json, text/plain, */*'
    }
    h.update(hea)
    return h
    
def build_url(query):
    return base_url + '?' + urlencode(query)

def addItemList(url, name, setArt, medType=False, infoLab={}, isF=True, isPla='false', contMenu=False, cmItems=[]):
    li=xbmcgui.ListItem(name)
    li.setProperty("IsPlayable", isPla)
    if medType:
        kodiVer=xbmc.getInfoLabel('System.BuildVersion')
        if kodiVer.startswith('19.'):
            li.setInfo(type=medType, infoLabels=infoLab)
        else:
            types={'video':'getVideoInfoTag','music':'getMusicInfoTag'}
            if medType!=False:
                setMedType=getattr(li,types[medType])
                vi=setMedType()
            
                labels={
                    'year':'setYear', #int
                    'episode':'setEpisode', #int
                    'season':'setSeason', #int
                    'rating':'setRating', #float
                    'mpaa':'setMpaa',
                    'plot':'setPlot',
                    'plotoutline':'setPlotOutline',
                    'title':'setTitle',
                    'originaltitle':'setOriginalTitle',
                    'sorttitle':'setSortTitle',
                    'genre':'setGenres', #list
                    'country':'setCountries', #list
                    'director':'setDirectors', #list
                    'studio':'setStudios', #list
                    'writer':'setWriters',#list
                    'duration':'setDuration', #int (in sec)
                    'tag':'setTags', #list
                    'trailer':'setTrailer', #str (path)
                    'mediatype':'setMediaType',
                    'cast':'setCast', #list        
                }
                
                if 'cast' in infoLab:
                    if infoLab['cast']!=None:
                        cast=[xbmc.Actor(c) for c in infoLab['cast']]
                        infoLab['cast']=cast

                for i in list(infoLab):
                    if i in list(labels):
                        setLab=getattr(vi,labels[i])
                        setLab(infoLab[i])
    li.setArt(setArt) 
    if contMenu:
        li.addContextMenuItems(cmItems, replaceItems=False)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=isF)

def ISAplayer(protocol,stream_url, isDRM=False, licURL=False, heaPlay='User-Agent='+UA, drm_cfg=''):
    import inputstreamhelper
    
    PROTOCOL = protocol
    DRM = 'com.widevine.alpha'
    is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
    
    if is_helper.check_inputstream():
        play_item = xbmcgui.ListItem(path=stream_url)                     
        play_item.setMimeType('application/xml+dash')
        play_item.setContentLookup(False)
        play_item.setProperty('inputstream', is_helper.inputstream_addon)        
        play_item.setProperty("IsPlayable", "true")
        play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
        #play_item.setProperty('inputstream.adaptive.license_flags', "persistent_storage")
        #play_item.setProperty('inputstream.adaptive.server_certificate', 'CrYCCAMSEJRzG84P41YiqFJz1Z5wB/UYkdXgpQUijgIwggEKAoIBAQC6vlJ9lUo8SDe3y/+eNs2VLLCWOW9ZOU97NUbwOJcN9HLbL9clUvzvVool4cPU6NFDvzWfjcIL3VvUmtQ7IQYNYMK9ps6JaMNN+pHyPkjsc0CLn2mX95gxeWWkZul6PAipMZVVTOWS7gVo4EAydZfa2wH7UZVJuTohFI8MrSZQueLel2FTO3+w+TUFlnqCRqrEiz5tUBqIiUcnO0VSDDx1kDWZkt0OYNNTaGvGex9aLOcBFmjlQOwqiTM+TDdJqJpNEO9Sm6PuKEbZ1K/eOxGiTuQyQgWfJad1onP3g5zYPuezUAgEGRf6BEUDUAuMAJyUwtrq6MH0tjhpxhvINpabAgMBAAE6CWNvbmF4LmNvbRKAA22PoCV8lNpk2b26PGrW5qiX+m9Q7DYRW5SRfYXCpfBM6VsN5WPosUoe26TLJXjBzvEBJRhLB+hN6rKv9KWDqyoQC+jPiIfducCkZngjUh4vdPTODjePE9C5Dx1rDURaZG+I7JD6z0lAKpjKyI1JyFGkfoXyywFp8l5dZbxuB+KJxw1Id0PXDUEQOrayXv9xVVWYXKUFGv4j8FKpFYJR9u0JEkkiMb1ylTBDS+shQznX3ajYUcrrJcB2OLlfVWneJG7/1TgXypLGVFAu/gVcJdtODK+TOT5zmU4Lin0gApOO1Ff7sp7KyzQfKpVEAyivl1GYtEIktEXX9wWPTNpXz05xNEi68FUwwxaKCiT0UdjWydyrV+rF9rUXLX4iWf+FqR9oZ8MV7S/4gm3jCLmthAlCsn6/yZAxLoTTCDqC5NO+tEOvGRSMqMc1CHtD/Py03lcCcoOY7t3GEXBlwKacPNBRfffYuOeDhwH+FXAozQHUkeSjZGm+HMUhUONkx20qEg==')
        play_item.setProperty('inputstream.adaptive.stream_headers', heaPlay)
        play_item.setProperty('inputstream.adaptive.manifest_headers', heaPlay)
        if isDRM:
            kodiVer=xbmc.getInfoLabel('System.BuildVersion')
            if int(kodiVer.split('.')[0])<22:
                play_item.setProperty('inputstream.adaptive.license_type', DRM)
                play_item.setProperty('inputstream.adaptive.license_key', licURL)
            else:
                play_item.setProperty("inputstream.adaptive.drm", json.dumps(drm_cfg))
    
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

def openF(u):
    try:
        f=open(u,'r',encoding = 'utf-8')
    except:
        f=open(u,'w+',encoding = 'utf-8')
    cont=f.read()
    f.close()
    return cont
    
def saveF(u,t):
    with open(u, 'w', encoding='utf-8') as f:
        f.write(t)
        
def timestampToDateStr(x,mask='%Y-%m-%d'):
    return datetime.datetime.fromtimestamp(x).strftime(mask)

def getBase():
    url='https://firebaseremoteconfig.googleapis.com/v1/projects/eurovision-sport-prod-772510/namespaces/firebase:fetch?key=AIzaSyDHnCA2y4Mqill1cTM9p0YP85X8PrzZmC4'
    data={
        "app_id": "1:1000511242667:web:00c893cf7f06e8325812ee",
        "app_instance_id": "f2YrCi6v-E3CngfXvxmMJE",
        "app_instance_id_token": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBJZCI6IjE6MTAwMDUxMTI0MjY2Nzp3ZWI6MDBjODkzY2Y3ZjA2ZTgzMjU4MTJlZSIsImV4cCI6MTcwNzk1MzM1MCwiZmlkIjoiZjJZckNpNnYtRTNDbmdmWHZ4bU1KRSIsInByb2plY3ROdW1iZXIiOjEwMDA1MTEyNDI2Njd9.AB2LPV8wRQIhAODe53tTvyrPE8gKqJLn2A4fa4c56OtfSqlJPaAzNg1IAiBYbHCdxEfFB1-_Y3Ci2z7Bi0_0t01O2a-odS5kdFl7cQ",
        "language_code": "pl",
        "sdk_version": "10.7.1"
    }
    resp=requests.post(url,headers=hea,json=data).json()
    baseVer=addon.getSetting('baseVer')
    if baseVer=='':
        baseVer='0'
    if resp['templateVersion']!=int(baseVer):
        saveF(PATH_profile+'base.txt',str(resp['entries']['st_competitions']))
        addon.setSetting('baseVer',str(resp['templateVersion']))
        #competitions base
        comps=[]
        y=json.loads(resp['entries']['st_competitions'])
        for s in list(y):
            sport=y[s]
            for f in list(sport['federations']):
                fed=sport['federations'][f]
                for c in fed['competitionTypes']:
                    c.update({'sport':s,'sport_link':sport['sportHomepageTemplate'],'federation':f,'federation_link':fed['portal']['templateToUse']})
                    comps.append(c)
        saveF(PATH_profile+'competitions.txt',str(comps))

def req(type,url,h,j=None,d=None):
    if type=='get':
        resp=requests.get(url,headers=h).json()
    elif type=='post':
        resp=requests.post(url,headers=h,data=d,json=j).json()
    if 'result' in resp:
        if resp['result'] in ['Bearer Token Expired','Bearer Token Decoding Failure']:
            if refreshToken(): #odświeżono token
                if 'Authorization' in h:
                    tokens=eval(addon.getSetting('tokens'))
                    h.update({'Authorization':'Bearer '+tokens['access_token']})
                if type=='get':
                    resp=requests.get(url,headers=h).json()
                elif type=='post':
                    resp=requests.post(url,headers=h,data=d,json=j).json()
                return resp
            else: #błąd odświeżania tokena -> wylogowano/przelogowano
                return None
        else:
            return resp    
    return resp

def getSession(): #dod
    url=baseurl+'api/auth/session'
    if addon.getSetting('cookies')=='':
        cookies={}
    else:
        cookies=eval(addon.getSetting('cookies'))
    resp=requests.get(url,headers=hea,cookies=cookies)
    cookies=dict(resp.cookies)
    addon.setSetting('cookies',str(cookies))

def get_csrfToken(): #dod
    url=baseurl+'api/auth/csrf'
    cookies=eval(addon.getSetting('cookies'))
    resp=requests.get(url,headers=hea,cookies=cookies).json()
    if 'csrfToken' in resp:
        addon.setSetting('csrfToken',resp['csrfToken'])
    else:
        xbmc.log('@@@csrfToken generation error', level=xbmc.LOGINFO)
        xbmcgui.Dialog().notification('Eurovision Sport', 'csrfToken generation error', xbmcgui.NOTIFICATION_INFO)#to_del
    
def credentials(): #dod
    get_csrfToken()
    url=baseurl+'api/auth/callback/credentials'

    email={
        "iasData":eval(addon.getSetting('tokens')),
        "username":addon.getSetting('username')
    }

    data={
        "redirect":"true",
        "email":str(email).replace('\'','\"').replace(' ',''),
        "callbackUrl":"https://eurovisionsport.com",
        "csrfToken":addon.getSetting('csrfToken'),
        "json":"true"
    }
    data=urlencode(data)
    cookies=eval(addon.getSetting('cookies'))
    HEA={'Content-Type': 'application/x-www-form-urlencoded'}
    HEA.update(hea)
    resp=requests.post(url,headers=HEA,cookies=cookies,data=data)
    try:
        respJSON=resp.json()
        if 'url' in respJSON:
            cookies.update(dict(resp.cookies))
            addon.setSetting('cookies',str(cookies))
            return True
        else:
            xbmc.log('@@@credentials error: '+str(respJSON), level=xbmc.LOGINFO)
            xbmcgui.Dialog().notification('Eurovision Sport', 'csrfToken generation error', xbmcgui.NOTIFICATION_INFO)#to_del
            return False
    except:
        xbmc.log('@@@credentials error_2', level=xbmc.LOGINFO)
        return False

def cleanCookies(): #dod
    cookies=eval(addon.getSetting('cookies'))
    new_cookies={
        '__Host-next-auth.csrf-token':cookies['__Host-next-auth.csrf-token'],
        '__Secure-next-auth.callback-url':cookies['__Secure-next-auth.callback-url']
    }
    addon.setSetting('cookies',str(new_cookies))
                
def refreshToken():
    url=apiURL+'ias/v2/token'
    params={
        'grant_type':'refresh_token',
        'refresh_token':eval(addon.getSetting('tokens'))['refresh_token']
    }
    data={
        "device": {
            "hardware": {
                "formFactor": "Firefox 122",
                "type": "Browser"
            },
            "OS": {
                "type": "Windows",
                "version": "10"
            },
            "screen": {
                "density": 1,
                "height": 1080,
                "width": 1920
            }
        }
    }
    Hea={'Accept':'application/json, text/plain, */*','Content-Type':'application/json','tenantid':'nagra'}
    Hea.update(hea)
    resp=requests.post(url,headers=Hea,params=params,json=data).json()
    if 'access_token' in resp:
        addon.setSetting('tokens',str(resp))
        credentials()
        #xbmcgui.Dialog().notification('Eurovision Sport', 'access_token refreshed', xbmcgui.NOTIFICATION_INFO)
        xbmc.log('@@@access_token refreshed', level=xbmc.LOGINFO)
        return True
    else:
        xbmc.log('@@@Error during access_token refreshing: '+str(resp), level=xbmc.LOGINFO)
        paraLogOut()
        logIn()
        return False
    
    
def paraLogOut():
    addon.setSetting('tokens','')
    addon.setSetting('logged','false')
    cleanCookies()
    xbmc.log('@@@Trying to re-login (paralogout)', level=xbmc.LOGINFO)
    #xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
    #xbmc.executebuiltin('Container.Update(plugin://plugin.video.eurovisionsport/,replace)')


def logIn():
    login=addon.getSetting('username')
    password=addon.getSetting('password')
    if login!='' and password!='':
        url=apiURL+'ias/v2/token'
        params={
            'grant_type':'password',
            'username':login,
            'password':password
        }
        data={
            "device": {
                "hardware": {
                    "formFactor": "Firefox 122",
                    "type": "Browser"
                },
                "OS": {
                    "type": "Windows",
                    "version": "10"
                },
                "screen": {
                    "density": 1,
                    "height": 1080,
                    "width": 1920
                }
            }
        }
        Hea={'Accept':'application/json, text/plain, */*','Content-Type':'application/json','tenantid':'nagra'}
        Hea.update(hea)
        resp=requests.post(url,headers=Hea,params=params,json=data).json()
        logged=False
        if 'access_token' in resp: #refresh_token,access_token,client_id,fixed_refresh_expires_in,accountId,refresh_expires_in,expires_in,bearer
            addon.setSetting('tokens',str(resp))
            if credentials():
                logged=True
        if logged:
            xbmcgui.Dialog().notification('Eurovision Sport', 'Logged In', xbmcgui.NOTIFICATION_INFO)
            addon.setSetting('logged','true')
        else:
            addon.setSetting('tokens','')
            xbmcgui.Dialog().notification('Eurovision Sport', 'LogIn error', xbmcgui.NOTIFICATION_INFO)
            xbmc.log('@@@LogIn error: '+str(resp), level=xbmc.LOGINFO)
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
            xbmc.executebuiltin('Container.Update(plugin://plugin.video.eurovisionsport/,replace)')
        
    else:
        xbmcgui.Dialog().notification('Eurovision Sport', 'Complete account data in settings', xbmcgui.NOTIFICATION_INFO)
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
        xbmc.executebuiltin('Container.Update(plugin://plugin.video.eurovisionsport/,replace)')
    
def logOut():
    get_csrfToken()
    url=baseurl+'api/auth/signout'
    data={
        "csrfToken": addon.getSetting('csrfToken'),
        "callbackUrl": "https://eurovisionsport.com",
        "json": "true"
    }
    cookies=eval(addon.getSetting('cookies'))
    resp=requests.post(url,headers=hea,json=data,cookies=cookies)
    respJSON=resp.json()
    if 'url' in respJSON:
        cookies.update(dict(resp.cookies))
        addon.setSetting('tokens','')
        addon.setSetting('logged','false')

    else:
        xbmcgui.Dialog().notification('Eurovision Sport', 'LogOut error', xbmcgui.NOTIFICATION_INFO)
        xbmc.log('@@@LogOut error: '+str(respJSON), level=xbmc.LOGINFO)
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
        xbmc.executebuiltin('Container.Update(plugin://plugin.video.eurovisionsport/,replace)')

def main_menu():
    if addon.getSetting('logged')!='true':
        sources=[
            ['Log In','logIn','','DefaultUser.png']
        ]
    else:
        sources=[
            ['Schedule','schedule','','DefaultYear.png'],
            ['Sports','browser','EBU-Explore-V2-Sports',img_addon],
            ['Federations','browser','EBU-Explore',img_addon],
            ['Log out','logOut','','DefaultUser.png']
        ]
    for s in sources:
        setArt={'icon': s[3],'fanart':fanart}
        url = build_url({'mode':s[1],'type':s[2]})       
        if s[1]=='playSource':
            addItemList(url, s[0], setArt, 'video', {}, False, 'true')
        else:
            addItemList(url, s[0], setArt)
        
    xbmcplugin.endOfDirectory(addon_handle)

def testSections(s): #helper
    y=[ss for ss in s if ss['contents'][0]!=None ]
    if len(y)==0:
        return False
    else:
        return True
        
def getCompImg(x,compsBase): #helper
    try:
        content=[s['contents'] for s in x['sections'] if s['contents'][0]!=None ][0]
        categs=content[0]['Categories']
        compName=[c.split(':')[-1] for c in categs if c.split(':')[0]=='Tournament_name'][0]
        img=[comp['UI']['defaultLogo'] for comp in compsBase if comp['id']==compName][0]
        return img
    except:
        return None
    

def browser(t):
    url=apiURL+'/contentdelivery/v2/templateviews/'+t
    HEA=heaGen()
    HEA.update({
        'Nagra-Target':'everything',
        'Nagra-Device-Type':'Android,IOS',
        'Accept-Language':'en_US'
    })
    compsBase=eval(openF(PATH_profile+'competitions.txt'))
    if t=='EBU-Explore-V2-Sports': #dyscypliny: lista
        ex=openF(PATH_profile+'base.txt')
        data=json.loads(ex)
        for k in list(data.keys()):
            sport=data[k]
            title=k
            img=sport['sportLogo']
            cid=sport['sportHomepageTemplate']
            
            setArt={'icon': img,'fanart':fanart}
            url = build_url({'mode':'browser','type':cid})       
            addItemList(url, title, setArt)
            
    elif t=='EBU-Explore': #federacje: lista
        ex=openF(PATH_profile+'base.txt')
        data=json.loads(ex)
        for k in list(data.keys()):
            feds=data[k]['federations']
            for f in list(feds.keys()):
                fed=feds[f]['portal']
                title=fed['title']
                img=fed['logo']
                cid=fed['templateToUse']
                
                setArt={'icon': img,'fanart':fanart}
                url = build_url({'mode':'browser','type':cid})       
                addItemList(url, title, setArt)
        
    elif 'LandingPage' in t: #federacja: zawartość
        items=['Videos','Competitions']
        for i in items:
            title=i
            cid=t.replace('LandingPage',i)
            setArt={'icon':img_addon,'fanart':fanart}
            if i=='Videos':
                url = build_url({'mode':'browser','type':cid})
            elif i=='Competitions':
                url = build_url({'mode':'competitions','cid':t})
            addItemList(url, title, setArt)
    
    else:
        resp=req('get',url,HEA)
        if resp!=None:
            for r in resp['rails']:
                
                #remove ads sections
                try:
                    if r['sections'][0]['properties']['componentToUse']=='Ad':
                        continue
                except:
                    pass

                title=r['title']
                name='Promoted' if title=='Carrousel' else title
                setArt={'icon':img_addon,'fanart':fanart}
                
                if title=='Live & Upcoming':
                    if 'sections' in r:
                        if len(r['sections'])==1:
                            filterKey=r['sections'][0]['properties']['filterKey']
                            filterValues=r['sections'][0]['properties']['filterValues']
                            url = build_url({'mode':'schedule','cid':filterValues,'type':filterKey})
                            addItemList(url, name, setArt)
                elif r['name']=='Competitions':
                    url = build_url({'mode':'competitions','cid':t})
                    addItemList(url, name, setArt)
                else:
                    saveF(PATH_profile+'browser.txt',str(resp['rails']))
                    url = build_url({'mode':'browseSections','title':title})       
                    imgComp=getCompImg(r,compsBase)
                    if imgComp!=None:
                        setArt={'icon': imgComp,'fanart':fanart}
                    if testSections(r['sections']) and r['name'] not in ['Competition','CompetitionCards']:
                        addItemList(url, name, setArt)
                    
    xbmcplugin.endOfDirectory(addon_handle)
    
def competitions(c):
    ex=openF(PATH_profile+'competitions.txt')
    data=eval(ex)
    if 'EBU-Home' in c:
        comps=[d for d in data if d['sport_link']==c]
    else:
        comps=[d for d in data if d['federation_link']==c]
    
    if len(comps)>0:
        def sortFN(i):
            return i['period']['start']

        comps.sort(key=sortFN,reverse=False)
    
    now=int(time.time())
    for c in comps:
        if True:#c['period']['end']>now:
            cid=c['id']
            title=c['title']
            title+= ' -  '+c['location']
            start=c['period']['start']
            end=c['period']['end']
            title+=' (%s - %s)'%(timestampToDateStr(start),timestampToDateStr(end))
            img=c['UI']['defaultLogo']
            
            setArt={'icon':img,'fanart':fanart}
            url = build_url({'mode':'schedule','cid':cid,'start':str(start),'end':str(end)}) 
            addItemList(url, title, setArt)        

    xbmcplugin.endOfDirectory(addon_handle)   

def addItem(content):
    title=content['title']
    date=timestampToDateStr(content['CUStartDate'])
    title+=' (%s)'%(date)
    dur=content['duration'] if 'duration' in content else 0
    dur=dur if dur!=None else 0
    desc=content['Description'] if 'Description' in content else ''
    year=content['Year'] if 'Year' in content else 0
    year=year if year!=None else 0
    playType=content['playbackType']
    cid=content['id']
    img='https://eurovisionsport.com/_next/image?url=https://api.evsports.opentv.com/ihs/v1/contents/'+cid+'?width=450&height=253&w=384&q=75'
    
    if 'vod-' in playType:
        iL={'title': title,'sorttitle': title,'plotoutline':desc,'plot': desc,'year':int(year),'duration':dur,'mediatype':'movie'}
        isF=False
        isP='true'
        URL=build_url({'mode':'playSource','cid':cid})
    else: #TO DO (czy w ogóle takie istnieją)
        iL={}
        URL=build_url({'mode':'noName','cid':cid})
        isF=False
        isP='true'
        title='[I]%s[/I]'%(title)
        
    setArt={'poster':'','icon': img,'fanart':fanart}    
    addItemList(URL, title, setArt, 'video', iL, isF, isP)
 
def browseSections(t):
    data=eval(openF(PATH_profile+'browser.txt'))
    item=[r for r in data if r['title']==t][0]

    if 'sections' in item:
        for s in item['sections']:
            if s['type']=='ContentItem':
                if 'contents' in s:
                    if len(s['contents'])==1: #TODO - sprawdzić czy jest więcej niż 1 content
                        content=s['contents'][0]
                        if content!=None:
                            addItem(content)
            
            elif s['type']=='DynamicContentGroupItem':
                if 'contents' in s:
                    for c in s['contents']:
                        addItem(c)
                
            elif s['name'] in ['Live','Live&Upcoming']:
                if 'contents' in s:
                    filterKey=s['properties']['filterKey']
                    filterValues=s['properties']['filterValues']
                    url = build_url({'mode':'schedule','cid':filterValues,'type':filterKey})
                    
                    setArt={'poster':'','icon': 'DefaultYear.png','fanart':fanart} 
                    addItemList(url, 'Live & Upcoming', setArt)
                        
        
    xbmcplugin.setContent(addon_handle, 'videos')    
    xbmcplugin.endOfDirectory(addon_handle)

def schedule(CID=None,s=None,e=None,type=None):
    c=''

    if s!=None and CID!=None: #sekcja competitions
        c='"editorial.tournament_name":"'+CID+'"'
        #url=apiURL+'metadata/delivery/GLOBAL/btv/programmes?token=undefined&filter={"editorial.isLive":"true",'+c+'"locale":"en_US","$and":[{"period.end":{"$gte": '+s+'}},{"period.start":{"$lt": '+e+'}}]}&limit=9999&sort=[["period.start", 1]]'
        now=str(int(time.time()))
        
        url=apiURL+'metadata/delivery/v2/GLOBAL/vod/editorials?filter={"editorial.isLive":"true","isValid":true,"isVisible":true,"technical.deviceType":{"$in":["Android"]},"technical.period.start":{ "$lt": '+now+' },"technical.media":{"$exists":true },"locale":"en_US",'+c+'}&limit=9999&sort=[["technical.period.start", 1]]'
        ct='editorials'
        
    if s==None: #sekcja epg
        now=int(time.time())
        now_date=datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d')
        now_tmp=int(datetime.datetime(*(time.strptime(now_date,'%Y-%m-%d')[0:6])).timestamp())
        future_tmp=now_tmp+14*24*60*60
        s=str(now_tmp)
        e=str(future_tmp)
        
        url=apiURL+'metadata/delivery/GLOBAL/btv/programmes?token=undefined&filter={"editorial.isLive":"true",'+c+'"locale":"en_US","$and":[{"period.end":{"$gte": '+s+'}},{"period.start":{"$lt": '+e+'}}]}&limit=9999&sort=[["period.start", 1]]'
        ct='programmes'
    
    HEA=heaGen()
    resp=req('get',url,HEA)
    if resp!=None:
        for r in resp[ct]:
            title=r['title']
            start=timestampToDateStr(r['period']['start'],'%Y-%m-%d %H:%M')
            end=timestampToDateStr(r['period']['end'],'%Y-%m-%d %H:%M')
            if start.split(' ')[0]==end.split(' ')[0]:
                d_start=start.split(' ')[0]
                h_start=start.split(' ')[1]
                h_end=end.split(' ')[1]
                title+=' | %s | %s - %s'%(d_start,h_start,h_end) 
            else:
                title+=' | %s - %s'%(start,end)
            title=title.replace(timestampToDateStr(int(time.time())),'[B]Today[/B]')
            dur=r['duration'] if 'duration' in r else 0
            dur=dur if dur!=None else 0
            desc=r['Description'] if 'Description' in r else ''
            year=r['Year'] if 'Year' in r else 0
            year=year if year!=None else 0
            cid=r['editorial']['id'] if ct=='programmes' else r['id']
            sid=r['serviceRef'] if ct=='programmes' else None
            img='https://eurovisionsport.com/_next/image?url=https://api.evsports.opentv.com/ihs/v1/contents/'+cid+'?width=450&height=253&w=384&q=75'
            
            iL={'title': title,'sorttitle': title,'plotoutline':desc,'plot': desc,'year':int(year),'duration':dur,'mediatype':'movie'}
            
            if time.time()>r['period']['start'] and time.time()<r['period']['end'] and ct=='programmes':
                title+=' [COLOR=yellow][LIVE][/COLOR]'
                isF=False
                isP='true'
                URL=build_url({'mode':'playLive','cid':sid})
            elif time.time()>r['period']['end'] or ct=='editorials' :
                isF=False
                isP='true'
                URL=build_url({'mode':'playSource','cid':cid})
            else:
                isF=False
                isP='false'
                URL=build_url({'mode':'noPlay'})
            
            setArt={'poster':'','icon': img,'fanart':fanart}    
            if cid!=None and type!=None:
                if r['editorial'][type] in CID.split(','):
                    addItemList(URL, title, setArt, 'video', iL, isF, isP)
            else:
                addItemList(URL, title, setArt, 'video', iL, isF, isP)
        
    xbmcplugin.setContent(addon_handle, 'videos')    
    xbmcplugin.endOfDirectory(addon_handle)

def playSource(cid,live=False):
    playable=True
    if live:
        url='https://api.evsports.opentv.com/metadata/delivery/GLOBAL/btv/services?token=undefined&filter={"technical.deviceType":"Android", "locale":"en_US" }&limit=9999'
        HEA=heaGen()
        resp=req('get',url,HEA)
        if resp!=None:
            services=[s for s in resp['services'] if s['editorial']['id']==cid][0]
            stream=services['technical']
            stream_url=stream['StartOverLocation']
            drmId=stream['drmId']
    
    else:
        url=apiURL+'metadata/delivery/v2/GLOBAL/vod/editorials?filter={"editorial.id":{"$in": ["'+cid+'"]},"locale":"en_US","isValid":true,"isVisible":true}&limit=9999&sort=[["Title", 1]]'
        HEA=heaGen()
        resp=req('get',url,HEA)
        if resp!=None:
            #print(resp)
            streams=resp['editorials'][0]['technicals']
            streamsDASH=[s for s in streams if 'DASH' in s['drmInstanceName']] #drmId
            if len(streamsDASH)==1:
                stream_url=streamsDASH[0]['media']['AV_PlaylistName']['uri']
                drmId=streamsDASH[0]['media']['AV_PlaylistName']['drmId']
            
    if stream_url!=None:
        #nv-token
        url=apiURL+'ias/v2/content_token?content_id='+drmId+'&type=device'
        HEA=heaGen()
        HEA.update({'Nv-Tenant-Id':'nagra'})
        resp=req('post',url,HEA)
        if resp!=None:
            content_token=resp['content_token']
               
            #licKey
            provider='EVSP4WAB' #czy zawsze taki?
            licURL='https://evsp4wab.anycast.nagra.com/'+provider+'/wvls/contentlicenseservice/v1/licenses'
            heaLic={
                'Content-Type':'application/octet-stream',
                'nv-authorizations':content_token
            }
            heaLic.update(hea)
            licKey='%s|%s|%s|'%(licURL,urlencode(heaLic),'R{SSM}')
            heaPlay=hea
            
            #K22
            drm_cfg = {
                "com.widevine.alpha": {
                    "license": {
                        "server_url": licURL,
                        "req_headers": urlencode(heaLic)
                    }
                }
            }
            
            ISAplayer('mpd',stream_url, True, licKey, urlencode(heaPlay), drm_cfg)
        else:
            playable=False
    else:
        playable=False
    
    if not playable:
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())


mode = params.get('mode', None)

if not mode:
    now=int(time.time())
    baseUpdt=addon.getSetting('baseUpdt')
    if baseUpdt=='':
        baseUpdt='0'
    if now-int(baseUpdt)>=6*60*60:
        getBase()
        addon.setSetting('baseUpdt',str(now))
    
    if addon.getSetting('cookies')=='':
        getSession()

    main_menu()
else:
    if mode=='logIn':
        logIn()
        if addon.getSetting('logged')=='true':
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
            xbmc.executebuiltin('Container.Update(plugin://plugin.video.eurovisionsport/,replace)')
            
    if mode=='logOut':
        logOut()
        if addon.getSetting('logged')=='false':
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
            xbmc.executebuiltin('Container.Update(plugin://plugin.video.eurovisionsport/,replace)')
    
    if mode=='browser':
        type=params.get('type')
        browser(type)
    
    if mode=='competitions':
        cid=params.get('cid')
        competitions(cid)
    
    if mode=='browseSections':
        title=params.get('title')
        browseSections(title)
        
    if mode=='schedule':
        cid=params.get('cid')
        start=params.get('start')
        end=params.get('end')
        type=params.get('type')
        schedule(cid,start,end,type)
    
    if mode=='playSource':
        cid=params.get('cid')
        playSource(cid)
     
    if mode=='playLive':
        cid=params.get('cid')
        playSource(cid,True)
     
    if mode=='noPlay':
        pass
        