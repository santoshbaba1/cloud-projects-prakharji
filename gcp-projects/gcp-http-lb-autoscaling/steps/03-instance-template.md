# Step 3 — Instance Template

An **instance template** is a reusable blueprint for a VM: machine type, image, network, tags, and a
**startup script**. The managed instance group (next step) stamps out identical VMs from this
template. Because every VM comes from the same template, they're truly interchangeable — which is
what makes autoscaling and self-healing possible.

---

## 3.1 What Goes in the Template

| Setting | Value | Why |
|---------|-------|-----|
| Name | `web-template` | The blueprint's name |
| Machine type | `e2-small` | Small but has enough memory for pip + Flask |
| Network / subnet | `web-vpc` / `web-subnet` | The private network from Step 1 |
| **External IP** | **None** | Backends stay private; NAT handles outbound |
| Network tag | `web` | Matches the firewall rules from Step 2 |
| Startup script | installs Flask, runs the app on :80 | Makes each VM a working web server at boot |

The startup script is [`src/startup-script.sh`](../src/startup-script.sh) — it installs Flask and
launches [`src/app.py`](../src/app.py), which answers `/`, `/healthz`, and `/load`.

---

## 3.2 Console — Create the Template

1. **☰ → Compute Engine → Instance templates → Create instance template.**
2. **Name:** `web-template`. **Machine type:** `e2-small`.
3. Expand **Advanced options → Networking**:
   - **Network tags:** `web`
   - Under **Network interfaces**, edit the interface: **Network** = `web-vpc`, **Subnetwork** =
     `web-subnet`, and set **External IPv4 address** = **None**.
4. Expand **Advanced options → Management → Automation → Startup script** and paste the contents of
   [`src/startup-script.sh`](../src/startup-script.sh).
5. Click **Create**.

---

## 3.3 gcloud CLI (Alternative)

```bash
gcloud compute instance-templates create web-template \
  --machine-type=e2-small \
  --network=web-vpc \
  --subnet=web-subnet \
  --no-address \
  --tags=web \
  --metadata-from-file=startup-script=src/startup-script.sh
```

Key flags:

- `--no-address` → **no external IP** (the whole point of the private backend).
- `--tags=web` → matches every firewall rule from Step 2.
- `--metadata-from-file=startup-script=...` → GCP runs this script on first boot.

> Run the command from the project root (`gcp-projects/gcp-http-lb-autoscaling/`) so the relative
> path `src/startup-script.sh` resolves. Or use an absolute path.

Verify:

```bash
gcloud compute instance-templates describe web-template \
  --format='value(properties.machineType, properties.tags.items)'
```

---

## 3.4 Why a Template Instead of Just Making VMs?

- **Immutable & repeatable:** every VM is identical — no "works on that one server" drift.
- **Required for MIGs:** a managed instance group *must* be backed by a template.
- **Rolling updates:** to ship new code, you create a new template version and tell the MIG to roll
  onto it (Challenge 3), rather than logging into servers.

---

## Checkpoint

- [ ] `web-template` exists with machine type `e2-small`
- [ ] The template has **no external IP** (`--no-address`)
- [ ] The template carries tag `web` and the startup script is attached
- [ ] You understand a template is a *blueprint*, not a running VM (nothing is billing yet)

---

**Next:** [Step 4 — Managed Instance Group](./04-managed-instance-group.md)
