import threading

try:  # Python 3
	from http.server import BaseHTTPRequestHandler, HTTPServer
	from socketserver import ThreadingMixIn
except ImportError:  # Python 2
	from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
	from SocketServer import ThreadingMixIn

try:  # Python 3
	from urllib.parse import parse_qs, urlparse, urlencode,quote,unquote, parse_qsl
except ImportError:  # Python 2
	from urlparse import urlparse, parse_qs, parse_qsl
	from urllib import urlencode,quote,unquote
	
import re
import socket
from contextlib import closing

import xbmcaddon, xbmc

addon = xbmcaddon.Addon('plugin.video.cdaplMB')
proxyport = addon.getSetting('proxyport')
import requests
import sys
PY3 = sys.version_info >= (3,0,0)
if PY3:
	LOGNOTICE = xbmc.LOGINFO

else:
	LOGNOTICE = xbmc.LOGNOTICE
__BLOCK_SIZE__ = 16

'''
import requests
from requests.exceptions import SSLError
import urllib3  # already used by "requests"
from urllib3.exceptions import MaxRetryError, SSLError as SSLError3
from certifi import where
'''

from requests import Session
from requests.adapters import HTTPAdapter
'''
from requests.packages.urllib3.util.ssl_ import create_urllib3_context

import ssl
from urllib3.util.ssl_ import DEFAULT_CIPHERS
'''
session = Session()
headersx = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0"}

class m3u8:
	def __init__(self):
		self.www = ''

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

	def parseUrl(self, tup):
		url = (self.path).split(tup)[-1]
		if "@" in url:
			urlk, h = url.split('@')
			SimpleHTTPRequestHandler.headers = dict(parse_qsl(h))
		else:
			urlk = url
		return urlk

	
	def do_HEAD(self):
    
		self.send_response(200)
		self.end_headers()

	def do_GET(self):
		"""Handle http get requests, used for manifest"""

		path = self.path  
		if 'dd=' in self.path:
		
			if '.mp4' in self.path:

				try:
					licurl = self.parseUrl('dd=')

						
					resp = session.get(url=licurl, headers=headersx, verify=False, timeout = 30, stream=True)#.text
					self.send_response(206)	
					for k,v in (resp.headers).items():
						self.send_header(k,v)

					self.end_headers()
											
					for chunk in resp.iter_content(8192):
						self.wfile.write(chunk)	

				except Exception as exc:
					xbmc.log('ExceptionExceptionExceptionException: %s' % str(exc), level=LOGNOTICE)
					self.send_response(500)
					self.end_headers()
			else:
					pathx = self.parseUrl('dd=')
					self.send_response(302)
					self.send_header('Location', pathx)

					self.send_header('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0")
					self.end_headers()

		else:

			return	
	def do_POST(self):
		"""Handle http post requests, used for license"""
		path = self.path  
		if '/license' not in path:
			self.send_response(404)
			self.end_headers()
			return

		length = int(self.headers.get('content-length', 0))
		isa_data = self.rfile.read(length).decode('utf-8').split('!')
		
		challenge = isa_data[0]
		path2 = path.split('cense=')[-1]
		
		licurl=(addon.getSetting('licurl'))
		ab=eval(addon.getSetting('hea'))
		result = requests.post(url=licurl, headers=ab, data=challenge).content
		if PY3:
			result = result.decode(encoding='utf-8', errors='strict')
		
		licens=re.findall('ontentid=".+?">(.+?)<',result)[0]
		
		if PY3:
			licens= licens.encode(encoding='utf-8', errors='strict')
		
		self.send_response(200)
		self.end_headers()
		
		self.wfile.write(licens)
		
def find_free_port():
	with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
		s.bind(('', 0))
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		addon.setSetting('proxyport',str(s.getsockname()[1]))
		return s.getsockname()[1]	
		
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
	
class http_server:
	def __init__(self, t1):
		PORT = find_free_port()
		server = ThreadedHTTPServer(('127.0.0.1', PORT), SimpleHTTPRequestHandler)
		server.t1 = t1
		server.allow_reuse_address = True
		httpd_thread = threading.Thread(target=server.serve_forever)
		httpd_thread.start()
		
		xbmc.Monitor().waitForAbort()
		
		server.shutdown()
		server.server_close()
		server.socket.close()
		httpd_thread.join() 
 
		
class main:
	def __init__(self):
		self.t1 = m3u8()
		self.server = http_server(self.t1)

if __name__ == '__main__':
	m = main()

