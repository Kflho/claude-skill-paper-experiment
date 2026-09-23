#!/usr/bin/env python3
""".m 代码大小写规范化 — 写完代码后自动修复。

保护范围（白名单之外一律小写化）：
  - 代码：白名单词、单大写字母（A）、A_z 式下标、≤4 位全大写、含 ≥2 个大写、
          Sigma_ 等矩阵前缀；`对象.属性` 的属性名一律不改（其大小写由外部 API 定义）
  - 注释：白名单词、$...$ LaTeX、URL、路径、单引号字符串、希腊字母、单大写矩阵变量、
          全大写缩略语（FAR / SNR / KS）、标签+序号（Theorem 1 / Model 3 / Table I / Fig. 2）、
          单位与维度标签（3dB / 20kHz / 2D cell array）、中文紧邻的符号（条件A / 矩阵Q）
  - 其余标识符（函数名、标量变量、模块名）→ 全小写 snake_case；其余注释词 → 小写

本工具对上下文无感知，改动须逐 hunk 审查（先用 --diff 看，再 --apply）：
  - 反复被误改的词（Snr、Montgomery 等）写进项目词表，一次加入永久生效
  - 已知边界：`'` 既可能是转置也可能是字符串起点，行内注释的分界可能判错

用法：
  python fix_m_code.py <file_or_dir> --diff       dry-run 并打印 diff（逐 hunk 审查用）
  python fix_m_code.py <file_or_dir> --apply      执行修改（自动 .bak 备份）
  python fix_m_code.py <file_or_dir> --check      dry-run；有需修改处则退出码 1

项目词表：`.fix_m_code_protect`（从目标文件所在目录向上查找，每行一个词，`#` 起注释）
"""
import sys, os, re, argparse, difflib
from collections import defaultdict

if sys.platform == 'win32':
    # 中文报错在 GBK 控制台上会变乱码，恰好是出错时最需要读的一段
    for _stream in (sys.stdout, sys.stderr):
        try: _stream.reconfigure(encoding='utf-8', errors='replace')
        except: pass

PH = '__fmc_'

# ASCII 词边界：Python 的 `\b` 把 CJK 也算词字符，于是 `条件A`、`矩阵Q` 这类
# 中文紧邻的符号拿不到边界，整条保护规则静默失效（实测：`条件A` → `条件a`，
# 切断了与下文 `故障源在 S_i ⟺ A ∧ B` 的对应）。这里把边界定义为「非 ASCII
# 词字符」——中文、全角括号、箭头都算分隔符，保护规则照常生效。
NB_L = r'(?<![A-Za-z0-9_])'
NB_R = r'(?![A-Za-z0-9_])'

# ============================================================
# 保护白名单 — 不应被小写化的标识符
# ============================================================

# 全大写缩写（2-6 字母，不含下划线）
ACRONYMS = {
    'LMI', 'DARE', 'SVD', 'CPU', 'MCU', 'PCB', 'FPGA', 'PID', 'LQR', 'LQG',
    'MIMO', 'SISO', 'ARE', 'LTI', 'LTV', 'ODE', 'PDE',
    'FDI', 'FTC', 'SoS', 'CPS', 'FDIA', 'ISA',
    'RAM', 'ROM', 'GPU', 'USB', 'HDMI', 'API', 'SDK', 'IDE', 'CLI', 'GUI',
    'CSV', 'JSON', 'XML', 'YAML', 'HTML', 'CSS', 'SQL', 'HTTP', 'FTP', 'SSH',
    'IIR', 'FIR', 'FFT', 'DFT', 'DCT', 'PSD',
}

# 人名 / 专有名词
PROPER_NOUNS = {
    'Kalman', 'Lyapunov', 'Schur', 'Luenberger', 'Riccati', 'Kronecker',
    'Gaussian', 'Laplace', 'Fourier', 'Markov', 'Cauchy', 'Euler',
    'Taylor', 'Newton', 'Runge', 'Kutta', 'Lagrange', 'Hamilton',
    'Jacobi', 'Gauss', 'Seidel', 'Chebyshev', 'Legendre',
    'Weierstrass', 'Boltzmann', 'Maxwell', 'Poisson', 'Helmholtz',
    'Bayes', 'Bernoulli', 'Fisher', 'Pearson', 'Wilcoxon',
    'Frobenius', 'Hermitian', 'Toeplitz', 'Hankel', 'Cholesky', 'Hadamard',
}

# 产品/品牌名
BRANDS = {
    'MATLAB', 'Simulink', 'Obsidian', 'Windows', 'Linux', 'GitHub', 'Git',
    'Python', 'VSCode', 'Keil', 'Zotero', 'Anki', 'WACOM', 'FPGA',
}

# 计量单位 — 大小写是单位符号的一部分（小写化会把 dB 变成 db、Hz 变成 hz）
# 只列大小写会变的：全小写单位（ms / rpm）小写化后不变，列进来是空配置
UNITS = {
    'dB', 'dBm', 'dBW', 'Hz', 'kHz', 'MHz', 'GHz', 'THz',
    'kW', 'kWh', 'mW', 'uW', 'mA', 'kV', 'kOhm', 'degC',
}

# 维度标签（1D/2D/3D 数组）— 与单位同样贴着数字写，边界规则共用
DIMENSION_TAGS = {'1D', '2D', '3D'}

# 矩阵变量前缀 — 这些前缀开头的变量视为矩阵，保留大写
MATRIX_PREFIXES = {'Sigma_', 'Omega_', 'Gamma_', 'Lambda_', 'Theta_', 'Delta_', 'Pi_'}

# 论文符号名（无下标时也可独立成段：eig_Sigma, Phi_dc）
GREEK_SYMBOLS = {'Sigma', 'Omega', 'Gamma', 'Lambda', 'Theta', 'Delta', 'Pi',
                 'Phi', 'Psi', 'Xi', 'Eta', 'Mu', 'Nu', 'Rho', 'Tau', 'Chi'}

# 独立的论文符号段：单大写字母（A）、字母+数字（H1, M2）、两字符符号（Az, Cg, Sv, Jw）
SYMBOL_SEGMENT = re.compile(r'^[A-Z]$|^[A-Z][0-9]+$|^[A-Z][a-z]$')


def has_paper_symbol(name):
    """名字里是否含完整的论文符号段（err_A / rank_H1 / use_exact_Cg / Az_w / eig_Sigma）。

    项目约定：变量的符号部分按论文写法保留大写（矩阵/协方差符号），因此整名不改。
    按 `_` 分段，段内再按大小写边界切（err_A → [err, A]；useExactCg → [use, Exact, Cg]）。
    """
    for seg in re.split(r'_+', name):
        for part in re.findall(r'[A-Z]+(?![a-z])|[A-Z][a-z]*|[a-z]+|[0-9]+', seg):
            if part in GREEK_SYMBOLS or SYMBOL_SEGMENT.match(part):
                return True
    return False

# MATLAB 内置函数/关键字 — 不参与重命名
MATLAB_BUILTINS = {
    'function', 'end', 'if', 'else', 'elseif', 'for', 'while', 'switch', 'case',
    'otherwise', 'try', 'catch', 'return', 'break', 'continue', 'global', 'persistent',
    'classdef', 'properties', 'methods', 'events', 'enumeration', 'arguments',
    'true', 'false', 'inf', 'NaN', 'pi', 'i', 'j', 'eps', 'realmax', 'realmin',
    'sparse', 'zeros', 'ones', 'eye', 'diag', 'blkdiag', 'length', 'size', 'numel',
    'exist', 'isempty', 'isfield', 'isnan', 'isinf', 'isreal', 'iscell', 'isstruct',
    'disp', 'fprintf', 'sprintf', 'error', 'warning', 'assert',
    'load', 'save', 'clear', 'clc', 'close', 'close all',
    'figure', 'plot', 'subplot', 'hold', 'grid', 'xlabel', 'ylabel', 'title', 'legend',
    'cell', 'struct', 'double', 'int', 'char', 'logical', 'string',
    'nargin', 'nargout', 'varargin', 'varargout',
    'abs', 'sqrt', 'sin', 'cos', 'tan', 'exp', 'log', 'log10', 'log2',
    'max', 'min', 'sum', 'mean', 'std', 'var', 'sort', 'find', 'unique',
    'rand', 'randn', 'randi', 'rng',
    'svd', 'eig', 'chol', 'lu', 'qr', 'inv', 'pinv', 'det', 'rank', 'trace', 'norm',
    'dare', 'care', 'lyap', 'dlyap', 'lmi', 'feasp', 'gevp', 'mincx', 'decnbr', 'dec2mat',
    'setlmis', 'getlmis', 'lmivar', 'lmiterm', 'newlmi',
    'ss', 'tf', 'zpk', 'feedback', 'series', 'parallel', 'connect',
    'step', 'impulse', 'lsim', 'bode', 'nyquist', 'margin',
    'sdpvar', 'optimize', 'value', 'solvesdp', 'set', 'yalmip',
    'cd', 'ls', 'pwd', 'mkdir', 'addpath', 'genpath', 'rmpath', 'path',
    'run', 'eval', 'feval', 'str2func', 'func2str', 'strcmp', 'strcmpi',
    'repmat', 'reshape', 'kron', 'cross', 'dot',
    'linspace', 'logspace', 'meshgrid', 'ndgrid',
    'sprintf', 'fopen', 'fclose', 'fread', 'fwrite', 'fprintf', 'fscanf',
}

ALL_PROTECTED = ACRONYMS | PROPER_NOUNS | BRANDS | MATLAB_BUILTINS

# 运行期追加的保护词：项目词表 (.fix_m_code_protect) + --protect，在 main() 中载入
EXTRA_PROTECTED = set()

# `对象.属性` 的属性名是否保护（--no-protect-properties 关闭）
PROTECT_PROPERTIES = True

DICT_NAME = '.fix_m_code_protect'


def build_protected_pattern():
    """按当前保护词表构建正则（长词优先，避免短词先匹配）。"""
    words = sorted(ALL_PROTECTED | EXTRA_PROTECTED, key=len, reverse=True)
    return NB_L + r'(?:' + '|'.join(re.escape(w) for w in words) + r')' + NB_R


PROTECTED_PATTERN = build_protected_pattern()


def build_units_pattern():
    """符号化写法的正则：左侧边界允许紧跟在数字后（3dB / 20kHz / 2D 分块）。

    这类词贴着数字写是常态，而数字属 ASCII 词字符，若沿用 NB_L 就整条失配
    （实测：`3dB` → `3db`、`2D cell array` → `2d`）；左侧只排除字母与下划线，
    右侧照旧排除全部词字符，这样 `xdB` 这类标识符不受影响。
    """
    words = sorted(UNITS | DIMENSION_TAGS, key=len, reverse=True)
    return r'(?<![A-Za-z_])(?:' + '|'.join(re.escape(w) for w in words) + r')' + NB_R


UNITS_PATTERN = build_units_pattern()


def read_dict_file(path):
    """读保护词表：每行一个词，`#` 起注释。"""
    toks = set()
    with open(path, 'r', encoding='utf-8', errors='replace') as fh:
        for ln in fh:
            ln = ln.split('#')[0].strip()
            if ln:
                toks.add(ln)
    return toks


def load_project_dict(start_dir):
    """向上查找所有 .fix_m_code_protect 并合并（近处=项目专属，高处=跨项目共用）。

    返回 (词集合, [命中的词表文件…])。
    """
    toks, found = set(), []
    d = os.path.abspath(start_dir)
    while True:
        f = os.path.join(d, DICT_NAME)
        if os.path.isfile(f):
            toks |= read_dict_file(f)
            found.append(f)
        parent = os.path.dirname(d)
        if parent == d:
            return toks, found
        d = parent


# ============================================================
# 判断标识符是否应保留大写
# ============================================================

def should_keep_case(name):
    """判断标识符是否应保留大写。"""
    # 0. 占位符保护 — 不可被 to_snake 的 strip('_') 裁切
    if name.startswith(PH):
        return True
    # 1. 白名单（ALL_PROTECTED + 项目词表/--protect 追加词）
    if name in ALL_PROTECTED or name in EXTRA_PROTECTED:
        return True

    # 2. 单字母大写 → 矩阵变量 (A, B, X, P, Q, R, U, Y, K, L, M, N, H, G, F, J, W, V, Z, T, S, D, C, E, O, I)
    if len(name) == 1 and name.isupper():
        return True

    # 3. 单大写字母后接下划线 → 矩阵带下标 (A_z, B_g, L_omega, C_s 等)
    #    模式: 一个大写字母 + _ + 小写字母/数字
    if re.match(r'^[A-Z]_[a-z0-9]', name):
        return True

    # 4. 全大写缩写已在白名单中，这里处理未列出的
    if len(name) <= 4 and name == name.upper() and '_' not in name:
        return True  # 可能是未列出的缩写，保守保留

    # 5. 已知矩阵前缀 (Sigma_, Gamma_ 等)
    for prefix in MATRIX_PREFIXES:
        if name.startswith(prefix):
            return True

    # 6. 开头大写 + 下划线 → 可能是有意的大写变量 (Omega_count, B_bar)
    #    如果只有一个大写字母在开头，且长度 >= 4 → 可能是标量，应小写
    #    如果有多个大写字母 → 可能是缩写组合，保留
    upper_count = sum(1 for c in name if c.isupper())
    if upper_count >= 2:
        return True  # 多字母大写组合，疑为缩写

    # 7. 含完整论文符号段 → 按论文写法保留（err_A, rank_H, use_exact_Cg, Az_w）
    if has_paper_symbol(name):
        return True

    return False


def to_snake(name):
    """将标识符转为 snake_case。PascalCase → snake_case, CamelCase → snake_case。"""
    result = name
    # PascalCase / CamelCase: 大写前加下划线
    result = re.sub(r'(?<=[a-z0-9])([A-Z])', r'_\1', result)
    result = result.lower()
    result = re.sub(r'_+', '_', result)
    result = result.strip('_')
    return result


# ============================================================
# 保护机制
# ============================================================

def protect_regions(text):
    """保护字符串、LaTeX、URL、文件路径 → 占位符"""
    p, c = {}, [0]
    def ph(): key = f'{PH}{c[0]}__'; c[0] += 1; return key
    def rp(m): key = ph(); p[key] = m.group(0); return key

    # LaTeX
    text = re.sub(r'\$\$[\s\S]*?\$\$', rp, text)
    text = re.sub(r'\$[^$\n]+\$', rp, text)
    # 字符串
    text = re.sub(r"'[^'\n]*'", rp, text)
    # URL
    text = re.sub(r'https?://[^\s\)\]、，\n]+', rp, text)
    # 文件路径
    text = re.sub(r'[A-Za-z]:[\\/][^\s,;:、，\n]+', rp, text)
    return text, p


def protect_dotted(text, store, counter):
    """保护 `对象.属性` 的属性名 → 占位符。

    属性名的大小写由该对象的 API 定义（Simulink timeseries 等），格式化器看不出
    哪些对象是外部的 → 一律不改（format.md「外部 API 属性名」）。定义处与引用处
    都是 `对象.属性`，两边一致保留，不会出现半改半不改。
    """
    def rp(m):
        key = f'{PH}prop{counter[0]}__'; counter[0] += 1
        store[key] = m.group(0)
        return key
    return re.sub(r'(?<=\.)[A-Za-z_][A-Za-z0-9_]*', rp, text)


def protect_comment(text):
    """保护注释中不应小写的内容 → 占位符"""
    p, c = {}, [0]
    def ph(): key = f'{PH}{c[0]}__'; c[0] += 1; return key
    def rp(m): key = ph(); p[key] = m.group(0); return key

    # 1. LaTeX（必须在矩阵模式之前，因为 $A_z$ 内的是 LaTeX）
    text = re.sub(r'\$\$[\s\S]*?\$\$', rp, text)
    text = re.sub(r'\$[^$\n]+\$', rp, text)
    # 2. URL
    text = re.sub(r'https?://[^\s\)\]、，\n]+', rp, text)
    # 3. 文件路径
    text = re.sub(r'[A-Za-z]:[\\/][^\s,;:、，\n]+', rp, text)
    # 4. 字符串
    text = re.sub(r"'[^'\n]*'", rp, text)
    # 5. 专有名词/缩写白名单（含项目词表）
    text = re.sub(PROTECTED_PATTERN, rp, text)
    # 5u. 计量单位（3dB / 20kHz）— 边界规则与白名单不同，单独一趟
    text = re.sub(UNITS_PATTERN, rp, text)
    # 5b. 标签 + 序号（Theorem 1 / Model 3 / Table II / Fig. 2 / Eq. (26)）
    #     必须排在 5c 之前：5c 会把序号 II 先占成占位符，5b 的向前看就落空了
    text = re.sub(NB_L + r'[A-Z][a-z]+' + NB_R + r'(?=\s*\.?\s*\(?\s*[0-9IVX]+' + NB_R + ')',
                  rp, text)
    # 5c. 全大写缩略语（FAR, SNR, KS, RMS…）— 白名单未列出的也保留
    text = re.sub(NB_L + r'[A-Z][A-Z0-9]{1,}' + NB_R, rp, text)
    # 5d. 含论文符号段的标识符（err_A / rank_H / Cg_w）— 与代码里的写法保持一致
    text = re.sub(NB_L + r'[A-Za-z_][A-Za-z0-9_]*' + NB_R,
                  lambda m: rp(m) if has_paper_symbol(m.group(0)) else m.group(0), text)
    # 6. 希腊字母（Unicode）— 保护 Ω, ω, Δ 等
    text = re.sub(r'[Α-Ωα-ω]+', rp, text)
    # 7. 矩阵变量：A, A_z, A_{z,ω} — 单大写字母+下标（后面不能是小写字母）
    text = re.sub(NB_L + r'[A-Z](?:_\{[^}]+\}|_[a-z0-9]+)?(?![a-z])', rp, text)
    # 8. #ok<...> pragma（注释内容不含 % 前缀）
    text = re.sub(r'#ok<[^>]+>', rp, text)
    return text, p

def restore_regions(text, p):
    for k, v in p.items():
        text = text.replace(k, v)
    while PH in text:
        for k, v in p.items():
            text = text.replace(k, v)
    return text


# ============================================================
# 行处理
# ============================================================

def process_line(line):
    """处理一行 .m 代码。返回 (new_line, changed)。

    行尾符（CRLF/LF）原样保留：改文件的工具不得顺手改行尾，否则 diff 全是噪声。
    """
    body = line.rstrip('\r\n')
    eol = line[len(body):]

    stripped = body.lstrip()
    # 纯注释行
    if stripped.startswith('%'):
        indent = body[:len(body) - len(stripped)]
        comment_marker = '%'
        if stripped.startswith('%%'):
            comment_marker = '%%'
            content = stripped[2:]
        else:
            content = stripped[1:]

        if not content.strip():
            return line, False

        pt, pd = protect_comment(content)
        lc = pt.lower()
        lc = restore_regions(lc, pd)
        if lc != content:
            return indent + comment_marker + lc + eol, True
        return line, False

    # 代码行（可能带行尾注释）
    # 分离代码和行尾注释
    # 注意：字符串内的 % 和转义的 \% 不能算注释
    code_part = body
    comment_part = ''

    # 简单处理：找最后一个不在字符串中的 %
    in_string = False
    string_char = None
    for i, ch in enumerate(code_part):
        if in_string:
            if ch == string_char and (i == 0 or code_part[i-1] != '\\'):
                in_string = False
        else:
            if ch in ("'", '"'):
                in_string = True
                string_char = ch
            elif ch == '%':
                # 确认前面不是转义的
                if i == 0 or code_part[i-1] != '\\':
                    comment_part = code_part[i:]
                    code_part = code_part[:i]
                    break

    # 处理代码部分：替换标识符
    new_code = code_part
    changed = False

    # 保护字符串、LaTeX
    pt, pd = protect_regions(code_part)

    # 保护 `对象.属性` 的属性名
    if PROTECT_PROPERTIES:
        pt = protect_dotted(pt, pd, [0])

    # 找到所有标识符并替换
    def repl_ident(m):
        nonlocal changed
        name = m.group(0)
        if should_keep_case(name):
            return name
        new_name = to_snake(name)
        if new_name != name:
            changed = True
            return new_name
        return name

    pt = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', repl_ident, pt)
    new_code = restore_regions(pt, pd)

    # 处理注释部分（小写化）
    if comment_part:
        comment_content = comment_part[1:]  # 去掉 %
        pt_c, pd_c = protect_comment(comment_content)
        lc = pt_c.lower()
        lc = restore_regions(lc, pd_c)
        if lc != comment_content:
            changed = True
            new_comment = '%' + lc
        else:
            new_comment = comment_part
        new_line = new_code + new_comment
    else:
        new_line = new_code

    return new_line + eol, changed


# ============================================================
# 文件处理
# ============================================================

def read_lines(filepath):
    """按 UTF-8 读文件；不是 UTF-8（如 GBK 编码的 .m）就报错，绝不按 UTF-8 覆写回去。"""
    with open(filepath, 'rb') as f:
        raw = f.read()
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError as e:
        raise RuntimeError(f'非 UTF-8 编码，拒绝改写（会损坏中文注释）— {e}')
    return text.splitlines(keepends=True)


def process_file(filepath, apply=False, show_diff=False, no_backup=False):
    lines = read_lines(filepath)

    changed_lines = 0
    new_lines = []
    for line in lines:
        nl, ch = process_line(line)
        new_lines.append(nl)
        if ch:
            changed_lines += 1

    if changed_lines == 0:
        return False, 0

    if show_diff:
        # 行尾统一去掉 CR/LF，否则 diff 输出里混入 ^M
        diff = difflib.unified_diff(
            [l.rstrip('\r\n') for l in lines],
            [l.rstrip('\r\n') for l in new_lines],
            fromfile=filepath, tofile=filepath + ' (格式化后)', lineterm='', n=1)
        for d in diff:
            print('    ' + d)

    if apply:
        bak = filepath + '.bak'
        if os.path.exists(bak):
            print(f'  ! 已存在备份 {bak}（上次审查未收尾？将被覆盖）', file=sys.stderr)
        # newline='' 关掉换行符翻译：写入内容与读到的字节逐行一致
        if not no_backup:
            with open(bak, 'w', encoding='utf-8', newline='') as f:
                f.writelines(lines)
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            f.writelines(new_lines)

    return True, changed_lines


# ============================================================
# 主流程
# ============================================================

def main():
    global PROTECTED_PATTERN, PROTECT_PROPERTIES
    p = argparse.ArgumentParser(
        description='.m 代码大小写规范化',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''示例：
  python fix_m_code.py src/ --diff              dry-run 并打印 diff（逐 hunk 审查）
  python fix_m_code.py src/ --apply             执行修改（自动 .bak 备份）
  python fix_m_code.py experiment_03.m --apply  单文件修改
  python fix_m_code.py . --protect Snr,Runger   本次运行额外保护两个词''')
    p.add_argument('path', help='.m 文件或目录')
    p.add_argument('--apply', action='store_true', help='执行修改（默认 dry-run）')
    p.add_argument('--diff', action='store_true', help='dry-run 并打印 unified diff（逐 hunk 审查）')
    p.add_argument('--check', action='store_true', help='dry-run；有需修改处则退出码 1')
    p.add_argument('--protect', action='append', default=[], metavar='词[,词]',
                   help='本次运行追加的保护词（可重复，逗号/空格分隔）')
    p.add_argument('--dictionary', metavar='FILE',
                   help=f'保护词表文件（默认从目标目录向上查找 {DICT_NAME}）')
    p.add_argument('--no-protect-properties', action='store_true',
                   help='不保护 `对象.属性` 的属性名（默认保护）')
    p.add_argument('--no-backup', action='store_true',
                   help='不写 .bak（确认已有 git 备份时才用）')
    a = p.parse_args()

    target = a.path
    mfiles = []
    if os.path.isfile(target):
        mfiles = [target]
    elif os.path.isdir(target):
        for r, ds, fs in os.walk(target):
            ds[:] = [d for d in ds if d not in {'.git', '.old', 'node_modules'}]
            for f in fs:
                if f.endswith('.m') and not f.endswith('.bak'):
                    mfiles.append(os.path.join(r, f))
    else:
        print(f'错误：路径不存在 — {target}', file=sys.stderr)
        sys.exit(1)

    base = target if os.path.isdir(target) else os.path.dirname(os.path.abspath(target))

    # 保护词表：项目词表（自动查找或 --dictionary 指定）+ --protect 追加
    if a.dictionary:
        if not os.path.isfile(a.dictionary):
            print(f'错误：词表文件不存在 — {a.dictionary}', file=sys.stderr)
            sys.exit(1)
        toks, dpaths = read_dict_file(a.dictionary), [a.dictionary]
    else:
        toks, dpaths = load_project_dict(base)
    EXTRA_PROTECTED.update(toks)
    for chunk in a.protect:
        EXTRA_PROTECTED.update(w for w in re.split(r'[,\s]+', chunk) if w)
    if a.no_protect_properties:
        PROTECT_PROPERTIES = False
    PROTECTED_PATTERN = build_protected_pattern()

    if not mfiles:
        print('未找到 .m 文件')
        return

    # 先报本次生效的保护配置，再动手（审查时才知道什么被保护了）
    print(f'目标：{target}')
    for dpath in dpaths:
        print(f'词表：{dpath}')
    print(f'词表合计：{len(toks)} 词' if toks else '词表：无')
    added = EXTRA_PROTECTED - toks
    if added:
        print(f'--protect 追加：{" ".join(sorted(added))}')
    print(f'属性名保护：{"开（对象.属性 一律不改）" if PROTECT_PROPERTIES else "关"}')

    total_files = 0
    total_lines = 0
    errors = 0
    for fp in sorted(mfiles):
        try:
            ok, n = process_file(fp, apply=a.apply, show_diff=a.diff, no_backup=a.no_backup)
        except RuntimeError as e:
            print(f'  ! {os.path.relpath(fp, base)} — {e}', file=sys.stderr)
            errors += 1
            continue
        if ok:
            total_files += 1
            total_lines += n
            status = '✓' if a.apply else '~'
            print(f'  {status} {os.path.relpath(fp, base)} ({n} 行)')

    if errors:
        print(f'\n{errors} 个文件因编码问题跳过（未改动）', file=sys.stderr)

    if a.apply:
        print(f'\n完成：{total_files} 个文件 {total_lines} 行已修改')
        if not a.no_backup:
            print('备份 (*.bak) 已生成，审查通过后删除，例如：find . -name "*.m.bak" -delete')
    elif a.check:
        print(f'\n[check] {total_files} 个文件 {total_lines} 行待规范')
        sys.exit(1 if (total_files or errors) else 0)
    else:
        print(f'\n[dry-run] {total_files} 个文件 {total_lines} 行需修改，使用 --apply 执行')
    if errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
