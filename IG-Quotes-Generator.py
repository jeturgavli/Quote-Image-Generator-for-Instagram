import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import colorama
from colorama import Fore
import random
import textwrap  # +++ ADDED: Import textwrap module

colorama.init(autoreset=True)

# Configuration constants
OUTPUT_DIR = Path('Quotes_Output')
BACKGROUNDS_DIR = Path('Backgrounds')
FONTS_DIR = Path('Fonts')
OVERLAY_PATH = Path('Program Stuff/Img-2.png')

FONT_SIZE = 40
TEXT_POSITION = (120, 750)
LINE_HEIGHT = 50
MAX_LINES = 5
BACKGROUND_RANGE = range(1, 11)
TEXT_WRAP_WIDTH = 30  # +++ ADDED: Set a character width for wrapping

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


# --- NOTE: This function is from PR 1. We keep it. ---
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


# --- CHANGED: Replaced get_text_lines with get_quote_text ---
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


# --- CHANGED: Now accepts quote_text and font_path, and performs wrapping ---
def create_quote_image(background, quote_text, text_color, font_path):
    """Create the quote image by compositing background, overlay, and text."""
    # Load font
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
    
    # Apply overlay if it exists
    try:
        overlay = Image.open(OVERLAY_PATH)
        background.paste(overlay, overlay)
    except FileNotFoundError:
        print(f"{Fore.YELLOW}Overlay image not found. Continuing without overlay.")
    
    # --- ADDED: Text wrapping logic ---
    # Wrap the text
    wrapped_lines = textwrap.wrap(quote_text, width=TEXT_WRAP_WIDTH)
    
    # Add text lines
    x, y_start = TEXT_POSITION
    for i, line in enumerate(wrapped_lines):
        if i >= MAX_LINES:  # Respect the maximum number of lines
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


def main():
    """Main function to run the quote generator."""
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}Quote Image Generator")
    print(f"{Fore.CYAN}{'='*50}\n")
    
    # Get user inputs
    background = choose_background()
    font_path = choose_font() 
    # --- CHANGED: Call get_quote_text instead of get_text_lines ---
    quote_text = get_quote_text()
    text_color = get_text_color()
    
    # Create the image
    # --- CHANGED: Pass quote_text ---
    final_image = create_quote_image(background, quote_text, text_color, font_path)
    
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