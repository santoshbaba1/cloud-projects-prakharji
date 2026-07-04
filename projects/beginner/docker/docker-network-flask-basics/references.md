# References

Official Docker documentation and related material for this project.

## Docker networking

- [Networking overview](https://docs.docker.com/network/) — how Docker networking is structured
- [Bridge network driver](https://docs.docker.com/network/drivers/bridge/) — default vs. user-defined bridge, and the DNS difference at the heart of this lab
- [Container networking](https://docs.docker.com/config/containers/container-networking/) — ports, published vs. exposed
- [`docker network create`](https://docs.docker.com/reference/cli/docker/network/create/) — CLI reference
- [`docker network inspect`](https://docs.docker.com/reference/cli/docker/network/inspect/) — CLI reference
- [`docker network connect`](https://docs.docker.com/reference/cli/docker/network/connect/) — attach a running container to another network

## Docker Compose

- [Compose overview](https://docs.docker.com/compose/) — what Compose is and why
- [Networking in Compose](https://docs.docker.com/compose/how-tos/networking/) — the default network Compose creates and how services find each other by name
- [Compose file reference](https://docs.docker.com/reference/compose-file/) — the full `docker-compose.yml` schema

## Flask

- [Flask documentation](https://flask.palletsprojects.com/) — the micro web framework used for both services

## Related projects in this repo

- [ECS on Fargate Basics](../../../intermediate/aws/aws-ecs-fargate-basics/README.md) — the same container, run in AWS
- [Monolith → Microservices on EKS](../../../advanced/kubernetes/eks-monolith-to-microservices/README.md) — service-to-service DNS on Kubernetes
