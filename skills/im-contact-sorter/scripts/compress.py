import os
import sys
import subprocess

def compress_images(work_dir, subdir_name):
    base_dir = os.path.join(work_dir, "02-cropped")
    target_dir = os.path.join(base_dir, subdir_name)
    
    if not os.path.exists(target_dir):
        print(f"错误: 未找到目录 {target_dir}")
        return

    files = [f for f in os.listdir(target_dir) if f.lower().endswith('.png')]
    print(f"开始原地压缩 {subdir_name} 中的 {len(files)} 张图片...")

    for filename in files:
        file_path = os.path.join(target_dir, filename)
        cmd = ["pngquant", "--force", "--ext", ".png", "--speed", "1", "--quality", "8", file_path]
        try:
            subprocess.run(cmd, check=True)
        except Exception as e:
            print(f"压缩失败 {filename}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python compress.py <工作目录> <子目录名>")
        sys.exit(1)
    compress_images(sys.argv[1], sys.argv[2])
