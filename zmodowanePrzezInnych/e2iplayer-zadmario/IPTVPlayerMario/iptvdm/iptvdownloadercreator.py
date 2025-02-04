# -*- coding: utf-8 -*-
#
#  IPTV downloader creator
#
#  $Id$
#
#
###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayerMario.tools.iptvtools import printDBG, printExc, IsExecutable
from Plugins.Extensions.IPTVPlayerMario.tools.iptvtypes import strwithmeta
from Plugins.Extensions.IPTVPlayerMario.libs.urlparser import urlparser
from Plugins.Extensions.IPTVPlayerMario.iptvdm.wgetdownloader import WgetDownloader
from Plugins.Extensions.IPTVPlayerMario.iptvdm.pwgetdownloader import PwgetDownloader
from Plugins.Extensions.IPTVPlayerMario.iptvdm.busyboxdownloader import BuxyboxWgetDownloader
from Plugins.Extensions.IPTVPlayerMario.iptvdm.m3u8downloader import M3U8Downloader
from Plugins.Extensions.IPTVPlayerMario.iptvdm.em3u8downloader import EM3U8Downloader
from Plugins.Extensions.IPTVPlayerMario.iptvdm.hlsdownloader import HLSDownloader
from Plugins.Extensions.IPTVPlayerMario.iptvdm.ehlsdownloader import EHLSDownloader
from Plugins.Extensions.IPTVPlayerMario.iptvdm.rtmpdownloader import RtmpDownloader
from Plugins.Extensions.IPTVPlayerMario.iptvdm.f4mdownloader import F4mDownloader
from Plugins.Extensions.IPTVPlayerMario.iptvdm.mergedownloader import MergeDownloader
from Plugins.Extensions.IPTVPlayerMario.iptvdm.ffmpegdownloader import FFMPEGDownloader
from Plugins.Extensions.IPTVPlayerMario.iptvdm.iptvdh import DMHelper
###################################################

###################################################
# FOREIGN import
###################################################
from Components.config import config
###################################################


def IsUrlDownloadable(url):
    if None != DownloaderCreator(url):
        return True
    else:
        return False


def DownloaderCreator(url):
    printDBG("DownloaderCreator url[%r]" % url)
    downloader = None

    url = urlparser.decorateUrl(url)
    iptv_proto = url.meta.get('iptv_proto', '')
    if 'm3u8' == iptv_proto:
        if config.plugins.IPTVPlayerMario.hlsdlpath.value != '':
            downloader = HLSDownloader()
        else:
            downloader = M3U8Downloader()
    elif 'em3u8' == iptv_proto:
        if config.plugins.IPTVPlayerMario.hlsdlpath.value != '':
            downloader = EHLSDownloader()
        else:
            downloader = EM3U8Downloader()
    elif 'f4m' == iptv_proto:
        downloader = F4mDownloader()
    elif 'rtmp' == iptv_proto:
        downloader = RtmpDownloader()
    elif iptv_proto in ['https', 'http']:
        downloader = WgetDownloader()
    elif 'merge' == iptv_proto:
        if url.meta.get('prefered_merger') == 'hlsdl' and config.plugins.IPTVPlayerMario.hlsdlpath.value != '' and config.plugins.IPTVPlayerMario.prefer_hlsdl_for_pls_with_alt_media.value:
            downloader = HLSDownloader()
        elif IsExecutable('ffmpeg') and config.plugins.IPTVPlayerMario.cmdwrappath.value != '':
            downloader = FFMPEGDownloader()
        else:
            downloader = MergeDownloader()
    elif 'mpd' == iptv_proto and IsExecutable('ffmpeg') and config.plugins.IPTVPlayerMario.cmdwrappath.value != '':
        downloader = FFMPEGDownloader()

    return downloader


def UpdateDownloaderCreator(url):
    printDBG("UpdateDownloaderCreator url[%s]" % url)
    if url.startswith('https'):
        if IsExecutable(DMHelper.GET_WGET_PATH()):
            printDBG("UpdateDownloaderCreator WgetDownloader")
            return WgetDownloader()
        elif IsExecutable('python'):
            printDBG("UpdateDownloaderCreator PwgetDownloader")
            return PwgetDownloader()
    else:
        if IsExecutable('wget'):
            printDBG("UpdateDownloaderCreator BuxyboxWgetDownloader")
            return BuxyboxWgetDownloader()
        elif IsExecutable(DMHelper.GET_WGET_PATH()):
            printDBG("UpdateDownloaderCreator WgetDownloader")
            return WgetDownloader()
        elif IsExecutable('python'):
            printDBG("UpdateDownloaderCreator PwgetDownloader")
            return PwgetDownloader()
    printDBG("UpdateDownloaderCreator downloader not available")
    return PwgetDownloader()
