echo "Usage: resize-SEL-bar-In-all.sh <source filename> <new size> <destination filename>"
echo "Example:resize-SEL-bar-In-all.sh sel_1390_100.png 1390x70 sel_1390_70.png"
echo
if [ -z $1 ]; then
  echo "Missing source picture name"
  exit 1
elif [ -z $2 ]; then
  echo "Missing destination size"
  exit 1
elif [ -z $3 ]; then
  echo "Missing destination filename"
  exit 1
fi

Katalogi=("/DuckboxDisk/github/eePlugins/BH/usr/share/enigma2/BlackHarmony/menu"
'/DuckboxDisk/github/eePlugins/BH/usr/share/enigma2/BlackHarmony/allBars/bar_blue.menu'
'/DuckboxDisk/github/eePlugins/BH/usr/share/enigma2/BlackHarmony/allBars/bar_gold.menu'
'/DuckboxDisk/github/eePlugins/BH/usr/share/enigma2/BlackHarmony/allBars/bar_gray.menu'
'/DuckboxDisk/github/eePlugins/BH/usr/share/enigma2/BlackHarmony/allBars/bar_standard_light.menu'
'/DuckboxDisk/github/eePlugins/BH/usr/share/enigma2/BlackHarmony/allBars/bar_standard.menu'
)

for kat in ${Katalogi[*]};
do
  if [ -e $kat/$1 ];then
    echo "Resizing $kat/$1 to $kat/$3"
    convert $kat/$1 -resize $2 $kat/$3
  else
    echo "No $kat/$1 file!!!"
  fi
done


#checking missing files
