import logging
import re

from streamlink.plugin import Plugin, PluginError, pluginmatcher
from streamlink.plugin.api import useragents
from streamlink.utils import update_scheme
from streamlink.stream.hls import HLSStream

log = logging.getLogger(__name__)


@pluginmatcher(re.compile(
    r"https?://www.wetter.com/hd-live-webcams",
))

class wettercomwebcams(Plugin):
    #http://www.wetter.com/hd-live-webcams/deutschland/roettenbach-deutschland/560d13e66ad05/
    #data-video-url-rtmp="rtmp://94.228.211.161:1935/live/livecam012.stream"
    #data-video-url-mp4=""
    #data-video-url-hls="https://5811bd721519c.streamlock.net:1936/live/livecam012.stream/playlist.m3u8"
    
    _url_re = re.compile(r"https?://www.wetter.com/hd-live-webcams")

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        #self.session.set_option('hls-live-edge', 10)
        self.session.http.headers.update({'User-Agent': useragents.CHROME})
        res = self.session.http.get(self.url)
        #log.debug(res.text)
        address = None
        
        #linki bezposrednie
        _addrs = [ re.compile(r'[ ]*data-video-url-rtmp="([^"]+)"'),
                   re.compile(r'[ ]*data-video-url-mp4="([^"]+)"'),
                   re.compile(r'[ ]*data-video-url-hls="([^"]+)"')                   
                 ]
        for _addr in _addrs:
            _addr = _addr.search(res.text)
            if not _addr is None and _addr.group(1) != '':
                address = _addr.group(1)
                break
        
        #adres z linkiem
        if address is None:
            _addr = re.compile(r'[ ]* data-video-url-endpoint="([^"]+)"')
            _addr = _addr.search(res.text)
            if not _addr is None and _addr.group(1) != '':
                res = self.session.http.get(_addr.group(1))
                log.debug("res: %s" % res.text)
                address = re.compile(r'.*"(http[^"]+)"')
                address = address.search(res.text).group(1)
                address = address.replace(r'\/','/')

        log.debug("Found address: %s" % address)
        
        return {"hls": HLSStream(self.session, *(address,))}

__plugin__ = wettercomwebcams
