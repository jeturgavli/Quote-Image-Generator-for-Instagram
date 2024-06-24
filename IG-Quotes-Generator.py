import os
from PIL import Image, ImageDraw, ImageFont
import colorama
from colorama import Fore, Back, Style
colorama.init(autoreset=True)

def get_text_color():
    while True:
        color = input("Enter text color (white or black): ").strip().lower()
        if color == 'white':
            return (255, 255, 255)
        elif color == 'black':
            return (0, 0, 0)
        else:
            print("Invalid color. Please try again.")

def save_image(image, filename):
    output_dir = 'Quotes_Output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    image.save(f'{output_dir}/{filename}.jpg')

def main():
    template = input("Choose Background: ")
    templateBg = Image.open(f'Backgrounds/{template}.jpg')

    font_object = ImageFont.truetype('Fonts/arial.ttf', 40)
    drawing_object = ImageDraw.Draw(templateBg)

    Parmanet_BG = Image.open('Program Stuff/Img-2.png')
    templateBg.paste(Parmanet_BG, Parmanet_BG)

    texts = []
    for i in range(5):
        texts.append(input(f"{i+1} line: "))

    text_color = get_text_color()

    # Default text location
    x = 120
    y_start = 750
    line_height = 50

    # Add text
    for i, text in enumerate(texts):
        y = y_start + line_height * i
        drawing_object.text((x, y), text, fill=text_color, font=font_object)

    # Preview the image
    templateBg.show()

    image_name = input("Enter image name: ")
    save_image(templateBg, image_name)

    repeat = input("Would you like to run again? (y/n): ").lower()
    if repeat == "y":
        main()
    else:
        print("Exiting...")

if __name__ == '__main__':
    main()
