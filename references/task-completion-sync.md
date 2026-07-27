# 任务完成同步清单

**每次完成一个实验脚本（或任何 CLAUDE.md 任务进度中列出的任务）后，必须同步更新以下所有位置：**

## 同步清单

| # | 文件 | 位置 | 操作 |
|---|---|---|---|
| 1 | **CLAUDE.md** | `## 任务进度` → 对应子节 | 标记复选框 `[x]`，补充函数/脚本名 |
| 2 | **Note** | `# 流程` → 对应实验 | 标记复选框 `[x]`，填写验收标准实际数值 |
| 3 | **Note** | `# 架构` → `## main` / `## scripts` / `## lib` | 标记对应脚本复选框 `[x]`；若文件名与架构中不一致，更正文件名 |
| 4 | **Note** | `# 总结` → `## 实验报告` | 追加/更新实验报告。**参数名必须用 LaTeX**（`$T_{sim}$` 非 `T_sim`）、科学计数法用 LaTeX 乘法（`$1.23 \times 10^{-15}$` 非 `1.23e-15`） |
| 5 | **Note** | `# 目标` | **若实验 `目标` 字段以 `验证目标X.Y` 开头**，标记对应编号的目标复选框 `[x]` |
| 6 | **Schedule** | 对应日期标题下 | 标记实验相关任务复选框 `[x]` |
| 7 | **代码** | 所有新写的 `.m` 文件 | 运行 `fix_m_code.py <file> --apply` 规范化大小写，修复引入的 bug |

## 特别注意

- `# 架构` 中的 **main** 小节列出了每个实验入口脚本——最容易遗漏。每次完成实验后必须检查这里。
- 架构中的文件名必须与实际文件一致。若创建时用了不同命名，同步更正。
- CLAUDE.md 中 `## 任务进度` 的复选框与 Note 架构中的复选框是两套独立的列表，都需要更新。
- 若新增了 scripts 或 lib 文件，在 `# 架构` 对应小节追加条目。

## 实验产出保存规范

实验脚本中的图片和数据应保存到 `outputs/experiment_XX_xxx/` 的对应子文件夹下：

```matlab
% 图片保存
out_dir = '../../outputs/experiment_01_decentralized_residual/figures/';
if ~exist(out_dir, 'dir'), mkdir(out_dir); end
saveas(figh, [out_dir 'residual_comparison.png']);
exportgraphics(gca, [out_dir 'residual_comparison.pdf']);

% 数据保存
data_dir = '../../outputs/experiment_01_decentralized_residual/data/';
if ~exist(data_dir, 'dir'), mkdir(data_dir); end
save([data_dir 'results.mat'], 'max_err_y', 'max_err_s', 'indices_omega');
```

- 使用相对路径 `../../outputs/...` —— 从 `src/main/` 运行时，`../../` 到达项目根目录
- 保存前确保目录存在（`mkdir`）
- 建议同时保存 PNG（位图）和 FIG（MATLAB 原生格式），便于后续修改
- 实验报告中通过备注注明产出路径

## 同步完成报告格式

同步完成后，按 [SKILL.md Output attribution](../SKILL.md#output-attribution) 格式逐条报告更新了哪个文件、哪个位置、哪些复选框：

```
**→ Project XX Note / 架构 / main**
- [x] `experiment_01_xxx.m`
- [x] `experiment_02_xxx.m`

**→ Project XX Note / 总结 / 实验报告**
### experiment_03_xxx
- 日期  2026-07-27
- 结论  通过
...
```
