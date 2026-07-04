# Project Folder Template

The standard layout every project should follow. **Not every project needs every folder** — keep
beginner projects lightweight and add structure only when the project genuinely needs it.

```
project-name/
├── README.md            # (mandatory) Overview, metadata, diagrams, step index, cost, cleanup
├── architecture.md      # (mandatory for intermediate+) Deeper diagrams if README gets crowded
├── prerequisites.md     # (mandatory) What must exist before Step 1 — account, tools, permissions
├── costs.md             # (optional) Only if cost is complex enough to need its own file
├── steps/               # (mandatory) Numbered, one concept per file; last file is cleanup
│   ├── 01-introduction.md
│   ├── 02-setup.md
│   ├── 03-build.md
│   ├── 04-test.md
│   ├── 05-monitoring.md
│   └── 06-cleanup.md
├── src/                 # (optional) Application source code
├── infra/               # (optional) IaC — only the subfolders the project actually uses
│   ├── terraform/
│   ├── cloudformation/
│   ├── kubernetes/
│   └── helm/
├── scripts/             # (optional) Helper scripts (seed data, load test, verify)
├── troubleshooting.md   # (mandatory) Error → Cause → Fix
├── challenges.md        # (optional) 5–7 extension tasks
└── references.md        # (mandatory) Official docs links
```

## File-by-file

| File / folder | Mandatory? | Purpose | Content |
|---------------|-----------|---------|---------|
| `README.md` | **Yes** | Front door. First thing a user reads. | Metadata block, what you'll build, architecture diagram, prerequisites summary, step index, cost, cleanup warning, links out. Use `project-readme-template.md`. |
| `architecture.md` | Intermediate+ | Home for diagrams too detailed for the README. | Mermaid diagrams (architecture, request flow, network, IAM, deploy). Beginner projects can keep the single diagram in the README instead. Use `architecture-template.md`. |
| `prerequisites.md` | **Yes** | Everything needed before Step 1. | Account/region, CLI tools + versions, required IAM permissions, prior projects to do first, cost prerequisites (e.g. billing linked). |
| `costs.md` | Optional | Cost detail when the README summary isn't enough. | Per-service breakdown, formulas, free-tier notes, "left running" warnings. Skip if the README cost section covers it. |
| `steps/` | **Yes** | The actual hands-on walkthrough. | One concept per numbered file. Each: narrative → Console walkthrough → CLI alternative → checkpoint. **Last file is always cleanup.** |
| `src/` | Optional | Application code. | Python only (repo convention). No comments unless the *why* is non-obvious. |
| `infra/` | Optional | Infrastructure as code. | Only include the subfolders used (`terraform/`, `kubernetes/`, `helm/`, `cloudformation/`). Don't create empty ones. |
| `scripts/` | Optional | Repeatable helpers. | Seed/verify/load-test/cleanup scripts. No hardcoded account IDs or secrets. |
| `troubleshooting.md` | **Yes** | Unblock stuck users. | `Error → Cause → Fix` format. Use `troubleshooting-template.md`. |
| `challenges.md` | Optional | Go further. | 5–7 extension challenges that build on the finished project. |
| `references.md` | **Yes** | Point to authority. | Official provider docs, relevant blog posts, related repo projects. |

## Rules

- **No `diagrams/` folder by default.** Mermaid lives inside `README.md` / `architecture.md`. Add a
  `diagrams/` folder only if a specific project needs exported/source diagram files.
- **No `assets/` folder.** Not used in this repo.
- **No empty folders.** Create a folder the moment it has a file, not before.
- **Cleanup is always the last step.** Every cloud project must be fully tear-down-able.
- **Cost warning is mandatory** for anything that can incur charges.

## Minimal beginner project

The lightest acceptable shape:

```
aws-lambda-basics/
├── README.md            # includes metadata, one diagram, cost, cleanup
├── prerequisites.md
├── steps/
│   ├── 01-*.md ... 0N-cleanup.md
├── src/
├── troubleshooting.md
└── references.md
```
