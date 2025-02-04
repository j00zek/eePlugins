find /usr/lib/enigma2/python/Plugins/Extensions/E2Kodi/site-packages/emukodislink* -iname *.py | 
  while read F 
  do
    #echo "$F"
	#sed "s/import streamlink/import emukodislink/g" -i "$F"
    #sed "s/from streamlink import/from emukodislink import/g" -i "$F"
    #sed "s/from streamlink\./from emukodislink./g" -i "$F"
    #sed "s/streamlink\./emukodislink./g" -i "$F"

	#sed "s/import streamlink_cli/import emukodislink_cli/g" -i "$F"
    #sed "s/from streamlink_cli import/from emukodislink_cli import/g" -i "$F"
    #sed "s/from streamlink_cli\./from emukodislink_cli./g" -i "$F"
    #sed "s/streamlink_cli\./emukodislink_cli./g" -i "$F"
    sed "s/streamlink/emukodislink/g" -i "$F"
  done
sed 's/\(log.debug."Dependencies:"\)/return\n#\1/' -i /usr/lib/enigma2/python/Plugins/Extensions/E2Kodi/site-packages/emukodislink_cli/main.py
