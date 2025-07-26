#!/usr/bin/env python3
"""
Favicon Generator for Logivest
Generates favicon files with "LI" text and AI-inspired background
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def create_favicon(size=32):
    """Create a favicon with given size"""
    if not PIL_AVAILABLE:
        print("PIL not available, creating simple fallback")
        return None
    
    # Create image with RGBA mode for transparency
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create gradient-like background using multiple rectangles
    colors = [
        (102, 126, 234),  # #667eea
        (118, 75, 162),   # #764ba2  
        (240, 147, 251),  # #f093fb
    ]
    
    # Draw gradient background
    for i in range(size):
        ratio = i / size
        if ratio < 0.5:
            # Interpolate between first two colors
            t = ratio * 2
            r = int(colors[0][0] * (1-t) + colors[1][0] * t)
            g = int(colors[0][1] * (1-t) + colors[1][1] * t)
            b = int(colors[0][2] * (1-t) + colors[1][2] * t)
        else:
            # Interpolate between last two colors
            t = (ratio - 0.5) * 2
            r = int(colors[1][0] * (1-t) + colors[2][0] * t)
            g = int(colors[1][1] * (1-t) + colors[2][1] * t)
            b = int(colors[1][2] * (1-t) + colors[2][2] * t)
        
        draw.rectangle([0, i, size, i+1], fill=(r, g, b, 255))
    
    # Add rounded corners by drawing a mask
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    radius = max(2, size // 8)
    mask_draw.rounded_rectangle([0, 0, size-1, size-1], radius=radius, fill=255)
    
    # Apply mask to create rounded corners
    img.putalpha(mask)
    
    # Add "LI" text
    try:
        # Try to use a system font
        font_size = max(8, size // 2)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
    
    # Get text size and position
    text = "LI"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 1
    
    # Draw text with shadow effect
    draw.text((x+1, y+1), text, font=font, fill=(0, 0, 0, 128))  # Shadow
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))  # Main text
    
    # Add small accent dot
    accent_size = max(1, size // 16)
    accent_x = int(size * 0.8)
    accent_y = int(size * 0.2)
    draw.ellipse([accent_x-accent_size, accent_y-accent_size, 
                  accent_x+accent_size, accent_y+accent_size], 
                 fill=(255, 193, 7, 255))
    
    return img

def generate_all_favicons():
    """Generate all required favicon sizes"""
    if not PIL_AVAILABLE:
        print("Creating simple text-based favicons...")
        # Create simple SVG-based fallback
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea"/>
      <stop offset="50%" style="stop-color:#764ba2"/>
      <stop offset="100%" style="stop-color:#f093fb"/>
    </linearGradient>
  </defs>
  <rect width="32" height="32" rx="4" fill="url(#g)"/>
  <text x="16" y="20" text-anchor="middle" font-family="Arial" font-size="12" font-weight="bold" fill="white">LI</text>
  <circle cx="25" cy="7" r="2" fill="#ffc107"/>
</svg>'''
        
        with open('/Users/rakeshkumarmallam/logivest/web_interface/static/favicon.svg', 'w') as f:
            f.write(svg_content)
        
        return
    
    # Generate different sizes
    sizes = [16, 32, 180]
    
    for size in sizes:
        img = create_favicon(size)
        if img:
            if size == 180:
                filename = f'/Users/rakeshkumarmallam/logivest/web_interface/static/apple-touch-icon.png'
            else:
                filename = f'/Users/rakeshkumarmallam/logivest/web_interface/static/favicon-{size}x{size}.png'
            
            img.save(filename, 'PNG')
            print(f"Created {filename}")
    
    # Create ICO file from 16x16 and 32x32
    try:
        img16 = create_favicon(16)
        img32 = create_favicon(32)
        
        ico_path = '/Users/rakeshkumarmallam/logivest/web_interface/static/favicon.ico'
        img32.save(ico_path, format='ICO', sizes=[(16, 16), (32, 32)])
        print(f"Created {ico_path}")
    except Exception as e:
        print(f"Could not create ICO file: {e}")

if __name__ == "__main__":
    generate_all_favicons()
