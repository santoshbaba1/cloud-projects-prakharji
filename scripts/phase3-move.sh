#!/usr/bin/env bash
#
# phase3-move.sh — Repo reorg Phases 2 + 3 (see docs/repo-migration-plan.md)
#
# Moves the current 26 projects into projects/<level>/<tech>/<name>/ using `git mv`
# (history-preserving), folds the rename into the same move, and tidies the loose ends
# (group READMEs, concepts/, send_message.py).
#
# This does NOT rewrite the ~200 cross-project markdown links — that is Phase 4 and must
# run in the SAME PR as this move. See "Phase 4" in docs/repo-migration-plan.md.
#
# USAGE:
#   scripts/phase3-move.sh            # DRY RUN — prints every action, changes nothing
#   scripts/phase3-move.sh --apply    # actually performs the moves
#
set -euo pipefail

APPLY=false
[[ "${1:-}" == "--apply" ]] && APPLY=true

# Resolve repo root from this script's location, then cd there.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# ── Guard rails ───────────────────────────────────────────────────────────────
if [[ ! -d .git ]]; then
  echo "ERROR: not a git repo root ($REPO_ROOT)"; exit 1
fi
if $APPLY && [[ -n "$(git status --porcelain)" ]]; then
  echo "ERROR: working tree is dirty. Commit or stash first — moves must be a clean, revertible PR."
  exit 1
fi

if $APPLY; then
  echo "== APPLY MODE: performing git mv =="
else
  echo "== DRY RUN: no changes will be made. Re-run with --apply to execute. =="
fi
echo

run()  { echo "+ $*"; $APPLY && eval "$*" || true; }

# Move helper: skip cleanly if the source is already gone (idempotent re-runs).
mv_project() {
  local src="$1" dst="$2"
  if [[ ! -e "$src" ]]; then echo "  skip (already moved): $src"; return; fi
  run "mkdir -p \"\$(dirname \"$dst\")\""
  run "git mv \"$src\" \"$dst\""
}

# ── Phase 2: create the leaf directories the 26 current projects need ─────────
echo "── Phase 2: create projects/ tree ──"
run "mkdir -p projects/beginner/aws projects/beginner/gcp"
run "mkdir -p projects/intermediate/aws projects/intermediate/gcp projects/intermediate/kubernetes"
run "mkdir -p projects/advanced/aws projects/advanced/kubernetes"
echo

# ── Phase 3: git mv each project (relocate + rename in one step) ──────────────
echo "── Phase 3: move + rename projects ──"

# beginner/aws (8)
mv_project lambda-basics                     projects/beginner/aws/aws-lambda-basics
mv_project lambda-s3-event-processing        projects/beginner/aws/aws-lambda-s3-event-processing
mv_project lambda-layers                     projects/beginner/aws/aws-lambda-layers
mv_project lambda-eventbridge-scheduled      projects/beginner/aws/aws-lambda-eventbridge-scheduled
mv_project lambda-ec2-start-stop-scheduler   projects/beginner/aws/aws-lambda-ec2-start-stop-scheduler
mv_project lambda-s3-housekeeping            projects/beginner/aws/aws-lambda-s3-housekeeping
mv_project s3-cloudfront-static-website      projects/beginner/aws/aws-s3-cloudfront-static-website
mv_project sqs-sns-iam-messaging             projects/beginner/aws/aws-sqs-sns-messaging

# intermediate/aws (8)
mv_project lambda-sqs-sns-trigger            projects/intermediate/aws/aws-lambda-sqs-sns-trigger
mv_project lambda-troubleshooting-monitoring projects/intermediate/aws/aws-lambda-troubleshooting-monitoring
mv_project iam-roles-and-policies            projects/intermediate/aws/aws-iam-roles-and-policies
mv_project api-gateway-rest-lambda           projects/intermediate/aws/aws-api-gateway-rest-lambda
mv_project api-gateway-http-dynamodb-crud    projects/intermediate/aws/aws-api-gateway-dynamodb-crud
mv_project serverless-monitored-webapp       projects/intermediate/aws/aws-serverless-monitored-webapp
mv_project aws-compute-rightsizing           projects/intermediate/aws/aws-compute-rightsizing
mv_project ecs-fargate-basics                projects/intermediate/aws/aws-ecs-fargate-basics

# advanced/aws (5)
mv_project ecs-fargate-advanced              projects/advanced/aws/aws-ecs-fargate-advanced
mv_project ec2-vpc-monitored-webapp          projects/advanced/aws/aws-ec2-vpc-monitored-webapp
mv_project rds-disaster-recovery             projects/advanced/aws/aws-rds-disaster-recovery
mv_project monolith-to-serverless-migration  projects/advanced/aws/aws-monolith-to-serverless-migration
mv_project database-migration-dms            projects/advanced/aws/aws-database-migration-dms

# kubernetes (3) — grouped by primary skill, not by AWS
mv_project k8s-optimization-and-recovery              projects/intermediate/kubernetes/k8s-optimization-and-recovery
mv_project monolith-to-microservices-eks              projects/advanced/kubernetes/eks-monolith-to-microservices
mv_project eks-projects/irsa-service-account-access   projects/advanced/kubernetes/eks-irsa-service-account-access

# gcp (2)
mv_project gcp-projects/gcp-vpc-firewall-basics       projects/beginner/gcp/gcp-vpc-firewall-basics
mv_project gcp-projects/gcp-http-lb-autoscaling       projects/intermediate/gcp/gcp-http-lb-autoscaling
echo

# ── Loose ends (same PR) ──────────────────────────────────────────────────────
echo "── Loose ends ──"
# Group index READMEs fold into PROJECT-CATALOG.md
[[ -e eks-projects/README.md ]] && run "git rm eks-projects/README.md"
[[ -e gcp-projects/README.md ]] && run "git rm gcp-projects/README.md"
# Remove the now-empty group dirs (ignore if not empty / not present)
run "rmdir eks-projects 2>/dev/null || true"
run "rmdir gcp-projects 2>/dev/null || true"
# AWS-architecture theory → docs/ (trim + split into basic-concepts later, Phase 6/7)
[[ -e concepts ]] && mv_project concepts docs/basic-concepts-draft
# Stray root script → its project. NOTE: scrub the hardcoded account ID after moving.
if [[ -e send_message.py ]]; then
  run "mkdir -p projects/beginner/aws/aws-sqs-sns-messaging/scripts"
  run "git mv send_message.py projects/beginner/aws/aws-sqs-sns-messaging/scripts/send_message.py"
  echo "  ⚠ TODO: scrub hardcoded AWS account ID / queue URL in the moved send_message.py"
fi
echo

# ── Verification ──────────────────────────────────────────────────────────────
echo "── Next steps ──"
cat <<'EOF'
Verify (after --apply):
  git status                                   # moves show as R (rename); history preserved
  find projects -mindepth 3 -maxdepth 3 -type d | wc -l   # expect 26
  git log --follow projects/beginner/aws/aws-lambda-basics/README.md | head

Then (Phase 4, SAME PR):
  - Rewrite ~200 cross-project + root/catalog links (mapping-driven; see migration plan).
  - Update root README.md and PROJECT-CATALOG.md paths.
  - Run the markdown link checker until clean before opening the PR.
EOF
