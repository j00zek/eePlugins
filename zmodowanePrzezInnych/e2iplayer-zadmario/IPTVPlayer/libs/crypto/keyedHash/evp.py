# -*- coding: utf-8 -*-
import sys

def EVP_BytesToKey(md, data, salt, keyLength, ivLength, count):
    #below probably also works for py2, to check later when issue resolved
    if sys.version_info[0] == 3:
        dtot =  md(data + salt).digest()
        d = [ dtot ]
        while len(dtot)<(ivLength+keyLength):
            d.append( md(d[-1] + data + salt).digest() )
            dtot += d[-1]
        return dtot[:keyLength], dtot[keyLength:keyLength+ivLength]

    assert(data)
    assert(keyLength > 0)
    assert(ivLength >= 0)
    if salt:
        assert(len(salt) == 8)
    assert(count >= 1)

    key = iv = hashed = ''

    while 1:
        m = md()
        if hashed:
            m.update(hashed)
        m.update(data)
        if salt:
            m.update(salt)
        hashed = m.digest()

        for i in xrange(count - 1):
            m = md()
            m.update(hashed)
            hashed = m.digest()

        keyNeeds = keyLength - len(key)
        tmp = hashed

        if keyNeeds > 0:
            key += tmp[:keyNeeds]
            tmp = tmp[keyNeeds:]
        ivNeeds = ivLength - len(iv)
        if tmp and (ivNeeds > 0):
            iv += tmp[:ivNeeds]

        if keyNeeds == ivNeeds == 0:
            break

    return key, iv
