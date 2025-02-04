from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer
from urllib.parse import parse_qs, urlparse, urlencode,quote,unquote
#import base64
import re
import socket
from contextlib import closing
import requests
import sys
import xbmcaddon, xbmc, xbmcgui
from resources.lib.base import b

base=b()
addon = base.addon

hea={
    'User-Agent':base.UA
}

import threading

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
        """Handle http get requests, used for manifest"""

        path = self.path
        if 'MANIFEST=' in(self.path) and '.m3u8' in (self.path):#
            url=self.path.split('MANIFEST=')[-1]
            try:
                result = requests.get(url, headers=hea, timeout = 30).content
                result = result.decode(encoding='utf-8', errors='strict')
                #print(result)
                '''
                replaceFROM = '#EXT-X-DISCONTINUITY'
                replaceTO = ''
                manifest_data = result.replace(replaceFROM,replaceTO)
                '''
                manifest_data = re.sub('#EXT-X-PROGRAM-DATE-TIME:.*\\n','',result)
                #print(manifest_data)
                self.send_response(200)
                self.send_header('Content-type', 'application/x-mpegURL')
                self.end_headers()
                self.wfile.write(manifest_data.encode(encoding='utf-8', errors='strict'))
            except Exception:
                self.send_response(500)
                self.end_headers()
        
        if '.m3u8' not in(self.path) and 'MANIFEST=' in (self.path):#
            url=(self.path).split('MANIFEST=')[-1]
            result=requests.get(url, headers=hea, verify=False, timeout = 30).content

            self.send_response(200)
            self.send_header('Content-type', 'application/vnd.apple.mpegurl')
            self.end_headers()

            self.wfile.write(result)

        else:

            return

    #def do_POST(self):
 