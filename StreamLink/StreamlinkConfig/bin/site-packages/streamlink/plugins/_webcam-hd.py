import logging
import re

from streamlink.plugin import Plugin, PluginError, pluginmatcher
from streamlink.plugin.api import useragents
from streamlink.utils import update_scheme
from streamlink.stream.hls import HLSStream

log = logging.getLogger(__name__)


@pluginmatcher(re.compile(
    r"https?://webcam-hd.fr/webcam",
))

class webcamHD(Plugin):
    #https://webcam-hd.fr/webcam?id=146&camera=la-sauzaie--bretignolles-sur-mer
    #frameBorder="0" scrolling="no" src="https://platforms5.joada.net/embeded/embeded.html?uuid=22fe66d0-dd4f-45a3-3332-3130-6d61-63-a6ab-7a9db0ee0884d&type=live&liveicon=0&vsheader=0">
    #22fe66d0-dd4f-45a3-3332-3130-6d61-63-a6ab-7a9db0ee0884d
    
    _url_re = re.compile(r"https?://webcam-hd.fr/webcam")
    _joada_re = re.compile(r'src=".*joada.*uuid=([^&]+)&.*type=live.*')

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        #self.session.set_option('hls-live-edge', 10)
        self.session.http.headers.update({'User-Agent': useragents.CHROME})
        res = self.session.http.get(self.url)
        #log.debug(res.text)
        
        try:
            UUID = self._joada_re.search(res.text).group(1)
            log.debug("Found UUID: %s" % UUID)
            address = "https://deliverys2.joada.net/contents/encodings/live/%s/master.m3u8" % str(UUID)
            
        except Exception as e:
            log.debug(str(e))
            return
        
        return {"hls": HLSStream(self.session, *(address,))}

__plugin__ = webcamHD
