from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer
from urllib.parse import parse_qs, urlparse, urlencode,quote,unquote
import base64
import re
import socket
from contextlib import closing
import time

import xbmcaddon, xbmcgui
import requests
import sys

addon = xbmcaddon.Addon(id='plugin.video.upcgo')
baseurl='https://www.upctv.pl/'
apiURL='https://spark-prod-pl.gnp.cloud.upctv.pl/'
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'

def accessToken_refresh(): #POWIELENIE z addon.py
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
    }
    data={
        'refreshToken':addon.getSetting('x_refresh_token'),
        'username':addon.getSetting('x_oesp_username')
    }
    cookies={
        'ACCESSTOKEN':addon.getSetting('accessToken'),
        'CLAIMSTOKEN':addon.getSetting('CLAIMSTOKEN')
    }
    url=apiURL+'auth-service/v1/authorization/refresh'
    resp=requests.post(url,headers=hea,cookies=cookies,json=data).json()
    addon.setSetting('accessToken',resp['accessToken'])
    addon.setSetting('x_refresh_token',resp['refreshToken'])

    return resp['accessToken']

def claimsToken_refresh():
    claimstoken=addon.getSetting('CLAIMSTOKEN')
    start=addon.getSetting('claimsToken_start')
    if start=='':
        start='0'
    now=int(time.time())
    if now-int(start)>=24*60*60:
        url=apiURL+'pol/web/personalization-service/v1/customer/'+addon.getSetting('x_cus')+'?with=profiles,devices&advertisementDeviceId='+addon.getSetting('advertisementDeviceId')
        hea={
            'User-Agent':UA,
            'Referer':baseurl,
            #'X-cus':addon.getSetting('x_cus'),
            'x-go-dev':addon.getSetting('x_go_dev'),
            'X-OESP-Username':addon.getSetting('x_oesp_username')
        }
        cookies={
            'ACCESSTOKEN':addon.getSetting('accessToken')#accessToken_refresh()
        }
        resp=requests.get(url,headers=hea,cookies=cookies)
        resp_cooks=dict(resp.cookies)
        if 'CLAIMSTOKEN' in resp_cooks:
            claimstoken=resp_cooks['CLAIMSTOKEN']
            addon.setSetting('CLAIMSTOKEN',claimstoken)
            addon.setSetting('claimsToken_start',str(now))
            print('CLAIMSTOKEN refresh')
    
    return claimstoken
    
def getCookies():
    c={
        'ACCESSTOKEN':accessToken_refresh(),
        'CLAIMSTOKEN':claimsToken_refresh()
    }
    return c

def refreshStreamingToken():#liveTV
    url=apiURL+'pol/web/session-manager/license/token'
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
        'X-cus':addon.getSetting('x_cus'),
        'x-go-dev':addon.getSetting('x_go_dev'),
        'X-OESP-Username':addon.getSetting('x_oesp_username'),
        'X-Profile':addon.getSetting('x_profile'),
        'x-streaming-token':addon.getSetting('x_streaming_token')
    }
    cookies=getCookies()
    resp=requests.post(url,headers=hea,cookies=cookies)
    #print('odświeżony')
    #print(resp)
    strTkn=resp.headers['x-streaming-token']
    addon.setSetting('x_streaming_token',strTkn)
    addon.setSetting('x_str_tkn_start',str(int(time.time())))

def refreshStreamingTokenReplay():#replayTV
    now=int(time.time())
    start=int(addon.getSetting('startPlaying'))
    position=now-start
    url=apiURL+'pol/web/session-manager/license/token?position='+str(position)
    hea={
        'User-Agent':UA,
        'Referer':baseurl,
        'X-cus':addon.getSetting('x_cus'),
        'x-go-dev':addon.getSetting('x_go_dev'),
        'X-OESP-Username':addon.getSetting('x_oesp_username'),
        'X-Profile':addon.getSetting('x_profile'),
        'x-streaming-token':addon.getSetting('x_streaming_token'),
        'x-tracking-id':addon.getSetting('x_tracking_id')
    }
    cookies=getCookies()
    resp=requests.post(url,headers=hea,cookies=cookies)
    #print('odświeżony')
    #print(resp)
    strTkn=resp.headers['x-streaming-token']
    addon.setSetting('x_streaming_token',strTkn)
    addon.setSetting('x_str_tkn_start',str(int(time.time())))

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        """Handle http get requests, used for manifest"""

        path = self.path  # Path with parameters received from request e.g. "/manifest?id=234324"

        if '/MANIFEST=' not in path:
            self.send_response(404)
            self.end_headers()
            return

        manifest_data=b''

        time_now=int(time.time())
        time_tkn=int(addon.getSetting('x_str_tkn_start'))

        if addon.getSetting('streamType')=='replaytv':
            print('replayTV')

            if 'index.mpd/Manifest' in path:
                url_stream=''
                url_stream=path.split('MANIFEST=')[1]
                hea={
                    'User-Agent':UA,
                    'Referer':baseurl
                }
                manifest_data = requests.get(url_stream, headers=hea).content
                
                self.send_response(200)
                self.send_header('Content-type', 'application/xml+dash')
                self.end_headers()
                self.wfile.write(manifest_data)
            else:
                old_token=addon.getSetting('x_streaming_token')
                url=''
                if time_now>=time_tkn+60 and '.mpd' in path:
                    refreshStreamingTokenReplay()
                    url=re.sub('vxttoken=[^/]+?/','vxttoken='+addon.getSetting('x_streaming_token')+'/',path.split('MANIFEST=')[1])
                else:
                    url_stream=path.split('MANIFEST=')[1]
                    url=re.sub('vxttoken=[^/]+?/','vxttoken='+old_token+'/',url_stream)

                self.send_response(302)
                self.send_header('Location', url)
                self.end_headers()

        if addon.getSetting('streamType')=='livetv':
            if 'manifest.mpd' in path:
                url_stream=re.sub('vxttoken=[^/]+?/','vxttoken='+addon.getSetting('x_streaming_token')+'/',path.split('MANIFEST=')[1])
                hea={
                    'User-Agent':UA,
                    'Referer':baseurl
                }
                manifest_data = requests.get(url_stream, headers=hea).content
                self.send_response(200)
                self.send_header('Content-type', 'application/xml+dash')
                self.end_headers()
                self.wfile.write(manifest_data)
            else:
                old_token=addon.getSetting('x_streaming_token')
                url=''
                if time_now>=time_tkn+60 and 'manifest.mpd' not in path:
                    refreshStreamingToken()
                    url=re.sub('vxttoken=[^/]+?/','vxttoken='+addon.getSetting('x_streaming_token')+'/',path.split('MANIFEST=')[1])
                else:
                    url_stream=path.split('MANIFEST=')[1]
                    url=re.sub('vxttoken=[^/]+?/','vxttoken='+old_token+'/',url_stream)

                self.send_response(302)
                self.send_header('Location', url)
                self.end_headers()


    def do_POST(self):
        """Handle http post requests, used for license"""
        pass
        '''
        path = self.path  # Path with parameters received from request e.g. "/license?id=234324"

        if '/licensetv' not in path:
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get('content-length', 0))
        isa_data = self.rfile.read(length)

        challenge = isa_data
        path2 = path.split('licensetv=')[-1]

        hea=eval(addon.getSetting('hea_lic'))
        cookies=getCookies()
        result = requests.post(url=path2, headers=hea, cookies=cookies, data=challenge)

        if result.status_code==200:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(result.content)

        else:
            resp=result.content.decode('utf-8')
            if '\"statusCode\":1111' in resp: #niedostępne poza siecią UPC
                xbmcgui.Dialog().notification('UPC', 'Kanał niedostępny poza siecią UPC.', xbmcgui.NOTIFICATION_INFO)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'')
        '''
def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        addon.setSetting('proxyport',str(s.getsockname()[1]))
        return s.getsockname()[1]


address = '127.0.0.1'  # Localhost

port = find_free_port()
server_inst = TCPServer((address, port), SimpleHTTPRequestHandler)
server_inst.serve_forever()
