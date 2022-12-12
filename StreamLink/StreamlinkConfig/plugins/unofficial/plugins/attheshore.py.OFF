"""
  attheshore.com Plugin for Streamlink by Billy2011.
  Version 0.1 / 2020-10-15
"""

import re

from streamlink.plugin import Plugin
from streamlink.plugin.api.utils import itertags
from streamlink.stream import HLSStream


class AtTheShore(Plugin):
    _url_re = re.compile(r"https?://attheshore\.com/livecam-(.+)")
    _videoapi_url = "http://api.igv.com/v1.5/getVideoStream?apiKey=T1iSb7bCmg3UPxKC9pHAg4ykgMGPAjsg&id={camid}"

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        res = self._url_re.search(self.url)
        if res:
            res = self.session.http.get(self._videoapi_url.format(camid=res.group(1)), headers={"Referer": self.url})
            for tag in itertags(res.text, "source"):
                if "src" in tag.attributes:
                    url = tag.attributes.get("src")
                    if ".m3u8" in url:
                        for s in HLSStream.parse_variant_playlist(self.session, url).items():
                            yield s


__plugin__ = AtTheShore
