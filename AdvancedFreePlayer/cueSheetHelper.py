from __future__ import absolute_import #zmiana strategii ladowanie modulow w py2 z relative na absolute jak w py3
from Plugins.Extensions.AdvancedFreePlayer.__init__ import printDEBUG
from os import path as os_path
import struct
import sys
PyMajorVersion = sys.version_info.major

cutsParser = struct.Struct('>QI') # big-endian, 64-bit PTS and 32-bit type
CUT_TYPE_LAST = 3
CUT_TYPE_LENGTH = 5

DBG = True

def setCut(cutsFileName, LastPosition, Movielength):
    if LastPosition is None or LastPosition == 0 or Movielength is None or Movielength == 0:
        printDEBUG('setCut>LastPosition or Movielength not provided, end')
        return
    printDEBUG('setCut(%s, LastPosition=%d, Movielength=%d):' % (cutsFileName,LastPosition, Movielength))
    CUT_LAST_VALUE = struct.pack('>QI', LastPosition, CUT_TYPE_LAST) #in py3 returns bytes
    CUT_LENG_VALUE = struct.pack('>QI', Movielength, CUT_TYPE_LENGTH) #in py3 returns bytes
    resetMoviePlayState(cutsFileName,CUT_LAST_VALUE, CUT_LENG_VALUE)
    return

def getCut(cutsFileName):
    if DBG: printDEBUG('getCut(%s):' % cutsFileName)
    data = ''
    currpts=0
    currLength=0
    if os_path.exists(cutsFileName):
        try:
            f = open(cutsFileName, 'rb')
            data = f.read()
            f.close()
        except Exception:
            pass
        if data:
            pos = 0
            while pos + 12 <= len(data):
                pts, what = struct.unpack('>QI', data[pos:pos + 12])
                if what == CUT_TYPE_LAST and pts > currpts:
                    currpts = int(pts/90/1000/60) #in mins
                    if DBG: printDEBUG("getCuts found: CUT_TYPE_LAST, pts=%d (%d mins)" % (pts, currpts))
                elif what == CUT_TYPE_LENGTH and pts > currLength:
                    currLength = int(pts/90/1000/60)
                    if DBG: printDEBUG("getCuts found: CUT_TYPE_LENGTH, pts=%d (%d mins)" % (pts, currLength))
                else:
                    if DBG: printDEBUG("getCuts found: what=%d, pts=%d" % (what, pts))
                pos += 12
            if currLength < currpts:
                currLength = currpts
    return currpts,currLength

def resetMoviePlayState(cutsFileName, CUT_LAST_VALUE = None, CUT_LENG_VALUE = None):
    if CUT_LAST_VALUE is None or CUT_LENG_VALUE is None:
        printDEBUG('resetMoviePlayState(%s, CUT_LAST_VALUE=None, CUT_LENG_VALUE=None) >>> exiting!!!' % (cutsFileName))
        return
    else:
        if PyMajorVersion == 2:
            printDEBUG('resetMoviePlayState(%s, CUT_LAST_VALUE=%s, CUT_LENG_VALUE=%s):' % (cutsFileName, ':'.join(x.encode('hex') for x in CUT_LAST_VALUE), ':'.join(x.encode('hex') for x in CUT_LENG_VALUE) ))
        else:
            printDEBUG('resetMoviePlayState(%s, CUT_LAST_VALUE=%s, CUT_LENG_VALUE=%s):' % (cutsFileName, ':'.join(hex(x) for x in CUT_LAST_VALUE), ':'.join(hex(x) for x in CUT_LENG_VALUE) ))
    cutlist = []
    if os_path.exists(cutsFileName):
        try:
            f = open(cutsFileName, 'rb')
            while 1:
                data = f.read(cutsParser.size)
                if len(data) < cutsParser.size:
                    break
                cut, cutType = cutsParser.unpack(data)
                if cutType not in [CUT_TYPE_LAST, CUT_TYPE_LENGTH]:
                    cutlist.append(data)
            f.close()
        except Exception as e:
            printDEBUG('resetMoviePlayState exception reading cuts file %s' % str(e))
    cutlist.append(CUT_LAST_VALUE)
    cutlist.append(CUT_LENG_VALUE)
    try:
        if len(cutlist) > 0:
            if PyMajorVersion == 2:
                cutlistStr = ''.join(cutlist)
            else:
                cutlistStr = b''.join(cutlist)
            with open(cutsFileName, 'wb') as f:
                f.write(cutlistStr)
                f.close()
            #backup when recording file
            with open(cutsFileName + '2', 'wb') as f:
                f.write(b''.join([CUT_LAST_VALUE, CUT_LENG_VALUE]))
                f.close()
    except Exception as e:
        printDEBUG('resetMoviePlayState exception writing cuts file %s' % str(e))
            
    try:
        if PyMajorVersion == 2:
            printDEBUG('resetMoviePlayState has written cutsFileName len(cutlist)=%d, cutlist=%s' % ( len(cutlistStr), ':'.join(x.encode('hex') for x in cutlistStr)))
        else:
            printDEBUG('resetMoviePlayState has written cutsFileName len(cutlist)=%d, cutlist=%s' % ( len(cutlistStr), ':'.join(hex(x) for x in cutlistStr)))
        printDEBUG(cutlistStr)
    except Exception as e:
        printDEBUG('resetMoviePlayState non-critical exception: %s' % str(e))

def clearLastPosition(cutsFileName):
    cutlist = []
    if os_path.exists(cutsFileName):
        try:
            f = open(cutsFileName, 'rb')
            while 1:
                data = f.read(cutsParser.size)
                if len(data) < cutsParser.size:
                    break
                cut, cutType = cutsParser.unpack(data)
                if cutType not in [CUT_TYPE_LAST]:
                    cutlist.append(data)
            f.close()
        except Exception as e:
            printDEBUG('clearLastPosition exception reading cuts file %s' % str(e))
        try:
            if len(cutlist) > 0:
                if PyMajorVersion == 2:
                    cutlistStr = ''.join(cutlist)
                else:
                    cutlistStr = b''.join(cutlist)
                with open(cutsFileName, 'wb') as f:
                    f.write(cutlistStr)
                    f.close()
        except Exception as e:
            printDEBUG('clearLastPosition exception writing cuts file: %s' % str(e))
        try:
            if PyMajorVersion == 2:
                printDEBUG('clearLastPosition has written cutsFileName len(cutlist)=%d, cutlist=%s' % ( len(cutlistStr), ':'.join(x.encode('hex') for x in cutlistStr)))
            else:
                printDEBUG('clearLastPosition has written cutsFileName len(cutlist)=%d, cutlist=%s' % ( len(cutlistStr), ':0x'.join(hex(x) for x in cutlistStr)))
            printDEBUG(cutlistStr)
        except Exception as e:
            printDEBUG('clearLastPosition() non-critical exception: %s' % str(e))
