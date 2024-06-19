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
    image.save(f'Quotes_Output/{filename}.jpg')

def main():
    template = input("Choose Background : ")
    templateBg = Image.open(f'Backgrounds/{template}.jpg')

    font_object =  ImageFont.truetype('Fonts/arial.ttf', 40 )
    drawing_object = ImageDraw.Draw(templateBg)

    Parmanet_BG = Image.open('Program Stuff/Img-2.png')
    templateBg.paste(Parmanet_BG, Parmanet_BG)

    texts = []
    for i in range(5):
        texts.append(input(f"{i} line : "))

    text_color = get_text_color()

    #shadows
    for i, text in enumerate(texts):
        x = 122
        y = 750 + 50 * i
        drawing_object.text((x, y), text, fill=(0, 0, 0), font=font_object)

    for i, text in enumerate(texts):
        x = 120
        y = 750 + 50 * i
        drawing_object.text((x, y), text, fill=text_color, font=font_object)

    image_name = input("Enter image name: ")
    save_image(templateBg, image_name)

    repeat = input("Would you like to run again? (y/n) ").lower()
    if repeat == "y":
        main()
    else:
        print("Exiting...")
        exit()

if __name__ == '__main__':
    main()