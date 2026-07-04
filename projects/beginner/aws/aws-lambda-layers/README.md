# Lambda Layers — Sharing Dependencies Across Functions

```yaml
level: beginner
cloud: aws
domain: serverless
technology:
  - lambda
  - iam
  - cloudwatch
estimated_time: 45 min
estimated_cost: free-tier
deployment_type: console + cli
cleanup_required: true
status: ready
```

## What You'll Build

Two Lambda functions that rely on third-party libraries — `requests` and `pandas` — packaged as **Lambda Layers**. You'll:

1. Build two layers (requests, pandas+numpy) locally
2. Publish both as versioned layers in your AWS account
3. Deploy Lambda functions that attach and use those layers
4. Understand how Lambda resolves layer contents at runtime
5. Attach multiple layers to a single function

---

## What Is a Lambda Layer?

A Lambda layer is a ZIP archive that Lambda extracts into the `/opt/` directory of the execution environment before your function runs. The Python runtime automatically adds `/opt/python` to `sys.path`, making any packages inside importable.

```
/opt/
└── python/
    └── lib/
        └── python3.14/
            └── site-packages/
                ├── requests/          ← from RequestsLayer
                ├── pandas/            ← from PandasLayer
                └── numpy/             ← from PandasLayer
```

Layers let you:
- **Share code** across many functions without duplicating it in each ZIP
- **Keep function ZIPs small** — each function ZIP only contains your business logic
- **Version dependencies independently** — update a layer without touching function code
- **Reuse third-party libraries** that are not part of the standard library

---

## Architecture

```
  ┌──────────────────────────────────────────────────────┐
  │                    Lambda Runtime                     │
  │                                                        │
  │  /var/task/          (your function code)             │
  │  /opt/python/        (layer contents → added to path) │
  │                                                        │
  │  ┌──────────────────────┐  ┌────────────────────────┐ │
  │  │  RequestsFunction    │  │   PandasFunction       │ │
  │  │  lambda_with_requests│  │  lambda_with_pandas.py │ │
  │  │  .py                 │  │                        │ │
  │  │  Layer: RequestsLayer│  │  Layers: RequestsLayer │ │
  │  └──────────────────────┘  │          PandasLayer   │ │
  │                            └────────────────────────┘ │
  └──────────────────────────────────────────────────────┘
```

---

## Layer Size Limits

| Limit | Value |
|-------|-------|
| Max unzipped layer size | 250 MB |
| Max ZIP size (per layer) | 50 MB |
| Max layers per function | 5 |
| Total unzipped size (function + all layers) | 250 MB |

`requests` + dependencies: ~3 MB unzipped  
`pandas` + `numpy`: ~60 MB unzipped  
Both well within limits.

---

## Project Structure

```
lambda-layers/
├── README.md
├── steps/
│   ├── 01-iam-role.md              ← Execution role for layer functions
│   ├── 02-build-requests-layer.md  ← Build and publish RequestsLayer
│   ├── 03-build-pandas-layer.md    ← Build and publish PandasLayer
│   ├── 04-deploy-functions.md      ← Deploy functions with layers attached
│   ├── 05-multiple-layers.md       ← Attach both layers to one function
│   ├── 06-testing.md               ← Invoke and verify
│   └── 07-cleanup.md
├── src/
│   ├── lambda_with_requests.py     ← Uses RequestsLayer
│   └── lambda_with_pandas.py       ← Uses PandasLayer
├── layers/
│   ├── requests-layer/
│   │   └── build.sh                ← Build script for RequestsLayer
│   └── pandas-layer/
│       └── build.sh                ← Build script for PandasLayer (Docker optional)
├── troubleshooting.md
└── challenges.md
```

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| AWS account | Lambda, IAM, CloudWatch access |
| AWS CLI | v2.x |
| Python | 3.9+ locally for running build scripts |
| pip | Must be able to install packages |
| Docker | Optional but recommended for the pandas layer (see Step 3) |
| Completed | [Lambda Basics](../aws-lambda-basics/README.md) |

---

## Step by Step

| Step | File | Goal |
|------|------|------|
| 1 | `01-iam-role.md` | Create execution role (needs outbound internet for requests) |
| 2 | `02-build-requests-layer.md` | Build and publish the requests layer |
| 3 | `03-build-pandas-layer.md` | Build and publish the pandas layer |
| 4 | `04-deploy-functions.md` | Deploy functions referencing the layers |
| 5 | `05-multiple-layers.md` | Attach both layers to one function |
| 6 | `06-testing.md` | Invoke and verify |
| 7 | `07-cleanup.md` | Remove all resources |

Start with **Step 1 →** [`steps/01-iam-role.md`](steps/01-iam-role.md)

---

## What's Next

- [Lambda Troubleshooting & Monitoring](../../../intermediate/aws/aws-lambda-troubleshooting-monitoring/README.md) — the most advanced project
