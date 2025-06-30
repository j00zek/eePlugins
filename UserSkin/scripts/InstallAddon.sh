# @j00zek 2015 dla Graterlia
#
#$2 = sciezka do aktualnej skorki

. $2/skin.config
addon=$1

echo "_(Downloading )$addon..."
curl -kLs --ftp-pasv $addons/$addon -o /tmp/$addon
if [ $? -gt 0 ]; then
  echo "_(Archive downloaded improperly)"
  exit 0
fi

echo "_(Checking archive consistency)..."
tar -tzf /tmp/$addon >/dev/null
if [ $? -gt 0 ]; then
  echo "_(Archive is broken)"
  exit 0
fi

echo "_(Unpacking )$addon..."
cd /
tar -zxf /tmp/$addon 2>/dev/null
if [ $? -gt 0 ]; then
  echo "_(Archive unpacked improperly)!!!"
else
  echo
  echo "_(Success: Addon ready to use.)"
fi
rm -rf /tmp/$addon
exit 0
