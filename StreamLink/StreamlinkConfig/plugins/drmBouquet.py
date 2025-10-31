import sys

if __name__ == '__main__':
    # /usr/bin/python /usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig/plugins/drmBouquet.py /etc/enigma2/userbouquet.cda.tv cda 8088 0 y 
    file_name = sys.argv[1]
    providerName = sys.argv[2]
    streamlinkURL = 'http%%3a//127.0.0.1%%3a%s/' % sys.argv[3]
    frameWork = str(sys.argv[4])
    if frameWork == "0":
        frameWork = "4097"
    exec('from pywidevinecdm.%sMain import generate_E2bouquet' % providerName)
    generate_E2bouquet(file_name, frameWork, streamlinkURL)
