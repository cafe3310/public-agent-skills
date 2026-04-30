# Phase 6: 最终产出 (Finalization)

## 目标
完成全量资产的归档与质量校验，并更新发布索引，确保本次发布周期的成果可溯源、可交付。

## 操作步骤

1. **视频最终处理 (Video Finishing)**:
   - 确认 `video-clipped/` 下的所有视频已按 `workflows/04-capture-and-notetaking.md` 完成加工。
   - 检查视频参数（分辨率、编码、流畅度）是否符合 `kb/recording-standards.md`。
2. **生成/更新发布索引 (Release Indexing)**:
   - 在工作区根目录下维护 `RELEASE_INDEX.md`。
   - **操作**: 将本次发布周期作为一个条目追加到索引中。
   - **条目格式**:
     ```markdown
     ## [YYYY-MM-DD-HH] 模型发布: {Model-Name} - {Version}
     - **评价报告**: [链接至 YYYY-MM-DD-HH-...-evaluation.md]
     - **演示案例**: 
       - [Showcase-Desc-1] (./showcases/YYYY-MM-DD-HH-...)
       - [Showcase-Desc-2] (./showcases/YYYY-MM-DD-HH-...)
     - **成品视频**: 
       - [Video-Desc-1] (./video-clipped/YYYY-MM-DD-HH-...)
     - **核心卖点**: {简短一句话描述}
     ```
3. **资产关联度检查 (Consistency Check)**:
   - 确保 `docs-and-ref/` 中的设计稿、`notes/` 中的洞察与 `showcases/` 中的代码逻辑完全一致。
   - 检查所有内部链接（Internal Links）是否有效。
4. **归档与提交 (Archiving)**:
   - 确认所有视频素材已正确提交至 Git LFS。
   - 使用 `git add . && git commit -m "feat: complete release cycle for {model}-{version}"` 记录状态。
5. **清理工作区 (Cleanup)**:
   - 如果适用，清理开发过程中产生的临时文件、Cache 或不必要的原始巨型素材。

## 完成标准
- [ ] `RELEASE_INDEX.md` 已更新并包含本次发布的完整信息链。
- [ ] 所有交付资产（视频、报告、代码）已就绪并完成 Git 提交。
- [ ] 整个发布周期的上下文在 `doc-todo-log-loop` 中标记为“已完成”。
