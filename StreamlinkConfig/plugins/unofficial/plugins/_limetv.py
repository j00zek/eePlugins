import logging
import re

from streamlink.plugin import Plugin
from streamlink.plugin.api import useragents
from streamlink.utils import update_scheme
from streamlink.stream._ffmpegmux import FFMPEGMuxer
from streamlink.stream import HLSStream 

log = logging.getLogger(__name__)


class PLUGINNAME(Plugin):
    #### Przykladowy link do kanalu
    #https://limehd.tv/lime-man lub https://stv.limehd.tv/lime-man
    #### kawalek kodu strony gdzie jest adres aktywnego strumienia
    # myPlayer.src({"src":"https:\/\/mhd.iptv2022.com\/p\/ytCAXCtghN74zVnP6hlPtw,1604901016\/streaming\/lime-man\/324\/vm2w\/playlist.m3u8","type":
    #### adres z powyzszego kawalka
    #http://mhd.iptv2022.com/p/ytCAXCtghN74zVnP6hlPtw,1604901016/streaming/lime-man/324/vm2w/playlist.m3u8
    
    _url_re = re.compile(r"https?://limehd.tv/|https?://stv.limehd.tv/")

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        #self.session.set_option('hls-live-edge', 10)
        self.session.http.headers.update({'User-Agent': useragents.CHROME})
        res = self.session.http.get(self.url)
        #log.debug(res.text)
        
        myName = self.url.rsplit("limehd.tv/")[1].replace("/","")
        searchesList = ['myPlayer\.src\({"src":"([^"]+)"' , 
                        "'(http:[^']*streaming[^']*%s[^']*)'" % myName ,
                        ]
        for searchRegEx in searchesList:
            searchRet = re.search(searchRegEx, res.text)
            if searchRet:
                break
        
        try:
            address = searchRet.group(1)
            address = address.replace('\/','/')
            log.debug("Found address: %s" % address)
        except Exception as e:
            log.debug(str(e))
            return
        
        return {"rtsp_stream": FFMPEGMuxer(self.session, *(address,), is_muxed=False, format='mpegts', vcodec = 'copy', acodec = 'copy' )}
__plugin__ = PLUGINNAME
