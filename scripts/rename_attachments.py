#!/usr/bin/env python3
"""将 vault 中所有 Attachments/ 目录重命名为 attachments/，并更新 .md 中的路径引用。"""
import sys, os, re, argparse
from pathlib import Path

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

SKIP_DIRS = {'.obsidian', '.git', '.trash', '.claude', 'node_modules'}

# ============================================================
# 保护区域（同 normalize_vault.py）
# ============================================================
PH_PREFIX = '__AR_P_'

def protect_regions(text):
    protected, counter = {}, [0]
    def ph():
        key = f'{PH_PREFIX}{counter[0]}__'
        counter[0] += 1
        return key
    def repl(m):
        key = ph()
        protected[key] = m.group(0)
        return key
    text = re.sub(r'```[\s\S]*?```', repl, text)
    text = re.sub(r'`[^`\n]+`', repl, text)
    text = re.sub(r'\$\$[\s\S]*?\$\$', repl, text)
    text = re.sub(r'\$[^$\n]+\$', repl, text)
    text = re.sub(r'https?://[^\s\)\]、，]+', repl, text)
    text = re.sub(r'[A-Za-z]:[\\/][^\s,;:、，]+', repl, text)
    text = re.sub(r'(?:\.\.?[/\\])+[^\s,;:、，]+', repl, text)
    return text, protected

def restore_regions(text, protected):
    for key, original in protected.items():
        text = text.replace(key, original)
    return text


def main():
    parser = argparse.ArgumentParser(description='Attachments → attachments')
    parser.add_argument('path', help='vault 根目录路径')
    parser.add_argument('--apply', action='store_true', help='执行修改')
    args = parser.parse_args()

    vault = args.path
    if not os.path.isdir(vault):
        print(f'错误：路径不存在 — {vault}', file=sys.stderr)
        sys.exit(1)

    # 收集所有 Attachments 目录（深度优先）
    dir_renames = []
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for d in dirs:
            if d == 'Attachments':
                old_path = os.path.join(root, d)
                new_path = os.path.join(root, 'attachments')
                dir_renames.append((old_path, new_path))
    dir_renames.sort(key=lambda x: -x[0].count(os.sep))

    print(f'Attachments 目录: {len(dir_renames)} 个')

    if not args.apply:
        print('[dry-run] 使用 --apply 执行')
        return

    # 阶段 1: 重命名目录
    print('重命名目录...')
    for old, new in dir_renames:
        try:
            os.rename(old, new)
            print(f'  ✓ {old} → {new}')
        except OSError as e:
            print(f'  ✗ {old}: {e}', file=sys.stderr)

    # 阶段 2: 更新 .md 内容中的 Attachments/ 路径引用
    print('更新 .md 内容引用...')
    updated = 0
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if not f.endswith('.md'):
                continue
            fp = os.path.join(root, f)
            with open(fp, 'r', encoding='utf-8') as fh:
                original = fh.read()

            protected_text, protected = protect_regions(original)

            # 替换路径中的 Attachments/ → attachments/
            # 匹配模式: /Attachments/ 或 Attachments/  (不匹配 attachments/ 已有小写)
            processed = re.sub(r'(?<![a-z])Attachments/', 'attachments/', protected_text)

            processed = restore_regions(processed, protected)

            if original != processed:
                updated += 1
                # 备份
                with open(fp + '.bak', 'w', encoding='utf-8') as fh:
                    fh.write(original)
                with open(fp, 'w', encoding='utf-8') as fh:
                    fh.write(processed)
                print(f'  ✓ {os.path.relpath(fp, vault)}')

    print(f'\n完成：{len(dir_renames)} 目录重命名，{updated} 文件内容更新')


if __name__ == '__main__':
    main()
