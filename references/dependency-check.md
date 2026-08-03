# MATLAB 依赖检测

> **核心原则：不静谧绕过。** 刚需和便利级 toolbox 缺失时，AI 必须主动告知用户并建议安装，不能默默用 fallback 替代。Fallback 只是用户明确选择不安装后的后备方案。

## 何时执行

- 首次初始化项目时（first-run.md Step 4.5）
- 每次写 MATLAB 脚本前（方法论/实验设计/批量编写阶段触发）
- 新增依赖后（如安装了新 toolbox，更新 CLAUDE.md）

## 检测命令

**核心原则：用 `exist('函数名', 'file')` 检测函数是否实际安装，不用 `license('test',...)` 查许可证。**

> ⚠️ `license('test', 'Statistics_Toolbox')` 返回 1 仅表示有许可证，不代表 toolbox 已安装。必须用 `exist()` 验证函数确实在路径上。

在 MATLAB 中运行以下命令，记录输出：

```matlab
% 列出所有实际安装的 toolbox（最可靠）
ver

% 检测关键函数是否实际可用（0=不可用, 2=内置, 3=MEX, 其他=文件路径）
% 这是最准确的安装检测方式
disp('--- Key Functions (0=NOT installed) ---');
fprintf('chi2inv: %d\n', exist('chi2inv', 'file'));
fprintf('chi2cdf: %d\n', exist('chi2cdf', 'file'));
fprintf('dlyap: %d\n', exist('dlyap', 'file'));
fprintf('lyap: %d\n', exist('lyap', 'file'));
fprintf('dare: %d\n', exist('dare', 'file'));
fprintf('care: %d\n', exist('care', 'file'));
fprintf('ss: %d\n', exist('ss', 'file'));
fprintf('lqr: %d\n', exist('lqr', 'file'));
fprintf('place: %d\n', exist('place', 'file'));

% 检测第三方工具是否在路径上
disp('--- Third-party Tools ---');
fprintf('YALMIP (sdpvar): %d\n', exist('sdpvar', 'file'));
fprintf('MOSEK (mosekopt): %d\n', exist('mosekopt', 'file'));
```

> **为什么不用 `license('test',...)`**：`license` 只检查许可证文件是否存在，不检查 toolbox 是否实际安装。有许可证 ≠ 已安装。`exist()` 直接检测函数文件是否在 MATLAB 路径上，是最可靠的安装检测方式。

或用一行命令快速检查：

```bash
matlab -batch "ver; disp('---KEY FUNCS---'); fns={'chi2inv','dlyap','ss','lqr','sdpvar','mosekopt'}; for i=1:length(fns), fprintf('%s: %d\n', fns{i}, exist(fns{i},'file')); end"
```

## 依赖分级与处理策略

| 级别 | 定义 | 缺失时的 AI 行为 |
|---|---|---|
| 🔴 **刚需** | 核心功能无法替代，无此 toolbox 实验不可行 | **阻断**：告知用户必须安装，不写绕过代码。脚本中插入 `error('请安装 XXX Toolbox')` 并给出安装指引 |
| 🟡 **极大便利** | 提供显著便利/可靠性/性能，有降级方案但会损失质量 | **建议安装**：推荐用户安装，同时提供降级方案（如 DARE 替代 LMI）。注释标注降级代价 |
| 🟢 **可选** | 单一可替代函数，纯 MATLAB 即可实现 | **自动 fallback**：使用项目内或 utils 中的纯 MATLAB 实现，无需告知用户 |

> **铁律**：🔴 和 🟡 级依赖缺失时，AI 必须明确告知用户。不能默默用 fallback 替代刚需 toolbox。

## 函数 → Toolbox 映射表

### 🔴 刚需 — 缺失时必须告知用户安装

| 函数 | 所属 Toolbox | 用途 | 说明 |
|---|---|---|---|
| `dlyap` | Control System Toolbox | 离散 Lyapunov 方程求解 | 分布式残差生成器设计的核心依赖 |
| `lyap` | Control System Toolbox | 连续 Lyapunov 方程求解 | |
| `care` | Control System Toolbox | 连续代数 Riccati 方程 | |
| `dare` | Control System Toolbox | 离散代数 Riccati 方程 | |
| `ss`, `tf`, `zpk` | Control System Toolbox | 状态空间/传递函数模型 | LTI 系统建模基础 |
| `place`, `acker` | Control System Toolbox | 极点配置 | |
| `lqr`, `dlqr` | Control System Toolbox | LQR 控制器设计 | |
| `kalman` | Control System Toolbox | Kalman 滤波器设计 | |
| `bode`, `nyquist`, `step` | Control System Toolbox | 频域/时域分析 | 实验可视化常用 |

### 🟡 极大便利 — 缺失时建议安装，提供降级

| 函数/工具 | 所属 | 用途 | 降级方案 |
|---|---|---|---|
| `sdpvar`, `optimize`, `constraints` | YALMIP (第三方) | LMI 建模与求解 | DARE 直接求解（仅适用特定问题） |
| `mosekopt` | MOSEK (第三方) | LMI 高性能求解器 | YALMIP 调用其他免费求解器 (SeDuMi, SDPT3) |
| `hinfsyn`, `h2syn` | Robust Control Toolbox | H∞/H2 综合 | 手动实现（复杂，不推荐） |

### 🟢 可选 — 缺失时自动 fallback

| 函数 | 所属 Toolbox | Fallback |
|---|---|---|
| `chi2inv` | Statistics and Machine Learning Toolbox | `utils/chi2inv.m`（纯 MATLAB 实现） |
| `chi2cdf` | Statistics and Machine Learning Toolbox | `utils/chi2cdf.m` 或 `chi2inv` + 变换 |
| `chi2rnd` | Statistics and Machine Learning Toolbox | Box-Muller + `randn` |
| `norminv` | Statistics and Machine Learning Toolbox | `erfcinv` 变换 |
| `tcdf`, `tinv` | Statistics and Machine Learning Toolbox | 近似公式 或 `betainc` 变换 |
| `pca` | Statistics and Machine Learning Toolbox | `svd` + 手动标准化 |
| `fmincon` | Optimization Toolbox | `fminsearch`（无约束）或纯 MATLAB SQP |
| `lsqnonlin` | Optimization Toolbox | Gauss-Newton 手动实现 |

## Fallback 实现指南

### 什么时候不该写 fallback

- 🔴 刚需 toolbox 缺失 → **不写 fallback**，告知用户安装。原因：手动实现 `dlyap` 不仅代码量大、易出错，而且数值稳定性远不如 MATLAB 内置实现，在科研场景下不可接受。
- 核心算法依赖第三方求解器（如 MOSEK 求解 SDP）→ **不写替代求解器**，告知用户安装或改用免费求解器。

### 什么时候可以写 fallback

- 🟢 单一数学函数（如 `chi2inv`）→ 纯 MATLAB 实现可行，放在 `utils/` 下供所有项目复用
- 🟡 降级方案（如 DARE 替代 LMI）→ 在脚本中实现，注释标注"安装 YALMIP 后可用更优的 LMI 方案"

### Fallback 函数编写规范

1. **放在 `utils/` 目录**：跨项目复用
2. **函数签名与原版一致**：调用方无需修改
3. **文件头注释标注来源**：
   ```matlab
   function x = chi2inv(p, v)
   %CHI2INV  Chi-squared inverse CDF (pure MATLAB fallback for Statistics Toolbox)
   %  Replaces: chi2inv(p, v) from Statistics and Machine Learning Toolbox
   %  Algorithm: [引用来源]
   ```
4. **精度测试**：与 MATLAB 内置函数对比，注释中记录最大偏差

## 结果记录

检测结果写入项目 CLAUDE.md 的 `## MATLAB 环境检测` 段：

```markdown
## MATLAB 环境检测

> 由 paper-experiment skill 自动检测。每次写 MATLAB 脚本前核对。
> 检测日期：YYYY-MM-DD

| Toolbox/工具 | 状态 | 级别 | 关键函数 | 缺失处理 |
|---|---|---|---|---|
| Control System Toolbox | ✅ | 🔴 刚需 | `dlyap`, `lyap`, `ss`, `lqr` | — |
| Statistics Toolbox | ❌ | 🟢 可选 | `chi2inv`, `chi2cdf` | `utils/chi2inv.m` fallback |
| YALMIP | ✅ | 🟡 便利 | `sdpvar`, `optimize` | — |
| MOSEK | ❌ | 🟡 便利 | `mosekopt` | YALMIP 降级 SeDuMi/SDPT3 |

> **策略**：🔴 刚需缺失 → 阻断告知安装 | 🟡 便利缺失 → 建议安装+降级方案 | 🟢 可选缺失 → 自动 fallback
```

## 检测流程（AI 操作步骤）

1. **执行检测命令**：在 MATLAB 中运行上述检测命令，获取 toolbox 列表和关键函数可用性
2. **对照映射表**：根据项目所用函数，对照函数→Toolbox 映射表，找出缺失的依赖
3. **分级报告**：按 🔴🟡🟢 三级分类报告缺失情况
4. **写入 CLAUDE.md**：更新 `## MATLAB 环境检测` 段
5. **阻断或降级**：
   - 🔴 缺失 → 告知用户，等待安装后再写脚本
   - 🟡 缺失 → 告知用户安装建议，在脚本中使用降级方案
   - 🟢 缺失 → 自动使用 fallback，无需告知
