import logging
import re

from streamlink.plugin import Plugin
from streamlink.plugin.api import useragents
from streamlink.utils import update_scheme
from streamlink.stream._ffmpegmux import FFMPEGMuxer

log = logging.getLogger(__name__)


class liveincam(Plugin):
    #https://www.liveincam.com/en/cam/nosy-be-nosy-be-andilana
    # >>>
    # >>>
    
    _url_re = re.compile(r"https?://www.liveincam.com")
    _addr_re = re.compile(r'[ ]*source:"([^"]+)"')

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        #self.session.set_option('hls-live-edge', 10)
        self.session.http.headers.update({'User-Agent': useragents.CHROME})
        res = self.session.http.get(self.url)
        #log.debug(res.text)
        
        try:
            address = self._addr_re.search(res.text).group(1)
            if not address.startswith('https:') or not address.startswith('http:'):
                address = 'https:' + address
            log.debug("Found address: %s" % address)
        except Exception as e:
            log.debug(str(e))
            return
        
        return {"rtsp_stream": FFMPEGMuxer(self.session, *(address,), is_muxed=False, format='mpegts', vcodec = 'copy', acodec = 'copy' )}

__plugin__ = liveincam
