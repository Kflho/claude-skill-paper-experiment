# 代码格式化脚本

## 写前检查：MATLAB 环境依赖

**写 MATLAB 脚本前必须执行依赖检测** → 完整流程与分级处理策略见 [dependency-check.md](dependency-check.md)。

---

## fmt.py — 中英文数字间距修复

修复中文/英文与数字之间的空格问题：

```bash
# 预览修改（dry-run）
python ~/.claude/skills/paper-experiment/scripts/fmt.py <文件或目录>

# 执行修改（自动 .bak 备份）
python ~/.claude/skills/paper-experiment/scripts/fmt.py <文件或目录> --apply
```

规则：中文↔数字去空格 | 英文↔数字加空格 | 自动保护代码块、LaTeX、URL、下划线标识符。详细规则见 [format.md](format.md)。

## fix_m_code.py — MATLAB 代码大小写规范化

写完 MATLAB 代码后**必须**运行格式化脚本，**格式化完再跑**——否则格式化器改坏的 API 属性名会导致运行时错误。

```bash
# 预览修改（dry-run）
python ~/.claude/skills/paper-experiment/scripts/fix_m_code.py <文件或目录>

# 执行修改（自动 .bak 备份）
python ~/.claude/skills/paper-experiment/scripts/fix_m_code.py <文件或目录> --apply

# 单文件修改
python ~/.claude/skills/paper-experiment/scripts/fix_m_code.py experiment_03.m --apply
```

规则：
- **保留大写**：矩阵变量（`A`, `B_z`, `Sigma_w`）、缩写（`LMI`, `DARE`, `SVD`）、人名（`Kalman`, `Lyapunov`）、品牌（`MATLAB`）
- **转为小写**：函数名、标量变量、模块名、注释文本（保护 LaTeX `$...$` 和专有名词）
- PascalCase/CamelCase 变量自动拆分：`ToDoList` → `to_do_list`、`OmegaCount` → `omega_count`
- 不修改字符串内容、LaTeX 数学、文件路径
- 详细规则见 [format.md](format.md) → Case conventions

> ⚠️ **已知限制**：格式化器对上下文无感知，需 AI 审查 diff：
> - **外部 API 边界**：`sim_w.Data` → `sim_w.data`（Simulink 属性名由 API 定义，格式化器不知道应保留大写）
> - **命名冲突暴露**：`Omega=2` + `for omega=1:Omega` → 格式化后两者都是 `omega`，循环失效。此时应改变量名（`Omega`→`n_omega`），而非保护不规范的命名。格式化规则本身正确。
> - **注释专有名词**：Hotelling's `T²` 被当普通文本小写化 → 应还原或用 `$J_{T^2}$` LaTeX 写法
>
> **🚨 强制工作流（格式化必须在跑之前完成）：**
> ```
> 1. 写 .m 代码
> 2. python ~/.claude/skills/paper-experiment/scripts/fix_m_code.py <file> --apply
> 3. git diff <file>  →  AI 逐条审查：
>    🔴 外部 API 属性名还原大写（如 sim_w.Data、sim_w.Time）
>    🟡 变量名变更是否导致命名冲突（Omega→n_omega 等）
>    🟢 注释中 LaTeX $...$ 和专有名词是否被误改
> 4. 修正格式化引入的错误
> 5. 跑 MATLAB 脚本
> ```
> 严禁跳过格式化直接跑——格式化器改坏的 API 属性名会导致运行时错误。详见 [fan-out-writing.md](fan-out-writing.md) Phase 2。
