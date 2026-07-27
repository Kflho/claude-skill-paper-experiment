#!/usr/bin/env python3
r"""
Obsidian vault 大小写规范化脚本。

只做一件事：将文件夹和 .md 文件名全小写化，同步更新文档内的 wikilink 和 markdown 链接引用。
不修改空格、标点、特殊字符——只改大小写。

保护区域：LaTeX 数学、代码块、行内代码、URL。

用法：
  python normalize_vault.py <vault_path>              dry-run 预览
  python normalize_vault.py <vault_path> --apply      执行修改（自动 .bak 备份）
  python normalize_vault.py <vault_path> --content-only  仅修复内容引用（重命名已完成时）
"""

import sys, os, re, argparse
from pathlib import Path

# Windows 控制台 UTF-8 编码修复
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# ============================================================
# 保护区域（参考 fmt.py）
# ============================================================
PH_PREFIX = '__NV_P_'


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

    # 保护顺序：代码块 → 行内代码 → LaTeX → URL → 文件路径 → 标识符
    text = re.sub(r'```[\s\S]*?```', repl, text)
    text = re.sub(r'`[^`\n]+`', repl, text)
    text = re.sub(r'\$\$[\s\S]*?\$\$', repl, text)
    text = re.sub(r'\$[^$\n]+\$', repl, text)
    text = re.sub(r'https?://[^\s\)\]、，]+', repl, text)
    # Windows 绝对路径
    text = re.sub(r'[A-Za-z]:[\\/][^\s,;:、，]+', repl, text)
    # 相对路径 ../.../
    text = re.sub(r'(?:\.\.?[/\\])+[^\s,;:、，]+', repl, text)

    return text, protected


def restore_regions(text, protected):
    """还原所有占位符"""
    for key, original in protected.items():
        text = text.replace(key, original)
    return text


# ============================================================
# 扫描
# ============================================================

SKIP_DIRS = {'.obsidian', '.git', '.trash', '.claude', 'node_modules'}
SKIP_DIR_NAMES = {'Attachments'}  # 不重命名但可进入


def scan_vault(vault_path):
    """扫描 vault，返回需要重命名的目录和 .md 文件列表（深度优先）。"""
    vault = Path(vault_path)

    dir_renames = []   # [(old_path, new_path), ...]
    file_renames = []  # [(old_path, new_path), ...]

    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        root_path = Path(root)

        for d in dirs[:]:
            if d in SKIP_DIR_NAMES:
                continue
            new_name = d.lower()
            if d != new_name:
                old_path = root_path / d
                new_path = root_path / new_name
                dir_renames.append((str(old_path), str(new_path)))

        for f in files:
            if not f.endswith('.md'):
                continue
            old_path = root_path / f
            stem = old_path.stem
            new_stem = stem.lower()
            if stem != new_stem:
                new_path = root_path / (new_stem + '.md')
                file_renames.append((str(old_path), str(new_path)))

    # 深度优先：最深的先改
    dir_renames.sort(key=lambda x: -x[0].count(os.sep))

    return dir_renames, file_renames


def build_name_map(dir_renames, file_renames):
    """构建 basename → 新 basename 映射。
    同时注册 .md 文件的无后缀版本，以匹配 [[wikilink]] 格式。"""
    name_map = {}
    for old_path, new_path in dir_renames + file_renames:
        old_name = os.path.basename(old_path)
        new_name = os.path.basename(new_path)
        name_map[old_name] = new_name
        # .md 文件同时注册无后缀 key
        if old_name.endswith('.md'):
            old_stem = old_name[:-3]
            new_stem = new_name[:-3]
            name_map[old_stem] = new_stem
    return name_map


def detect_conflicts(dir_renames, file_renames):
    """检测重命名后是否会产生同名冲突（Windows 大小写不敏感）。"""
    new_paths = {}
    conflicts = []

    for old_path, new_path in dir_renames + file_renames:
        key = new_path.lower()
        if key in new_paths:
            conflicts.append((new_paths[key], new_path))
        else:
            new_paths[key] = new_path

    all_existing = set()
    for old_path, _ in dir_renames + file_renames:
        parent = os.path.dirname(old_path)
        try:
            for name in os.listdir(parent):
                all_existing.add(os.path.join(parent, name).lower())
        except OSError:
            pass

    for old_path, new_path in dir_renames + file_renames:
        if new_path.lower() in all_existing:
            if old_path.lower() != new_path.lower():
                conflicts.append(('已存在', new_path))

    return conflicts


# ============================================================
# 内容更新 — 文件/目录已重命名后使用
# ============================================================

def collect_known_names(vault_path):
    """收集 vault 中已重命名的 .md 文件名和目录名（仅这些被 lowercase 过）。
    排除 Attachments 等未被重命名的目录，排除图片等非 .md 文件。"""
    names = set()
    for root, dirs, files in os.walk(vault_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for d in dirs:
            if d not in SKIP_DIR_NAMES:
                names.add(d.lower())
        for f in files:
            if f.endswith('.md'):
                names.add(f.lower())           # "foo.md"
                names.add(f[:-3].lower())      # "foo" (wikilink 无后缀形式)
            # 非 .md 文件（图片等）未被重命名，不收入 —— 避免误 downcase 其引用
    return names


def update_content_lowercase(filepath, known_names, apply=False):
    """更新单个 .md 文件：lowercase wikilink target + markdown link path。"""
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()

    protected_text, protected = protect_regions(original)

    # --- wikilink: [[Target]] / [[Target|Alias]] / ![[Target]] ---
    def repl_wikilink(m):
        prefix = m.group(1) or ''       # ! or empty
        target = m.group(2)             # Page Name or Page Name.md or Page Name#heading
        alias = m.group(3) or ''        # |alias (includes the |)

        # 分离 #heading 部分
        if '#' in target:
            page, anchor = target.split('#', 1)
        else:
            page, anchor = target, None

        # 判断是否需要 lowercase：当前名（大小写不敏感）是否在 known_names 中
        page_lower = page.lower()
        if page_lower in known_names or (page_lower + '.md') in known_names:
            new_page = page_lower
            if anchor is not None:
                new_target = new_page + '#' + anchor
            else:
                new_target = new_page
            if new_target != target:
                return f'{prefix}[[{new_target}{alias}]]'

        return m.group(0)

    processed = re.sub(r'(!?)\[\[([^\]|#]+(?:#[^\]|]+)?)(\|[^\]]+)?\]\]', repl_wikilink, protected_text)

    # --- markdown 链接: [text](path/component/File.md) ---
    def repl_mdlink(m):
        prefix = m.group(1)   # [text](
        path = m.group(2)     # folder/file.md or folder/file.md#anchor
        suffix = m.group(3)   # )

        # 分离 anchor
        if '#' in path:
            path_part, anchor = path.rsplit('#', 1)
        else:
            path_part, anchor = path, None

        parts = path_part.split('/')
        changed = False
        for i, part in enumerate(parts):
            if not part:
                continue
            part_lower = part.lower()
            # 仅当小写版存在于 known_names 时才改（排除 Attachments 等未改名的目录）
            if part != part_lower and part_lower in known_names:
                parts[i] = part_lower
                changed = True

        if changed:
            new_path = '/'.join(parts)
            if anchor is not None:
                new_path += '#' + anchor
            return prefix + new_path + suffix
        return m.group(0)

    processed = re.sub(r'(\[.*?\]\()([^)]+)(\))', repl_mdlink, processed)

    # 还原保护区域
    processed = restore_regions(processed, protected)

    if original == processed:
        return False

    if apply:
        backup = filepath + '.bak'
        with open(backup, 'w', encoding='utf-8') as f:
            f.write(original)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(processed)

    return True


# ============================================================
# 查找所有 .md 文件
# ============================================================

def find_md_files(vault_path):
    """查找 vault 下所有 .md 文件（排除受保护目录）。"""
    md_files = []
    for root, dirs, files in os.walk(vault_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith('.md'):
                md_files.append(os.path.join(root, f))
    return md_files


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='Obsidian vault 大小写规范化 — 只改大小写，不动格式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''示例：
  python normalize_vault.py vault/                dry-run 预览
  python normalize_vault.py vault/ --apply        执行修改（自动 .bak 备份）
  python normalize_vault.py vault/ --content-only 仅修复内容引用（重命名已完成时）''')
    parser.add_argument('path', help='vault 根目录路径')
    parser.add_argument('--apply', action='store_true', help='执行修改（默认 dry-run）')
    parser.add_argument('--content-only', action='store_true',
                        help='仅更新内容引用，不重命名文件（用于重命名已完成后的修复）')
    args = parser.parse_args()

    vault = args.path
    if not os.path.isdir(vault):
        print(f'错误：路径不存在或不是目录 — {vault}', file=sys.stderr)
        sys.exit(1)

    if args.content_only:
        # ---- 仅修复内容 ----
        print(f'扫描 vault 内容引用: {vault}')
        known_names = collect_known_names(vault)
        md_files = find_md_files(vault)
        print(f'已收集 {len(known_names)} 个已知文件名/目录名')

        updated = 0
        for fp in sorted(md_files):
            if update_content_lowercase(fp, known_names, apply=args.apply):
                updated += 1
                if args.apply:
                    print(f'  ✓ {os.path.relpath(fp, vault)}')
                else:
                    print(f'  ~ {os.path.relpath(fp, vault)}')

        if not args.apply:
            print(f'\n[dry-run] {updated} 个文件内容需要更新，使用 --apply --content-only 执行')
        else:
            print(f'\n完成：{updated} 个文件内容已更新')
        return

    # ---- 完整流程：扫描 + 重命名 + 内容更新 ----
    print(f'扫描 vault: {vault}')
    dir_renames, file_renames = scan_vault(vault)

    if not dir_renames and not file_renames:
        print('所有文件和目录已是全小写，无需修改。')
        return

    conflicts = detect_conflicts(dir_renames, file_renames)
    if conflicts:
        print('\n⚠️  冲突检测：以下路径改名后会产生冲突，请手动处理：')
        for a, b in conflicts:
            print(f'  {a}  ⇄  {b}')
        if args.apply:
            print('\n终止：请先解决上述冲突再执行 --apply。')
            sys.exit(1)

    name_map = build_name_map(dir_renames, file_renames)

    print(f'\n目录重命名 ({len(dir_renames)}):')
    for old, new in dir_renames:
        print(f'  {os.path.basename(old)}  →  {os.path.basename(new)}')

    print(f'\n文件重命名 ({len(file_renames)}):')
    for old, new in file_renames:
        print(f'  {os.path.basename(old)}  →  {os.path.basename(new)}')

    if not args.apply:
        print(f'\n[dry-run] 使用 --apply 执行实际修改')
        print(f'共 {len(dir_renames)} 个目录、{len(file_renames)} 个文件将重命名')
        return

    # ============================================================
    # 执行修改
    # ============================================================

    print(f'\n=== 阶段 1/3：重命名目录 ===')
    for old, new in dir_renames:
        try:
            os.rename(old, new)
            print(f'  ✓ {os.path.basename(old)}  →  {os.path.basename(new)}')
        except OSError as e:
            print(f'  ✗ {old}: {e}', file=sys.stderr)

    print(f'\n=== 阶段 2/3：重命名文件 ===')
    for old, new in file_renames:
        try:
            os.rename(old, new)
            print(f'  ✓ {os.path.basename(old)}  →  {os.path.basename(new)}')
        except OSError as e:
            print(f'  ✗ {old}: {e}', file=sys.stderr)

    print(f'\n=== 阶段 3/3：更新文档内容引用 ===')
    known_names = collect_known_names(vault)
    md_files = find_md_files(vault)
    updated = 0
    for fp in sorted(md_files):
        if update_content_lowercase(fp, known_names, apply=True):
            updated += 1
            print(f'  ✓ {os.path.relpath(fp, vault)}')

    print(f'\n完成：{len(dir_renames)} 目录 + {len(file_renames)} 文件重命名，{updated} 文件内容更新')
    print('备份文件 (*.bak) 已生成，确认无误后可删除。')


if __name__ == '__main__':
    main()
