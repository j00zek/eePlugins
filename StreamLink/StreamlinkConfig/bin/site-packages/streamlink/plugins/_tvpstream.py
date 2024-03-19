import logging
import re,json

from streamlink.plugin import Plugin, PluginError, pluginmatcher
from streamlink.plugin.api import useragents
from streamlink.utils import update_scheme
#from streamlink.stream._ffmpegmux import FFMPEGMuxer
from streamlink.exceptions import PluginError
from streamlink.stream import HLSStream, HTTPStream
from streamlink.stream.dash import DASHStream
#from streamlink.stream._hlsdl import HLSDL

log = logging.getLogger(__name__)

#livesrc="http://tvpstream.vod.tvp.pl/sess/tvplayer.php?object_id=%s"
#livesrc="http://tvp_player.php?object_id=%s"


@pluginmatcher(re.compile(
    r'https?://tvp_player.php\?object_id=',
))

class tvpstream(Plugin):
    #### Przykladowy wpis bukietu
    #SERVICE 4097:0:1:0:0:0:0:0:0:0:http%3a//127.0.0.1%3a8088/http%3a//tvp_player.php?object_id=51656539:Poland In
    #### link
    #http%3a//tvp_player.php?object_id=51656539
    #uruchomienie testowe
    #streamlink -l debug -o /tmp/tvpstream.mp4 "http%3a//tvp_player.php?object_id=51656539" best

    player_url = 'https://www.tvp.pl/sess/tvplayer.php?object_id={0}&autoplay=true'

    _url_re = re.compile(r'https?://tvp_player.php\?object_id=')

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def getM3U(self,myURL):
        streams = []
        try:
            for s in HLSStream.parse_variant_playlist(self.session, myURL, name_fmt='{pixels}_{bitrate}').items():
                #log.debug('s = %s\n' % str(s))
                streams.append(s)
        except Exception as e:
            log.debug('getM3U() EXCEPTION: %s\n' % str(e))
        return streams
        
    def getMPD(self,myURL):
        streams = []
        try:
            streams = DASHStream.parse_manifest(self.session, myURL)
            #log.debug('streams = %s\n' % streams)
        except Exception as e:
            log.debug('getMPD() EXCEPTION: %s\n' % str(e))
        return streams
    
    def getHLSDL(self,myURL):
        streams = []
        CacheFileName = '/tmp/stream.ts'
        _cmd = ['/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/bin/hlsdl'] 
        _cmd.extend([myURL])
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
            log.info('FileCache:%s:%s' % ( processPID, CacheFileName ))
            #raise Exception('FileCache:%s:%s' % ( processPID, CacheFileName ))
            return
            #import time
            #time.sleep(2)
            #if os.path.exists(CacheFileName):
            #    return {"file_stream": FileStream(self.session, CacheFileName)} 
        else:
            raise Exception('ERROR initiating processHLSDL')
        return streams
    
    def _get_streams(self):
        self.url = self.url.replace('//tvp_player.php','//tvpstream.vod.tvp.pl/sess/tvplayer.php')
        #log.debug('self.url = %s' % self.url)
        
        id = re.compile(r'object_id=(\d+)',re.DOTALL).findall(self.url)[0]
        log.debug('id = %s' % id)

        prefer_stream_type = re.compile('&prefertype=([^&]+)',re.DOTALL).findall(self.url)
        if prefer_stream_type is None or len(prefer_stream_type) == 0:
            prefer_stream_type = 'auto'
        else:
            prefer_stream_type = prefer_stream_type[0]
        log.debug('prefer_stream_type = %s' % str(prefer_stream_type))
        
        url = 'http://www.tvp.pl/shared/cdn/tokenizer_v2.php?object_id='+id
        self.session.http.headers.update({'User-Agent': u'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'}) 
        res = self.session.http.get(url)
        log.debug('\n##############################res.text = %s\n##############################' % res.text)
        data = json.loads(res.text)
        stream_url = ''
        mpd_url = ''
        streams = []
        
        if data.get('status', 'NOT_PLAYABLE') == 'OK':
            for item in data.get('formats', []):
                log.debug('item = %s\n' % item)
                mimeType = item.get('mimeType', 'unknown')
                if mimeType in ('application/x-mpegurl', 'application/dash+xml'):
                    tmpURL = item.get('url', '')
                    if tmpURL.endswith('.m3u8') and stream_url == '':
                        stream_url = tmpURL
                    elif tmpURL.endswith('.mpd') and mpd_url == '':
                        mpd_url = tmpURL
                if stream_url != '' and mpd_url != '':
                    break
        elif id == '45417105': #wilno
            log.debug('Plansza TVP Wilno nadaje codziennie od 17:30 PL /18:30 LT')
            #stream_url = 'http://s.tvp.pl/files/portal/ss2/tvpstream/img/wilno-stream.jpg'
            raise Exception('E2MSG:text=TVP Wilno nadaje codziennie od 17:30 PL /18:30 LT&type=2&timeout=30')    
            return
        
        if stream_url == '' and mpd_url == '':
            log.debug('\n############## BRAK stream_url i mpd_url ################\ndata = %s\n##############################\n' % data)
        elif prefer_stream_type in ('auto','m3u8'):
            if len(streams) == 0 and stream_url.endswith('.m3u8'): streams = self.getM3U(stream_url)
            if len(streams) == 0 and mpd_url.endswith('.mpd'):    streams = self.getMPD(mpd_url)
        elif prefer_stream_type == 'mpd':
            if len(streams) == 0 and mpd_url.endswith('.mpd'):    streams = self.getMPD(mpd_url)
            if len(streams) == 0 and stream_url.endswith('.m3u8'): streams = self.getM3U(stream_url)
        elif prefer_stream_type == 'hlsdl':# hlsdl dziala chyba lepiej z hlsmulti, a taki jest w niektorych strumieniach
            if mpd_url.endswith('.mpd'): streams = self.getHLSDL(mpd_url)
        elif stream_url.endswith('.mp4'):
            streams.append(('vod', HTTPStream(self.session, stream_url)))

        log.debug('streams = %s\n' % streams)
        return streams
 


__plugin__ = tvpstream 