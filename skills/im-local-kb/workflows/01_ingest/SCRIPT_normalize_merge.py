import hashlib
import argparse
from SCRIPT_util import *
from typing import Callable, Any, List

def seq_match(list_s: List[Any], list_l: List[Any], item_getter: Callable[[Any], Any]) -> int:
    """
    在 list_l 中寻找 list_s 的连续匹配项，返回匹配的起始索引，如果没有找到返回 -1
    虽然 KMP 更好，但我们先无视
    long_l = [
        {'id': 10, 'name': 'A'},
        {'id': 20, 'name': 'B'},
        {'id': 30, 'name': 'C'},
        {'id': 40, 'name': 'D'},
        {'id': 50, 'name': 'E'}
    ]

    short_l_1 = [{'id': 30}, {'id': 40}]
    short_l_2 = [{'id': 20}, {'id': 99}]

    getter = lambda x: x['id']

    print(seq_match(short_l_1, long_l, getter))  # 输出: 2
    print(seq_match(short_l_2, long_l, getter))  # 输出: -1
    """
    n = len(list_s)
    m = len(list_l)

    if n == 0:
        return 0
    if n > m:
        return -1

    # 预先提取短列表的特征值，避免在双重循环中重复计算
    target_s = [item_getter(item) for item in list_s]

    for i in range(m - n + 1):
        match = True
        for j in range(n):
            # 逐个比对，一旦发现不匹配立即终止当前窗口的比对
            if item_getter(list_l[i + j]) != target_s[j]:
                match = False
                break

        if match:
            return i

    return -1

def seq_longest_common_prefix_length(list_s: List[Any], list_l: List[Any], item_getter: Callable[[Any], Any]) -> int:
    """
    寻找两个 list 的公共最长前缀长度，返回匹配的长度。
    如果没有，返回 0。
    例如：
    long_l = [
        {'id': 10, 'name': 'A'},
        {'id': 20, 'name': 'B'},
        {'id': 30, 'name': 'C'},
        {'id': 40, 'name': 'D'},
        {'id': 50, 'name': 'E'}
    ]

    short_l_1 = [{'id': 10}, {'id': 20}, {'id': 99}]
    short_l_2 = [{'id': 30}, {'id': 40}]
    short_l_3 = [{'id': 99}, {'id': 100}]

    getter = lambda x: x['id']
    
    print(seq_longest_prefix_match(short_l_1, long_l, getter))  # 输出: 2
    print(seq_longest_prefix_match(short_l_2, long_l, getter))  # 输出: 0
    print(seq_longest_prefix_match(short_l_3, long_l, getter))  # 输出: 0
    """
    i = 0
    j = 0
    max_match_length = 0

    while i < len(list_s) and j < len(list_l):
        if item_getter(list_s[i]) == item_getter(list_l[j]):
            max_match_length += 1
            i += 1
            j += 1
        else:
            break

    return max_match_length

def seq_longest_common_suffix_length(list_s: List[Any], list_l: List[Any], item_getter: Callable[[Any], Any]) -> int:
    """
    寻找两个 list 的公共最长后缀长度，返回匹配的长度。
    如果没有，返回 0。
    """
    i = len(list_s) - 1
    j = len(list_l) - 1
    max_match_length = 0

    while i >= 0 and j >= 0:
        if item_getter(list_s[i]) == item_getter(list_l[j]):
            max_match_length += 1
            i -= 1
            j -= 1
        else:
            break

    return max_match_length

class MatchPoint:
    """
    描述单一匹配点的详细信息。
    """
    def __init__(self):
        self.desc: str = "匹配点详情，包含是否找到匹配、在待合并块中的索引、在目标文件中的原始行号及内容预览。"
        self.found: bool = False
        self.match_index_in_new_block: int = -1  # 匹配窗口在 new_block 中的起始/结束索引
        self.line_no_in_target: int = -1         # 匹配行在目标文件中的物理行号
        self.content_preview: str = ""           # 匹配行的内容预览
        self.matching_max_line_count_in_target: int = -1    # 目标文件中，匹配窗口内的最大覆盖长度（物理行数）
        self.matching_max_line_count_in_new_block: int = -1 # 待合并块中，匹配窗口内的最大覆盖长度（物理行数）


class MergeResult:
    """
    包含 magic_merge 执行后的完整审计信息。
    """
    def __init__(self, target_file: str, chat_name: str, block_date: str):
        # 基础元数据
        self.meta = {
            "desc": "基础元数据，包含目标文件路径、聊天名称、块日期及任务执行时间。",
            "target_file": target_file,
            "chat_name": chat_name,
            "block_date": block_date,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        # 统计信息
        self.block_stats = {
            "desc": "待合并块的统计信息，包含总行数、有效哈希行数及被过滤的噪音行数。",
            "total_lines": 0,
            "hashable_lines": 0,
            "ignored_lines": 0
        }
        self.target_stats = {
            "desc": "目标文件的状态，包含是否存在及初始总行数。",
            "exists": False,
            "initial_total_lines": 0
        }
        # 匹配详情
        self.start_anchor = MatchPoint()
        self.end_anchor = MatchPoint()
        # 差异分析
        self.overlap_analysis = {
            "desc": "重叠区域分析，对比待合并块与目标文件在起始/结束锚点之间的哈希行数差异。",
            "new_block_hashes_between": 0,
            "target_file_hashes_between": 0,
            "diff_count": 0
        }
        # 执行结果
        self.action_taken = {
            "desc": "最终执行动作，包含合并策略、最终行数、净增行数及任务状态。",
            "strategy": "UNKNOWN",
            "final_total_lines": 0,
            "added_lines": 0,
            "status": "pending"
        }

    def to_dict(self):
        """
        转换为可序列化的字典，用于 YAML 输出。
        """
        from collections import OrderedDict
        return OrderedDict([
            ("01_meta", self.meta),
            ("02_target_stats", self.target_stats),
            ("03_block_stats", self.block_stats),
            ("04_match_details", {
                "start_anchor": vars(self.start_anchor),
                "end_anchor": vars(self.end_anchor)
            }),
            ("05_overlap_analysis", self.overlap_analysis),
            ("06_action_taken", self.action_taken)
        ])


def magic_merge(new_block: ChatBlock, target_filename: str) -> MergeResult:
    """
    使用 new_block 和 target_filename 定位的目标文件进行合并，返回 MergeResult

    这个方法会
    1. 处理 new_block 的每一行，留下 hash 部分和非 hash 部分(保留和 new_block 的映射关系)
    2. 处理目标文件的每一行，留下 hash 部分和非 hash 部分(保留和目标文件原始行的映射关系)
    3. 用 new_block 的前 N 行（仅 hash 行）去目标文件中匹配，找到最后一个完全匹配的行（match_start）
    4. 用 new_block 的后 N 行（仅 hash 行）去目标文件中匹配，找到第一个完全匹配的行（match_end）

    如果 match_start 和 match_end 都存在，且 match_start 行号 < match_end 行号，则认为 new_block 在目标文件中间找到匹配，可以进行拼接合并

        写出顺序：
        1. 目标文件中 match_start 行（映射回原始行号）之前的内容
        2. new_block 中 match_start 行（映射回原始行号）到 match_end 行（映射回原始行号）的内容
        3. 目标文件中 match_end 行（映射回原始行号）之后的内容

    如果只有 match_start 存在，认为 new_block 的前半部分在目标文件中找到匹配，可以进行拼接合并

        写出顺序：
        1. 目标文件中 match_start 行（映射回原始行号）之前的内容
        2. new_block 中 match_start 行（映射回原始行号）到结尾的内容

    如果只有 match_end 存在，认为 new_block 的后半部分在目标文件中找到匹配，可以进行拼接合并

        写出顺序：
        1. 目标文件的 yaml header 部分（如果有的话）
        1. new_block 中 从开始到 match_end 行（映射回原始行号）的内容
        2. 目标文件中 match_end 行（映射回原始行号）之后的内容

    如果都没找到，认为 new_block 没有在目标文件中找到匹配，直接按时间顺序插入到目标文件中合适的位置。

        构建一个 ChatOrgFile,
        然后添加 new_block，
        按照时间顺序排序，
        写出覆盖目标文件即可。

    """
    # 1. 初始化结果对象与参数
    RESULT = MergeResult(target_filename, new_block.chat_name, new_block.time_tag)
    opt_search_lines = 5  # 可配置：匹配时考虑的行数范围

    # 2. 构建 hash function
    def hash_line(s: str) -> str:
        return hashlib.sha256(s.encode('utf-8')).hexdigest()

    # 我们需要用一个数据结构表达 chat_block -> {hashable_line, hash, original_content_line_idx}[]
    RESULT.block_stats["total_lines"] = len(new_block.content)
    new_block_hash_list = []
    for idx, line in enumerate(new_block.content):
        hashing = RegexPatterns.extract_hashing_line(line)
        if hashing:
            new_block_hash_list.append({
                "hash": hash_line(hashing),
                "original_content_line_idx": idx,
                "content": line
            })
    RESULT.block_stats["hashable_lines"] = len(new_block_hash_list)
    RESULT.block_stats["ignored_lines"] = RESULT.block_stats["total_lines"] - RESULT.block_stats["hashable_lines"]

    # 我们用另一个数据结构表达 target_file -> {hashable_line, hash, original_content_line_idx}[]
    target_lines = []
    target_file_hash_list = []
    if os.path.exists(target_filename):
        RESULT.target_stats["exists"] = True
        with open(target_filename, 'r', encoding='utf-8') as f:
            target_lines = f.readlines()
        RESULT.target_stats["initial_total_lines"] = len(target_lines)
        for idx, line in enumerate(target_lines):
            hashing = RegexPatterns.extract_hashing_line(line)
            if hashing:
                target_file_hash_list.append({
                    "hash": hash_line(hashing),
                    "original_content_line_idx": idx,
                    "content": line
                })

    # 3. 用 new_block 的前 N 行（仅 hash 行）去目标文件中匹配
    begin_match = seq_match(new_block_hash_list[:opt_search_lines], target_file_hash_list, lambda x: x['hash'])
    # 如果 begin_match != -1，说明找到了匹配的起点行，我们记录这个行号（在目标文件中的行号）和内容
    if begin_match != -1:

        RESULT.start_anchor.found = True
        RESULT.start_anchor.match_index_in_new_block = new_block_hash_list[0]['original_content_line_idx']
        RESULT.start_anchor.line_no_in_target = target_file_hash_list[begin_match]['original_content_line_idx']
        RESULT.start_anchor.content_preview = target_file_hash_list[begin_match]['content'].strip()
        
        # 我们用 prefix match 的方式分析，new_block 从 match_start 行开始，能匹配的最长 hash 连续行数
        common_prefix_hashable_length = seq_longest_common_prefix_length(new_block_hash_list, target_file_hash_list[begin_match:], lambda x: x['hash'])
        
        # 转换回物理行数，记录在结果中
        if common_prefix_hashable_length > 0:
            last_matching_idx_in_target = target_file_hash_list[begin_match + common_prefix_hashable_length - 1]['original_content_line_idx']  # 需要找到 target_file_hash_list 中第 common_prefix_hashable_length 个匹配行的原始行号
            RESULT.start_anchor.matching_max_line_count_in_target = last_matching_idx_in_target - RESULT.start_anchor.line_no_in_target + 1
            
            last_matching_idx_in_new_block = new_block_hash_list[0 + common_prefix_hashable_length - 1]['original_content_line_idx']  # 需要找到 new_block_hash_list 中第 common_prefix_hashable_length 个匹配行的原始行号
            RESULT.start_anchor.matching_max_line_count_in_new_block = last_matching_idx_in_new_block - RESULT.start_anchor.match_index_in_new_block + 1
            
    # 4. 用 new_block 的后 N 行（仅 hash 行）去目标文件中匹配
    end_match = seq_match(new_block_hash_list[-opt_search_lines:], target_file_hash_list, lambda x: x['hash'])

    # 如果 end_match != -1，说明找到了匹配的结尾行，我们记录这个行号（在目标文件中的行号）和内容
    if end_match != -1:
        RESULT.end_anchor.found = True
        # 记录窗口中最后一个匹配行的信息
        last_match_idx_in_window = opt_search_lines - 1
        last_match_idx_in_target = end_match + last_match_idx_in_window
        
        # 我们用 suffix match 的方式分析，new_block 从 match_end 行开始往前，能匹配的最长 hash 连续行数
        common_suffix_hashable_length = seq_longest_common_suffix_length(new_block_hash_list, target_file_hash_list[:end_match + opt_search_lines], lambda x: x['hash'])
        
        # 转换回物理行数，记录在结果中
        if common_suffix_hashable_length > 0:
            first_matching_idx_in_target = target_file_hash_list[end_match + last_match_idx_in_window - common_suffix_hashable_length + 1]['original_content_line_idx']  # 需要找到 target_file_hash_list 中第 common_suffix_hashable_length 个匹配行的原始行号
            RESULT.end_anchor.matching_max_line_count_in_target = last_match_idx_in_target - first_matching_idx_in_target + 1
            
            first_matching_idx_in_new_block = new_block_hash_list[-opt_search_lines + last_match_idx_in_window - common_suffix_hashable_length + 1]['original_content_line_idx']  # 需要找到 new_block_hash_list 中第 common_suffix_hashable_length 个匹配行的原始行号
            RESULT.end_anchor.matching_max_line_count_in_new_block = new_block_hash_list[-1]['original_content_line_idx'] - first_matching_idx_in_new_block + 1

        RESULT.end_anchor.match_index_in_new_block = new_block_hash_list[-1]['original_content_line_idx']
        RESULT.end_anchor.line_no_in_target = target_file_hash_list[last_match_idx_in_target]['original_content_line_idx']
        RESULT.end_anchor.content_preview = target_file_hash_list[last_match_idx_in_target]['content'].strip()

    # 5. 根据匹配结果进行合并
    final_lines = []

    if RESULT.start_anchor.found and RESULT.end_anchor.found and RESULT.start_anchor.line_no_in_target <= RESULT.end_anchor.line_no_in_target:
        # 如果两边都存在匹配，且 match_start 行号 < match_end 行号，则认为 new_block 在目标文件中间找到匹配，可以进行拼接合并
        RESULT.action_taken["strategy"] = "both_match"
        
        # 写出顺序：
        # 1. 目标文件中 match_start 行（映射回原始行号）之前的内容
        final_lines.extend(target_lines[:RESULT.start_anchor.line_no_in_target])
        # 2. new_block 中 match_start 行（映射回原始行号）到 match_end 行（映射回原始行号）的内容
        final_lines.extend(new_block.content[RESULT.start_anchor.match_index_in_new_block:RESULT.end_anchor.match_index_in_new_block + 1])
        # 3. 目标文件中 match_end 行（映射回原始行号）之后的内容
        final_lines.extend(target_lines[RESULT.end_anchor.line_no_in_target + 1:])
        
    elif RESULT.start_anchor.found:
        # 如果只有 match_start 存在，认为 new_block 的前半部分在目标文件中找到匹配，可以进行拼接合并

        RESULT.action_taken["strategy"] = "begin_match"
  
        # 写出顺序：
        # 1. 目标文件中直到最末匹配行的内容（以保留目标文件中匹配部分的后续内容，避免丢失） -- line_no_in_target 和 matching_max_line_count_in_target
        final_lines.extend(target_lines[:RESULT.start_anchor.line_no_in_target + RESULT.start_anchor.matching_max_line_count_in_target])
        # 2. new_block 中最末匹配行（映射回原始行号）到结尾的内容
        final_lines.extend(new_block.content[RESULT.start_anchor.match_index_in_new_block + RESULT.start_anchor.matching_max_line_count_in_new_block:])
        # 3. 目标文件中最末匹配行之后的内容
        final_lines.extend(target_lines[RESULT.start_anchor.line_no_in_target + RESULT.start_anchor.matching_max_line_count_in_target:])
        
    elif RESULT.end_anchor.found:
        # 如果只有 match_end 存在，认为 new_block 的后半部分在目标文件中找到匹配，可以进行拼接合并
        RESULT.action_taken["strategy"] = "end_match"
        
        # 写出顺序：
        # 1. 目标文件直到最早匹配行的内容（以保留目标文件中匹配部分的前续内容，避免丢失） -- line_no_in_target 和 matching_max_line_count_in_target
        final_lines.extend(target_lines[:RESULT.end_anchor.line_no_in_target - RESULT.end_anchor.matching_max_line_count_in_target + 1])
        # 2. new_block 中 从开始到最早匹配行（映射回原始行号）的内容
        final_lines.extend(new_block.content[:RESULT.end_anchor.match_index_in_new_block - RESULT.end_anchor.matching_max_line_count_in_new_block + 1])
        # 3. 目标文件中最早匹配行之后的内容
        final_lines.extend(target_lines[RESULT.end_anchor.line_no_in_target - RESULT.end_anchor.matching_max_line_count_in_target + 1:])
        
    else:
        # 如果都没找到，认为 new_block 没有在目标文件中找到匹配，直接按时间顺序插入到目标文件中合适的位置。

        RESULT.action_taken["strategy"] = "no_match"
        if RESULT.target_stats["exists"]:
            # 注意：此处 target_org 解析通常不需要 fallback_year，因为整理后的文件应该已有年份
            target_org = FileParser.parse_org_file(target_filename)
        else:
            target_org = ChatOrgFile(target_filename)
        target_org.chat_blocks.append(new_block)
        final_lines = target_org.convert_to_md_lines()

    # 6. 持久化写入并记录最终状态
    os.makedirs(os.path.dirname(target_filename), exist_ok=True)
    with open(target_filename, 'w', encoding='utf-8') as f:
        f.writelines(final_lines)

    RESULT.action_taken["final_total_lines"] = len(final_lines)
    RESULT.action_taken["added_lines"] = RESULT.action_taken["final_total_lines"] - RESULT.target_stats["initial_total_lines"]
    RESULT.action_taken["status"] = "success"

    return RESULT


# ==========================================
# 主流程 (Main Controller)
# ==========================================

def parse_args():
    """
    解析命令行参数:
    --input_dir: 原始文件目录
    --output_dir: 归档输出目录
    --tasks_dir: 任务状态目录
    --fallback_year: 缺少年份时的兜底年份
    """
    parser = argparse.ArgumentParser(description="高可靠性聊天记录归档脚本")
    parser.add_argument("--input_dir", required=True, type=str, help="原始文件目录")
    parser.add_argument("--output_dir", required=True, type=str, help="归档输出目录")
    parser.add_argument("--knowledge_base_dir", required=True, type=str, help="知识库目录")
    parser.add_argument("--fallback_year", type=int, help="缺少年份时的兜底年份 (例如 2026)")
    return parser.parse_args()


def main():

    # 1. 初始化
    args = parse_args()

    # 2. 任务信息目录准备
    norm_task_run_dir = KnowledgeBasePaths.get_task_run_dir('normalize', args.knowledge_base_dir)
    os.makedirs(norm_task_run_dir,  exist_ok=True)

    # 3. 校验并获取相对路径
    # 确保输入目录在 00-chats-input-raw 目录下，以保留归档时的子目录结构
    raw_input_root = os.path.abspath(os.path.join(args.knowledge_base_dir, "00-chats-input-raw"))
    abs_input_dir = os.path.abspath(args.input_dir)

    if os.path.commonpath([abs_input_dir, raw_input_root]) != raw_input_root:
        raise ValueError(f"输入目录 {args.input_dir} (解析为 {abs_input_dir}) 必须位于知识库的 00 根目录 {raw_input_root} 之下")

    file_tasks = []  # (full_path, rel_path)
    for root, dirs, files in os.walk(args.input_dir):
        # 排除 10-chats-input-raw-used, processed 目录 (防御性)
        dirs[:] = [d for d in dirs if d not in ['processed', '10-chats-input-raw-used']]
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                # 计算相对于 00 根目录的路径，以确保归档到 10 时复刻完整的目录结构
                rel_path = os.path.relpath(os.path.abspath(full_path), raw_input_root)
                file_tasks.append((full_path, rel_path))

    if not file_tasks:
        print(f"No .md files found in {args.input_dir}")
        return

    # 4. 解析原始文件，获取所有 (ChatRawFile, rel_path)
    raw_files_with_rel: List[Tuple[ChatRawFile, str]] = []
    for full_path, rel_path in file_tasks:
        chat_raw_file = FileParser.parse_raw_file(full_path, fallback_year=args.fallback_year)
        raw_files_with_rel.append((chat_raw_file, rel_path))

    # --- debug: dump raw blocks to filename-idx_chunk.yaml ---
    for raw_file, rel_path in raw_files_with_rel:
        # 使用相对路径生成 dump 文件名，避免重名冲突
        safe_rel_name = rel_path.replace(os.sep, '_').replace('.', '_')
        for idx, block in enumerate(raw_file.chat_blocks):
            dump_filename = f"{safe_rel_name}_{idx}_raw_chunk"
            dump_path = KnowledgeBasePaths.get_task_orig_chunk_path(norm_task_run_dir, dump_filename)
            with open(dump_path, 'w', encoding='utf-8') as f:
                f.write(block.dump_yaml())

    # 5. for each file 的 each block, 合并到已有的目标文件中
    for raw_file, rel_path in raw_files_with_rel:
        safe_rel_name = rel_path.replace(os.sep, '_').replace('.', '_')
        for idx, block in enumerate(raw_file.chat_blocks):

            # 先在 args.output_dir 中定位目标群的目标月份文件（不检查，仅定位）
            # 目标文件命名规范: {group_id}_{YYYYMM}.md
            target_filename = KnowledgeBasePaths.get_org_file_path(args.knowledge_base_dir, chat_name=block.chat_name, dt=block.time_tag)

            # 合并
            merge_result = magic_merge(block, target_filename);
            # 写出合并日志 dump_{orig_filename}_{block_idx}_merge_chunk.yaml
            dump_filename = f"{safe_rel_name}_{idx}_merge_chunk"
            dump_path = KnowledgeBasePaths.get_task_merged_chunk_path(norm_task_run_dir, dump_filename)
            with open(dump_path, 'w', encoding='utf-8') as f:
                # 合并 merge_result 和 block 的信息，生成 dump 内容
                yaml.dump({
                    "block_info": yaml.safe_load(block.dump_yaml_without_content()),
                    "merge_result": merge_result.to_dict()
                }, f, allow_unicode=True)

    # 6. 归档原始文件到 10-chats-input-raw-used 目录
    for full_path, rel_path in file_tasks:
        dst_path = KnowledgeBasePaths.get_used_raw_file_path(args.knowledge_base_dir, rel_path)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        os.rename(full_path, dst_path)
        print(f"Archived: {rel_path} -> 10-chats-input-raw-used/")


if __name__ == "__main__":
    main()
