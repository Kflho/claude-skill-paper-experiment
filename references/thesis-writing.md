# Thesis Writing — LaTeX 论文写作工作流

> 框架优先，逐节讨论，编译验证。只记录实验跑出的真实数据，不美化。

## 核心规则：Obsidian 与 LaTeX 的分工

| 操作 | 目标 | 规则 |
|---|---|---|
| 实验报告 | Obsidian Note（`{项目名} note.md` → `## 实验报告`） | **直接写入**，无需确认。跑完实验立即更新。 |
| 流程/架构复选框 | Obsidian Note（`# 流程` / `# 架构`） | **直接更新**。标记完成状态、补充结果摘要。 |
| LaTeX `.tex` 文件 | `latex/` 目录下的 `.tex` 文件 | **必须用户确认后写入**。先在对话中贴草案 → 用户确认 → 再写入 tex。 |
| LaTeX 编译 | `latexmk -pdf` | 写入 tex 后可立即编译验证，但**写入本身需要确认**。 |

**铁律：跑完实验 → 写 Obsidian（直接）。写完 Obsidian → 贴草案给用户 → 用户说"可以写" → 写 tex。不跳过用户确认直接改 tex。**

## 前置条件

项目 CLAUDE.md 必须包含以下路径（初始化时收集）：

| 路径项 | CLAUDE.md 段 | 示例 |
|---|---|---|
| LaTeX 文件夹 | `## Scientific Research Paths` → `latex 文件夹` | `D:/.../pg_01/latex/` |
| MATLAB 源码目录 | `## Scientific Research Paths` → `MATLAB 项目根目录` | `D:/.../project_01_distributed_fault_monitoring/src/` |
| results 目录 | `## Scientific Research Paths` → `results 文件夹` | `D:/.../pg_01/results/` |

## 编译环境

### latexmkrc

检查 LaTeX 文件夹下是否有 `.latexmkrc`：

- **有** → 直接使用
- **没有，但存在 `.tex` 文件** → 分析主文件的 `\documentclass`、bib 引擎、编译引擎，自动生成合适的 `.latexmkrc`：

| 检测项 | 来源 | 配置 |
|---|---|---|
| 编译引擎 | `\documentclass` 参数 | `$pdf_mode`：pdflatex→1, xelatex→5, lualatex→4 |
| bib 处理 | `\bibliographystyle` + `\usepackage{natbib}` 等 | `$bibtex_use`：natbib→1.9(bibtex), biblatex→2(biber) |
| 重复编译 | — | 默认 `$max_repeat = 3` |
| 清理文件 | — | 默认 `$clean_ext = "aux blg log out synctex.gz fls fdb_latexmk"` |

- **没有 `.tex` 文件** → 不生成，标注 `(pending)`，等用户写入内容后再配

### 编译命令

```bash
cd "<latex 文件夹>" && latexmk -pdf <主文件名>.tex
```

编译失败时报告具体错误行，不静默跳过。

## 写作流程

### Step 1：信息收集

读取以下来源建立完整上下文：

| 来源 | 内容 | 用途 |
|---|---|---|
| Note `# 目标` | 研究目标与指标 | 对齐论文贡献 |
| Note `## 实验报告` | 6 个实验的全部运行结果 | 仿真章节数据来源 |
| 参考文献 `# 论文解读` | 论文逐节解读 | 理论章节参照 |
| 参考文献 `# 论文方法` | 仿真搭建方法 | 参数与拓扑描述 |
| MATLAB 源码 | `create_model_1.m`、`init_parameters.m`、各 `experiment_XX_*.m` | 确认实际参数与实验配置 |

### Step 2：搭建章节框架

1. 读 LaTeX 主文件，确认 `\input{}` 结构和已有章节
2. 写/重写的目标章节，先输出**框架骨架**——只有章节标题 + 注释标注数据来源，**不写具体内容**：

```
\subsection{System configuration}
% 数据来源：create_model_1.m (A_i, B_i, ...), init_parameters.m (T_sim, k_fault)
% Fig: simulation_topology.pdf

\subsection{Validation of distributed residual generation}
\subsubsection{Decentralized computation}
% 数据来源：Note / experiment_01_decentralized_residual
% 关键指标：局域 vs 全局残差最大偏差 ~10^{-15}
\subsubsection{Zero-mean property}
% 数据来源：Note / experiment_02_zero_mean_residual
```

3. 框架中每个 `%` 注释标注该节数据来自哪个实验/脚本，确保不张冠李戴
4. 框架写好后的 tex 文件中只有 section/subsection 命令和 `%` 注释，没有正文
5. 将框架**贴到对话里给用户审阅**，不直接写完整内容

### Step 3：逐节讨论与写入

对框架中每个子节：

1. **提案** — 在对话中贴出该节的 markdown 草案（含完整段落、公式、数值、引用），标注数据来源
2. **讨论** — 用户审阅数值是否准确、措辞是否恰当、结论是否妥当。修改直到用户确认
3. **写入** — 用户确认后，将内容写入 `.tex` 文件（用 Edit 工具替换对应的 `% TODO` 注释块）
4. **编译** — 写入后立即 `latexmk -pdf` 编译验证：`cd "<latex 文件夹>" && latexmk -pdf v1.0.tex`
5. **下一节** — 编译通过后进入下一节，重复 1-4

### Step 4：完成

全部章节写入并编译通过后：

- 报告最终 PDF 路径
- 如有编译 warning（underfull/overfull），列出供用户判断是否需要处理
- 更新 Note 的 `## 实验报告` 中对应实验的备注，标注"已写入 thesis Chapter 5"

## 铁律

1. **框架确认前不写正文 tex**。框架留在 `.tex` 文件中的只有 `% TODO` 注释
2. **所有数值必须来自实验报告**。禁止从论文原文照抄数值；禁止凭空编造检测延迟、误报率、定位准确率
3. **实事求是**。实验跑出 75% 定位准确率就写 75%，不美化；讨论失败原因，不掩盖
4. **每节写完立即编译**。不攒到最后一次性编译——定位错误困难
5. **对照 MATLAB 源码**。写仿真参数时必须读 `create_model_1.m` / `init_parameters.m` 确认矩阵数值、噪声协方差、计算中心划分
6. **公式编号不重复**。Chapter 5 是仿真章节，不定义新公式编号；引用前文章节公式用 `Eq.~(27)` 等形式
7. **图片路径**：中文论文引用 `../results/cn/<filename>`，英文论文引用 `../results/eng/<filename>`（**中文论文 → 中文图片，英文论文 → 英文图片**）；语言无关图（拓扑/原理示意图）放 `../results/` 根目录共用。图片由 MATLAB 实验脚本生成，不在此阶段重新生成
8. **图片只标注论文参数** → 见 [SKILL.md 论文写作铁律 #4](../SKILL.md)。
