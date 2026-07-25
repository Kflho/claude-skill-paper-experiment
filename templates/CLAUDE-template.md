# CLAUDE.md — <PROJECT_NAME>

## Scientific Research Paths

| Role | Path |
|---|---|
| Note | `<project_note_path>` |
| 参考文献 | `<project_ref_path>` |
| Schedule | `<project_schedule_path>` |

## 项目仓库

```
<project_repo_root>/
  Function/     # 可复用函数
  Script/       # 可复用脚本
  Test/         # 单元测试
  Main/         # 实验入口
  Output/       # 实验产出
  参考文献/      # 论文 PDF + markdown
```

## 路径添加（MATLAB）

从 Main/、Script/ 等子文件夹内运行脚本时：

```matlab
addpath(genpath('../../../Common/'));
addpath(genpath('../Function/'));
addpath(genpath('../Script/'));
```

## Git

```bash
# 备份铁律 — 运行批量实验/重构前必须执行
cd "<project_repo_root>"
git add -A && git commit -m "备份：<操作>前 — $(date +%Y-%m-%d)"
```

> 实验代码迭代快、产出多。git 是唯一保险——没有撤销按钮。

## 任务进度

### 前期准备
- [ ] 1. 子系统建模与参数配置
- [ ] 2. 模型等价转换
- [ ] 3. 分布式残差生成器离线设计
- [ ] 4. 未知输入模型与递归滤波器
- [ ] 5. 仿真数据生成与在线监测

### 实验
- [ ] Experiment_01_decentralized_residual.m
- [ ] Experiment_02_zero_mean_residual.m
- [ ] Experiment_03_T2_detection.m
- [ ] Experiment_04_detectability_bound.m
- [ ] Experiment_05_coarse_localization.m
- [ ] Experiment_06_fine_localization.m

## SKILL INITIALIZED: true
