# Step 1 — Install the gcloud CLI & Authenticate

Before you can build anything on Google Cloud, you need two things on your machine:

1. The **gcloud CLI** — Google Cloud's command-line tool (the equivalent of the AWS CLI).
2. An **authenticated session** tied to your Google account and a **project**.

This step gets both done. Every later step gives you a **Console** (web UI) path *and* a
**gcloud CLI** path — but the CLI path only works once this step is complete.

> **Console-only?** If you plan to click through the web Console for everything, you still need a
> Google Cloud **project** (sections 1.4–1.6). You can skip the install, but installing gcloud is
> strongly recommended — the CLI paths are faster and easier to copy.

---

## 1.1 What Is a Project? (Read This First)

On Google Cloud, **everything lives inside a Project**. A project is a billing-and-permissions
boundary — like an AWS account, but you can have many projects under one Google login. Resources
(networks, VMs, firewall rules) belong to exactly one project.

```
Google Account (you)
└── Project: my-networking-labs   ← everything in this repo goes here
    ├── VPC networks
    ├── Firewall rules
    └── Compute Engine VMs
```

You'll create one project and reuse it for **both** GCP projects in this series.

---

## 1.2 Install the gcloud CLI

Pick your operating system.

### Linux

```bash
# Download and run the interactive installer
curl -sSL https://sdk.cloud.google.com | bash

# Restart your shell so the `gcloud` command is on your PATH
exec -l $SHELL
```

> On Debian/Ubuntu you can instead use the apt package — see the
> [official install guide](https://cloud.google.com/sdk/docs/install#deb).

### macOS

```bash
# With Homebrew (recommended)
brew install --cask google-cloud-sdk
```

Or download the `.tar.gz` from the [install guide](https://cloud.google.com/sdk/docs/install#mac)
and run `./google-cloud-sdk/install.sh`.

### Windows

Download and run the installer from the
[official install guide](https://cloud.google.com/sdk/docs/install#windows). It adds `gcloud` to
your PATH and opens a terminal at the end. Use that terminal (or PowerShell) for the CLI commands
in this repo.

### Verify the install (all platforms)

```bash
gcloud --version
```

You should see `Google Cloud SDK` and a version number. If the command isn't found, close and
reopen your terminal.

---

## 1.3 Log In

This opens a browser and links the CLI to your Google account:

```bash
gcloud auth login
```

A browser window opens. Choose your Google account and click **Allow**. When it says you're
authenticated, return to the terminal.

---

## 1.4 Create a Project

You need a **globally unique** project ID. Add a few random digits to make it unique.

### Console

1. Go to the [Cloud Console](https://console.cloud.google.com/).
2. Click the **project picker** at the top of the page → **New Project**.
3. Fill in the form:

   | Field | Value |
   |-------|-------|
   | Project name | `My Networking Labs` |
   | Project ID | `my-networking-labs-1234` (must be globally unique) |

4. Click **Create**, then select the new project in the project picker.

### gcloud CLI (Alternative)

```bash
# Pick a globally-unique ID (letters, digits, hyphens; 6–30 chars)
export PROJECT_ID="my-networking-labs-$RANDOM"

gcloud projects create "$PROJECT_ID" --name="My Networking Labs"

# Make it your default so you don't have to type --project every time
gcloud config set project "$PROJECT_ID"
```

Confirm which project is active at any time:

```bash
gcloud config get-value project
```

---

## 1.5 Link Billing

Google Cloud requires a **billing account** even for free-tier resources. Nothing here is expensive
(see [costs.md](../costs.md)), but the account must exist.

### Console

1. Go to **Billing** in the left menu (☰).
2. If you have no billing account, click **Create account** and follow the prompts (you'll get a
   free-trial credit as a new user).
3. On the project, click **Link a billing account** and select yours.

### gcloud CLI (Alternative)

```bash
# List your billing accounts and copy the ACCOUNT_ID (looks like 0X0X0X-0X0X0X-0X0X0X)
gcloud billing accounts list

# Link it to your project
gcloud billing projects link "$PROJECT_ID" \
  --billing-account=0X0X0X-0X0X0X-0X0X0X
```

---

## 1.6 Enable the Compute Engine API

On Google Cloud, each service's API must be **enabled** per project before you can use it. Networks,
firewall rules, and VMs are all part of the **Compute Engine API**.

### Console

1. Go to **APIs & Services** → **Enabled APIs & services** → **+ Enable APIs and Services**.
2. Search for **Compute Engine API**, open it, and click **Enable**. (This takes a minute.)

### gcloud CLI (Alternative)

```bash
gcloud services enable compute.googleapis.com
```

---

## 1.7 Set a Default Region and Zone

We'll use **`us-east1`** (region) and **`us-east1-b`** (zone) throughout, to match the rest of this
repo. Setting defaults means you can omit `--region`/`--zone` on most commands.

```bash
gcloud config set compute/region us-east1
gcloud config set compute/zone us-east1-b
```

> **Region vs. Zone:** A **region** (e.g. `us-east1`) is a geographic area. A **zone** (e.g.
> `us-east1-b`) is one isolated data center inside that region. **Subnets** live in a region; **VMs**
> live in a zone.

---

## Checkpoint

- [ ] `gcloud --version` prints a version number
- [ ] `gcloud auth login` succeeded (browser said "You are now authenticated")
- [ ] `gcloud config get-value project` prints your project ID
- [ ] Billing is linked to the project
- [ ] Compute Engine API is enabled
- [ ] Default region `us-east1` and zone `us-east1-b` are set

---

**Next:** [Step 2 — Create a Custom VPC & Subnets](./02-create-vpc-subnets.md)
