# Fan-out Writing

> 并行编写多个独立脚本的工作流。一次准备，N 个 agent 同时写，主线程零 token 增量。

## Decision gate

在 fan-out 前判断：这些脚本能并行吗？

**可并行**（三个条件全部满足）：
1. 写入不同文件（无写冲突）
2. 共享依赖只读（lib 函数、参数脚本、数据文件）
3. 无运行时数据依赖（脚本 A 的输出不是脚本 B 的输入）

**不可并行** → 串行编写。脚本 B 依赖脚本 A 的输出 → 先写 A，A 跑通后再写 B。

## Phase 1: Scan

**做什么**：扫描项目依赖目录，提取所有可调用函数/脚本的签名，生成 API 速查表。

**谁做**：1 个只读 Explore agent。

**Prompt template**：

```
Very thoroughly scan these directories and extract the function signature
(function name, inputs, outputs) of EVERY source file:

[List each dependency directory with absolute paths]

For each function, report:
- Function name
- Full signature line
- 1-sentence summary of what it does

Also note scripts (files without function definitions) separately.

Output format: a clean reference table, no narrative.
```

**Completion criterion**：速查表覆盖所有依赖目录，每个文件一条记录，签名完整。

**额外读取**：
- 读取一个已有同类脚本作为风格模板（如已有的实验脚本）
- 读取 Schedule 中每个目标脚本的任务描述

## Phase 2: Dispatch

**做什么**：为每个目标脚本启动 1 个 general-purpose agent，全部并行。

**谁做**：主线程组装 prompt，N 个 agent 并行。

**Prompt template**（每个 agent）：

```
Write a complete [language] script `[relative/path/to/script.ext]` for the project at:
[absolute project root]

## TASK FROM SCHEDULE
[粘贴 Schedule 中该脚本的完整任务描述，含目标、流程、验收标准]

## AVAILABLE API
[粘贴 Phase 1 的 API 速查表]

## DEPENDENCY SCRIPTS
[列出该脚本需要调用的其他脚本及其作用，1 行 1 个]

## PROJECT CONVENTIONS
[粘贴项目 CLAUDE.md 中的路径规范、命名规范、addpath 块]

## REFERENCE TEMPLATE
[粘贴已有同类脚本的完整内容或关键结构段落]

## IMPLEMENTATION GUIDANCE
[具体实现步骤，1 步 1 条，来自 Schedule 流程描述]
- 使用与参考模板相同的 coding style（注释密度、section 分隔、fprintf 详细程度）
- 脚本需 production-ready，不是 stub

Write ONLY the file [path]. Do NOT modify any existing files.
```

**Completion criterion**：每个脚本文件存在且语法可解析（用语言工具检查，如 `matlab -batch` 或 `python -m py_compile`）。

**Agent 数**：N = 目标脚本数。若 N > 4，分批（每批 ≤4 个），避免 agent 间上下文干扰。

## Phase 3: Review & Format

### 3a. 逻辑审查

**做什么**：审查所有产出脚本的一致性和正确性。

**谁做**：1 个 general-purpose agent。

**Prompt template**：

```
Review these [N] scripts for consistency and correctness:

[List each script path]

Check:
1. **Consistency**: Do they use the same addpath block, same output directory pattern,
   same variable naming? Flag any divergence.
2. **Correctness**: Does each script match its task description?
   [粘贴 Schedule 中对应任务]
3. **Completeness**: Are all验收标准 covered? Any missing sections?
4. **API usage**: Do all function calls match the actual signatures?
   [粘贴 API 速查表]

Report findings as a table: script | issue | severity.
Fix minor issues (typos, path errors) directly.
Flag major issues (missing logic, wrong algorithm) for manual review.
```

**Completion criterion**：审查报告产出，所有 minor issues 已修复。

### 3b. 格式化（AI 审查 diff）

**做什么**：运行代码格式化工具，AI 审查前后 diff，纠正误改。

**步骤**：
1. `cp script.m script.m.bak` — 备份
2. 运行格式化工具（如 `fix_m_code.py --apply`）
3. `diff script.m.bak script.m` — 生成 diff
4. **AI 审查 diff**，逐条判断每条变更属于以下哪类：

   **🔴 外部 API 边界 — 必须还原**
   属性/字段访问的大小写由外部 API 决定，格式化器不知道上下文：
   - `sim_w.Data` → `sim_w.data`（Simulink timeseries 属性名是 `Data`，大写 D）
   - 任何 `identifier.Property` 或 `struct.field` 中的 Property/field → 还原

   **🟡 命名冲突暴露 — 改变量名，不还原格式**
   格式化器正确应用了 snake_case，但暴露了原代码中靠大小写区分的坏名字：
   - `Omega = 2` + `for omega = 1:Omega` → 格式化后两者都是 `omega`，循环失效
   - **不还原 `Omega`**，而是重命名变量：`Omega` → `n_omega`
   - 判断标准：变量是不是矩阵？不是 → 该小写。冲突了 → 改名字，不改规则。

   **🟢 注释中专有名词 — 保留原样**
   统计/数学专有名词在注释中应保持约定俗成的写法：
   - Hotelling's `T²` → 还原为 `T²`（非 `t²`）
   - 但能用 LaTeX 就用 LaTeX：`$J_{T^2}$` 优于 `J_T²`

5. AI 根据分类处理：🔴 用 Edit 还原，🟡 改变量名（可能涉及多个文件），🟢 还原专有名词
6. `rm script.m.bak` — 清理备份
7. 对每个脚本重复

**为什么不用 AI 直接格式化**：格式化规则复杂（大小写、缩写、矩阵变量、人名），AI 容易漏改或过度改。规则引擎一次性覆盖所有模式，AI 只做 diff 级别的判断——精确且可审计。

**Completion criterion**：所有脚本 diff 已审查，误改已纠正，.bak 已清理。

## Anti-patterns

- **跳过 Phase 1**：不扫描 API 就直接让 agent 写 → agent 编造不存在的函数签名 → 运行时报错。
- **Prompt 太短**：只给任务描述不给 API 速查表和模板 → 每个 agent 各自搜索依赖 → 重复阅读、token 浪费、风格不一致。
- **fan-out 有依赖的脚本**：脚本 B 需要脚本 A 的输出 → agent B 猜测 A 的输出格式 → 接口不匹配。有依赖就串行。
- **一个 agent 写多个脚本**：agent 注意力分散，第二个脚本质量下降。一个 agent 一个脚本。
- **跳过 Phase 3b diff 审查**：直接信任格式化器输出 → `sim_w.Data` 变 `sim_w.data` 运行时报错。规则引擎无上下文，必须 AI 过一遍 diff。
- **还原格式化器的正确修改**：遇到 `Omega`→`omega` 冲突，不去改变量名而是保护 `Omega` → 变相鼓励不规范的命名。格式化器是对的，改变量名。
