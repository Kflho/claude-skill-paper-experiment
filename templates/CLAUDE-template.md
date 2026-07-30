# CLAUDE.md — <PROJECT_NAME>

## Scientific Research Paths

| Role | Path |
|---|---|
| Note | `<project_note_path>` |
| 参考文献 | `<project_ref_path>` |
| Schedule | `<project_schedule_path>` |
| 论文文件夹 | `<papers_dir_path>` |

## 项目仓库

```
<project_root>/                  # 用户指定的项目根目录（所有依赖的公共祖先）
  utils/                         # 跨项目共享（如存在）
  projects/
    [category]/
      project_XX/
        src/
          lib/                   # 项目内部函数依赖
          scripts/               # 可复用脚本
          tests/                 # 单元测试
          main/                  # 实验入口
        outputs/                  # 实验产出
        ...                      # 实际目录由初始化扫描确定
```

## 路径规范

**强制规则：所有路径必须使用相对路径，禁止硬编码绝对路径（如 `D:\data\...`）。** 保证整个项目根目录移动到任意位置后脚本仍可正常运行。

### 路径解析表

初始化时扫描项目根目录自动生成。以下为示例（从 `src/main/`、`src/tests/`、`src/scripts/` 出发）：

| 相对路径 | 解析目标 |
|---|---|
| `<../到 utils 的层数>/utils/` | 仓库根工具库 |
| `../lib/` | 项目内部函数 |
| `../scripts/` | 可复用脚本 |
| `../../outputs/experiment_XX_xxx/` | 实验产出目录（含 `figures/`、`data/`） |

### 路径添加（MATLAB）

```matlab
% 初始化时扫描 <project_root> 下所有含 .m 的文件夹，计算相对路径后填入
addpath(genpath('<../到 utils 的层数>/utils/'));
addpath(genpath('../lib/'));
addpath(genpath('../scripts/'));
```

### 读写文件

产出保存到 `../../outputs/experiment_XX_xxx/` 下对应子文件夹，禁止写到项目外路径。

```matlab
out_pic = '../../outputs/experiment_01_xxx/figures/';
out_data = '../../outputs/experiment_01_xxx/data/';
if ~exist(out_pic, 'dir'), mkdir(out_pic); end
save([out_data 'results.mat'], ...);
```

> **注意：** MATLAB 的 `addpath` 相对路径基于 `pwd`（当前工作目录），非脚本文件位置。务必从脚本所在目录运行（`cd` 到 `src/main/` / `src/tests/` / `src/scripts/` 后再执行），否则相对路径会解析错误。

## MATLAB 环境检测

> 由 scientific-research skill 自动检测。每次写 MATLAB 脚本前核对。
> 检测日期：YYYY-MM-DD

| Toolbox/工具 | 状态 | 级别 | 关键函数 | 缺失处理 |
|---|---|---|---|---|
| Control System Toolbox | ✅/❌ | 🔴 刚需 | `dlyap`, `lyap`, `ss`, `lqr`, `place` | 阻断，告知安装 |
| Statistics Toolbox | ✅/❌ | 🟢 可选 | `chi2inv`, `chi2cdf` | `utils/chi2inv.m` fallback |
| Optimization Toolbox | ✅/❌ | 🟢 可选 | `fmincon`, `lsqnonlin` | `fminsearch` 或手动实现 |
| Signal Processing Toolbox | ✅/❌ | 🟢 可选 | `filter`, `fft` | 手动实现 |
| System Identification Toolbox | ✅/❌ | 🟢 可选 | `ssest`, `n4sid` | 手动子空间辨识 |
| Robust Control Toolbox | ✅/❌ | 🟡 便利 | `hinfsyn`, `h2syn` | 手动实现（不推荐） |
| YALMIP (第三方) | ✅/❌ | 🟡 便利 | `sdpvar`, `optimize` | 建议安装，降级 DARE |
| MOSEK (第三方) | ✅/❌ | 🟡 便利 | `mosekopt` | 建议安装，降级 SeDuMi |

> **策略**：🔴 刚需缺失 → 阻断告知安装 | 🟡 便利缺失 → 建议安装+降级方案 | 🟢 可选缺失 → 自动 fallback

## Git

```bash
# 备份铁律 — 运行批量实验/重构前必须执行
cd "<project_repo_root>"
git add -A && git commit -m "备份：<操作>前 — $(date +%Y-%m-%d)"
```

> 实验代码迭代快、产出多。git 是唯一保险——没有撤销按钮。

## 任务进度

### scripts — 参数与仿真脚本
- [ ] `create_model_1.m`
- [ ] `init_parameters.m`
- [ ] `start_simulation.m`

### lib — 核心算法
- [ ] 1. 模型等价转换（model_1_to_model_2, assemble_global_model）
- [ ] 2. 分布式残差生成器离线设计（solve_luenberger_lmi, split_matrices_and_cov）
- [ ] 3. 未知输入模型（model_2_to_model_3_qr）
- [ ] 4. 在线计算（compute_online_residuals, inject_fault, recursive_joint_filter）

### tests — 验证
- [ ] 单元测试（test_01 ~ test_09）
- [ ] 实验 01 — 去中心化验证（目标 1.1）
- [ ] 实验 02 — 零均值验证（目标 1.2）
- [ ] 实验 03 — T² 检测（目标 2.1）
- [ ] 实验 04 — 可检测性边界（目标 2.2）
- [ ] 实验 05 — 粗定位（目标 3.1）
- [ ] 实验 06 — 精定位（目标 3.2）

## Handoff

`/clear` 后自动读取系统临时目录下的 `handoff-*.md`（按修改时间取最新），恢复上下文继续工作。

## SKILL INITIALIZED: true
