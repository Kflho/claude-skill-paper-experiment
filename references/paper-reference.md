# Paper reference

## 目录结构

每篇论文在 `参考文献/` 下有自己的子文件夹，以论文标题命名（PDF 文件名去掉 `.pdf`）：

```
参考文献/
  <Paper Title>/
    <Paper Title>.pdf      # 原始 PDF
    paper_full.md           # 全文 markdown
    paper_p1-5.md           # 前 5 页 markdown（可选）
```

## 读取流程

当用户要求参考论文、读取 PDF 或查阅 参考文献 中的技术细节：

1. 在 `参考文献/` 下按论文标题关键词匹配子文件夹。
2. **子文件夹中有 `.md`** → 直接 Read（优先 `paper_full.md`）。
3. **子文件夹不存在或仅有 PDF** → 调用 `pdf-converter` skill 创建文件夹并转为 markdown。

## 两类文献文件的区别

- **Obsidian `Project XX 参考文献.md`**：用户自己的解读笔记，AI 只读不写。
- **`参考文献/<Paper Title>/paper_full.md`**：原始论文文本，供 AI 在方法论和实验设计阶段查阅。
