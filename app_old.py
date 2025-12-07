# from flask_cors import CORS
# from flask import Flask, jsonify, request
# from flask_mysqldb import MySQL

# # entry point
# app = Flask(__name__)
# CORS(app)

# # MySQL config
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'password'
# app.config['MYSQL_DB'] = 'shop'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # so we get dicts instead of tuples

# mysql = MySQL(app)

# # routes
# @app.route("/products", methods=["GET"])
# def get_products():
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM products")
#     products = cur.fetchall()
#     cur.close()
#     return jsonify(products)  # list of dicts -> JSON


from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)


def get_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Create table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)

    # Optional: seed data if table is empty
    cur.execute("SELECT COUNT(*) AS cnt FROM products")
    if cur.fetchone()["cnt"] == 0:
        cur.executemany(
            "INSERT INTO products (name, price) VALUES (?, ?)",
            [
                ("Banana", 3.5),
                ("Apple", 2.2),
                ("Cherry", 4.8),
            ]
        )

    conn.commit()
    conn.close()


# ✅ Run init_db as soon as the module is imported
init_db()


@app.route("/products", methods=["GET"])
def get_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price FROM products")
    rows = cur.fetchall()
    conn.close()

    products = [dict(row) for row in rows]
    return jsonify(products)


@app.route("/products", methods=["POST"])
def add_product():
    data = request.get_json()
    name = data.get("name")
    price = data.get("price")

    if not name or price is None:
        return jsonify({"error": "name and price are required"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (name, price) VALUES (?, ?)",
        (name, price)
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return jsonify({"id": new_id, "name": name, "price": price}), 201


if __name__ == "__main__":
    app.run(debug=True)
