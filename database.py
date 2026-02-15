"""Database operations for ProCoupon bot."""
import sqlite3
from datetime import datetime
from typing import Optional
from contextlib import contextmanager

from config import DB_PATH


@contextmanager
def get_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Initialize database tables."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Create coupons table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coupons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                code TEXT NOT NULL,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT,
                used_count INTEGER DEFAULT 0,
                last_validated_at TEXT
            )
        """)

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                is_admin INTEGER DEFAULT 0
            )
        """)


def add_coupon(brand: str, code: str, description: str = None, expires_at: str = None) -> int:
    """Add a new coupon to the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO coupons (brand, code, description, expires_at) VALUES (?, ?, ?, ?)",
            (brand, code, description, expires_at)
        )
        return cursor.lastrowid


def get_coupon_by_brand(brand: str) -> Optional[dict]:
    """Get an active coupon by brand name."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM coupons
               WHERE LOWER(brand) = LOWER(?) AND is_active = 1
               ORDER BY used_count ASC, created_at DESC LIMIT 1""",
            (brand,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def _is_coupon_valid(coupon: dict) -> bool:
    """Check if a coupon is valid (active and not expired)."""
    if not coupon.get('is_active'):
        return False

    expires_at = coupon.get('expires_at')
    if expires_at:
        try:
            expiry = datetime.fromisoformat(expires_at)
            if datetime.now() > expiry:
                return False
        except (ValueError, TypeError):
            pass

    return True


def get_valid_coupon_by_brand(brand: str) -> Optional[dict]:
    """
    Get a valid coupon by brand with daily validation caching.

    Returns a coupon only if:
    1. It exists and is active
    2. It has not expired
    3. It was validated today (or needs validation now)

    The validation result is cached for the day.
    """
    coupon = get_coupon_by_brand(brand)
    if not coupon:
        return None

    today = datetime.now().date().isoformat()
    last_validated = coupon.get('last_validated_at')

    # If already validated today, return cached result
    if last_validated == today:
        # Check cached validity status from is_active
        if coupon.get('is_active'):
            return coupon
        return None

    # Not validated today, check validity now
    if _is_coupon_valid(coupon):
        # Update validation timestamp
        update_last_validated(coupon['id'])
        return coupon

    return None


def get_all_coupons() -> list:
    """Get all coupons."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM coupons ORDER BY brand, created_at DESC")
        return [dict(row) for row in cursor.fetchall()]


def deactivate_coupon(coupon_id: int) -> bool:
    """Deactivate a coupon by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE coupons SET is_active = 0 WHERE id = ?", (coupon_id,))
        return cursor.rowcount > 0


def increment_used_count(coupon_id: int):
    """Increment the used count for a coupon."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE coupons SET used_count = used_count + 1 WHERE id = ?", (coupon_id,))


def update_last_validated(coupon_id: int):
    """Update the last validated timestamp for a coupon to today."""
    today = datetime.now().date().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE coupons SET last_validated_at = ? WHERE id = ?",
            (today, coupon_id)
        )


def add_user(telegram_id: int, username: str = None) -> int:
    """Add a new user to the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?)",
            (telegram_id, username)
        )
        cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
        return cursor.fetchone()[0]


def get_user(telegram_id: int) -> Optional[dict]:
    """Get a user by Telegram ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
