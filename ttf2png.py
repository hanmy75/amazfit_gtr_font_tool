import sys, os
import numpy as np
import png
import argparse
from PIL import Image, ImageDraw, ImageFont

font_postfix = "181a190018ff0001"

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
        theImage = Image.new('L', (font_size, font_size+2), color='black')
        theDrawPad = ImageDraw.Draw(theImage)
        theDrawPad.text((0.0, -1.0), unicodeChars[0], font=font, fill='white' )

        file_name = output_path + "/" + uni + "-" + font_postfix
        theImage.save('{}.png'.format(file_name))

        print("Create %04x : size(%d,%d)" % (int(uni,16), theImage.width, theImage.height))


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
