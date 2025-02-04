echo "_crop_Images.sh <fileName(s) with path> <crop parameters>"
echo "example crop single images:   _crop_Images.sh ./Animated_Messagebox_j00zek/img.jpg 980x345+470+330"
echo "example crop multiple images: _crop_Images.sh ./Animated_Messagebox_j00zek/ALL.jpg 980x345+470+330"

#/DuckboxDisk/github/eePlugins/BHaP/_crop_Images.sh /DuckboxDisk/github/eePlugins/BHaP/Animated_Messagebox_j00zek/Confused-100_00.jpg 980x335+470+330

#/DuckboxDisk/github/eePlugins/BHaP/_crop_Images.sh /DuckboxDisk/github/eePlugins/BHaP/Animated_Messagebox_j00zek/Confused-100_*.jpg 980x335+470+330 /DuckboxDisk/github/eePlugins/BHaP/Animated_Messagebox_j00zek/Confused-%02d.jpg
#cd mogrify -crop 980x335+470+330 *.jpg
if [ -z $1 ];then exit 0
elif [ -z $2 ];then exit 0
elif [ ! -f $1 ];then exit 0
else
  echo
fi

imageToCrop=$1
CropParams=$2

if [ `echo $aqq|grep -c '/ALL.jpg$'` -gt 0 ];then
  dirName=`dirname "$imageToCrop"`
  cd $dirName
  fileExtension=`basename "$imageToCrop"|sed 's/^.*\.//'`
  mogrify -crop $CropParams *.$fileExtension
else
  convert $imageToCrop -crop $CropParams Cropped$imageToCrop
fi


