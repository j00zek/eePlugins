# @j00zek 2015 dla Graterlia
#
#$2 = sciezka do aktualnej skorki

addon=$1
[ -e /tmp/$addon ] && rm -rf /tmp/$addon
url="https://github.com/j00zek/Converted-Skins/raw/master/$addon"

echo "_(Downloading )$addon..."
curl -kLs $url -o /tmp/$addon
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
  echo "_(Archive unpacked improperly)"
  exit 0
fi
rm -rf /tmp/$addon
echo
echo "_(Archive unpacked properly, you can select it in skin selector)"
