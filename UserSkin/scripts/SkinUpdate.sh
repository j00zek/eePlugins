# @j00zek 2015 dla Graterlia & BlackHarmony
#
[ -e /tmp/.rebootGUI ] && rm -rf /tmp/.rebootGUI

skinpath=$1
if [ ! -f $skinpath/skin.config ]; then
  echo "_(This skin is not configured for updates.)"
  exit 0
fi
. $skinpath/skin.config
if [ -z $skinurl ];then
  echo "_(This skin is not configured for updates.)"
  exit 0
fi
echo "_(Updating) $description ..."

curl --help 1>/dev/null 2>%1
if [ $? -gt 0 ]; then
  echo "_(Required program 'curl' is not installed. Trying to install it via OPKG.)"
  echo
  opkg update  1>/dev/null 2>%1
  opkg install curl
  sync
  curl --help 1>/dev/null 2>%1
  if [ $? -gt 0 ]; then
    echo
    echo "_(Required program 'curl' is not available. Please install it first manually.)"
    exit 0
  fi
fi

echo "_(Checking installation mode)..."
if `opkg list-installed 2>/dev/null | tr '[:upper:]' '[:lower:]'| grep -q 'blackharmony'`;then
  echo "_(Skin controlled by OPKG. Please use it for updates.)"
  exit 0
fi

echo "_(Downloading latest skin version)..."
tarName=`echo $skinurl|sed 's;^.*/;;'`
curl -kLs --ftp-pasv $skinurl -o /tmp/$tarName
if [ $? -gt 0 ]; then
  echo "_(Archive downloaded improperly)"
  exit 0
fi

echo "_(Checking archive consistency)..."
tar -tzf /tmp/$tarName >/dev/null
if [ $? -gt 0 ]; then
  echo "_(Archive is broken)"
  exit 0
fi

echo "_(Unpacking new version)..."
cd /
tar -zxf /tmp/$tarName 2>/dev/null
if [ $? -gt 0 ]; then
  echo "_(Archive unpacked improperly)"
else
  echo
  echo "_(Success: Skin updated properly.)"
  touch /tmp/.rebootGUI
fi

rm -rf /tmp/$tarName
exit 0
