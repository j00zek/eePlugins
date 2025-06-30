echo "searching for png's with wrong colors depth"

Katalogi=("/DuckboxDisk/github/eePlugins/BH/usr/share/enigma2/BlackHarmony/menu"
'/DuckboxDisk/github/eePlugins/BH/usr/share/enigma2/BlackHarmony/allBars/bar_standard_light.menu'
'/DuckboxDisk/github/eePlugins/BH/usr/share/enigma2/BlackHarmony/allBars/bar_standard.menu'
'/DuckboxDisk/github/eePlugins/BHextensions/allBars/'
)

for kat in ${Katalogi[*]};
do
#  find $kat -iname "*.png" -type f | xargs -I{} identify -format '%i %[bit-depth]\n ' {} | awk '$2=24' | convert -depth 8 {} /tmp/{}
  find $kat -iname "*.png" -type f | xargs -I{} identify -format '%i %[bit-depth]\n ' {} | awk '$2=24' |
  while read F
  do
    F2=`echo "$F"| cut -d ' ' -f1`
    if [ -e "$F2" ];then
      echo "$F"
      convert "$F2" -depth 8 /tmp/tmp.png
      mv -f /tmp/tmp.png "$F2"
    fi
  done 
done


#checking missing files
