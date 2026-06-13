# Step 10 — Deploy with GitHub Actions (OIDC + SSM)

The final piece is **automation of deployment**. Instead of SSHing into servers, a GitHub
Actions workflow assumes an AWS role via **OIDC** (no stored keys), validates the app, and
rolls the new code out to every instance with **SSM Run Command** (no open SSH port).

The sample workflow is `.github/workflows/deploy.yml`. This step creates the AWS side it
needs.

---

## 10.1 The Pipeline at a Glance

```mermaid
flowchart LR
    Push["git push to main"] --> GA["GitHub Actions runner"]
    GA -->|OIDC token| IAM["AWS IAM<br/>GitHubActionsDeployRole"]
    IAM -->|temp creds| GA
    GA -->|aws s3 sync| S3["S3 deploy bucket"]
    GA -->|ssm send-command| SSM["SSM Run Command<br/>targets tag Project=webapp"]
    SSM -->|pull + restart| EC2["EC2 instances"]
    EC2 -->|aws s3 sync| S3
```

No long-lived `AWS_ACCESS_KEY_ID` lives in GitHub. The runner gets **short-lived**
credentials by proving its identity to AWS with an OIDC token — exactly the federation
pattern from the [iam-roles-and-policies](../../iam-roles-and-policies/README.md) project.

---

## 10.2 Create the GitHub OIDC Provider (once per account)

1. **IAM → Identity providers → Add provider**.
   - Provider type: **OpenID Connect**
   - Provider URL: `https://token.actions.githubusercontent.com`
   - Audience: `sts.amazonaws.com`
2. **Add provider.**

---

## 10.3 Create the Deploy Role

Create `GitHubActionsDeployRole` with a trust policy scoped to **your** repo (replace
`ORG/REPO`), so only that repository can assume it:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Federated": "arn:aws:iam::<ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"},
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {"token.actions.githubusercontent.com:aud": "sts.amazonaws.com"},
      "StringLike": {"token.actions.githubusercontent.com:sub": "repo:ORG/REPO:ref:refs/heads/main"}
    }
  }]
}
```

Attach a **least-privilege** permission policy — only what the deploy needs:

| Permission | Why It's Needed |
|------------|-----------------|
| `s3:PutObject`, `s3:ListBucket` on the deploy bucket | Upload the new app artifact |
| `ssm:SendCommand` | Trigger the rollout on the instances |
| `ssm:GetCommandInvocation`, `ssm:ListCommandInvocations` | Poll the deploy result |

```bash
aws iam create-role --role-name GitHubActionsDeployRole \
  --assume-role-policy-document file://github-trust.json
# then attach an inline policy with the permissions above (see challenges.md for the JSON)
```

> Also create the S3 deploy bucket (e.g. `webapp-deploy-<account-id>`) and grant the
> **instance role** (`WebAppInstanceRole`) `s3:GetObject` on it, so instances can pull the
> artifact during `aws s3 sync`.

---

## 10.4 Wire Up the Workflow

1. Copy `.github/workflows/deploy.yml` into the `.github/workflows/` folder of **your app
   repository** (not the cloud-projects repo — GitHub only runs workflows from a repo's own
   root).
2. Replace the placeholders:
   - `<ACCOUNT_ID>` → your account id (in the `role-to-assume` ARN)
   - `<DEPLOY_BUCKET>` → your S3 deploy bucket name
3. Commit and push to `main`. The **Actions** tab shows the run: it validates the app with
   `test_app.py`, syncs `src/` to S3, then SSM tells every `Project=webapp` instance to pull
   and `systemctl restart webapp.service`.

---

## 10.5 Verify the Deploy

1. Bump `APP_VERSION` in `src/app.py` (e.g. to `1.1.0`), commit, push.
2. Watch the Actions run go green.
3. `curl http://<ALB-DNS-name>/` — the `version` field now shows `1.1.0`.
4. Cross-check in **CloudTrail Event history** for the `SendCommand` event — the whole
   deploy is auditable back to the commit SHA.

---

## Checkpoint

- [ ] GitHub OIDC identity provider exists in IAM
- [ ] `GitHubActionsDeployRole` trusts only `repo:ORG/REPO` on `main`
- [ ] Role has least-privilege S3 + SSM permissions
- [ ] S3 deploy bucket exists; instance role can `GetObject` from it
- [ ] A push to `main` deploys new code; `version` updates behind the ALB
- [ ] The deploy appears in CloudTrail

---

**Next:** [Step 11 — Cleanup](./11-cleanup.md)
