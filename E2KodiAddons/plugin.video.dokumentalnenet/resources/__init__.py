#to jest po to, zeby sciezki we wtyczkach sie zgadzaly
import sys
for p in sys.path:
    if p.endswith('site-packages'):
        p1 = p + '/emukodi'
        if p1 not in sys.path:
            sys.path.append(p1)
