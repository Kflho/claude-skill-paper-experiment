# Scientific Research — Claude Code Skill

[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-6C4DFF)](https://claude.com/claude-code)

让 AI 管理你的科研工作流：**论文分析 → 目标设定 → 实验设计 → 方法论 → 架构映射 → 任务规划**。

## 怎么用

```bash
# 1. 克隆到 Claude Code skills 目录
git clone <your-repo-url> ~/.claude/skills/scientific-research

# 2. （推荐）安装依赖 skill
git clone https://github.com/mattpocock/skills.git ~/.agents/skills

# 3. 在 Claude Code 对话中输入
/scientific-research

# 4. 跟随内置初始化向导，告诉 AI 你的 Obsidian vault 和项目路径
#    然后 AI 自动路由到正确的科研阶段。
```

**首次使用**会走初始化向导，配置完成后下次直接用。

## 它做什么

```
你的需求 ──→ 阶段路由 ──→ 读三文件 ──→ AI 分析/建议 ──→ 标注输出目标
               │               │
               ▼               ▼
         论文分析           Note
         目标设定           参考文献
         实验设计           Schedule
         方法论
         架构映射
         任务规划
```

| 阶段 | 触发词 | AI 做什么 |
|------|--------|-----------|
| **论文分析** | 读论文、解读文献 | 转 PDF 为 markdown，解读方法，找研究缺口 |
| **目标设定** | 项目目标、课题方向 | 基于论文提出研究目标，grilling 压力测试 |
| **实验设计** | 设计实验、怎么验证 | 设计验证方案，选方法论，定验收标准 |
| **方法论** | 怎么实现、技术细节 | 技术解答，归属到论文章节 |
| **架构映射** | 项目架构、文件结构 | 映射研究流程到文件夹结构 |
| **任务规划** | 今天做什么、进度 | 基于 Note 目标 + Schedule 历史建议今日任务 |

## 核心理念

**AI 只读不写。** 你的三文件（Note、参考文献、Schedule）完全由你维护。AI 的每条回复标注目标文档和章节（如 **→ Project XX Note / 目标**），你直接复制粘贴到 Obsidian。

## 项目结构

```
├── SKILL.md                  ← AI 入口
├── README.md                 ← GitHub 首页（你在这里）
├── references/               ← AI 参考文档
│   ├── first-run.md          ←   初始化向导
│   ├── setup.md              ←   环境设置 + mattpocock/skills 推荐
│   └── FORMAT.md             ←   Obsidian 输出格式规范
├── templates/                ← 项目配置模板
│   └── CLAUDE-template.md    ←   占位符模板
```

> 🤖 **AI 注意**：入口是 `SKILL.md`，不是这个文件。从 SKILL.md 的「首次使用？」段开始执行。

## 依赖 skill（推荐）

| Skill | 用途 |
|-------|------|
| `pdf-converter` | PDF 论文转 markdown |
| `writing-great-skills` | 写/改 skill 规范 |
| `grilling` | 压力测试研究方案 |
| `research` | 多源调研 |
| `prototype` | 快速原型验证 |
| `dataviz` | 实验图表 |

全部可从 [mattpocock/skills](https://github.com/mattpocock/skills) 安装。

## 参考

- [Claude Code Skills 文档](https://docs.claude.com/en/claude-code/skills)
- [mattpocock/skills](https://github.com/mattpocock/skills)
