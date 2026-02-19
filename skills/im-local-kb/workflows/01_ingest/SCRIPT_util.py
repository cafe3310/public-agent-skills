import re
import os
import yaml
from datetime import datetime
from typing import List, Optional, Tuple

"""
SCRIPT_util.py
描述: 提供统一的接口，解析原始 (00) 和 整理后的 (01) 聊天记录文件。
遵循 fail-fast 原则，确保解析过程中的错误能够被及时捕获和处理。
"""

class RegexPatterns:
    """
    定义用于解析聊天记录的正则表达式模式。
    """

    @staticmethod
    def extract_time_tag(line: str, ref_date: Optional[str], fallback_year: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """
        判断给定行是否包含日期时间标签。
        如果是，则返回 True 和提取的日期时间参考 ref_date 补全之后的结果。返回的日期一定会是 YYYY-MM-DD HH:mm 形式。
        如果不是，返回 False 和 None。

        日期时间标签匹配模式，在前导 '-- ' 之后，支持多种格式，如
        - "2024-06-01"(日期)
        - "07-02"（日期）
        - "14:30"（时间）
        - "2024-06-01 14:30"（日期和时间）
        - "07-02 14:30"（日期和时间）

        如果 ref_date 不为 None，则可以用来补全缺失的年月日部分。
        如果 ref_date 为 None 且提供了 fallback_year，则可以补全 MM-DD 格式的年份。
        如果尝试补全之后仍然无法得到有效的日期时间格式，则抛异常，建议用户写更详细的日期。

        >>> RegexPatterns.extract_time_tag("-- 2024-06-01 14:30", "2024-01-01 00:00")
        (True, '2024-06-01 14:30')
        >>> RegexPatterns.extract_time_tag("-- 07-02", "2024-01-01 00:00")
        (True, '2024-07-02 00:00')
        >>> RegexPatterns.extract_time_tag("-- 07-02", None, 2024)
        (True, '2024-07-02 00:00')
        >>> RegexPatterns.extract_time_tag("-- 14:30", "2024-06-01 00:00")
        (True, '2024-06-01 14:30')
        """
        # 正则匹配一下。如果非 ^-- 开头，直接返回 False 和 None
        if not line.strip().startswith("--"):
            return False, None

        # 如果匹配 -- [仅包含 \d, :, - 和空格]，则继续处理；否则返回 False 和 None
        if not re.match(r"^--\s*[\d:\-\s]+$", line.strip()):
            return False, None

        orig_time_str = line.strip()[2:].strip()  # 去掉前导 '--' 和两边空白

        # 如果去掉前导 -- 后不包含数字，说明不是时间标签
        if not re.search(r"\d", orig_time_str):
            return False, None

        # 定义一个时间解析 fn，成功时返回时间对象，失败时返回 None
        def time_parse(s: str, fnt: str) -> Optional[datetime]:
            try:
                return datetime.strptime(s, fnt)
            except ValueError:
                return None

        # 将 ref_date 解析成 datetime 对象，方便后续补全
        # ref_date 可以是 None，也可以是 "YYYY-MM-DD" 或 "YYYY-MM-DD HH:mm" 格式
        ref_dt = None
        if ref_date:
            ref_dt = time_parse(ref_date, "%Y-%m-%d %H:%M") or time_parse(ref_date, "%Y-%m-%d")
            if not ref_dt:
                raise ValueError(f"提供的参考日期 '{ref_date}' 格式不正确，应该是 'YYYY-MM-DD' 或 'YYYY-MM-DD HH:mm'")

        # 然后我们就能用 if ... elif ... 来判断不同的时间格式，并尝试解析
        if time_parse(orig_time_str, "%Y-%m-%d %H:%M"):
            return True, orig_time_str  # 已经是完整的日期时间格式
        elif time_parse(orig_time_str, "%Y-%m-%d"):
            return True, orig_time_str + " 00:00"  # 补全时间部分
        elif time_parse(orig_time_str, "%m-%d %H:%M"):
            if ref_dt:
                return True, f"{ref_dt.year}-{orig_time_str}"  # 补全年份部分
            elif fallback_year:
                return True, f"{fallback_year}-{orig_time_str}" # 使用 fallback_year
            else:
                raise ValueError(f"无法解析时间标签 '{orig_time_str}'，由于缺少年份信息且未提供 fallback_year。")
        elif time_parse(orig_time_str, "%m-%d"):
            if ref_dt:
                return True, f"{ref_dt.year}-{orig_time_str} 00:00"  # 补全年份和时间部分
            elif fallback_year:
                return True, f"{fallback_year}-{orig_time_str} 00:00" # 使用 fallback_year
            else:
                raise ValueError(f"无法解析时间标签 '{orig_time_str}'，由于缺少年份信息且未提供 fallback_year。")
        elif time_parse(orig_time_str, "%H:%M") and ref_dt:
            return True, f"{ref_dt.year}-{ref_dt.month:02d}-{ref_dt.day:02d} {orig_time_str}"  # 补全日期部分
        else:
            raise ValueError(f"无法解析时间标签 '{orig_time_str}'，请提供更完整的日期时间信息")

    @staticmethod
    def extract_chat_name(line: str) -> Tuple[bool, Optional[str]]:
        """
        判断给定行是否包含聊天名称标签。
        如果是，则返回 True 和提取的聊天名称字符串；
        否则返回 False 和 None。
        聊天名称匹配模式
        (任意 heading + '-- ' + 名称)

        >>> RegexPatterns.extract_chat_name("## -- 摸鱼群")
        (True, '摸鱼群')
        >>> RegexPatterns.extract_chat_name("### -- [项目讨论群]")
        (True, '项目讨论群')
        >>> RegexPatterns.extract_chat_name("### 普通行")
        (False, None)
        """
        match = re.match(r"^#+\s+--\s+(.+)$", line.strip())
        if match:
            name = match.group(1).strip().strip("[]")
            return True, name
        return False, None

    @staticmethod
    def is_frontmatter(line: str) -> bool:
        """
        判断给定行是否为 FRONTMATTER 的开始或结束标记。
        """
        return line.strip() == "---"

    @staticmethod
    def extract_hashing_line(content: str) -> Optional[str]:
        """
        对内容进行预处理，以便进行 Hashing 匹配。
        包括：
        - 去除圆括号内的内容
        - 去除方括号内少于6字的内容
        - 去除整体过短的内容（如少于10字）
        - trim 前后空白
        返回预处理后的字符串。如果该行内容过短或不适合进行 Hashing，则返回 None。
        - 用于内容 Hashing 的匹配模式
            - Hashing 预处理 function（去除圆括号内内容；去除方括号内少于6字内容；去除整体过短的内容；trim 前后空白）

        >>> RegexPatterns.extract_hashing_line("这是一个测试消息 (图片) [表情]")
        '这是一个测试消息'
        >>> RegexPatterns.extract_hashing_line("短消息 (图片) [表情]")
        None
        """
        # 1. 去除圆括号内的内容
        text = re.sub(r"\(.*?\)", "", content)
        # 2. 去除方括号内少于6字的内容 (通常是 [图片], [表情] 等)
        text = re.sub(r"\[[^]]{1,5}]", "", text)
        # 3. trim 前后空白
        text = text.strip()
        # 4. 去除整体过短的内容 (少于 5 字)
        if len(text) < 5:
            return None
        return text


class ChatBlock:
    """
    代表一个以日期标注的聊天记录块，包含以下属性：
    - chat_name: 聊天名称字符串，如 "项目讨论群", "张三"
    - time_tag: 日期时间字符串，如 "2024-06-01", "07-02", "14:30", "2024-06-01 14:30", "07-02 14:30"
    - content: 聊天记录内容字符串（多行）
    - associated_file_path: 该块关联的来源或目标文件路径字符串
    """

    def __init__(self, chat_name: str, time_tag: str, content: List[str], associated_file_path: str):
        self.chat_name = chat_name
        self.time_tag = time_tag
        self.associated_file_path = associated_file_path
        self.content = content

    def dump_yaml(self) -> str:
        """
        将该聊天记录块以 YAML 格式写入目标文件路径，调试用。
        """
        data = {
            'chat_name': self.chat_name,
            'time_tag': self.time_tag,
            'associated_file_path': self.associated_file_path,
            'content': ''.join(self.content)
        }
        return yaml.dump(data, allow_unicode=True)

    def dump_yaml_without_content(self) -> str:
        """
        将该聊天记录块的元信息（不包含 content）以 YAML 格式写入目标文件路径，调试用。
        content 展示前 80 个字符，方便快速查看块的信息而不暴露全部内容。
        """
        data = {
            'chat_name': self.chat_name,
            'time_tag': self.time_tag,
            'associated_file_path': self.associated_file_path,
            'content_ellipsed': (''.join(self.content)[:80] + '...') if self.content else ''
        }
        return yaml.dump(data, allow_unicode=True)


class ChatRawFile:
    """
    代表一个原始聊天记录文件。可包含多个 chat 的各种时间的聊天记录块。
    包含以下属性：
    - file_path: 文件路径字符串
    - chat_blocks: List[ChatBlock]，文件中解析出的聊天记录块列表
    - dump_to_yaml(target_path): 将 chat_blocks 按照原始格式写入目标文件路径，调试用
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.chat_blocks: List[ChatBlock] = []


class ChatOrgFile:
    """
    代表一个整理后的聊天记录文件。仅包含一个 chat 的、按时间组织的聊天记录块列表。
    包含以下属性：
    - file_path: 文件路径字符串
    - chat_blocks: List[ChatBlock]，文件中解析出的聊天记录块列表

    包含以下方法：
    - validate_and_sort_blocks(): 验证 chat_blocks 中的块是否属于同一 chat，并按时间顺序排序。
    - write_to_markdown(target_path): 将 chat_blocks 按照整理后的格式写入目标文件路径。
    - dump_to_yaml(target_path): 将 chat_blocks 按照整理后的格式写入目标文件路径，调试用
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.chat_blocks: List[ChatBlock] = []

    def validate_and_sort_blocks(self):
        """
        如果包含不同的 chat 报错。
        如果包含时间缺失，或没有年-月-日的时间标签，报错。
        否则按时间顺序排序。
        """
        if not self.chat_blocks:
            return

        # 检查所有块的 chat_name 是否相同
        first_chat_name = self.chat_blocks[0].chat_name
        if not all(block.chat_name == first_chat_name for block in self.chat_blocks):
            raise ValueError(f"整理后的文件应该只包含一个 chat，但找到多个不同的 chat")

        # 检查所有块都有有效的时间标签
        # YYYY-MM-DD HH:mm 格式中，一定要包含 年-月-日；但允许缺失时间部分
        for block in self.chat_blocks:
            if not block.time_tag:
                raise ValueError(f"聊天记录块缺少时间标签")
            if not re.match(r"^\d{4}-\d{2}-\d{2}", block.time_tag):
                raise ValueError(f"时间标签 '{block.time_tag}' 不包含年-月-日信息")

        # 按时间顺序排序（如果时间标签格式正确，直接按字符串排序即可）
        self.chat_blocks.sort(key=lambda b: b.time_tag)

    def convert_to_md_lines(self) -> List[str]:
        """
        将 chat_blocks 转换成整理后的 Markdown 格式的行列表，准备写入目标文件。
        """
        self.validate_and_sort_blocks()
        md_lines = []
        if self.chat_blocks:
            chat_name = self.chat_blocks[0].chat_name
            md_lines.append(f"## -- {chat_name}\n\n")

            for block in self.chat_blocks:
                md_lines.append(f"-- {block.time_tag}\n\n")
                md_lines.extend(block.content)
                md_lines.append("\n\n")
        return md_lines

class FileParser:
    """
    解析器类，提供静态方法解析原始和整理后的聊天记录文件。
    """

    @staticmethod
    def parse_raw_file(file_path: str, fallback_year: Optional[int] = None) -> ChatRawFile:
        """
        解析原始聊天记录文件，提取其中的 ChatBlock 列表。

        1. 如果内容第一行是 frontmatter, 跳过前后 frontmatter 部分
        2. 设置 last_chat_name 是 None，last_time_tag 是 None, current_content 是 []
        3. 遍历每一行，使用 RegexPatterns.extract_chat_name 判断是否为 chat_name 行。
            - 如果是，说明这是一个新的 chat 块的开始。将之前的块（如果存在）保存到 chat_blocks 中，然后重置 last_time_tag=None, current_content=[]；更新 last_chat_name。
            - 否则，使用 RegexPatterns.extract_time_tag 判断是否为 time_tag 行（传递当前的 last_time_tag 作为 ref_time）。
                - 如果是，说明这是一个新的时间块的开始。将之前的块（如果存在）保存到 chat_blocks 中，然后重置 current_content；更新 last_time_tag。
                - 否则，将该行添加到 current_content 中。
        4. 最后将最后一个块（如果存在）保存到 chat_blocks 中。
        """
        raw_file = ChatRawFile(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 跳过 frontmatter
        start_idx = 0
        if lines and RegexPatterns.is_frontmatter(lines[0]):
            start_idx = 1
            while start_idx < len(lines) and not RegexPatterns.is_frontmatter(lines[start_idx]):
                start_idx += 1
            start_idx += 1  # 跳过结束的 frontmatter 标记

        last_chat_name = None
        last_time_tag = None
        current_content = []

        for line in lines[start_idx:]:
            is_chat, chat_name = RegexPatterns.extract_chat_name(line)
            if is_chat:
                # 保存之前的块
                if last_chat_name is not None and last_time_tag is not None:
                    raw_file.chat_blocks.append(ChatBlock(last_chat_name, last_time_tag, current_content, file_path))
                # 重置状态
                last_chat_name = chat_name
                last_time_tag = None
                current_content = []
            else:
                is_time, time_tag = RegexPatterns.extract_time_tag(line, last_time_tag, fallback_year=fallback_year)
                if is_time:
                    # 保存之前的块
                    if last_chat_name is not None and last_time_tag is not None:
                        raw_file.chat_blocks.append(ChatBlock(last_chat_name, last_time_tag, current_content, file_path))
                    # 更新时间标签并重置内容
                    last_time_tag = time_tag
                    current_content = []
                else:
                    # 普通内容行
                    current_content.append(line)

        # 保存最后一个块
        if last_chat_name is not None and last_time_tag is not None:
            raw_file.chat_blocks.append(ChatBlock(last_chat_name, last_time_tag, current_content, file_path))

        return raw_file

    @staticmethod
    def parse_org_file(file_path: str, fallback_year: Optional[int] = None) -> ChatOrgFile:
        """
        解析整理后的聊天记录文件，提取其中的 ChatBlock 列表。
        直接调用 parse_raw_file 解析原始文件，然后调用 ChatOrgFile 的 validate_and_sort_blocks() 方法验证和排序。
        """
        raw_file = FileParser.parse_raw_file(file_path, fallback_year=fallback_year)
        org_file = ChatOrgFile(file_path)
        org_file.chat_blocks = raw_file.chat_blocks
        org_file.validate_and_sort_blocks()
        return org_file


class KnowledgeBasePaths:
    """
    定义知识库中相关文件的路径结构和命名规范，相对于 kb 根目录。
    """
    @staticmethod
    def get_task_run_dir(task_type: str, knowledge_base_dir: str) -> str:
        """
        根据任务类型生成任务运行目录路径。
        例如： kb/tasks/normalize/run_2024-06-01_14-30/
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        path = os.path.join(knowledge_base_dir, "tasks", task_type, f"run_{timestamp}")
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def get_task_orig_chunk_path(task_run_dir: str, chunk_name: str) -> str:
        """
        根据任务运行目录和块名称生成原始块文件路径。
        例如： {task_run_dir}/chunks/{chunk_name}.yaml
        """
        path = os.path.join(task_run_dir, "chunks", f"{chunk_name}.yaml")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    @staticmethod
    def get_task_merged_chunk_path(task_run_dir: str, chunk_name: str) -> str:
        """
        根据任务运行目录和块名称生成合并后块文件路径。
        例如： {task_run_dir}/chunks_merged/{chunk_name}.yaml
        """
        path = os.path.join(task_run_dir, "chunks_merged", f"{chunk_name}.yaml")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    @staticmethod
    def get_org_file_path(knowledge_base_dir: str, chat_name: str, dt: str) -> str:
        """
        根据聊天名称和日期时间生成整理后文件路径。
        例如： kb/01-chats-input-organized/{chat_name}/{YYYY-MM}.md
        """
        try:
            dt_obj = datetime.strptime(dt, "%Y-%m-%d %H:%M")
        except ValueError:
            dt_obj = datetime.strptime(dt, "%Y-%m-%d")

        date_str = dt_obj.strftime("%Y-%m")
        return os.path.join(knowledge_base_dir, "01-chats-input-organized", chat_name, f"{date_str}.md")

    @staticmethod
    def get_used_raw_file_path(knowledge_base_dir: str, rel_path: str) -> str:
        """
        根据相对路径生成已使用的原始文件路径。
        例如： kb/10-chats-input-raw-used/{rel_path}
        """
        return os.path.join(knowledge_base_dir, "10-chats-input-raw-used", rel_path)

    @staticmethod
    def get_task_prompt_path(task_run_dir: str, task_idx: int) -> str:
        """
        根据任务运行目录、索引和提示名称生成提示文件路径。
        例如： {task_run_dir}/prompts_{task_idx}.md
        """
        return f"{task_run_dir}/prompts_{task_idx}.md"

    @staticmethod
    def get_task_output_slice_path(task_run_dir: str, task_idx: int, chunk_idx: int) -> str:
        """
        根据任务运行目录、索引和响应名称生成分段输出文件路径。
        例如： {task_run_dir}/outputs_{task_idx}_chunk_{chunk_idx}.md
        """
        return f"{task_run_dir}/outputs_{task_idx}_chunk_{chunk_idx}.md"

if __name__ == "__main__":
    import doctest
    doctest.testmod()
