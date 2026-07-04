# Challenges

Extensions that build on the finished project. Each one deepens a different piece of Docker
networking. Do them in any order.

## 1. Add a third container (a data tier)

Add a `redis` (or `postgres`) container to `appnet` and have the **backend** read/write it by name
(`redis:6379`). Update `docker-compose.yml` with the new service. This mirrors the real web → API →
database chain — three tiers, all finding each other by name.

## 2. Prove IPs are unstable, names are not

Run the stack, note the backend's IP (`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' backend`),
then `docker rm -f backend` and re-run it. The IP usually changes; the **name** `backend` still
resolves. Explain in your own words why hardcoding the IP would have broken the frontend.

## 3. Network isolation between two networks

Create a second network `backnet`. Put `backend` on **both** `appnet` and `backnet`
(`docker network connect backnet backend`), but keep `frontend` only on `appnet`. Add a `db`
container on `backnet` only. Verify the frontend **cannot** reach `db` (different network) while the
backend **can** — that's how you segment a public tier from a private one.

## 4. DNS aliases

Give the backend a friendlier name to the frontend using `--network-alias api` (CLI) or the
`networks: { appnet: { aliases: [api] } }` form in Compose. Point `BACKEND_URL` at `http://api:5000`
and confirm it still works. Note that a container can answer to several names on one network.

## 5. Scale the backend and load-balance by name

With Compose, run `docker compose up --scale backend=3`. Docker's DNS returns **all three** backend
IPs for the name `backend` and round-robins across them. Hit the frontend several times and watch the
`container` field in the response change (it prints the backend's hostname). This is client-side DNS
load balancing, for free.

## 6. Add container health checks

Add a `healthcheck:` to each service in `docker-compose.yml` (curl the `/health` endpoint) and make
the frontend `depends_on` the backend `condition: service_healthy`. Observe how Compose now waits for
the backend to be healthy before starting the frontend — removing the race in Challenge-free runs.

## 7. Publish nothing, debug from inside

Remove the frontend's published port so **nothing** is exposed to the host. Reach the app by
`exec`-ing into a throwaway container on the same network:
`docker run --rm -it --network appnet curlimages/curl http://frontend:8080/`. This is how you debug a
fully-internal service that has no host port.
