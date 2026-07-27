#!/usr/bin/env python3
r"""
中英文数字间距格式化脚本。

基于 scientific-research FORMAT.md 规则，自动修复中文/英文与数字之间的空格：
  中文+数字 → 无空格（中心 1 → 中心1）
  数字+中文 → 无空格（5000 步 → 5000步）
  英文+数字 → 有空格（model1 → model 1）
  数字+英文 → 有空格（100km → 100 km）

保护区域（不修改）：代码块、行内代码、LaTeX 数学、URL、文件路径、下划线标识符

用法：
  python fmt.py <path>              dry-run 预览 diff
  python fmt.py <path> --apply      执行修改（自动备份 .bak）
  python fmt.py <path> --select     逐文件确认
"""

import sys, os, re, difflib, argparse
from pathlib import Path

# Windows 控制台 UTF-8 编码修复
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# ============================================================
# Unicode 字符类（标准 re 不支持 \p{Han}，使用 Unicode 区间）
# ============================================================
CJK = (
    r'一-鿿'      # CJK 统一汉字（基本区）
    r'㐀-䶿'      # CJK 扩展 A
    r'豈-﫿'      # CJK 兼容汉字
)
CJK_CHAR = f'[{CJK}]'
CJK_OR_PUNCT = f'[{CJK}　-〿＀-￯]'  # 含中文标点

# 保护占位符前缀
PH_PREFIX = '__FMT_P_'

# ============================================================
# 保护区域
# ============================================================

def protect_regions(text):
    """将不可修改的区域替换为占位符。返回 (processed_text, dict)。"""
    protected = {}
    counter = [0]

    def ph():
        key = f'{PH_PREFIX}{counter[0]}__'
        counter[0] += 1
        return key

    def repl(m):
        key = ph()
        protected[key] = m.group(0)
        return key

    # 保护顺序由外到内：代码块 → 行内代码 → LaTeX → URL → 文件路径 → 标识符
    # 1. 围栏代码块 ```...```
    text = re.sub(r'```[\s\S]*?```', repl, text)

    # 2. 行内代码 `...`
    text = re.sub(r'`[^`\n]+`', repl, text)

    # 3. LaTeX 块 $$...$$
    text = re.sub(r'\$\$[\s\S]*?\$\$', repl, text)

    # 4. LaTeX 行内 $...$
    text = re.sub(r'\$[^$\n]+\$', repl, text)

    # 5. URL
    text = re.sub(r'https?://[^\s\)\]、，]+', repl, text)

    # 6. 文件路径（Windows 绝对路径、相对路径 ../.../）
    text = re.sub(r'[A-Za-z]:[\\/][^\s,;:、，]+', repl, text)
    text = re.sub(r'(?:\.\.?[/\\])+[^\s,;:、，]+', repl, text)

    # 7. 下划线标识符（snake_case / Pascal_Snake_Case，如 Experiment_01_dec、model_1）
    text = re.sub(r'\b[a-zA-Z][a-zA-Z0-9]*(?:_[a-zA-Z0-9]+)+\b', repl, text)

    return text, protected


def restore_regions(text, protected):
    """还原所有占位符"""
    for key, original in protected.items():
        text = text.replace(key, original)
    return text


# ============================================================
# 间距规则
# ============================================================

def apply_spacing_rules(text):
    """对文本应用全部间距规则。"""

    # --- 中文 ↔ 数字：去空格 ---

    # 规则 1：中文 + 空格 + 数字 → 去空格
    # 例：中心 1 → 中心1、公式 7 → 公式7
    text = re.sub(f'({CJK_CHAR}) +(\\d)', r'\1\2', text)
    # 再处理中文后空格 + 负号 + 数字（如 偏差 - 0.05 → 偏差-0.05 这种不该触发，但不会）
    # 额外：中文标点 + 空格 + 数字（如 值为 0 → 值为0）
    text = re.sub(f'({CJK_OR_PUNCT}) +(\\d)', r'\1\2', text)

    # 规则 2：数字 + 空格 + 中文 → 去空格
    # 例：5000 步 → 5000步、到 5000 后 → 到5000后
    text = re.sub(f'(\\d) +({CJK_CHAR})', r'\1\2', text)
    text = re.sub(f'(\\d) +({CJK_OR_PUNCT})', r'\1\2', text)

    # --- 英文 ↔ 数字：加空格 ---

    # 规则 3：英文字母 + 数字（中间无空格）→ 加空格
    # 例：model1 → model 1、Experiment01 → Experiment 01
    # 下划线标识符已在保护步骤处理，此处放心匹配
    text = re.sub(r'(?<=[a-zA-Z])(\d)', r' \1', text)

    # 规则 4：数字 + 英文字母（中间无空格）→ 加空格
    # 例：100km → 100 km、4800steps → 4800 steps
    # (?<!\d) 避免 "12km" 中的 "2k" 也加空格（\d+ 贪婪匹配到 12 再匹配 k）
    # [a-zA-Z]{2,} 要求至少 2 个字母，避免 2D/1D 维度标记误报
    text = re.sub(r'(?<!\d)(\d+)([a-zA-Z]{2,})', r'\1 \2', text)
    # 撤回序数缩写误报：1st, 2nd, 3rd, 4th 等
    text = re.sub(r'(\d) (st|nd|rd|th)\b', r'\1\2', text)

    return text


# ============================================================
# 文件处理
# ============================================================

def process_file(filepath, apply=False):
    """
    处理单个 .md 文件。
    返回 (diff_text, has_changes) — diff_text 为 None 表示无修改。
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()

    # 保护 → 规则 → 还原
    protected_text, protected = protect_regions(original)
    processed = apply_spacing_rules(protected_text)
    processed = restore_regions(processed, protected)

    if original == processed:
        return None, False

    diff = ''.join(difflib.unified_diff(
        original.splitlines(keepends=True),
        processed.splitlines(keepends=True),
        fromfile=f'a/{os.path.basename(filepath)}',
        tofile=f'b/{os.path.basename(filepath)}',
    ))

    if apply:
        # 备份
        backup = filepath + '.bak'
        with open(backup, 'w', encoding='utf-8') as f:
            f.write(original)
        # 覆盖
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(processed)

    return diff, True


def find_md_files(path):
    """查找路径下的所有 .md 文件。"""
    p = Path(path)
    if p.is_file():
        return [str(p)] if p.suffix == '.md' else []
    if not p.is_dir():
        return []
    files = []
    for root, dirs, filenames in os.walk(p):
        dirs[:] = [d for d in dirs if d not in ('.git', '.obsidian', '.trash', 'node_modules', '.claude')]
        for f in filenames:
            if f.endswith('.md') and not f.endswith('.bak'):
                files.append(os.path.join(root, f))
    return sorted(files)


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='中英文数字间距格式化 — 基于 scientific-research FORMAT.md 规则',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''示例：
  python fmt.py note.md                dry-run 预览
  python fmt.py vault/                 dry-run 预览目录下所有 .md
  python fmt.py note.md --apply        执行修改（自动 .bak 备份）
  python fmt.py vault/  --apply --select  逐文件确认''')
    parser.add_argument('path', help='.md 文件或包含 .md 的目录')
    parser.add_argument('--apply', action='store_true', help='执行修改（默认 dry-run）')
    parser.add_argument('--select', action='store_true', help='逐文件确认是否修改')
    args = parser.parse_args()

    target = args.path
    if not os.path.exists(target):
        print(f'错误：路径不存在 — {target}', file=sys.stderr)
        sys.exit(1)

    md_files = find_md_files(target)
    if not md_files:
        print('未找到 .md 文件')
        sys.exit(0)

    mode = '执行修改' if args.apply else 'dry-run 预览'
    print(f'处理 {len(md_files)} 个 .md 文件 — {mode}')
    print('规则：中文↔数字去空格 | 英文↔数字加空格 | 保护代码/LaTeX/URL/标识符\n')

    changed = 0
    for fp in md_files:
        if args.select:
            ans = input(f'处理 {os.path.basename(fp)}？[y/n/q] ').strip().lower()
            if ans == 'q':
                break
            if ans != 'y':
                continue

        diff, has_changes = process_file(fp, apply=args.apply)
        if has_changes:
            changed += 1
            print(f'── {fp}')
            print(diff)
            if args.apply:
                print(f'  ✓ 已修改（备份 → {fp}.bak）')
        else:
            print(f'  ✓ {fp} — 无需修改')

    print(f'\n完成：{changed}/{len(md_files)} 个文件有修改')
    if not args.apply and changed > 0:
        print('提示：使用 --apply 执行实际修改')  # 末尾空行


if __name__ == '__main__':
    main()
