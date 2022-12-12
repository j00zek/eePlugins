import logging
import re

from streamlink.plugin import Plugin
from streamlink.plugin.api import useragents
from streamlink.utils import update_scheme
from streamlink.stream._ffmpegmux import FFMPEGMuxer

log = logging.getLogger(__name__)

def cookiesToString(cookies):
    try:
        return "; ".join([str(x) + "=" + str(y) for x, y in cookies.get_dict().items()])
    except Exception as e:
        return str(e)

class skylinewebcams(Plugin):
    #https://www.skylinewebcams.com/webcam/italia/lazio/roma/piazza-navona.html
    #source:"https://hddn00.skylinewebcams.com/live.m3u8?a=q92i5fipp4jsk7484kkf2u4nr2",
    
    _url_re = re.compile(r"https?://www.skylinewebcams.com/")
    _addr_re = re.compile(r"source:[\'\"]?([^\'\"]+)")

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        #self.session.set_option('hls-live-edge', 10)
        self.session.http.headers.update({'User-Agent': useragents.CHROME})
        res = self.session.http.get(self.url)
        log.trace("Responce:\n %s" % res.text)
        log.trace("Cookies:\n %s" % cookiesToString(res.cookies))
        
        try:
            address = self._addr_re.search(res.text).group(1)
            log.debug("Found address: %s" % address)
        except Exception as e:
            log.debug(str(e))
            log.debug("For responce:\n %s" % res.text)
            return
        
        return {"rtsp_stream": FFMPEGMuxer(self.session, *(address,), is_muxed=False, format='mpegts', vcodec = 'copy', acodec = 'copy' )}

__plugin__ = skylinewebcams
