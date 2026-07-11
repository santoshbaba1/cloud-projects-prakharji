"""
Seed the Cloud SQL demo database with a known table, a few sample orders, and one
special "RPO marker" row you can use as a Recovery Point Objective reference point:
"I want to recover to just after this marker was written."

Connect via the Cloud SQL Auth Proxy (127.0.0.1:3306) or a direct public IP — the
proxy is the GCP-idiomatic path and needs no SSL cert handling on your end.

Usage:
    pip install -r requirements.txt
    export DB_HOST=127.0.0.1        # Auth Proxy default; or the instance's public IP
    export DB_USER=orders_app
    export DB_PASSWORD=<password>
    export DB_NAME=meridian_orders
    python db_seed.py [--rows 5]
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

RPO_MARKER_CUSTOMER = "RPO-MARKER"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=os.environ.get("DB_HOST", "127.0.0.1"))
    ap.add_argument("--user", default=os.environ.get("DB_USER", "orders_app"))
    ap.add_argument("--password", default=os.environ.get("DB_PASSWORD"))
    ap.add_argument("--database", default=os.environ.get("DB_NAME", "meridian_orders"))
    ap.add_argument("--rows", type=int, default=5)
    args = ap.parse_args()

    if not args.password:
        raise SystemExit("Provide --password (or the DB_PASSWORD env var)")

    conn = pymysql.connect(host=args.host, user=args.user, password=args.password,
                           database=args.database, autocommit=True, connect_timeout=10)
    with conn.cursor() as cur:
        cur.execute(DDL)
        now = datetime.datetime.utcnow()
        for i in range(args.rows):
            cur.execute(
                "INSERT INTO orders (customer, amount, created_at) VALUES (%s, %s, %s)",
                (f"customer-{i+1}", round(15 + i * 4.25, 2), now),
            )
        # A dedicated marker row (not a real order) gives db_verify.py one unambiguous
        # thing to check for after a restore, instead of relying on row counts alone.
        cur.execute(
            "INSERT INTO orders (customer, amount, created_at) VALUES (%s, %s, %s)",
            (RPO_MARKER_CUSTOMER, 0.00, now),
        )
        cur.execute("SELECT COUNT(*) FROM orders")
        total = cur.fetchone()[0]

    print(f"Seeded {args.rows} order row(s) + 1 RPO marker. Table now has {total} row(s).")
    print(f"RPO MARKER (UTC): {now.isoformat()}Z  <-- restore to a time AFTER this")
    conn.close()


if __name__ == "__main__":
    main()
