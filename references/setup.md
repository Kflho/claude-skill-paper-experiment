# 环境设置

> 首次使用或更换环境时执行。已验证过的项目跳过。

## 推荐安装 mattpocock/skills

此 skill 依赖以下子 skill，推荐从 [mattpocock/skills](https://github.com/mattpocock/skills) 安装：

```bash
git clone https://github.com/mattpocock/skills.git ~/.claude/skills/mattpocock
```

| Skill | 用途 | 科研阶段 |
|---|---|---|
| `writing-great-skills` | 写/改 skill 的规范参考 | 所有阶段 |
| `grilling` | 压力测试研究方案和实验设计 | 目标设定、实验设计 |
| `pdf-converter` | PDF 论文转 markdown | 论文分析 |
| `research` | 多源调研、背景搜索 | 论文分析、实验设计 |
| `prototype` | 快速原型验证想法 | 实验设计 |
| `dataviz` | 实验数据可视化 | 实验执行 |
| `tdd` | 测试驱动开发实验代码 | 方法论/实现 |
| `code-review` | 代码审查 | 方法论/实现 |
| `diagnosing-bugs` | 调试实验代码 | 方法论/实现 |
| `codebase-design` | 模块接口设计 | 架构映射 |

## 验证

```bash
# 确认关键 skill 已安装
test -d ~/.claude/skills/writing-great-skills && echo "[OK] writing-great-skills" || echo "[MISSING] writing-great-skills — clone mattpocock/skills"
test -d ~/.claude/skills/grilling && echo "[OK] grilling" || echo "[MISSING] grilling — clone mattpocock/skills"
test -d ~/.claude/skills/pdf-converter && echo "[OK] pdf-converter" || echo "[MISSING] pdf-converter"
```

有 `[MISSING]` → 告知用户安装。缺失的 skill 不影响核心工作流，对应阶段会降级运行。

## Git 备份（铁律）

**每次运行会修改文件的脚本前（批量实验、代码重构），必须 git commit 备份。**

```bash
cd "<project-repo>"
git add -A && git commit -m "备份：<操作>前 — $(date +%Y-%m-%d)"
```

> 如果项目目录还不是 git repo，先 `git init` + `git add -A` + `git commit`。
> 实验代码迭代快、产出多，git 是唯一保险——没有撤销按钮。
> 参考字幕校对 skill 的做法：pipeline 原地覆写文件，不可逆。

## Obsidian 配置

确保 Obsidian vault 路径已知。skill 通过项目 CLAUDE.md 中的 `## Scientific Research Paths` 读取五文件路径，不会直接写入 vault。

## MATLAB 配置（如适用）

```bash
# 验证 MATLAB 可用
matlab -batch "disp('[OK] MATLAB'); exit" 2>/dev/null || echo "[MISSING] MATLAB"
```

MATLAB 不可用时仍可使用 skill 进行论文分析、实验设计等非代码工作。
