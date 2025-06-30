#!/usr/bin/env python
import os
import re
import sys
import time
import errno
try:
    import simplejson as json
except ImportError:
    import json
import atexit
import socketserver
import streamlink.logger as logger
import http.server as SimpleHTTPServer
import subprocess
from contextlib import suppress
from streamlink import Streamlink
from streamlink.options import Options
from streamlink.utils.parse import parse_qsd
from streamlink._version import __version__ as streamlink_ver
from socket import socket, AF_INET, SOCK_DGRAM
from urllib.parse import unquote, urlparse, urlencode
from signal import signal, SIGTERM
from copy import deepcopy
from abc import abstractmethod


__copyright__ = '©Dorik1972 aka Pepsik mod for SLK j00zek'
__version__ = '1.0.2'
__updated__ = '2024-03-01'
__description__ = 'Streamlink library proxy daemon for Enigma2 framework'  # https://streamlink.github.io
__author_email__ = 'pepsik@ukr.net'
__license__ = 'GNU GENERAL PUBLIC LICENSE version 3'


srvname = 'streamlinkproxySRV'
logger.root.name = srvname
logger.basicConfig()
timeout = 20
sort_streams = lambda s: [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]
_streams = lambda s: dict(sorted(s.items(), key=lambda x: sort_streams(x[0])))


class RequestHandler(SimpleHTTPServer.BaseHTTPRequestHandler):

    server_version = f'{srvname[:10].capitalize()} {srvname[10:]}'
    protocol_version = 'HTTP/1.1'
    ### initiate a streamlink session with the specified parameters most suitable for Enigma2 "media players"
    ### to krytyczne, jak sie wywala wpada w petle!!!!!
    streamlink: Streamlink = Streamlink({
                            "stream-timeout": timeout,
                            "stream-segment-threads": 6,
                            "hls-segment-stream-data": True,
                            "hls-audio-select": "*",
                            "ringbuffer-size": 1024 * 1024 * 32,
                            "ffmpeg-no-validation": True,
                        }, plugins_builtin=True)

    default_options = deepcopy(streamlink.options)


    def setup(self):
        SimpleHTTPServer.BaseHTTPRequestHandler.setup(self)
        self.request.settimeout(timeout)

    def log_message(self, format, *args):
        pass

    def log_request(self, code='-', size='-'):
        logger.root.info(f'Request from: {self.address_string()} - {unquote(self.requestline)} {code} {size}')
        logger.root.trace(f'Request headers:\n{json.dumps(dict(self.headers), indent=2)}')

    def do_GET(self):
        with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n") #for safety to not get GS due to lack of memory
        subprocess.Popen('/usr/bin/killall -q exteplayer3;/usr/bin/killall -q -9 exteplayer3', shell=True)
        """Respond to a GET request."""
        self.send_response(200)
        self.send_header("Content-type", "video/mp2t")
        self.send_header("Transfer-Encoding", "chunked")
        self.send_header("Connection", "keep-alive")
        self.send_header("Keep-Alive", "timeout=%s, max=100" % timeout)
        self.send_header("Accept-Ranges", "none")
        self.end_headers()
        self.streamlink.options = deepcopy(self.default_options)
        try:
            url = unquote(self.path[1:])
            parsed_url = urlparse(url)
            query = parse_qsd(parsed_url.query)
            default_stream = query.pop('default-stream', None)
            plugin_options = Options()
            pluginname, pluginclass, _ = self.streamlink.resolve_url(url)
            for k in [*query]:
                if k in self.streamlink.options:
                    self.streamlink.set_option(k, query.pop(k))
                elif k.startswith(pluginname):
                    plugin_options.set(k.replace(f'{pluginname}-', ''), query.pop(k))
            url = parsed_url._replace(query=urlencode(query)).geturl()
            if not (streams := _streams({k[:k.rfind('_')] if "_alt" in k else k:v for k,v in pluginclass(self.streamlink, url, plugin_options).streams().items() if k[:1].isdigit() and v.__class__.__name__ != 'MuxedStream' or 'live' in k})):
                raise ValueError
            logger.root.debug(f'{pluginname.upper()} plugin found sreams: {[*streams]}')
        except Exception as err:
            if 'NoPluginError' in err.__class__.__name__:
                msg = f'No suitable streamlink plugin was found for the given URL: {url}'
            elif 'ValueError' in err.__class__.__name__:
                msg = f'No playable streams found for the given URL: {url}'
            else:
                msg = f'{pluginname.upper()} plugin exception: {err}'
            logger.root.error(msg)
            url = 'https://devstreaming-cdn.apple.com/videos/streaming/examples/bipbop_16x9/bipbop_16x9_variant.m3u8'
            streams = _streams({k:v for k,v in self.streamlink.streams(url).items() if k[:1].isdigit()})
        finally:
            try:
                with suppress(BrokenPipeError, ConnectionResetError, OSError):
                    with streams.get(default_stream, streams.popitem()[1]).open() as fd:
                        fsrc_read = fd.read
                        fdst_write = self.wfile.write
                        COPY_BUFSIZE = 64 * 1024
                        while chunk := fsrc_read(COPY_BUFSIZE):
                            fdst_write(b'%X\r\n%s\r\n' % (len(chunk),chunk))
            except Exception as err:
                logger.root.error(f"Unexpected error occurs: {err}")


class Daemon:
    """
    A generic daemon class.
    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile: str) -> None:
        self.pidfile = pidfile

    def _daemonize(self) -> None:
        if (pid := os.fork()) > 0:
            sys.exit(0)  # End parent
        # Change some defaults so the daemon doesn't tie up dirs, etc.
        os.setsid()
        os.umask(0)
        # Fork a child and end parent (so init now owns process)
        if (pid := os.fork()) > 0:
            with open(self.pidfile, "w+") as fd:
                fd.write(f"{pid}\n")
            sys.exit(0)  # End parent

        atexit.register(self._cleanup)
        signal(SIGTERM, self._cleanup)
        # Close STDIN, STDOUT and STDERR so we don't tie up the controlling terminal
        for fd in range(3):
            try:
                os.close(fd)
            except OSError:
                pass
        # Reopen the closed file descriptors so other os.open() calls don't
        # accidentally get tied to the stdin etc.
        os.open("/dev/null", os.O_RDWR)  # standard input (0)
        os.dup2(0, 1)                    # standard output (1)
        os.dup2(0, 2)                    # standard error (2)


    def _cleanup(self) -> None:
        if os.path.isfile(self.pidfile):
            os.unlink(self.pidfile)

    def _pid_running(self, pid: str) -> bool:
        try:
            os.kill(pid, 0)
        except OSError as err:
            if err.errno == errno.ESRCH:
                return False
        return True

    def get_pid(self) -> int or None:
        try:
            with open(self.pidfile, "r") as pf:
                return int(pf.readline().strip())
        except (ValueError, FileNotFoundError):
            return None

    def is_running(self) -> bool:
        return (True, False)[self.get_pid() is None]

    def start(self) -> None:
        # Check for a pidfile to see if the daemon already runs
        if self.is_running():
            logger.root.warning(f"pidfile {self.pidfile} already exist. '{srvname.capitalize()}' daemon already running?\n")
            sys.exit(1)
        # Start the daemon
        self._daemonize()
        self.run()

    def stop(self) -> None:
        if not self.is_running():
            logger.root.error(f"pidfile {self.pidfile} does not exist. '{srvname.capitalize()}' daemon not running?\n")
        # Kill the daemon and wait until the process is gone
        if pid := self.get_pid():
            os.kill(pid, SIGTERM)
            for _ in range(25):  # 5 seconds
                time.sleep(0.2)
                if not self._pid_running(pid):
                    break
            else:
                logger.root.warning(f"Couldn't stop the '{srvname}' daemon. A broadcast may be in progress.\n")

    def restart(self) -> None:
        if self.is_running():
            self.stop()
        self.start()

    @abstractmethod
    def run(self) -> None:
        """
        """

class StreamlinkDaemon(Daemon):

    def run(self) -> None:
        start()


def start():
    try:
        ip = [(s.connect(('1.1.1.1', 0)), s.getsockname()[0], s.close()) for s in [socket(AF_INET, SOCK_DGRAM)]][0][1]
    except:
        ip = 'localhost'
    socketserver.ForkingTCPServer.allow_reuse_address = True
    with socketserver.ForkingTCPServer(("", 8088), RequestHandler) as server:
        logger.root.info(f"{srvname.capitalize()} wersja serwera {__version__}, zasób - {ip}:{server.server_address[1]}")
        logger.root.debug(f'Biblioteka Steamlink w wersji: {streamlink_ver}')
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.root.info(f"{srvname.capitalize()} serwer zatrzymany")
        except Exception as err:
            logger.root.error(f"{srvname.capitalize()} wystąpił nieznany błąd: {err}")

if __name__ == "__main__":
    daemon = StreamlinkDaemon("/var/run/%s.pid" % srvname)
    if len(sys.argv) in (2,3):
        if "start" == sys.argv[1]:
            daemon.start()
        elif "stop" == sys.argv[1]:
            daemon.stop()
        elif "restart" == sys.argv[1]:
            daemon.restart()
        elif "manualstart" == sys.argv[1]:
            if daemon.is_running():
                daemon.stop()
            if len(sys.argv) == 3:
                _loglevel = {
                    'CRITICAL': logger.CRITICAL,
                    'ERROR': logger.ERROR,
                    'WARNING': logger.WARNING,
                    'INFO': logger.INFO,
                    'DEBUG': logger.DEBUG,
                    'TRACE': logger.TRACE,
                    }.get(sys.argv[2], logger.INFO)
            else:
                _loglevel = logger.INFO
            logger.root.setLevel(_loglevel)
            if not daemon.is_running():
                start()
        else:
            print("Nieznana komenda")
            sys.exit(2)
        sys.exit(0)
    else:
        print(f"usage: {os.path.basename(sys.argv[0])} start|stop|restart|manualstart [CRITICAL|ERROR|WARNING|INFO|DEBUG|TRACE]")
        sys.exit(2)
