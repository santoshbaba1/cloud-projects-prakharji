#!/usr/bin/env python3
"""
check-markdown-links.py — verify every relative markdown link resolves to a real file.

Skips external (http, mailto), absolute (/), pure-anchor (#...) and template-placeholder
(< >, { }) links, and links inside fenced ``` code blocks. Exits non-zero if any link is broken.

USAGE:  scripts/check-markdown-links.py
"""
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SKIP_DIRS = {".git"}
# templates intentionally contain placeholder links (steps/01-introduction.md, etc.)
SKIP_PATHS = {os.path.join(REPO, "docs", "templates")}

broken = []
checked = 0

for root, dirs, files in os.walk(REPO):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    if any(root == p or root.startswith(p + os.sep) for p in SKIP_PATHS):
        continue
    for fn in files:
        if not fn.endswith(".md"):
            continue
        path = os.path.join(root, fn)
        with open(path, encoding="utf-8") as fh:
            in_fence = False
            for line in fh:
                if line.lstrip().startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                for link in LINK_RE.findall(line):
                    l = link.strip()
                    if (not l or l.startswith("#") or l.startswith("/")
                            or "://" in l or l.startswith("mailto:")
                            or "<" in l or "{" in l):
                        continue
                    target = l.split("#", 1)[0].split("?", 1)[0]
                    if not target:
                        continue
                    checked += 1
                    resolved = os.path.normpath(os.path.join(os.path.dirname(path), target))
                    if not os.path.exists(resolved):
                        broken.append((os.path.relpath(path, REPO), link))

print("Checked %d relative link(s)." % checked)
if broken:
    print("\n%d BROKEN link(s):" % len(broken))
    for src, link in broken:
        print("  %s  ->  %s" % (src, link))
    sys.exit(1)
print("All links resolve. ✅")
