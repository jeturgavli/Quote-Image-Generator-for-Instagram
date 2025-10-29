import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import colorama
from colorama import Fore
import random

colorama.init(autoreset=True)

# Configuration constants
OUTPUT_DIR = Path('Quotes_Output')
BACKGROUNDS_DIR = Path('Backgrounds')
FONT_PATH = Path('Fonts/arial.ttf')
OVERLAY_PATH = Path('Program Stuff/Img-2.png')

FONT_SIZE = 40
TEXT_POSITION = (120, 750)
LINE_HEIGHT = 50
MAX_LINES = 5
BACKGROUND_RANGE = range(1, 11)

COLOR_MAP = {
    'white': (255, 255, 255),
    'black': (0, 0, 0)
}


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


def get_text_lines(num_lines=MAX_LINES):
    """Get text lines from user."""
    print(f"\n{Fore.CYAN}Enter your text (up to {num_lines} lines):")
    lines = []
    for i in range(num_lines):
        line = input(f"Line {i+1}: ").strip()
        lines.append(line)
    return lines


def create_quote_image(background, text_lines, text_color, font_path=FONT_PATH):
    """Create the quote image by compositing background, overlay, and text."""
    # Load font
    try:
        font = ImageFont.truetype(str(font_path), FONT_SIZE)
    except OSError:
        print(f"{Fore.YELLOW}Font not found. Using default font.")
        font = ImageFont.load_default()
    
    # Create drawing context
    draw = ImageDraw.Draw(background)
    
    # Apply overlay if it exists
    try:
        overlay = Image.open(OVERLAY_PATH)
        background.paste(overlay, overlay)
    except FileNotFoundError:
        print(f"{Fore.YELLOW}Overlay image not found. Continuing without overlay.")
    
    # Add text lines
    x, y_start = TEXT_POSITION
    for i, line in enumerate(text_lines):
        if line:  # Only draw non-empty lines
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


def main():
    """Main function to run the quote generator."""
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}Quote Image Generator")
    print(f"{Fore.CYAN}{'='*50}\n")
    
    # Get user inputs
    background = choose_background()
    text_lines = get_text_lines()
    text_color = get_text_color()
    
    # Create the image
    final_image = create_quote_image(background, text_lines, text_color)
    
    # Preview
    print(f"\n{Fore.CYAN}Opening preview...")
    final_image.show()
    
    # Save
    filename = input("\nEnter image name (without extension): ").strip()
    if filename:
        save_image(final_image, filename)
    else:
        print(f"{Fore.YELLOW}No filename provided. Image not saved.")
    
    # Ask to repeat
    if get_user_choice("\nCreate another image? (y/n): ", ['y', 'n']) == 'y':
        print("\n")
        main()
    else:
        print(f"\n{Fore.GREEN}Thank you for using Quote Image Generator!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Program interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n{Fore.RED}An unexpected error occurred: {e}")