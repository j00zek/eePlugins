#!/usr/bin/python3
#
# Linux Python3 Streamlink Daemon with native client
#
# j00zek 2020-2023
#                                          
# License: GPLv2+
#

__version__ = "1.5"
import atexit
import errno
import logging
import os
import platform
import re
import signal
import socket
import subprocess
import sys
import time

from http.server import HTTPServer, BaseHTTPRequestHandler
from six.moves.urllib_parse import unquote
from socketserver import ForkingMixIn #ThreadingMixIn as ForkingMixIn
from streamlink import jtools
from streamlink import Streamlink
from streamlink.options import Options
from streamlink.utils.parse import parse_qsd
from streamlink._version import __version__ as streamlink_ver

jtools.killSRVprocess(os.getpid())
jtools.cleanCMD(forceKill = True)

from streamlink import Streamlink
from streamlink.options import Options
from streamlink.utils.parse import parse_qsd
from streamlink._version import __version__ as streamlink_ver

PORT_NUMBER = jtools.GetPortNumber()
_loglevel = LOGLEVEL = jtools.GetLogLevel()
streamCLIport = 8808

if jtools.LogToFile():
    logging.basicConfig(handlers=[logging.FileHandler(jtools.GetLogFileName()),logging.StreamHandler()],
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.NOTSET)
else:
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.NOTSET)
# do not change
LOGGER = logging.getLogger('streamlinkSRV')

def redirectToStreamlinkCLI(http, useAddr):
    LOGGER.debug("redirectToStreamlinkCLI to http://%s:%s/" % (useAddr,streamCLIport))
    http.send_response(301)
    http.send_header("Location", 'http://%s:%s/' % (useAddr,streamCLIport))
    http.end_headers()

def sendHeaders(http, status=200, type="text/html"):
    http.send_response(status)
    http.send_header("Serwer", "Enigma2 Streamlink")
    http.send_header("Content-type", type)
    http.end_headers()

def sendOfflineMP4(http, send_headers=True, file2send="offline.mp4"):
    if not file2send.startswith('/'):
        file2send = os.path.join('/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/streams/', file2send)
    print("Send Offline clip: %s" % file2send)
    if send_headers:
        sendHeaders(http, type="video/mp4")
    infile = open(file2send, "rb").read()
    http.wfile.write(infile)
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
        elif os.path.getsize(file2send) == 0:
            LOGGER.debug("\twaiting for content {0} ms".format(int(1000 * 0.1 * x)))
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
            #LOGGER.debug('aqq1')
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
        os.system('kill -s 9 %s 2>/dev/null;killall -q hlsdl;killall -q ffmpeg' % pid)
        if os.path.exists(file2send):
            os.remove(file2send)
        if os.path.exists('/proc/%s') % str(pid):
            LOGGER.debug("Error killing pid {0}".format(pid))
        else:
            LOGGER.debug("pid {0} has been killed".format(pid))

def useCLI(http, url, argstr, quality, useAddr, cacheMode = False):
    LOGGER.debug("useCLI(url=%s, argstr=%s, quality=%s, useAddr=%s) >>>" %(url,argstr,quality,useAddr))
    _cmd = [] 
    _cmd.extend(['/usr/sbin/streamlink'])
    #standard SRV for different pythons.
    if cacheMode:
        cacheFile = '/hdd/slkCache.mp4'
        if os.path.exists(cacheFile):
            os.remove(cacheFile)
        _cmd.extend(['-l', LOGLEVEL, '-o', cacheFile , url, quality])
    else:
        _cmd.extend(['-l', LOGLEVEL, '--player-external-http', '--player-external-http-port', str(streamCLIport) , url, quality])
    LOGGER.debug("run command: %s" % ' '.join(_cmd))
    try:
        processCLI = subprocess.Popen(_cmd, stdout= subprocess.PIPE, stderr= subprocess.DEVNULL )
        serverRunning = False
        if processCLI:
            #waiting for CLI to proceed
            LOGGER.debug("processCLI.pid=%s : Waiting for streamlink to proceed..." % processCLI.pid)
            for x in range(1, 100):
                outLine = processCLI.stdout.readline()
                try:
                    outLine = outLine.decode('utf-8')
                except Exception:
                    pass
                if outLine != '':
                    LOGGER.debug('\t%s' % outLine.replace('\n','').strip())
                    if 'http://127.0.0.1:%s/' % streamCLIport in outLine:
                        serverRunning = True
                        redirectToStreamlinkCLI(http, useAddr)
                        return
                    elif '[download] Written' in outLine or 'Writing stream to output' in outLine:
                        mWaitTime = 10
                        sendCachedFile(http, send_headers=True, pid=int(processCLI.pid), file2send=cacheFile, maxWaitTime = mWaitTime )
                        return
                    elif 'FileCache:' in outLine:
                        retData = outLine.strip().split(':')
                        processCLI.kill()
                        if len(retData) >= 4:
                            mWaitTime = int(retData[3])
                        else:
                            mWaitTime = 10
                        sendCachedFile(http, send_headers=True, pid=int(retData[1]), file2send=retData[2], maxWaitTime = mWaitTime )
                        return
                    elif 'wperror-403' in outLine:
                        processCLI.kill()
                        sendOfflineMP4(http, send_headers=True, file2send="wperror-403.mp4")
                        return
                    elif 'wperror-422' in outLine:
                        processCLI.kill()
                        sendOfflineMP4(http, send_headers=True, file2send="wperror-422.mp4")
                        return
                    elif 'HTTP-403' in outLine:
                        processCLI.kill()
                        sendOfflineMP4(http, send_headers=True, file2send="http-403.mp4")
                        return
                    elif 'http-404' in outLine.lower():
                        processCLI.kill()
                        sendOfflineMP4(http, send_headers=True, file2send="http-404.mp4")
                        return
                time.sleep(0.1)
            try:
                open('/var/run/processPID.pid', "w").write("%s\n" % processCLI.pid)
            except Exception:
                pass
        else:
            LOGGER.error('BŁĄD: CLI subprocess not stared :(')
        
        if serverRunning == False:
            sendOfflineMP4(http)
    except Exception as e:
        LOGGER.error('EXCEPTION: %s' % str(e))
        sendOfflineMP4(http)
        
class StreamHandler(BaseHTTPRequestHandler):

    def do_HEAD(s):
        sendHeaders(s)

    def do_GET(s):
        jtools.cleanCMD()
        url = unquote(s.path[1:])
        quality = "best"
        if url.startswith('buforuj/'):
            cacheFile = True
            url = url[8:]
        else:
            cacheFile = False

        calledAddr = re.findall(r"laddr=\('([^']+)", str(s.connection))
        if calledAddr is not None and len(calledAddr)>0:
            calledAddr = calledAddr[0]
        else:
            calledAddr = '127.0.0.1'

        LOGGER.debug("Adres do odpowiedzi: %s" % calledAddr)
        LOGGER.debug("Odebrano URL: {}".format(url))
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
        LOGGER.debug("Analiza URL: {0}".format(url[0].strip()))
        useCLI(s, url[0].strip(), url[1:2], quality, calledAddr, cacheFile)
        return

    def finish(self, *args, **kw):
        LOGGER.debug("finish >>>")
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

    httpd = ThreadedHTTPServer(("", PORT_NUMBER), StreamHandler)
    try:
        sys.path.append('/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/')
        from version import Version as jVersion
    except Exception as e:
        jVersion = str(e)
    LOGGER.info("####################mod j00zek#####################")
    LOGGER.info("{0} Serwer ({1} - {2}) uruchomiony".format(time.asctime(), __version__, jVersion))
    LOGGER.info("Port:            {0}".format(PORT_NUMBER))
    LOGGER.info("OS:              {0}".format(platform.platform()))
    LOGGER.info("Python:          {0}".format(platform.python_version()))
    LOGGER.info("###################################################")
    

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("Przerwano! Kończę...")
    httpd.server_close()
    LOGGER.info("{0} Serwer zatrzymany , Port: {1}".format(time.asctime(), PORT_NUMBER))


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
                #sys.stderr.write('Missing pid file for already running streamlinkSRV?')
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

        sys.stdout.write('Serwer streamlinka uruchomiony, poziom logowania: %s\n' % LOGLEVEL)
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
        jtools.cleanCMD(forceKill = True)
        
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
            if err.find("No such process") > 0 or err.find("Brak procesu") > 0:
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
    daemon = StreamlinkDaemon("/var/run/streamlinkSRV.pid")
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
            else:
                _loglevel = LOGLEVEL = "debug"
            start()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("użyj: %s start|stop|restart|manualstart" % sys.argv[0])
        print("          manualstart najpierw zatrzymuje demona")
        sys.exit(2)