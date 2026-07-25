# Project Initialization — Scientific Research

Before any phase routing, verify that file paths for the current project are known. If not, run this initialization flow.

## Trigger — when to run

Any of these means initialization is needed. Run it **before** proceeding to phase routing:

- User mentions a project name (e.g., "Project 01") for the first time in a scientific-research context
- User asks about 论文/文献/实验 but file paths have never been provided
- The project's CLAUDE.md does not exist or lacks a `## Scientific Research Paths` section

## Step 1 — Identify project and vault

Ask the user two things (can combine into one message):

1. **Obsidian vault path** — absolute path to the vault root (e.g., `D:/Obsidian/MainVault`)
2. **Project name** — the short prefix used to name the three files (e.g., `Project 01`)

If the user has already mentioned the project name, reuse it and only ask for the vault path.

## Step 2 — Derive and confirm file paths

From vault + project name, derive expected paths:

| Role | Expected path |
|---|---|
| Note | `{vault}/Project {XX} Note.md` |
| 参考文献 | `{vault}/Project {XX} 参考文献.md` |
| Schedule | `{vault}/Project {XX} Schedule.md` |

Present these three derived paths to the user and ask: "这些路径对吗？" Allow correction of each path individually (user may use different naming or nested folders).

## Step 3 — Handle missing files

For each file:

| File status | Action |
|---|---|
| **Exists on disk** | Record path as-is |
| **Missing, user wants template** | Create the file with a minimal skeleton (H1 heading only, matching the file's role) and record path |
| **Missing, user will create later** | Record path with `(pending)` annotation |

Template skeletons:

```
# 目标
```

```
# 论文解读
```

```
# MM.DD
```

## Step 4 — Write CLAUDE.md

Write (or update) the project's CLAUDE.md at `{vault}/CLAUDE.md`. Insert or replace a `## Scientific Research Paths` section:

```markdown
## Scientific Research Paths

| Role | Path |
|---|---|
| Note | `D:/Obsidian/MainVault/Project 01 Note.md` |
| 参考文献 | `D:/Obsidian/MainVault/Project 01 参考文献.md` |
| Schedule | `D:/Obsidian/MainVault/Project 01 Schedule.md` |
```

If `{vault}/CLAUDE.md` does not exist, create it with this section as the initial content.

If the project has its own nested CLAUDE.md (e.g., `{vault}/Project_XX/CLAUDE.md`), prefer writing there instead.

## Step 5 — Confirm and proceed

Report a summary of what was recorded:

```
**→ Scientific Research / 初始化完成**

已记录以下文件路径到 `{claude_md_path}`：

| Role | Path | Status |
|---|---|---|
| Note | `...` | ready |
| 参考文献 | `...` | ready |
| Schedule | `...` | pending (用户稍后创建) |
```

Then proceed to the original request (phase routing).

## Already initialized

If the project's CLAUDE.md already has a `## Scientific Research Paths` section with valid paths, **skip initialization entirely**. Read the paths from CLAUDE.md and proceed directly to phase routing.
