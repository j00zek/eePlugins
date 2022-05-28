#!/usr/bin/python3
#
# Linux Python2/3 Streamlink Daemon
#
# Copyright (c) 2017 - 2021 Billy2011 @vuplus-support.org
# Copyright (c) 2021 jbleyel (python3 mod)
#                                          
# License: GPLv2+
#
# mod j00zek 2020-2022
# changes:
# - connection with e2settings
# - proceeding url parameters according to html standard
# - using hlsdl for some m3u services

from streamlink import jtools
import os
jtools.killSRVprocess(os.getpid())
jtools.cleanCMD()
processCLI = None
import subprocess
try:
    from subprocess import DEVNULL # Python 3.
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')

from six import PY2
""" Streamlink Daemon """

__version__ = "1.8.3"
__optparserversion__ = "0.3.0"
import argparse
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
from six import itervalues, iteritems
from six.moves.urllib_parse import unquote
from websocket import __version__ as websocket_version

from shlex import split as argsplit
from string import printable
from textwrap import dedent
from contextlib import contextmanager
from collections import OrderedDict

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
from streamlink import plugins
from streamlink.exceptions import FatalPluginError
from streamlink import __version__ as streamlink_version
from streamlink.plugin import PluginOptions
from streamlink.utils.args import comma_list, comma_list_filter, filesize, keyvalue, num
from streamlink.utils.times import hours_minutes_seconds
from streamlink.stream import HTTPStream
from streamlink.stream.ffmpegmux import MuxedStream

#try:
#    from streamlink import opts_parser
#    from streamlink.opts_parser import *
#    from streamlink.opts_parser import __version__ as opts_parser_version
#except ImportError:
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

STREAM_PASSTHROUGH = ["hls", "http", "hls-multi", "dash"]
XDG_CONFIG_HOME = "/home/root/.config"
XDG_STATE_HOME = "/home/root/.local/state"
CONFIG_FILES = [
    os.path.expanduser(XDG_CONFIG_HOME + "/streamlink/config"),
    os.path.expanduser(XDG_CONFIG_HOME + "/.streamlinkrc")
]
PLUGINS_DIR = os.path.expanduser(XDG_CONFIG_HOME + "/streamlink/plugins")
LOG_DIR = os.path.expanduser(XDG_STATE_HOME + "/streamlink/logs")

_printable_re = re.compile(r"[{0}]".format(printable))
_option_re = re.compile(r"""
    (?P<name>[\w-]+) # A option name, valid characters are A to z and dash.
    \s*
    (?P<op>=)? # Separating the option and the value with a equals sign is
               # common, but optional.
    \s*
    (?P<value>.*) # The value, anything goes.
""", re.VERBOSE)
DEFAULT_LEVEL = "info"


@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
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

def sendCachedFile(http, send_headers=True, pid=0, file2send=None, maxWaitTime = 10 ):
    LOGGER.debug("sendCachedFile(send_headers={0}, pid={1}, file2send={2})".format(str(send_headers), pid, file2send))
    if file2send is None:
        return 

    #waiting for cache file
    for x in range(1, maxWaitTime):
        if not os.path.exists(file2send):
            LOGGER.debug("\twaiting for cache file {0} ms".format(int(1000 * 0.1 * x) ))
            time.sleep(0.1)
        else:
            break
    #if still no file, send offline.mp4
    if not os.path.exists(file2send):
        sendOfflineMP4(http)
        return 
    
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
            LOGGER.error("sendCachedFile aborted")
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


class ArgumentParser(argparse.ArgumentParser):
    def convert_arg_line_to_args(self, line):
        match = _printable_re.search(line)
        if not match:
            return
        line = line[match.start():].strip()

        # Skip lines that do not start with a valid option (e.g. comments)
        option = _option_re.match(line)
        if not option:
            return

        name, value = option.group("name", "value")
        if name and value:
            yield "--{0}={1}".format(name, value)
        elif name:
            yield "--{0}".format(name)

    def error(self, message):
        LOGGER.error(message)


class HelpFormatter(argparse.RawDescriptionHelpFormatter):
    def __init__(self, max_help_position=4, *args, **kwargs):
        # A smaller indent for args help.
        kwargs["max_help_position"] = max_help_position
        argparse.RawDescriptionHelpFormatter.__init__(self, *args, **kwargs)

    def _split_lines(self, text, width):
        text = dedent(text).strip() + "\n\n"
        return text.splitlines()


def build_parser():
    global PARSER
    PARSER = ArgumentParser(
        fromfile_prefix_chars="@",
        formatter_class=HelpFormatter,
        add_help=False,
        usage="%(prog)s [OPTIONS] <URL> [STREAM]",
        description=dedent("""
        Streamlink is command-line utility that extracts streams from
        various services and pipes them into a video player of choice.
        """),
        epilog=dedent("""
        For more in-depth documentation see:
        https://streamlink.github.io
        Please report broken plugins or bugs to the issue tracker on Github:
        https://github.com/streamlink/streamlink/issues
        """)
    )

    general = PARSER.add_argument_group("General options")
    general.add_argument(
        "-h", "--help",
        action="store_true",
    )
    general.add_argument(
        "--locale",
        type=str,
        metavar="LOCALE",
    )
    general.add_argument(
        "-l", "--loglevel",
        metavar="LEVEL",
        choices=logger.levels,
        default=DEFAULT_LEVEL,
    )
    general.add_argument(
        "--logfile",
        metavar="FILE",
    )
    general.add_argument(
        "--interface",
        type=str,
        metavar="INTERFACE",
    )
    general.add_argument(
        "-4", "--ipv4",
        action="store_true",
    )
    general.add_argument(
        "-6", "--ipv6",
        action="store_true",
    )

    player = PARSER.add_argument_group("Player options")
    player.add_argument(
        "--player-passthrough",
        metavar="TYPES",
        type=comma_list_filter(STREAM_PASSTHROUGH),
        default=[],
    )

    http = PARSER.add_argument_group("HTTP options")
    http.add_argument(
        "--http-proxy",
        metavar="HTTP_PROXY",
    )
    http.add_argument(
        "--https-proxy",
        metavar="HTTPS_PROXY",
    )
    http.add_argument(
        "--http-cookie",
        metavar="KEY=VALUE",
        type=keyvalue,
        action="append",
    )
    http.add_argument(
        "--http-header",
        metavar="KEY=VALUE",
        type=keyvalue,
        action="append",
    )
    http.add_argument(
        "--http-query-param",
        metavar="KEY=VALUE",
        type=keyvalue,
        action="append",
    )
    http.add_argument(
        "--http-ignore-env",
        action="store_true",
    )
    http.add_argument(
        "--http-no-ssl-verify",
        action="store_true",
    )
    http.add_argument(
        "--http-disable-dh",
        action="store_true",
    )
    http.add_argument(
        "--http-ssl-cert",
        metavar="FILENAME",
    )
    http.add_argument(
        "--http-ssl-cert-crt-key",
        metavar=("CRT_FILENAME", "KEY_FILENAME"),
        nargs=2,
    )
    http.add_argument(
        "--http-timeout",
        metavar="TIMEOUT",
        type=num(float, min=0),
    )

    transport = PARSER.add_argument_group("Stream transport options")
    transport.add_argument(
        "--hds-live-edge",
        type=num(float, min=0),
        metavar="SECONDS",
    )
    transport.add_argument("--hds-segment-attempts", help=argparse.SUPPRESS)
    transport.add_argument("--hds-segment-threads", help=argparse.SUPPRESS)
    transport.add_argument("--hds-segment-timeout", help=argparse.SUPPRESS)
    transport.add_argument("--hds-timeout", help=argparse.SUPPRESS)
    transport.add_argument(
        "--hls-live-edge",
        type=num(int, min=0),
        metavar="SEGMENTS",
    )
    transport.add_argument("--hls-segment-stream-data", action="store_true", help=argparse.SUPPRESS)
    transport.add_argument(
        "--hls-playlist-reload-attempts",
        type=num(int, min=0),
        metavar="ATTEMPTS",
    )
    transport.add_argument(
        "--hls-playlist-reload-time",
        metavar="TIME",
    )
    transport.add_argument("--hls-segment-attempts", help=argparse.SUPPRESS)
    transport.add_argument("--hls-segment-threads", help=argparse.SUPPRESS)
    transport.add_argument("--hls-segment-timeout", help=argparse.SUPPRESS)
    transport.add_argument(
        "--hls-segment-ignore-names",
        metavar="NAMES",
        type=comma_list,
    )
    transport.add_argument(
        "--hls-segment-key-uri",
        metavar="URI",
        type=str,
    )
    transport.add_argument(
        "--hls-audio-select",
        type=comma_list,
        metavar="CODE",
    )
    transport.add_argument("--hls-timeout", help=argparse.SUPPRESS)
    transport.add_argument(
        "--hls-start-offset",
        type=hours_minutes_seconds,
        metavar="HH:MM:SS",
        default=None,
    )
    transport.add_argument(
        "--hls-duration",
        type=hours_minutes_seconds,
        metavar="HH:MM:SS",
        default=None,
    )
    transport.add_argument(
        "--hls-live-restart",
        action="store_true",
    )
    transport.add_argument(
        "--http-add-audio",
        metavar="URL",
    )
    transport.add_argument("--http-stream-timeout", help=argparse.SUPPRESS)
    transport.add_argument(
        "--ringbuffer-size",
        metavar="SIZE",
        type=filesize,
    )
    transport.add_argument(
        "--rtmp-proxy",
        metavar="PROXY",
    )
    transport.add_argument(
        "--rtmp-rtmpdump",
        metavar="FILENAME",
    )
    transport.add_argument("--rtmpdump", help=argparse.SUPPRESS)
    transport.add_argument("--rtmp-timeout", help=argparse.SUPPRESS)
    transport.add_argument(
        "--stream-segment-attempts",
        type=num(int, min=0),
        metavar="ATTEMPTS",
    )
    transport.add_argument(
        "--stream-segment-threads",
        type=num(int, max=10),
        metavar="THREADS",
    )
    transport.add_argument(
        "--stream-segment-timeout",
        type=num(float, min=0),
        metavar="TIMEOUT",
    )
    transport.add_argument(
        "--stream-timeout",
        type=num(float, min=0),
        metavar="TIMEOUT",
    )
    transport.add_argument(
        "--subprocess-errorlog",
        action="store_true",
    )
    transport.add_argument(
        "--subprocess-errorlog-path",
        type=str,
        metavar="PATH",
    )
    transport.add_argument(
        "--ffmpeg-ffmpeg",
        metavar="FILENAME",
    )
    transport.add_argument(
        "--ffmpeg-verbose",
        action="store_true",
    )
    transport.add_argument(
        "--ffmpeg-verbose-path",
        type=str,
        metavar="PATH",
    )
    transport.add_argument(
        "--ffmpeg-fout",
        type=str,
        metavar="OUTFORMAT",
    )
    transport.add_argument(
        "--ffmpeg-video-transcode",
        metavar="CODEC",
    )
    transport.add_argument(
        "--ffmpeg-audio-transcode",
        metavar="CODEC",
    )
    transport.add_argument(
        "--ffmpeg-copyts",
        action="store_true",
    )
    transport.add_argument(
        "--ffmpeg-start-at-zero",
        action="store_true",
    )
    transport.add_argument(
        "--mux-subtitles",
        action="store_true",
    )

    stream = PARSER.add_argument_group("Stream options")
    stream.add_argument(
        "--default-stream",
        type=comma_list,
        metavar="STREAM",
    )
    stream.add_argument(
        "--stream-types", "--stream-priority",
        metavar="TYPES",
        type=comma_list,
    )
    stream.add_argument(
        "--stream-sorting-excludes",
        metavar="STREAMS",
        type=comma_list,
    )
    stream.add_argument(
        "--retry-open",
        metavar="ATTEMPTS",
        type=num(int, min=0),
        default=1,
    )

    return PARSER


def setupTransportOpts(streamlink, args):
    """Sets Streamlink options."""
    if args.interface:
        streamlink.set_option("interface", args.interface)

    if args.ipv4:
        streamlink.set_option("ipv4", args.ipv4)

    if args.ipv6:
        streamlink.set_option("ipv6", args.ipv6)

    if args.hls_live_edge:
        streamlink.set_option("hls-live-edge", args.hls_live_edge)

    if args.hls_playlist_reload_attempts:
        streamlink.set_option("hls-playlist-reload-attempts", args.hls_playlist_reload_attempts)

    if args.hls_playlist_reload_time:
        streamlink.set_option("hls-playlist-reload-time", args.hls_playlist_reload_time)

    if args.hls_segment_ignore_names:
        streamlink.set_option("hls-segment-ignore-names", args.hls_segment_ignore_names)

    if args.hls_segment_key_uri:
        streamlink.set_option("hls-segment-key-uri", args.hls_segment_key_uri)

    if args.hls_audio_select:
        streamlink.set_option("hls-audio-select", args.hls_audio_select)

    if args.hls_start_offset:
        streamlink.set_option("hls-start-offset", args.hls_start_offset)

    if args.hls_duration:
        streamlink.set_option("hls-duration", args.hls_duration)

    if args.hls_live_restart:
        streamlink.set_option("hls-live-restart", args.hls_live_restart)

    if args.hds_live_edge:
        streamlink.set_option("hds-live-edge", args.hds_live_edge)

    if args.http_add_audio:
        streamlink.set_option("http-add-audio", args.http_add_audio)

    if args.ringbuffer_size:
        streamlink.set_option("ringbuffer-size", args.ringbuffer_size)

    if args.rtmp_proxy:
        streamlink.set_option("rtmp-proxy", args.rtmp_proxy)

    if args.rtmp_rtmpdump:
        streamlink.set_option("rtmp-rtmpdump", args.rtmp_rtmpdump)
    elif args.rtmpdump:
        streamlink.set_option("rtmp-rtmpdump", args.rtmpdump)

    # deprecated
    if args.hds_segment_attempts:
        streamlink.set_option("hds-segment-attempts", args.hds_segment_attempts)
    if args.hds_segment_threads:
        streamlink.set_option("hds-segment-threads", args.hds_segment_threads)
    if args.hds_segment_timeout:
        streamlink.set_option("hds-segment-timeout", args.hds_segment_timeout)
    if args.hds_timeout:
        streamlink.set_option("hds-timeout", args.hds_timeout)
    if args.hls_segment_attempts:
        streamlink.set_option("hls-segment-attempts", args.hls_segment_attempts)
    if args.hls_segment_threads:
        streamlink.set_option("hls-segment-threads", args.hls_segment_threads)
    if args.hls_segment_timeout:
        streamlink.set_option("hls-segment-timeout", args.hls_segment_timeout)
    if args.hls_timeout:
        streamlink.set_option("hls-timeout", args.hls_timeout)
    if args.http_stream_timeout:
        streamlink.set_option("http-stream-timeout", args.http_stream_timeout)

    if args.rtmp_timeout:
        streamlink.set_option("rtmp-timeout", args.rtmp_timeout)

    # generic stream- arguments take precedence over deprecated stream-type arguments
    if args.stream_segment_attempts:
        streamlink.set_option("stream-segment-attempts", args.stream_segment_attempts)

    if args.stream_segment_threads:
        streamlink.set_option("stream-segment-threads", args.stream_segment_threads)

    if args.stream_segment_timeout:
        streamlink.set_option("stream-segment-timeout", args.stream_segment_timeout)

    if args.stream_timeout:
        streamlink.set_option("stream-timeout", args.stream_timeout)

    if args.ffmpeg_ffmpeg:
        streamlink.set_option("ffmpeg-ffmpeg", args.ffmpeg_ffmpeg)
    if args.ffmpeg_verbose:
        streamlink.set_option("ffmpeg-verbose", args.ffmpeg_verbose)
    if args.ffmpeg_verbose_path:
        streamlink.set_option("ffmpeg-verbose-path", args.ffmpeg_verbose_path)
    if args.ffmpeg_fout:
        streamlink.set_option("ffmpeg-fout", args.ffmpeg_fout)
    if args.ffmpeg_video_transcode:
        streamlink.set_option("ffmpeg-video-transcode", args.ffmpeg_video_transcode)
    if args.ffmpeg_audio_transcode:
        streamlink.set_option("ffmpeg-audio-transcode", args.ffmpeg_audio_transcode)
    if args.ffmpeg_copyts:
        streamlink.set_option("ffmpeg-copyts", True)
    if args.ffmpeg_start_at_zero:
        streamlink.set_option("ffmpeg-start-at-zero", False)

    if args.mux_subtitles:
        streamlink.set_option("mux-subtitles", args.mux_subtitles)

    streamlink.set_option("subprocess-errorlog", args.subprocess_errorlog)
    streamlink.set_option("subprocess-errorlog-path", args.subprocess_errorlog_path)
    streamlink.set_option("locale", args.locale)


def setupHttpSession(streamlink, args):
    """Sets the global HTTP settings, such as proxy and headers."""
    if args.http_proxy:
        streamlink.set_option("http-proxy", args.http_proxy)

    if args.https_proxy:
        streamlink.set_option("https-proxy", args.https_proxy)

    if args.http_cookie:
        streamlink.set_option("http-cookies", dict(args.http_cookie))

    if args.http_header:
        streamlink.set_option("http-headers", dict(args.http_header))

    if args.http_query_param:
        streamlink.set_option("http-query-params", dict(args.http_query_param))

    if args.http_ignore_env:
        streamlink.set_option("http-trust-env", False)

    if args.http_no_ssl_verify:
        streamlink.set_option("http-ssl-verify", False)

    if args.http_disable_dh:
        streamlink.set_option("http-disable-dh", True)

    if args.http_ssl_cert:
        streamlink.set_option("http-ssl-cert", args.http_ssl_cert)

    if args.http_ssl_cert_crt_key:
        streamlink.set_option("http-ssl-cert", tuple(args.http_ssl_cert_crt_key))

    if args.http_timeout:
        streamlink.set_option("http-timeout", args.http_timeout)


def setup_plugin_args(streamlink):
    """Sets Streamlink plugin options."""

    plugin_args = PARSER.add_argument_group("Plugin options")
    for pname, plugin in streamlink.plugins.items():
        defaults = {}
        for parg in plugin.arguments:
            if not parg.is_global:
                plugin_args.add_argument(parg.argument_name(pname), **parg.options)
                defaults[parg.dest] = parg.default
            else:
                pargdest = parg.dest
                for action in PARSER._actions:
                    # find matching global argument
                    if pargdest != action.dest:
                        continue
                    defaults[pargdest] = action.default

                    # add plugin to global argument
                    plugins = getattr(action, "plugins", [])
                    plugins.append(pname)
                    setattr(action, "plugins", plugins)

        plugin.options = PluginOptions(defaults)

    return True




def setup_plugin_options(streamlink, plugin, args):
    pname = plugin.module
    required = OrderedDict({})
    for parg in plugin.arguments:
        if parg.options.get("help") == argparse.SUPPRESS:
            continue

        value = getattr(args, parg.dest if parg.is_global else parg.namespace_dest(pname))
        streamlink.set_plugin_option(pname, parg.dest, value)

        if not parg.is_global:
            if parg.required:
                required[parg.name] = parg
            # if the value is set, check to see if any of the required arguments are not set
            if parg.required or value:
                try:
                    for rparg in plugin.arguments.requires(parg.name):
                        required[rparg.name] = rparg
                except RuntimeError:
                    LOGGER.error("{0} plugin has a configuration error and the arguments cannot be parsed".format(pname))
                    break

    if required:
        for req in required.values():
            if not streamlink.get_plugin_option(pname, req.dest):
                streamlink.set_plugin_option(pname, req.dest, "")


def setup_config_files(streamlink, url):
    config_files = []
    pluginclass = None

    if url:
        with ignored(NoPluginError):
            pluginclass, resolved_url = streamlink.resolve_url(url)
            config_files += ["{0}.{1}".format(fn, pluginclass.module) for fn in CONFIG_FILES]

    for config_file in filter(os.path.isfile, CONFIG_FILES):
        config_files.append(config_file)
        break

    return (config_files, pluginclass(resolved_url))


def setup_args(arglist, config_files=[], ignore_unknown=False):
    for config_file in filter(os.path.isfile, config_files):
        arglist.insert(0, "@" + config_file)

    args, unknown = PARSER.parse_known_args(arglist)

    if unknown and not ignore_unknown:
        PARSER.error("unrecognized arguments: {0}".format(' '.join(unknown)))

    return args


def conv_argitems_to_arglist(argitems):
    arglist = []
    for item in argitems:
        for option in PARSER.convert_arg_line_to_args(item):
            arglist.append(option)

    return arglist


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

        if LOGLEVEL in ["trace", "debug"]:
            logger.root.setLevel(LOGLEVEL)

        if not plugin:
            plugin, resolved_url = streamlink.resolve_url(url)
            plugin = plugin(resolved_url)

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

        if args.http_add_audio:
            http_add_audio = HTTPStream(streamlink, args.http_add_audio)
        else:
            http_add_audio = False
        prebuffer = None
        stream_names = [stream_name] + alt_streams
        for stream_name in stream_names:
            stream = streams[stream_name]
            stream_type = type(stream).shortname()

            if http_add_audio and stream_type in ("hls", "http", "rtmp"):
                stream = MuxedStream(streamlink, stream, http_add_audio, add_audio=True)
                stream_type = "muxed-stream"

            # forece passthrough for YT hls
            player_passthrough = False #True if stream_type in ("hls") and plugin.module in ("youtube") else False

            LOGGER.info("Opening stream: {0} ({1})".format(stream_name, stream_type))
            if stream_type in args.player_passthrough or player_passthrough:
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


def useCLI(http, url, argstr, quality):
    LOGGER.info("useCLI(%s,%s,%s) >>>" %(url,argstr,quality))
    CacheFileName = '/tmp/stream.ts'
    if os.path.exists(CacheFileName):
        os.remove()
    _cmd = ['/usr/sbin/streamlink'] 
    _cmd.extend(['-l', 'debug', '-o', CacheFileName, url, quality])
    LOGGER.debug("run command: %s" % ' '.join(_cmd))
    try:
        processCLI = subprocess.Popen(_cmd, stdout= subprocess.PIPE, stderr= DEVNULL )
        if processCLI:
            #waiting for CLI to proceed
            LOGGER.debug("processCLI.pid=%s : Waiting for streamlink to proceed..." % processCLI.pid)
            for x in range(1, 100):
                if not os.path.exists(CacheFileName):
                    outLine = processCLI.stdout.readline()
                    try:
                        outLine = outLine.decode('utf-8')
                    except Exception:
                        pass
                    if outLine != '':
                        LOGGER.debug('\t%s' % outLine.strip())
                    time.sleep(0.1)
                else:
                    break
            open('/var/run/processPID.pid', "w").write("%s\n" % processCLI.pid)
            if os.path.exists(CacheFileName):
                sendCachedFile(http, send_headers=True, pid=processCLI.pid, file2send=CacheFileName, maxWaitTime = 100)
            else:
                sendOfflineMP4(http)
        else:
            LOGGER.error('ERROR: CLI subprocess not stared :(')
    except Exception as e:
        LOGGER.debug('EXCEPTION: ' % str(e))
        

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
        if url[0].strip().startswith('useCLI/'):
            useCLI(s, url[0].strip()[7:], url[1:2], quality)
            return
        elif jtools.GetuseCLI() == 'a':
            useCLI(s, url[0].strip(), url[1:2], quality)
            return
        elif jtools.GetuseCLI() == 's' and (url[0].strip().startswith('https://ok.ru') or 
                                            url[0].strip().startswith('https://www.youtube.com/channel')
                                           ):
            useCLI(s, url[0].strip(), url[1:2], quality)
            return
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                streamlink = Streamlink2()

            return Stream(streamlink, s, url[0].strip(), url[1:2], quality) #ciekawa konstrukcja, zwraca url[1] jesli istnieje lub [] jesli nie

    def finish(self, *args, **kw):
        LOGGER.debug("finish >>>")
        jtools.cleanCMD()
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
    PARSER = build_parser()

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
    LOGGER.info("Streamlink:      {0}".format(streamlink_version))
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
        open(self.pidfile, "w+").write("%s\n" % pid)

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = open(self.pidfile, "r")
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
            pf = open(self.pidfile, "r")
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
