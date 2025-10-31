import os
import sys

import requests
from emukodi import xbmc
from emukodi import xbmcgui
from emukodi import xbmcplugin
from emukodi import xbmcaddon
from emukodi import xbmcvfs
import json
import time,datetime
import re
from html import unescape
from urllib.parse import urlencode, quote_plus, quote, unquote, parse_qsl
from .base import b

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
base=b(base_url,addon_handle)

addon = base.addon
PATH_profile=base.PATH_profile
PATH=addon.getAddonInfo('path')
img_path=PATH+'/resources/images/'

hea={
    'User-Agent':base.UA
}

class tvpExt:
    def __init__(self, livePlayerType, cnt, streamTvProtocol):
        self.livePlayerType=livePlayerType
        self.cnt=cnt
        self.streamTvProtocol=streamTvProtocol
        self.protocols={'HLS':'hls','DASH':'mpd'}
        self.mimeTypes={'HLS':'application/x-mpegurl','DASH':'application/dash+xml'}
    
    def playProg(self,aId,live=False):#TVPINFO
        #url='https://www.tvp.pl/shared/cdn/tokenizer_v2.php?object_id='+str(aId)+'&sdt_version=1'
        url='https://token-java-v2.tvp.pl/tokenizer/token/'+str(aId)
        resp=requests.get(url,headers=hea).json()
        stream_url=''
        if 'formats' in resp:
            mimeType=self.mimeTypes[self.streamTvProtocol] if live else 'application/x-mpegurl'
            protocol=self.protocols[self.streamTvProtocol] if live else 'hls'
            if resp['formats']!=None:
                formats = [f for f in resp['formats'] if f['mimeType']==mimeType]
                def sortFN(i):
                    return i['totalBitrate']
                formats.sort(key=sortFN,reverse=True)
                stream_url=formats[0]['url']
                '''
                if 'audioLang' not in formats[0]:
                    stream_url=formats[0]['url']
                else:
                    src=[]
                    urls=[]
                    for f in formats:
                        if 'audioLang' in f:
                            src.append(f['audioLang'])
                        else:
                            src.append('Nieokreślony')
                        urls.append(f['url'])
                    select = xbmcgui.Dialog().select('Źródła', src)
                    if select > -1:
                        url_stream=src[select]
                    else:
                        quit()
                '''
        if stream_url!='':
            xbmc.log('@@@stream_url: '+stream_url, level=xbmc.LOGINFO)
            #subt=subt_gen_free(aId)
            if '.mp4' in stream_url:        
                base.directPlayer(stream_url)
            elif live and self.livePlayerType=='ffmpeg':
                base.ISffmpegPlayer(protocol,stream_url)
            else:
                if protocol=='hls' and live:    
                    proxyport = addon.getSetting('proxyport')
                    stream_url='http://127.0.0.1:%s/MANIFEST='%(str(proxyport))+stream_url
                
                import inputstreamhelper
                PROTOCOL = protocol
                is_helper = inputstreamhelper.Helper(PROTOCOL)
                if is_helper.check_inputstream():
                    play_item = xbmcgui.ListItem(path=stream_url)
                    play_item.setContentLookup(False)
                    play_item.setMimeType('application/dash+xml')
                    #play_item.setSubtitles(subt)
                    play_item.setProperty("inputstream", is_helper.inputstream_addon)
                    play_item.setProperty("inputstream.adaptive.manifest_type", PROTOCOL)
                    play_item.setProperty('inputstream.adaptive.stream_headers', 'User-Agent='+base.UA)
                    play_item.setProperty('inputstream.adaptive.manifest_headers', 'User-Agent='+base.UA)#K21
                    
                    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
        else:
            xbmcgui.Dialog().notification('TVP_VOD', 'Brak źródła', xbmcgui.NOTIFICATION_INFO)
            xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
                     
    def sportTrans(self):#TVP SPORT
        count=500
        url='http://www.api.v3.tvp.pl/shared/listing.php?dump=json&direct=false&count='+str(count)+'&parent_id=13010508&type=epg_item&filter={"is_live":True}&order={"release_date_long":-1}'
        hea.update({'Referer':'https://sport.tvp.pl/'})
        resp=requests.get(url,headers=hea).json()
        transData=[]
        for i in resp['items']:
            now=1000*int(time.time())
            if i['broadcast_end_date_long']>now or (i['playable'] and not i['is_released']):
                #asset_id=i['asset_id']
                today=datetime.datetime.now().strftime('%Y-%m-%d')
                date='Dziś' if today==i['release_date_dt'] else i['release_date_dt']
                title='[B]%s[/B] %s | %s'%(date,i['release_date_hour'],i['title'])
                playable='true' if i['playable'] else 'false'
                if i['playable']:
                    title='[COLOR=yellow][LIVE][/COLOR]'+title.split('|')[1]
                descr='%s\n\n[I]%s[/I]'%(title,self.cleanText(i['lead']))
                channel_id=i['video_id'] #sprawdzić z którego ID odtwarza
                img=''
                if 'image' in i:
                    if 'file_name' in i['image'][0]:
                        imgFile=i['image'][0]['file_name']
                        imgType=imgFile.split('.')[-1]
                        imgWidth=i['image'][0]['width']
                        img='http://s.v3.tvp.pl/images/%s/%s/%s/uid_%s_width_%d_gs_0.%s' %(imgFile[0],imgFile[1],imgFile[2],imgFile[:-4],imgWidth,imgType)
                plot=descr
                timeStart=i['release_date_long']
                timeEnd=i['broadcast_end_date_long']
                transData.append([title,plot,img,channel_id,timeStart,timeEnd,playable])
        transDataRev=transData[::-1]
        for t in transDataRev:
            iL={'title': t[0],'sorttitle': t[0],'plot': t[1]}
            setArt={'thumb': t[2], 'poster': t[2], 'banner': t[2], 'icon': t[2], 'fanart': ''}
            url_cont = base.build_url({'mode':'playSportLive','asset_id':t[3],'timeStart':t[4],'timeEnd':t[5],'playable':t[6]})
            base.addItemList(url_cont, t[0], setArt, 'video', iL, False, 'true')
        xbmcplugin.endOfDirectory(addon_handle)

    def playSportLive(self,aId,ts,te,pla):#TVP SPORT
        '''
        now=1000*int(time.time())
        if now>int(ts):
            self.playProg(aId,live=True)
        '''
        if pla=='true':
            self.playProg(aId,live=True)
        else:
            xbmcgui.Dialog().notification('TVP SPORT', 'Transmisja nie jest jeszcze prowadzona', xbmcgui.NOTIFICATION_INFO)
            xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())

    #rc
    def itemCategs(self,aid):
        url='http://www.api.v3.tvp.pl/shared/listing.php?dump=json&direct=true&count=100&parent_id='+aid
        resp=requests.get(url,headers=hea).json()
        #progDir=[r['asset_id'] for r in resp['items'] if 'object_type' in r and r['object_type']=='directory_series'][0]
        
        for i in resp['items']:
            img=''
            setArt={'thumb': '', 'poster': img_path+'rc.png', 'banner': '', 'icon': 'OverlayUnwatched.png', 'fanart': ''}
            url_cont = base.build_url({'mode':'progList','asset_id':str(i['asset_id'])})
            base.addItemList(url_cont, i['title'], setArt)
        xbmcplugin.endOfDirectory(addon_handle)


    #tvp3
    def regionyList(self):
        url='http://www.api.v3.tvp.pl/shared/listing.php?dump=json&direct=true&count=100&parent_id=38345166'
        resp=requests.get(url,headers=hea).json()
          
        setArt={'thumb': '', 'poster': img_path+'tvp3.png', 'banner': '', 'icon': 'OverlayUnwatched.png', 'fanart': ''}
        url_cont = base.build_url({'mode':'progCategs','asset_id':'38345015'})
        base.addItemList(url_cont, 'Pasmo wspólne', setArt)
        
        for i in resp['items']:
            setArt={'thumb': '', 'poster': img_path+'tvp3.png', 'banner': '', 'icon': 'OverlayUnwatched.png', 'fanart': ''}
            url_cont = base.build_url({'mode':'progCategs','asset_id':str(i['asset_id'])})
            base.addItemList(url_cont, i['title'], setArt)
        xbmcplugin.endOfDirectory(addon_handle)

    def progCategs(self,aid):
        url='http://www.api.v3.tvp.pl/shared/listing.php?dump=json&direct=true&count=100&parent_id='+aid
        resp=requests.get(url,headers=hea).json()
        progDir=[r['asset_id'] for r in resp['items'] if 'object_type' in r and r['object_type']=='directory_series'][0]
        
        url='http://www.api.v3.tvp.pl/shared/listing.php?dump=json&direct=true&count=100&parent_id='+str(progDir)
        resp=requests.get(url,headers=hea).json()
            
        setArt={'thumb': '', 'poster': img_path+'tvp3.png', 'banner': '', 'icon': 'OverlayUnwatched.png', 'fanart': ''}
        url_cont = base.build_url({'mode':'progList','asset_id':str(progDir),'all':'true'})
        base.addItemList(url_cont, '[B]Wszystkie programy[/B]', setArt)
        
        for i in resp['items']:
            img=img_path+'tvp3.png'
            if 'image' in i:
                img=self.getImage(i['image'])
            
            setArt={'thumb': '', 'poster': img, 'banner': '', 'icon': 'OverlayUnwatched.png', 'fanart': ''}
            url_cont = base.build_url({'mode':'progList','asset_id':str(i['asset_id'])})
            base.addItemList(url_cont, i['title'], setArt)
            
        xbmcplugin.endOfDirectory(addon_handle)

    def getImage(self,ai): #helper
        img=''
        if len(ai)>0:
            try:
                imgFile,imgExt=ai[0]['file_name'].split('.')
                imgW=ai[0]['width'] if 'width' in ai[0] and ai[0]['width']>0 else '320'
                imgH=ai[0]['height'] if 'height' in ai[0] and ai[0]['height']>0 else '180'
                #img='https://s.tvp.pl/images/a/1/1/uid_%s_width_%s_play_0_pos_0_gs_0.%s'%(imgFile,imgW,imgExt)
                #img='https://s1.tvp.pl/%s/a/0/0/uid_%s_width_%s_play_0_pos_0_gs_0_height_%s.%s' %('images2',imgFile,imgW,imgH,imgExt)
                img='http://s.v3.tvp.pl/images/%s/%s/%s/uid_%s_width_%s_gs_0.%s' %(imgFile[0],imgFile[1],imgFile[2],imgFile,imgW,imgExt)
            except:
                img=''
        return img

    def progList(self,aid,all=None):
        if all=='true':
            url='http://www.api.v3.tvp.pl/shared/listing.php?dump=json&direct=false&count=200&parent_id='+aid+'&type=website&order={"title":1}'
        else:
            url='http://www.api.v3.tvp.pl/shared/listing.php?dump=json&direct=true&count=100&parent_id='+aid+'&type=website&order={"title":1}'
        resp=requests.get(url,headers=hea).json()
        
        for i in resp['items']:
            Aid=str(i['asset_id'])
            title=i['title']
            desc=i['lead'] if 'lead' in i else ''
            if desc=='!!! pusty LEAD !!!':
                desc=i['lead_root'] if 'lead_root' in i and i['lead_root']!='!!! pusty LEAD !!!' else ''
            img=''
            if 'logo' in i:
                img=self.getImage(i['logo'])
            elif 'image_16x9' in i:
                img=self.getImage(i['image_16x9'])
            elif 'image' in i:
                img=self.getImage(i['image'])
            elif 'image_vod' in i:
                img=self.getImage(i['image_vod'])
            
            if 38608004 in i['parents']: #programy z pasma wspólnego
                if '/regiony-tvp/' not in i['url']: #przekierowanie na www innego regionu 
                    Aid=i['url'].split('/')[3]
            
            iL={'title': title,'sorttitle': '','plot': self.cleanText(desc)}
            setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart': ''}
            url_cont = base.build_url({'mode':'vidDir','asset_id':Aid})
            cmItems=[('[B]Dodaj do ulubionych[/B]','RunPlugin(plugin://plugin.video.TVP_VOD?mode=favExtAdd&url='+quote(url_cont)+'&title='+quote(title)+'&infoLab='+quote(str(iL))+'&img='+quote(img)+')')]
            base.addItemList(url_cont, title, setArt, 'video', iL, contMenu=True, cmItems=cmItems)
            
        xbmcplugin.endOfDirectory(addon_handle)

    def vidDir(self,aid):#sprawdzenie czy materiały wideo są grupowane w kategoriach
        url='http://www.api.v3.tvp.pl/shared/listing.php?dump=json&direct=true&count=100&parent_id='+aid
        resp=requests.get(url,headers=hea).json()
        dirs=[i for i in resp['items'] if 'object_type' in i and i['object_type']=='directory_video']
        if len(dirs)>1:
            if len(dirs)==2 and dirs[0]['title']==dirs[1]['title']:#dot. rc (zdublowane katalogi z video)
                self.epList(str(dirs[0]['asset_id']),'1')
            else:
                for j,d in enumerate(dirs):
                    if j==0 or (j>0 and d['title']!=dirs[j-1]['title']):#dot. rc (zdublowane katalogi z video)
                        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': '', 'fanart': ''}
                        url_cont = base.build_url({'mode':'epList','asset_id':str(d['asset_id']),'page':'1'})
                        base.addItemList(url_cont, d['title'], setArt)
                xbmcplugin.endOfDirectory(addon_handle)
        else:
            self.epList(aid,'1')
        
    def epList(self,aid,pg):
        cnt=self.cnt
        start=(int(pg)-1)*int(cnt)
        
        url='http://www.api.v3.tvp.pl/shared/listing.php?dump=json&direct=false&count='+cnt+'&parent_id='+aid+'&object_type=video&filter={%22playable%22:True}&order={"release_date_long":-1}&offset='+str(start)
        resp=requests.get(url,headers=hea).json()
        for i in resp['items']:
            title=i['title']
            if 'website_title' in i:
                title=i['website_title']+ ' | '+title
            desc=i['lead'] if 'lead' in i else ''
            if desc=='!!! pusty LEAD !!!':
                desc=i['lead_root'] if 'lead_root' in i and i['lead_root']!='!!! pusty LEAD !!!' else ''
            if desc=='':
                desc=i['description_root'] if 'description_root' in i and i['description_root']!='!!! pusty LEAD !!!' else ''
            dur=i['duration_min'] if 'duration_min' in i else 0
            
            plot=''
            if dur>0:
                plot+='[B]Długość: [/B]'+str(dur)+' min.\n'
            if desc!='':
                plot+='[I]'+self.cleanText(desc)+'[/I]'
            
            img=''
            if 'image_16x9' in i:
                img=self.getImage(i['image_16x9'])
            elif 'image' in i:
                img=self.getImage(i['image'])
                    
            iL={'title': title,'sorttitle': '','plot': plot}
            setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart': ''}
            url_cont = base.build_url({'mode':'playProg','asset_id':i['asset_id']})
            base.addItemList(url_cont, title, setArt, 'video', iL, False, 'true')

        if start+int(cnt)<resp['total_count']:        
            setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': '', 'fanart': ''}
            url_cont = base.build_url({'mode':'epList','asset_id':aid,'page':str(int(pg)+1)})
            base.addItemList(url_cont, '[B][COLOR=yellow]>>> Następna strona[/COLOR][/B]', setArt,'video')
                    
        xbmcplugin.setContent(addon_handle, 'videos')
        xbmcplugin.endOfDirectory(addon_handle)

    def cleanText(self,t):
        t=unescape(t)
        toDel=['<p>','</p>','<strong>','</strong>','&nbsp;','</span>']
        for d in toDel:
            t=t.replace(d,'')
        t=t.replace('<br>',' ')
        t=re.sub('<([^<]+?)>','',t)
        return t

    ###NEW API

    def getApiUrl(self,p): #helper
        api={
            'tvp_info':'https://www.tvp.info/api/info/',
            'tvp_sport':'https://sport.tvp.pl/api/sport/'
        }
        return api[p]
        
    def tmpToStr(self,x): #helper
        y=int(x/1000)
        return datetime.datetime.fromtimestamp(y).strftime('%Y-%m-%d %H:%M')

    def categsList(self,portal,id): #TVP INFO
        url=self.getApiUrl(portal)+'category?device=www&id='+id
        resp=requests.get(url,headers=hea).json()
        
        for r in resp['data']['menu']:
            setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': 'DefaultAddonVideo.png', 'fanart': ''}
            url_cont = base.build_url({'mode':'videoList','portal':portal,'cid':str(r['_id']),'page':'1'})
            base.addItemList(url_cont, r['title'], setArt)
            
        xbmcplugin.endOfDirectory(addon_handle)

    def addItemToList(self,r): #helper
        if r['type'] in ['VIDEO','video'] and r['playable']:
            vid=r['_id']
            title=r['title']
            date=self.tmpToStr(r['publication_start'])
            dur=str(int(r['duration']/60))+' min.'
            if dur=='0 min.': 
                dur='mniej niż minuta'
            desc=r['lead']
            try:
                img=r['image']['url'].format(width=r['image']['width'],height=r['image']['height'])
            except:
                img=img_path+'tvp.png'
            
            plot=''
            plot+='[B]Data publikacji: [/B]%s\n'%(date)
            plot+='[B]Długość: [/B]%s\n'%(dur)
            if desc!=None and desc!='':
                plot+=self.cleanText(desc)
            
            iL={'title': title,'sorttitle': '','plot': plot}
            setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart': ''}
            URL = base.build_url({'mode':'playProg','asset_id':str(vid)})
            base.addItemList(URL, title, setArt, 'video', iL, False, 'true')
        else: 
            return
        
    def videoList(self,portal,cid,page): #TVP INFO
        limit=100
        url=self.getApiUrl(portal)+'list?device=www&id='+cid+'&page='+page+'&limit='+str(limit)
        resp=requests.get(url,headers=hea).json()
        for r in resp['data']['items']:
            self.addItemToList(r)
            
        total=resp['data']['total_count']
        if int(page)*limit+len(resp['data']['items'])<total:
            setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_path+'empty.png', 'fanart': ''}
            url_cont = base.build_url({'mode':'videoList','portal':portal,'cid':cid,'page':str(int(page)+1)})
            base.addItemList(url_cont, '[B][COLOR=yellow]>>> Następna strona[/COLOR][/B]', setArt,'video')
                    
        xbmcplugin.setContent(addon_handle, 'videos')
        xbmcplugin.endOfDirectory(addon_handle)
        
    def categsListSport(self,portal,cid,subMain=None): #TVP SPORT
        if subMain==None:
            url=self.getApiUrl(portal)+'www/directory/list?direct=true&sort=position,1&limit=30&id='+cid
        else:
            url=self.getApiUrl(portal)+'www/block/list?device=www&id='+cid
        resp=requests.get(url,headers=hea).json()
        if subMain!=None and len(resp['data']['items'])==1: #jedna podkategoria-->pominięcie listy podkategorii
            r=resp['data']['items'][0]
            ccid=str(r['_id'])
            count=str(r['params']['limit'])
            self.videoListSport(portal,ccid,'1',count)
            return
        for r in resp['data']['items']:
            ccid=str(r['_id'])
            if subMain==None:
                title=r['title']
                URL=base.build_url({'mode':'categsListSport','portal':portal,'cid':ccid,'subMain':'true'})
            else:
                title=r['params']['title']
                count=str(r['params']['limit'])
                URL=base.build_url({'mode':'videoListSport','portal':portal,'cid':ccid,'page':'1','count':count})
            
            setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': 'DefaultAddonVideo.png', 'fanart': ''}
            base.addItemList(URL, title, setArt)
        
        xbmcplugin.endOfDirectory(addon_handle)

    def videoListSport(self,portal,cid,page,count): #TVP SPORT
        url=self.getApiUrl(portal)+'www/block/items?device=www&id='+cid
        if page!='1':
            url+='&page='+page
        resp=requests.get(url,headers=hea).json()
        for r in resp['data']['items']:
            self.addItemToList(r)
        if len(resp['data']['items'])==int(count):
            setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_path+'empty.png', 'fanart': ''}
            url_cont = base.build_url({'mode':'videoListSport','portal':portal,'cid':cid,'page':str(int(page)+1),'count':count})
            base.addItemList(url_cont, '[B][COLOR=yellow]>>> Następna strona[/COLOR][/B]', setArt,'video')
                    
        xbmcplugin.setContent(addon_handle, 'videos')
        xbmcplugin.endOfDirectory(addon_handle)
    