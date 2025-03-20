# -*- coding: utf-8 -*-


import threading

import requests,re


try:  # Python 3
    from http.server import BaseHTTPRequestHandler
except ImportError:  # Python 2
    from BaseHTTPServer import BaseHTTPRequestHandler

try:  # Python 3
    from socketserver import TCPServer
except ImportError:  # Python 2
    from SocketServer import TCPServer


from emukodi import xbmcaddon, xbmc
addon = xbmcaddon.Addon('plugin.video.orangetvgo')

class Proxy(BaseHTTPRequestHandler):

    server_inst = None

    @staticmethod
    def start():
        """ Start the Proxy. """

        def start_proxy():
            """ Start the Proxy. """
            Proxy.server_inst = TCPServer(('127.0.0.1', 0), Proxy)

            port = Proxy.server_inst.socket.getsockname()[1]
            addon.setSetting('proxyport', str(port))

            Proxy.server_inst.serve_forever()

        thread = threading.Thread(target=start_proxy)
        thread.start()

        return thread

    @staticmethod
    def stop():
        """ Stop the Proxy. """
        if Proxy.server_inst:
            Proxy.server_inst.shutdown()
    def do_HEAD(self):

        self.send_response(200)
        self.end_headers()
    def do_GET(self):  

        path = self.path 
        if 'MLB=' in path:
            try:
                m3u_url = (path).split('MLB=')[-1]
    
                if 'm3u8' in m3u_url:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/x-mpegURL')
                    self.end_headers()
                    xbmc.log('manifest_datamanifest_datamanifest_data: %s'%str(manifest_data), level=xbmc.LOGINFO)
                    
                    
                    self.wfile.write(manifest_data.encode(encoding='utf-8', errors='strict'))
                elif (m3u_url).endswith('.ts'):

                    result=requests.get(m3u_url, verify=False, timeout = 30).content
                
                    self.send_response(200)
                    self.send_header('Content-Type', 'video/mp2t')
                    
                    self.send_header('Content-Length', len(result))
                    self.end_headers()
    
                    self.wfile.write(result)

            except Exception as exc: 
                xbmc.log('blad w proxy: %s'%str(exc), level=xbmc.LOGINFO)
                self.send_response(500)
                self.end_headers()
        elif 'NHL=' in path:
            try:
                m3u_url = (path).split('NHL=')[-1]
    
                if 'm3u8' in m3u_url:

                    result = requests.get(m3u_url, verify=False, timeout = 30).content
                    
                    manifest_data = result.decode(encoding='utf-8', errors='strict')
                    
                    manifest_data = manifest_data.replace( "https://mf.svc.nhl.com/", "https://api.nhl66.ir/api/get_key_url/")
                    manifest_data = manifest_data.replace( "https://playback.svcs.plus.espn.com/", "https://api.nhl66.ir/api/get_key_url/")
                    mainuri =     addon.getSetting("mainurikey")
                    self.send_response(200)
                    self.send_header('Content-type', 'application/x-mpegURL')
                    self.end_headers()
                    xbmc.log('manifest_datamanifest_datamanifest_data: %s'%str(manifest_data), level=xbmc.LOGINFO)
                    
                    
                    self.wfile.write(manifest_data.encode(encoding='utf-8', errors='strict'))
                elif (m3u_url).endswith('.ts'):

                    result=requests.get(m3u_url, verify=False, timeout = 30).content
                
                    self.send_response(200)
                    self.send_header('Content-Type', 'video/mp2t')
                    
                    self.send_header('Content-Length', len(result))
                    self.end_headers()
    
                    self.wfile.write(result)

            except Exception as exc: 
                xbmc.log('blad w proxy: %s'%str(exc), level=xbmc.LOGINFO)
                self.send_response(500)
                self.end_headers()
    def do_POST(self):
        """Handle http post requests, used for license"""
        path = self.path  # Path with parameters received from request e.g. "/license?id=234324"
        print('HTTP POST Request received to {}'.format(path))
        if '/license' not in path:
            self.send_response(404)
            self.end_headers()
            return

        path2 = path.split('licensetv=')[-1]
        try:
            length = int(self.headers.get('content-length', 0))
            isa_data = self.rfile.read(length)
    
            challenge = isa_data
    
            path2 = path.split('licensetv=')[-1]
    
            result = requests.post(url=path2, data=challenge)
    
            if result.status_code==200:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(result.content)
        except Exception as exc: 
            xbmc.log('blad w proxy: %s'%str(exc), level=xbmc.LOGINFO)
            self.send_response(500)
            self.end_headers()