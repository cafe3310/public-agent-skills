# Workflow: Chat Metadata & Notes Management

## 核心目标
维护 `02-project-specs/notes.yaml`，记录群聊、单聊的非项目性背景信息，为 Agent 提供长期记忆支撑。

## 记录场景
1. **身份识别**：记录参与者的真实姓名、职位、别名。
2. **关系梳理**：记录记录人与对方的协作关系、信任程度。
3. **分类锚点**：记录该群聊应归属的长期项目或业务领域。

## 操作规范

### 1. 查阅备注 (Lookup)
- 在开始任何深度分析（Generate）前，Agent 应主动检查 `02-project-specs/notes.yaml` 是否存在相关群聊的背景信息。
- 引用备注信息时，无需标注来源，直接融入背景分析即可。

### 2. 更新备注 (Update/Append)
- **发现新信息**：当在 Ingest 或分析过程中发现明确的身份或关系信息时。
- **执行追加**：
    - 使用 `read_file` 读取 `notes.yaml`。
    - 如果 `chats` 列表中已存在该 `name`，使用 `replace` 在其 `notes` 数组中追加新条目。
    - 如果不存在，则在 `chats` 数组末尾添加新对象：
      ```yaml
      - name: "新群聊"
        notes:
          - "备注内容"
      ```
- **保持简洁**：每条备注应为短句，避免长篇大论。

## 文件格式约束
必须严格遵守 `notes.yaml` 的 YAML 语法：
```yaml
meta: {id: "notes", description: "..." }
chats: 
  - name: string
    notes: string[]
```
