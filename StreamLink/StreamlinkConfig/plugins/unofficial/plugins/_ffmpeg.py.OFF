# -*- coding: utf-8 -*-
import logging
import re

from streamlink.plugin import Plugin
from streamlink.plugin.api import validate
from streamlink.stream._ffmpegmux import FFMPEGMuxer

log = logging.getLogger(__name__)

class ffmpegCMDplugin(Plugin):
    _url_re = re.compile(r".*ffmpeg\|.*")

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        log.debug("ffmpegCMDplugin._get_streams() >>>")
        params = self.url.split('ffmpeg|')[1].split('|')
        url = params.pop(0)
        log.debug("\t url: %s" % url)
        #params in url
        formatVal = "matroska"
        vcodecVal = 'copy'
        acodecVal = 'copy'
        ffmpegParams= {}
        if len(params) > 0:
            log.debug("\t ffmpeg params: {0}".format(' '.join(params)))
            for param in params:
                if param.startswith('format='): formatVal = param.split('=')[1]
                if param.startswith('vcodec='): vcodecVal = param.split('=')[1]
                if param.startswith('acodec='): acodecVal = param.split('=')[1]
        else:
            log.debug("\t additional ffmpeg params NOT provided")
          
        return {"ffmpeg_stream": FFMPEGMuxer(self.session, *(url,), is_muxed=False, format=formatVal, vcodec = vcodecVal, acodec = acodecVal, extraParams = ffmpegParams)}


__plugin__ = ffmpegCMDplugin
