"""Tests for database module."""
import pytest
import os
import tempfile
from datetime import datetime, timedelta

# Set test database path before importing config
TEST_DB = tempfile.mktemp(suffix='.db')

import config
config.DB_PATH = TEST_DB


def test_add_and_get_coupon():
    """Test adding and retrieving a coupon."""
    from database import init_db, add_coupon, get_coupon_by_brand

    init_db()

    # Add a coupon
    coupon_id = add_coupon("Nike", "NIKE20", "20% off", None)
    assert coupon_id > 0

    # Get coupon by brand
    coupon = get_coupon_by_brand("Nike")
    assert coupon is not None
    assert coupon['brand'] == "Nike"
    assert coupon['code'] == "NIKE20"
    assert coupon['is_active'] == 1


def test_get_coupon_case_insensitive():
    """Test brand lookup is case insensitive."""
    from database import init_db, add_coupon, get_coupon_by_brand

    init_db()
    add_coupon("Nike", "NIKE10", "10% off")

    coupon = get_coupon_by_brand("nike")
    assert coupon is not None
    assert coupon['code'] == "NIKE10"


def test_coupon_not_found():
    """Test getting non-existent coupon returns None."""
    from database import init_db, get_coupon_by_brand

    init_db()

    coupon = get_coupon_by_brand("NonExistent")
    assert coupon is None


def test_deactivate_coupon():
    """Test deactivating a coupon."""
    from database import init_db, add_coupon, get_coupon_by_brand, deactivate_coupon

    init_db()

    coupon_id = add_coupon("Adidas", "ADIDAS15", "15% off")
    deactivated = deactivate_coupon(coupon_id)
    assert deactivated is True

    coupon = get_coupon_by_brand("Adidas")
    assert coupon is None


def test_increment_used_count():
    """Test incrementing used count."""
    from database import init_db, add_coupon, get_coupon_by_brand, increment_used_count

    init_db()

    coupon_id = add_coupon("Puma", "PUMA25", "25% off")
    coupon = get_coupon_by_brand("Puma")
    assert coupon['used_count'] == 0

    increment_used_count(coupon_id)
    coupon = get_coupon_by_brand("Puma")
    assert coupon['used_count'] == 1


def test_add_user():
    """Test adding a user."""
    from database import init_db, add_user, get_user

    init_db()

    user_id = add_user(123456, "testuser")
    assert user_id > 0

    user = get_user(123456)
    assert user is not None
    assert user['telegram_id'] == 123456
    assert user['username'] == "testuser"
    assert user['is_admin'] == 0


def test_get_all_coupons():
    """Test getting all coupons."""
    from database import init_db, add_coupon, get_all_coupons

    init_db()

    add_coupon("Nike", "NIKE20")
    add_coupon("Adidas", "ADIDAS15")

    coupons = get_all_coupons()
    assert len(coupons) == 2
    brands = [c['brand'] for c in coupons]
    assert "Nike" in brands
    assert "Adidas" in brands


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test database after each test."""
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
