find /usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayerMario/hosts/ -iname *.py | 
  while read F 
  do
    sed 's/config\.plugins\.iptvplayer\./config.plugins.IPTVPlayerMario./g' -i "$F"
    sed "s/['\"]IPTVPlayer['\"]/'IPTVPlayerMario'/g" -i "$F"
    sed "s;Extensions/IPTVPlayer/;Extensions/IPTVPlayerMario/;g" -i  "$F"
    sed "s/Extensions\.IPTVPlayer\./Extensions.IPTVPlayerMario./g" -i "$F"
  done
