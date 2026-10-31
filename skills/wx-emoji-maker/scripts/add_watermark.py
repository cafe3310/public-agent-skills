#!/usr/bin/env python3
import os
import argparse
from PIL import Image, ImageDraw, ImageFont, ImageChops

# Define system fonts on macOS
_USER_FONTS = os.path.expanduser('~/Library/Fonts')
FONTS = {
    'rounded-thin': os.path.join(_USER_FONTS, 'M_PLUS_Rounded_1c/MPLUSRounded1c-Thin.ttf'),
    'rounded-light': os.path.join(_USER_FONTS, 'M_PLUS_Rounded_1c/MPLUSRounded1c-Light.ttf'),
    'rounded': os.path.join(_USER_FONTS, 'M_PLUS_Rounded_1c/MPLUSRounded1c-Regular.ttf'),
    'rounded-medium': os.path.join(_USER_FONTS, 'M_PLUS_Rounded_1c/MPLUSRounded1c-Medium.ttf'),
    'rounded-bold': os.path.join(_USER_FONTS, 'M_PLUS_Rounded_1c/MPLUSRounded1c-Bold.ttf'),
    'rounded-extrabold': os.path.join(_USER_FONTS, 'M_PLUS_Rounded_1c/MPLUSRounded1c-ExtraBold.ttf'),
    'rounded-black': os.path.join(_USER_FONTS, 'M_PLUS_Rounded_1c/MPLUSRounded1c-Black.ttf'),
    'handwritten': '/System/Library/Fonts/Noteworthy.ttc',
    'serif': '/System/Library/Fonts/Supplemental/Georgia Italic.ttf',
    'sans': '/System/Library/Fonts/Helvetica.ttc',
    'comic': '/System/Library/Fonts/Supplemental/Comic Sans MS.ttf'
}

# 默认参数已根据冰箱贴的最终微调效果进行了更新：
# - font_type: 默认使用圆体字 M_PLUS_Rounded_1c Medium ('rounded-medium')
# - opacity: 0.60 (60% 透明度)
# - size: 119px (在 108px 基础上调整至 110%，适合 4096px 大图)
# - position: southeast (右下角)
# - offset_x: 150px (在 100px 基础上调整至 150%)
# - offset_y: 100px (距离底部边缘的距离)
# - color: (123, 107, 100) (对应十六进制 7b6b64 的深棕色)
# - letter_spacing: 0.85 (字符间距因子，0.85 能将间隙缩小约 50%，使排版更紧凑)
# - round_ratio: 0.03 (圆角正方形裁切比例，默认 0.03 即 3% 的圆角)
def add_watermark(image_path, text, output_path, style='standard', font_type='rounded-medium', 
                  opacity=0.60, size=119, position='southeast', offset_x=150, offset_y=100,
                  color=(123, 107, 100), letter_spacing=0.85, round_ratio=0.03):
    """
    Adds a custom watermark to an image and crops it to a rounded square.
    
    style: 'standard' (translucent text) or 'sticker' (white stroke border + solid text)
    """
    img = Image.open(image_path)
    # Convert to RGBA to support transparency
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
        
    width, height = img.size
    
    # Create overlay for watermark
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Load font
    font_path = FONTS.get(font_type, font_type)
    if not os.path.exists(font_path):
        # Fallback to default if path not found
        font = ImageFont.load_default()
        print(f"Warning: Font {font_path} not found. Using default font.")
    else:
        # Load from ttc/ttf. Since Noteworthy is TTC, Pillow handles it
        try:
            font = ImageFont.truetype(font_path, size)
        except Exception as e:
            print(f"Error loading font {font_path}: {e}. Falling back to default.")
            font = ImageFont.load_default()

    # Calculate text dimensions using letter_spacing by summing character advance widths
    text_width = 0
    char_widths = []
    for i, char in enumerate(text):
        w = font.getlength(char)
        char_widths.append(w)
        if i < len(text) - 1:
            text_width += w * letter_spacing
        else:
            text_width += w
            
    bbox = draw.textbbox((0, 0), text, font=font)
    text_height = bbox[3] - bbox[1]
    
    # Calculate position coordinates
    if position == 'southeast':
        x = width - text_width - offset_x
        y = height - text_height - offset_y
    elif position == 'southwest':
        x = offset_x
        y = height - text_height - offset_y
    elif position == 'south':
        x = (width - text_width) // 2
        y = height - text_height - offset_y
    elif position == 'northeast':
        x = width - text_width - offset_x
        y = offset_y
    elif position == 'northwest':
        x = offset_x
        y = offset_y
    else:
        # Custom coordinates parsed as "x,y"
        try:
            x, y = map(int, position.split(','))
        except:
            x = width - text_width - offset_x
            y = height - text_height - offset_y

    # Calculate exact drawing coordinates for each character
    draw_positions = []
    cur_x = x
    for i, char in enumerate(text):
        draw_positions.append((cur_x, y))
        cur_x += char_widths[i] * letter_spacing
            
    # Apply watermark style and draw character-by-character
    if style == 'sticker':
        stroke_width = 16
        stroke_color = (255, 255, 255, 255) # Opaque white
        text_color = color + (255,) # Opaque brown
        
        # Draw outlines first so overlapping characters align properly
        for i, char in enumerate(text):
            draw.text(draw_positions[i], char, font=font, fill=text_color, 
                      stroke_width=stroke_width, stroke_fill=stroke_color)
        # Draw fills on top
        for i, char in enumerate(text):
            draw.text(draw_positions[i], char, font=font, fill=text_color)
    else:
        # Standard translucent watermark
        alpha = int(opacity * 255)
        text_color = color + (alpha,)
        
        for i, char in enumerate(text):
            draw.text(draw_positions[i], char, font=font, fill=text_color)
        
    # Composite overlay onto original image
    watermarked = Image.alpha_composite(img, overlay)
    
    # 应用圆角裁剪 (生成小圆角正方形，圆角外部透明)
    if round_ratio > 0:
        radius = int(width * round_ratio)
        mask = Image.new('L', img.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=255)
        
        # 将原始 Alpha 通道与圆角遮罩进行乘积合并 (取交集，保护原本有透明度的地方)
        r, g, b, a = watermarked.split()
        new_alpha = ImageChops.multiply(a, mask)
        watermarked = Image.merge('RGBA', (r, g, b, new_alpha))
        
    # Save image
    watermarked.save(output_path, 'PNG')
    print(f"Watermarked image saved to {output_path}")

def generate_thumbnail(image_path, output_path, size=(512, 512)):
    img = Image.open(image_path)
    img.thumbnail(size)
    img.save(output_path, 'PNG')

def main():
    parser = argparse.ArgumentParser(description="Add watermarks to cafe3310 sticker images.")
    parser.add_argument("--input", "-i", help="Path to input PNG image or directory of PNGs", default=".")
    parser.add_argument("--output-dir", "-o", help="Directory to save output files", default="watermarked_final")
    # 以下默认参数已更新为冰箱贴制作的最佳效果：
    parser.add_argument("--text", "-t", help="水印内容", default="© 2026 cafe3310")
    parser.add_argument("--style", "-s", choices=["standard", "sticker"], default="standard", 
                        help="水印风格: standard (常规半透明) 或 sticker (带白边的贴纸风)")
    parser.add_argument("--font", "-f", choices=list(FONTS.keys()), default="rounded-medium", 
                        help="字体类型 (rounded-medium=M_PLUS_Rounded_1c Medium, handwritten=Noteworthy)")
    parser.add_argument("--opacity", "-p", type=float, default=0.60, help="水印不透明度 (0.0 到 1.0)")
    parser.add_argument("--size", type=int, default=119, help="字号大小 (基于 4096px 图像)")
    parser.add_argument("--pos", choices=["southeast", "southwest", "south", "northeast", "northwest"], default="southeast", 
                        help="水印位置 (东南/右下, 西南/左下, 正南/底部居中, 东北/右上, 西北/左上)")
    parser.add_argument("--offset-x", type=int, default=150, help="水印距离左右边缘的距离 (像素)")
    parser.add_argument("--offset-y", type=int, default=100, help="水印距离上下边缘的距离 (像素)")
    parser.add_argument("--color", default="7b6b64", help="水印文字的十六进制颜色 (默认 7b6b64 深棕色)")
    parser.add_argument("--letter-spacing", type=float, default=0.85, help="字间距因子 (默认 0.85，可将空隙缩小约 50%%)")
    parser.add_argument("--round-ratio", type=float, default=0.03, help="圆角比例因子 (默认 0.03 即 3%% 的圆角正方形，0 为不裁切圆角)")
    parser.add_argument("--thumb", action="store_true", help="Generate a companion thumbnail in 'watermarked/thumbs'")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    if args.thumb:
        os.makedirs(os.path.join(args.output_dir, "thumbs"), exist_ok=True)
        
    # Determine input files
    if os.path.isdir(args.input):
        files = [os.path.join(args.input, f) for f in os.listdir(args.input) if f.lower().endswith('.png') and not f.startswith('.')]
    else:
        files = [args.input]
        
    for file_path in files:
        # Skip files already in output directory or thumbnails we created
        if "watermarked" in file_path or "_thumb.png" in file_path or "test" in file_path:
            continue
            
        base_name = os.path.basename(file_path)
        out_path = os.path.join(args.output_dir, base_name)
        
        # Parse color
        hex_color = args.color.lstrip('#')
        try:
            rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except Exception:
            rgb_color = (123, 107, 100) # Fallback to default
        
        print(f"Processing {base_name}...")
        add_watermark(
            image_path=file_path,
            text=args.text,
            output_path=out_path,
            style=args.style,
            font_type=args.font,
            opacity=args.opacity,
            size=args.size,
            position=args.pos,
            offset_x=args.offset_x,
            offset_y=args.offset_y,
            color=rgb_color,
            letter_spacing=args.letter_spacing,
            round_ratio=args.round_ratio
        )
        
        if args.thumb:
            thumb_path = os.path.join(args.output_dir, "thumbs", base_name.replace(".png", "_thumb.png"))
            generate_thumbnail(out_path, thumb_path)
            print(f"Generated thumbnail at {thumb_path}")

if __name__ == "__main__":
    main()
