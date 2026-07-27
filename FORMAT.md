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

**实验 `目标` 字段必须显式引用项目目标**：每个实验的 `目标` 格式固定为 `目标 ：验证目标X.Y，<目标描述>`，其中 `X.Y` 对应 Note `# 目标` 下的编号，`<目标描述>` 为该目标的完整原文。AI 据此判断实验完成时该勾选哪个目标复选框。

```
目标 ：验证目标1.1，证明每个计算中心仅使用本地输入/输出数据即可独立计算残差，无需全局信息
目标 ：验证目标1.2，验证在没有中央融合节点的情况下，正常状态残差的期望值为0
目标 ：验证目标2.1，复现公式 (27) 的 $J_{T^2,\omega}$ 统计量，验证正常状态下无误报
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
| File name / function name | `` `backtick` `` | `` `model_1_to_model_2.m` `` |
| Inline math | `$...$` | `$\Sigma_{r_\omega}$` |
| Block math | `$$...$$` | `$$\begin{aligned}...\end{aligned}$$` |
| Bold emphasis | `**text**` | `**$s_{j,k}$为临近节点发出的信息变量**` |
| Code / variable | `` `backtick` `` | `` `indices_omega` `` |

## Experiment report format

每个实验完成后，AI 在 Note 的 `# 总结` → `## 实验报告` 板块下追加报告。格式：

```
# 总结
## 实验报告
### Experiment_01_xxx
- 日期  YYYY-MM-DD
- 结论  通过 / 未通过（一句话总结）
- 参数  
	- $T_{sim} = 2000$
	- 计算中心划分 = $\{[1,3], [2,4]\}$
	- $A_z$ max$|\lambda| = 0.962$
- 指标  
	- 中心 1 $r^y$ 最大偏差 = $1.23 \times 10^{-15}$  [通过]
	- 中心 2 $r^s$ 维度 2 样本均值/界 = 0.42  [通过]
- 备注  
	- 发现/问题/注意事项
```

规则：
- `# 总结` 为 H1，`## 实验报告` 为 H2，每个实验用 H3（脚本名）
- 日期用当天
- 短标签（日期、结论）同行；多行内容（参数、指标、备注）标签独占一行，内容下一行 Tab 缩进
- 指标项每条独立一行，括号内标注通过/未通过
- 实验重新运行后更新对应 H3 块，不重复追加
- **产出路径**：若实验生成图片/数据，在备注中注明 `outputs/experiment_XX_xxx/` 下的产出路径
- **LaTeX 参数名**：报告中所有数学变量名必须用 LaTeX 数学模式（`$T_{sim}$`、`$r^y$`、`$A_z$`），禁止使用代码风格下划线（`T_sim`、`r_y`）。文件名/函数名仍用 `` `backtick` `` 包裹（`` `split_matrices_and_cov` ``）。
- **科学计数法**：极小/极大数值用 LaTeX 乘法（`$1.23 \times 10^{-15}$`），不用 `1.23e-15`

## Schedule file format

- Date header: `# MM.DD`
- All entries are task lists
- Nesting follows the same Tab rules as Note

```
# 07.17
- [x] 未知输入模型与递归滤波器
	- [x] 函数 model_2_to_model_3_qr.m
		- [x] 组装公式 35-36 的动态耦合映射矩阵
	- [x] 函数 recursive_joint_filter.m
		- [x] 偏置创新向量 → 未知输入估计
```

## Content spacing rules

### Chinese, English, and numbers

| Pattern | Spacing | Example |
|---|---|---|
| Chinese + number | No space | `2025年`, `中心1`, `模型2` |
| Number + Chinese | No space | `1个`, `500步`, `3σ` |
| English + number | One space | `model 1`, `Experiment 01`, `100 km` |
| Number + English | One space | `100 km`, `4800 steps` |
| Chinese + English | One space | `模型 model` |
| English + Chinese | One space | `model 模型` |
| English + number + Chinese | One space both sides | `model 1 运行时`, `Experiment 01 实验` |
| Chinese + number + English | One space both sides | `中心 1 model` |

### Exceptions

- Proper nouns / brand names: follow official spelling (e.g. `iPhone 17`, `UX7`)
- In code context (`` `backtick` ``): no spacing rules apply
- Annotations / notes after content: use a colon
- Attributes (scores, aliases) after content: use parentheses directly, no space before. If in folder names, replace spaces with underscores.

## Case conventions

全小写为默认。仅以下情况保留大写：

| 保留大写 | 示例 | 说明 |
|---|---|---|
| 矩阵变量 | `A`, `B_z`, `L_ω`, `A_{z,ω}`, `Sigma_w` | 单大写字母 + 可选下标 |
| 人名 | Kalman, Lyapunov, Schur, Luenberger | 专有名词 |
| 缩写 acronym | LMI, DARE, SVD, MCU, PCB, FPGA | 全大写缩写 |
| 品牌/产品名 | MATLAB, Simulink, Obsidian | 官方拼写 |
| 希腊字母 | `Ω`, `ω`, `Δ`, `Σ` | Unicode 数学符号 |
| MATLAB pragma | `%#ok<AGROW>` | 代码检查抑制指令 |

其余一律小写：函数名、模块名、文件夹名、文档名、普通描述文本。

## File naming

| 规则 | 示例 |
|---|---|
| 全小写 snake_case，下划线分隔 | `compute_online_residuals.m`, `project_01_note.md` |
| 禁止数字开头 | ❌ `01_test.m` → ✅ `test_01_model_1_to_model_2.m` |
| 顺序编号用 `类别_编号_描述` 前缀 | `test_01_`, `experiment_02_`, `project_01_` |
| 专有名词编号中数字紧跟单词 | `model_1_to_model_2`, `experiment_01_decentralized_residual` |
| `.m` 文件名 = 主函数名 | `compute_online_residuals.m` → `function [...] = compute_online_residuals(...)` |

## Folder naming

| 规则 | 示例 |
|---|---|
| 全小写 snake_case，下划线分隔 | `src/lib/`, `src/scripts/`, `outputs/experiment_01/` |
| 能加复数加复数 | `projects/`, `scripts/`, `tests/`, `outputs/`, `utils/` |
| 不可数/不适合复数保持单数 | `lib/`, `main/`, `data/`, `src/` |
| 禁止数字开头 | ❌ `01_project/` → ✅ `project_01_distributed_fault_monitoring/` |
| 文件夹是限定词，不重复命名 | `tools/resources/` 非 `tools/tool_resources/` |

**脚本代码中**（`.m` 文件）：
- 变量名 snake_case，矩阵变量可大写（`A`, `B_z`, `Sigma_w`）
- 函数名全小写 snake_case，与文件名一致
- 注释文本遵循上述所有规则，矩阵引用与代码一致
- 写完代码后运行 `fix_m_code.py` 自动规范化，修复引入的 bug
