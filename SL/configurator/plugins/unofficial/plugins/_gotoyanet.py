import logging
import re

from streamlink.plugin import Plugin
from streamlink.plugin.api import useragents
from streamlink.utils import update_scheme
from streamlink.stream._ffmpegmux import FFMPEGMuxer
from streamlink.stream._hlsdl import HLSDL
from streamlink.stream.file import FileStream

log = logging.getLogger(__name__)


class gotoyanet(Plugin):
    #### Przykladowy link do kamery
    #https://go.toya.net.pl/25-kamery/13758-lodz/444413758155-piotrkowska-narutowicza/play
    #### kawalek kodu strony gdzie jest adres strumienia
    #class="player" data-stream="https://cdn-3-go.toya.net.pl:8081/kamery/lodz_piotrkowskanarutowicza.m3u8?p=474f43414d005f5e0ff.bd9750ac468f5d2d573a00637374" data-mode="cam"
    #### adres z powyzszego kawalka
    #https://cdn-3-go.toya.net.pl:8081/kamery/lodz_piotrkowskanarutowicza.m3u8?p=474f43414d005f5e0ff.bd9750ac468f5d2d573a00637374
    
    _url_re = re.compile(r"https?://go\.toya\.net\.pl")
    _addr_re = re.compile(r'[ ]*data-stream="([^"]+)"')
    #_addr_re = re.compile(r'[ ]*src="blob:([^"]+)"')

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        #self.session.set_option('hls-live-edge', 10)
        self.session.http.headers.update({'Referer': 'https://go.toya.net.pl'})
        self.session.http.headers.update({'User-Agent': useragents.ANDROID})
        res = self.session.http.get(self.url)
        #log.debug(res.text)
        
        try:
            address = self._addr_re.search(res.text).group(1)
            address = address.split('?p')[0]
            log.debug("Found address: %s" % address)
        except Exception as e:
            log.debug(str(e))
            return

        if 1 == 1: #a workarround for now because I don't know how to make it happen in stream
            CacheFileName = '/tmp/stream.ts'
            _cmd = ['/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/bin/hlsdl'] 
            _cmd.extend([address])
            _cmd.extend(['-b', '-f', '-o', CacheFileName])
            log.debug("hlsdl command: {0}".format(' '.join(_cmd))) 
            import subprocess
            try:
                from subprocess import DEVNULL # Python 3.
            except ImportError:
                import os
                DEVNULL = open(os.devnull, 'wb')
            processHLSDL = subprocess.Popen(_cmd, stdout= DEVNULL, stderr= DEVNULL )
            if processHLSDL: 
                processPID = processHLSDL.pid
                log.debug('FileCache:%s:%s' % ( processPID, CacheFileName )) 
                #raise Exception('FileCache:%s:%s' % ( processPID, CacheFileName ))
                return
                #import time
                #time.sleep(2)
                #if os.path.exists(CacheFileName):
                #    return {"file_stream": FileStream(self.session, CacheFileName)} 
                
            else:
                raise Exception('ERROR initiating processHLSDL')
                return
        else:
            return {"rtsp_stream": HLSDL(self.session, *(address,), is_muxed=False, format='mpegts', vcodec = 'copy', acodec = 'copy')} 

__plugin__ = gotoyanet
