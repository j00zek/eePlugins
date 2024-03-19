import re

from streamlink.exceptions import PluginError
from streamlink.plugin import Plugin, PluginError, pluginmatcher
#from streamlink.plugin.api import http
from streamlink.plugin.api import useragents
from streamlink.stream import HLSStream
from streamlink.stream import HTTPStream

_url_re = re.compile(r"http(s)?://(www\.)?popler.tv/live/TawizjaTV")
_RE_PLAYLIST = re.compile(r'src:\s*"([^"]+)"') 


@pluginmatcher(re.compile(
    r"http(s)?://(www\.)?popler.tv/live/TawizjaTV",
))

class Tawizja(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    def _get_streams(self):
        res = self.session.http.get(self.url)
        text = res.text 
        playlist_url = _RE_PLAYLIST.search(text).group(1) 
        if playlist_url.startswith("//"): playlist_url='http:'+playlist_url
        hls_streams = HLSStream.parse_variant_playlist(
            self.session,
            playlist_url,
            headers={'Referer': self.url, 'User-Agent': useragents.ANDROID}
        )
        for s in hls_streams.items():
            yield s


__plugin__ = Tawizja
