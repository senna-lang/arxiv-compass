# Logosyncx Usage for AI Agents

You have access to the `logos` CLI for managing plan and task context.
`logos` is a shell binary — call it via terminal/shell commands.

---

## MANDATORY Triggers

| Condition | You MUST run |
|---|---|
| Starting any work session | `logos ls --json` (check past plans before doing anything) |
| User says "save this plan", "log this", "記録して" | `logos save --topic "..."` then write body with Write tool |
| User says "make that a task", "add a TODO", "タスクにして" | `logos task create --plan <name> --title "..."` then write body with Write tool |
| User says "continue from last time", "前回の続き" | `logos ls --json` then `logos refer --name <name> --summary` |
| User mentions a past plan or decision | `logos ls --json` and check excerpts for relevance |

> **Never say "I can't save plans" or "I don't have access to logos."**
> The `logos` binary is installed and available via shell. Always use it.

### Agent contract for writing document bodies

Before writing any document body (plan, task, knowledge), you MUST:

1. Read the corresponding template from `.logosyncx/templates/`.
2. Use the template's section structure as the basis for the document.
3. Write the body **directly into the file** using the Write tool — not via a CLI flag.

The CLI produces a frontmatter scaffold only. You fill the body.

---

## Workflow for finding relevant context

1. Run `logos ls --json` to get all plans with excerpts
2. Read `topic`, `tags`, and `excerpt` fields to judge relevance yourself
3. Run `logos refer --name <filename> --summary` on relevant plans to get details
4. If you want to narrow down by keyword first, use `logos search --keyword <keyword>`

## Workflow for saving a plan

```
# 1. Scaffold the plan file
logos save --topic "short description" --tag go --tag cli --agent claude-code

# 2. Read the plan template
cat .logosyncx/templates/plan.md

# 3. Write the plan body directly into the file
# (use the Write tool to fill in sections)
```

## Commands

### List plans
```
logos ls                       # human-readable table
logos ls --tag auth            # filter by tag
logos ls --since 2026-01-01    # filter by date
logos ls --blocked             # show only blocked plans
logos ls --json                # structured output with excerpts (preferred for agents)
```

### Read a plan
```
logos refer --name <filename>            # full content
logos refer --name <partial-name>        # partial match
logos refer --name <filename> --summary  # key sections only (saves tokens, prefer this)
```

### Save a plan
```
logos save --topic "short description"
logos save --topic "..." --tag go --tag cli --agent claude-code --depends-on 20260304-auth.md
```

### Search (keyword narrowing)
```
logos search --keyword "keyword"
logos search --keyword "auth" --tag security
```

### Sync index
```
logos sync
```

Rebuilds the plan and task indexes from the filesystem.

### Garbage collect stale plans
```
logos gc --dry-run
logos gc
logos gc purge --force
```

---

## Tasks

Tasks are work items linked to a plan. Each task has a `TASK.md` (what to do)
and optionally a `WALKTHROUGH.md` (what actually happened — filled after completion).

### Workflow for creating a task

```
# 1. Scaffold the task
logos task create --plan <plan-filename> --title "Implement the thing" --priority high --tag go

# 2. Read the task template
cat .logosyncx/templates/task.md

# 3. Write TASK.md body directly using the Write tool
```

### Workflow for completing a task

> **CRITICAL ORDER**: Write WALKTHROUGH.md content FIRST, then mark done.
> `logos task update --status done` will FAIL if WALKTHROUGH.md has no real content.

```
# 1. Read the walkthrough template
cat .logosyncx/templates/walkthrough.md

# 2. Find the task's directory path
logos task refer --name <task-name> | head -5

# 3. Write WALKTHROUGH.md content using the Write tool
#    Path: .logosyncx/tasks/<plan-slug>/<NNN-task-name>/WALKTHROUGH.md

# 4. Only after writing content — mark done
logos task update --plan <plan-filename> --name <task-name> --status done
```

A line counts as "real content" if it is non-empty and does not start with `<!--`.
Scaffold-only files (all HTML comment blocks) will be rejected.

### Task commands

```
# List tasks
logos task ls                                     # all tasks
logos task ls --plan <plan-filename>              # tasks for a specific plan
logos task ls --status open                       # filter by status
logos task ls --blocked                           # show only blocked tasks
logos task ls --json                              # structured output (preferred for agents)

# Read a task
logos task refer --name <name>                    # full TASK.md content
logos task refer --name <name> --summary          # key sections only (saves tokens)

# Create a task
logos task create --plan <plan-filename> --title "..."
logos task create --plan <plan-filename> --title "..." --priority high --tag go --depends-on 1

# Update a task
logos task update --plan <plan-filename> --name <name> --status in_progress
logos task update --plan <plan-filename> --name <name> --status done
logos task update --plan <plan-filename> --name <name> --priority high

# Open walkthrough scaffold
logos task walkthrough --plan <plan-filename> --name <name>
```

---

## Distill

After all tasks in a plan are done, distil the work into reusable knowledge:

```
# Preview — no writes
logos distill --plan <plan-filename> --dry-run

# Write knowledge scaffold
logos distill --plan <plan-filename>

# Read the knowledge template, then fill in the knowledge file using the Write tool
cat .logosyncx/templates/knowledge.md
```

---

## Token strategy
- Use `logos ls --json` first to scan all plans cheaply via excerpts
- Use `--summary` on `refer` unless you need the full plan body
- Only use full `refer` when the summary is insufficient
