# References

Official Docker documentation for the networking and storage features used here.

## Networking

- [Networking overview](https://docs.docker.com/network/) — drivers and concepts
- [Bridge networks](https://docs.docker.com/network/drivers/bridge/) — user-defined bridges and embedded DNS
- [`--internal` networks](https://docs.docker.com/reference/cli/docker/network/create/#internal) — isolating a network from external access
- [`docker network create`](https://docs.docker.com/reference/cli/docker/network/create/) / [`connect`](https://docs.docker.com/reference/cli/docker/network/connect/) / [`inspect`](https://docs.docker.com/reference/cli/docker/network/inspect/)

## Storage

- [Storage overview](https://docs.docker.com/storage/) — volumes vs bind mounts vs tmpfs
- [Volumes](https://docs.docker.com/storage/volumes/) — named volumes, the recommended way to persist data
- [Bind mounts](https://docs.docker.com/storage/bind-mounts/) — mounting a host directory
- [tmpfs mounts](https://docs.docker.com/storage/tmpfs/) — in-memory, ephemeral storage
- [Back up, restore, or migrate volumes](https://docs.docker.com/storage/volumes/#back-up-restore-or-migrate-data-volumes) — the helper-container pattern used in Step 5
- [`docker volume`](https://docs.docker.com/reference/cli/docker/volume/) — CLI reference

## Compose

- [Compose overview](https://docs.docker.com/compose/)
- [Networking in Compose](https://docs.docker.com/compose/how-tos/networking/) — default network, multiple networks, `internal`
- [Volumes in Compose](https://docs.docker.com/reference/compose-file/volumes/) — named volumes and their lifecycle
- [`docker compose down`](https://docs.docker.com/reference/cli/docker/compose/down/) — note the `-v/--volumes` flag

## Related projects in this repo

- [Docker Networking Basics (beginner)](../../../beginner/docker/docker-network-flask-basics/README.md) — the single-network foundation
- [ECS on Fargate — Advanced](../../../advanced/aws/aws-ecs-fargate-advanced/README.md) — networks + persistence in AWS
- [k8s Optimization & Recovery](../../kubernetes/k8s-optimization-and-recovery/README.md) — persistent volumes + backup/restore with Velero
