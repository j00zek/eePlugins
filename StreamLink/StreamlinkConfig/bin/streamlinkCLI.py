#!/usr/bin/python3
from streamlink.jtools import *

print('PRZYKLAD: streamlink -l debug [ -o /tmp/fileName] "url" best')
cleanCMD(forceKill = True)

import sys
idx = 0
for argument in sys.argv:
    if argument.startswith('http%3a//127.0.0.1%3a8088/'):
        argument = argument[len('http%3a//127.0.0.1%3a8088/'):]
    elif argument.startswith('http://127.0.0.1%3a8088/'):
        argument = argument[len('http://127.0.0.1%3a8088/'):]
    elif argument.startswith('http://127.0.0.1:8088/'):
        argument = argument[len('http://127.0.0.1:8088/'):]
    if argument.startswith('http%3a') or argument.startswith('https%3a'):
        argument = argument.split(':')[0]
    argument = argument.replace('%3a',':')
    sys.argv[idx] = argument
    idx += 1
#print sys.argv
import streamlink_cli.main
streamlink_cli.main.main()

cleanCMD(forceKill = True)