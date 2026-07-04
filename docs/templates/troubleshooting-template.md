# Troubleshooting Template

Copy the section below into a project's `troubleshooting.md`. Always use the **Error → Cause → Fix**
format so a stuck user can scan for their exact symptom.

---

<!-- ==== COPY FROM HERE ==== -->

# Troubleshooting — <Project Title>

> Find your error message or symptom below. Each entry says **what it means** and **how to fix it**.

## <Short symptom, e.g. "AccessDenied when the Lambda calls S3">

**Error / symptom**

```
<paste the exact error text or describe the observable symptom>
```

**Cause**

Plain-language explanation of why this happens.

**Fix**

1. Concrete step
2. Concrete step

```bash
# copy-paste command that resolves it, if applicable
```

**Verify**

How to confirm it's actually fixed.

---

## <Next symptom>

**Error / symptom** …

**Cause** …

**Fix** …

---

## Still stuck?

- Re-check [prerequisites.md](prerequisites.md) — most issues are a missing tool, permission, or region mismatch.
- Confirm your region matches the project (this repo uses `us-east-1` for AWS, `us-east1` for GCP).
- Check the relevant logs (CloudWatch Logs / `kubectl logs` / `gcloud logging read`).

<!-- ==== COPY TO HERE ==== -->
