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
      outputs/                    # 实验产出（先按语言分 cn/eng，再按实验分子文件夹）
        cn/                       # 中文版实验产出
          experiment_XX_descriptor/
            figures/             # 图表（PNG）
            data/                # 数据（MAT, CSV）
        eng/                      # 英文版实验产出
          experiment_XX_descriptor/
            figures/             # 图表（PNG）
            data/                # 数据（MAT, CSV）
```

**命名与格式规范详见 [format.md](format.md)**：
- File naming：snake_case、禁止数字开头、编号前缀、`.m` 文件名 = 主函数名
- Folder naming：snake_case、能加复数加复数、禁止数字开头、不重复命名
- Case conventions：矩阵/人名/缩写/品牌/希腊字母保留大写，其余全小写
- Content spacing：中英文数字间距规则
- 写完代码后运行 `fix_m_code.py` 自动规范化大小写

**MATLAB 路径**：初始化时由用户指定项目根目录，Claude 扫描该目录下所有含 `.m` 文件的子文件夹，自动计算相对路径并写入项目 CLAUDE.md。不预设目录名——`utils/`、`src/lib/`、`src/scripts/` 只是默认约定的名字。

### 路径强制规则

**所有脚本中的路径必须使用相对路径，禁止硬编码绝对路径（如 `D:\data\...`、`C:\Users\...`）。** 保证整个项目根目录移动到任意位置后脚本仍可正常运行。

- `addpath`、`save`、`saveas`、`load`、文件读写 —— 一律用相对路径
- 相对路径基准：脚本所在目录（即脚本从哪个目录运行，就是那个目录）
- MATLAB 的 `addpath` 基于 `pwd`，因此务必从脚本所在目录运行（`cd` 到 `src/main/` / `src/tests/` / `src/scripts/` 后再执行）

产出文件写到 `../../outputs/{cn,eng}/experiment_XX_xxx/` 下对应子文件夹，禁止写到项目外路径。

CLAUDE.md 中应包含完整的路径解析表，让后续工作一目了然：

```markdown
| 相对路径 | 解析目标 |
|---|---|
| `../../../../../utils/` | 仓库根工具库 |
| `../lib/` | 项目内部函数 |
| `../scripts/` | 可复用脚本 |
| `../../outputs/cn/experiment_XX_xxx/` | 中文版实验产出目录 |
| `../../outputs/eng/experiment_XX_xxx/` | 英文版实验产出目录 |
```
