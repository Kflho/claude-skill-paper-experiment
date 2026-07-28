---
name: scientific-research
description: Scientific research workflow — experiment design, paper analysis, methodology planning, Obsidian-formatted output. Use when the user discusses 论文, 文献, 实验设计, 课题, 项目目标, 方法论, 科研流程, or needs structured research notes output.
---

# Scientific Research

## 首次使用？

检查项目 CLAUDE.md 末尾是否有 `## SKILL INITIALIZED: true`。

- **没有** → 读取 `references/first-run.md`，跟随 9 步初始化向导完成配置后再继续。
- **有** → 已初始化。从 CLAUDE.md 的 `## Scientific Research Paths` 获取三文件路径，直接进入阶段路由。

> 重新初始化：删除 CLAUDE.md 中的 `SKILL INITIALIZED: true` 行。

## 环境设置

首次使用或更换环境 → [references/setup.md](references/setup.md)（mattpocock/skills 安装、git 备份铁律、MATLAB 验证）。已验证的项目跳过。

---

## Three-file workflow

三文件位于用户 Obsidian vault 中，路径记录在项目 CLAUDE.md。

| Role | Sections | When to read |
|---|---|---|
| **Note** | 目标 → 参考 → 流程 → 架构 → 总结（含实验报告）→ 问题 | 项目目标、实验设计、架构映射 |
| **参考文献** | 论文解读 → 论文方法 | 论文内容、方法论、技术实现 |
| **Schedule** | `# MM.DD` 日期标题 + 任务列表 | 今日任务、进度查询 |

**权限：**
- ✅ 可修改：任务复选框、脚本/函数名、文件路径、代码块引用
- ⚠️ 用户授权后：实验目标措辞、验收标准、公式数值、流程步骤
- ❌ 不可修改：论文解读内容

**实验设计铁律：**
1. **验收标准不得预设精度**：严禁在实验运行前写入具体数值精度。仅写"运行后报告实际精度"或"记录实际偏差与理论界对比"。
2. **目标 = 验证什么，非怎么实现**：实验目标写高层验证目的，实现步骤写入流程。
3. **目标必须显式引用项目目标**：格式 `目标 ：验证目标X.Y，<目标原文>`——写明验证的是 Note `# 目标` 中的哪个编号。AI 据此判断实验对应哪个复选框。
4. **数值仅在运行后填入**：`验收标准` 字段中的具体数值必须来自实际运行结果。

---

## Phase routing

根据用户输入识别科研阶段：

| Phase | Trigger | Read | Invoke | AI action |
|---|---|---|---|---|
| Paper analysis | 读论文, 解读文献, literature review | 参考文献 | `pdf-converter`, `research`, `grilling` | 解读论文，找研究缺口。[论文目录结构 →](references/paper-reference.md) |
| Objective setting | 项目目标, 课题方向, research objective | Note | `grilling`, `writing-great-skills` | 基于论文提出研究目标 |
| Experiment design | 设计实验, 怎么验证, experiment design | Note + 参考文献 | `grilling`, `research`, `prototype`, `dataviz` | 设计实验验证目标。每个实验的目标字段引用 Note 目标编号。实验通过后标记对应复选框 |
| Methodology | 怎么实现, 技术细节, method | 参考文献 | `codebase-design`, `tdd` | 技术解答，归属到论文章节。[代码格式化脚本 →](references/scripts.md) |
| Architecture mapping | 项目架构, 文件结构 | Note | — | 映射研究流程到文件夹结构。[项目结构规范 →](references/project-structure.md) |
| Task planning | 今天做什么, 进度, plan | Note + Schedule | — | 读取 Schedule 最新日期下未完成任务，自动实现。**写→格式化→跑**，跑通后自动复盘操作问题（通用→skill，本项目→CLAUDE.md），执行[任务完成同步 →](references/task-completion-sync.md) |
| Batch writing | 批量写脚本, fan-out, 并行编写, 同时写多个, 多个实验脚本 | Note + Schedule | — | 并行编写多个独立脚本。**写→格式化→审查diff→跑** → [references/fan-out-writing.md](references/fan-out-writing.md) |

---

## Output attribution

每条 AI 回复标注入目标文档和章节：

```
**→ Project XX Note / 目标**
... content ...

**→ Project XX 参考文献 / 论文方法**
... content ...

**→ Project XX Schedule / MM.DD**
... content ...
```

## Output format

所有输出遵循 Obsidian 格式规范 → [FORMAT.md](FORMAT.md)。

写完 MATLAB 代码后可运行格式化脚本规范化大小写 → [references/scripts.md](references/scripts.md)。

## 任务完成同步

**每次完成实验脚本或 CLAUDE.md 任务进度中的任务后**，必须同步更新所有位置的复选框和内容 → [references/task-completion-sync.md](references/task-completion-sync.md)。完成后按 Output attribution 格式逐条报告更新。

## Project structure

新建项目默认结构 → [references/project-structure.md](references/project-structure.md)。已有项目初始化时扫描实际目录自动适配。
