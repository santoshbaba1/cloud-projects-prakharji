# Step 7 — Cleanup

Everything is local, so cleanup is fast and there's no bill to stop. The one thing to reclaim is
your laptop's CPU/RAM by deleting the cluster.

---

## 7.1 (Optional) Tidy Inside the Cluster First

If you want to practice teardown without destroying the cluster:

```bash
velero backup delete webapp-backup --confirm
velero restore delete webapp-restore --confirm
kubectl delete namespace webapp velero
```

---

## 7.2 Delete the Whole Cluster

This is the real cleanup — it removes the cluster and everything in it at once.

### kind

```bash
kind delete cluster --name optrec
```

### minikube

```bash
minikube delete --profile optrec
```

---

## 7.3 (Optional) Remove the Local Image and Files

```bash
docker image rm webapp:1.0
rm -f credentials-velero
```

---

## 7.4 Verify

```bash
kubectl config get-contexts        # the optrec context is gone
docker ps                          # no kind/minikube node container running
```

---

## Checkpoint

- [ ] The `optrec` cluster is deleted (`kind delete` / `minikube delete`)
- [ ] No cluster node container shows in `docker ps`
- [ ] (Optional) Local `webapp:1.0` image and `credentials-velero` removed
- [ ] Your laptop's CPU/RAM are reclaimed

That's the series complete — you've practiced **optimization and recovery** on **EC2**
([Project 1](../../../aws/aws-compute-rightsizing/README.md)), **RDS**
([Project 2](../../../../advanced/aws/aws-rds-disaster-recovery/README.md)), and **Kubernetes** (here). See
[challenges.md](../challenges.md) to push further, including porting
this to **Amazon EKS** with real S3-backed Velero backups.
