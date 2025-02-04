import logging
import re

from streamlink.plugin import Plugin, PluginError, pluginmatcher
from streamlink.plugin.api import useragents
from streamlink.utils import update_scheme
from streamlink.stream.hls import HLSStream

log = logging.getLogger(__name__)


@pluginmatcher(re.compile(
    r"https?://rtsp.me/embed/",
))

class rtspme(Plugin):
    _url_re = re.compile(r"https?://rtsp.me/embed/")
    _playlist_re = re.compile(r'[ ]*var n_url = "([^"]+)";')

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        self.session.set_option('hls-live-edge', 10)
        res = self.session.http.get(self.url)
        playlist_m = self._playlist_re.search(res.text)

        if playlist_m:
            address = playlist_m.group(1)
            log.debug("Found: '%s'" % address)
            return {"hls": HLSStream(self.session, *(address,))}
        else:
            log.debug("Could not find stream data")


__plugin__ = rtspme
