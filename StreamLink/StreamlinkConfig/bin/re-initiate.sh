#!/bin/sh
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
    if [ -e /usr/lib/$pythonType/site-packages/$entryName ] && [ ! -L /usr/lib/$pythonType/site-packages$entryName ];then
      echo "Paczkę $entryName zainstalowao już z nieznanego źródła."
    elif [ ! -e /usr/lib/$pythonType/site-packages/$entryName ];then
      echo "Instaluję paczkę $entryName"
      ln -sf "$entry" "/usr/lib/$pythonType/site-packages/$entryName"
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
  ln -sf $plugBinDir/bin/streamlinkSRV.py /etc/init.d/streamlinkSRV
  ln -sf /usr/sbin/streamlinkSRV /etc/rc3.d/S50streamlinkSRV
  ln -sf /usr/sbin/streamlinkSRV /etc/rc4.d/S50streamlinkSRV
  echo "Mod j00zka serwera streamlink zainstalowany"
  mkdir -p /etc/streamlink
  [ ! -f /etc/streamlink/config ] && cp $plugBinDir/bin/etc_streamlink_config.template /etc/streamlink/config
fi

#tworzenie linkow w strukturze drzewa
if [ -e "/usr/lib/$pythonType/site-packages/streamlink" ];then
  echo "Dołączanie pakietów emukodi i streamlink_cli do pythona..."
  ln -sf $plugBinDir/bin/jtools.py /usr/lib/$pythonType/site-packages/streamlink/jtools.py
  ln -sf $plugBinDir/bin/e2config.py /usr/lib/$pythonType/site-packages/streamlink/e2config.py
  [ -e /usr/lib/$pythonType/site-packages/emukodi ] || ln -sf "$plugBinDir/plugins/emukodi" /usr/lib/$pythonType/site-packages/emukodi
  [ -e /usr/lib/$pythonType/site-packages/streamlink_cli ] || ln -sf "$plugBinDir/plugins/streamlink_cli" /usr/lib/$pythonType/site-packages/streamlink_cli
  echo "Dołączanie nieoficjalnych wtyczek j00zka do streamlinka..."
  find -L "/usr/lib/$pythonType/site-packages/streamlink" -name *.py -type l -exec  rm {} +
  find $plugBinDir/plugins/unofficial/ -iname *.py|while read f; do
    #echo "$f"
    f2=`echo "$f"|sed "s;$plugBinDir/plugins/unofficial/;;"`
    #echo "$f2"
    ln -sf "$f" "/usr/lib/$pythonType/site-packages/streamlink/$f2"
  done

  if [ `grep -c '__version_date__' < "/usr/lib/$pythonType/site-packages/streamlink/__init__.py"` -lt 1 ];then
    echo "Modyfikuję __init__.py ..."
    sed -i '/del get_versions/i __version_date__ = get_versions()["date"]' /usr/lib/$pythonType/site-packages/streamlink/__init__.py
  fi

  if [ `grep -c 'except ImportError as e:' < "/usr/lib/$pythonType/site-packages/streamlink/utils/l10n.py"` -lt 1 ];then
    echo "Modyfikuję l10n.py ..."
    sed -i 's/\(^except ImportError\)\(:.*\)/\1 as e\2\n    print(str(e))\n/' /usr/lib/$pythonType/site-packages/streamlink/utils/l10n.py
  fi


  if [ `grep -c '#j00zek_patch 1' < "/usr/lib/$pythonType/site-packages/streamlink_cli/main.py"` -lt 1 ];then
    echo "Modyfikuję streamlink_cli/main.py ..."
    sed -i 's/\(from socks import __version__ as socks_version\)/\n#j00zek_patch 1\ntry: \1\nexcept Exception: from websocket import __version__ as socks_version\n/' /usr/lib/$pythonType/site-packages/streamlink_cli/main.py
  fi
fi
exit 0
