import logging
import re

from streamlink.plugin import Plugin, PluginError, pluginmatcher
from streamlink.plugin.api import useragents
from streamlink.utils import update_scheme
from streamlink.stream.hls import HLSStream

log = logging.getLogger(__name__)


@pluginmatcher(re.compile(
    r"https?:\/\/(g[0-9]\.|)ipcamlive\.com\/player\/player\.php",
))

class ipcamlive(Plugin):
    #g0.ipcamlive.com/player/player.php?alias=kadan&autoplay=1
    _url_re = re.compile(r"https?:\/\/(g[0-9]\.|)ipcamlive\.com\/player\/player\.php")
    _addr_re = re.compile(r"[ ]*var address = '([^']+)';")
    _stID_re = re.compile(r"[ ]*var streamid = '([^']+)';")

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        self.session.set_option('hls-live-edge', 10)
        res = self.session.http.get(self.url)
        #log.debug(res.text)
        
        try:
            address = self._addr_re.search(res.text).group(1)
            log.debug("Found address: %s" % address)
        
            streamID = self._stID_re.search(res.text).group(1)
            log.debug("Found streamID: %s" % streamID)
        
            fullURL= '%s/streams/%s/stream.m3u8' %(address, streamID)
            log.debug("Built URL: %s" % fullURL)
        except Exception as e:
            log.debug(str(e))
            return
        
        return {"hls": HLSStream(self.session, *(fullURL,))} 

__plugin__ = ipcamlive
