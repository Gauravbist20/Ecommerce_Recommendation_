
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "ecommerce.db"

DATA_DIR.mkdir(exist_ok=True)


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_database():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            rating REAL NOT NULL,
            UNIQUE(user_id, product_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM products")

    if cursor.fetchone()[0] == 0:
        products = [
            (1, "Gaming Laptop", "Electronics", 65000, "High performance gaming laptop with fast processor"),
            (2, "Smartphone", "Electronics", 25000, "Android smartphone with excellent camera"),
            (3, "Wireless Headphones", "Electronics", 2500, "Bluetooth headphones with clear sound"),
            (4, "Running Shoes", "Fashion", 1800, "Comfortable sports running shoes"),
            (5, "Casual T Shirt", "Fashion", 700, "Cotton casual clothing for everyday use"),
            (6, "Smart Watch", "Electronics", 3500, "Fitness tracking smart watch"),
            (7, "Programming Book", "Books", 500, "Learn Python programming"),
            (8, "Data Science Book", "Books", 800, "Machine learning and data science guide"),
            (9, "Office Chair", "Furniture", 5500, "Comfortable ergonomic office chair"),
            (10, "Study Table", "Furniture", 4000, "Wooden study table for home and office")
        ]

        cursor.executemany(
            "INSERT INTO products VALUES (?, ?, ?, ?, ?)",
            products
        )

    conn.commit()
    conn.close()


def get_products():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY id")
    products = cursor.fetchall()
    conn.close()
    return products


def create_user(name, email, password):
    conn = connect()

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user_by_email(email):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, email, password FROM users WHERE email = ?",
        (email,)
    )

    user = cursor.fetchone()
    conn.close()
    return user


def add_rating(user_id, product_id, rating):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ratings (user_id, product_id, rating)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, product_id)
        DO UPDATE SET rating = excluded.rating
    """, (user_id, product_id, rating))

    conn.commit()
    conn.close()


def get_ratings():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, product_id, rating FROM ratings")
    ratings = cursor.fetchall()
    conn.close()
    return ratings
