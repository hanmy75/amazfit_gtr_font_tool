#!/usr/bin/python3
import sys, os
import png
import glob
import argparse
from struct import unpack
from PIL import Image, ImageDraw, ImageFont


test_string = "ABCD가나다라"
test_image_filename = "test_image.png"
canvas_width = 200
canvas_height = 50
canvas_baseline = 30
vo_base = 4
font_postfix = "ff0001"


#http://www.brescianet.com/appunti/vari/unicode.htm#Latino_base
#w+ is the w+ the space between the next char
#vo is the vertical offset of the image...
#ofs         Ul  Uh w  h  vo    w+
#00 00 00 00 00  00 00 00 00 00 00 ff 00 01 nul
#00 00 00 00 0d  00 00 00 00 00 08 ff 00 01 cr
#00 00 00 00 20  00 00 00 00 00 08 ff 00 01 sp
#00 00 00 00 21  00 04 16 16 02 08 ff 00 01 !
#2c 00 00 00 22  00 0a 08 16 01 0c ff 00 01 "
#59 00 00 00 23  00 13 16 16 00 13 ff 00 01 #
#35 01 00 00 24  00 0f 1a 17 01 11 ff 00 01 $
#3e 37 00 00 a2  00 0d 16 16 02 11 ff 00 01 c/

# https://jrgraphix.net/research/unicode_blocks.php
font_range_list = [
#    [0x2150, 0x218f],  # Number Forms
#    [0x2190, 0x21ff],  # Arrows
#    [0x2200, 0x22ff],  # Mathematical Operators
#    [0x2460, 0x24ff],  # Enclosed Alphanumerics
#    [0x2500, 0x257f],  # Box Drawing
#    [0x25a0, 0x25ff],  # Geometric Shapes
#    [0x2600, 0x26ff],  # Miscellaneous Symbols
#    [0x2700, 0x27bf],  # Dingbats
#    [0x3040, 0x309f],  # Hiragana
#    [0x30a0, 0x30ff],  # Katakana
    [0x3130, 0x318f],  # Hangul Compatibility Jamo
    [0xac00, 0xd7a3],  # Hangul Syllables
]

def RemoveExistCharacter():
    for sub_range in font_range_list:
        start = sub_range[0]
        end   = sub_range[1]
        for uni in range(start, end+1):
            # Remove existing character
            for n in glob.glob(output_path + "/" + "%04x*" % uni):
                if os.path.isfile(n):
                    print("Remove %s" % n)
                    os.remove(n)

def DrawTestString(string):
    # Create image
    theImage = Image.new('L', (canvas_width, canvas_height), color='black')
    tuple_of_shorts = unpack('H'*(len(string)//2),string)
    x = 4
    y = 4
    for uni in tuple_of_shorts:
        if uni == 0xfeff:
            continue
        for n in glob.glob(output_path + "/" + "%04x*" % uni):
            if os.path.isfile(n):
                position_info = n.split('-')[1]
                width  = int(position_info[0:2], 16)
                height = int(position_info[2:4], 16)
                vo     = int(position_info[4:6], 16)
                ho     = int(position_info[6:8], 16)
                next_offset = int(position_info[8:10], 16)
                if vo>=128:
                    vo = vo - 256
                if ho>=128:
                    ho = ho - 256

                #print("Data[%04x] %d,%d - %d,%d" % (uni, ho, vo, width, height))

                im = Image.open(n)
                theImage.paste(im, (x+ho,y+canvas_baseline-vo))
                x = x + next_offset
    theImage.save(test_image_filename)


def ConvertTTF(font_path, font_size):
    font = ImageFont.truetype(font=font_path, size = font_size)
    ascent, descent = font.getmetrics()

    for sub_range in font_range_list:
        start = sub_range[0]
        end   = sub_range[1]
        for uni in range(start, end+1):
            unicodeChars = chr(uni)

            width, height = font.getsize(unicodeChars)
            (width, baseline), (offset_x, offset_y) = font.font.getsize(unicodeChars)
            cropped_width  = width  - offset_x
            cropped_height = height - offset_y

            if cropped_width>0 and cropped_height>0 :
                theImage = Image.new('L', (width, height), color='black')
                theDrawPad = ImageDraw.Draw(theImage)
                theDrawPad.text((0.0, 0.0), unicodeChars[0], font=font, fill='white' )
                croppedImage = theImage.crop((offset_x, offset_y, width, height))

                # Get vertical offset
                vo = ascent - offset_y + vo_base

                print("Create %04x : size(%d,%d) offset %d" % (uni, cropped_width, cropped_height, vo))

                file_name = output_path + "/" + "%04x-%02x%02x%02x%02x%02x%s" % (uni, cropped_width, cropped_height, vo&0xff, offset_x&0xff, width, font_postfix)
                croppedImage.save('{}.png'.format(file_name))
            else :
                file_name = output_path + "/" + "%04x-%02x%02x%02x%02x%02x%s.png" % (uni, 0, 0, 0, 0, width, font_postfix)
                dummypng = open(file_name, "wb")
                dummypng.close()


# Main
parser = argparse.ArgumentParser(description="Convert TTF to PNG")
parser.add_argument("filename",
                    help="<filename>")
args = parser.parse_args()

if args.filename:
    output_path = "./output"
    os.makedirs(output_path, exist_ok = True)
    #RemoveExistCharacter()
    ConvertTTF(args.filename, font_size=26)
    DrawTestString(test_string.encode('utf-16'))
else:
    print('Usage:')
    print('   python3', sys.argv[0], 'NanumGothicBold.ttf')
