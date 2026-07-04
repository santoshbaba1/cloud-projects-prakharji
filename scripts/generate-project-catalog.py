#!/usr/bin/env python3
"""
generate-project-catalog.py — build PROJECT-CATALOG.md from project README metadata.

Walks projects/**/README.md, parses the ```yaml metadata block at the top of each, and
regenerates the catalog table + grouped sections. Run after adding/editing a project.

USAGE:
  scripts/generate-project-catalog.py            # print to stdout (dry run)
  scripts/generate-project-catalog.py --write     # overwrite PROJECT-CATALOG.md
  scripts/generate-project-catalog.py --check      # exit 1 if PROJECT-CATALOG.md is stale (CI)
"""
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WRITE = "--write" in sys.argv[1:]
CHECK = "--check" in sys.argv[1:]
CATALOG = os.path.join(REPO, "PROJECT-CATALOG.md")

COST_ICON = {"free-tier": "🟢", "low": "🟡", "hourly": "🔴"}
CLOUD_LABEL = {"aws": "AWS", "gcp": "GCP", "azure": "Azure", "kubernetes": "Kubernetes",
               "docker": "Docker"}
LEVEL_ORDER = {"beginner": 0, "intermediate": 1, "advanced": 2}
# recommended display order (path suffix -> order); anything unlisted sorts after, by level
ORDER = [
    "aws-lambda-basics", "aws-lambda-s3-event-processing", "aws-lambda-layers",
    "aws-lambda-eventbridge-scheduled", "aws-lambda-ec2-start-stop-scheduler",
    "aws-lambda-s3-housekeeping", "aws-s3-cloudfront-static-website", "aws-sqs-sns-messaging",
    "aws-lambda-sqs-sns-trigger", "aws-lambda-troubleshooting-monitoring",
    "aws-iam-roles-and-policies", "aws-api-gateway-rest-lambda", "aws-api-gateway-dynamodb-crud",
    "aws-serverless-monitored-webapp", "aws-compute-rightsizing", "aws-ecs-fargate-basics",
    "aws-ecs-fargate-advanced", "aws-ec2-vpc-monitored-webapp", "aws-rds-disaster-recovery",
    "aws-monolith-to-serverless-migration", "aws-database-migration-dms",
    "eks-monolith-to-microservices", "eks-irsa-service-account-access",
    "k8s-optimization-and-recovery", "gcp-vpc-firewall-basics", "gcp-http-lb-autoscaling",
    "docker-network-flask-basics", "docker-networks-storage-notes",
]

YAML_BLOCK = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)


def parse_meta(text):
    m = YAML_BLOCK.search(text[:1200])
    if not m:
        return None
    meta, tech, in_tech = {}, [], False
    for line in m.group(1).splitlines():
        if line.startswith("  - "):
            if in_tech:
                tech.append(line[4:].strip())
            continue
        in_tech = False
        if ":" in line:
            k, v = line.split(":", 1)
            k, v = k.strip(), v.strip()
            if k == "technology":
                in_tech = True
            else:
                meta[k] = v
    meta["technology"] = tech
    return meta


def title_of(readme_text):
    for line in readme_text.splitlines():
        if line.startswith("# "):
            # compact catalog title: drop a trailing " — subtitle" and a trailing "(detail)"
            t = line[2:].split(" — ")[0]
            t = re.sub(r"\s*\([^)]*\)\s*$", "", t)
            return t.strip()
    return "Untitled"


def collect():
    rows = []
    base = os.path.join(REPO, "projects")
    for root, _d, files in os.walk(base):
        if "README.md" not in files:
            continue
        rel = os.path.relpath(root, base)
        if rel.count(os.sep) != 2:  # level/tech/project only
            continue
        with open(os.path.join(root, "README.md"), encoding="utf-8") as fh:
            text = fh.read()
        meta = parse_meta(text)
        if not meta:
            continue
        name = os.path.basename(root)
        rows.append({
            "name": name,
            "path": os.path.relpath(os.path.join(root, "README.md"), REPO),
            "title": title_of(text),
            "level": meta.get("level", "?"),
            "cloud": meta.get("cloud", "?"),
            "domain": meta.get("domain", "?"),
            "time": meta.get("estimated_time", "?"),
            "cost": meta.get("estimated_cost", "?"),
        })
    rows.sort(key=lambda r: (ORDER.index(r["name"]) if r["name"] in ORDER
                             else 999 + LEVEL_ORDER.get(r["level"], 9)))
    for i, r in enumerate(rows, 1):
        r["order"] = i
    return rows


def cloud_disp(r):
    label = CLOUD_LABEL.get(r["cloud"], r["cloud"].title())
    if r["cloud"] == "kubernetes":
        label += " (EKS)" if r["name"].startswith("eks-") else " (local)"
    return label


def render(rows):
    out = []
    out.append("# Project Catalog\n")
    out.append("> **Auto-generated** by `scripts/generate-project-catalog.py` from each project's "
               "README metadata block. Do not edit by hand — update the project README and "
               "re-run the script.\n")
    out.append("The main navigation page for this repo. Pick a project by **level, cloud/tech, "
               "domain, time, or cost** — then jump straight in. The `Order` column is a "
               "**suggestion**, not a required path.\n")
    out.append("> Projects live under `projects/<level>/<cloud-or-tech>/`.\n")
    out.append("**Legend** — Cost: 🟢 free-tier · 🟡 small lab cost · 🔴 real hourly cost "
               "(no free tier). Status: ✅ ready.\n")
    out.append("## All projects\n")
    out.append("| Order | Level | Cloud/Tech | Domain | Project | Time | Cost | Status |")
    out.append("|------:|-------|-----------|--------|---------|------|------|--------|")
    for r in rows:
        icon = COST_ICON.get(r["cost"], r["cost"])
        out.append(f"| {r['order']} | {r['level'].title()} | {cloud_disp(r)} | "
                   f"{r['domain']} | [{r['title']}]({r['path']}) | {r['time']} | {icon} | ✅ |")
    out.append("")
    hourly = [str(r["order"]) for r in rows if r["cost"] == "hourly"]
    out.append(f"> 🔴 **Real-cost projects** ({', '.join(hourly)}): bill per hour with no free-tier "
               "umbrella. Do the cleanup step **the same day**.\n")

    # By level
    out.append("## By level\n")
    for lvl in ("beginner", "intermediate", "advanced"):
        sel = [r for r in rows if r["level"] == lvl]
        if sel:
            out.append(f"### {lvl.title()}")
            out.append(" · ".join(f"{r['order']} {r['title']}" for r in sel) + "\n")

    # By cloud / tech
    out.append("## By cloud / technology\n")
    for cl in ("aws", "gcp", "azure", "kubernetes", "docker"):
        sel = [r for r in rows if r["cloud"] == cl]
        label = CLOUD_LABEL.get(cl, cl.title())
        out.append(f"### {label} Projects")
        if sel:
            out.append(" · ".join(f"{r['order']} {r['title']}" for r in sel) + "\n")
        else:
            out.append("*None yet.*\n")
    return "\n".join(out) + "\n"


def main():
    rows = collect()
    text = render(rows)
    if CHECK:
        current = ""
        if os.path.exists(CATALOG):
            with open(CATALOG, encoding="utf-8") as fh:
                current = fh.read()
        if current != text:
            sys.stderr.write(
                "PROJECT-CATALOG.md is out of date. Run:\n"
                "    scripts/generate-project-catalog.py --write\n"
                "and commit the result.\n")
            sys.exit(1)
        print(f"PROJECT-CATALOG.md is up to date ({len(rows)} projects).")
    elif WRITE:
        with open(CATALOG, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"Wrote PROJECT-CATALOG.md ({len(rows)} projects).")
    else:
        sys.stdout.write(text)
        sys.stderr.write(f"\n[dry run] {len(rows)} projects. Use --write to save.\n")


if __name__ == "__main__":
    main()
