# Project structure

此 skill 创建新项目时默认采用以下约定。若用户已有现成项目结构，初始化时扫描实际目录自动适配。

```
utils/                           # 跨项目共享代码（与 projects/ 同级）
projects/                        # 所有项目（固定层，防止摊平）
  [category]/                    # 可选分类（如 postgraduate/）
    project_xx_descriptor/       # 单个项目
      src/
        lib/                     # 项目内部函数依赖（不可独立运行）
        scripts/                 # 可复用脚本（可独立运行，也可被调用）
        tests/                   # 单元测试
        main/                    # 实验入口（experiment_XX_xxx.m）
      outputs/                    # 实验产出（按实验分子文件夹）
        experiment_XX_descriptor/
          figures/               # 图表（PNG, FIG, PDF）
          data/                  # 数据（MAT, CSV）
```

**命名与格式规范详见 [FORMAT.md](../FORMAT.md)**：
- File naming：snake_case、禁止数字开头、编号前缀、`.m` 文件名 = 主函数名
- Folder naming：snake_case、能加复数加复数、禁止数字开头、不重复命名
- Case conventions：矩阵/人名/缩写/品牌/希腊字母保留大写，其余全小写
- Content spacing：中英文数字间距规则
- 写完代码后运行 `fix_m_code.py` 自动规范化大小写

**MATLAB 路径**：初始化时由用户指定项目根目录，Claude 扫描该目录下所有含 `.m` 文件的子文件夹，自动计算相对路径并写入项目 CLAUDE.md。不预设目录名——`utils/`、`src/lib/`、`src/scripts/` 只是默认约定的名字。
