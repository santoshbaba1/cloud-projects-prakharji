"""Generate ongoing changes on the SOURCE to prove CDC (change data capture).

While the DMS task is in the 'full load complete, replicating ongoing changes'
phase, run this against the SOURCE. It keeps inserting orders. Watch them appear
in the TARGET within seconds — that is CDC replaying the binlog. This is what
makes a near-zero-downtime migration possible: the source stays live during the
whole migration.

Usage:
    python3 cdc_writer.py --host <source-ip> --user admin --password '<pw>' --count 20
"""

import argparse
import time
import uuid

import pymysql


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=True)
    ap.add_argument("--port", type=int, default=3306)
    ap.add_argument("--user", default="admin")
    ap.add_argument("--password", required=True)
    ap.add_argument("--count", type=int, default=20)
    ap.add_argument("--interval", type=float, default=1.0)
    args = ap.parse_args()

    conn = pymysql.connect(host=args.host, port=args.port,
                           user=args.user, password=args.password, autocommit=True)
    cur = conn.cursor()
    cur.execute("USE shopdb")
    cur.execute("SELECT id FROM customers LIMIT 1")
    customer_id = cur.fetchone()[0]

    for i in range(args.count):
        oid = str(uuid.uuid4())
        cur.execute("INSERT INTO orders VALUES (%s,%s,%s,%s)",
                    (oid, customer_id, 99.00 + i, "CDC-LIVE"))
        print(f"[{i+1}/{args.count}] inserted order {oid} on SOURCE — expect it in TARGET soon")
        time.sleep(args.interval)

    conn.close()
    print("Done. Verify these CDC-LIVE orders now exist in the TARGET (db_verify.py).")


if __name__ == "__main__":
    main()
