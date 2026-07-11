import os
import time

import redis

CACHE_TTL_SECONDS = 60

FAKE_DATABASE = {
    "product:SKU-1001": "Wireless Mouse - $19.99 - 42 in stock",
    "product:SKU-2044": "Mechanical Keyboard - $49.50 - 17 in stock",
}


def get_client() -> redis.Redis:
    host = os.environ.get("REDIS_HOST", "localhost")
    port = int(os.environ.get("REDIS_PORT", "6379"))
    return redis.Redis(host=host, port=port, decode_responses=True, socket_timeout=5)


def fetch_from_database(key: str) -> str:
    time.sleep(1.5)
    return FAKE_DATABASE.get(key, "NOT FOUND")


def get_cached(client: redis.Redis, key: str) -> str:
    cached = client.get(key)
    if cached is not None:
        print(f"  [HIT]  {key} -> {cached}")
        return cached

    print(f"  [MISS] {key} -> fetching from database...")
    value = fetch_from_database(key)
    client.setex(key, CACHE_TTL_SECONDS, value)
    print(f"  [SET]  {key} cached for {CACHE_TTL_SECONDS}s")
    return value


def main() -> None:
    client = get_client()
    client.ping()

    key = "product:SKU-1001"

    print("First read (expect a miss):")
    get_cached(client, key)

    print("\nSecond read, immediately after (expect a hit):")
    get_cached(client, key)

    print("\nExpiring the key manually to simulate TTL elapsing...")
    client.delete(key)

    print("Third read, after expiry (expect a miss again):")
    get_cached(client, key)


if __name__ == "__main__":
    main()
