import logging
import re

from streamlink.plugin import Plugin, PluginError, pluginmatcher
from streamlink.plugin.api import useragents
from streamlink.utils import update_scheme
from streamlink.stream.hls import HLSStream

log = logging.getLogger(__name__)


@pluginmatcher(re.compile(
    r"https?://lookcam.pl/",
))

class lookcam(Plugin):
    #https://lookcam.pl/warszawa-plac-zamkowy/
    #<iframe class="embed-responsive-item" src="https://lookcam.live/player/MEzluwuAhC/" frameborder="0" scrolling="no" allowfullscreen></iframe>
    #https://lookcam.live/player/MEzluwuAhC/
    #<source src="https://big-edge01.cdn.wolfcloud.pl/lookcam/qnoWDLx0g1dp2ZY0KAXeGnM8lNrBJPjxbRz3wL4ObDW6Ek5oaxyQ9vqVZXGbdYQl/index.m3u8?token=jpbOHyQqiMtLRLfkIijCdw&amp;expires=1598286918" type="application/x-mpegURL" />
    #https://big-edge01.cdn.wolfcloud.pl/lookcam/qnoWDLx0g1dp2ZY0KAXeGnM8lNrBJPjxbRz3wL4ObDW6Ek5oaxyQ9vqVZXGbdYQl/index.m3u8?token=jpbOHyQqiMtLRLfkIijCdw&amp;expires=1598286918
    
    _url_re = re.compile(r"https?://lookcam.pl/")
    _url2_re = re.compile(r'<iframe.*embed-responsive-item.* src="([^"]+)"')
    _addr_re = re.compile(r'[ ]*source src="([^"]+)"')

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def cookiesToString(self, cookies):
        try:
            return "; ".join([str(x) + "=" + str(y) for x, y in cookies.get_dict().items()])
        except Exception as e:
            return str(e)

    def _get_streams(self):
        #self.session.set_option('hls-live-edge', 10)
        self.session.http.headers.update({'User-Agent': useragents.ANDROID})
        res = self.session.http.get(self.url)
        log.trace("Responce:\n %s" % res.text)
        log.debug("Cookies:\n %s" % self.cookiesToString(res.cookies))
        self.url = self._url2_re.search(res.text).group(1)
        if not self.url.startswith('http'):
            self.url = 'https://lookcam.live' + self.url
        res = self.session.http.get(self.url)
        log.trace("Responce2:\n %s" % res.text)
        log.debug("Cookies2:\n %s" % self.cookiesToString(res.cookies))
        try:
            address = self._addr_re.search(res.text).group(1)
            log.debug("Found address: %s" % address)
        except Exception as e:
            log.debug(str(e))
            #log.debug("For responce:\n %s" % res.text) 
            return
        
        return {"hls": HLSStream(self.session, *(address,))}

__plugin__ = lookcam
