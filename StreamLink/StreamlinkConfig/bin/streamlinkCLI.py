#!/usr/bin/python3
import os, subprocess, sys
print('PRZYKLAD: streamlink -l debug [ -o /tmp/fileName] "url" best')
#os.nice(-10)

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

pid = os.getpid()
fname = '/var/run/%s.pid' % os.path.basename(__file__).replace('.pyc', '').replace('.pyo', '').replace('.py', '')
if os.path.exists(fname):
    #print('[%s] found, killing process' % fname )
    pid2del = open(fname , 'r').read().strip()
    os.remove(fname)
    subprocess.Popen('kill %s 2>/dev/null;sleep 0.3;rm -f /tmp/streamlinkpipe-%s-* 2>/dev/null' % (pid2del,pid2del), shell=True)
with open(fname , 'w') as f:
    f.write(str(pid))
    f.close()

import streamlink_cli.main
#print('main()')
streamlink_cli.main.main()
