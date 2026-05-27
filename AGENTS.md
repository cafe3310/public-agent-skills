- 在创建 agent skill 时，在 yaml 的 frontmatter 中自定义部分定义如下：
  - `author`: 技能作者。若为自主开发则写为 `github/cafe3310`；若为别处复制/衍生而来则写为原始链接/项目。
  - `depends_on_skill`: 列表格式。一个或多个本 skill 运行所依赖的其他 agent skill （例如 `- github/cafe3310/agent-skill-memories-off -> memories-off`）。
  - `depends_on_binary`: 列表格式。一个或多个本 skill 运行所依赖的其他系统程序（典型的如 `- ffmpeg`）。
- 技能目录使用 kebab-case；脚本统一存放在 `scripts/`。
- 暂时不用的技能存放在 `skills_parked/` 目录下，并在 `README.md` 中进行说明。
- `SKILL.md` 必须包含完整的 frontmatter (name, description, author, license, 以及上述自定义依赖属性)。
- 维护技能时，优先保持其原有的目录结构和文档风格。

