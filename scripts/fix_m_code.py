#!/usr/bin/env python3
""".m 代码大小写规范化 — 写完代码后自动修复。
规则（来自 FORMAT.md Case conventions）：
  - 矩阵变量（单大写字母 A, B, X, P 等 及 带后缀的 A_z, Sigma_w 等）→ 保留大写
  - 缩写（LMI, DARE, SVD, MCU, FPGA 等）→ 保留
  - 人名（Kalman, Lyapunov, Schur 等）→ 保留
  - 其余标识符（函数名、标量变量、模块名）→ 全小写 snake_case
  - 注释文本 → 全小写（保护 LaTeX、专有名词）

用法：
  python fix_m_code.py <file_or_dir>              dry-run 预览
  python fix_m_code.py <file_or_dir> --apply      执行修改（自动 .bak 备份）
"""
import sys, os, re, argparse
from collections import defaultdict

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except: pass

PH = '__fmc_'

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
}

# 产品/品牌名
BRANDS = {
    'MATLAB', 'Simulink', 'Obsidian', 'Windows', 'Linux', 'GitHub', 'Git',
    'Python', 'VSCode', 'Keil', 'Zotero', 'Anki', 'WACOM', 'FPGA',
}

# 矩阵变量前缀 — 这些前缀开头的变量视为矩阵，保留大写
MATRIX_PREFIXES = {'Sigma_', 'Omega_', 'Gamma_', 'Lambda_', 'Theta_', 'Delta_', 'Pi_'}

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

# 构建保护正则（按长度降序，避免短词先匹配）
_sorted_protected = sorted(ALL_PROTECTED, key=len, reverse=True)
PROTECTED_PATTERN = r'\b(?:' + '|'.join(re.escape(w) for w in _sorted_protected) + r')\b'


# ============================================================
# 判断标识符是否应保留大写
# ============================================================

def should_keep_case(name):
    """判断标识符是否应保留大写。"""
    # 1. 白名单
    if name in ALL_PROTECTED:
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
    # 5. 专有名词/缩写白名单
    text = re.sub(PROTECTED_PATTERN, rp, text)
    # 6. 希腊字母（Unicode）— 保护 Ω, ω, Δ 等
    text = re.sub(r'[Α-Ωα-ω]+', rp, text)
    # 7. 矩阵变量：A, A_z, A_{z,ω} — 单大写字母+下标（后面不能是小写字母）
    text = re.sub(r'\b[A-Z](?:_\{[^}]+\}|_[a-z0-9]+)?(?![a-z])', rp, text)
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
    """处理一行 .m 代码。返回 (new_line, changed)。"""
    stripped = line.lstrip()
    # 纯注释行
    if stripped.startswith('%'):
        indent = line[:len(line) - len(stripped)]
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
            return indent + comment_marker + lc, True
        return line, False

    # 代码行（可能带行尾注释）
    # 分离代码和行尾注释
    # 注意：字符串内的 % 和转义的 \% 不能算注释
    code_part = line.rstrip('\n\r')
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

    return new_line + ('\n' if line.endswith('\n') else ''), changed


# ============================================================
# 文件处理
# ============================================================

def process_file(filepath, apply=False):
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    changed_lines = 0
    new_lines = []
    for line in lines:
        nl, ch = process_line(line)
        new_lines.append(nl)
        if ch:
            changed_lines += 1

    if changed_lines == 0:
        return False, 0

    if apply:
        with open(filepath + '.bak', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

    return True, changed_lines


# ============================================================
# 主流程
# ============================================================

def main():
    p = argparse.ArgumentParser(
        description='.m 代码大小写规范化',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''示例：
  python fix_m_code.py src/                 dry-run 预览
  python fix_m_code.py src/ --apply         执行修改（自动 .bak 备份）
  python fix_m_code.py experiment_03.m --apply  单文件修改''')
    p.add_argument('path', help='.m 文件或目录')
    p.add_argument('--apply', action='store_true', help='执行修改（默认 dry-run）')
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

    if not mfiles:
        print('未找到 .m 文件')
        return

    total_files = 0
    total_lines = 0
    for fp in sorted(mfiles):
        ok, n = process_file(fp, apply=a.apply)
        if ok:
            total_files += 1
            total_lines += n
            status = '✓' if a.apply else '~'
            print(f'  {status} {os.path.relpath(fp, target)} ({n} 行)')

    if not a.apply:
        print(f'\n[dry-run] {total_files} 个文件 {total_lines} 行需修改，使用 --apply 执行')
    else:
        print(f'\n完成：{total_files} 个文件 {total_lines} 行已修改')
        print('备份文件 (*.bak) 已生成，确认无误后可删除。')


if __name__ == '__main__':
    main()
