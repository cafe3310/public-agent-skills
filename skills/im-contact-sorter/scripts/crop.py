import os
import sys
import subprocess

def crop_images(work_dir, subdir_name, left, top, width, height):
    # 使用绝对路径
    base_input_dir = os.path.join(work_dir, "01-raw")
    base_output_dir = os.path.join(work_dir, "02-cropped")
    
    input_path = os.path.join(base_input_dir, subdir_name)
    output_path = os.path.join(base_output_dir, subdir_name)
    geometry = f"{width}x{height}+{left}+{top}"
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"创建输出目录: {output_path}")

    if not os.path.exists(input_path):
        print(f"错误: 输入目录不存在: {input_path}")
        return

    files = [f for f in os.listdir(input_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not files:
        print(f"在 {input_path} 中未找到图片文件。")
        return

    print(f"开始裁剪 {subdir_name} 中的 {len(files)} 张图片...")
    for filename in files:
        src_file = os.path.join(input_path, filename)
        dst_file = os.path.join(output_path, filename)
        cmd = ["magick", src_file, "-crop", geometry, dst_file]
        try:
            subprocess.run(cmd, check=True)
        except Exception as e:
            print(f"处理失败 {filename}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("用法: python crop.py <工作目录> <子目录名> <左> <上> <宽> <高>")
        sys.exit(1)
    crop_images(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
