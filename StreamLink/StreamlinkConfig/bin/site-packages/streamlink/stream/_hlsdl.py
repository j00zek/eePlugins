import os
import random
import threading

import subprocess

import sys

from shutil import which
from streamlink import StreamError
from streamlink.stream import Stream
from streamlink.stream.stream import StreamIO
from streamlink.utils import NamedPipe
from streamlink.compat import devnull
import logging

log = logging.getLogger(__name__)

class HLSDL(StreamIO):
    __commands__ = ['hlsdl4streamlink', 'hlsdl']

    __shortname__ = "hlsdl"

    @classmethod
    def shortname(cls):
        return cls.__shortname__

    @staticmethod
    def copy_to_pipe(self, stream, pipe):
        log.debug("Starting copy to pipe: {0}".format(pipe.path))
        pipe.open("wb")
        
        while not stream.closed:
            try:
                data = stream.read(8192)
                if len(data):
                    pipe.write(data)
                else:
                    break
            except IOError:
                log.error("Pipe copy aborted: {0}".format(pipe.path))
                return
        try:
            pipe.close()
        except IOError:  # might fail closing, but that should be ok for the pipe
            pass
        log.debug("Pipe copy complete: {0}".format(pipe.path))

    def __init__(self, session, *streams, **options):
        if not self.is_usable(session):
            raise StreamError("cannot use HLSDL")

        self.session = session
        self.process = None
        self.processHLSDL = None
        self.streams = streams

        self.is_muxed = options.pop("is_muxed", False)
        outpath = options.pop("outpath", "pipe:1")
        metadata = options.pop("metadata", {})
        maps = options.pop("maps", [])
        copyts = options.pop("copyts", False)

        self._cmd = [self.command(session)]

        self._cmd.extend([self.streams[0]])

        self._cmd.extend(['-b', '-f', '-o', '/tmp/hlsdl.ts'])


        log.debug("hlsdl command: {0}".format(' '.join(self._cmd)))
        self.close_errorlog = False

        if session.options.get("ffmpeg-verboseOFF"):
            self.errorlog = sys.stderr
        elif session.options.get("ffmpeg-verbose-pathOFF"):
            self.errorlog = open(session.options.get("ffmpeg-verbose-path"), "w")
            self.close_errorlog = True
        else:
            self.errorlog = devnull()
            
    def open(self):
        if os.path.exists('/tmp/hlsdl.ts'):
            os.remove('/tmp/hlsdl.ts')
        if os.path.exists('/tmp/aqq'):
            os.remove('/tmp/aqq')
        self.processHLSDL = subprocess.Popen(self._cmd, stdout=None, stdin=None, stderr=None)
         
        self.process = subprocess.Popen('sleep 10;cat /tmp/hlsdl.ts', stdout=subprocess.PIPE,
                                        stdin= open("/tmp/hlsdl.ts", "rb"), stderr=self.errorlog)

        return self

    @classmethod
    def is_usable(cls, session):
        return cls.command(session) is not None

    @classmethod
    def command(cls, session):
        command = []
        for cmd in command or cls.__commands__:
            if which(cmd):
                return cmd

    def read(self, size=-1):
        data = self.process.stdout.read(size)
        return data

    def close(self):
        log.debug("Closing hlsdl thread")
        if self.process:
            # kill hlsdl
            #self.processHLSDL.kill()
            self.process.kill()
            self.process.stdout.close()

            # close the streams
            if self.is_muxed:
                for stream in self.streams:
                    if hasattr(stream, "close"):
                        stream.close()

                log.debug("Closed all the substreams")
        if self.close_errorlog:
            self.errorlog.close()
            self.errorlog = None
