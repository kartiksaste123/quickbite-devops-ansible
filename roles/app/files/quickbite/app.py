"""QuickBite - small food delivery order API used for the DevOps assignment."""
import os
import socket
from datetime import datetime

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

MENU = [
    ("Spice Garden", "Paneer Butter Masala", 220),
    ("Spice Garden", "Butter Naan", 40),
    ("Pune Biryani House", "Chicken Biryani", 260),
    ("Pune Biryani House", "Veg Biryani", 190),
    ("Daily Dosa", "Masala Dosa", 90),
]


def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "quickbite_db"),
        user=os.getenv("DB_USER", "quickbite"),
        password=os.getenv("DB_PASSWORD", ""),
        connect_timeout=3,
    )


def init_db():
    conn = get_db()
    with conn, conn.cursor() as cur:
        cur.execute("""CREATE TABLE IF NOT EXISTS menu_items (
                         id SERIAL PRIMARY KEY, restaurant TEXT, item TEXT, price INT)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS orders (
                         id SERIAL PRIMARY KEY, customer TEXT, item_id INT REFERENCES menu_items(id),
                         qty INT, status TEXT DEFAULT 'PLACED', created_at TIMESTAMP DEFAULT now())""")
        cur.execute("SELECT count(*) FROM menu_items")
        if cur.fetchone()[0] == 0:
            cur.executemany("INSERT INTO menu_items (restaurant, item, price) VALUES (%s, %s, %s)", MENU)
    conn.close()


@app.route("/")
def index():
    return jsonify(app="QuickBite Food Delivery API", env=os.getenv("APP_ENV", "dev"),
                   served_by=socket.gethostname())


@app.route("/health")
def health():
    try:
        conn = get_db()
        conn.close()
        db = "up"
    except Exception:
        db = "down"
    code = 200 if db == "up" else 503
    return jsonify(status="ok" if code == 200 else "error", database=db,
                   time=datetime.now().isoformat(timespec="seconds")), code


@app.route("/api/menu")
def menu():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id, restaurant, item, price FROM menu_items ORDER BY id")
        rows = cur.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "restaurant": r[1], "item": r[2], "price": r[3]} for r in rows])


@app.route("/api/orders", methods=["GET", "POST"])
def orders():
    conn = get_db()
    if request.method == "POST":
        data = request.get_json(force=True)
        with conn, conn.cursor() as cur:
            cur.execute("INSERT INTO orders (customer, item_id, qty) VALUES (%s, %s, %s) RETURNING id",
                        (data["customer"], data["item_id"], data.get("qty", 1)))
            order_id = cur.fetchone()[0]
        conn.close()
        return jsonify(order_id=order_id, status="PLACED"), 201

    with conn.cursor() as cur:
        cur.execute("""SELECT o.id, o.customer, m.item, o.qty, o.status FROM orders o
                       JOIN menu_items m ON m.id = o.item_id ORDER BY o.id""")
        rows = cur.fetchall()
    conn.close()
    return jsonify([{"order_id": r[0], "customer": r[1], "item": r[2], "qty": r[3], "status": r[4]}
                    for r in rows])


# create tables when gunicorn loads the app (skipped in unit tests)
if os.getenv("DB_HOST"):
    try:
        init_db()
    except Exception as e:
        print("DB init failed:", e)
