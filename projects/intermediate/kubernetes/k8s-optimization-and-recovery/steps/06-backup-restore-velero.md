# Step 6 — Back Up & Restore with Velero

Self-healing (Step 5) recovers pods, but it can't bring back a **deleted namespace** — once the
objects are gone, the controller has nothing to reconcile. For that you need real backups.
**Velero** backs up Kubernetes objects (and volumes) to object storage and restores them. You'll
back up to **MinIO**, an S3-compatible store running in the cluster — so this is the exact same
workflow you'd use on EKS with a real S3 bucket, at zero cost.

This is the Kubernetes parallel to [RDS DR](../../../../advanced/aws/aws-rds-disaster-recovery/README.md): back up state,
simulate a disaster, restore, verify.

---

## 6.1 Install MinIO (the S3 stand-in)

Apply a minimal MinIO deployment and a bucket-creating Job in a `velero` namespace:

```bash
kubectl create namespace velero

kubectl apply -n velero -f - <<'YAML'
apiVersion: apps/v1
kind: Deployment
metadata: { name: minio, labels: { app: minio } }
spec:
  selector: { matchLabels: { app: minio } }
  template:
    metadata: { labels: { app: minio } }
    spec:
      containers:
        - name: minio
          image: minio/minio:latest
          args: ["server", "/data", "--console-address", ":9001"]
          env:
            - { name: MINIO_ROOT_USER, value: "minio" }
            - { name: MINIO_ROOT_PASSWORD, value: "minio123" }
          ports: [{ containerPort: 9000 }]
---
apiVersion: v1
kind: Service
metadata: { name: minio }
spec:
  selector: { app: minio }
  ports: [{ port: 9000, targetPort: 9000 }]
YAML

# create the "velero" bucket once MinIO is up
kubectl wait -n velero --for=condition=available deploy/minio --timeout=120s
kubectl run -n velero mc --rm -it --restart=Never --image=minio/mc:latest -- \
  sh -c 'mc alias set m http://minio:9000 minio minio123 && mc mb -p m/velero'
```

> On a real cluster you'd point Velero at an **S3 bucket** with an IAM-scoped credential. MinIO
> speaks the S3 API, so the only thing that changes for EKS is the endpoint and credentials —
> the Velero commands below are identical.

---

## 6.2 Install Velero Pointed at MinIO

Install the [Velero CLI](https://velero.io/docs/main/basic-install/), then:

```bash
cat > credentials-velero <<'EOF'
[default]
aws_access_key_id=minio
aws_secret_access_key=minio123
EOF

velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.10.0 \
  --bucket velero \
  --secret-file ./credentials-velero \
  --use-volume-snapshots=false \
  --backup-location-config \
region=minio,s3ForcePathStyle=true,s3Url=http://minio.velero.svc:9000

kubectl get pods -n velero          # velero pod should reach Running
velero backup-location get          # PHASE should be Available
```

> `--use-volume-snapshots=false`: we're backing up Kubernetes **objects** (Deployment, Service,
> ConfigMap, HPA, PDB) — no persistent volumes here. For stateful apps you'd enable volume
> snapshots or **File System Backup** ([Challenge 5](../challenges.md)).

---

## 6.3 Back Up the `webapp` Namespace

```bash
velero backup create webapp-backup --include-namespaces webapp --wait
velero backup describe webapp-backup
velero backup get        # STATUS Completed
```

The backup — every object in `webapp`, including the ConfigMap holding your `/data` value — now
sits in the MinIO bucket. This is your **recovery point**.

---

## 6.4 Simulate a Disaster

Delete the entire namespace. Self-healing **cannot** save you here — the controllers are gone too:

```bash
kubectl delete namespace webapp
kubectl get ns webapp          # NotFound
kubectl get pods -n webapp     # nothing
```

Your app, its config, and its `/data` value are all gone.

---

## 6.5 Restore from the Backup

```bash
velero restore create webapp-restore --from-backup webapp-backup --wait
velero restore describe webapp-restore     # STATUS Completed

kubectl get ns webapp
kubectl get all,configmap,hpa,pdb -n webapp
```

The namespace, Deployment, Service, ConfigMap, HPA, and PDB are all back. Wait for the pods to be
Ready, then prove the **state** returned:

```bash
kubectl port-forward -n webapp svc/webapp 8080:80
curl -s localhost:8080/data
# -> "v1 — this value was captured by the Velero backup"
```

The exact value from Step 2 is restored. You've completed a full Kubernetes DR cycle: **back up →
destroy → restore → verify** — RPO = age of the backup, RTO = restore duration.

> **Backups you never test are hopes.** You just *tested* this one by actually deleting and
> restoring. Schedule recurring backups with `velero schedule create webapp-daily --schedule
> "0 2 * * *" --include-namespaces webapp` and periodically rehearse the restore
> ([Challenge 6](../challenges.md)).

---

## Checkpoint

- [ ] MinIO is Running and a `velero` bucket exists
- [ ] `velero backup-location get` shows **Available**
- [ ] `webapp-backup` completed
- [ ] Deleting the namespace removed everything
- [ ] `webapp-restore` completed and `/data` returns the original value

---

**Next:** [Step 7 — Cleanup](./07-cleanup.md)
