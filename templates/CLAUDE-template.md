# CLAUDE.md — <PROJECT_NAME>

## Scientific Research Paths

| Role | Path |
|---|---|
| Note | `<project_note_path>` |
| 参考文献 | `<project_ref_path>` |
| Schedule | `<project_schedule_path>` |

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

## 路径添加（MATLAB）

以下路径由初始化时扫描项目根目录自动生成，**不做预设**：

```matlab
% 初始化时扫描 <project_root> 下所有含 .m 的文件夹，计算相对路径后填入
addpath(genpath('<../到 utils 的层数>/utils/'));
addpath(genpath('../src/lib/'));
addpath(genpath('../src/scripts/'));
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
