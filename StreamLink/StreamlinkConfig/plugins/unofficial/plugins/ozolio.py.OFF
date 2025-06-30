"""
  Ozolio Plugin for Streamlink by Billy2011.
  Version 0.1 / 2020-10-14
"""

import logging
import re

from streamlink.compat import quote
from streamlink.plugin import Plugin
from streamlink.plugin.api import validate
from streamlink.stream import HLSStream


class Ozolio(Plugin):
    _url_re = re.compile(r"https?://(?:www\.)?ozolio\.com/explore/(.+)")

    _sesapi_cid_url = "https://relay.ozolio.com//ses.api?cmd=init&oid=CID_{cid}&ver=5&channel=0&control=1&document={document}"
    _sesapi_sid_url = "https://relay.ozolio.com/ses.api?cmd=open&oid={sid}&output=1&format=M3U8"
    _sesapi_cid_schema = validate.Schema(
        {
            "session": {
                "id": validate.text,
            }
        },
        validate.get("session"),
    )
    _sesapi_sid_schema = validate.Schema(
        {
            "output": {
                "state": validate.contains("Active"),
                "media": validate.contains("LIVE"),
                "source": validate.url(),
            }
        },
        validate.get("output"),
        validate.get("source"),
    )

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        res = self._url_re.search(self.url)
        if res:
            res = self.session.http.get(self._sesapi_cid_url.format(cid=res.group(1), document=quote(self.url)))
            res = self.session.http.json(res, schema=self._sesapi_cid_schema)
            res = self.session.http.get(self._sesapi_sid_url.format(sid=res["id"]))
            m3u8_url = self.session.http.json(res, schema=self._sesapi_sid_schema)
            for s in HLSStream.parse_variant_playlist(self.session, m3u8_url).items():
                yield s


__plugin__ = Ozolio
