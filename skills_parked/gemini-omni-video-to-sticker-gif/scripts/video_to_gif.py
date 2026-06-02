#!/usr/bin/env python3
import sys
import os
import argparse
import subprocess
import re

# Simple font dictionary for coordinates
font = {
    '0': [[1,1,1],[1,0,1],[1,0,1],[1,0,1],[1,1,1]],
    '1': [[0,1,0],[0,1,0],[0,1,0],[0,1,0],[0,1,0]],
    '2': [[1,1,1],[0,0,1],[1,1,1],[1,0,0],[1,1,1]],
    '3': [[1,1,1],[0,0,1],[1,1,1],[0,0,1],[1,1,1]],
    '4': [[1,0,1],[1,0,1],[1,1,1],[0,0,1],[0,0,1]],
    '5': [[1,1,1],[1,0,0],[1,1,1],[0,0,1],[1,1,1]],
    '6': [[1,1,1],[1,0,0],[1,1,1],[1,0,1],[1,1,1]],
    '7': [[1,1,1],[0,0,1],[0,0,1],[0,0,1],[0,0,1]],
    '8': [[1,1,1],[1,0,1],[1,1,1],[1,0,1],[1,1,1]],
    '9': [[1,1,1],[1,0,1],[1,1,1],[0,0,1],[1,1,1]]
}

def draw_char(pixels, width, height, char, start_x, start_y, scale=2, color=(255,255,255), bg_color=(0,0,0)):
    if char not in font:
        return
    bmp = font[char]
    char_w = len(bmp[0])
    char_h = len(bmp)
    for dy in range(-2, char_h * scale + 2):
        for dx in range(-2, char_w * scale + 2):
            px = start_x + dx
            py = start_y + dy
            if 0 <= px < width and 0 <= py < height:
                idx = (py * width + px) * 3
                pixels[idx] = bg_color[0]
                pixels[idx+1] = bg_color[1]
                pixels[idx+2] = bg_color[2]
    for cy in range(char_h):
        for cx in range(char_w):
            if bmp[cy][cx]:
                for dy in range(scale):
                    for dx in range(scale):
                        px = start_x + cx * scale + dx
                        py = start_y + cy * scale + dy
                        if 0 <= px < width and 0 <= py < height:
                            idx = (py * width + px) * 3
                            pixels[idx] = color[0]
                            pixels[idx+1] = color[1]
                            pixels[idx+2] = color[2]

def draw_string(pixels, width, height, s, start_x, start_y, scale=2, color=(255,255,255), bg_color=(0,0,0)):
    curr_x = start_x
    for char in s:
        draw_char(pixels, width, height, char, curr_x, start_y, scale, color, bg_color)
        curr_x += len(font.get(char, [[0]])[0]) * scale + scale

def draw_grid_ppm(in_ppm, out_ppm):
    with open(in_ppm, 'rb') as f:
        header = f.readline()
        line = f.readline()
        while line.startswith(b'#'):
            line = f.readline()
        parts = line.split()
        while len(parts) < 2:
            parts += f.readline().split()
        w = int(parts[0])
        h = int(parts[1])
        line = f.readline()
        while line.startswith(b'#'):
            line = f.readline()
        maxval = int(line.strip())
        pixels = bytearray(f.read())

    # Vertical lines
    for x in range(0, w, 50):
        is_major = (x % 100 == 0)
        color = (255, 0, 0) if is_major else (255, 255, 0)
        for y in range(h):
            if not is_major and (y % 10 < 5):
                continue
            idx = (y * w + x) * 3
            if idx + 2 < len(pixels):
                pixels[idx] = color[0]
                pixels[idx+1] = color[1]
                pixels[idx+2] = color[2]

    # Horizontal lines
    for y in range(0, h, 50):
        is_major = (y % 100 == 0)
        color = (255, 0, 0) if is_major else (255, 255, 0)
        for x in range(w):
            if not is_major and (x % 10 < 5):
                continue
            idx = (y * w + x) * 3
            if idx + 2 < len(pixels):
                pixels[idx] = color[0]
                pixels[idx+1] = color[1]
                pixels[idx+2] = color[2]

    scale = 2
    for x in range(100, w, 100):
        draw_string(pixels, w, h, str(x), x + 4, 10, scale)
        draw_string(pixels, w, h, str(x), x + 4, h - 25, scale)
    for y in range(100, h, 100):
        draw_string(pixels, w, h, str(y), 10, y + 4, scale)
        draw_string(pixels, w, h, str(y), w - 50, y + 4, scale)

    with open(out_ppm, 'wb') as f:
        f.write(b"P6\n")
        f.write(f"{w} {h}\n".encode())
        f.write(f"{maxval}\n".encode())
        f.write(pixels)

def parse_crop(crop_str):
    if not crop_str:
        return None
    numbers = re.findall(r'\d+', crop_str)
    if len(numbers) == 4:
        # Check for explicit wh / xy prefixes
        clean_str = re.sub(r'\s+', '', crop_str.lower())
        w_match = re.search(r'wh(\d+)[x:](\d+)', clean_str)
        x_match = re.search(r'xy(\d+)[x:](\d+)', clean_str)
        if w_match and x_match:
            return f"{w_match.group(1)}:{w_match.group(2)}:{x_match.group(1)}:{x_match.group(2)}"
        
        # Check if user wrote width/height or x/y first
        # Format: if it contains ":" (e.g. 700:700:292:10)
        if ':' in crop_str:
            return ":".join(numbers)
        
        # If it's comma/space separated, e.g. "x,y,w,h" vs "w,h,x,y"
        # Usually, x,y,w,h is like 292,10,700,700 where coords are smaller than sizes
        n = [int(x) for x in numbers]
        if n[2] >= n[0] and n[3] >= n[1]: # x, y, w, h -> convert to w:h:x:y
            return f"{n[2]}:{n[3]}:{n[0]}:{n[1]}"
        else: # w, h, x, y
            return f"{n[0]}:{n[1]}:{n[2]}:{n[3]}"
            
    return crop_str

def make_grid_preview(video_path, ss, output_path):
    temp_raw_png = output_path + ".raw.png"
    temp_ppm = output_path + ".raw.ppm"
    temp_out_ppm = output_path + ".out.ppm"
    try:
        # Extract frame
        subprocess.run(["ffmpeg", "-ss", str(ss), "-i", video_path, "-vframes", "1", temp_raw_png, "-y"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Convert to PPM
        subprocess.run(["ffmpeg", "-i", temp_raw_png, temp_ppm, "-y"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Draw grid
        draw_grid_ppm(temp_ppm, temp_out_ppm)
        # Convert back to PNG
        subprocess.run(["ffmpeg", "-i", temp_out_ppm, output_path, "-y"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Successfully generated grid preview: {output_path}")
    finally:
        for f in [temp_raw_png, temp_ppm, temp_out_ppm]:
            if os.path.exists(f):
                os.remove(f)

def make_gif(video_path, output_path, ss, duration, crop, scale, speed, freeze):
    filters = []
    parsed_crop = parse_crop(crop)
    if parsed_crop:
        filters.append(f"crop={parsed_crop}")
    if scale:
        filters.append(f"scale={scale}")
    if speed != 1.0:
        filters.append(f"setpts=PTS/{speed}")
    if freeze > 0:
        filters.append(f"tpad=stop_mode=clone:stop_duration={freeze}")
        
    filter_complex = ",".join(filters)
    if filter_complex:
        filter_complex += ","
    filter_complex += "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
    
    cmd = ["ffmpeg"]
    if ss:
        cmd += ["-ss", str(ss)]
    if duration:
        cmd += ["-t", str(duration)]
    cmd += ["-i", video_path, "-filter_complex", filter_complex, output_path, "-y"]
    
    print(f"Running ffmpeg command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print(f"Successfully generated GIF: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Convert video to dynamic sticker GIF or generate coordinate grid preview.")
    parser.add_argument("video_path", help="Path to input video file")
    parser.add_argument("-o", "--output", required=True, help="Path to output file")
    parser.add_argument("--ss", type=float, default=0.0, help="Start time in seconds")
    parser.add_argument("-t", "--duration", type=float, help="Duration in seconds")
    parser.add_argument("--to", type=float, help="End time in seconds")
    parser.add_argument("--crop", help="Crop specification (e.g., 'w:h:x:y' or 'x,y,w,h')")
    parser.add_argument("--scale", default="600:600", help="Output scale (default: 600:600)")
    parser.add_argument("--speed", type=float, default=1.0, help="Speed multiplier (default: 1.0)")
    parser.add_argument("--freeze", type=float, default=0.0, help="Freeze frame duration at end in seconds")
    parser.add_argument("--grid", action="store_true", help="Generate grid preview instead of GIF")
    
    args = parser.parse_args()
    
    # Calculate duration if --to is provided
    duration = args.duration
    if args.to is not None:
        duration = args.to - args.ss
        
    if args.grid:
        make_grid_preview(args.video_path, args.ss, args.output)
    else:
        make_gif(args.video_path, args.output, args.ss, duration, args.crop, args.scale, args.speed, args.freeze)

if __name__ == "__main__":
    main()
