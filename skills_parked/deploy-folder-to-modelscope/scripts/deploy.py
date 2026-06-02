# scripts/deploy.py
import subprocess
import os
import shutil
import sys

def run_command(command, cwd=None):
    try:
        result = subprocess.run(command, check=True, shell=True, capture_output=True, text=True, cwd=cwd)
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e.cmd}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def deploy_to_modelscope(modelscope_url, source_folder):
    temp_dir = None
    try:
        # 1. 创建临时目录
        print("创建临时目录...")
        temp_dir = subprocess.check_output("mktemp -d", shell=True, text=True).strip()
        print(f"临时目录: {temp_dir}")

        # 2. 克隆 ModelScope 仓库
        print(f"克隆 ModelScope 仓库到 {temp_dir}...")
        if not run_command(f"git clone {modelscope_url} {temp_dir}"):
            return False

        # 3. 清空临时目录中除 .git 以外的所有内容
        print(f"清空临时目录 {temp_dir} 中除 .git 以外的所有内容...")
        if not run_command(f"find {temp_dir} -maxdepth 1 -mindepth 1 -not -name '.git' -exec rm -rf {{}} +"):
            return False

        # 4. 复制源目录的内容到临时目录
        print(f"复制 {source_folder} 的内容到 {temp_dir}...")
        # `dirs_exist_ok=True` 允许我们将内容复制到已存在的目录中
        shutil.copytree(source_folder, temp_dir, dirs_exist_ok=True)

        # 5. 在临时目录中执行 git add, commit, push
        print(f"在 {temp_dir} 中执行 Git 操作...")
        if not run_command("git add .", cwd=temp_dir):
            return False
        if not run_command("git commit -m 'update from deploy-folder-to-modelscope skill'", cwd=temp_dir):
            # If nothing to commit, it's not an error for this flow
            print("Nothing to commit, continuing...")
        else:
            if not run_command("git push", cwd=temp_dir):
                return False

        print("部署成功！")
        return True

    finally:
        # 6. 清理临时目录
        if temp_dir and os.path.exists(temp_dir):
            print(f"清理临时目录 {temp_dir}...")
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python deploy.py <modelscope_url> <source_folder>")
        sys.exit(1)

    modelscope_url = sys.argv[1]
    source_folder = sys.argv[2]

    if not os.path.isdir(source_folder):
        print(f"错误: 源目录 '{source_folder}' 不存在或不是一个目录。")
        sys.exit(1)

    if deploy_to_modelscope(modelscope_url, source_folder):
        print("任务完成。")
    else:
        print("部署失败。")
        sys.exit(1)
