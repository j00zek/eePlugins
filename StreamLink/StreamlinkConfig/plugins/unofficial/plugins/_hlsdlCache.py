import logging
import re

from streamlink.plugin import Plugin, PluginError, pluginmatcher
from streamlink.plugin.api import useragents
from streamlink.utils import update_scheme
#from streamlink.stream._ffmpegmux import FFMPEGMuxer #20230223
#from streamlink.stream.ffmpegmux import FFMPEGMuxer #20230223
#from streamlink.stream._hlsdl import HLSDL #20230223
#from streamlink.stream.file import FileStream

log = logging.getLogger(__name__)

@pluginmatcher(re.compile(
    r"https?://hlsdlCache.",
))

class hlsdlCache(Plugin):
    
    _url_re = re.compile(r"https?://hlsdlCache.")
    _addr_re = re.compile(r'[ ]*data-stream="([^"]+)"')
    #_addr_re = re.compile(r'[ ]*src="blob:([^"]+)"')

    @classmethod
    def can_handle_url(cls, url):
        return cls._url_re.match(url) is not None

    def _get_streams(self):
        address = self.url.replace('hlsdlCache.','')
        log.debug("Real address: %s" % address)

        CacheFileName = '/tmp/stream.ts'
        _cmd = ['/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/bin/hlsdl'] 
        _cmd.extend([address])
        _cmd.extend(['-b', '-f', '-o', CacheFileName])
        log.debug("hlsdl command: {0}".format(' '.join(_cmd))) 
        import subprocess
        from subprocess import DEVNULL # Python 3.
        processHLSDL = subprocess.Popen(_cmd, stdout= DEVNULL, stderr= DEVNULL )
        if processHLSDL: 
            processPID = processHLSDL.pid
            log.info('FileCache:%s:%s:%s' % ( processPID, CacheFileName, 20 )) 
            #raise Exception('FileCache:%s:%s' % ( processPID, CacheFileName ))
        else:
            raise Exception('ERROR initiating HLSDL process')
        return

__plugin__ = hlsdlCache
