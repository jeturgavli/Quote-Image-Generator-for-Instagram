import os
import random
import textwrap
from enum import Enum, auto
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional, Union

from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps, ImageFilter, ImageChops
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

# Enums for better type safety
class BackgroundType(Enum):
    SOLID = 'solid'
    GRADIENT = 'gradient'
    IMAGE = 'image'
    PATTERN = 'pattern'

class TextAlign(Enum):
    LEFT = 'left'
    CENTER = 'center'
    RIGHT = 'right'
    JUSTIFY = 'justify'

# Configuration
class Config:
    # Directory settings
    OUTPUT_DIR = Path('Quotes_Output')
    BACKGROUNDS_DIR = Path('Backgrounds')
    FONTS_DIR = Path('Fonts')
    PATTERNS_DIR = Path('Patterns')
    OVERLAY_PATH = Path('Program Stuff/Img-2.png')
    
    # Font settings
    FONT_PATHS = {
        'Arial': 'arial.ttf',
        'Roboto': 'Roboto-Regular.ttf',
        'Montserrat': 'Montserrat-Regular.ttf',
    }
    
    # Layout settings
    MIN_FONT_SIZE = 16
    MAX_FONT_SIZE = 120
    DEFAULT_FONT_SIZE = 42
    TEXT_MARGIN = 60
    LINE_SPACING = 1.5
    MAX_LINES = 8
    
    # Colors (RGBA)
    COLOR_MAP = {
        'white': (255, 255, 255, 255),
        'black': (0, 0, 0, 255),
        'gold': (255, 215, 0, 255),
        'silver': (192, 192, 192, 255),
        'overlay': (0, 0, 0, 180),  # Semi-transparent black overlay
    }
    
    # Gradients (start_color, end_color)
    GRADIENTS = {
        'sunset': [(255, 100, 100), (255, 200, 150)],
        'ocean': [(0, 100, 200), (0, 200, 255)],
        'forest': [(0, 80, 40), (150, 200, 100)],
    }
    
    # Default background settings
    DEFAULT_BG_COLOR = (53, 73, 94)  # Dark blue-gray
    DEFAULT_BG_GRADIENT = [(30, 40, 60), (10, 20, 30)]  # Dark gradient


def get_user_choice(prompt, valid_options, case_sensitive=False):
    """Generic function to get validated user input."""
    while True:
        choice = input(prompt).strip()
        if not case_sensitive:
            choice = choice.lower()
        
        if choice in valid_options:
            return choice
        
        print(f"{Fore.RED}Invalid choice. Please try again.")


def get_text_color() -> Tuple[int, int, int, int]:
    """Get text color from user with validation."""
    while True:
        print(f"\n{Fore.CYAN}Available text colors:")
        for i, color in enumerate(Config.COLOR_MAP.keys(), 1):
            print(f"{i}. {color.capitalize()}")
        
        color_choice = input(f"\n{Fore.CYAN}Choose text color (1-{len(Config.COLOR_MAP)}): ").strip()
        
        try:
            color_idx = int(color_choice) - 1
            if 0 <= color_idx < len(Config.COLOR_MAP):
                color_name = list(Config.COLOR_MAP.keys())[color_idx]
                return Config.COLOR_MAP[color_name]
            print(f"{Fore.RED}Please enter a number between 1 and {len(Config.COLOR_MAP)}")
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a number.")


def get_available_backgrounds() -> List[Path]:
    """Return a list of available background image paths."""
    Config.BACKGROUNDS_DIR.mkdir(exist_ok=True)
    
    # Get all image files from the backgrounds directory
    image_extensions = ('.jpg', '.jpeg', '.png', '.webp')
    backgrounds = [f for f in Config.BACKGROUNDS_DIR.iterdir() 
                  if f.suffix.lower() in image_extensions]
    
    return sorted(backgrounds, key=lambda x: x.name.lower())

def get_available_fonts() -> Dict[str, Path]:
    """Return a dictionary of available fonts with their paths."""
    available_fonts = {}
    
    # Check for default fonts
    for font_name, font_file in Config.FONT_PATHS.items():
        font_path = Config.FONTS_DIR / font_file
        if font_path.exists():
            available_fonts[font_name] = font_path
    
    # Add any additional fonts from the Fonts directory
    if Config.FONTS_DIR.exists():
        for ext in ['.ttf', '.otf']:
            for font_file in Config.FONTS_DIR.glob(f'*{ext}'):
                font_name = font_file.stem
                if font_name not in available_fonts:
                    available_fonts[font_name] = font_file
    
    # If no fonts found, use default system font as fallback
    if not available_fonts:
        try:
            default_font = ImageFont.load_default()
            available_fonts['System Default'] = None
        except:
            pass
    
    return available_fonts

def select_background() -> Dict[str, Any]:
    """Let user select a background type and return the selection."""
    print(f"\n{Fore.CYAN}Background Options:")
    print("1. Solid Color")
    print("2. Gradient")
    print("3. Image")
    print("4. Pattern")
    
    while True:
        choice = input(f"\n{Fore.CYAN}Choose background type (1-4): ").strip()
        
        if choice == '1':
            # Solid color background
            print(f"\n{Fore.CYAN}Available colors:")
            colors = list(Config.COLOR_MAP.keys())
            for i, color in enumerate(colors, 1):
                print(f"{i}. {color.capitalize()}")
            
            while True:
                color_choice = input(
                    f"\n{Fore.CYAN}Choose a color (1-{len(colors)}): "
                ).strip()
                
                try:
                    color_idx = int(color_choice) - 1
                    if 0 <= color_idx < len(colors):
                        color_name = colors[color_idx]
                        color = Config.COLOR_MAP[color_name]
                        return {
                            'type': BackgroundType.SOLID,
                            'color': color,
                            'name': f"Solid {color_name.capitalize()}"
                        }
                    print(f"{Fore.RED}Please enter a number between 1 and {len(colors)}")
                except ValueError:
                    print(f"{Fore.RED}Invalid input. Please enter a number.")
        
        elif choice == '2':
            # Gradient background
            print(f"\n{Fore.CYAN}Available gradients:")
            gradients = list(Config.GRADIENTS.items())
            for i, (name, _) in enumerate(gradients, 1):
                print(f"{i}. {name.capitalize()}")
            
            while True:
                grad_choice = input(
                    f"\n{Fore.CYAN}Choose a gradient (1-{len(gradients)}): "
                ).strip()
                
                try:
                    grad_idx = int(grad_choice) - 1
                    if 0 <= grad_idx < len(gradients):
                        name, colors = gradients[grad_idx]
                        return {
                            'type': BackgroundType.GRADIENT,
                            'colors': colors,
                            'name': f"{name.capitalize()} Gradient"
                        }
                    print(f"{Fore.RED}Please enter a number between 1 and {len(gradients)}")
                except ValueError:
                    print(f"{Fore.RED}Invalid input. Please enter a number.")
        
        elif choice == '3':
            # Image background
            backgrounds = get_available_backgrounds()
            
            if not backgrounds:
                print(f"{Fore.YELLOW}No background images found in the Backgrounds folder.")
                print(f"{Fore.YELLOW}Using a solid color background instead.")
                return {
                    'type': BackgroundType.SOLID,
                    'color': Config.DEFAULT_BG_COLOR,
                    'name': "Default Solid"
                }
            
            print(f"\n{Fore.CYAN}Available backgrounds:")
            for i, bg in enumerate(backgrounds, 1):
                print(f"{i:02d}. {bg.name}")
            
            while True:
                bg_choice = input(
                    f"\n{Fore.CYAN}Choose a background (01-{len(backgrounds):02d}), "
                    "'r' for random, or 'b' to go back: "
                ).strip().lower()
                
                if bg_choice == 'b':
                    break
                    
                if bg_choice == 'r':
                    bg_path = random.choice(backgrounds)
                    print(f"{Fore.CYAN}Selected random background: {bg_path.name}")
                    return {
                        'type': BackgroundType.IMAGE,
                        'path': bg_path,
                        'name': bg_path.stem,
                        'blur': 0
                    }
                
                try:
                    bg_num = int(bg_choice)
                    if 1 <= bg_num <= len(backgrounds):
                        bg_path = backgrounds[bg_num - 1]
                        print(f"{Fore.CYAN}Selected background: {bg_path.name}")
                        
                        # Ask for blur amount
                        blur = 0
                        blur_choice = input(
                            f"{Fore.CYAN}Add blur effect? (0-10, 0 for no blur): "
                        ).strip()
                        
                        try:
                            blur = min(10, max(0, int(blur_choice)))
                        except ValueError:
                            print(f"{Fore.YELLOW}Invalid blur amount. Using 0 (no blur).")
                        
                        return {
                            'type': BackgroundType.IMAGE,
                            'path': bg_path,
                            'name': bg_path.stem,
                            'blur': blur
                        }
                    print(f"{Fore.RED}Please enter a number between 01 and {len(backgrounds):02d}")
                except ValueError:
                    print(f"{Fore.RED}Invalid input. Please enter a number, 'r' for random, or 'b' to go back.")
        
        elif choice == '4':
            # Pattern background
            Config.PATTERNS_DIR.mkdir(exist_ok=True)
            patterns = [f for f in Config.PATTERNS_DIR.glob('*') 
                       if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp')]
            
            if not patterns:
                print(f"{Fore.YELLOW}No pattern images found in the Patterns folder.")
                print(f"{Fore.YELLOW}Using a solid color background instead.")
                return {
                    'type': BackgroundType.SOLID,
                    'color': Config.DEFAULT_BG_COLOR,
                    'name': "Default Solid"
                }
            
            print(f"\n{Fore.CYAN}Available patterns:")
            for i, pattern in enumerate(patterns, 1):
                print(f"{i:02d}. {pattern.name}")
            
            while True:
                pattern_choice = input(
                    f"\n{Fore.CYAN}Choose a pattern (01-{len(patterns):02d}), "
                    "'r' for random, or 'b' to go back: "
                ).strip().lower()
                
                if pattern_choice == 'b':
                    break
                    
                if pattern_choice == 'r':
                    pattern_path = random.choice(patterns)
                    print(f"{Fore.CYAN}Selected random pattern: {pattern_path.name}")
                    return {
                        'type': BackgroundType.PATTERN,
                        'path': pattern_path,
                        'name': f"Pattern: {pattern_path.stem}",
                        'opacity': 0.7
                    }
                
                try:
                    pattern_num = int(pattern_choice)
                    if 1 <= pattern_num <= len(patterns):
                        pattern_path = patterns[pattern_num - 1]
                        print(f"{Fore.CYAN}Selected pattern: {pattern_path.name}")
                        
                        # Ask for opacity
                        opacity = 0.7
                        opacity_choice = input(
                            f"{Fore.CYAN}Pattern opacity (0.1-1.0, default 0.7): "
                        ).strip()
                        
                        try:
                            opacity = min(1.0, max(0.1, float(opacity_choice or '0.7')))
                        except ValueError:
                            print(f"{Fore.YELLOW}Invalid opacity. Using 0.7.")
                        
                        return {
                            'type': BackgroundType.PATTERN,
                            'path': pattern_path,
                            'name': f"Pattern: {pattern_path.stem}",
                            'opacity': opacity
                        }
                    print(f"{Fore.RED}Please enter a number between 01 and {len(patterns):02d}")
                except ValueError:
                    print(f"{Fore.RED}Invalid input. Please enter a number, 'r' for random, or 'b' to go back.")
        
        else:
            print(f"{Fore.RED}Invalid choice. Please enter a number between 1 and 4.")


def get_text_lines() -> List[str]:
    """Get text lines from user with better handling of empty lines."""
    print(f"\n{Fore.CYAN}Enter your quote (up to {Config.MAX_LINES} lines, press Enter twice to finish):")
    lines = []
    
    for i in range(Config.MAX_LINES):
        line = input(f"Line {i+1}: ").strip()
        if not line and i > 0:  # Allow empty line to finish input
            break
        if line:  # Only add non-empty lines
            lines.append(line)
    
    # If first line is empty, add a default text
    if not lines:
        print(f"{Fore.YELLOW}No text provided. Using default text.")
        lines = ["Your text here"]
    
    return lines


def create_gradient(colors: List[Tuple[int, int, int]], size: Tuple[int, int]) -> Image.Image:
    """Create a gradient background from a list of colors."""
    width, height = size
    gradient = Image.new('RGBA', (width, height))
    draw = ImageDraw.Draw(gradient)
    
    if len(colors) == 1:
        return Image.new('RGBA', size, (*colors[0], 255))
    
    # Create vertical gradient
    for y in range(height):
        # Calculate the color at this y position
        ratio = y / (height - 1)
        color = []
        for i in range(3):  # RGB components
            start_color = colors[0][i] if len(colors) > 0 else 0
            end_color = colors[-1][i] if len(colors) > 1 else start_color
            color.append(int(start_color + (end_color - start_color) * ratio))
        color.append(255)  # Full alpha
        
        # Draw a horizontal line with the calculated color
        draw.line([(0, y), (width, y)], fill=tuple(color))
    
    return gradient

def create_tiled_pattern(pattern: Image.Image, size: Tuple[int, int], opacity: float = 1.0) -> Image.Image:
    """Create a tiled pattern from a small pattern image."""
    width, height = size
    pattern_width, pattern_height = pattern.size
    
    # Create a new image with the desired size
    result = Image.new('RGBA', (width, height))
    
    # Tile the pattern
    for y in range(0, height, pattern_height):
        for x in range(0, width, pattern_width):
            result.paste(pattern, (x, y), pattern if pattern.mode == 'RGBA' else None)
    
    # Apply opacity if needed
    if opacity < 1.0 and pattern.mode == 'RGBA':
        alpha = result.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        result.putalpha(alpha)
    
    return result

def apply_overlay(background: Image.Image) -> Image.Image:
    """Apply overlay image if it exists."""
    if not Config.OVERLAY_PATH.exists():
        return background
    
    try:
        overlay = Image.open(Config.OVERLAY_PATH).convert('RGBA')
        # Resize overlay to match background if needed
        if overlay.size != background.size:
            overlay = overlay.resize(background.size, Image.Resampling.LANCZOS)
        # Create a new image with the overlay applied
        return Image.alpha_composite(background, overlay)
    except Exception as e:
        print(f"{Fore.YELLOW}Warning: Could not apply overlay: {e}")
        return background

def prepare_background(background_config: Dict[str, Any], target_size: Tuple[int, int] = (1200, 1200)) -> Image.Image:
    """Prepare the background based on the configuration."""
    width, height = target_size
    
    # Create base background based on type
    if background_config['type'] == BackgroundType.SOLID:
        bg = Image.new('RGBA', (width, height), background_config['color'])
    elif background_config['type'] == BackgroundType.GRADIENT:
        bg = create_gradient(background_config['colors'], (width, height))
    elif background_config['type'] == BackgroundType.IMAGE:
        try:
            bg = Image.open(background_config['path']).convert('RGBA')
            # Resize while maintaining aspect ratio
            bg = ImageOps.fit(bg, (width, height), method=Image.Resampling.LANCZOS)
            # Apply blur if specified
            if background_config.get('blur', 0) > 0:
                bg = bg.filter(ImageFilter.GaussianBlur(background_config['blur']))
        except Exception as e:
            print(f"{Fore.YELLOW}Warning: Could not load background image: {e}")
            print(f"{Fore.YELLOW}Falling back to solid color background.")
            bg = Image.new('RGBA', (width, height), Config.DEFAULT_BG_COLOR)
    elif background_config['type'] == BackgroundType.PATTERN:
        try:
            pattern = Image.open(background_config['path']).convert('RGBA')
            bg = create_tiled_pattern(pattern, (width, height), background_config.get('opacity', 0.7))
        except Exception as e:
            print(f"{Fore.YELLOW}Warning: Could not load pattern: {e}")
            print(f"{Fore.YELLOW}Falling back to solid color background.")
            bg = Image.new('RGBA', (width, height), Config.DEFAULT_BG_COLOR)
    else:
        bg = Image.new('RGBA', (width, height), Config.DEFAULT_BG_COLOR)
    
    # Apply overlay if it exists
    bg = apply_overlay(bg)
    
    # Apply dark overlay for better text visibility (except for solid colors)
    if background_config['type'] != BackgroundType.SOLID:
        overlay = Image.new('RGBA', (width, height), Config.COLOR_MAP['overlay'])
        bg = Image.alpha_composite(bg, overlay)
    
    return bg

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    """Wrap text to fit within max_width using the specified font."""
    words = text.split()
    if not words:
        return []
        
    lines = []
    current_line = []
    
    for word in words:
        # Create a test line with the new word
        test_line = ' '.join(current_line + [word])
        test_bbox = font.getbbox(test_line)
        test_width = test_bbox[2] - test_bbox[0]
        
        if test_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def calculate_font_size(draw: ImageDraw.ImageDraw, text: str, max_width: int, max_height: int, 
                       min_size: int = Config.MIN_FONT_SIZE, 
                       max_size: int = Config.MAX_FONT_SIZE) -> Tuple[ImageFont.FreeTypeFont, List[str]]:
    """Calculate the optimal font size and wrapped text that fits the given dimensions."""
    # Try to load the font
    try:
        # Start with the default font size
        font_size = Config.DEFAULT_FONT_SIZE
        font = ImageFont.truetype(str(Config.FONTS_DIR / 'arial.ttf'), font_size)
    except (IOError, OSError):
        print(f"{Fore.YELLOW}Warning: Could not load the specified font. Using default font.")
        font = ImageFont.load_default()
        return font, [text]
    
    # Binary search for the largest font size that fits
    low, high = min_size, max_size
    best_font = font
    best_wrapped = [text]
    
    while low <= high:
        mid = (low + high) // 2
        try:
            test_font = ImageFont.truetype(str(Config.FONTS_DIR / 'arial.ttf'), mid)
        except (IOError, OSError):
            test_font = ImageFont.load_default()
        
        # Wrap the text with the current font size
        wrapped = []
        for line in text.split('\n'):
            wrapped.extend(wrap_text(line, test_font, max_width - (2 * Config.TEXT_MARGIN)))
        
        # Calculate total height needed
        line_heights = [test_font.getbbox(line)[3] - test_font.getbbox(line)[1] for line in wrapped]
        total_height = sum(line_heights) + (len(wrapped) - 1) * (Config.LINE_SPACING - 1) * line_heights[0] if line_heights else 0
        
        # Check if text fits
        if total_height <= max_height - (2 * Config.TEXT_MARGIN):
            best_font = test_font
            best_wrapped = wrapped
            low = mid + 1  # Try a larger font size
        else:
            high = mid - 1  # Try a smaller font size
    
    return best_font, best_wrapped

def create_quote_image(background_config: Dict[str, Any], text: str, 
                      text_color: Tuple[int, int, int, int]) -> Image.Image:
    """Create the final quote image with the given parameters."""
    # Prepare the background
    img = prepare_background(background_config)
    draw = ImageDraw.Draw(img)
    
    # Calculate available space for text
    width, height = img.size
    max_width = width - (2 * Config.TEXT_MARGIN)
    max_height = height - (2 * Config.TEXT_MARGIN)
    
    # Calculate font size and wrap text
    font, wrapped_lines = calculate_font_size(draw, text, max_width, max_height)
    
    # Calculate text position (centered)
    line_heights = [font.getbbox(line)[3] - font.getbbox(line)[1] for line in wrapped_lines]
    total_text_height = sum(line_heights) + (len(wrapped_lines) - 1) * (Config.LINE_SPACING - 1) * line_heights[0] if line_heights else 0
    
    y_position = (height - total_text_height) // 2
    
    # Draw each line of text with a subtle shadow for better readability
    shadow_color = (0, 0, 0, 100) if text_color == Config.COLOR_MAP['white'] else (255, 255, 255, 100)
    
    for i, line in enumerate(wrapped_lines):
        if not line.strip():
            continue
            
        # Get text size
        text_bbox = font.getbbox(line)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Calculate x position (centered)
        x_position = (width - text_width) // 2
        
        # Draw shadow (slightly offset)
        shadow_position = (x_position + 2, y_position + 2)
        draw.text(shadow_position, line, font=font, fill=shadow_color)
        
        # Draw main text
        draw.text((x_position, y_position), line, font=font, fill=text_color)
        
        # Move to next line position
        y_position += int(text_height * Config.LINE_SPACING)
    
    return img


def save_image(image: Image.Image, filename: str) -> bool:
    """Save the image to the specified path."""
    try:
        # Ensure the output directory exists
        Config.OUTPUT_DIR.mkdir(exist_ok=True)
        
        # Ensure the filename has a .jpg extension
        if not filename.lower().endswith(('.jpg', '.jpeg')):
            filename += '.jpg'
            
        output_path = Config.OUTPUT_DIR / filename
        
        # Convert to RGB if needed (JPEG doesn't support alpha channel)
        if image.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])  # Paste with alpha as mask
            image = background
        
        # Save with high quality
        image.save(output_path, 'JPEG', quality=95)
        print(f"{Fore.GREEN}Image saved successfully: {output_path}")
        return True
    except Exception as e:
        print(f"{Fore.RED}Error saving image: {e}")
        return False


def main():
    """Main function to run the quote generator."""
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}Enhanced Quote Image Generator")
    print(f"{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}Creates beautiful quote images with custom backgrounds\n")
    
    while True:
        try:
            # Get user inputs
            background_config = select_background()
            text_lines = get_text_lines()
            text = '\n'.join(line for line in text_lines if line.strip())
            
            if not text.strip():
                print(f"{Fore.YELLOW}No text provided. Please try again.")
                continue
            
            text_color = get_text_color()
            
            # Create the image
            final_image = create_quote_image(background_config, text, text_color)
            
            # Get output filename and save
            filename = input("\nEnter image name (without extension): ").strip()
            if filename:
                if save_image(final_image, filename):
                    # Try to open the image with the default viewer
                    try:
                        final_image.show()
                    except Exception as e:
                        print(f"{Fore.YELLOW}Note: Could not open the image viewer: {e}")
                        print(f"{Fore.CYAN}You can find the image at: {Config.OUTPUT_DIR / filename}")
            else:
                print(f"{Fore.YELLOW}No filename provided. Image not saved.")
            
            # Ask to create another image
            if get_user_choice("\nCreate another image? (y/n): ", ['y', 'n']) != 'y':
                print(f"\n{Fore.GREEN}Thank you for using the Quote Image Generator!")
                break
                
            print("\n" + "="*50 + "\n")
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Operation cancelled by user.")
            break
        except Exception as e:
            print(f"\n{Fore.RED}An error occurred: {e}")
            if get_user_choice("\nContinue? (y/n): ", ['y', 'n']) != 'y':
                break


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n{Fore.RED}A critical error occurred: {e}")
        print("Please report this issue if it persists.")
    finally:
        # Ensure colorama is properly reset
        print(colorama.Style.RESET_ALL, end='')