# 代码格式化脚本

## fmt.py — 中英文数字间距修复

修复中文/英文与数字之间的空格问题：

```bash
# 预览修改（dry-run）
python ~/.claude/skills/scientific-research/scripts/fmt.py <文件或目录>

# 执行修改（自动 .bak 备份）
python ~/.claude/skills/scientific-research/scripts/fmt.py <文件或目录> --apply
```

规则：中文↔数字去空格 | 英文↔数字加空格 | 自动保护代码块、LaTeX、URL、下划线标识符。详细规则见 [FORMAT.md](../FORMAT.md)。

## fix_m_code.py — MATLAB 代码大小写规范化

写完 MATLAB 代码后自动规范化大小写：

```bash
# 预览修改（dry-run）
python ~/.claude/skills/scientific-research/scripts/fix_m_code.py <文件或目录>

# 执行修改（自动 .bak 备份）
python ~/.claude/skills/scientific-research/scripts/fix_m_code.py <文件或目录> --apply

# 单文件修改
python ~/.claude/skills/scientific-research/scripts/fix_m_code.py experiment_03.m --apply
```

规则：
- **保留大写**：矩阵变量（`A`, `B_z`, `Sigma_w`）、缩写（`LMI`, `DARE`, `SVD`）、人名（`Kalman`, `Lyapunov`）、品牌（`MATLAB`）
- **转为小写**：函数名、标量变量、模块名、注释文本（保护 LaTeX `$...$` 和专有名词）
- PascalCase/CamelCase 变量自动拆分：`ToDoList` → `to_do_list`、`OmegaCount` → `omega_count`
- 不修改字符串内容、LaTeX 数学、文件路径
- 详细规则见 [FORMAT.md](../FORMAT.md) → Case conventions
