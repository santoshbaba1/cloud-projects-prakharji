# Contributing

This repo is a **hands-on project hub**, not a course. Every contribution is a project someone can
build, test, troubleshoot, and tear down. Keep it practical.

## Before you start

- Read [docs/templates/project-template.md](docs/templates/project-template.md) (folder layout) and
  [docs/templates/project-readme-template.md](docs/templates/project-readme-template.md) (README).
- Check [PROJECT-CATALOG.md](PROJECT-CATALOG.md) so you don't duplicate an existing project.

## Adding a new project

1. **Pick the location:** `projects/<level>/<cloud-or-technology>/<project-name>/`
   - `level` = `beginner` | `intermediate` | `advanced` (by operational complexity, not topic).
   - `cloud-or-technology` = the **primary learning goal**. AWS Lambda → `aws/`. A Terraform-only
     project → `terraform/` even if it targets AWS. An EKS/K8s project → `kubernetes/`.
   - Create the provider folder only if your project is the first to need it. **No empty folders.**
2. **Name the folder** per the rules below.
3. **Copy the templates** and fill them in.
4. **Fill in the YAML metadata block** at the top of your README (`level`, `cloud`, `domain`,
   `technology`, `estimated_time`, `estimated_cost`, …), then regenerate the catalog:
   `scripts/generate-project-catalog.py --write`. **Do not hand-edit `PROJECT-CATALOG.md`** — it is
   generated from the metadata blocks.

### Folder naming rules

- lowercase, `kebab-case`
- start with the **provider or main technology**: `aws-`, `gcp-`, `azure-`, `k8s-`, `eks-`,
  `terraform-`, `docker-`, `argocd-`, `prometheus-`, …
- include the **main service or concept**: `aws-api-gateway-dynamodb-crud`
- clear over clever; avoid `project1`, `demo`, `test`, `sample`, `app`
- keep it reasonably short

✅ `aws-lambda-basics`, `gcp-vpc-firewall-basics`, `terraform-aws-vpc-three-tier`,
`github-actions-aws-lambda-deploy`
❌ `lambda1`, `my-cool-project`, `aws-super-advanced-full-stack-serverless-web-application`

## Required files

Mandatory in every project:

- `README.md` with the **metadata block** (see the README template) + at least one Mermaid diagram
- `prerequisites.md`
- `architecture.md` for intermediate+ (beginner may keep the single diagram in the README)
- `steps/` — numbered, one concept per file, **last file is cleanup**
- `troubleshooting.md` (`Error → Cause → Fix`)
- `references.md`

Optional: `src/`, `infra/`, `scripts/`, `challenges.md`, `costs.md` (only if cost is too complex for
the README section).

## Requirements checklist

- **README metadata:** every README starts with the YAML block (`level`, `cloud`, `domain`,
  `technology`, `estimated_time`, `estimated_cost`, `deployment_type`, `cleanup_required`, `status`).
- **Architecture diagrams:** Mermaid only, inside Markdown. Match the per-level diagram set in
  [docs/templates/architecture-template.md](docs/templates/architecture-template.md).
- **Cleanup:** every cloud project ends in a cleanup step and is fully tear-down-able. Use
  [docs/templates/cleanup-template.md](docs/templates/cleanup-template.md).
- **Cost:** a cost table + a ⚠️ "left running" warning for anything billable. Flag real-cost (no
  free tier) projects prominently.
- **Security:** no secrets, credentials, `.env`, or hardcoded account IDs committed. Use
  least-privilege IAM and explain every permission (`Permission | Service | Why`).
- **Testing:** include a validation/testing checklist; verify the project actually works end-to-end
  before submitting.

## Style rules

**Markdown**
- Simple, beginner-friendly language; plain-language explanation before jargon.
- Use tables for comparisons; keep commands copy-paste friendly.
- Explain **why** important commands/permissions exist, not just what.
- Region: `us-east-1` (AWS), `us-east1` / `us-east1-b` (GCP).

**Mermaid**
- Diagrams live **inside** `README.md` / `architecture.md` — no exported images.
- One sentence before each diagram (what it shows), one takeaway after.

**Code**
- Python only (`python3.14` Lambda runtime, `python:3.12-slim` containers, `flask==3.1.0`).
- No comments unless the *why* is non-obvious.

## Do / Don't

| Do | Don't |
|----|-------|
| Keep projects hands-on and self-contained | Turn READMEs into theory chapters |
| Put concepts in `docs/basic-concepts/` and link to them | Duplicate concept theory inside a project |
| Add a folder when it has a file | Create empty folders |
| Use Mermaid in Markdown | Add an `assets/` directory |
| Keep it project-specific | Add a `learning-paths/` directory |

## Automated checks (CI)

The `repo-checks` GitHub Action runs on every PR. Run the same checks locally before pushing:

```bash
python3 scripts/check-markdown-links.py            # every relative link resolves
python3 scripts/check-required-files.py            # each project has the required structure
python3 scripts/generate-project-catalog.py --check # PROJECT-CATALOG.md is in sync with metadata
```

A separate job scans the diff for committed secrets.

## Pull request checklist

- [ ] Folder is `projects/<level>/<tech>/<kebab-name>/` and named per the rules
- [ ] README has the metadata block + at least one Mermaid diagram
- [ ] `prerequisites.md`, `troubleshooting.md`, `references.md` present
- [ ] Steps are numbered; **cleanup is the last step**
- [ ] Cost table + "left running" warning included
- [ ] No secrets / credentials / hardcoded account IDs
- [ ] Least-privilege IAM, permissions explained
- [ ] Validation/testing checklist included and verified
- [ ] README metadata block filled in and `scripts/generate-project-catalog.py --write` re-run
- [ ] No unnecessary folders; no `assets/`; no `learning-paths/`
