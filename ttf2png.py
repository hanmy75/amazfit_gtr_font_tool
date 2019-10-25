import sys, os
import numpy as np
import png
import argparse
from PIL import Image, ImageDraw, ImageFont


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

font_postfix = "ff0001"

co = "0 1 2 3 4 5 6 7 8 9 a b c d e f"
start = "ac00"
end = "d7a3"
co = co.split(" ")

Hangul_Syllables = [a+b+c+d
                    for a in co
                    for b in co
                    for c in co
                    for d in co]

Hangul_Syllables = np.array(Hangul_Syllables)
s = np.where(start == Hangul_Syllables)[0][0]
e = np.where(end == Hangul_Syllables)[0][0]
Hangul_Syllables = Hangul_Syllables[s : e + 1]


def ConvertTTF(font_path, font_size):
    output_path = "./output"
    os.makedirs(output_path, exist_ok = True)

    for uni in Hangul_Syllables:
        unicodeChars = chr(int(uni, 16))

        font = ImageFont.truetype(font=font_path, size = font_size)
        width, height = font.getsize(unicodeChars)
        theImage = Image.new('L', (font_size, font_size+2), color='black')
        theDrawPad = ImageDraw.Draw(theImage)
        theDrawPad.text((0.0, 0.0), unicodeChars[0], font=font, fill='white' )

        file_name = output_path + "/" + "%04x-%02x%02x%02x%02x%02x%s" % (int(uni,16), width, height, height-1, 1, width+2, font_postfix)
        theImage.save('{}.png'.format(file_name))

        print("Create %04x : size(%d,%d)" % (int(uni,16), width, height))



# Main
parser = argparse.ArgumentParser(description="Convert TTF to PNG")
parser.add_argument("filename",
                    help="<filename>")
args = parser.parse_args()

if args.filename:
    ConvertTTF(args.filename, font_size=24)
else:
    print('Usage:')
    print('   python3', sys.argv[0], 'NanumGothicBold.ttf')
