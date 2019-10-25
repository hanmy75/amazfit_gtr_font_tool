#!/bin/bash

ttf_file=$1
font_output=$2

default_png=font/default_png.tgz
png_folder=output

# Check argument
if [ $# -ne  2 ]; then
	echo "Useage : $0 <TTF font> <Font output>"
	echo "         $0 font/NanumGothicBold.ttf nanumgothicbold.ft"
	exit 1
fi

# Copy default PNG
rm -rf $png_folder
mkdir -p $png_folder
tar -zxf $default_png -C $png_folder

# Convert TTF to PNG
python3 ttf2png.py $ttf_file

# Packaging GTR font
python3 fonttool-gtr.py -d $png_folder pack $font_output
