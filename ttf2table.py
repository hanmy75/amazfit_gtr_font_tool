#!/usr/bin/python3
import sys, os
import png
import glob
import argparse
from struct import unpack
from PIL import Image, ImageDraw, ImageFont


table_width  = 8
table_height = 8

# https://jrgraphix.net/research/unicode_blocks.php
font_range_list = [
     [0x20, 0x007f]    # ASCII
]

def RotateRowCol(in_buffer):
    rotated_buffer = bytearray(16)
    for i in range(0,7):
        value = 0
        for j in range(0,5):
            bit = (in_buffer[j] >> (7-i)) & 0x01
            value = value | (bit << (4-j))
        rotated_buffer[i] = value & 0xff
    return rotated_buffer

def GenerateTable():
    for sub_range in font_range_list:
        start = sub_range[0]
        end   = sub_range[1]
        print(" # Font table 0x%02x ~ 0x%02x" % (start, end))
        print("FontTable = [")
        for uni in range(start, end+1):
            unicodeChars = chr(uni)
            # Open PNG
            theImage = Image.open(output_path + "/" + "%04x.png" % uni)
            finalImage = Image.new('1', (table_width, table_height), color='black')
            finalImage.paste(theImage, (0, 0))

            # Rotate Row and Col
            raw_buffer = finalImage.tobytes()
            rotated_buffer = RotateRowCol(raw_buffer)

            print("    [0x%02x, 0x%02x, 0x%02x, 0x%02x, 0x%02x, 0x%02x, 0x%02x, 0x%02x], # %c" % (rotated_buffer[0], rotated_buffer[1], rotated_buffer[2], rotated_buffer[3], rotated_buffer[4], rotated_buffer[5], rotated_buffer[6], rotated_buffer[7], unicodeChars))
        print("]")

def ConvertTTF2PNG(font_path, font_size):
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

            # Draw font
            theImage = Image.new('1', (width, height), color='black')
            theDrawPad = ImageDraw.Draw(theImage)
            theDrawPad.text((0.0, 0.0), unicodeChars[0], font=font, fill='white' )

            # Crop and past image
            croppedImage = theImage.crop((offset_x, offset_y, offset_x+width, offset_y+height))
            finalImage = Image.new('1', (table_width, table_height), color='black')
            finalImage.paste(croppedImage, (1, 0))

            print("Create %04x : size(%d,%d)" % (uni, cropped_width, cropped_height))
            file_name = output_path + "/" + "%04x" % (uni)
            finalImage.save('{}.png'.format(file_name))



# Main
parser = argparse.ArgumentParser(description="Convert TTF to PNG")
parser.add_argument("filename",
                    help="<filename>")
args = parser.parse_args()

if args.filename:
    output_path = "./output"
    os.makedirs(output_path, exist_ok = True)
    #ConvertTTF2PNG(args.filename, font_size=10)
    GenerateTable()
else:
    print('Usage:')
    print('   python3', sys.argv[0], 'NanumGothicBold.ttf')
