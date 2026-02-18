import os
import argparse
import sys
import yaml
import re
from pathlib import Path
from datetime import datetime

def setup_logger():
    import logging
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    return logging.getLogger("InitValidate")

logger = setup_logger()

# 必需的目录结构
REQUIRED_DIRS = [
    "kb/tasks",
    "kb/backups",
    "kb/00-chats-input-raw/attachments",
    "kb/00-chats-input-raw/processed",
    "kb/01-chats-input-organized",
    "kb/02-project-specs",
    "kb/03-missing-periods",
    "kb/04-output-documents"
]

def check_structure(root_path):
    """检测目录结构"""
    logger.info(">>> 1. 正在检查目录结构...")
    root = Path(root_path)
    if not root.exists():
        logger.warning(f"根目录 {root} 不存在，正在创建...")
        root.mkdir(parents=True, exist_ok=True)

    missing_count = 0
    for d in REQUIRED_DIRS:
        target_dir = root / d
        if not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"  [创建] 目录: {target_dir}")
            missing_count += 1
        else:
            # logger.debug(f"  [存在] 目录: {target_dir}")
            pass

    if missing_count == 0:
        logger.info("  [OK] 所有基础目录结构完整。")
    else:
        logger.info(f"  [修复] 自动创建了 {missing_count} 个缺失目录。")

def validate_specs(root_path):
    """检测 02 中的 YAML 项目定义"""
    logger.info(">>> 2. 正在校验项目定义 (02-project-specs)...")
    spec_dir = Path(root_path) / "kb/02-project-specs"

    if not spec_dir.exists():
        return

    valid_count = 0
    invalid_count = 0

    for yaml_file in spec_dir.glob("*.yaml"):
        # 跳过示例文件
        if "sample" in yaml_file.name.lower():
            continue

        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            errors = []

            # 检查 Meta
            if 'meta' not in data or 'id' not in data['meta']:
                errors.append("缺失 'meta.id'")

            # 检查 Scope
            if 'scope' not in data:
                errors.append("缺失 'scope'")
            else:
                scope = data['scope']
                if 'time_range' not in scope or 'start' not in scope['time_range'] or 'end' not in scope['time_range']:
                    errors.append("Scope 中缺失有效的 'time_range' (start/end)")

                if 'sources' not in scope or not isinstance(scope['sources'], list):
                    errors.append("Scope 中缺失 'sources' 列表")
                else:
                    # 检查 Sources Schema
                    for i, src in enumerate(scope['sources']):
                        if isinstance(src, dict):
                            if 'name' not in src:
                                errors.append(f"Source[{i}] 缺失 'name' 字段")
                        elif isinstance(src, str):
                            # 允许简写字符串，但建议警告
                            pass
                        else:
                            errors.append(f"Source[{i}] 格式错误")

            if errors:
                logger.error(f"  [失败] {yaml_file.name}: {'; '.join(errors)}")
                invalid_count += 1
            else:
                logger.info(f"  [通过] {yaml_file.name}")
                valid_count += 1

        except Exception as e:
            logger.error(f"  [错误] 无法解析 {yaml_file.name}: {e}")
            invalid_count += 1

    logger.info(f"  校验完成: {valid_count} 个有效, {invalid_count} 个无效。")

def validate_raw_inputs(root_path):
    """检测 00 中的时间戳格式"""
    logger.info(">>> 3. 正在抽检原始输入 (00-chats-input-raw)...")
    raw_dir = Path(root_path) / "kb/00-chats-input-raw"

    md_files = list(raw_dir.glob("*.md"))
    if not md_files:
        logger.info("  [提示] 00 目录为空，暂无新数据。")
        return

    warn_count = 0
    for md_file in md_files:
        has_anchor = False
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                # 只检查前 100 行
                for _ in range(100):
                    line = f.readline()
                    if not line: break
                    # 匹配 -- YYYY-MM-DD 或 -- MM-DD
                    if re.match(r'^--\s+\d{2,4}-\d{1,2}', line.strip()):
                        has_anchor = True
                        break
        except Exception:
            pass

        if not has_anchor:
            logger.warning(f"  [警告] {md_file.name}: 前100行未检测到时间锚点 (格式: '-- 2023-01-01')。这可能导致清洗失败。")
            warn_count += 1

    if warn_count == 0:
        logger.info(f"  [OK] 所有 {len(md_files)} 个原始文件均包含有效时间标记。")

def report_status(root_path):
    """汇总 03, Tasks, Backups 的状态"""
    root = Path(root_path)

    # 4. 检测 03-missing-periods
    logger.info(">>> 4. 检测数据完整性报告 (03)...")
    gap_dir = root / "kb/03-missing-periods"
    gap_reports = list(gap_dir.glob("**/*.yaml"))
    if gap_reports:
        logger.info(f"  发现 {len(gap_reports)} 份完整性报告:")
        # 取最近修改的 3 个
        gap_reports.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        for r in gap_reports[:3]:
            logger.info(f"    - {r.parent.name}/{r.name} (修改于: {datetime.fromtimestamp(r.stat().st_mtime).strftime('%Y-%m-%d %H:%M')})")
    else:
        logger.info("  暂无缺失报告。")

    # 5. 检测 Tasks
    logger.info(">>> 5. 检测后台任务 (tasks)...")
    task_dir = root / "kb/tasks"
    tasks = list(task_dir.glob("*.yaml")) + list(task_dir.glob("*.json"))
    if tasks:
        logger.info(f"  发现 {len(tasks)} 个任务记录:")
        tasks.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        for t in tasks[:3]:
             logger.info(f"    - {t.name} (修改于: {datetime.fromtimestamp(t.stat().st_mtime).strftime('%Y-%m-%d %H:%M')})")
    else:
        logger.info("  当前无活跃或挂起的任务。")

    # 6. 检测 Backups
    logger.info(">>> 6. 检测备份状态 (backups)...")
    backup_dir = root / "kb/backups"
    backups = list(backup_dir.glob("*.zip"))
    if backups:
        logger.info(f"  发现 {len(backups)} 个备份包:")
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        latest = backups[0]
        size_mb = latest.stat().st_size / (1024 * 1024)
        logger.info(f"    [最新] {latest.name} ({size_mb:.2f} MB)")
    else:
        logger.warning("  [警告] 未发现任何备份文件！建议立即运行 backup_full.py。")

def main():
    parser = argparse.ArgumentParser(description="im-local-kb 初始化与校验工具")
    parser.add_argument("--root", default=".", help="工作区根目录 (默认为当前目录)")
    args = parser.parse_args()

    print("="*60)
    print("im-local-kb - 环境自检程序")
    print("="*60)

    check_structure(args.root)
    validate_specs(args.root)
    validate_raw_inputs(args.root)
    report_status(args.root)

    print("-" * 60)
    logger.info("自检完成。")

if __name__ == "__main__":
    main()
