import logging
import re

from streamlink.plugin import Plugin, PluginError, pluginmatcher
from streamlink.plugin.api import useragents
from streamlink.utils import update_scheme
from streamlink.stream.hls import HLSStream

log = logging.getLogger(__name__)


@pluginmatcher(re.compile(
    r"https?://(?:\w+)?balticlivecam\.com",
))

class BalticLivecam(Plugin):
    #https://balticlivecam.com/cameras/poland/gdansk/old-town-stare-miasto/

    _url_re = re.compile(r'https://(?:\w+)?balticlivecam\.com')
    _data_re = re.compile(r'''data\s*=\s*(?P<data>\{.*?});''', re.DOTALL)
    _data_2_re = re.compile(r'''(?P<name>\w+):\s?["']?(?P<data>[^"',\s]+)["']?(?:,|(?:\s+)?})''')

    _iframe_re = re.compile(r'''<iframe[^><]+src=["'](?P<url>[^"']+)["']''')
    _hls_re = re.compile(r'''["'](?P<url>[^"']+\.m3u8(?:[^"']+)?)["']''')

    api_url = 'https://balticlivecam.com/wp-admin/admin-ajax.php'

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    @classmethod
    def js_to_json_regex(cls, js_data):
        data_all = cls._data_2_re.findall(js_data)
        data_new = {}
        for name, data in data_all:
            data_new[name] = data
        return data_new

    def _get_streams(self):
        self.session.http.headers.update({'User-Agent': useragents.FIREFOX})
        log.debug('Version 2024-11-28')
        log.info('This is a custom plugin.')
        res = self.session.http.get(self.url)

        data = self._data_re.search(res.text)
        if data:
            log.debug('Found _data_re')
            data = self.js_to_json_regex(data.group(1))
            res = self.session.http.post(self.api_url, data=data)
            m = self._hls_re.search(res.text)
            if m:
                log.debug('Found _hls_re')
                hls_url = m.group('url')
                hls_url = update_scheme('http://', hls_url)
                log.debug('URL={0}'.format(hls_url))
                streams = HLSStream.parse_variant_playlist(self.session, hls_url)
                if not streams:
                    return {'live': HLSStream(self.session, hls_url)}
                else:
                    return streams

        iframe = self._iframe_re.search(res.text)
        if iframe:
            log.debug('Found _iframe_re')
            iframe_url = iframe.group('url')
            iframe_url = update_scheme('http://', iframe_url)
            log.debug('URL={0}'.format(iframe_url))
            return self.session.streams(iframe_url)


__plugin__ = BalticLivecam
