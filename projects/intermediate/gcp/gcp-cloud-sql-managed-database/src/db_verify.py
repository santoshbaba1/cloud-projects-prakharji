"""
Verify a Cloud SQL database — the primary, a PITR-restored instance, or a read
replica — by counting rows and checking for the RPO marker row that db_seed.py
writes. Point --host at any of them to confirm the data is where you expect it.

Usage:
    python db_verify.py --host 127.0.0.1              # via Cloud SQL Auth Proxy
    python db_verify.py --host <REPLICA_PUBLIC_IP>     # direct to a replica
"""

import argparse
import os

import pymysql

RPO_MARKER_CUSTOMER = "RPO-MARKER"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=os.environ.get("DB_HOST", "127.0.0.1"))
    ap.add_argument("--user", default=os.environ.get("DB_USER", "orders_app"))
    ap.add_argument("--password", default=os.environ.get("DB_PASSWORD"))
    ap.add_argument("--database", default=os.environ.get("DB_NAME", "meridian_orders"))
    args = ap.parse_args()

    if not args.password:
        raise SystemExit("Provide --password (or the DB_PASSWORD env var)")

    conn = pymysql.connect(host=args.host, user=args.user, password=args.password,
                           database=args.database, connect_timeout=10)
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM orders")
        total = cur.fetchone()[0]
        cur.execute(
            "SELECT created_at FROM orders WHERE customer = %s ORDER BY id DESC LIMIT 1",
            (RPO_MARKER_CUSTOMER,),
        )
        marker = cur.fetchone()
        cur.execute("SELECT id, customer, amount, created_at FROM orders ORDER BY id DESC LIMIT 1")
        newest = cur.fetchone()

    print(f"Host        : {args.host}")
    print(f"Database    : {args.database}")
    print(f"Order rows  : {total}")
    print(f"Newest row  : {newest}")
    if marker:
        print(f"RPO marker  : FOUND (written {marker[0]}) -- PASS")
    else:
        print("RPO marker  : NOT FOUND -- FAIL (data predates the marker, or wrong instance)")
    conn.close()


if __name__ == "__main__":
    main()
