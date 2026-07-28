# Paper reference

## 目录结构

论文 PDF 和 markdown 存储在项目外部的独立目录中，路径在初始化时记录到项目 CLAUDE.md 的 `## Scientific Research Paths` 表中（`论文文件夹` 字段）。

每篇论文在论文文件夹下有自己的子文件夹，以论文标题命名（PDF 文件名去掉 `.pdf`）：

```
<论文文件夹>/
  <Paper Title>/
    <Paper Title>.pdf      # 原始 PDF
    paper_full.md           # 全文 markdown
    paper_p1-5.md           # 前 5 页 markdown（可选）
```

论文文件夹独立于项目仓库——不在 `projects/` 目录内，不参与项目 git 追踪。

## 读取流程

当用户要求参考论文、读取 PDF 或查阅论文中的技术细节：

1. 从项目 CLAUDE.md → `## Scientific Research Paths` → `论文文件夹` 获取路径。
2. 在该路径下按论文标题关键词匹配子文件夹。
3. **子文件夹中有 `.md`** → 直接 Read（优先 `paper_full.md`）。
4. **子文件夹不存在或仅有 PDF** → 调用 `pdf-converter` skill 创建文件夹并转为 markdown。

## 两类文献文件的区别

- **Obsidian `Project XX 参考文献.md`**：用户自己的解读笔记，AI 只读不写。
- **`<论文文件夹>/<Paper Title>/paper_full.md`**：原始论文文本，供 AI 在方法论和实验设计阶段查阅。
