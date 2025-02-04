import logging
import re

from streamlink.plugin import Plugin, PluginError, pluginmatcher
from streamlink.plugin.api import useragents
from streamlink.utils import update_scheme
from streamlink.stream.hls import HLSStream

log = logging.getLogger(__name__)


@pluginmatcher(re.compile(
    r"https?://www.skylinewebcams.com/",
))

class skylinewebcams(Plugin):
    #https://www.skylinewebcams.com/webcam/italia/lazio/roma/piazza-navona.html
    #source:"https://hddn00.skylinewebcams.com/live.m3u8?a=q92i5fipp4jsk7484kkf2u4nr2",
    
    _url_re = re.compile(r"https?://www.skylinewebcams.com/")
    _addr_re = re.compile(r"source:[\'\"]?([^\'\"]+)")

    def cookiesToString(self,cookies):
        try:
            return "; ".join([str(x) + "=" + str(y) for x, y in cookies.get_dict().items()])
        except Exception as e:
            return str(e)

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        #self.session.set_option('hls-live-edge', 10)
        self.session.http.headers.update({'User-Agent': useragents.CHROME})
        res = self.session.http.get(self.url)
        log.trace("Responce:\n %s" % res.text)
        log.trace("Cookies:\n %s" % self.cookiesToString(res.cookies))
        
        try:
            address = self._addr_re.search(res.text).group(1)
            if address.startswith('livee.m3u8'):
                address = 'https://hd-auth.skylinewebcams.com/' + address.replace('livee', 'live')
            log.debug("Found address: %s" % address)
        except Exception as e:
            log.debug(str(e))
            log.debug("For responce:\n %s" % res.text)
            return
        
        return {"hls": HLSStream(self.session, *(address,))}

__plugin__ = skylinewebcams
