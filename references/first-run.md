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
> | 3 | **论文文件夹路径** | 存放论文 PDF/markdown 的外部目录 | ✅ 必需 |
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
> - 论文文件夹: `<用户提供的路径>`
>
> 这些路径对吗？

允许逐文件修正。对缺失的文件：

> `{filename}` 不存在。要我现在创建模板骨架吗？（y/n）
>
> - **y** → 创建含默认 H1 的文件（Note=`# 目标`，参考文献=`# 论文解读`，Schedule=`# MM.DD`）
> - **n** → 记录路径，标注 `(pending)`

论文文件夹不存在时：

> 论文文件夹 `<path>` 不存在。要我现在创建吗？（y/n）
>
> - **y** → `mkdir -p <path>`
> - **n** → 记录路径，标注 `(pending)`。后续放入论文 PDF 后告诉 AI "读这篇论文" 即可。

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
outputs/

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
> 详细规则见 [setup.md](setup.md)。参考字幕校对 skill 的做法——pipeline 原地覆写文件，不可逆，git 是唯一保险。

写入 CLAUDE.md 的 git 段。

---

## Step 4：收集项目根目录并自动扫描 MATLAB 路径

向用户提问：

> 你的项目根目录在哪里？——即包含所有代码依赖的顶层目录。
>
> （例如 `D:/Data/.../Matlab/`，其下有 `utils/`、`projects/` 等）
>
> 不确定可以留空，后续在 CLAUDE.md 中手动补充。

### 4.1 扫描所有含 .m 的文件夹

拿到根目录后，扫描其下所有包含 `.m` 文件的文件夹（排除 `.git/`、`.Old/`、`Output/`、`outputs/`、`node_modules/` 等）：

```bash
find "<root>" -name "*.m" -not -path "*/.git/*" -not -path "*/.Old/*" \
  -not -path "*/Output/*" -not -path "*/outputs/*" | sed 's|/[^/]*\.m$||' | sort -u
```

这会得到类似：
```
<root>/utils/calculations
<root>/utils/visualizations
<root>/projects/postgraduate/project_01/src/lib
<root>/projects/postgraduate/project_01/src/scripts
<root>/projects/postgraduate/project_01/src/tests
<root>/projects/postgraduate/project_01/src/main
```

### 4.2 确定项目工作目录

向用户确认：

> 你的实验代码（main、scripts）从哪个项目目录运行？
>
> 默认是当前工作目录。如果扫描到多个项目，让用户选一个。

### 4.3 计算所有 addpath 行

对 4.1 得到的每个目录，计算从 4.2 的项目工作目录出发的相对路径，生成完整的 `addpath` 列表。**不预设目录名**——`utils/`、`src/lib/`、`src/scripts/` 都只是用户碰巧用的名字，不是规则。

**为什么必须用相对路径**：硬编码绝对路径（如 `D:\data\...`）会导致项目根目录移动后所有脚本失效。相对路径保证整个文件夹移到任意位置均可正常运行。

计算逻辑：
1. 项目工作目录绝对路径 = `<project_dir>/src/scripts/`（或用户指定的入口目录）
2. 对每个含 `.m` 的目录，计算 `relpath(project_dir, target_dir)` → `../` 层数 + 子路径
3. 用 `genpath` 包裹以递归包含子目录

生成的 addpath 块示例：

```matlab
addpath(genpath('<../到 utils 的层数>/utils/'));
addpath(genpath('../src/lib/'));
addpath(genpath('../src/scripts/'));
```

### 4.4 写入项目 CLAUDE.md

将生成的 addpath 块写入 CLAUDE.md 的 `## 路径添加（MATLAB）` 段，每行加注释标注该目录的角色（共享库 / 项目函数 / 项目脚本 / ...），注释由 Claude 根据目录名推断，不做硬性分类。

---

## Step 5：论文目录检测

检查用户在 Step 2 提供的论文文件夹路径：

```bash
ls "<用户提供的论文文件夹路径>/" 2>/dev/null
```

根据结果分支：

**情况 A：已有论文子文件夹 + markdown** → 直接记录，告知用户：

> 检测到已转换的论文：
> - `<Paper Title>/paper_full.md`

**情况 B：只有 PDF** → 告知用户：

> 检测到 `<N>` 个 PDF 文件，尚未转换为 markdown。初始化完成后告诉 AI "读这篇论文" 即可自动调用 `pdf-converter` 转换。

**情况 C：目录为空** → 告知用户：

> 论文文件夹为空。当你放入论文 PDF 后，告诉 AI "读这篇论文"，会自动调用 `pdf-converter` 创建同名文件夹并转为 markdown。

---

## Step 6：推荐安装 mattpocock/skills

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

## Step 7：生成 CLAUDE.md

读取 `templates/CLAUDE-template.md`，将用户的回答填入占位符。

**绝不硬编码任何用户路径到 skill 文件。所有路径只写入项目的 CLAUDE.md。**

如果项目已有 CLAUDE.md → 只更新 `## Scientific Research Paths` 和 `## Git` 段，保留其他内容。无冲突时追加新段，不覆盖已有。

---

## Step 8：完成

告知用户初始化完成，摘要配置：

> 初始化完成！配置摘要：
>
> - 项目: <name>
> - Note: <path>
> - 参考文献: <path>
> - Schedule: <path>
> - 论文文件夹: <path>
> - 仓库: <repo>
> - Git: <已初始化/已是仓库/已跳过>
> - 论文目录: <有/无>
>
> 下次运行 skill 时将直接进入科研工作流。如需重新初始化，删除 CLAUDE.md 中的 `SKILL INITIALIZED: true` 行即可。

写入 CLAUDE.md 末尾：`## SKILL INITIALIZED: true`
