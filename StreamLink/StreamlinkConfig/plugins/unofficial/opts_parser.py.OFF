
"""
  Options Parser for Streamlinksrv by Billy2011.
  Options must be appended to the URL.
  Not all options are supported.
"""

import argparse
import os
import re
from collections import OrderedDict
from contextlib import contextmanager
from shlex import split as argsplit
from string import printable
from textwrap import dedent

from streamlink import NoPluginError
from streamlink import logger
from streamlink.plugin import PluginOptions
from streamlink.utils.args import comma_list, comma_list_filter, filesize, keyvalue, num
from streamlink.utils.times import hours_minutes_seconds

__version__ = "0.2.9"

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

LOGGER = None
PARSER = None
DEFAULT_LEVEL = "info"


@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass


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
    transport.add_argument(
        "--hds-segment-attempts",
        type=num(int, min=0),
        metavar="ATTEMPTS",
    )
    transport.add_argument(
        "--hds-segment-threads",
        type=num(int, max=10),
        metavar="THREADS",
    )
    transport.add_argument(
        "--hds-segment-timeout",
        type=num(float, min=0),
        metavar="TIMEOUT",
    )
    transport.add_argument(
        "--hds-timeout",
        type=num(float, min=0),
        metavar="TIMEOUT",
    )
    transport.add_argument(
        "--hls-live-edge",
        type=num(int, min=0),
        metavar="SEGMENTS",
    )
    transport.add_argument(
        "--hls-segment-stream-data",
        action="store_true",
    )
    transport.add_argument(
        "--hls-segment-attempts",
        type=num(int, min=0),
        metavar="ATTEMPTS",
    )
    transport.add_argument(
        "--hls-playlist-reload-attempts",
        type=num(int, min=0),
        metavar="ATTEMPTS",
    )
    transport.add_argument(
        "--hls-playlist-reload-time",
        metavar="TIME",
    )
    transport.add_argument(
        "--hls-segment-threads",
        type=num(int, max=10),
        metavar="THREADS",
    )
    transport.add_argument(
        "--hls-segment-timeout",
        type=num(float, min=0),
        metavar="TIMEOUT",
    )
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
    transport.add_argument(
        "--hls-timeout",
        type=num(float, min=0),
        metavar="TIMEOUT",
    )
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
        "--http-stream-timeout",
        type=num(float, min=0),
        metavar="TIMEOUT",
    )
    transport.add_argument(
        "--http-add-audio",
        metavar="URL",
    )
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
    transport.add_argument(
        "--rtmp-timeout",
        type=num(float, min=0),
        metavar="TIMEOUT",
    )
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

    if args.hls_segment_attempts:
        streamlink.set_option("hls-segment-attempts", args.hls_segment_attempts)

    if args.hls_segment_stream_data:
        streamlink.set_option("hls-segment-stream-data", args.hls_segment_stream_data)

    if args.hls_playlist_reload_attempts:
        streamlink.set_option("hls-playlist-reload-attempts", args.hls_playlist_reload_attempts)

    if args.hls_playlist_reload_time:
        streamlink.set_option("hls-playlist-reload-time", args.hls_playlist_reload_time)

    if args.hls_segment_threads:
        streamlink.set_option("hls-segment-threads", args.hls_segment_threads)

    if args.hls_segment_timeout:
        streamlink.set_option("hls-segment-timeout", args.hls_segment_timeout)

    if args.hls_segment_ignore_names:
        streamlink.set_option("hls-segment-ignore-names", args.hls_segment_ignore_names)

    if args.hls_segment_key_uri:
        streamlink.set_option("hls-segment-key-uri", args.hls_segment_key_uri)

    if args.hls_timeout:
        streamlink.set_option("hls-timeout", args.hls_timeout)

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

    if args.hds_segment_attempts:
        streamlink.set_option("hds-segment-attempts", args.hds_segment_attempts)

    if args.hds_segment_threads:
        streamlink.set_option("hds-segment-threads", args.hds_segment_threads)

    if args.hds_segment_timeout:
        streamlink.set_option("hds-segment-timeout", args.hds_segment_timeout)

    if args.hds_timeout:
        streamlink.set_option("hds-timeout", args.hds_timeout)

    if args.http_add_audio:
        streamlink.set_option("http-add-audio", args.http_add_audio)

    if args.http_stream_timeout:
        streamlink.set_option("http-stream-timeout", args.http_stream_timeout)

    if args.ringbuffer_size:
        streamlink.set_option("ringbuffer-size", args.ringbuffer_size)

    if args.rtmp_proxy:
        streamlink.set_option("rtmp-proxy", args.rtmp_proxy)

    if args.rtmp_rtmpdump:
        streamlink.set_option("rtmp-rtmpdump", args.rtmp_rtmpdump)
    elif args.rtmpdump:
        streamlink.set_option("rtmp-rtmpdump", args.rtmpdump)

    if args.rtmp_timeout:
        streamlink.set_option("rtmp-timeout", args.rtmp_timeout)

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
    plugin = None

    if url:
        with ignored(NoPluginError):
            plugin = streamlink.resolve_url(url)
            config_files += ["{0}.{1}".format(fn, plugin.module) for fn in CONFIG_FILES]

    for config_file in filter(os.path.isfile, CONFIG_FILES):
        config_files.append(config_file)
        break

    return (config_files, plugin)


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


__all__ = ["build_parser", "setup_args", "setupHttpSession", "setupTransportOpts", "conv_argitems_to_arglist",
           "setup_plugin_args", "setup_plugin_options", "setup_config_files", "argsplit", "PLUGINS_DIR", "LOG_DIR"]
