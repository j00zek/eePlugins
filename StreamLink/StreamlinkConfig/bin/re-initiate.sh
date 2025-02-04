#!/bin/sh
echo "(Re)inicjacja komponentów"
plugBinDir='/usr/lib/enigma2/python/Plugins/Extensions/StreamlinkConfig'

pythonType='unknown'
if [ -e /usr/lib/python3.12 ]; then
  pythonType='python3.12'
elif [ -e /usr/lib/python3.11 ]; then
  pythonType='python3.11'
elif [ -e /usr/lib/python3.10 ]; then
  pythonType='python3.10'
elif [ -e /usr/lib/python3.9 ]; then
  pythonType='python3.9'
else
  [ -e /etc/opkg/opkg-j00zka.conf ] && rm -f /etc/opkg/opkg-j00zka.conf
  exit 1
fi

for entry in "$plugBinDir/bin/site-packages"/*
  do
    entryName=`basename "$entry"`
    destEntry="/usr/lib/$pythonType/site-packages/$entryName"
    if [ -e "$destEntry" ] && [ ! -L "$destEntry" ];then
      echo "Paczkę $entryName zainstalowao już z nieznanego źródła."
    elif [ ! -e $destEntry ];then
      echo "Instaluję paczkę $entryName"
      ln -sf "$entry" "$destEntry"
    #else
    #  echo "Paczka $entryName jest już zainstalowana."
    fi
  done

if [ ! -f /usr/sbin/streamlink ];then
  ln -sf $plugBinDir/bin/streamlinkCLI.py /usr/sbin/streamlink
  ln -sf $plugBinDir/bin/streamlinkCLI.py $plugBinDir/bin/streamlinkProxy.py
  ln -sf $plugBinDir/bin/streamlinkCLI.py $plugBinDir/bin/streamlinkRecorder.py
fi

if [ ! -f /usr/sbin/streamlinkSRV ];then
  ln -sf $plugBinDir/bin/streamlinkSRV.py /usr/sbin/streamlinkSRV
  #ln -sf $plugBinDir/bin/streamlinkSRV.py /etc/init.d/streamlinkSRV
  ln -sf $plugBinDir/bin/streamlinkSRV.py streamlinkproxySRV.py /usr/sbin/streamlinkproxySRV
  #ln -sf /usr/sbin/streamlinkSRV /etc/rc3.d/S50streamlinkSRV
  #ln -sf /usr/sbin/streamlinkSRV /etc/rc4.d/S50streamlinkSRV
  echo "Mod j00zka serwera streamlink zainstalowany"
  mkdir -p /etc/streamlink
  [ ! -f /etc/streamlink/config ] && cp $plugBinDir/bin/etc_streamlink_config.template /etc/streamlink/config
fi

[ ! -e /usr/sbin/streamlinkSRV ] && ln -sf $plugBinDir/bin/streamlinkSRV.py /usr/sbin/streamlinkSRV
[ ! -e /usr/sbin/streamlinkproxySRV ] &&   ln -sf $plugBinDir/bin/streamlinkproxySRV.py /usr/sbin/streamlinkproxySRV
mkdir -p /etc/streamlink
[ ! -f /etc/streamlink/config ] && cp $plugBinDir/bin/etc_streamlink_config.template /etc/streamlink/config

exit 0
