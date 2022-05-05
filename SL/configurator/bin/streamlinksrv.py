#!/usr/bin/python
#
# Linux Python2/3 Streamlink Daemon
#
# Copyright (c) 2017 - 2021 Billy2011 @vuplus-support.org
# Copyright (c) 2021 jbleyel (python3 mod)
#                                          
# License: GPLv2+
#
# mod j00zek 2020-2021
# changes:
# - connection with e2settings
# - proceeding url parameters according to html standard
# - using hlsdl for some m3u services

try:
    from streamlink import jtools
except Exception:
    import jtools
import os
jtools.killSRVprocess(os.getpid())
jtools.cleanCMD()

""" Streamlink Daemon """

__version__ = "1.8.3"

import atexit
import errno
import logging
import os
import platform
import re
import shutil
import signal
import socket
import sys
import time
import traceback
import warnings
from platform import node as hostname

from requests import __version__ as requests_version
from six import PY2, iteritems, itervalues
from six.moves.urllib_parse import unquote
from websocket import __version__ as websocket_version

if PY2:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from SocketServer import ForkingMixIn
else:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from socketserver import ThreadingMixIn as ForkingMixIn

try:
    from socks import __version__ as socks_version
except ImportError:
    socks_version = "N/A"

import streamlink.logger as logger
from streamlink import NoPluginError, NoStreamsError, PluginError, StreamError
from streamlink import Streamlink
from streamlink import StreamlinkError
from streamlink import __version__ as streamlink_version
from streamlink import __version_date__ as streamlink_version_date #wymaga dodania w __init__.py linia 14: __version_date__ = get_versions()['date']
from streamlink import plugins
from streamlink.exceptions import FatalPluginError
from streamlink.stream import HTTPStream
from streamlink.stream.ffmpegmux import MuxedStream

try:
    from streamlink import opts_parser
    from streamlink.opts_parser import *
    from streamlink.opts_parser import __version__ as opts_parser_version
except ImportError:
    opts_parser_version = "N/A"

try:
    from youtube_dl.version import __version__ as ytdl_version
except ImportError:
    ytdl_version = "N/A"

PORT_NUMBER = jtools.GetPortNumber()
_loglevel = LOGLEVEL = jtools.GetLogLevel()

if jtools.LogToFile() :
    logging.basicConfig(filename= jtools.GetLogFileName(),
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.NOTSET)
    
# do not change
LOGGER = logging.getLogger('streamlink.streamlinksrv')
STREAM_SYNONYMS = ["best", "worst", "best-unfiltered", "worst-unfiltered"]
PARSER = None
PLUGIN_ARGS = False



#
# setup options
#
def setOptions(streamlink):
    """
    main config file /etc/streamlink/config
    plugins config files /etc/streamlink/config/plugins
    
    As of version 1.0.5, it's possible to save the options or plug-in-specific options in configuration files: https://streamlink.github.io/cli.html#configuration-file

    You can also append these options to URL.
    Example for commandline streamlink client:
        streamlink https://pilot.wp.pl/api/v1/channel/158 720,best --hls-segment-threads=3
        
    Example HTTP URL:
        http://127.0.0.1:8088/https://pilot.wp.pl/api/v1/channel/11;SLARGS;quality=720,best;--hls-segment-threads=3

    To test streamlinksrv from commandline:
        curl "http://127.0.0.1:8088/https://pilot.wp.pl/api/v1/channel/11;SLARGS;quality=720,best;--hls-segment-threads=3" -o /dev/null
    """
    pass
    
def resolve_stream_name(streams, stream_name):
    if stream_name in STREAM_SYNONYMS and stream_name in streams:
        for name, stream in iteritems(streams):
            if stream is streams[stream_name] and name not in STREAM_SYNONYMS:
                return name

    return stream_name

def format_valid_streams(plugin, streams):
    delimiter = ", "
    validstreams = []

    for name, stream in sorted(iteritems(streams), key=lambda stream: plugin.stream_weight(stream[0])):
        if name in STREAM_SYNONYMS:
            continue

        def synonymfilter(n):
            return stream is streams[n] and n is not name

        synonyms = list(filter(synonymfilter, streams.keys()))

        if len(synonyms) > 0:
            joined = delimiter.join(synonyms)
            name = "{0} ({1})".format(name, joined)

        validstreams.append(name)

    return delimiter.join(validstreams)

def test_stream(plugin, args, stream):
    prebuffer = None
    retry_open = args.retry_open if True else 1
    for i in list(range(retry_open)):
        stream_fd = None
        try:
            stream_fd = stream.open()
            LOGGER.debug("Pre-buffering 8192 bytes")
            prebuffer = stream_fd.read(8192)
        except StreamError as err:
            LOGGER.error("Try {0}/{1}: Could not open stream {2} ({3})".format(i + 1, retry_open, stream, err))
            return stream_fd, prebuffer
        except IOError as err:
            stream_fd.close()
            LOGGER.error("Failed to read data from stream: {0}".format(err))
        else:
            break

    if not prebuffer:
        if stream_fd is not None:
            stream_fd.close()
        LOGGER.error("No data returned from stream")

    return stream_fd, prebuffer
    
def log_current_arguments(streamlink, args, url, quality):
    global PARSER, LOGGER

    if not logger.root.isEnabledFor(logging.DEBUG):
        return

    sensitive = set()
    for pname, plugin in iteritems(streamlink.plugins):
        for parg in plugin.arguments:
            if parg.sensitive:
                sensitive.add(parg.argument_name(pname))

    LOGGER.debug("Arguments:")
    LOGGER.debug(" url={0}".format(url))
    LOGGER.debug(" stream={0}".format(quality.split(",")))
    for action in PARSER._actions:
        if not hasattr(args, action.dest):
            continue
        value = getattr(args, action.dest)
        if action.default != value:
            name = next(  # pragma: no branch
                (option for option in action.option_strings if option.startswith("--")), action.option_strings[0]
            ) if action.option_strings else action.dest
            LOGGER.debug(" {0}={1}".format(name, value if name not in sensitive else '*' * 8))

def sendHeaders(http, status=200, type="text/html"):
    http.send_response(status)
    http.send_header("Server", "Enigma2 Streamlink")
    http.send_header("Content-type", type)
    http.end_headers()

def sendOfflineMP4(http, send_headers=True, file2send="/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/streams/offline.mp4"):
    LOGGER.debug("Send Offline clip: %s" % file2send)
    if send_headers:
        sendHeaders(http, type="video/mp4")

    http.wfile.write(open(file2send, "rb").read())
    http.wfile.close()

def sendCachedFile(http, send_headers=True, pid=0, file2send=None):
    LOGGER.debug("sendCachedFile(send_headers={0}, pid={1}, file2send={2})".format(str(send_headers), pid, file2send))
    if file2send is None:
        return

    #waiting for cache file
    for x in range(1, 10):
        if not os.path.exists(file2send):
            LOGGER.debug("\twaiting for cache file {0} ms".format(int(1000 * 0.1 * x) ))
            time.sleep(0.1)
        else:
            break
            
    #filling buffer
    initialBuffer = 8192 * 10
    for x in range(1, 10):
        currBufferSize = os.path.getsize(file2send)
        LOGGER.debug("\tfilling initial buffer {0} / {1}".format(currBufferSize, initialBuffer ))
        if int(currBufferSize) >= int(initialBuffer):
            LOGGER.debug("\tbuffered data: {0}".format(currBufferSize ))
            break
        else:
            LOGGER.debug("\tfilling initial buffer {0} / {1}".format(currBufferSize, initialBuffer ))
            time.sleep(0.1)

    if send_headers:
        sendHeaders(http, type="video/mp4")

    CachedFile = open(file2send, "rb")
    
    readBufferSize = 0
    while not CachedFile.closed:
        try:
            currBufferSize = int(os.path.getsize(file2send))
            LOGGER.debug("\t data in buffer: {0} (read {1} / total {2})".format((currBufferSize - readBufferSize), readBufferSize, currBufferSize ))
            data = CachedFile.read(8192)
            if len(data):
                readBufferSize += len(data)
                http.wfile.write(data)
                time.sleep(0.05)
            else:
                break
            
        except IOError:
            log.error("sendCachedFile aborted")
            os.system('kill -s 9 %s;killall hlsdl' % pid)
            return
    http.wfile.close()
    if int(pid) > 1000:
        os.system('kill -s 9 %s;killall hlsdl' % pid)
        if os.path.exists('/proc/%s') % pid:
            LOGGER.debug("Error killing pid {0}".format(pid))
        else:
            LOGGER.debug("pid {0} has been killed".format(pid))
            
def stream_to_url(stream):
    try:
        return stream.to_url()
    except TypeError:
        return None
            
def Stream(streamlink, http, url, argstr, quality):
    global PARSER, _loglevel

    if url.startswith('remoteE2/'):
        url = jtools.remoteE2(url)
        E2url = True
    else:
        E2url = False
      
    fd = None
    not_stream_opened = True
    try:
        setOptions(streamlink) # setup default options

        # setup plugin, http & stream specific options
        args = plugin = None
        if PARSER:
            global PLUGIN_ARGS
            if not PLUGIN_ARGS:
                PLUGIN_ARGS = setup_plugin_args(streamlink)
            config_files, plugin = setup_config_files(streamlink, url)
            if config_files or argstr:
                arglist = argsplit(" -{}".format(argstr[0])) if argstr else []
                try:
                    args = setup_args(arglist, config_files=config_files, ignore_unknown=False)
                except Exception:
                    return sendOfflineMP4(http, send_headers=not_stream_opened, file2send="/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/streams/wrongURLargs.mp4")
                else:
                    _loglevel = args.loglevel
                    logger.root.setLevel(_loglevel)
                    setupHttpSession(streamlink, args)
                    setupTransportOpts(streamlink, args)

        if not plugin:
            plugin = streamlink.resolve_url(url)

        if PARSER and PLUGIN_ARGS and args:
            setup_plugin_options(streamlink, plugin, args)
            log_current_arguments(streamlink, args, url, quality)

        LOGGER.info("Found matching plugin {0} for URL {1}".format(plugin.module, url))
        if args:
            streams = plugin.streams(stream_types=args.stream_types, sorting_excludes=args.stream_sorting_excludes)

        if any((not streams, not args)):
            LOGGER.error("No playable streams found on this URL: {0}".format(url))
            return sendOfflineMP4(http, send_headers=not_stream_opened, file2send="/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/streams/noStreamsFound.mp4")

        LOGGER.info("Available streams:\n{0}".format(format_valid_streams(plugin, streams)))
        stream = None
        for stream_name in (resolve_stream_name(streams, s.strip()) for s in quality.split(',')):
            if stream_name in streams:
                stream = True
                break

        if not stream:
            if "best" in streams:
                stream_name = "best"
                LOGGER.info("The specified stream(s) '{0}' could not be found, using '{1}' stream".format(quality, stream_name))
            else:
                LOGGER.error("The specified stream(s) '{0}' could not be found".format(quality))
                return sendOfflineMP4(http, send_headers=not_stream_opened)

        if not stream_name.endswith("_alt") and stream_name not in STREAM_SYNONYMS:
            def _name_contains_alt(k):
                return k.startswith(stream_name) and "_alt" in k

            alt_streams = list(filter(lambda k: _name_contains_alt(k), sorted(streams.keys())))
        else:
            alt_streams = []

        if opts_parser_version >= "0.2.8" and args.http_add_audio:
            http_add_audio = HTTPStream(streamlink, args.http_add_audio)
        else:
            http_add_audio = False

        stream_names = [stream_name] + alt_streams
        for stream_name in stream_names:
            stream = streams[stream_name]
            stream_type = type(stream).shortname()
            
            if http_add_audio and stream_type in ("hls", "http", "rtmp"):
                stream = MuxedStream(streamlink, stream, http_add_audio, add_audio=True)
                stream_type = "muxed-stream"

            LOGGER.info("Opening stream: {0} ({1})".format(stream_name, stream_type))
            if stream_type in args.player_passthrough:
                LOGGER.debug("301 Passthrough - URL: {0}".format(stream_to_url(stream)))
                http.send_response(301)
                http.send_header("Location", stream_to_url(stream))
                return http.end_headers()

            fd, prebuffer = test_stream(plugin, args, stream)
            if prebuffer:
                break

        if not prebuffer:
            raise StreamError("Could not open stream {0}, tried {1} times, exiting", stream, args.retry_open)

        LOGGER.debug("Writing stream to player")
        not_stream_opened = False
        sendHeaders(http)
        http.wfile.write(prebuffer)
        shutil.copyfileobj(fd, http.wfile)
    except NoPluginError:
        LOGGER.error("No plugin can handle URL: {0}".format(url))
        sendOfflineMP4(http, send_headers=not_stream_opened, file2send="/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/streams/noPluginFound.mp4")
    except PluginError as err:
        LOGGER.error("Plugin error: {0}".format(err))
        sendOfflineMP4(http, send_headers=not_stream_opened, file2send="/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/streams/PluginError.mp4")
    except FatalPluginError as err:
        LOGGER.error("Fatal Plugin error: {0}".format(err))
        sendOfflineMP4(http, send_headers=not_stream_opened, file2send="/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/streams/PluginFatalError.mp4")
    except StreamError as err:
        LOGGER.error("Stream Error: {0}".format(err))
        sendOfflineMP4(http, send_headers=not_stream_opened, file2send="/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/streams/noStreamsFound.mp4")
    except NoStreamsError as err:
        LOGGER.error("No Streams Error: {0}".format(err))
        sendOfflineMP4(http, send_headers=not_stream_opened, file2send="/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/streams/noStreamsFound.mp4")
    except socket.error as err:
        if err.errno != errno.EPIPE:
            # Not a broken pipe
            raise
        else:
            # player disconnected
            LOGGER.info('Detected player disconnect')
    except Exception as err:
        if str(err).startswith('E2MSG:'):
            E2MSG = str(err).replace('E2MSG:','http://localhost/web/message?')
            os.system('wget -O /dev/null -q "%s"' % E2MSG)
        if str(err) == 'wperror-403':
            sendOfflineMP4(http, send_headers=not_stream_opened, file2send="/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/streams/wperror-403.mp4")
        elif str(err) == 'wperror-422':
            sendOfflineMP4(http, send_headers=not_stream_opened, file2send="/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/streams/wperror-422.mp4")
        elif str(err).startswith('FileCache:'): #<<<<< FileCache
            retData = str(err).strip().split(':')
            #LOGGER.debug("FileCache data: pid= {0}, file2send= {1}", retData[1], retData[2])
            sendCachedFile(http, send_headers=not_stream_opened, pid=retData[1], file2send=retData[2])
        else:
            if not_stream_opened and LOGLEVEL not in ("debug", "trace"):
                LOGGER.error("Got exception: {0}".format(err))
            else:
                LOGGER.error("Got exception: {0}\n{1}".format(err, traceback.format_exc().splitlines()))
            sendOfflineMP4(http, send_headers=not_stream_opened)
    except KeyboardInterrupt:
        pass
    finally:
        if fd:
            LOGGER.info("Stream ended")
            fd.close()
            LOGGER.info("Closing currently open stream...")
            if E2url:
                jtools.remoteE2() #to put in standby
        jtools.cleanCMD() #troche porzadku bo smietnik zostaje

class Streamlink2(Streamlink):
    _loaded_plugins = None

    def load_builtin_plugins(self):
        if self.__class__._loaded_plugins is not None:
            self._update_loaded_plugins()
        else:
            self.load_plugins(plugins.__path__[0])
            if os.path.isdir(PLUGINS_DIR):
                self.load_ext_plugins([PLUGINS_DIR])
            self.__class__._loaded_plugins = self.plugins.copy()

    def _update_loaded_plugins(self):
        self.plugins = self.__class__._loaded_plugins.copy()
        for plugin in itervalues(self.plugins):
            plugin.session = self

    def load_ext_plugins(self, dirs):
        dirs = [os.path.expanduser(d) for d in dirs]
        for directory in dirs:
            if os.path.isdir(directory):
                self.load_plugins(directory)
            else:
                LOGGER.warning("Plugin path {0} does not exist or is not a directory!".format(directory))

class StreamHandler(BaseHTTPRequestHandler):

    def do_HEAD(s):
        sendHeaders(s)

    def do_GET(s):
        jtools.cleanCMD()
        url = unquote(s.path[1:])
        quality = "best"

        LOGGER.debug("Received URL: {}".format(url))
        #split args
        url = url.split(';SLARGS;', 1)
        if len(url) > 1:
            #zeby zadowolic linie 290 i podac poprawna nazwe argumentu
            #dla pierwszego argumentu
            if url[1].startswith('--'):
                url[1] = url[1][1:]
            #dla pozostalych
            url[1] = url[1].replace(';--',';-') 
            LOGGER.debug("args: {}".format(url[1]))
            url[1] = url[1].replace(';',' ')
            if 'quality=' in url[1]:
                for arg in url[1].split(' '):
                    if arg.startswith('quality='):
                        quality = arg[8:]
                        LOGGER.debug("quality params: {}".format(quality))
                        url[1] = url[1].replace('quality=%s' % quality,'').strip()
                        break
        LOGGER.info("Processing URL: {0}".format(url[0].strip()))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            streamlink = Streamlink2()
        return Stream(streamlink, s, url[0].strip(), url[1:2], quality) #ciekawa konstrukcja, zwraca url[1] jesli istnieje lub [] jesli nie

    def finish(self, *args, **kw):
        try:
            if not self.wfile.closed:
                self.wfile.flush()
                self.wfile.close()
        except socket.error:
            pass
        self.rfile.close()

    def handle(self):
        try:
            BaseHTTPRequestHandler.handle(self)
        except socket.error:
            pass

    if LOGLEVEL not in ("debug", "trace"):
        def log_message(self, format, *args):
            return

class ThreadedHTTPServer(ForkingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def start():
    def setup_logging(stream=sys.stdout, level="info"):
        fmt = ("[{asctime},{msecs:0.0f}]" if level == "trace" else "") + "[{name}][{levelname}] {message}"
        logger.basicConfig(stream=stream, level=level, format=fmt, style="{", datefmt="%H:%M:%S")

    global LOGGER, PARSER
    setup_logging(level=LOGLEVEL)
    if opts_parser_version != "N/A":
        try:
            opts_parser.LOGGER = LOGGER
            opts_parser.DEFAULT_LEVEL = LOGLEVEL
            PARSER = build_parser()
        except Exception as err:
            LOGGER.error("err: {}".format(str(err)))

    httpd = ThreadedHTTPServer(("", PORT_NUMBER), StreamHandler)
    try:
        sys.path.append('/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/')
        from version import Version as jVersion
    except Exception as e:
        jVersion = str(e)
    LOGGER.info("####################mod j00zek#####################")
    LOGGER.info("{0} Server ({1} - {2}) started".format(time.asctime(), __version__, jVersion))
    LOGGER.info("Host:            {0}".format(hostname()))
    LOGGER.info("Port:            {0}".format(PORT_NUMBER))
    LOGGER.info("OS:              {0}".format(platform.platform()))
    LOGGER.info("Python:          {0}".format(platform.python_version()))
    LOGGER.info("Streamlink:      {0} / {1}".format(streamlink_version, streamlink_version_date))
    LOGGER.info("Log level:       {0}".format( _loglevel))
    LOGGER.debug("Options Parser: {0}".format(opts_parser_version))
    LOGGER.debug("youtube-dl:     {0}".format(ytdl_version))
    LOGGER.info("Requests({0}), Socks({1}), Websocket({2})".format(requests_version, socks_version, websocket_version))
    LOGGER.info("###################################################")
    

    streamlink = Streamlink2()
    del streamlink
    signal.signal(signal.SIGTSTP, signal.default_int_handler)
    signal.signal(signal.SIGQUIT, signal.default_int_handler)
    signal.signal(signal.SIGTERM, signal.default_int_handler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("Interrupted! Exiting...")
    httpd.server_close()
    LOGGER.info("{0} Server stopped - Host: {1}, Port: {2}".format(time.asctime(), hostname(), PORT_NUMBER))


class Daemon:
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, stdin="/dev/null", stdout="/dev/null", stderr="/dev/null"):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                #sys.stderr.write('Missing pid file for already running streamlinksrv?')
                # exit first parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        sys.stdout.write('streamlink started correctly, logging level: %s\n' % LOGLEVEL)
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.stdin, "r")
        so = open(self.stdout, "a+")
        se = open(self.stderr, "a+")
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        open(self.pidfile,"w+").write("%s\n" % pid)

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = open(self.pidfile,"r")
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        jtools.killSRVprocess(os.getpid())
        jtools.cleanCMD()
        
        try:
            pf = open(self.pidfile,"r")
            pid = int(pf.read().strip())
            pf.close()
        except IOError as e:
            #print(str(e))
            pid = None

        if not pid:
            if os.path.exists(self.pidfile): 
                os.remove(self.pidfile)
            #message = "pidfile %s does not exist. Probably already killed by jtools.killSRVprocess\n"
            #sys.stderr.write(message % self.pidfile)
            return # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err))
                sys.exit(1)
        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """


class StreamlinkDaemon(Daemon):
    def run(self):
        start()


if __name__ == "__main__":
    daemon = StreamlinkDaemon("/var/run/streamlink.pid")
    if len(sys.argv) >= 2:
        if "start" == sys.argv[1]:
            daemon.start()
        elif "stop" == sys.argv[1]:
            daemon.stop()
        elif "restart" == sys.argv[1]:
            daemon.restart()
        elif "manualstart" == sys.argv[1]:
            daemon.stop()
            if len(sys.argv) > 2 and sys.argv[2] in ("debug", "trace"):
                _loglevel = LOGLEVEL = sys.argv[2]
            start()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart|manualstart" % sys.argv[0])
        print("          manualstart include a stop")
        sys.exit(2)
