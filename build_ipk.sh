#!/bin/bash

myPath=$(dirname $0)
myAbsPath=$(readlink -fn "$myPath")
ipkdir=/tmp/IPK

if [ -z $1 ]; then
  echo "Error: no path to plugin provided, please us build_ipk.sh <path_to_plugin> [version]"
  exit 0
elif [ $(echo $1|grep -c $myPath) -eq 0 ]; then
  echo "Error: provided pluginpath is NOT subfolder of script path"
  exit 0
elif [ ! -e "$1" ]; then
  echo "Error: provided pluginpath does NOT exist"
  exit 0
elif [ ! -d "$1" ]; then
  echo "Error: provided pluginpath is NOT a directory"
  exit 0
elif [ ! -e "$1/CONTROL/control" ]; then
  echo "Error: required by ipk control file missing"
  exit 0
fi
plugAbsPath=$(readlink -fn "$1")
PluginName_lower=`grep 'Package:' < $plugAbsPath/CONTROL/control|cut -d ':' -f2|xargs`
PluginPath=`grep 'DestinationPath:' < $plugAbsPath/CONTROL/control|cut -d ':' -f2|xargs`
ExcludeFolder=`grep 'ExcludeFolder' < $plugAbsPath/CONTROL/control|cut -d ':' -f2|xargs`
RunScriptBeforeBuild=`grep 'RunScriptBeforeBuild' < $plugAbsPath/CONTROL/control|cut -d ':' -f2|xargs`

#sprawdzanie czy xmle nie maja bledow
find $plugAbsPath -iname "*.xml" | 
  while read F 
  do
    xmllint --noout "$F"
    if [[ $? -gt 0 ]];then
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR in XML !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      exit 1
    fi
  done
[ $? -gt 0 ] && exit 1
#sprawdzanie czy py nie maja bledow
echo "import sys
filename = sys.argv[1]
source = open(filename, 'r').read() + '\n'
compile(source, filename, 'exec')
" > /tmp/checker.py

find $plugAbsPath -iname "*.py" | 
  while read F 
  do
    python /tmp/checker.py "$F"
    if [[ $? -gt 0 ]];then
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR in PY !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      exit 1
      break
    fi
  done
[ $? -gt 0 ] && exit 1
#find $plugAbsPath -iname "*.py" | 
#  while read F 
#  do
#    [ -e "${F/.py/.pyo}" ] || touch "${F/.py/.pyo}"
#    [ -e "${F/.py/.pyc}" ] && rm -f "${F/.py/.pyc}"
#    [ -e "${F/.py/.py~}" ] && rm -f "${F/.py/.py~}"
#    [ -e "$F" ] && rm -f "${F/.py/.pyo}"
#  done
if [ -z $2 ]; then
  echo "Info: no version provided, date &time of last modification will be used"
  #version=`ls -atR --full-time "$plugAbsPath/"|egrep -v '^dr|version.py|control|*.mo'|grep -m 1 -o '20[12][5678].[0-9]*.[0-9]* [0-9]*\:[0-9]*'|sed 's/^20//'|sed 's/ /./'|sed 's/-/./g'|sed 's/\://g'`
  version=`ls -atR --full-time "$plugAbsPath/"|egrep -v '^dr|version\.py|control|*\.mo'|grep -o '20[12][901].[0-9]*.[0-9]* [0-9]*\:[0-9]*'|sort -r|head -1|sed 's/^20//'|sed 's/ /./'|sed 's/-/./g'|sed 's/\://g'`
  versionFileName=`find "$plugAbsPath/" -name version.py ! -path "*/tsiplayer/*"`
  echo "Found version file: '$versionFileName'"
  echo "'$version'"
  [ -z $version ] && echo "Error getting version" && exit 0
else
  version=$2
fi
sed -i "s/^Version\:.*/Version: $version/" $plugAbsPath//CONTROL/control
if [ -e $plugAbsPath/version.py ];then echo "Version='$version'" > $plugAbsPath/version.py
elif [ -e $plugAbsPath/Plugins/Extensions/MSNweather/version.py ];then echo "Version='$version'" > $plugAbsPath/Plugins/Extensions/MSNweather/version.py
elif [ ! -z $versionFileName ] && [ `grep -c 'IPTV_VERSION=' < $versionFileName` -gt 0 ];then  echo "IPTV_VERSION='$version'" > $versionFileName
elif [ ! -z $versionFileName ] && [ -e $versionFileName ];then echo "Version='$version'" > $versionFileName
fi
find $plugAbsPath/ -type f -name *.po  -exec bash -c 'msgfmt "$1" -o "${1%.po}".mo' - '{}' \;
if [ ! -z $RunScriptBeforeBuild ] && [ -e $plugAbsPath/$RunScriptBeforeBuild ];then
  $plugAbsPath/$RunScriptBeforeBuild
fi

[ -e $ipkdir ] && sudo rm -rf $ipkdir
mkdir -p $ipkdir$PluginPath/
cp -a $plugAbsPath/* $ipkdir$PluginPath/
mv -f $ipkdir$PluginPath/CONTROL $ipkdir/
if [ ! -z $ExcludeFolder ] && [ -e $ipkdir/$ExcludeFolder ];then
  rm -rf $ipkdir/$ExcludeFolder
fi
#if [ -e $ipkdir/usr/lib/enigma2/python ];then
find $ipkdir/ -iname "*.py" | 
  while read F 
  do
    [ -e "${F/.py/.pyo}" ] || touch "${F/.py/.pyo}"
    [ -e "${F/.py/.pyc}" ] && rm -f "${F/.py/.pyc}"
    [ -e "${F/.py/.py~}" ] && rm -f "${F/.py/.py~}"
  done
#fi
sudo chmod 755 $ipkdir/CONTROL/post* 2>/dev/null
sudo chmod 755 $ipkdir/CONTROL/pre* 2>/dev/null
sudo chown -R root $ipkdir/
cd /tmp
sudo rm -rf /tmp/IPKG_BUILD* 2>/dev/null
rm -f ~/tmp/$PluginName_lower*
$myAbsPath/tools/ipkg-build.sh $ipkdir
#echo $PluginName_lower
if [ -d ~/opkg-repository ] && [ ! -z $PluginName_lower ];then
  rm -f ~/opkg-repository/$PluginName_lower*
  mv /tmp/$PluginName_lower* ~/opkg-repository/
fi

exit 0
