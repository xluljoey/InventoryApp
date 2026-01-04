"""
Generate app icon with blue-green gradient and MCF or chicken logo
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(icon_type='mcf', output_path='app.ico'):
    """Create a blue-green icon with either MCF text or chicken logo"""
    
    # Create image
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create gradient background (blue-green)
    for y in range(size):
        # Interpolate between cyan and teal
        ratio = y / size
        r = int(6 + (14 - 6) * ratio)
        g = int(182 + (116 - 182) * ratio)
        b = int(212 + (144 - 212) * ratio)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
    
    # Draw rounded rectangle mask
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(0, 0), (size, size)], radius=40, fill=255)
    
    # Apply mask
    output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    output.paste(img, (0, 0), mask)
    draw = ImageDraw.Draw(output)
    
    if icon_type == 'mcf':
        # Draw MCF text
        try:
            # Try to use a bold font (cross-platform)
            import platform
            if platform.system() == "Windows":
                font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 90)
            elif platform.system() == "Darwin":  # macOS
                font = ImageFont.truetype("/System/Library/Fonts/Arial Bold.ttf", 90)
            else:  # Linux and others
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", 90)
            except:
                font = ImageFont.load_default()
        
        text = "MCF"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size - text_width) / 2 - bbox[0]
        y = (size - text_height) / 2 - bbox[1]
        
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        
    else:  # chicken
        # Draw simplified chicken
        # Body (ellipse)
        draw.ellipse([78, 90, 178, 210], fill=(255, 255, 255, 255))
        
        # Head (circle)
        draw.ellipse([93, 55, 163, 125], fill=(255, 255, 255, 255))
        
        # Beak (triangle)
        draw.polygon([(145, 85), (170, 90), (145, 95)], fill=(251, 191, 36, 255))
        
        # Eye
        draw.ellipse([136, 81, 144, 89], fill=(31, 41, 55, 255))
        
        # Crest (crown)
        draw.polygon([
            (115, 65), (120, 55), (128, 60), (136, 55), (141, 65), (128, 70)
        ], fill=(239, 68, 68, 255))
        
        # Legs
        draw.line([(110, 210), (110, 230)], fill=(251, 191, 36, 255), width=6)
        draw.line([(146, 210), (146, 230)], fill=(251, 191, 36, 255), width=6)
        
        # Feet
        draw.line([(100, 230), (120, 230)], fill=(251, 191, 36, 255), width=4)
        draw.line([(136, 230), (156, 230)], fill=(251, 191, 36, 255), width=4)
    
    # Add subtle border
    border_mask = Image.new('L', (size, size), 0)
    border_draw = ImageDraw.Draw(border_mask)
    border_draw.rounded_rectangle([(2, 2), (size-2, size-2)], radius=38, outline=255, width=4)
    
    border_img = Image.new('RGBA', (size, size), (255, 255, 255, 76))
    final = Image.alpha_composite(output, Image.new('RGBA', (size, size), (0, 0, 0, 0)))
    
    # Save as ICO with multiple sizes
    icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    images = [output.resize(s, Image.Resampling.LANCZOS) for s in icon_sizes]
    
    images[0].save(output_path, format='ICO', sizes=icon_sizes)
    print(f"✅ Icon created: {output_path}")
    
    # Also save as PNG for preview
    output.save(output_path.replace('.ico', '.png'), format='PNG')
    print(f"✅ PNG preview created: {output_path.replace('.ico', '.png')}")

if __name__ == '__main__':
    import sys
    
    print("🎨 Icon Generator for Sales & Inventory Management System")
    print("=" * 50)
    
    icon_type = 'mcf'
    if len(sys.argv) > 1:
        icon_type = sys.argv[1].lower()
    
    print(f"Creating {icon_type.upper()} icon...")
    create_icon(icon_type=icon_type)
    print("\n✨ Done! Icon is ready for use.")