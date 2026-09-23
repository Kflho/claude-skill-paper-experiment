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

写完 MATLAB 代码后**必须**规范化，**格式化完再跑**——先改后跑，才不会把格式化器的误改当成运行错误来查。

```bash
# 1. 先看 diff（不写文件）
python ~/.claude/skills/paper-experiment/scripts/fix_m_code.py <文件或目录> --diff

# 2. 确认无误后写入（自动 .bak 备份）
python ~/.claude/skills/paper-experiment/scripts/fix_m_code.py <文件或目录> --apply

# 3. 检查是否已规范（有需改动处则退出码 1）
python ~/.claude/skills/paper-experiment/scripts/fix_m_code.py <文件或目录> --check
```

**🚨 工作流（格式化必须在跑之前完成）：**

```
1. 写/改 .m 代码
2. --diff → 对每一处 hunk 判定：误改（还原）还是正确规范（保留）——不留未判项
3. 修正：误改的词进项目词表（一次加入永久生效）；命名冲突（Omega 与既有 omega 撞名）→ 改变量名 n_omega
4. --apply 写入 → 删除 *.bak
5. 跑 MATLAB 脚本
```

**审查按有罪推定**：格式化器对上下文无感知，每处改动先当**误改**，能说出「这是正确规范」的才保留。按「看着像规范化」放行是本流程唯一会伤到代码的失误——实测中曾有文件 **12 处改动全是误改**（`sim_w.Data` → `sim_w.data` 会直接运行报错），而它们看上去都像正常规范化。

保留/小写清单（判定基准）见 [format.md](format.md) → Case conventions——**判定以那份清单为准**，别凭手感。

**项目词表 `.fix_m_code_protect`**（放在项目根，向上逐级合并）：
- 每行一个词，`#` 起注释；命中处在代码与注释里都保留
- 放规则盖不住的词：专名（`Snr`、`Montgomery`、`Runger`）、外部 API 属性名（`Data`、`Time`、`Units`）、三字符矩阵符号（`Azw`、`Bzw`、`Gzw`）
- **审查里还原过的词必须进词表**——否则下个文件同一处再错一遍，等于每份文件都重犯
- 临时词用 `--protect Snr,Runger`（仅本次运行）

其他开关：`--no-protect-properties`（连 `对象.属性` 一起小写化，默认保护）、`--no-backup`（已有 git 备份时）、`--dictionary FILE`（指定词表）。

**判定「误改」之后分两类处理：**
- **词的例外**（`Snr`、`Montgomery`、`Azw`）→ 进项目词表
- **规则的漏洞**（`条件A` → `条件a`、`3dB` → `3db`、`2D` → `2d`）→ 修 `fix_m_code.py` 的规则。词表治不了同一类里的下一个词——中文紧邻的符号是整类失效（Python 的 `\b` 把中文算作词字符），堆词表等于每遇到一个新符号就再修一次

**边界：**
- 非 UTF-8 的 `.m`（如 GBK 项目）报错跳过，不会按 UTF-8 覆写、毁掉中文注释
- 行尾符 CRLF/LF 原样保留，不产生整文件 diff
- `'` 既可能是转置也可能是字符串起点，行内注释的分界可能判错 → 在 diff 里盯代码行上的注释改动
- 批量产出（fan-out 多脚本）时逐个文件独立走一遍审查 → [fan-out-writing.md](fan-out-writing.md)
