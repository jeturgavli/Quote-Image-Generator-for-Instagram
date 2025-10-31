import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import colorama
from colorama import Fore
import random
import textwrap  # Feature from PR 2
import argparse


colorama.init(autoreset=True)

# Configuration constants
OUTPUT_DIR = Path('Quotes_Output')
BACKGROUNDS_DIR = Path('Backgrounds')
FONTS_DIR = Path('Fonts')  # Feature from PR 1
OVERLAY_PATH = Path('Program Stuff/Img-2.png')

FONT_SIZE = 40
TEXT_POSITION = (120, 750)
LINE_HEIGHT = 50
MAX_LINES = 5
BACKGROUND_RANGE = range(1, 11)
TEXT_WRAP_WIDTH = 30  # Feature from PR 2

COLOR_MAP = {
    'white': (255, 255, 255),
    'black': (0, 0, 0)
}

def parse_args():
    parser = argparse.ArgumentParser(description="Quote Image Generator CLI")

    parser.add_argument("--quote", type=str, help="Quote text to render on the image")
    parser.add_argument("--bg", type=str, help="Background number (01-10) or 'random'")
    parser.add_argument("--color", type=str, choices=["white", "black", "random"], help="Text color")
    parser.add_argument("--font", type=str, help="Font index (1, 2, 3...) or 'random'")
    parser.add_argument("--output", type=str, help="Output filename (without extension)")

    return parser.parse_args()


def get_user_choice(prompt, valid_options, case_sensitive=False):
    """Generic function to get validated user input."""
    while True:
        choice = input(prompt).strip()
        if not case_sensitive:
            choice = choice.lower()
        
        if choice in valid_options:
            return choice
        
        print(f"{Fore.RED}Invalid choice. Please try again.")


def get_text_color():
    """Get text color from user."""
    color = get_user_choice(
        "Enter text color (white/black): ",
        COLOR_MAP.keys()
    )
    return COLOR_MAP[color]


def choose_background():
    """Let user choose a background image."""
    valid_choices = [f'{i:02d}' for i in BACKGROUND_RANGE]
    
    choice = get_user_choice(
        "Choose Background (01-10 or random): ",
        valid_choices + ['random']
    )
    
    if choice == 'random':
        choice = random.choice(valid_choices)
    
    bg_path = BACKGROUNDS_DIR / f'{choice}.jpg'
    
    try:
        return Image.open(bg_path)
    except FileNotFoundError:
        print(f"{Fore.RED}Background file not found: {bg_path}")
        print("Please ensure the file exists and try again.")
        return choose_background()


# This is the function from your conflicting PR 1
def choose_font():
    """Scan Fonts directory and let user choose a font."""
    print(f"\n{Fore.CYAN}Available Fonts:")
    try:
        font_files = list(FONTS_DIR.glob('*.ttf')) + list(FONTS_DIR.glob('*.otf'))
        if not font_files:
            print(f"{Fore.RED}No font files (.ttf, .otf) found in {FONTS_DIR}/")
            print(f"{Fore.YELLOW}Using default PIL font.")
            return "default" 

        font_names = [f.name for f in font_files]
        for i, name in enumerate(font_names):
            print(f"  {i+1}: {name}")
        
        valid_choices = [str(i+1) for i in range(len(font_names))] + ['random']
        
        choice = get_user_choice(
            f"Choose Font (1-{len(font_names)} or random): ",
            valid_choices
        )

        if choice == 'random':
            chosen_font_path = random.choice(font_files)
        else:
            chosen_font_path = font_files[int(choice) - 1]
            
        print(f"{Fore.GREEN}Selected font: {chosen_font_path.name}")
        return str(chosen_font_path)

    except FileNotFoundError:
        print(f"{Fore.RED}Fonts directory not found: {FONTS_DIR}")
        print(f"{Fore.YELLOW}Using default PIL font.")
        return "default"


# This is the function from your accepted PR 2
def get_quote_text():
    """Get a single block of quote text from the user."""
    print(f"\n{Fore.CYAN}Enter your quote. The text will be wrapped automatically.")
    print(f"{Fore.CYAN}(Press Enter twice to finish typing):")
    
    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)
    
    return " ".join(lines)


# This function combines both features
def create_quote_image(background, quote_text, text_color, font_path):
    """Create the quote image by compositing background, overlay, and text."""
    # Load font (from PR 1)
    try:
        if font_path == "default":
             font = ImageFont.load_default()
        else:
            font = ImageFont.truetype(font_path, FONT_SIZE)
    except OSError:
        print(f"{Fore.YELLOW}Font not found at {font_path}. Using default font.")
        font = ImageFont.load_default()
    
    # Create drawing context
    draw = ImageDraw.Draw(background)
    
    # Apply overlay
    try:
        overlay = Image.open(OVERLAY_PATH)
        background.paste(overlay, overlay)
    except FileNotFoundError:
        print(f"{Fore.YELLOW}Overlay image not found. Continuing without overlay.")
    
    # Text wrapping logic (from PR 2)
    wrapped_lines = textwrap.wrap(quote_text, width=TEXT_WRAP_WIDTH)
    
    # Add text lines
    x, y_start = TEXT_POSITION
    for i, line in enumerate(wrapped_lines):
        if i >= MAX_LINES: 
            break
        y = y_start + LINE_HEIGHT * i
        draw.text((x, y), line, fill=text_color, font=font)
    
    return background


def save_image(image, filename):
    """Save the image to the output directory."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / f'{filename}.jpg'
    
    try:
        image.save(output_path)
        print(f"{Fore.GREEN}Image saved successfully: {output_path}")
    except Exception as e:
        print(f"{Fore.RED}Error saving image: {e}")


# This main function combines both features
def main():
    # Display program header
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}Quote Image Generator")
    print(f"{Fore.CYAN}{'='*50}\n")

    # Parse command-line arguments
    args = parse_args()

    # Choose background
    if args.bg:
        if args.bg.lower() == "random":
            bg_choice = random.choice([f'{i:02d}' for i in BACKGROUND_RANGE])
        else:
            bg_choice = args.bg
        background = Image.open(BACKGROUNDS_DIR / f"{bg_choice}.jpg")
    else:
        background = choose_background()

    # Choose font
    if args.font:
        font_files = list(FONTS_DIR.glob("*.ttf")) + list(FONTS_DIR.glob("*.otf"))
        if args.font.lower() == "random":
            font_path = str(random.choice(font_files))
        else:
            index = int(args.font) - 1
            font_path = str(font_files[index])
    else:
        font_path = choose_font()

    # Get quote text
    if args.quote:
        quote_text = args.quote
    else:
        quote_text = get_quote_text()

    # Choose text color
    if args.color:
        if args.color == "random":
            text_color = random.choice(list(COLOR_MAP.values()))
        else:
            text_color = COLOR_MAP[args.color]
    else:
        text_color = get_text_color()

    # Create the final image
    final_image = create_quote_image(background, quote_text, text_color, font_path)

    # Save the image
    filename = args.output or input("\nEnter image name (without extension): ").strip()
    if filename:
        save_image(final_image, filename)
    else:
        print(f"{Fore.YELLOW}No filename provided. Image not saved.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Program interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n{Fore.RED}An unexpected error occurred: {e}")
