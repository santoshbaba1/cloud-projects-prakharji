"""
Verify a database (the original, a restored instance, or a promoted replica) by
counting rows and showing the newest order. Run it against any endpoint to confirm
a restore brought your data back.

Usage:
    python db_verify.py --host <ENDPOINT> --user admin --password <PW>
"""

import argparse
import os

import pymysql


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=os.environ.get("DB_HOST"))
    ap.add_argument("--user", default=os.environ.get("DB_USER", "admin"))
    ap.add_argument("--password", default=os.environ.get("DB_PASSWORD"))
    ap.add_argument("--database", default="appdb")
    args = ap.parse_args()

    if not args.host or not args.password:
        raise SystemExit("Provide --host and --password (or DB_HOST / DB_PASSWORD env vars)")

    conn = pymysql.connect(host=args.host, user=args.user, password=args.password,
                           database=args.database, connect_timeout=10)
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM orders")
        total = cur.fetchone()[0]
        cur.execute("SELECT id, customer, amount, created_at FROM orders ORDER BY id DESC LIMIT 1")
        newest = cur.fetchone()

    print(f"Host    : {args.host}")
    print(f"Orders  : {total}")
    print(f"Newest  : {newest}")
    conn.close()


if __name__ == "__main__":
    main()
