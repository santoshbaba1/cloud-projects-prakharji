"""
Seed the RDS demo database with a known table and rows, then print a "marker"
timestamp. You use that marker as your Recovery Point Objective (RPO) reference:
"I want to recover to just after this row was written."

Usage:
    pip install pymysql
    python db_seed.py --host <ENDPOINT> --user admin --password <PW> [--rows 5]

The host/user/password can also come from env vars DB_HOST / DB_USER / DB_PASSWORD.
"""

import argparse
import datetime
import os

import pymysql

DDL = """
CREATE TABLE IF NOT EXISTS orders (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    customer    VARCHAR(64) NOT NULL,
    amount      DECIMAL(10,2) NOT NULL,
    created_at  DATETIME NOT NULL
)
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=os.environ.get("DB_HOST"))
    ap.add_argument("--user", default=os.environ.get("DB_USER", "admin"))
    ap.add_argument("--password", default=os.environ.get("DB_PASSWORD"))
    ap.add_argument("--database", default="appdb")
    ap.add_argument("--rows", type=int, default=5)
    args = ap.parse_args()

    if not args.host or not args.password:
        raise SystemExit("Provide --host and --password (or DB_HOST / DB_PASSWORD env vars)")

    conn = pymysql.connect(host=args.host, user=args.user, password=args.password,
                           autocommit=True, connect_timeout=10)
    with conn.cursor() as cur:
        cur.execute("CREATE DATABASE IF NOT EXISTS appdb")
        cur.execute("USE appdb")
        cur.execute(DDL)
        now = datetime.datetime.utcnow()
        for i in range(args.rows):
            cur.execute(
                "INSERT INTO orders (customer, amount, created_at) VALUES (%s, %s, %s)",
                (f"customer-{i+1}", round(10 + i * 3.5, 2), now),
            )
        cur.execute("SELECT COUNT(*) FROM orders")
        total = cur.fetchone()[0]

    print(f"Seeded {args.rows} row(s). Table now has {total} order(s).")
    print(f"RPO MARKER (UTC): {now.isoformat()}Z  <-- restore to a time after this")
    conn.close()


if __name__ == "__main__":
    main()
