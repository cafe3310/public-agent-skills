#!/bin/bash

# ==========================================
# Hugging Face 数据查询脚本 (原生 Bash + Python 版)
# 移除对 jq 的依赖，改用 Python 处理 JSON
# ==========================================

# 终端颜色配置
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# 1. 检查基础依赖
if ! command -v curl &> /dev/null; then
    echo -e "${RED}❌ 错误: 缺少依赖 'curl'，请先安装。${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 错误: 缺少依赖 'python3'。${NC}"
    exit 1
fi

# 2. 检查输入参数
if [ "$#" -lt 2 ]; then
    echo -e "${CYAN}用法: $0 <repo_type> <repo_id> [dataset_name]${NC}"
    echo -e "  模型示例: $0 model google-bert/bert-base-uncased"
    echo -e "  数据集示例: $0 dataset clin-re/medical_reports"
    echo -e "  Space示例: $0 space multimodalart/flux-tarot"
    echo -e "  组织示例 (按下载量排序): $0 org inclusionAI"
    echo -e "  组织示例 (按发布时间排序): $0 org_new inclusionAI"
    exit 1
fi

REPO_TYPE=$(echo "$1" | tr '[:upper:]' '[:lower:]')
REPO_ID=$2
REPO_TYPE_UPPER=$(echo "$REPO_TYPE" | tr '[:lower:]' '[:upper:]')

# 3. 构建 API 请求
if [ "$REPO_TYPE" = "model" ]; then
    URL="https://huggingface.co/api/models/${REPO_ID}?expand%5B%5D=downloads&expand%5B%5D=downloadsAllTime"
elif [ "$REPO_TYPE" = "dataset" ]; then
    URL="https://huggingface.co/api/datasets/${REPO_ID}?expand%5B%5D=downloads&expand%5B%5D=downloadsAllTime"
elif [ "$REPO_TYPE" = "space" ]; then
    URL="https://huggingface.co/api/spaces/${REPO_ID}"
elif [ "$REPO_TYPE" = "org" ] || [ "$REPO_TYPE" = "org_new" ]; then
    URL="https://huggingface.co/api/models?author=${REPO_ID}&limit=200&expand%5B%5D=createdAt&expand%5B%5D=downloads&expand%5B%5D=likes"
else
    echo -e "${RED}❌ 错误: 不支持的 repo_type '${REPO_TYPE}'。仅支持 'model'、'dataset'、'space'、'org' 或 'org_new'。${NC}"
    exit 1
fi

echo -e "${CYAN}🔍 正在查询 ${REPO_TYPE_UPPER}: ${REPO_ID} ...${NC}"
echo "------------------------------------------------"

# 4. 发送请求
TEMP_FILE=$(mktemp)
curl -m 15 -s "$URL" > "$TEMP_FILE"

# 5. 错误处理与解析 (使用 Python 处理 JSON)
# 定义一个通用的 Python 处理函数
python_parse() {
    python3 -c "
import sys, json

def fmt(n):
    try: return '{:,}'.format(int(n))
    except: return str(n)

try:
    with open('$TEMP_FILE', 'r') as f:
        data = json.load(f)
except Exception as e:
    print('ERROR: 解析数据失败')
    sys.exit(1)

if isinstance(data, dict) and 'error' in data:
    print(f'ERROR: {data.get(\"error\", \"未知错误\")}')
    sys.exit(0)

repo_type = '$REPO_TYPE'
repo_id = '$REPO_ID'

if repo_type in ['model', 'dataset']:
    name = data.get('id', '未知')
    author = name.split('/')[0] if '/' in name else '未知'
    created = data.get('createdAt', '未知')
    d30 = data.get('downloads', 0)
    dall = data.get('downloadsAllTime', 0)
    likes = data.get('likes', 0)
    
    icon = '📦' if repo_type == 'model' else '📊'
    print(f'{icon} ID:       \033[0;32m{name}\033[0m')
    print(f'👤 作者:     \033[0;32m{author}\033[0m')
    print(f'📅 创建时间:  \033[0;32m{created}\033[0m')
    print(f'⬇️  最近30天下载: \033[0;32m{fmt(d30)}\033[0m')
    print(f'📈 历史总下载量: \033[0;32m{fmt(dall)}\033[0m')
    print(f'❤️  点赞数:    \033[0;32m{fmt(likes)}\033[0m')

elif repo_type == 'space':
    name = data.get('id', '未知')
    likes = data.get('likes', 0)
    rt = data.get('runtime', {})
    status = rt.get('stage', '未知')
    hw = rt.get('hardware', '未知')
    sdk = data.get('sdk', '未知')
    
    print(f'🚀 Space ID: \033[0;32m{name}\033[0m')
    print(f'⚙️  运行状态: \033[0;32m{status}\033[0m')
    print(f'💻 硬件规格: \033[0;32m{hw}\033[0m')
    print(f'🛠  SDK类型:  \033[0;32m{sdk}\033[0m')
    print(f'❤️  点赞数:   \033[0;32m{fmt(likes)}\033[0m')
    print('\n\033[1;33m注: Hugging Face 官方 API 不提供 Space 访问量，流量热度可参考点赞数。\033[0m')

elif repo_type in ['org', 'org_new']:
    if not isinstance(data, list):
        print('ERROR: 返回数据格式不正确')
        sys.exit(0)
    
    count = len(data)
    total_d = sum(item.get('downloads', 0) for item in data)
    total_l = sum(item.get('likes', 0) for item in data)
    
    print(f'🏢 组织名称: \033[0;32m{repo_id}\033[0m')
    print(f'📊 模型总数:  \033[0;32m{fmt(count)}\033[0m')
    print(f'⬇️  最近30天总下载: \033[0;32m{fmt(total_d)}\033[0m')
    print(f'❤️  总点赞数:  \033[0;32m{fmt(total_l)}\033[0m')
    
    if repo_type == 'org_new':
        print('\n\033[0;36m🆕 最新发布列表 (Top 20 By Creation Time):\033[0m')
        # 按创建时间排序
        items = sorted(data, key=lambda x: x.get('createdAt', ''), reverse=True)[:20]
        for item in items:
            created = (item.get('createdAt') or '未知')[:10]
            print(f'  • {item.get(\"id\")}: {created} 发布, {fmt(item.get(\"downloads\", 0))} 下载')
    else:
        print('\n\033[0;36m📋 热门模型列表 (Top 20 By Downloads):\033[0m')
        # 按下载量排序
        items = sorted(data, key=lambda x: x.get('downloads', 0), reverse=True)[:20]
        for item in items:
            print(f'  • {item.get(\"id\")}: {fmt(item.get(\"downloads\", 0))} 下载, {fmt(item.get(\"likes\", 0))} 点赞')
    
    if count > 20:
        print(f'\033[1;33m  ... 还有 {count - 20} 个模型未显示\033[0m')
"
}

# 执行解析
RESULT=$(python_parse)

# 检查是否有错误
if [[ "$RESULT" == ERROR:* ]]; then
    echo -e "${RED}❌ ${RESULT}${NC}"
else
    echo -e "$RESULT"
fi

echo "------------------------------------------------"
rm -f "$TEMP_FILE"
