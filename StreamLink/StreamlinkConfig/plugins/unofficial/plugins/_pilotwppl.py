# -*- coding: utf-8 -*-
import logging
import re

#from streamlink.compat import html_unescape
from streamlink.plugin import Plugin, PluginError, pluginmatcher
from streamlink.plugin.api import useragents
#from streamlink.plugin.api.utils import itertags
#from streamlink.stream._hls4wp import HLSStream
from streamlink.stream.hls import HLSStream
from streamlink.stream.dash import DASHStream
from streamlink.stream.file import FileStream
from streamlink.utils import update_scheme

#>>> zeby rozwiazac problem error 449
import ssl
from streamlink.session.http import SSLContextAdapter

class WPplAdapter(SSLContextAdapter):
    def get_ssl_context(self):
        ctx = super().get_ssl_context()
        ctx.check_hostname = False
        ctx.options &= ~ssl.OP_NO_TICKET
        ctx.options &= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1

        return ctx
#<<<

log = logging.getLogger(__name__)

import sys
sys.path.append('/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/')

from wpConfig import headers
from wpConfig import params #'login_url', 'main_url', 'video_url', 'close_stream_url'
from wpConfig import data
from wpConfig import getCookie
from wpConfig import PreferDash
from wpConfig import videoDelay
from wpBouquet import _login


@pluginmatcher(re.compile(
    r"https?://pilot.wp.pl/api/v1/channel/",
))

class PilotWPpl(Plugin):
    _url_re = re.compile(r"https?://pilot.wp.pl/api/v1/channel/")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session.http.mount("https://pilot.wp.pl/", WPplAdapter())

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        def _Response():
            try:
                return self.session.http.get(
                                                 self.url,
                                                 params=data,
                                                 verify=False,
                                                 headers=headers,
                                                ).json()
        
            except Exception as e:
                strErr = str(e)
                log.debug("EXCEPTION: %s" % strErr)
                if '403' in strErr:
                    return '403'
                if '422' in strErr:
                    return '422'
                else:
                    return strErr
                    
        log.debug("PilotWPpl._get_streams() >>>")
        cookies = getCookie()
        if not cookies:
            cookies = _login()
          
        data = {'format_id': '2', 'device_type': 'android_tv'}
        
        #print headers
        self.session.http.headers.update({'User-Agent': headers['User-Agent']})
        self.session.http.headers.update({'Accept': headers['Accept']})
        self.session.http.headers.update({'x-version': headers['x-version']})
        self.session.http.headers.update({'content-type': headers['content-type']})
        self.session.http.headers.update({'Cookie': cookies})
        
        response = _Response()
        if response == '403':
            cookies = _login()
            self.session.http.headers.update({'Cookie': cookies})
            response = _Response()
        if response == '403': #403 Client Error: Forbidden for url:
            log.info('wperror-403')
            raise Exception('wperror-403')    
            return
        elif response == '422': #422 Client Error: Unprocessable Entity for url:
            log.info('wperror-422')
            #raise Exception('wperror-422')    
            return

        log.debug("Response: %s" % response)
        meta = response.get('_meta', None)
        log.debug("meta: %s" % meta)
        if meta is not None:
            token = meta.get('error', {}).get('info', {}).get('stream_token', None)
            log.debug("token: %s" % token)
            """if token is not None:
                json = {'channelId': video_id, 't': token}
                response = requests.post(
                    close_stream_url,
                    json=json,
                    verify=False,
                    headers=headers
                  ).json()
                if response.get('data', {}).get('status', '') == 'ok' and not retry:
                    return stream_url(video_id, True)
                else:
                    return"""
            
        log.debug("1st stream type: %s" % response[u'data'][u'stream_channel'][u'streams'][0][u'type'])
        
        if 'dash@live:abr' in response[u'data'][u'stream_channel'][u'streams'][0][u'type']:
            dashUrl = response[u'data'][u'stream_channel'][u'streams'][0][u'url'][0]
        if 'hls@live:abr' in response[u'data'][u'stream_channel'][u'streams'][1][u'type']:
            hlsUrl = response[u'data'][u'stream_channel'][u'streams'][1][u'url'][0]
        log.debug("Found streams:\n\t dash: %s\n\t hls: %s" % (dashUrl,hlsUrl))
        
        if PreferDash:
            log.debug("use DASH stream")
            return DASHStream.parse_manifest(self.session, dashUrl)
        else:
            log.debug("use HLS stream")
            log.debug("videoDelay = %s" % videoDelay)
            return HLSStream.parse_variant_playlist(self.session,
                                                    update_scheme(self.url, hlsUrl),
                                                    headers={'Referer': self.url, 
                                                             'User-Agent': headers['User-Agent'],
#                                                            'accept': 'application/json', 
                                                             'x-version': headers['x-version'],
#                                                            'content-type': 'application/json; charset=UTF-8',
                                                             'Cookie': cookies
                                                            }
                                                    )

__plugin__ = PilotWPpl
