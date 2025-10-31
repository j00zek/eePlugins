import os
import sys

import requests
from emukodi import xbmc
from emukodi import xbmcgui
from emukodi import xbmcplugin
from emukodi import xbmcaddon
from emukodi import xbmcvfs
import json
import time
import datetime
import re
from urllib.parse import urlencode, quote_plus, quote, unquote, parse_qsl
from .base import b

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
base=b(base_url,addon_handle)

addon = base.addon
PATH=addon.getAddonInfo('path')
img_path=PATH+'/resources/images/'
img_inne='https://hbb-prod.tvp.pl/apps/manager/_nuxt/img/b1966b153d6da55d855eb3ce3966dce3.png'

baseurl='http://hbbtest.v3.tvp.pl/hub_oryg/index_tvp_stream.php' #'https://hbb-prod.tvp.pl/apps/manager/hub/?name_channel=MUX3_TVP1_HD'
api_hbbtv='https://hbb-prod.tvp.pl/apps/manager/api/hub/graphql'

heaTV={
    'User-Agent':base.UA,
    'Referer':baseurl
}
hea_oth={
    'User-Agent':base.UA
}

menu_TV=[
    ['Kanały na żywo','liveTV'],
    ['Replay TV','replayTV'],
    ['Replay TV (new)','listTV'],
]

class tvpGo:
    def __init__(self, livePlayerType, streamTvProtocol, cuOffset):
        self.livePlayerType=livePlayerType
        self.streamTvProtocol=streamTvProtocol
        self.cuOffset=cuOffset
        self.stations={
            'TVP1':{'code':'T1D', 'cid':'51689486','catchup':'y','img':'http://s8.tvp.pl/images2/8/a/c/uid_8ac2b72c379abf831e4d27a56988eae11638275540325{imgURL}','tvpgo_hbb':'y'},
            'TVP2':{'code':'T2D', 'cid':'51696811','catchup':'y','img':'http://s3.tvp.pl/images2/3/8/3/uid_38313bd81e2ec78f92fa8d360e738b921638275558292{imgURL}','tvpgo_hbb':'y'},
            'TVP Info':{'code':'INF', 'cid':'51696820','catchup':'y','img':'http://s4.tvp.pl/images2/4/a/d/uid_4ad77ef5d9314477a07a2372b0bc10a9{imgURL}','tvpgo_hbb':'y'}, 
            'TVP NAUKA':{'code':'NK', 'cid':'71345993','catchup':'y','img':'http://s5.tvp.pl/images2/e/3/a/uid_e3a95bba0e16e0eed0e5fd59229cfbd01663860050881{imgURL}','tvpgo_hbb':'y'},#62975271
            'TVP Sport':{'code':'KSP', 'cid':'51696827','catchup':'y','img':'http://s9.tvp.pl/images2/9/6/b/uid_96b6b3e217181c3d3925ba783fe68a131638275633849{imgURL}','tvpgo_hbb':'y'},
            'TVP Kultura':{'code':'T5D', 'cid':'51696822','catchup':'y','img':'http://s9.tvp.pl/images2/9/6/1/uid_96117b8fceb8a7db897a9757240316451638275727542{imgURL}','tvpgo_hbb':'y'},
            'TVP Historia':{'code':'TKH', 'cid':'51696819','catchup':'y','img':'http://s4.tvp.pl/images2/d/5/e/uid_d5e250a46a37955df5b33847a1f661921638275686065{imgURL}','tvpgo_hbb':'y'},
            'TVP ABC':{'code':'ABC', 'cid':'51696812','catchup':'y','img':'http://s5.tvp.pl/images2/5/c/8/uid_5c8ba79e2229bf9909ffa4ea9907595e1638275665760{imgURL}','tvpgo_hbb':'y'},
            'Alfa TVP':{'code':'ALFA', 'cid':'65184034','catchup':'n','img':'http://s6.tvp.pl/images2/6/0/0/uid_6008af70ab882fa088c7f00ec2f640271671613962973{imgURL}','tvpgo_hbb':'y'},
            'TVP Dokument':{'code':'DOK','cid':'53795159','catchup':'y','img':'http://s1.tvp.pl/images2/a/f/1/uid_af1b5529d584f3e6dc893021b38901971638275709609{imgURL}','tvpgo_hbb':'y'},
            'TVP Kobieta':{'code':'KBT','cid':'53795158','catchup':'y','img':'http://s3.tvp.pl/images2/3/6/2/uid_362ac36e5828f7e25f5e5d028b7abb7b1638275648497{imgURL}','tvpgo_hbb':'y'},
            'TVP Polonia':{'code':'T4D','cid':'51696824','catchup':'y','img':'http://s5.tvp.pl/images2/e/7/b/uid_e7b9ee2c3a342e7b97eda1b96e48808d1638275742066{imgURL}','tvpgo_hbb':'y'},
            'TVP Rozrywka':{'code':'TRO','cid':'51696825','catchup':'y','img':'http://s9.tvp.pl/images2/9/6/4/uid_9647031d5810bf7b78b1a9f30904468c1638275757901{imgURL}','tvpgo_hbb':'y'},
            'TVP World':{'code':'PIE','cid':'57181932','catchup':'n','img':'http://s6.tvp.pl/images2/6/6/e/uid_66ec3a95ffbb04ac674efd2a8ba2e4631637224384316{imgURL}','tvpgo_hbb':'y'},
            'TVP Kultura 2':{'code':'KUL2','cid':'56275381','catchup':'n','img':'http://s9.tvp.pl/images2/9/a/b/uid_9ab326a136b5dd5ff06262155bcc02ca1607116286623{imgURL}','tvpgo_hbb':'y'},
            'TVP ABC 2':{'code':'DMPR','cid':'57181933','catchup':'n','img':'http://s3.tvp.pl/images2/c/d/2/uid_cd2dd2eb58a62fa3571592bd8a61ad2c1644934718964{imgURL}','tvpgo_hbb':'y'},
            'TVP Historia 2':{'code':'H2','cid':'57181934','catchup':'n','img':'http://s7.tvp.pl/images2/7/f/2/uid_7f29c7a0db297706c9a0ff4e625572221614186561005{imgURL}','tvpgo_hbb':'y'},    
            'TVP3 Białystok':{'code':'XCC','cid':'71345939','catchup':'y','img':'http://s2.tvp.pl/images2/b/1/9/uid_b19c0fe3d69594dc055a76bd316148d71566388357439{imgURL}','tvpgo_hbb':'y'},
            'TVP3 Bydgoszcz':{'code':'XBB','cid':'71345962','catchup':'y','img':'http://s5.tvp.pl/images2/5/e/9/uid_5e9126648da6925f4fe771d02eae724c1566388527267{imgURL}','tvpgo_hbb':'y'},
            'TVP3 Gdańsk':{'code':'XGG','cid':'71345915','catchup':'y','img':'http://s1.tvp.pl/images2/1/6/e/uid_16ef2e3899aa0f6a86bab4e7d4ad7acb1566388553274{imgURL}','tvpgo_hbb':'y'},
            'TVP3 Gorzów Wielkopolski':{'code':'XFF','cid':'71345976','catchup':'y','img':'http://s9.tvp.pl/images2/9/a/6/uid_9a63db7e7850c553fd5f99ef4a4764bf1566388710402{imgURL}','tvpgo_hbb':'y'},
            'TVP3 Katowice':{'code':'XTT','cid':'71345996','catchup':'y','img':'http://s1.tvp.pl/images2/a/7/0/uid_a7082896b3af87dee93a7e82f4574aea1566388722532{imgURL}','tvpgo_hbb':'y'},
            'TVP3 Kielce':{'code':'XEE','cid':'71345997','catchup':'y','img':'http://s6.tvp.pl/images2/f/a/a/uid_faa42ba4b4a31b226a2f1da99e1ac56d1566388734756{imgURL}','tvpgo_hbb':'y'},
            'TVP3 Kraków':{'code':'XKK','cid':'71346000','catchup':'y','img':'http://s6.tvp.pl/images2/f/e/7/uid_fe765a5a9a4f710c1e73ca72d57dcfb41566388748581{imgURL}','tvpgo_hbb':'y'},
            'TVP3 Lublin':{'code':'XLL','cid':'71346005','catchup':'y','img':'http://s2.tvp.pl/images2/2/c/3/uid_2c30eb4d856d156d025168f37a072a241566388774571{imgURL}','tvpgo_hbb':'y'},
            'TVP3 Łódź':{'code':'XDD','cid':'71345979','catchup':'y','img':'http://s8.tvp.pl/images2/8/d/a/uid_8daf45383144552ab0a791a45dea90691566388793484{imgURL}','tvpgo_hbb':'y'},
            'TVP3 Olsztyn':{'code':'XHH','cid':'71346007','catchup':'y','img':'http://s9.tvp.pl/images2/9/9/2/uid_9923ae9c5aa8a9089a9f8034651c5d9c1566388829799{imgURL}','tvpgo_hbb':'y'},
            #'TVP3 Olsztyn/Elbląg':{'code':'XHH','cid':'62977634','catchup':'y','img':'http://s9.tvp.pl/images2/9/9/2/uid_9923ae9c5aa8a9089a9f8034651c5d9c1566388829799{imgURL}','tvpgo_hbb':'n'},#slot usunięty z api
            'TVP3 Opole':{'code':'XJJ','cid':'71346013','catchup':'y','img':'http://s4.tvp.pl/images2/4/1/1/uid_411f024dee7040009307c76894fdb19c1566389096981{imgURL}','tvpgo_hbb':'y'},
            'TVP3 Poznań':{'code':'XPP','cid':'71346014','catchup':'y','img':'http://s4.tvp.pl/images2/d/e/3/uid_de3a8c5ef41e6cc72874d0769b392c731566388858694{imgURL}','tvpgo_hbb':'y'},
            'TVP3 Rzeszów':{'code':'XRR','cid':'71346017','catchup':'y','img':'http://s10.tvp.pl/images2/0/5/f/uid_05ffe9f2c1085affb565b3539443df431566388871032{imgURL}','tvpgo_hbb':'y'},
            'TVP3 Szczecin':{'code':'XSS','cid':'71345990','catchup':'y','img':'http://s5.tvp.pl/images2/5/1/0/uid_5100b76fed6bea98077a74a5d85a20d81566388884052{imgURL}','tvpgo_hbb':'y'},
            'TVP3 Warszawa HD':{'code':'XAA','cid':'71345991','catchup':'y','img':'http://s4.tvp.pl/images2/d/6/e/uid_d6ef379170d95c5d3d84c872b09a0cad1566388902716{imgURL}','tvpgo_hbb':'y'},
            'TVP3 Wrocław':{'code':'XWW','cid':'71346019','catchup':'y','img':'http://s4.tvp.pl/images2/d/6/e/uid_d6e43f98434ee3b9ce0848e83d26e5f81566388918436{imgURL}','tvpgo_hbb':'y'},
            'TVP Parlament Sejm':{'code':'PARSEJM','cid':'75458913','catchup':'n','img':'https://s7.tvp.pl/images2/7/c/f/uid_7cfce7f50ce4470f9867158038e110cd{imgURL}','tvpgo_hbb':'n'},#png do podmiany #16047033
            'TVP Parlament Senat':{'code':'PARSENAT','cid':'75458927','catchup':'n','img':'https://s6.tvp.pl/images2/f/0/2/uid_f02bc9a37a4d4001b5d49f8b30a60a68{imgURL}','tvpgo_hbb':'n'},#png do podmiany #16047033
            'TVP Parlament Komisja 1':{'code':'','cid':'75458936','catchup':'n','img':'http://s3.tvp.pl/images2/c/d/3/uid_cd316e49c8185069f085884fb881f0f51448633997759{imgURL}','tvpgo_hbb':'n'},#16047097
            'TVP Parlament Komisja 2':{'code':'','cid':'75458957','catchup':'n','img':'http://s6.tvp.pl/images2/f/d/9/uid_fd9c7b1a21511f29d8cedeba544e16a11448634093730{imgURL}','tvpgo_hbb':'n'},#16047099
            'TVP Wilno':{'code':'WILNO','cid':'61881035','catchup':'n','img':'http://s3.tvp.pl/images2/3/7/2/uid_37273101aabbe28f9f6e62d62ca3dc201568710101823{imgURL}','tvpgo_hbb':'n'},#44418594
            'TVP Wilno':{'code':'WILNO','cid':'74979895','catchup':'n','img':'http://s3.tvp.pl/images2/3/7/2/uid_37273101aabbe28f9f6e62d62ca3dc201568710101823{imgURL}','tvpgo_hbb':'y'},#44418594
            #'Jasna Góra':{'code':'','cid':'53415775','catchup':'n','img':'https://s10.tvp.pl/images2/0/0/5/uid_00525b67452c04a9eb6aa0e32d4888fc1619004489426{imgURL}','tvpgo_hbb':'n'},
            'Belsat':{'code':'TVBI','cid':'17251711','catchup':'n','img':'http://s9.tvp.pl/images2/9/4/d/uid_94daec69fb7046226f9c42ad28c8f7251638805351087{imgURL}','tvpgo_hbb':'y'},
            'UA1':{'code':'UA1','cid':'58758689','catchup':'n','img':'http://s2.tvp.pl/images2/2/2/e/uid_22e0d031662761cdeb669c49b31738b81645961764558{imgURL}','tvpgo_hbb':'y'},
            'TVP Seriale':{'code':'TRS','cid':'72827372','catchup':'n','img':'https://s.tvp.pl/images/images/e/c/3/uid_ec3fc6856ea9427db7a6a84802b31512{imgURL}','tvpgo_hbb':'y'},
            'TVP HD':{'code':'KHSH','cid':'72827367','catchup':'n','img':'http://s.tvp.pl/images/images/4/d/d/uid_4dd65f81dbb546228ec23986d5434903{imgURL}','tvpgo_hbb':'y'},
        }
    
        self.protocols={'HLS':'hls','DASH':'mpd'}
        self.mimeTypes={'HLS':'application/x-mpegurl','DASH':'application/dash+xml'}

    def findStByCode(self,stCode): #helper
        result=None
        if stCode!=None:
            st=[l for l in list(self.stations) if self.stations[l]['code']==stCode]
            if len(st)>0:
                result=st[0]
        
        return result
    
    def virtChan(self): #virtual channel z TVP GO apk
        url='https://sport.tvp.pl/api/tvp-stream/program-tv/stations?device=android'
        resp=requests.get(url,headers=hea_oth).json()
        try:
            virtChans=[[d['code'],d['name'],d['image']['url'].format(width='510',height='0'),'vc_'+d['code']] for d in resp['data'] if d['stream_type']=='VIRTUAL_CHANNEL']
        except:
            virtChans=[]
            
        return virtChans
        
    def vc_cid(self,vc_code):
        url='https://sport.tvp.pl/api/tvp-stream/stream/data?station_code='+vc_code.replace('vc_','')+'&device=android'
        resp=requests.get(url,headers=hea_oth).json()
        if resp['error']==None:
            try:
                cid=resp['data']['stream_url'].split('?')[0].split('/')[-1]
            except:
                cid=''
        return cid
        
    def playerISA(self,url,protocol,live=True,fromStart=True):
        xbmc.log('@@@stream_url: '+url, level=xbmc.LOGINFO)
        p={'hls':'application/x-mpegurl','mpd':'application/xml+dash'}

        if protocol=='hls':
            proxyport = addon.getSetting('proxyport')
            url='http://127.0.0.1:%s/MANIFEST='%(str(proxyport))+url
        
        import inputstreamhelper
        PROTOCOL = protocol#hls,mpd
        is_helper = inputstreamhelper.Helper(PROTOCOL)
        if is_helper.check_inputstream():
            play_item = xbmcgui.ListItem(path=url)
            play_item.setMimeType(p[protocol])
            play_item.setContentLookup(False)
            play_item.setProperty('inputstream', is_helper.inputstream_addon)
            play_item.setProperty("IsPlayable", "true")
            if not live and fromStart==True:
                play_item.setProperty('ResumeTime', '1')
                play_item.setProperty('TotalTime', '1')
            play_item.setProperty('inputstream.adaptive.stream_headers', 'User-Agent='+base.UA)
            play_item.setProperty('inputstream.adaptive.manifest_headers', 'User-Agent='+base.UA)#K21
            play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)

        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
    

    def getCurProg(self,code): #helper
        now=int(time.time())
        date=self.fromTstmptoStr(now,'%Y-%m-%d')
        url='http://www.api.v3.tvp.pl/shared/programtv-listing.php?station_code='+code+'&count=1000&dump=json&today_from_midnight=1&date='+date
        resp=requests.get(url,headers=hea_oth).json()
        prog=[p['date_start']/1000 for p in resp['items'] if p['date_start']<=now*1000 and p['date_end']>now*1000]
        p=prog[0] if len(prog)>0 else None
        
        return p

    def fromTstmptoStr(self,x,f,t=None): #helper
        if t=='utc':
            return datetime.datetime.utcfromtimestamp(x).strftime(f)
        else:
            return datetime.datetime.fromtimestamp(x).strftime(f)    

       
    def menuTV(self):
        for m in menu_TV:    
            img=img_path+'tvp_go.png'
            setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart': ''}
            url = base.build_url({'mode':m[1]})
            base.addItemList(url, m[0], setArt)    
        xbmcplugin.endOfDirectory(addon_handle)

    def channelArrayGen(self):#JSON-live channel list
        #2024-02-01
        strin='{"operationName":"landingPageVideos","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"8865dec5b5d336e09aac0856e2b8c21b7392eaa79b17b178b94efdc21e8382d3"}},"query":"query landingPageVideos {\\n  landingPageVideos {\\n    ... on DriverDataLandingPageVideos {\\n      types {\\n        default\\n        __typename\\n      }\\n      title\\n      elements {\\n        id\\n        type\\n        titles {\\n          main\\n          sub\\n          __typename\\n        }\\n        img {\\n          videoHolders {\\n            _16x9\\n            __typename\\n          }\\n          website {\\n            holder_16x9\\n            __typename\\n          }\\n          hbbtv\\n          image\\n          __typename\\n        }\\n        labels {\\n          ... on Expiring {\\n            type\\n            text\\n            __typename\\n          }\\n          ... on PEGILabel {\\n            type\\n            text\\n            __typename\\n          }\\n          ... on PayableOrCatchup {\\n            type\\n            text\\n            __typename\\n          }\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    ... on ListingDataLandingPageVideos {\\n      types {\\n        default\\n        __typename\\n      }\\n      title\\n      elements {\\n        id\\n        type\\n        img {\\n          videoHolders {\\n            _16x9\\n            __typename\\n          }\\n          website {\\n            holder_16x9\\n            __typename\\n          }\\n          hbbtv\\n          image\\n          __typename\\n        }\\n        labels {\\n          ... on Expiring {\\n            type\\n            text\\n            __typename\\n          }\\n          ... on PEGILabel {\\n            type\\n            text\\n            __typename\\n          }\\n          ... on PayableOrCatchup {\\n            type\\n            text\\n            __typename\\n          }\\n          __typename\\n        }\\n        countVideos {\\n          default\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    ... on CategoriesDataLandingPageVideos {\\n      type\\n      title\\n      elements {\\n        title\\n        id\\n        types {\\n          default\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n  stationsForMainpage {\\n    id\\n    name\\n    code\\n    image_square {\\n      url\\n      __typename\\n    }\\n    background_color\\n    __typename\\n  }\\n}\\n"}'
        data=json.loads(strin)
        resp=requests.post(api_hbbtv,json=data,headers=heaTV).json()
        if 'errors' not in resp:
            ch_data=resp['data']['stationsForMainpage']
            ar_chan=[]
            for c in ch_data:
                ch_code=c['code']
                ch_name=c['name'].replace('EPG - ','').replace('Domowe Przedszkole','ABC 2')
                ch_img=unquote(c['image_square']['url']).format(width='510',height='0')
                ch_id=''
                ar_chan.append([ch_code,ch_name,ch_img,ch_id])
        else:
            ar_chan=[]
            channels=list(self.stations.keys())
            for c in channels:
                if self.stations[c]['tvpgo_hbb']=='y':
                    code=self.stations[c]['code']
                    img=self.stations[c]['img'].format(imgURL='_width_510_play_0_pos_0_gs_0_height_0.png')
                    cid=''
                    ar_chan.append([code,c,img,cid])
        
        ar_new=[ #braki w TVP GO ver. HbbTV
            ['','TVP Parlament KOMISJA 1','https://s.tvp.pl/files/tvp-parlament/gfx/logo/tvp-parlament.png','aid_75458936'],#16047097
            ['','TVP Parlament KOMISJA 2','https://s.tvp.pl/files/tvp-parlament/gfx/logo/tvp-parlament.png','aid_75458957'],#16047099
            ['TRS','TVP Seriale','https://s.tvp.pl/images/images/e/c/3/uid_ec3fc6856ea9427db7a6a84802b31512_width_510_play_0_pos_0_gs_0_height_0.png','aid_72827372'],
            ['KHSH','TVP HD','http://s.tvp.pl/images/images/4/d/d/uid_4dd65f81dbb546228ec23986d5434903_width_510_play_0_pos_0_gs_0_height_0.png','aid_72827367'],            
        ]
        ar_chan+=ar_new
        
        #uzupełnienie o kanały wirtualne z TVPGO apk
        ar_chan+=self.virtChan()
        
        return ar_chan

    def channels_gen(self,):#menu-live channel list
        channels=self.channelArrayGen()
        for ch in channels:        
            iL={'title': ch[1],'sorttitle': ch[1],'plot': 'EPG dostępne z poziomu menu kontekstowego'}
            setArt={'thumb': ch[2], 'poster': ch[2], 'banner': ch[2], 'icon': ch[2], 'fanart': ch[2]}
            url = base.build_url({'mode':'playLiveTV','chCode':ch[0],'chID':ch[3]})
            if ch[0]!='':
                CM=True
                cmItems=[('[B]EPG[/B]','RunPlugin(plugin://plugin.video.TVP_VOD?mode=EPG&stCode='+ch[0]+')')]
            else:
                CM=True
                cmItems=[]
            base.addItemList(url, ch[1], setArt, 'video', iL, False, 'true', CM, cmItems)
        xbmcplugin.endOfDirectory(addon_handle)

    def PlayStream(self,chCode,chId,s=None,e=None):#play live channel
        protocol=self.protocols[self.streamTvProtocol]
        mimeType=self.mimeTypes[self.streamTvProtocol]
        
        def toSC(url_stream): #SimpleClient catchup
            co=int(self.cuOffset)
            s1=(datetime.datetime(*(time.strptime(s,'%Y%m%dT%H%M%S')[0:6]))+datetime.timedelta(hours=co)).strftime('%Y%m%dT%H%M%S')
            e1=(datetime.datetime(*(time.strptime(e,'%Y%m%dT%H%M%S')[0:6]))+datetime.timedelta(hours=co)).strftime('%Y%m%dT%H%M%S')
            url_stream=url_stream.split('?')[0]+'?end='+e1+'&begin='+s1 #end=20231219T041500&begin=20231219T035000
            
            if self.livePlayerType=='ISA':
                self.playerISA(url_stream,protocol,False,True)
            else:
                #base.directPlayer(url_stream)
                base.ISffmpegPlayer(protocol,url_stream)
        
        def streamUrlGen(cid,chCode=None): #tokenizer korzystający z channel_id
            url='https://token-java-v2.tvp.pl/tokenizer/token/'+cid
            resp=requests.get(url,headers=hea_oth).json()
            if "NOT_PLAYABLE" not in resp['status']:                
                streams_ar=[s['url'] for s in resp['formats'] if s['mimeType']==mimeType]
                if len(streams_ar)>0:
                    url_stream=streams_ar[0]
                    if chCode!=None and self.livePlayerType=='ISA' and protocol!='mpd': #zatrzymanie odtwarzania gdy manifest MPD ma znacznik begin
                        station=self.findStByCode(chCode)
                        if station!=None and self.stations[station]['catchup']=='y':
                            tstart=self.getCurProg(chCode)
                            if tstart!=None:
                                url_stream+='?begin='+self.fromTstmptoStr(tstart,'%Y%m%dT%H%M%S','utc')
                            
                
                if s!=None and e!=None: #SimpleClient catchup
                    toSC(url_stream)
                else:
                    if self.livePlayerType=='ISA':
                        self.playerISA(url_stream,protocol)
                    else:
                        #base.directPlayer(url_stream)
                        base.ISffmpegPlayer(protocol,url_stream)
            else:
                xbmcgui.Dialog().notification('TVP_VOD', 'Przerwa w emisji', xbmcgui.NOTIFICATION_INFO)
                xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
        
        if chCode!=None and chId==None:                
            #2024-02-01
            strin='{"operationName":"currentProgramAsLive","variables":{"code_station":"'+chCode+'"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"c44e45d19ebab8a5b0778b42d44ffa1fcca031f0a9b8720d1712df1081f163ff"}},"query":"query currentProgramAsLive($code_station: String!) {\\n  currentProgramAsLive(code_station: $code_station) {\\n    occurrence {\\n      ... on NotFastOccurrenceResponseCurrentProgramAsLive {\\n        id\\n        title\\n        date_start\\n        date_end\\n        description\\n        description_long\\n        pegi\\n        description_akpa\\n        description_akpa_medium\\n        description_akpa_long\\n        station {\\n          npvr\\n          fast\\n          __typename\\n        }\\n        program {\\n          title\\n          __typename\\n        }\\n        akpa_attributes\\n        __typename\\n      }\\n      __typename\\n    }\\n    date_current\\n    video {\\n      ... on VideoFromTokenizerWithoutDebugInfo {\\n        title\\n        formats {\\n          mime_type\\n          url\\n          __typename\\n        }\\n        __typename\\n      }\\n      ... on VideoFromTokenizerWithDebugInfo {\\n        title\\n        formats {\\n          mime_type\\n          url\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'
            data=json.loads(strin)
            resp=requests.post(api_hbbtv,json=data,headers=heaTV).json()
            if 'errors' in resp:
                #alternatywa gdy api TVP GO HbbTV nie dostarcza url strumienia
                cids=[self.stations[s]['cid'] for s in list(self.stations.keys()) if self.stations[s]['code']==chCode]
                if len(cids)>0:
                    streamUrlGen(cids[0])
                else:
                    xbmcgui.Dialog().notification('TVPGO', 'Przerwa w emisji', xbmcgui.NOTIFICATION_INFO)
                    xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
            elif resp['data']['currentProgramAsLive'] is not None:
                streams=resp['data']['currentProgramAsLive']['video']['formats']
                streamsByType=[s['url'] for s in streams if s['mime_type']==mimeType ]
                if len(streamsByType)>0:
                    url_stream=streamsByType[0]
                    if protocol=='mpd': #zatrzymanie odtwarzania gdy manifest MPD ma znacznik begin
                        url_stream=url_stream.split('?')[0]
                
                if s!=None and e!=None: #SimpleClient catchup
                    toSC(url_stream)
                else:
                    if self.livePlayerType=='ISA':
                        self.playerISA(url_stream,protocol)
                    else:
                        #base.directPlayer(url_stream)
                        base.ISffmpegPlayer(protocol,url_stream)
            else:
                xbmcgui.Dialog().notification('TVPGO', 'Przerwa w emisji', xbmcgui.NOTIFICATION_INFO)
                xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
        else:
            url_stream=''
            cid=''
            if 'aid' in chId:
                cid=chId.split('aid_')[-1]
                
            elif 'vc' in chId:
                cid=self.vc_cid(chId)

            if cid !='':
                #new=True if 'new' in chId else False
                streamUrlGen(cid,chCode)               

            else:
                xbmcgui.Dialog().notification('TVP_VOD', 'Brak źródła', xbmcgui.NOTIFICATION_INFO)
                xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())

    def replayChannelsArrayGen(self): #JSON: replay channels
        #2024-02-01
        strin='{"operationName":"stations","variables":{"filters":{"fast":true}},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"a74161f0c3105006a1dde621c533d3a2b7d078ebdceade36014d034ded65d9d3"}},"query":"query stations($filters: InputFiltersStations, $forces: InputForcesStations) {\\n  stations(filters: $filters, forces: $forces) {\\n    name\\n    code\\n    image_square {\\n      url\\n      __typename\\n    }\\n    background_color\\n    __typename\\n  }\\n}\\n"}'
        data=json.loads(strin)
        resp=requests.post(api_hbbtv,json=data,headers=heaTV).json()
        ch_data=resp['data']['stations']
        ar_chan=[]
        for ch in ch_data:
            if ch['code'] in [self.stations[s]['code'] for s in list(self.stations.keys()) if self.stations[s]['catchup']=='y']:
                chName=ch['name']
                chCode=ch['code']
                img=unquote(ch['image_square']['url']).format(width='510',height='0')
                ar_chan.append([chName,chCode,img])

        ar_new=[
            #['TVP3 Olsztyn/Elbląg','XHHE','http://s9.tvp.pl/images2/9/9/2/uid_9923ae9c5aa8a9089a9f8034651c5d9c1566388829799_width_510_play_0_pos_0_gs_0_height_0.png'],
        ]
        ar_chan+=ar_new
        
        return ar_chan

    def replayChannelsGen(self):#menu-replay channel list
        channels=self.replayChannelsArrayGen()
        for ch in channels:        
            code=ch[1]
            img=ch[2]
            
            iL={'title': ch[0],'sorttitle': ch[0],'plot': ''}
            setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart': ''}
            url = base.build_url({'mode':'replayTVdate','chCode':ch[1]})
            base.addItemList(url, ch[0], setArt, infoLab=iL)    
        xbmcplugin.endOfDirectory(addon_handle)

    def replayCalendarGen(self,chCode):#kalendarz
        now=datetime.datetime.now()
        ar_date=[]
        for i in range(0,8):
            date=(now-datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            ar_date.append(date)
        
        for d in ar_date:   
            iL={'title': d,'sorttitle': d,'plot': ''}
            setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': 'DefaultYear.png', 'fanart': ''}
            url = base.build_url({'mode':'replayTVprogs','date':d,'chCode':chCode})
            base.addItemList(url, d, setArt, infoLab=iL) 
        xbmcplugin.endOfDirectory(addon_handle)

    def replayProgramsGen(self,chCode,date):#menu-replay program list
        #2024-02-01
        strin='{"operationName":"occurrencesProgramTV","variables":{"code_station":"'+chCode+'","category":"","date":"'+date+'","include_images":true},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"df8faf4caa3f1915447315bb56a103ea8813e15d4c60babb808e2c674e325caf"}},"query":"query occurrencesProgramTV($code_station: String, $date: Date, $category: String, $include_images: Boolean) {\\n  occurrencesProgramTV(\\n    code_station: $code_station\\n    date: $date\\n    category: $category\\n    include_images: $include_images\\n  ) {\\n    total_count\\n    items {\\n      ... on NotFastItemResponseGetOccurrencesProgramTV {\\n        id\\n        record_id\\n        title\\n        date_start\\n        date_end\\n        duration\\n        code_station\\n        description\\n        description_long\\n        program {\\n          id\\n          type\\n          title\\n          year\\n          lang\\n          image {\\n            type\\n            title\\n            point_of_origin\\n            url\\n            width\\n            height\\n            description\\n            __typename\\n          }\\n          program_type {\\n            id\\n            type\\n            title\\n            __typename\\n          }\\n          cycle {\\n            id\\n            type\\n            title\\n            image_logo {\\n              type\\n              title\\n              point_of_origin\\n              url\\n              width\\n              height\\n              description\\n              __typename\\n            }\\n            __typename\\n          }\\n          rating\\n          website_id\\n          has_video_vod\\n          cms_id\\n          __typename\\n        }\\n        station {\\n          id\\n          name\\n          code\\n          image {\\n            type\\n            title\\n            point_of_origin\\n            url\\n            width\\n            height\\n            description\\n            __typename\\n          }\\n          image_square {\\n            type\\n            title\\n            point_of_origin\\n            url\\n            width\\n            height\\n            description\\n            __typename\\n          }\\n          background_color\\n          fast\\n          __typename\\n        }\\n        url\\n        url_canonical\\n        categories {\\n          id\\n          category_type\\n          title\\n          __typename\\n        }\\n        akpa_attributes\\n        pegi\\n        description_akpa\\n        description_akpa_medium\\n        description_akpa_long\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'
        data=json.loads(strin)
        resp=requests.post(api_hbbtv,json=data,headers=heaTV).json()
        ar_prog=[]
        if 'errors' not in resp:
            pr_data=resp['data']['occurrencesProgramTV']['items']
            time_now=int(time.time())*1000
            def hm(t):
                return datetime.datetime.fromtimestamp(t/1000).strftime('%H:%M')
            def dt(t):
                return datetime.datetime.fromtimestamp(t/1000).strftime('%Y-%m-%d')
            for p in pr_data:
                if p['date_start']<time_now and p['date_end']>time_now-8*24*60*60*1000:#7
                    pID=p['record_id']
                    pTitle='[B]'+hm(p['date_start'])+'[/B]  '+p['title']
                    pDescr=p['description']
                    try:
                        img=unquote(p['program']['image']['url']).replace('{width}','608').replace('{height}','342')
                    except:
                        img=img_inne
                    if p['program']!=None:
                        progType=p['program']['program_type']['title'] if p['program']['program_type']!=None else None
                        year=p['program']['year'] if 'year' in p['program'] else None
                    else:
                        progType=None
                        year=None
                    blackout=True if 'InternetStreamDisabled' in p['akpa_attributes'] or 'catchUpDisabled' in p['akpa_attributes'] else False
                                            
                    plot=''
                    if progType !=None:
                        plot+='[B]'+progType+'[/B]\n'
                    if blackout==True:
                        plot+='[COLOR=yellow]Niedostępny z powodu ograniczeń licencyjnych[/COLOR]\n'
                        progTitle='[COLOR=red]'+pTitle+'[/COLOR]'
                    else:
                        progTitle=pTitle
                    if pDescr !=None:
                        plot+=pDescr+'\n'
                    if year !=None:
                        plot+='[B]Rok prod.: '+str(year)+'[/B]'
                            
                    title=[s for s in list(self.stations.keys()) if self.stations[s]['code']==chCode][0]+' | ' 
                    title+=dt(p['date_start'])+' '+progTitle
                
                    iL={'title': pTitle,'sorttitle': pTitle,'plot': plot}
                    setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img, 'fanart': ''}
                    url = base.build_url({'mode':'playReplayTV','chCode':chCode,'progID':pID})
                    cmItems=[('[B]Dodaj do ulubionych[/B]','RunPlugin(plugin://plugin.video.TVP_VOD?mode=favExtAdd&url='+quote(url)+'&title='+quote(title)+'&infoLab='+quote(str(iL))+'&img='+quote(img)+')')]
                    base.addItemList(url, progTitle, setArt, 'video', iL, False, 'true', True, cmItems)
        
        xbmcplugin.setContent(addon_handle, 'videos')
        xbmcplugin.endOfDirectory(addon_handle)

    def PlayProgram(self,chCode,progID):#play program
        #2024-02-01
        strin='{"operationName":"programByRecordID","variables":{"id":"'+progID+'","code_station":"'+chCode+'"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"92a1625f33134e6a12483dd86b82bf873354c71e8aef41d56ad0a17aa2d52402"}},"query":"query programByRecordID($id: ID!, $code_station: String!) {\\n  programByRecordID(id: $id, code_station: $code_station) {\\n    occurrence {\\n      ... on NotFastResponseOccurrenceProgramTV {\\n        id\\n        title\\n        date_start\\n        date_end\\n        description\\n        description_long\\n        description_akpa_long\\n        description_akpa_medium\\n        description_akpa\\n        pegi\\n        __typename\\n      }\\n      __typename\\n    }\\n    stream {\\n      code_station\\n      ids {\\n        occurrence\\n        record\\n        __typename\\n      }\\n      urls {\\n        vast\\n        stream\\n        __typename\\n      }\\n      __typename\\n    }\\n    date_current\\n    video {\\n      ... on VideoFromTokenizerWithoutDebugInfo {\\n        title\\n        formats {\\n          mime_type\\n          url\\n          __typename\\n        }\\n        __typename\\n      }\\n      ... on VideoFromTokenizerWithDebugInfo {\\n        title\\n        formats {\\n          mime_type\\n          url\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'
        data=json.loads(strin)
        resp=requests.post(api_hbbtv,json=data,headers=heaTV).json()
        if 'errors' not in resp:
            mimeType=self.mimeTypes[self.streamTvProtocol]
            playerProtocol=self.protocols[self.streamTvProtocol]
            #streams=resp['data']['programByRecordID']['video']['formats'] #złe odczyty znaczników czasowych
            tokenizer=resp['data']['programByRecordID']['stream']['urls']['stream']
            resp_tkn=requests.get(tokenizer,headers=hea_oth).json()
            streams=resp_tkn['formats']
            url_stream=''
            s_url=[s['url'] for s in streams if s['mimeType']==mimeType]
            if len(s_url)>0:
                url_stream=s_url[0]
            
            xbmc.log('@@@stream_url: '+url_stream, level=xbmc.LOGINFO)
            
            pathFile='plugin://plugin.video.TVP_VOD/?mode=playReplayTV&chCode='+chCode+'&progID='+progID
            request={
                "jsonrpc": "2.0", 
                "method": "Files.GetFileDetails", 
                "params": {
                    "file": pathFile, 
                    "media": "video", 
                    "properties": ["resume"]
                },
                "id":"1"
            }
            results = json.loads(xbmc.executeJSONRPC(json.dumps(request)))
            if 'resume' not in results['result']['filedetails']:
                fromStart=True
            else:
                fromStart=False
            
            self.playerISA(url_stream,playerProtocol,live=False,fromStart=fromStart)
        else:
            #alternatywa gdy API TVP GO HbbTV nie dostarcza url strumienia 
            url='https://sport.tvp.pl/api/tvp-stream/stream/data?station_code=%s&record_id=%s&device=android' %(chCode,progID)
            resp=requests.get(url,headers=hea_oth).json()
            streamData=dict(parse_qsl(resp['data']['stream_url'].split('?')[1]))
            if 'begin' in streamData:
                b=streamData['begin']
                e=streamData['end']
                st=list(self.stations.keys())

                cid=[self.stations[s]['cid'] for s in st if self.stations[s]['code']==chCode][0]
                self.playReplay(cid,b,e,'y')
            else:
                xbmcgui.Dialog().notification('TVPGO', 'Nagranie niedostępne', xbmcgui.NOTIFICATION_INFO)
                xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
            
    def epgData(self,stCode):
        hea={
            'User-Agent':base.UA
        }
        period=12*60*60*1000
        date=[]
        today=datetime.datetime.now().strftime('%Y-%m-%d')
        date.append(today)
        hour=int(datetime.datetime.now().strftime('%H'))
        if hour>=12:
            date.append((datetime.datetime.now()+datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
        epg=[]
        now=int(time.time())*1000
        for d in date:
            url='http://www.api.v3.tvp.pl/shared/programtv-listing.php?station_code='+stCode+'&count=500&dump=json&today_from_midnight=1&date='+d
            resp=requests.get(url,headers=hea).json()
            for r in resp['items']:
                if r['date_end']>=now and r['date_start']<=now+period:
                    start=datetime.datetime.fromtimestamp(int(r['date_start']/1000)).strftime('%H:%M')
                    title=r['title']
                    try:
                        type=r['program']['type']['name']
                    except:
                        type=''
                    epg.append([start,title,type])
        return epg

    def getEPG(self,sc):
        epg=self.epgData(sc)
        plot=''
        for e in epg:
            plot+='[B]'+e[0]+'[/B] '+e[1]
            if e[2] !='':
                plot+=' [I]('+e[2]+')[/I]'
            plot+='\n'
        if plot=='':
            plot='Brak danych EPG'
        dialog = xbmcgui.Dialog()
        dialog.textviewer('EPG', plot)
        
    def generate_m3u(self,file_name,path_m3u):
        if file_name == '' or path_m3u == '':
            xbmcgui.Dialog().notification('TVP_VOD', 'Ustaw nazwę pliku oraz katalog docelowy.', xbmcgui.NOTIFICATION_ERROR)
            return
        xbmcgui.Dialog().notification('TVP_VOD', 'Generuję listę M3U.', xbmcgui.NOTIFICATION_INFO)
        stCU=[self.stations[c]['code'] for c in list(self.stations.keys()) if self.stations[c]['catchup']=='y']
        
        data = '#EXTM3U\n'
        c=self.channelArrayGen()
        for item in c:
            channelCode = item[0]
            channelName = item[1]
            channelLogo = item[2]
            channelID = item[3]
            
            if channelCode in stCU:
                data += '#EXTINF:0 tvg-id="%s" tvg-logo="%s" group-title="TVP_VOD" catchup="append" catchup-source="&s={utc:YmdTHMS}&e={utcend:YmdTHMS}" catchup-days="7" catchup-correction="0.0",%s\nplugin://plugin.video.TVP_VOD?mode=playLiveTV&chCode=%s&chID=%s\n' % (channelName,channelLogo,channelName,channelCode,channelID)
            else:
                data += '#EXTINF:0 tvg-id="%s" tvg-logo="%s" group-title="TVP_VOD",%s\nplugin://plugin.video.TVP_VOD?mode=playLiveTV&chCode=%s&chID=%s\n' % (channelName,channelLogo,channelName,channelCode,channelID)
            
        f = xbmcvfs.File(path_m3u + file_name, 'w')
        f.write(data)
        f.close()
        xbmcgui.Dialog().notification('TVP_VOD', 'Wygenerowano listę M3U.', xbmcgui.NOTIFICATION_INFO)


    #REPLAY (new)
    
    def listTV(self):
        #uzupełnienie o virtual channels z TVP GO apk
        vc=self.virtChan()
        for v in vc:
            self.stations[v[1]]={'code':v[3].replace('vc_',''),'cid':'','catchup':'y_cms','img':v[2],'tvpgo_hbb':'n'}
        
        channels=list(self.stations.keys())
        for c in channels:
            if self.stations[c]['catchup']!='n':
                name=c
                cid=self.stations[c]['cid']
                code=self.stations[c]['code']
                img=self.stations[c]['img'].format(imgURL='_width_510_play_0_pos_0_gs_0_height_0.png') if self.stations[c]['img'] !='' else 'OverlayUnwatched.png'
                catchup=self.stations[c]['catchup']
                
                setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img, 'fanart':''}
                url = base.build_url({'mode':'calendar','cid':cid,'code':code,'catchup':catchup})
                base.addItemList(url, name, setArt)
        xbmcplugin.endOfDirectory(addon_handle)

    def calendar(self,code,cid,cu):
        today=datetime.datetime.now()
        ar_date=[]
        i=0
        replayPeriod='7'#addon.getSetting('replay_period')
        while i<=int(replayPeriod):#7
            day=(today-datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            ar_date.append(day)
            i=i+1

        for d in ar_date:    
            iL={'title': d,'sorttitle': d,'plot': ''}
            setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': 'DefaultYear.png', 'fanart': ''}
            url = base.build_url({'mode':'programs','date':d,'code':code,'cid':cid,'catchup':cu})
            base.addItemList(url, d, setArt, infoLab=iL)
        
        xbmcplugin.endOfDirectory(addon_handle)

    def programs(self,d,code,cid,cu):
        if cu=='y_cms':
            cid=self.vc_cid(code)
        
        now=int(time.time())
        #past=now-7*24*60*60
        replayPeriod='7'#addon.getSetting('replay_period')
        past=now-int(replayPeriod)*24*60*60
        u='http://www.api.v3.tvp.pl/shared/programtv-listing.php?station_code='+code+'&count=1000&dump=json&today_from_midnight=0&date={date}'
        url=u.format(date=d) 
        resp1=requests.get(url,headers=hea_oth).json()
        d1=(datetime.datetime(*(time.strptime(d,'%Y-%m-%d')[0:6]))-datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        url=u.format(date=d1) 
        resp2=requests.get(url,headers=hea_oth).json()
        resp=resp2['items']+resp1['items']
        for r in resp:
            date=self.fromTstmptoStr(int(r['date_start']/1000),'%Y-%m-%d') 
            if date==d and r['date_start']>=1000*past and r['date_start']<=1000*now:
                title='[B]%s[/B] '%(self.fromTstmptoStr(int(r['date_start']/1000),'%H:%M')) 
                title+=r['title']
                try:
                    type=r['program']['type']['name']
                    title+=' [I]('+type+')[/I]'
                except:
                    pass
                plot=''
                img=img_inne
                if 'program' in r:
                    p=r['program']
                    if cu=='y_cms':
                        cid=p['cms_id'] if p['cms_id']!=None else ''
                    year=p['year'] if 'year' in p else ''
                    desc=p['description_long'] if 'description_long' in p else ''
                    try:
                        type=p['type']['name'] if 'type' in p else ''
                    except:
                        type=''
                    land='/'.join(p['land']) if 'land' in p else ''
                    
                    if type !='':
                        plot+='[B]'+type+'[/B]\n'
                    if year !=None:
                        plot+='[B]Rok prod: [/B]'+str(year)+'\n'
                    if land !='':
                        plot+='[B]Kraj: [/B]'+land+'\n'
                    if desc not in ['',None]:
                        plot+='[I]'+desc+'[/I]'
                    
                    if 'image_source' in p:
                        imgSrc=[]
                        if p['image_source']=='program_type':
                            imgSrc=p['images']
                            imgType='images2'
                        elif p['image_source']=='akpa_type' or  p['image_source']=='cms_type':
                            try:
                                imgSrc=p['akpa_images']
                                imgType='images-akpa'
                            except:
                                pass
                        
                        if len(imgSrc)>0:
                            try:
                                imgFile,imgExt=imgSrc[0]['fileName'].split('.')
                                imgW=imgSrc[0]['width']
                                imgH=imgSrc[0]['height']
                                img='https://s1.tvp.pl/%s/a/0/0/uid_%s_width_%s_play_0_pos_0_gs_0_height_%s.%s' %(imgType,imgFile,imgW,imgH,imgExt)
                            except:
                                pass


                begin=self.fromTstmptoStr(int(r['date_start']/1000),'%Y%m%dT%H%M%S','utc')
                end=self.fromTstmptoStr(int(r['date_end']/1000+15*60),'%Y%m%dT%H%M%S','utc')#wydłużenie czasu zakończenia o 15 minut ze względu na możliwe opóźnienia w ramówce      
                
                if cid!='':
                    url_ch = base.build_url({'mode':'playReplay','begin':begin,'end':end,'cid':cid,'catchup':cu})
                    isPlayable='true'
                else:
                    url_ch = base.build_url({'mode':'noSource'})
                    isPlayable='false'
                    title='[COLOR=red]'+title+'[/COLOR]'
                                       
                if cu=='y':
                    tit=[s for s in self.stations if self.stations[s]['cid']==cid][0]+' | '
                    tit+=d+' '+title
                elif cu=='y_cms':
                    tit=title
                            
                iL={'title': title,'sorttitle': title,'plot': plot}
                setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart': ''}
                cmItems=[('[B]Dodaj do ulubionych[/B]','RunPlugin(plugin://plugin.video.TVP_VOD?mode=favExtAdd&url='+quote(url_ch)+'&title='+quote(tit)+'&infoLab='+quote(str(iL))+'&img='+quote(img)+')')]
                base.addItemList(url_ch, title, setArt, 'video', iL, False, isPlayable, True, cmItems)
        
        xbmcplugin.setContent(addon_handle, 'videos')
        xbmcplugin.endOfDirectory(addon_handle)
        
    def playReplay(self,cid,b,e,cu):
        pathFile='plugin://plugin.video.TVP_VOD/?mode=playReplay&begin='+b+'&end='+e+'&cid='+cid+'&catchup='+cu
        request={
            "jsonrpc": "2.0", 
            "method": "Files.GetFileDetails", 
            "params": {
                "file": pathFile, 
                "media": "video", 
                "properties": ["resume"]
            },
            "id":"1"
        }
        results = json.loads(xbmc.executeJSONRPC(json.dumps(request)))
        if 'resume' not in results['result']['filedetails']:
            fromStart=True
        else:
            fromStart=False
       
        url='https://token-java-v2.tvp.pl/tokenizer/token/'+cid
        resp=requests.get(url,headers=hea_oth).json()
        url_stream=''
        protocol=''
        if resp['formats']!=None:
            mimeType=self.mimeTypes[self.streamTvProtocol]
            formats = [f for f in resp['formats'] if f['mimeType']==mimeType]
            def sortFN(i):
                return i['totalBitrate']
            formats.sort(key=sortFN,reverse=True)
            if cu=='y':
                url_stream=formats[0]['url']+'?begin='+b#+'&end='+e
            elif cu=='y_cms':
                url_stream=formats[0]['url']
            protocol=self.protocols[self.streamTvProtocol]
            if url_stream !='':
                self.playerISA(url_stream,protocol,live=False,fromStart=fromStart)    
            else:
                xbmcgui.Dialog().notification('TVP_VOD', 'Brak źródła', xbmcgui.NOTIFICATION_INFO)
                xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
        else:
            xbmcgui.Dialog().notification('TVP_VOD', 'Brak źródła', xbmcgui.NOTIFICATION_INFO)
            xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
