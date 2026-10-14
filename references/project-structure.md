# Project structure

此 skill 创建新项目时默认采用以下约定。**目录名是默认约定，不是硬性规则**——若用户已有现成项目结构，初始化时扫描实际目录自动适配，不强行改名、不强制迁移。

## 领域与项目

项目按**领域**就地存放，不集中到一个全局项目文件夹里。每个领域一根，根下两层：

```
<领域根>/                        # 如 D:\...\programming\Matlab\
  utils/                         # 跨项目共享代码（与 projects/ 同级）
  projects/
    <分类>/                      # 领域内的项目分类，如 postgraduate/
      <缩写>_<编号>/             # 单个项目，如 pg_01/
```

- **文件夹一律不带空格**，下划线分隔（`pg_01`、`js_03`）
- **笔记（Obsidian 侧）同名前缀可带空格**（`pg 01 note.md`）——笔记给人读、代码给机器跑，两套命名各自成立，不要互相拉平
- 分类缩写与编号跟项目登记表保持一致（`pg` = 研究生项目、`js` = javascript、`ug` = 本科）
- 一个项目有多个子任务时：**代码侧仍是一个项目文件夹**，子任务在五文件（note/src/report）里区分

## 项目内部

```
<项目>/
  dev/                           # 开发相关（原型验证、过程记录、临时试验）
  src/                           # 代码
    lib/                         # 项目内部函数依赖（不可独立运行）
    scripts/                     # 可复用脚本（可独立运行，也可被调用）
    tests/                       # 单元测试
    main/                        # 实验入口（experiment_XX_xxx.m）
  bin/                           # 资产与产物
    doc/                         # 项目文档（任务书、流程）
    template/                    # 模板
    images/                      # 实验图片（PNG）
      cn/experiment_XX_descriptor/
      eng/experiment_XX_descriptor/
    data/                        # 实验数据（MAT、CSV）
      cn/experiment_XX_descriptor/
      eng/experiment_XX_descriptor/
    references/                  # 参考文献（论文 PDF / markdown）
    exports/                     # 论文本体（LaTeX 工程）
```

三条职责分界：

- **`dev/` = 过程**：原型、throwaway 代码、排查记录。可以乱，可以删。
- **`src/` = 代码**：正式实验代码，走 tdd 流程，命名与格式受 format.md 约束。
- **`bin/` = 资产与产物**：要留存、要交付、要被论文引用的东西。**实验产出不再使用 `outputs/`**——图进 `bin/images/`，数据进 `bin/data/`，论文进 `bin/exports/`。

`bin/` 的子目录**按需建**，不必一次建齐；`doc/`、`template/` 这类用不到就不建。上述名称是默认值，实际项目里叫别的名字（如 `figures/`、`assets/`）就按实际名字记录，不强制迁移。

**命名与格式规范详见 [format.md](format.md)**：
- File naming：snake_case、禁止数字开头、编号前缀、`.m` 文件名 = 主函数名
- Folder naming：snake_case、能加复数加复数、禁止数字开头、不重复命名、**不带空格**
- Note naming：小写 + 空格（`pg 01 note.md`），与文件夹命名是两套规则
- Case conventions：矩阵/人名/缩写/品牌/希腊字母保留大写，其余全小写
- Content spacing：中英文数字间距规则
- 写完代码后按 [scripts.md](scripts.md) 的格式化工作流规范化大小写（**有罪推定**逐 hunk 审查 diff）

**MATLAB 路径**：初始化时由用户指定项目根目录，Claude 扫描该目录下所有含 `.m` 文件的子文件夹，自动计算相对路径并写入项目 CLAUDE.md。不预设目录名——`utils/`、`src/lib/`、`src/scripts/` 只是默认约定的名字。

### 路径强制规则

**所有脚本中的路径必须使用相对路径，禁止硬编码绝对路径（如 `D:\data\...`、`C:\Users\...`）。** 保证整个项目根目录移动到任意位置后脚本仍可正常运行。

- `addpath`、`save`、`saveas`、`load`、文件读写 —— 一律用相对路径
- 相对路径基准：脚本所在目录（即脚本从哪个目录运行，就是那个目录）
- MATLAB 的 `addpath` 基于 `pwd`，因此务必从脚本所在目录运行（`cd` 到 `src/main/` / `src/tests/` / `src/scripts/` 后再执行）

产出文件写到 `../../bin/images/{cn,eng}/experiment_XX_xxx/` 与 `../../bin/data/{cn,eng}/experiment_XX_xxx/` 下对应子目录，禁止写到项目外路径。

CLAUDE.md 中应包含完整的路径解析表，让后续工作一目了然：

```markdown
| 相对路径 | 解析目标 |
|---|---|
| `../../../../../utils/` | 仓库根工具库 |
| `../lib/` | 项目内部函数 |
| `../scripts/` | 可复用脚本 |
| `../../bin/images/cn/experiment_XX_xxx/` | 中文版实验图表目录 |
| `../../bin/images/eng/experiment_XX_xxx/` | 英文版实验图表目录 |
| `../../bin/data/cn/experiment_XX_xxx/` | 中文版实验数据目录 |
| `../../bin/data/eng/experiment_XX_xxx/` | 英文版实验数据目录 |
```
