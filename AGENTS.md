
## Logosyncx

Use `logos` CLI for plan and task management.
Full reference: `.logosyncx/USAGE.md`

**MANDATORY triggers:**

- **Start of every session** → `logos ls --json` (check past plans before doing anything)
- User says "save this plan" / "記録して" → `logos save --topic "..."` then write body with Write tool
- User says "make that a task" / "タスクにして" → `logos task create --plan <name> --title "..."`
- User says "continue from last time" / "前回の続き" → `logos ls --json` then `logos refer --name <name> --summary`

Always read the template before writing any document body. Write bodies directly into the file using the Write tool.
