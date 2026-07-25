---
name: scientific-research
description: Scientific research workflow — experiment design, paper analysis, methodology planning, Obsidian-formatted output. Use when the user discusses 论文, 文献, 实验设计, 课题, 项目目标, 方法论, 科研流程, or needs structured research notes output.
---

# Scientific Research

**Leading words:** 论文 (paper analysis), 文献 (literature review), 实验设计 (experiment design), 课题/项目目标 (research objective), 方法论/科研流程 (methodology), Note (project note), Schedule (daily log), 参考文献 (literature notes), Target (experiment target).

## 首次使用？

检查项目 CLAUDE.md 末尾是否有 `## SKILL INITIALIZED: true`。

**没有** → 首次使用。读取 `references/first-run.md`，跟随 9 步初始化向导完成配置后再继续。

**有** → 已初始化。从 CLAUDE.md 获取三文件路径，直接进入阶段路由。

> 如需重新初始化（更换 vault、添加新项目等），删除 CLAUDE.md 中的 `SKILL INITIALIZED: true` 行即可。

## 环境设置

首次使用或更换环境 → [references/setup.md](references/setup.md)（mattpocock/skills 安装、git 备份铁律、MATLAB 验证）。

已验证过的项目跳过，直接从 CLAUDE.md 读取配置。Git 备份铁律：**运行批量实验/重构前必须 `git add -A && git commit`** —— 实验代码迭代快，git 是唯一保险。

---

## Three-file workflow

Three project files live somewhere in the user's Obsidian vault. **Read only — never write.** The user maintains all three manually. Actual paths are recorded in the project's CLAUDE.md during [Project initialization](#project-initialization).

| Role | Sections | When to read |
|---|---|---|
| **Note** | 目标 → 参考 → 流程 → 架构 → 总结 → 问题 | User discusses project goals, experiment design, or architecture mapping |
| **参考文献** | 论文解读 → 论文方法 | User asks about paper content, methodology, or technical implementation |
| **Schedule** | Date headers `# MM.DD`, task lists | User asks "今天做什么" or needs progress-aware suggestions |

The user may name and locate these files however they like — initialization records the actual paths. The default convention is `Project XX Note.md` / `Project XX 参考文献.md` / `Project XX Schedule.md` at the vault root, but any path within the vault is valid.

## Project initialization

Before any phase routing, verify that file paths for the current project are known. If the project's CLAUDE.md lacks a `## Scientific Research Paths` section, run the full initialization flow in [references/first-run.md](references/first-run.md). If already initialized, read paths from CLAUDE.md and proceed.

---

## Phase routing

Before routing to a phase, **always** check: are file paths initialized for this project? If not, run Project initialization first.

Identify the user's current research phase from their prompt, then act:

| Phase | Trigger examples | Read | Invoke sub-skills | AI action |
|---|---|---|---|---|
| Paper analysis | 读论文, 解读文献, literature review | 参考文献 | `pdf-converter`, `research`, `grilling` | Interpret paper; surface gaps and open questions |
| Objective setting | 项目目标, 课题方向, research objective | Note | `grilling`, `writing-great-skills` | Propose research objectives grounded in paper findings |
| Experiment design | 设计实验, 怎么验证, experiment design | Note + 参考文献 | `grilling`, `research`, `prototype`, `dataviz` | Design experiments to validate each objective; justify method choices |
| Methodology | 怎么实现, 技术细节, method | 参考文献 | `codebase-design`, `tdd` | Answer with technical explanation; attribute output to doc section |
| Architecture mapping | 项目架构, 文件结构 | Note | — | Map research workflow to folder structure (see Project structure below) |
| Task planning | 今天做什么, 进度, plan | Note + Schedule | — | Suggest today's tasks based on Note goals and Schedule history |

## Paper reference

Each paper lives in its own subfolder under `参考文献/`, named after the paper title (PDF filename without `.pdf`):

```
参考文献/
  <Paper Title>/
    <Paper Title>.pdf      # original PDF
    paper_full.md           # full paper text (markdown)
    paper_p1-5.md           # first 5 pages (markdown, optional)
```

When the user asks to reference a paper, read a PDF, or consult 参考文献 for technical details:

1. Look for a matching subfolder under `参考文献/` — match by paper title keywords.
2. **If the subfolder with `.md` exists** → read the markdown directly with Read (prefer `paper_full.md`).
3. **If subfolder missing or has PDF only** → invoke `pdf-converter` to create the folder and convert to markdown.

The Obsidian `Project XX 参考文献.md` is the user's own interpretation notes (read-only for AI). The markdown under `参考文献/` is the raw paper text for AI consumption during methodology and experiment design phases.

---

## Output attribution

**Every AI response** that maps to a section of the three files must lead with its destination:

```
**→ Project XX Note / 目标**
... suggested objective ...

**→ Project XX 参考文献 / 论文方法**
... technical explanation ...

**→ Project XX Schedule / MM.DD**
... suggested tasks ...
```

This lets the user copy-paste without editing. The attribution header names the doc and the section within it.

## Output format

All output must match the user's Obsidian conventions exactly so text is copy-paste ready. See [FORMAT.md](FORMAT.md) for the complete specification. Key rules at a glance:

- **Tab** indentation only; no spaces for indent
- `- [ ]` / `- [x]` for task items; `-` for plain lists
- No blank lines between same-level siblings; one blank line between groups
- `#` / `##` / `###` heading hierarchy; `---` for major section breaks
- File and function names in `` `backticks` ``; math in `$inline$` / `$$block$$`
- Short labels (目标, 流程, 验收标准) inline with content on same line; long content on next line with one Tab indent

## Project structure

此 skill 创建新项目时默认采用以下约定。若用户已有现成项目结构，初始化时扫描实际目录自动适配。

```
Common/                          # 跨项目共享代码（与 Project/ 同级）
Project/                         # 所有项目（固定层，防止摊平）
  [Category]/                    # 可选分类（如 Postgraduate/）
    Project_XX_descriptor/       # 单个项目
      Function/                  # 可复用函数（不可独立运行）
      Script/                    # 可复用脚本（可独立运行，也可被调用）
      Test/                      # 单元测试（扁平）
      Main/
        Target_XX/               # 按实验目标分组的入口
      Output/
        Experiment_XX_descriptor/  # 按实验分组的产出
```

**File naming:** `CapitalCase_underscore_separated`。数字前缀：`Test_01_` / `Experiment_01_`。MATLAB 约束：文件名必须以字母开头。

**Code formatting:** variable and function names follow the same CapitalCase convention. Inline formatting rules (Chinese-English spacing, bracket annotations, colon notes) match [FORMAT.md](FORMAT.md).

**MATLAB 路径**：初始化时由用户指定项目根目录（所有依赖的公共祖先），Claude 扫描该目录下所有含 `.m` 文件的子文件夹，自动计算相对路径并写入项目 CLAUDE.md。不预设目录名——`Common/`、`Function/`、`Script/` 只是默认约定的名字。
