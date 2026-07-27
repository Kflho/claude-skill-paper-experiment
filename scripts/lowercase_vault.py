#!/usr/bin/env python3
"""vault 内容全小写化 — 保护代码/LaTeX/URL/wikilink/markdown link，其余全部 lower()。"""
import sys, os, re, argparse

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except: pass

PH = '__llcc_'  # 全小写，避免被 .lower() 改掉

def protect(text):
    p, c = {}, [0]
    def ph():
        key = f'{PH}{c[0]}__'; c[0] += 1; return key
    def rp(m):
        key = ph(); p[key] = m.group(0); return key
    text = re.sub(r'```[\s\S]*?```', rp, text)
    text = re.sub(r'`[^`\n]+`', rp, text)
    text = re.sub(r'\$\$[\s\S]*?\$\$', rp, text)
    text = re.sub(r'\$[^$\n]+\$', rp, text)
    text = re.sub(r'https?://[^\s\)\]、，]+', rp, text)
    text = re.sub(r'!?\[\[.+?\]\]', rp, text)
    text = re.sub(r'\[.*?\]\(.*?\)', rp, text)
    text = re.sub(r'[A-Za-z]:[\\/][^\s,;:、，\n]+', rp, text)
    return text, p

def restore(text, p):
    for k, v in p.items(): text = text.replace(k, v)
    # 处理嵌套占位符：markdown link 内包 URL 占位符时，外层先恢复会漏掉内层
    while PH in text:
        for k, v in p.items(): text = text.replace(k, v)
    return text

def main():
    p = argparse.ArgumentParser(description='vault 全小写')
    p.add_argument('path'); p.add_argument('--apply', action='store_true')
    a = p.parse_args()
    if not os.path.isdir(a.path): sys.exit(1)

    skip = {'.obsidian', '.git', '.trash', '.claude', 'node_modules'}
    md_files = []
    for r, ds, fs in os.walk(a.path):
        ds[:] = [d for d in ds if d not in skip]
        for f in fs:
            if f.endswith('.md') and not f.endswith('.bak'):
                md_files.append(os.path.join(r, f))

    changed = 0
    for fp in sorted(md_files):
        with open(fp, 'r', encoding='utf-8') as fh: orig = fh.read()
        pt, pd = protect(orig)
        lc = pt.lower()
        lc = restore(lc, pd)
        if orig == lc: continue
        changed += 1
        if a.apply:
            with open(fp + '.bak', 'w', encoding='utf-8') as fh: fh.write(orig)
            with open(fp, 'w', encoding='utf-8') as fh: fh.write(lc)
            print(f'  ✓ {os.path.relpath(fp, a.path)}')
        else:
            print(f'  ~ {os.path.relpath(fp, a.path)}')

    print(f'\n{"完成" if a.apply else "[dry-run]"} {changed} 个文件')
    if not a.apply: print('使用 --apply 执行')

if __name__ == '__main__': main()
