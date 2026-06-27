"""Verify a MySQL endpoint's 'shopdb' contents — run against SOURCE and TARGET.

Prints the row counts and a cheap checksum per table so you can prove the target
matches the source after the DMS full load (+ CDC). Run it against both hosts and
compare the output line-for-line.

Usage:
    python3 db_verify.py --host <source-or-target-host> --user admin --password '<pw>'
"""

import argparse

import pymysql


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=True)
    ap.add_argument("--port", type=int, default=3306)
    ap.add_argument("--user", default="admin")
    ap.add_argument("--password", required=True)
    args = ap.parse_args()

    conn = pymysql.connect(host=args.host, port=args.port,
                           user=args.user, password=args.password)
    cur = conn.cursor()
    cur.execute("USE shopdb")

    for table in ("customers", "orders"):
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        # CHECKSUM TABLE gives a content-sensitive value; equal source/target = parity
        cur.execute(f"CHECKSUM TABLE {table}")
        checksum = cur.fetchone()[1]
        print(f"{table:10s} rows={count:<6d} checksum={checksum}")

    conn.close()
    print("Compare this output between SOURCE and TARGET — they should be identical.")


if __name__ == "__main__":
    main()
