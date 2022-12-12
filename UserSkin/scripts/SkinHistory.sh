# @j00zek 2015 dla Graterlia
#
skinpath=$1
if [ ! -f $skinpath/skin.config ]; then
  echo "_(This skin does not have the history of changes.)"
  exit 0
fi
. $skinpath/skin.config
if [ -z $history ];then
  echo "_(This skin does not have the history of changes.)"
  exit 0
fi

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

curl -s --ftp-pasv $history -o /tmp/history.txt
if [ $? -gt 0 ]; then
  echo "_(Error downloading the history of changes)"
  exit 0
fi

cat /tmp/history.txt
rm -r /tmp/history.txt >/dev/null
exit 0