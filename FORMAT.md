# Format Specification — Scientific Research

All AI output must follow these rules so the user can copy-paste directly into Obsidian without editing.

## 快速参考

> 最常用的 5 条规则。完整规范见下方各节。

| 场景 | 规则 |
|---|---|
| 实验报告结构 | `### experiment_XX_xxx` → 日期 / 结论 / 参数 / 指标 / 备注（参数名 LaTeX 化） |
| 参数与变量 | LaTeX 数学模式：`$T_{sim}$` 非 `T_sim`；极小值 `$1.23 \times 10^{-15}$` 非 `1.23e-15` |
| 文件名 | 全小写 snake_case：`experiment_01_xxx.m`，禁止数字开头 |
| Case | 矩阵大写（`A`, `B_z`, `Sigma_w`），缩写大写（`LMI`, `DARE`），其余小写。外部 API 属性保留官方大小写 |
| Note 流程段 | 每个实验必含 3 字段：目标（引用 Note 编号）、方法（引用论文公式）、产出（数值 + 图片 + 数据） |
| 函数所有权 | `[手写]` = 用户实现核心算法，`[AI组装]` = AI 拼装脚本。src 中每个函数条目标注 |

---

## Heading hierarchy

| Level | Markdown | Use |
|---|---|---|
| H1 | `# Title` | File top-level sections: 目标, 流程, 架构, 论文解读, 论文方法 |
| H2 | `## Title` | Major phases or categories: 流程, 架构, Scripts, Lib, Tests, 指标一/二/三 |
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

**Short labels** (目标, 流程, 架构, 总结, 验收标准): label followed by one space, then content on the **same line**:

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

每个实验完成后，AI 在 `pg 01 report.md`（实验报告文档）追加报告。格式：

```
# 实验报告
### experiment_01_xxx
- 日期  YYYY-MM-DD
- 结论  通过 / 未通过（一句话总结）
- 参数  
	- $T_{sim} = 2000$
	- 计算中心划分 = $\{[1,3], [2,4]\}$
	- $A_z$ max$|\lambda| = 0.962$
- 指标  
	- 中心 1 $r^y$ 最大偏差 = $1.23 \times 10^{-15}$  [通过]
	- 中心 2 $r^y$ 最大偏差 = $3.67 \times 10^{-15}$  [通过]
- 备注  
	- 发现/问题/注意事项
```

规则：
- `# 实验报告` 为 H1，每个实验用 H3（脚本名）
- 日期用当天
- 短标签（日期、结论）同行；多行内容（参数、指标、备注）标签独占一行，内容下一行 Tab 缩进
- 指标项每条独立一行，括号内标注通过/未通过
- 实验重新运行后更新对应 H3 块，不重复追加
- **产出路径**：若实验生成图片/数据，在备注中注明 `outputs/{cn,eng}/experiment_XX_xxx/` 下的产出路径
- **LaTeX 参数名**：报告中所有数学变量名必须用 LaTeX 数学模式（`$T_{sim}$`、`$r^y$`、`$A_z$`），禁止使用代码风格下划线（`T_sim`、`r_y`）。文件名/函数名仍用 `` `backtick` `` 包裹（`` `split_matrices_and_cov` ``）。
- **科学计数法**：极小/极大数值用 LaTeX 乘法（`$1.23 \times 10^{-15}$`），不用 `1.23e-15`

## Note file structure

Note 文件固定四个 H1 段：

```
# 目标          ← 研究目标与指标（复选框，编号 目标X.Y）
# 流程          ← 实验清单：每个实验仅含目标、方法、产出。数据流/参数溯源 → src.md，结论 → 结论
# 结论          ← 各实验结论汇总（按指标分组，每个实验一句话结论）
```

**Schedule 文件结构**（**内容由用户维护；AI 只允许勾选/取消已有复选框，禁止新增/编辑任何文字**）：
```
# MM.DD        ← 日期标题 + 当日任务列表（用户记录：只记录做了什么，不写怎么做）
# 问题          ← 方法不一致/参数臆造等未解决问题（从 Note 移出，统一跟踪）
```

**示例**：
```
# 问题
1. 实验4 $G_{z,\omega}$ 的 DC 增益 [臆造概念] [错误声称]
	当前：称"DC 增益"参数，标注"论文未给出，自行推导"
	实际：公式 19-22 给出了全局矩阵，$G_{z,\omega}$ 是对应第 $\omega$ 个计算中心拆分出的分块矩阵，无需"自行推导"
	修复：删除"DC 增益"概念，$G_{z,\omega}$ 来源标注为公式 19-22 拆分
```

### 流程段格式

按指标分组。每个实验必须包含 3 个字段：目标、方法、产出。**论文未给出的信息必须标注来源。** 数据流与参数溯源 → src.md，结论 → Note `# 结论`。

```
# 流程

## 指标一 — 分布式残差生成
- [x] 实验 01 — 去中心化验证
  - 脚本：`experiment_01_decentralized_residual.m`
  - 目标：目标 1.1 — 各中心仅用本地数据独立计算残差
  - 方法：
    - 步骤 1（离线设计）：执行管线 A（model 1 → 2 → 组装 → LMI → 拆分），公式 7-26
    - 步骤 2（闭环仿真）：管线 B，LQR 控制器 + 噪声驱动，$T_{sim}=500$，无故障
    - ...
    - 判定准则：$\forall \omega$: max$|r_{y,loc}^\omega - r_{y,all}^\omega| < 10^{-12}$
  - 产出：
    - 局域 vs 全局输出残差最大偏差 $\sim 10^{-15}$，验证分布式计算无精度损失（仅验证 $r_y$，$r_s$ 不参与检测）
    - 图片：
      - `center{1,2}_ry_comparison.png` — 论证局域与全局输出残差一致。标题：`实验 01：中心 ω 输出残差 — 局域 vs 全局`
    - 数据：
      - `results.mat` — `max_err_y`, `indices_omega`, `n_omega`, `T_sim`
```

**3 字段要求：**

| 字段 | 要求 |
|------|------|
| 目标 | 格式 `目标 ：验证目标X.Y，<目标原文>`，显式引用 Note `# 目标` 编号 |
| 方法 | 每个步骤引用论文公式/定理/表。论文未明确描述时标注「论文未指定，实现选择：<理由>」。判定准则作为方法最后一步 |
| 产出 | 关键数值结果 + 图片（文件名、论证目的、标题模板）+ 数据（`.mat` 文件名、包含变量、用途） |

**技术细节透明规则**：论文没有、但实现必须的技术决策，格式固定为「论文未指定，实现选择：<做法>。理由：<原因>。」简化/替代实现必须说明论文原文做法、本实现做法、为何可/不可等价、差异对结论的影响。详细数据流与参数溯源 → src.md。

规则：
- H2 按指标分组（`## 指标一 — ...`、`## 指标二 — ...`、`## 指标三 — ...`）
- 辅助脚本（show_liquid_level、batch_experiments）放 `## 辅助`
- 结论不在实验中写，统一汇总到 Note `# 结论`

### 架构段（→ `pg 01 src.md`）

架构（函数目录、数据管线、设计决策）已从 Note 迁移到 `pg 01 src.md`。Note `# 流程` 中的实验方法引用管线步骤（如"管线 A"），具体函数调用链和参数溯源见 src.md。

src.md 结构：`# scripts` → `# lib`（按论文推导链分阶段）→ `# tests` → `# main`（共用数据管线 + 设计决策 + 各实验数据流/参数溯源）。

四个 H2 子段：`## scripts`、`## lib`、`## tests`、`## main`。核心要求：**每项标注上下游依赖，读文档即可落地。**

**scripts** — 参数/仿真脚本：
```
- [x] `create_model_1.m`
  - 功能：定义四容水箱 model 1 的状态空间矩阵与网络拓扑
  - 输出：A, B, C, D, E, F, C_s, D_s, M, N, n_x, n_y, n_s, Sigma_w, Sigma_v
  - 下游：所有实验脚本的第一步调用
```

**lib** — 核心算法，按论文推导链分阶段。每个函数标注所有权：`[手写]`（用户实现）或 `[AI组装]`（AI 拼装）：
```
### 阶段 1：模型等价转换（公式 7-14）
- [x] `model_1_to_model_2.m` `[AI组装]`
  - 功能：model 1 → model 2 转换，公式 7-10
  - 输入：create_model_1 的 A, B, C, D, E, F, C_s, D_s, M, N
  - 输出：A_bar, B_bar, C_bar, D_bar, E_bar, F_bar, C_s_bar, D_s_bar
  - 下游：→ assemble_global_model, model_2_to_model_3_qr
```

规则：
- 每项必有：功能 + 输入 + 输出 + 下游（用 `→` 箭头指向调用方）
- 输入/输出写具体变量名，不写"各子系统矩阵"等模糊描述
- 外部依赖（YALMIP、dlyap）标注在 `依赖：` 行
- 公式引用用 `公式 X-Y` 或 `Theorem 1`

**tests** — 单元测试：
```
- [x] `test_01_model_1_to_model_2` — model_1_to_model_2：与 create_controlled_system 逐元素比对（偏差 $< 10^{-12}$）
```
一行一个测试，破折号后写被测函数和验证方式。

**main** — 在线实验。先写共用数据管线（含 I/O 溯源），再逐个列出实验。

**共用数据管线**每步必须标注：输入变量来源（从哪个上一步产出）、论文公式出处、输出变量的物理含义。示例：

```
### 共用数据管线
**A. 离线设计**（→ `## lib` 阶段 1-2）：
1. `create_model_1` → 子系统矩阵 `A, B, C, D, ...`
2. `model_1_to_model_2(A, B, C, D, E, F, C_s, D_s, M, N)` → model 2 矩阵 `A_bar, B_bar, C_bar, D_bar`（公式 7-10）
3. `assemble_global_model(A_bar, B_bar, C_bar, D_bar, n_x)` → 全局系统 `A_g, B_g, C_g, D_g`（公式 11-14）
4. `solve_luenberger_lmi(A_g, C_g, Sigma_w, Sigma_v)` → 观测器 `A_z, L`（Theorem 1）
   - 输入 A_g, C_g：步骤 3 产出（公式 11-14，全局状态空间矩阵）
   - 输入 Sigma_w, Sigma_v：create_model_1 产出（噪声协方差，论文未给出数值，经验设定）
   - 输出 A_z：残差生成器状态转移矩阵（公式 15-18 中的 $A_{z,\omega}$ 拆分前身）
   - 输出 L：Luenberger 增益（公式 15-18 中的 $L_{z,\omega}$ 拆分前身）
```

**数据管线要求**：

1. **I/O 溯源**：每个处理步骤标注输入变量 ← 来源（上一步产出 + 论文公式出处）和输出变量 → 含义（对应论文哪个量）+ 下游用途
2. **数据变换透明**：任何非平凡的数据变换（如故障注入、标准化、协方差投影等）必须在管线中显式描述，标注论文公式或自行推导过程
3. **仿真数据溯源**：列出关键仿真变量的维度、物理含义、论文公式、生成方式
4. **论文未指定的依赖**：外部工具（如 LMI 求解器）、控制器类型等论文未指定的选择，必须标注
5. **设计决策**：论文未覆盖的技术决策（如瞬态截断、随机种子方案、检测准则等）在管线末尾统一记录，格式「做法 + 推导/理由」

**实验产出要求**（Note 流程段每个实验的 `产出` 字段）：

- 关键数值结果（一句话）
- 图片：每张图的文件名、展示内容、科学含义（论证了什么）
- 数据：每个 `.mat` 文件的文件名、包含变量、用途
- 格式：
  ```
    - 产出：
      - <关键数值结果>
      - 图片：
        - `<name>.png` — <展示内容>，论证 <科学含义>
      - 数据：
        - `results.mat` — 包含 <变量列表>，用于 <用途>
  ```

- [x] `experiment_01_decentralized_residual` — 目标 1.1
  - 做什么：调用管线 A+B+C。先对所有中心一起算残差，再逐个中心单独算，对比偏差。
  - 数据流：`create_model_1 → model_1_to_model_2 → ... → compute_online_residuals`
  - 产出：局域 vs 全局残差最大偏差 $\sim 10^{-15}$。
```

规则：
- 共用管线用编号步骤 + `函数名(参数) → 产出变量` 格式，标注阶段对应 lib 位置
- 每个实验：做什么（一句话）+ 数据流（完整调用链）+ 产出（关键数值）
- 数据流要具体到函数名和变量名，不写"离线链路 + → xxx"

## Schedule file format

日程表只记录**做什么、完成没有**，**内容由用户维护**。实施方案（函数、调用链、参数）全部在 src。**AI 只允许勾选/取消已有复选框，禁止新增/编辑任何文字。**

- Date header: `# MM.DD`
- 每项一个任务复选框，标注实验编号 + 目标引用
- 不展开实现细节（函数名、公式、参数）——这些属于 Note

```
# 07.28
- [x] 实验 03 — T² 检测与零误报（目标 2.1）
- [x] 实验 04 — 可检测性边界（目标 2.2）
- [x] 实验 05 — 粗定位（目标 3.1）。结论：论文方法在此拓扑无法实施。

# 07.29
- [x] 实验 06 — 修正脚本逻辑，精定位与粗定位分离，重跑通过（100%）
- [x] 合并 Note 前期准备/实验/架构，消除冗余
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
| 外部 API 属性名 | `sim_w.Data`, `sim_v.Data`, `sim_w.Time` | 由外部 API 定义的属性名，大小写必须与 API 文档一致 |

**外部 API 属性名识别规则**：当变量名引用外部对象（Simulink timeseries、MATLAB 对象、第三方库）的属性时，属性名的大小写由该对象的 API 决定，不得修改。常见场景：
- `sim_w.Data` / `sim_v.Data` — Simulink `timeseries` 对象的属性，必须大写 `D`
- `sim_w.Time` — 同上，必须大写 `T`
- `obj.PropertyName` — 任何 `.` 访问的外部对象属性，格式化前先确认 API 文档

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
| 全小写 snake_case，下划线分隔 | `src/lib/`, `src/scripts/`, `outputs/cn/experiment_01/` |
| 能加复数加复数 | `projects/`, `scripts/`, `tests/`, `outputs/`, `utils/` |
| 不可数/不适合复数保持单数 | `lib/`, `main/`, `data/`, `src/` |
| 禁止数字开头 | ❌ `01_project/` → ✅ `project_01_distributed_fault_monitoring/` |
| 文件夹是限定词，不重复命名 | `tools/resources/` 非 `tools/tool_resources/` |

**脚本代码中**（`.m` 文件）：
- 变量名 snake_case，矩阵变量可大写（`A`, `B_z`, `Sigma_w`）
- 函数名全小写 snake_case，与文件名一致
- 注释文本遵循上述所有规则，矩阵引用与代码一致
- 写完代码后运行 `fix_m_code.py` 自动规范化，修复引入的 bug
