# ARCHIVE.md 记录格式参考

此文件定义了 `git-snapshot-rollback` 技能在存档和落地阶段生成的日志格式。

## 存档阶段 (Archive) 记录模板

```markdown
## [YYYY-MM-DD HH:MM:SS] 存档记录

- **动作**: 准备回退
- **原因**: {reason}
- **当前分支**: {current_branch}
- **生成的存档分支**: `archive/{current_branch}/YYYY-MM-DD-HH-mm`
- **回退目标 (Target)**: `{commit_b[:7]}`
- **目标详情**: {commit_b_info}

----------------------------------------
```

## 落地阶段 (Land) 记录模板

```markdown
## [YYYY-MM-DD HH:MM:SS] 存档记录

- **动作**: 回退完成
- **原因**: {reason}
- **来源存档分支**: `archive/{current_branch}/YYYY-MM-DD-HH-mm`
- **回退的分支**: {current_branch}
- **来源 Commit**: `{commit_a[:7]}`
- **来源详情**: {commit_a_info}

----------------------------------------
```
