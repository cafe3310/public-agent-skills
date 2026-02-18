# scripts/main.py
import os
import subprocess
import sys

# Assume these tools are available in the Gemini environment
# Placeholder for actual tool calls, will be replaced with direct Python logic or subprocess calls as needed.
def _read_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None

def _write_file(file_path, content):
    with open(file_path, 'w') as f:
        f.write(content)

def _run_shell_command(command, description):
    print(f"Executing: {description} (Command: {command})")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print(f"Stdout:\n{result.stdout}")
        if result.stderr:
            print(f"Stderr:\n{result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Stdout:\n{e.stdout}")
        print(f"Stderr:\n{e.stderr}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def get_modelscope_url():
    env_file_path = os.path.join(os.getcwd(), '.env')
    modelscope_url = None

    if os.path.exists(env_file_path):
        content = _read_file(env_file_path)
        if content:
            for line in content.splitlines():
                if line.startswith("MODEL_SCOPE_URL="):
                    modelscope_url = line.split("=", 1)[1].strip()
                    break

    if not modelscope_url:
        modelscope_url = input("请输入 ModelScope 仓库的 URL (例如: http://oauth2:...@www.modelscope.cn/studios/...): ")
        if not modelscope_url:
            print("ModelScope URL 不能为空。")
            sys.exit(1)

        # Update .env file
        env_content = ""
        if os.path.exists(env_file_path):
            env_content = _read_file(env_file_path)

        new_env_content_lines = []
        url_found_in_env = False
        if env_content:
            for line in env_content.splitlines():
                if line.startswith("MODEL_SCOPE_URL="):
                    new_env_content_lines.append(f"MODEL_SCOPE_URL={modelscope_url}")
                    url_found_in_env = True
                else:
                    new_env_content_lines.append(line)
        
        if not url_found_in_env:
            new_env_content_lines.append(f"MODEL_SCOPE_URL={modelscope_url}")
        
        _write_file(env_file_path, "\n".join(new_env_content_lines))
        print(f"ModelScope URL 已保存到 {env_file_path}")

    return modelscope_url


def get_deploy_directory():
    env_file_path = os.path.join(os.getcwd(), '.env')
    deploy_dir = None

    if os.path.exists(env_file_path):
        content = _read_file(env_file_path)
        if content:
            for line in content.splitlines():
                if line.startswith("MODEL_SCOPE_DEPLOY_DIR="):
                    deploy_dir = line.split("=", 1)[1].strip()
                    break

    if not deploy_dir:
        user_input_dir = input("请输入要部署的本地目录路径 (例如: gradio_app): ")
        if not user_input_dir:
            print("要部署的目录路径不能为空。")
            sys.exit(1)
        
        if not os.path.isdir(user_input_dir):
            print(f"错误: 源目录 '{user_input_dir}' 不存在或不是一个目录。")
            sys.exit(1)
        
        deploy_dir = user_input_dir

        # Update .env file
        env_content = ""
        if os.path.exists(env_file_path):
            env_content = _read_file(env_file_path)

        new_env_content_lines = []
        dir_found_in_env = False
        if env_content:
            for line in env_content.splitlines():
                if line.startswith("MODEL_SCOPE_DEPLOY_DIR="):
                    new_env_content_lines.append(f"MODEL_SCOPE_DEPLOY_DIR={deploy_dir}")
                    dir_found_in_env = True
                else:
                    new_env_content_lines.append(line)
        
        if not dir_found_in_env:
            new_env_content_lines.append(f"MODEL_SCOPE_DEPLOY_DIR={deploy_dir}")
        
        _write_file(env_file_path, "\n".join(new_env_content_lines))
        print(f"部署目录已保存到 {env_file_path}")

    return deploy_dir

def ensure_gitignore_entry():
    gitignore_path = os.path.join(os.getcwd(), '.gitignore')
    if not os.path.exists(gitignore_path):
        _write_file(gitignore_path, ".env\n")
        print(".gitignore 文件已创建，并添加了 .env")
        return

    content = _read_file(gitignore_path)
    
    # Check for .env
    if ".env" not in content.splitlines():
        content += "\n.env"
        print(".env 已添加到 .gitignore")
    else:
        print(".env 已存在于 .gitignore 中")

    # Write back the potentially modified content
    _write_file(gitignore_path, content.strip() + "\n")

def main():
    modelscope_url = get_modelscope_url()
    deploy_dir = get_deploy_directory()
    ensure_gitignore_entry()

    # Call the deploy.py script
    deploy_script_path = os.path.join(os.path.dirname(__file__), 'deploy.py')
    command = f"python3 {deploy_script_path} \"{modelscope_url}\" \"{deploy_dir}\""
    
    if _run_shell_command(command, "执行部署脚本"):
        print("部署流程已成功启动。请检查控制台输出以获取详细信息。")
    else:
        print("部署流程启动失败。")

if __name__ == "__main__":
    main()

