#to jest po to, zeby sciezki we wtyczkach sie zgadzaly
import sys
for pTa in ['/usr/lib/enigma2/python/Plugins/Extensions/E2Kodi/site-packages/emukodi',
           ]:
  if pTa not in sys.path:
    sys.path.append(pTa)
