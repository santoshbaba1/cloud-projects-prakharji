"""Seed the SOURCE MySQL with a small 'shopdb' so there's data to migrate.

Run this against the source MySQL (on EC2) BEFORE you start the DMS task. It
creates a database, two tables, and rows, then prints a row count you'll compare
against the target after migration (your data-parity check / RPO marker).

Usage:
    pip install pymysql
    python3 db_seed.py --host <source-ip> --user admin --password '<pw>'
"""

import argparse
import uuid

import pymysql


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=True)
    ap.add_argument("--port", type=int, default=3306)
    ap.add_argument("--user", default="admin")
    ap.add_argument("--password", required=True)
    args = ap.parse_args()

    conn = pymysql.connect(host=args.host, port=args.port,
                           user=args.user, password=args.password, autocommit=True)
    cur = conn.cursor()

    cur.execute("CREATE DATABASE IF NOT EXISTS shopdb")
    cur.execute("USE shopdb")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id   VARCHAR(36) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            city VARCHAR(100) NOT NULL
        )""")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id          VARCHAR(36) PRIMARY KEY,
            customer_id VARCHAR(36) NOT NULL,
            amount      DECIMAL(10,2) NOT NULL,
            status      VARCHAR(20) NOT NULL,
            INDEX (customer_id)
        )""")

    customers = [(str(uuid.uuid4()), n, c) for n, c in [
        ("Ada Lovelace", "London"), ("Alan Turing", "Manchester"),
        ("Grace Hopper", "New York"), ("Edsger Dijkstra", "Austin"),
    ]]
    cur.executemany("INSERT IGNORE INTO customers VALUES (%s,%s,%s)", customers)

    orders = []
    for cust in customers:
        for i in range(3):
            orders.append((str(uuid.uuid4()), cust[0], 19.99 + i, "PLACED"))
    cur.executemany("INSERT IGNORE INTO orders VALUES (%s,%s,%s,%s)", orders)

    cur.execute("SELECT COUNT(*) FROM customers")
    nc = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM orders")
    no = cur.fetchone()[0]
    print(f"SOURCE seeded: {nc} customers, {no} orders")
    print("RPO marker — record these counts; the target must match after migration.")
    conn.close()


if __name__ == "__main__":
    main()
