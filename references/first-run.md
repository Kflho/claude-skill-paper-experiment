# 初始化向导

> Claude：此文件是首次初始化时执行的步骤脚本。
> 触发条件：项目 CLAUDE.md 不存在或不含 `SKILL INITIALIZED: true`。
> 完成后写入 CLAUDE.md，末尾加 `SKILL INITIALIZED: true` 标记。

---

## Step 1：告知流程和原理

向用户说明：

> 科研 skill 基于**三文件工作流**管理你的研究：
>
> | 文件 | 内容 | 谁维护 |
> |------|------|--------|
> | **Project XX Note** | 目标、流程、架构、问题记录 | 你 |
> | **Project XX 参考文献** | 论文解读与方法论笔记 | 你 |
> | **Project XX Schedule** | 每日任务进度（`# MM.DD` 格式） | 你 |
>
> AI **只读不写**这三个文件。每次回复会标注目标文档和章节（如 **→ Project XX Note / 目标**），你直接复制粘贴到 Obsidian。
>
> 科研流程分六个阶段：论文分析 → 目标设定 → 实验设计 → 方法论 → 架构映射 → 任务规划。AI 根据你的输入自动路由到对应阶段。

---

## Step 2：收集三文件路径

向用户提问：

> 请提供以下信息：
>
> | # | 路径项 | 用途 | 是否必需 |
> |---|--------|------|:---:|
> | 1 | **Obsidian vault 路径** | vault 根目录 | ✅ 必需 |
> | 2 | **项目名称** | 如 `Project 01`、`课题_xxx` | ✅ 必需 |
>
> 你的三文件叫什么名字？（默认：`{项目名} Note.md`、`{项目名} 参考文献.md`、`{项目名} Schedule.md`）
>
> - 用默认命名 → 直接确认
> - 自定义名称 → 逐个告诉我

从 vault + 项目名推导路径，确认：

> 推导的路径如下：
>
> - Note: `{vault}/{项目名} Note.md`
> - 参考文献: `{vault}/{项目名} 参考文献.md`
> - Schedule: `{vault}/{项目名} Schedule.md`
>
> 这些路径对吗？

允许逐文件修正。对缺失的文件：

> `{filename}` 不存在。要我现在创建模板骨架吗？（y/n）
>
> - **y** → 创建含默认 H1 的文件（Note=`# 目标`，参考文献=`# 论文解读`，Schedule=`# MM.DD`）
> - **n** → 记录路径，标注 `(pending)`

---

## Step 3：Git 版本管理

### 3.1 检测 git 状态

```bash
cd "<repo>" && git rev-parse --git-dir 2>/dev/null && echo "is_repo" || echo "not_repo"
```

### 3.2 情况 A：已是 git 仓库

> 检测到项目已是 git 仓库。当前分支：`<branch>`，最近提交：`<last_commit_msg>`。

确认 git 用户配置：

```bash
git config user.name && git config user.email
```

未配置时提醒用户设置。

### 3.3 情况 B：不是 git 仓库

> ⚠️ 项目目录还不是 git 仓库。**强烈建议初始化**：
>
> ```bash
> cd "<repo>"
> git init
> git add -A
> git commit -m "初始化：<项目名> 科研项目"
> ```
>
> 科研项目需要版本管理的原因：
> - 实验代码迭代快，出问题时需要回滚
> - `skill-activator` 修改 `skill-rules.json` 前可备份
> - 批量实验产出大量数据，git 追踪代码、`.gitignore` 排除数据
>
> 是否现在初始化 git？（y/n）

**如果选 y** → 执行 `git init` + `git add -A` + `git commit`。

**如果选 n** → 跳过。后续警告用户：修改代码前先备份。

### 3.4 写入 .gitignore

如果是 MATLAB 项目或已检测到项目类型，写入对应的 `.gitignore`。如果已有 `.gitignore`，追加缺失的模式而非覆盖。

MATLAB 项目模板：

```gitignore
# MATLAB
*.m~
*.mat
*.fig
*.mex*
*.slxc
*.slx.autosave
slprj/
__pycache__/
*.pyc

# 实验产出（数据大，不追踪）
Output/

# Obsidian（不在代码仓内）
.obsidian/
```

### 3.5 Git 备份铁律

> **铁律**：运行会修改文件的脚本前（批量实验、代码重构、skill-activator 修改），必须 git 备份：
>
> ```bash
> git add -A && git commit -m "备份：<操作>前 — $(date +%Y-%m-%d)"
> ```
>
> 参考字幕校对 skill 的做法——pipeline 原地覆写文件，不可逆，git 是唯一保险。

写入 CLAUDE.md 的 git 段。

---

## Step 4：收集项目仓库路径与计算 MATLAB 路径深度

向用户提问：

> 你的项目代码在哪个目录？
>
> 不确定可以留空，后续在 CLAUDE.md 中手动补充。

如果用户提供路径，验证目录存在。检测项目类型：

```bash
# 自动检测
test -d "<repo>/Function" && test -d "<repo>/Script" && echo "[MATLAB project]"
test -f "<repo>/pyproject.toml" && echo "[Python project]"
```

### 4.1 MATLAB 项目：计算 Common 路径深度

**关键**：不要写死 `../../` 层数。每个项目的 Script/ 到仓库根的距离不同。

计算方法：

1. 确定两个绝对路径：`<project>/Script/` 和 `<repo_root>/`（即 Common/ 的父目录）
2. 计算从 Script/ 回到 repo_root 需要几层 `../`
3. 把结果写入项目 CLAUDE.md 的路径添加段

示例：若项目在 `<repo_root>/Project/Postgraduate/Project_01/`：

```
Script/ 绝对路径:  <repo_root>/Project/Postgraduate/Project_01/Script/
回到 <repo_root>:  ../  → Project_01/
                   ../../  → Postgraduate/
                   ../../../  → Project/
                   ../../../../  → <repo_root>/
需要: ../../../../Common/
```

生成的 addpath 行：

```matlab
addpath(genpath('../../../../Common/'));   % 4 层 — 由初始化计算得出
addpath(genpath('../Function/'));
addpath(genpath('../Script/'));
```

若项目直接在 `<repo_root>/Project/Project_XX/`（无 Category 层），则为 `../../../Common/`。**每次初始化都重新计算，不要照搬其他项目的数字。**

---

## Step 5：论文目录检测

检查项目仓库下 `参考文献/` 目录：

```bash
ls "<repo>/参考文献/" 2>/dev/null
```

根据结果分支：

**情况 A：已有论文子文件夹 + markdown** → 直接记录，告知用户：

> 检测到已转换的论文：
> - `<Paper Title>/paper_full.md`

**情况 B：只有 PDF** → 告知用户：

> 检测到 `<N>` 个 PDF 文件，尚未转换为 markdown。初始化完成后告诉 AI "读这篇论文" 即可自动调用 `pdf-converter` 转换。

**情况 C：目录不存在** → 告知用户：

> 未检测到 `参考文献/` 目录。当你放入论文 PDF 后，告诉 AI "读这篇论文"，会自动调用 `pdf-converter` 创建同名文件夹并转为 markdown。

---

## Step 6：配置 skill-activator 规则

向用户说明：

> 科研工作流需要在 `~/.claude/skill-rules.json` 中注册自动激活规则，这样输入"设计实验"时会自动触发相关 skill。

已存在的规则不再添加。只追加缺失项。

**核心科研 skill**（始终推荐）：

| Skill | 触发场景 |
|-------|----------|
| `scientific-research` | 论文/文献/实验设计/课题/方法论/科研流程 |
| `pdf-converter` | PDF/论文转换/读论文/提取内容 |
| `writing-great-skills` | 写 skill/修改 skill/更新 skill |

**阶段相关 skill**（推荐）：

| Skill | 触发场景 |
|-------|----------|
| `grilling` | 方案评估/压力测试/trade-off/敲定方向 |
| `research` | 调研/查资料/搜索信息 |
| `prototype` | 原型/快速验证/sanity check |
| `dataviz` | 图表/可视化/绘图/dashboard |
| `tdd` | 测试驱动/写测试/单元测试 |
| `code-review` | 代码审查/审查变更 |
| `diagnosing-bugs` | bug/报错/异常/崩溃/诊断 |
| `codebase-design` | 设计/架构/重构/接口设计 |
| `git-guardrails-claude-code` | git push/reset --hard/force push 等危险操作 |

> 是否全部添加？（y/n）**推荐 y**。
>
> - **y** → 自动补全所有缺失规则
> - **n** → 只补核心三项（scientific-research, pdf-converter, writing-great-skills）
> - **逐个选择** → 我列出每项，你逐条确认

写入 `skill-rules.json` 后验证 JSON 有效：

```bash
python -c "import json; json.load(open('$HOME/.claude/skill-rules.json', encoding='utf-8')); print('Valid JSON')"
```

> ⚠️ 修改前自动 git 备份 `skill-rules.json`（如果 `~/.claude/` 是 git 仓库）。
> ⚠️ 绝不覆盖用户已有的规则。只追加缺失项。

---

## Step 7：推荐安装 mattpocock/skills

检测 `writing-great-skills` 是否已安装：

```bash
test -d ~/.claude/skills/writing-great-skills && echo "installed" || echo "missing"
```

**如果缺失**：

> 推荐安装 [mattpocock/skills](https://github.com/mattpocock/skills)：
>
> ```bash
> git clone https://github.com/mattpocock/skills.git ~/.agents/skills
> ```
>
> 这个仓库包含科研常用的 skill（`writing-great-skills`、`grilling`、`prototype` 等）。不装也能用，但对应 skill 缺失时阶段会降级。

**如果已安装** → 跳过。

---

## Step 8：生成 CLAUDE.md

读取 `templates/CLAUDE-template.md`，将用户的回答填入占位符。

**绝不硬编码任何用户路径到 skill 文件。所有路径只写入项目的 CLAUDE.md。**

如果项目已有 CLAUDE.md → 只更新 `## Scientific Research Paths` 和 `## Git` 段，保留其他内容。无冲突时追加新段，不覆盖已有。

---

## Step 9：完成

告知用户初始化完成，摘要配置：

> 初始化完成！配置摘要：
>
> - 项目: <name>
> - Note: <path>
> - 参考文献: <path>
> - Schedule: <path>
> - 仓库: <repo>
> - Git: <已初始化/已是仓库/已跳过>
> - 论文目录: <有/无>
> - skill-activator: <N 条规则已添加/已跳过>
>
> 下次运行 skill 时将直接进入科研工作流。如需重新初始化，删除 CLAUDE.md 中的 `SKILL INITIALIZED: true` 行即可。

写入 CLAUDE.md 末尾：`## SKILL INITIALIZED: true`
