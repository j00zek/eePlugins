#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#   Coded by j00zek
#

import os
import re
import sys

if __name__ == '__main__':
    if len(sys.argv) >=3:
        bouquetFileName = sys.argv[1]
        msg = sys.argv[2]
        if os.path.exists(bouquetFileName):
            os.system('rm -f %s' % bouquetFileName)
            print(msg)
