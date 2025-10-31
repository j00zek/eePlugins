copy offline.png to new name
add text on it
generate mp4 using the following commance
ffmpeg  -loop 1 -i /tmp/inFile.png -vf fps=1/1 -ss 00:00:00 -t 00:00:10 -crf 35 /tmp/outFile.mp4 -y
for extplayer
ffmpeg -loop 1 -i /tmp/inFile.png -c:v libx264 -t 5 -pix_fmt yuv420p /tmp/outFile.mp4 -y