---
name: scientific-research
description: Scientific research workflow — experiment design, paper analysis, methodology planning, Obsidian-formatted output. Use when the user discusses 论文, 文献, 实验设计, 课题, 项目目标, 方法论, 科研流程, or needs structured research notes output.
---

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
| **Note** | 目标 → 流程 → 架构 → 总结（实验报告）。完整结构见 [FORMAT.md → Note file structure](FORMAT.md#note-file-structure) | 项目目标、实验计划、实现架构、实验数据 |
| **参考文献** | 论文解读 → 论文方法 | 论文内容、方法论、技术实现 |
| **Schedule** | `# MM.DD` 日期标题 + 任务列表。只记录做了什么，不写怎么做（怎么做 → Note `# 架构`） | 进度追踪、今日任务 |

论文 PDF/markdown 原始文件存储在项目外部的独立目录中，路径记录在 CLAUDE.md → `## Scientific Research Paths` → `论文文件夹`。目录结构与读取流程见 [references/paper-reference.md](references/paper-reference.md)。

**权限：**
- ✅ 可修改：任务复选框、脚本/函数名、文件路径、代码块引用
- ⚠️ 用户授权后：实验目标措辞、验收标准、公式数值
- ❌ 不可修改：论文解读内容

**写前依赖检测铁律：**
1. **写 MATLAB 脚本前必须检测环境依赖**：运行 `ver` + `license('test',...)` 确认 toolbox 可用性。详见 [references/dependency-check.md](references/dependency-check.md)。
2. **依赖写入 CLAUDE.md**：检测结果记录到 `## MATLAB 环境检测` 段。
3. **缺失分级处理，不静谧绕过**：
   - 🔴 刚需 toolbox 缺失（如 Control System Toolbox）→ **阻断**，告知用户安装，不写绕过代码
   - 🟡 便利 toolbox 缺失（如 YALMIP/MOSEK）→ **建议安装**，同时提供降级方案供用户选择
   - 🟢 可选函数缺失（如 `chi2inv`）→ 自动使用 `utils/` 中的纯 MATLAB fallback

**实验设计铁律：**
1. **验收标准不预设精度**：实验运行前不写入具体数值。仅写"运行后报告实际精度"或"记录实际偏差与理论界对比"。
2. **目标写验证目的，非实现步骤**：实验目标写高层验证目的，实现步骤写入流程。
3. **目标显式引用项目目标编号**：格式 `目标 ：验证目标X.Y，<目标原文>`——写明验证的是 Note `# 目标` 中的哪个编号。

**方法落地铁律：**
1. **严格按论文方法实现**：实验脚本必须实现论文原文描述的方法，不得自创替代方法。论文方法在本系统上无法实施时，如实报告"无法实施"及原因（如"此拓扑无跨中心 $M_{ij}$ 连接，无可切断的交互链路"），结束实验。
2. **不自创替代方法**：论文方法在本系统上无法实施时，如实报告"无法实施"及原因，结束实验。不自创变通方案（如把切断内部 $M_{ij}$ 说成切断区域间交互、自创基线检测替代粗定位等）。替代方案 = 自创方法 = 造假。
3. **论文方法是唯一依据**：写脚本前先确认论文原文对方法的描述（哪一节、哪个表、哪段话）。脚本注释中引用论文原文作为方法出处。

**论文写作铁律：**
1. **术语来自原文**：任何术语必须在论文原文中有出处。原文未命名的量，直接用公式和变量符号指代，不自行命名。如论文中 $\Vert\Sigma_{r_\omega}^{-1/2} G_{z,\omega} \Psi_y\Vert$ 无名称，写作时直接写该表达式，不自创「DC 增益范数」等名称。
2. **符号与原文一致**：变量符号、矩阵名称与所引用论文完全相同。原文用 $G_{z,\omega}$ 就不写成 $G_f(I)$，即使含义相近。
3. **数值仅在运行后填入**：写作中所有具体数值（检出率、偏差值、门限值、回落比例等）必须来自实际运行结果。未运行的实验不留任何数值，写"运行后填入"。

---

## Phase routing

根据用户输入识别科研阶段：

| Phase | Trigger | Read | Invoke | AI action |
|---|---|---|---|---|
| Paper analysis | 读论文, 解读文献, literature review | 参考文献 | `pdf-converter`, `research`, `grilling` | 解读论文，找研究缺口。[论文目录结构 →](references/paper-reference.md) |
| Objective setting | 项目目标, 课题方向, research objective | Note | `grilling`, `writing-great-skills` | 基于论文提出研究目标 |
| Experiment design | 设计实验, 怎么验证, experiment design | Note + 参考文献 | `grilling`, `research`, `prototype`, `dataviz` | 设计实验验证目标。每个实验的目标字段引用 Note 目标编号。**遵守方法落地铁律**。实验通过后标记对应复选框 |
| Methodology | 怎么实现, 技术细节, method | 参考文献 | `codebase-design`, `tdd` | 技术解答，归属到论文章节。**写 MATLAB 代码前执行依赖检测** → [references/dependency-check.md](references/dependency-check.md)。**遵守方法落地铁律**。[代码格式化 →](references/scripts.md) |
| Architecture mapping | 项目架构, 文件结构 | Note | — | 映射研究流程到文件夹结构。[项目结构规范 →](references/project-structure.md) |
| Task planning | 今天做什么, 进度, plan | Note + Schedule | — | 读 Schedule 最新日期下未完成任务 → 读 Note `# 架构` 获取实施方案（函数、调用链、依赖）→ 实现 → 跑通后更新 Schedule 复选框，写 Note `## 实验报告`。复盘操作问题（通用→skill，本项目→CLAUDE.md），执行[任务完成同步 →](references/task-completion-sync.md) |
| Batch writing | 批量写脚本, fan-out, 并行编写, 同时写多个, 多个实验脚本 | Note + Schedule | — | 并行编写多个独立脚本。**遵守方法落地铁律**。**依赖检测→写→格式化→审查diff→跑** → [references/fan-out-writing.md](references/fan-out-writing.md) |
| Thesis writing | 写论文, 写tex, 写latex, 论文写作, thesis, chapter, 章节, 写仿真 | Note + 参考文献 | — | 框架优先：搭章节框架标注数据源→逐节提案讨论→用户确认后写tex→编译验证。**遵守论文写作铁律 + 方法落地铁律**。详见 [references/thesis-writing.md](references/thesis-writing.md) |

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

**五部分同步铁律**：目标(Note `# 目标`) ↔ 实验计划(Note `# 流程`) ↔ 实验报告(Note `## 实验报告`) ↔ 实验脚本(MATLAB) ↔ 项目日程表(Schedule)。**任一部分更新后必须检查其余四部分。**

详细同步清单与操作步骤 → [references/task-completion-sync.md](references/task-completion-sync.md)。完成后按 Output attribution 格式逐条报告更新。

## Project structure

新建项目默认结构 → [references/project-structure.md](references/project-structure.md)。已有项目初始化时扫描实际目录自动适配。
