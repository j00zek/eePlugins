myPath=$(dirname $0)
myAbsPath=$(readlink -fn "$myPath")
MainPAth=$myAbsPath/MSNweatherTMP/

for paczka in deszcz_bez_parasolki deszcz_nad_parasolka deszcz_pod_parasolka
do
  [ -e $MainPAth ] && rm -rf $MainPAth
  cp -rf $myAbsPath/MSNweather_wspolna_baza $MainPAth
  cp -rf $myAbsPath/MSNweather_dodatkowe/* $MainPAth
  
  cp -rf $myAbsPath/MSNweather_dodatkowe_$paczka/* $MainPAth
  
  pkgname=$(echo $paczka|tr _ -)
  echo "Package: enigma2-plugin-picons--j00zeks-msnweather-animated-icons-$pkgname"

  echo "Package: enigma2-plugin-picons--j00zeks-msnweather-animated-icons-$pkgname
Priority: optional
Section: utils
Depends: enigma2-plugin-skins--j00zeks-blackharmonyfhd
Description: Animowane ikony pogody dla skórki BlackHarmony
Maintainer: j00zek
Source: http://github.com/j00zek/eePlugins
Version: 21.01.15.1627
Architecture: all
DestinationPath: /usr/share/enigma2/animatedWeatherIcons" > $MainPAth/CONTROL/control

  /DuckboxDisk/github/eePlugins/build_ipk.sh $MainPAth
done
[ -e $MainPAth ] && rm -rf $MainPAth
