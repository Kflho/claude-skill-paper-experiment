# claude-skill-paper-experiment

> 科研论文实验全流程管理 Skill —— 从论文解读、实验设计、MATLAB 实现、结果报告到论文写作，用「五文件工作流」把整个科研过程钉在 Obsidian vault 里。

一个 [Claude Code](https://claude.com/claude-code) skill，专为**「复现论文方法 → 设计仿真实验 → 跑出可信结果 → 写入论文」**这一完整科研闭环设计。AI 根据你的输入自动路由到科研阶段，全程遵守论文方法忠实落地、参数可溯源、数值只来自真实运行结果等铁律。

---

## 它能做什么

| 阶段 | 触发词 | AI 做什么 |
|---|---|---|
| **论文分析** | 读论文, 解读文献, literature review | 解读论文方法，确认每个公式的实现条件与边界 |
| **目标设定** | 项目目标, 课题方向 | 基于论文提出研究目标 |
| **实验设计** | 设计实验, 怎么验证 | 设计实验验证目标，产出函数清单 + 图表清单 |
| **代码架构** | 代码架构, 模块设计, 函数签名 | 设计文件结构、调用链、函数签名 |
| **原型验证** | 原型验证, prototype | 对高风险模块写 throwaway 代码验证可行性 |
| **实现** | 写脚本, 实现, implement | TDD 方式逐个实现实验，格式化→审查→跑通 |
| **代码审查** | 审查代码, review | 双轴审查（规范 + 逻辑）+ 消除冗余 |
| **任务规划** | 今天做什么, 进度 | 读日程→实现→同步五文件 |

核心承诺：**AI 只负责"胶水"，论文核心逻辑由你手写**——任何论文公式、算法、变换的实现都由你亲自把关，AI 绝不自创方法。

---

## 核心设计：五文件工作流

所有研究内容沉淀在 Obsidian vault 中的五个文件里，路径记录在项目 `CLAUDE.md`：

| 文件 | 内容 | 谁维护 |
|---|---|---|
| **Note** | 目标 → 流程 → 结论 | 你 |
| **src** | 代码架构、数据管线、设计决策、参数溯源 | 你 + AI |
| **report** | 每个实验一个报告块（日期/结论/参数/指标/备注） | AI 写入 |
| **参考文献** | 论文解读 + 方法论笔记 | 你 |
| **Schedule** | 每日任务 + 问题跟踪 | **你**（AI 只可勾选已有复选框） |

**五部分同步铁律**：目标 ↔ 实验计划 ↔ 实验报告 ↔ 实验脚本 ↔ 项目日程表，任一部分更新后必须检查其余部分。

AI 每条回复都标注目标文档和章节（如 `→ Project XX Note / 目标`），你直接复制粘贴到 Obsidian 即可。

---

## 安装

```bash
git clone https://github.com/Kflho/claude-skill-paper-experiment.git ~/.claude/skills/paper-experiment
```

### 依赖的子 skill

实验流程会调用以下子 skill（来自 [mattpocock/skills](https://github.com/mattpocock/skills)，缺失时对应阶段降级运行）：

```bash
git clone https://github.com/mattpocock/skills.git ~/.claude/skills/mattpocock
```

`grilling`（拷问实验设计）、`pdf-converter`（PDF→Markdown）、`research`（多源调研）、`prototype`（原型验证）、`tdd`（测试驱动实现）、`code-review` / `simplify`（审查）、`codebase-design`（接口设计）。

验证安装：

```bash
test -d ~/.claude/skills/paper-experiment && echo "[OK] paper-experiment"
test -d ~/.claude/skills/grilling && echo "[OK] grilling"
```

---

## 初始化

新项目首次使用时，告诉 AI「用 paper-experiment 初始化」，它会运行 9 步向导：

1. 告知五文件工作流原理
2. 收集三文件路径（Obsidian vault、论文文件夹、项目仓库）
3. 初始化 git + 写入 `.gitignore`
4. 扫描 MATLAB 项目结构，自动计算相对路径的 `addpath` 块
5. 检测 MATLAB 环境依赖（toolbox 三级分级）
6. 检测论文目录（PDF / Markdown 状态）
7. 生成项目 `CLAUDE.md`（含 Handoff 机制，`/clear` 后自动恢复上下文）
8. 完成，写入 `SKILL INITIALIZED: true` 标记

**绝不硬编码用户路径到 skill 文件**——所有路径只写入项目自己的 `CLAUDE.md`。

---

## 实验落地方案（5 步管线）

设计论文实验落地时，按固定顺序加载技能：

```
1. 实验设计  → grilling + research   → 产出函数清单（[手写]/[AI组装] 标注）
2. 代码架构  → codebase-design       → 文件结构、调用链、函数签名
3. 原型验证  → prototype             → 高风险模块可行性验证（按需触发）
4. 脚本实现  → tdd                   → 测试→实现→格式化→审查→跑通
5. 审查      → code-review + simplify → 规范检查 + 逻辑审查
```

发现问题的回路：格式问题直接修 → 脚本逻辑问题退步骤 4 → 架构问题退步骤 2 → 实验设计问题退步骤 1。

---

## 铁律一览

### 方法落地铁律
- **严格按论文方法实现**，不得自创替代方法；论文方法不可行时如实报告并结束实验
- 论文是唯一依据：变量、指标、术语必须在论文原文有定义，参数来自原文
- 实验直接验证论文的具体公式/定理/表，论文没有的分析角度不做

### 公式规格铁律
**规格 = 原文以公式/算法形式给出、必须逐字复现的结构。与参数溯源是两条轴：结构零自由度，取值可自选。**
- 公式从**原生载体**（PDF 公式层 / pptx-docx 的 OMML）逐字取；纯文本 `.md` 提取不含公式，**不得作为公式依据**（见 [公式载体](references/paper-reference.md#公式载体)）
- **禁止等价替换**：换损失函数/相似度/散度、把求和改成求均值、补门控补系数——看似等价的改写是偏离，不是实现细节
- 符号有定义而值未给 → 取值自由并记理由；符号**连定义都没有** → 留旋钮 + 非零即抛错 + 问原作者，不编定义顶上
- 任何"已对齐"都要附逐字引文 + 位置；溯源条目的出处与代码对不上就是**假账**，按缺陷处理

### 参数溯源铁律
每个数值标注来源，只能是三类之一：`论文 <章节>` / `由 <公式> 推导` / `经验选择：<理由>`（理由必须具体可验证）。脚本与 Note 数值必须一致。

### 核心计算铁律
- **论文逻辑由用户手写，胶水代码由 AI 组装**。判断标准：去掉论文，这个函数还需要存在吗？
  - 不需要 → `[手写]`：AI 不得实现
  - 需要 → `[AI组装]`：仿真循环、数据读写、可视化等

### 图片输出约束
- 只输出 **PNG**，禁止 `.fig`
- **中英双语输出**：`outputs/cn/` 与 `outputs/eng/` 各一份
- 标题严格单行，**参数入图例、标题留目标**（如 `±3σ=4.56e-16` 放图例，标题只写验证目标）
- 统一走 `run_visualization`，禁引入第三方绘图库

### MATLAB 依赖检测
写脚本前用 `exist('func','file')` 检测（**不用** `license('test',...)`——有许可证 ≠ 已安装），三级处理：

| 级别 | 缺失时 |
|---|---|
| 🔴 刚需（Control System Toolbox） | 阻断，告知安装，不写绕过代码 |
| 🟡 便利（YALMIP/MOSEK） | 建议安装 + 提供降级方案 |
| 🟢 可选（`chi2inv` 等） | 自动用 `utils/` 纯 MATLAB fallback |

### Git 备份铁律
任何批量编辑、脚本修改、破坏性操作前，必须 `git add -A && git commit` 备份当前状态。绝不裸奔。

### Schedule 只读铁律
AI 只能勾选/取消已有复选框，禁止新增/编辑任何文字（日期章节、任务条目、修复备注等）。

---

## 项目结构约定

```
utils/                           # 跨项目共享代码
projects/
  [category]/
    project_xx_descriptor/
      src/
        lib/                     # 项目内部函数（不可独立运行）
        scripts/                 # 可复用脚本
        tests/                   # 单元测试
        main/                    # 实验入口
      outputs/
        cn/experiment_XX_descriptor/{figures,data}/
        eng/experiment_XX_descriptor/{figures,data}/
```

- **所有路径必须用相对路径**，禁止硬编码绝对路径，保证项目可移植
- 命名：全小写 snake_case、禁止数字开头、`.m` 文件名 = 主函数名

---

## 附带脚本

| 脚本 | 作用 |
|---|---|
| `fix_m_code.py` | MATLAB 代码大小写规范化（保护矩阵变量/缩写/人名/LaTeX），dry-run + `--apply`（自动 `.bak` 备份） |
| `fmt.py` | 中英文数字间距修复（中文↔数字无空格、英文↔数字加空格） |
| `normalize_vault.py` | Obsidian vault 文件夹与 `.md` 文件名全小写化，同步更新 wikilink 引用 |
| `lowercase_vault.py` | vault 文档内容全小写化（保护代码块/LaTeX/URL/链接） |
| `rename_attachments.py` | `Attachments/` → `attachments/` 并更新路径引用 |

**强制工作流**（详见 [references/scripts.md](references/scripts.md)）：写 `.m` → `--diff` → **有罪推定**逐 hunk 判定误改/正确规范 → 修正（误改的词进项目词表 `.fix_m_code_protect`）→ `--apply` → 删除 `.bak` → 再跑。

---

## 论文写作衔接

仿真跑完后，可无缝衔接 LaTeX 论文写作（见 `references/thesis-writing.md`）：

- 实验报告 → 直接写入 Obsidian；LaTeX `.tex` → **必须用户确认后写入**
- 框架优先：先贴章节骨架给用户审阅，逐节讨论确认后才写入
- **所有数值必须来自实验报告**，禁止从论文照抄、禁止编造
- 中文论文引用中文图片（`results/cn/`），英文论文引用英文图片（`results/eng/`）

---

## 目录结构

```
paper-experiment/
├── SKILL.md                  # 主文件：阶段路由 + 全部铁律
├── references/               # 按需加载的参考文档
│   ├── first-run.md          # 初始化向导（9 步）
│   ├── setup.md              # 环境设置
│   ├── project-structure.md  # 项目结构规范
│   ├── format.md             # Obsidian 格式规范
│   ├── dependency-check.md   # MATLAB 依赖检测
│   ├── paper-reference.md    # 论文目录读取流程
│   ├── task-completion-sync.md # 五部分同步清单
│   ├── thesis-writing.md     # LaTeX 论文写作工作流
│   └── fan-out-writing.md    # 多脚本并行编写
├── scripts/                  # Python 格式化脚本
├── templates/                # CLAUDE.md 模板
└── .claude/settings.local.json
```

---

## License

仅供个人科研使用。所有实验数据与论文内容归项目所有者所有，本 skill 只提供流程规范。
