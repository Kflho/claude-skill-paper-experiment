# Fan-out Writing

> 并行编写多个独立脚本的工作流。一次准备，N 个 agent 同时写，主线程零 token 增量。
>
> **铁律：写 → 格式化 → 审查 diff → 跑。** 格式化必须在跑之前完成，否则格式化器改坏的 API 属性名（如 `sim_w.Data` → `sim_w.data`）会导致运行时错误。

## Decision gate

在 fan-out 前判断：这些脚本能并行吗？

**可并行**（三个条件全部满足）：
1. 写入不同文件（无写冲突）
2. 共享依赖只读（lib 函数、参数脚本、数据文件）
3. 无运行时数据依赖（脚本 A 的输出不是脚本 B 的输入）

**不可并行** → 串行编写。脚本 B 依赖脚本 A 的输出 → 先写 A，A 跑通后再写 B。

## Phase 1: Scan

**做什么**：扫描项目依赖目录，提取所有可调用函数/脚本的签名，生成 API 速查表。**同时检测 MATLAB 环境依赖。**

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
- Toolbox dependency (if any) — check against the function→toolbox mapping in
  references/dependency-check.md

Also note scripts (files without function definitions) separately.

ALSO run these MATLAB commands and report the output:
  1. `ver` — list all actually installed toolboxes
  2. `exist('chi2inv', 'file')` — check chi2inv actually installed (0=NO)
  3. `exist('dlyap', 'file')` — check dlyap actually installed (0=NO)
  4. `exist('ss', 'file')` — check ss (Control System) actually installed (0=NO)
  5. `exist('lqr', 'file')` — check lqr (Control System) actually installed (0=NO)
  6. `exist('sdpvar', 'file')` — check YALMIP actually installed (0=NO)
  7. `exist('mosekopt', 'file')` — check MOSEK actually installed (0=NO)

  IMPORTANT: Use `exist('func', 'file')` NOT `license('test',...)`.
  `license` only checks license file, NOT actual installation.
  `exist` returns 0 if function is NOT on MATLAB path — that's the only reliable check.

For each function in the API table, cross-reference its toolbox requirement
against the installed toolboxes. Flag any function whose toolbox is NOT available.
Classify each missing dependency as:
  - 🔴 刚需（必须安装）— core functions like dlyap, ss, lqr
  - 🟡 便利（建议安装）— YALMIP, MOSEK
  - 🟢 可选（自动 fallback）— chi2inv, chi2cdf

Output format: a clean reference table (functions) + a toolbox availability table,
no narrative.
```

**Completion criterion**：速查表覆盖所有依赖目录，每个文件一条记录，签名完整。Toolbox 可用性表完整，缺失依赖已按 🔴🟡🟢 分级标注。

**额外读取**：
- 读取项目 CLAUDE.md 的 `## MATLAB 环境检测` 段（若存在），更新检测结果
- 读取一个已有同类脚本作为风格模板（如已有的实验脚本）
- 读取 Schedule 中每个目标脚本的任务描述

## Phase 2: Dispatch + Format

**做什么**：为每个目标脚本启动 1 个 general-purpose agent 并行编写，写完后立即格式化并审查 diff。

**谁做**：主线程组装 prompt，N 个 agent 并行；主线程在 agent 返回后立即对每个产出文件执行格式化+diff 审查。

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
- **外部 API 属性名**：Simulink timeseries 等外部对象的属性名必须保持官方大小写（如 `sim_w.Data` 非 `sim_w.data`）。所有 `.` 右侧的属性名，若来自外部 API 而非自定义结构体，不得 smallcaps 化。详见 format.md → Case conventions → 外部 API 属性名。
- **Toolbox 约束**（根据 Phase 1 检测结果）：
  - 🔴 刚需 toolbox 缺失 → 脚本开头插入 `error('请安装 XXX Toolbox: <说明与安装指引>')`，**不写绕过代码**。告知用户阻断原因。
  - 🟡 便利 toolbox 缺失 → 优先写降级方案（如 DARE 回退），注释中标注 `% TODO: 安装 XXX 后可用更优方案`。告知用户安装建议和降级代价。
  - 🟢 可选函数缺失 → 自动替换为 `utils/` 中的 fallback 函数，无需告知。

Write ONLY the file [path]. Do NOT modify any existing files.
```

**Agent 返回后，主线程立即对每个产出文件执行格式化**：

```
对每个新写的脚本：
  1. cp script.m script.m.bak — 备份
  2. python fix_m_code.py script.m --apply — 格式化
  3. diff script.m.bak script.m — 生成 diff
  4. AI 审查 diff，分类处理：
     🔴 外部 API 属性名被改 → 还原（如 sim_w.data → sim_w.Data）
     🟡 命名冲突暴露 → 改变量名（如 Omega → n_omega），不还原格式
     🟢 注释专有名词被改 → 还原（如 t² → T²，model 1 → Model 1）
  5. rm script.m.bak — 清理
```

**Completion criterion**：每个脚本文件存在、格式化完成、diff 已审查、误改已纠正、.bak 已清理。

**Agent 数**：N = 目标脚本数。若 N > 4，分批（每批 ≤4 个），避免 agent 间上下文干扰。

## Phase 3: Review

**做什么**：审查所有产出脚本的一致性和正确性（格式化已在 Phase 2 完成，此处只审逻辑）。

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

## Anti-patterns

- **跳过依赖检测**：不先检查 MATLAB toolbox 可用性就让 agent 写 → agent 写出依赖 `dlyap`/`chi2inv` 的代码 → 用户跑的时候才发现报错。**铁律：Phase 1 必须包含 `ver` + `license('test',...)` 检测。**
- **静谧绕过刚需依赖**：Control System Toolbox 缺失时默默写手动 Lyapunov 求解 → 数值不稳定、科研不可接受。🔴 级缺失必须告知用户安装，不在脚本中绕过。
- **Prompt 太短**：只给任务描述不给 API 速查表和模板 → 每个 agent 各自搜索依赖 → 重复阅读、token 浪费、风格不一致。
- **fan-out 有依赖的脚本**：脚本 B 需要脚本 A 的输出 → agent B 猜测 A 的输出格式 → 接口不匹配。有依赖就串行。
- **一个 agent 写多个脚本**：agent 注意力分散，第二个脚本质量下降。一个 agent 一个脚本。
- **写完不格式化直接跑**：跳过 Phase 2 的格式化步骤 → `sim_w.Data` 变 `sim_w.data` 运行时报错。规则引擎无上下文，必须 AI 过一遍 diff 再跑。
- **跳过格式化 diff 审查**：直接信任格式化器输出而不审查 diff → 外部 API 属性名被改残。格式化 → diff → AI 分类（🔴/🟡/🟢）→ 修正，四步缺一不可。
- **还原格式化器的正确修改**：遇到 `Omega`→`omega` 冲突，不去改变量名而是保护 `Omega` → 变相鼓励不规范的命名。格式化器是对的，改变量名。
