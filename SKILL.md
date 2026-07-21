---
name: scientific-research
description: Scientific research workflow — experiment design, paper analysis, methodology planning, Obsidian-formatted output. Use when the user discusses 论文, 文献, 实验设计, 课题, 项目目标, 方法论, 科研流程, or needs structured research notes output.
---

# Scientific Research

**Leading words:** 论文 (paper analysis), 文献 (literature review), 实验设计 (experiment design), 课题/项目目标 (research objective), 方法论/科研流程 (methodology), Note (project note), Schedule (daily log), 参考文献 (literature notes), Target (experiment target).

## Three-file workflow

Three project files live in the user's Obsidian vault. **Read only — never write.** The user maintains all three manually.

| File | Sections | When to read |
|---|---|---|
| `Project XX Note.md` | 目标 → 参考 → 流程 → 架构 → 总结 → 问题 | User discusses project goals, experiment design, or architecture mapping |
| `Project XX 参考文献.md` | 论文解读 → 论文方法 | User asks about paper content, methodology, or technical implementation |
| `Project XX Schedule.md` | Date headers `# MM.DD`, task lists | User asks "今天做什么" or needs progress-aware suggestions |

**First project entry:** ask where these three files live, record paths in the project's CLAUDE.md.

## Phase routing

Identify the user's current research phase from their prompt, then act:

| Phase | Trigger examples | Read | Invoke sub-skills | AI action |
|---|---|---|---|---|
| Paper analysis | 读论文, 解读文献, literature review | 参考文献 | `deep-research`, `research` | Interpret paper; surface gaps and open questions |
| Objective setting | 项目目标, 课题方向, research objective | Note | `grilling` | Propose research objectives grounded in paper findings |
| Experiment design | 设计实验, 怎么验证, experiment design | Note + 参考文献 | `grilling`, `deep-research` | Design experiments to validate each objective; justify method choices |
| Methodology | 怎么实现, 技术细节, method | 参考文献 | — | Answer with technical explanation; attribute output to doc section |
| Architecture mapping | 项目架构, 文件结构 | Note | — | Map research workflow to folder structure (see Project structure below) |
| Task planning | 今天做什么, 进度, plan | Note + Schedule | — | Suggest today's tasks based on Note goals and Schedule history |

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

When mapping research workflow to filesystem, apply this template:

```
Common/                          # Cross-project shared code
[Middle_layer]/                  # Optional: organizational grouping (e.g. Postgraduate_project/)
  Project_XX_descriptor/         # Individual project
    Function/                    # Non-runnable functions — must be called by others
    Script/                      # Runnable standalone scripts; may also be called
    Test/                        # Flat directory, temporary unit tests
    Main/
      Target_XX/                 # Experiment targets grouped by objective
    Output/
      Experiment_XX_descriptor/  # Per-experiment outputs: data + figures
```

**File naming:** `CapitalCase_underscore_separated`. Numbered prefixes: `Test_01_` / `Experiment_01_`. MATLAB constraint: files must start with a letter. Experiment name and figure name are the only per-experiment variables.

**Code formatting:** variable and function names follow the same CapitalCase convention. Inline formatting rules (Chinese-English spacing, bracket annotations, colon notes) match [FORMAT.md](FORMAT.md).
