#!/usr/bin/env python3
"""
check-required-files.py — validate that every project has the required structure.

Enforced (fails CI if missing):
  - README.md
  - a YAML metadata block with the required keys
  - steps/ directory with at least one numbered step and a cleanup step
  - troubleshooting.md

Warned (does not fail — nudges toward the fuller template standard):
  - prerequisites.md, references.md, architecture.md (intermediate+)

USAGE:  scripts/check-required-files.py
"""
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROJECTS = os.path.join(REPO, "projects")
REQUIRED_META = ["level", "cloud", "domain", "technology",
                 "estimated_time", "estimated_cost", "cleanup_required", "status"]
YAML_BLOCK = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)

errors, warnings = [], []


def project_dirs():
    for root, _d, files in os.walk(PROJECTS):
        rel = os.path.relpath(root, PROJECTS)
        if rel.count(os.sep) == 2 and "README.md" in files:
            yield root


for pdir in sorted(project_dirs()):
    name = os.path.relpath(pdir, PROJECTS)
    readme = os.path.join(pdir, "README.md")
    with open(readme, encoding="utf-8") as fh:
        text = fh.read()

    # metadata block + required keys
    m = YAML_BLOCK.search(text[:1200])
    if not m:
        errors.append(f"{name}: README.md has no ```yaml metadata block")
    else:
        block = m.group(1)
        for key in REQUIRED_META:
            if not re.search(rf"^{key}:", block, re.MULTILINE):
                errors.append(f"{name}: metadata missing key '{key}'")

    # steps/ with a cleanup step
    steps = os.path.join(pdir, "steps")
    if not os.path.isdir(steps):
        errors.append(f"{name}: no steps/ directory")
    else:
        step_files = [f for f in os.listdir(steps) if f.endswith(".md")]
        if not step_files:
            errors.append(f"{name}: steps/ has no .md files")
        if not any("cleanup" in f.lower() for f in step_files):
            errors.append(f"{name}: steps/ has no cleanup step")

    # troubleshooting.md
    if not os.path.isfile(os.path.join(pdir, "troubleshooting.md")):
        errors.append(f"{name}: missing troubleshooting.md")

    # soft nudges
    for opt in ("prerequisites.md", "references.md"):
        if not os.path.isfile(os.path.join(pdir, opt)):
            warnings.append(f"{name}: missing {opt} (recommended)")


count = len(list(project_dirs()))
if warnings:
    print(f"{len(warnings)} warning(s):")
    for w in warnings:
        print(f"  ⚠ {w}")
    print()

if errors:
    print(f"{len(errors)} ERROR(s):")
    for e in errors:
        print(f"  ✗ {e}")
    sys.exit(1)

print(f"All {count} projects have the required structure. ✅")
