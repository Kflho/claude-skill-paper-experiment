# Format Specification — Scientific Research

All AI output must follow these rules so the user can copy-paste directly into Obsidian without editing.

## Heading hierarchy

| Level | Markdown | Use |
|---|---|---|
| H1 | `# Title` | File top-level sections: 目标, 流程, 架构, 论文解读, 论文方法 |
| H2 | `## Title` | Major phases or categories: 前期准备, 实验, Script, Function, 仿真搭建 |
| H3 | `### Title` | Sub-entries: paper section titles, specific module names |
| Separator | `---` | Major block breaks within a section; on its own line with blank lines above and below |

## Indentation

- **Tab only.** Never use spaces for indentation.
- Each nesting level = one additional Tab.
- Examples:

```
# 目标
- [ ] 指标一，描述
	- [x] 目标 1.1，子描述
		- [ ] 更细的子任务
- [ ] 指标二，描述
```

## Lists

- `- [ ]` unchecked task, `- [x]` completed task, `-` plain list item
- After the bracket: **one space**, then content directly
- Sibling items at the same indent level: **no blank line** between them
- Different groups at the same indent level: **one blank line** between groups

```
- [x] 第一组任务一
- [x] 第一组任务二

- [ ] 第二组任务一
- [ ] 第二组任务二
```

## Labels and content

**Short labels** (目标, 流程, 参考, 架构, 总结, 问题, 验收标准): label followed by one space, then content on the **same line**:

```
目标  证明每个计算中心仅使用本地数据即可独立计算残差
流程  从脚本仿真获取数据，对各计算中心分别运行
验收标准  最大偏差 < 10^{-12}
```

**Long content**: label on its own line, content on next line with one Tab indent:

```
流程  
	从脚本仿真获取数据，对各计算中心 ω 分别运行 Compute_online_residuals
	验证每个中心仅访问本地数据，不依赖其他区域数据
	对比各中心独立计算的残差与理论全局残差的对应分块是否一致
```

## Inline formatting

| Element | Format | Example |
|---|---|---|
| File name / function name | `` `backtick` `` | `` `Model_1_to_model_2.m` `` |
| Inline math | `$...$` | `$\Sigma_{r_\omega}$` |
| Block math | `$$...$$` | `$$\begin{aligned}...\end{aligned}$$` |
| Bold emphasis | `**text**` | `**$s_{j,k}$为临近节点发出的信息变量**` |
| Code / variable | `` `backtick` `` | `` `indices_omega` `` |

## Schedule file format

- Date header: `# MM.DD`
- All entries are task lists
- Nesting follows the same Tab rules as Note

```
# 07.17
- [x] 未知输入模型与递归滤波器
	- [x] 函数 Model_2_to_model_3_qr.m
		- [x] 组装公式 35-36 的动态耦合映射矩阵
	- [x] 函数 Recursive_joint_filter.m
		- [x] 偏置创新向量 → 未知输入估计
```

## Content spacing rules

- English letters and numbers: generally add one space between them (e.g. `Model 1`, `100 km`)
- Exception — no space: serial numbers (e.g. `model 1`, `iPhone 17`), units (e.g. `100 km`)
- Exception — no space: proper nouns (e.g. `UX7`)
- Chinese and English: one space between them
- Chinese and numbers: no space between them
- Annotations / notes after content: use a colon
- Attributes (scores, aliases) after content: use parentheses directly, no space before. If in folder names, replace spaces with underscores.
