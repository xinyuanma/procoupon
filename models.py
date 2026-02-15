"""Data models for ProCoupon bot."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Coupon:
    """Coupon data model."""
    id: int
    brand: str
    code: str
    description: Optional[str]
    is_active: bool
    created_at: str
    expires_at: Optional[str]
    used_count: int

    @classmethod
    def from_dict(cls, data: dict) -> 'Coupon':
        """Create Coupon from dictionary."""
        return cls(
            id=data['id'],
            brand=data['brand'],
            code=data['code'],
            description=data.get('description'),
            is_active=bool(data['is_active']),
            created_at=data['created_at'],
            expires_at=data.get('expires_at'),
            used_count=data.get('used_count', 0)
        )

    def is_expired(self) -> bool:
        """Check if the coupon is expired."""
        if not self.expires_at:
            return False
        try:
            expiry = datetime.fromisoformat(self.expires_at)
            return datetime.now() > expiry
        except (ValueError, TypeError):
            return False


@dataclass
class User:
    """User data model."""
    id: int
    telegram_id: int
    username: Optional[str]
    created_at: str
    is_admin: bool

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create User from dictionary."""
        return cls(
            id=data['id'],
            telegram_id=data['telegram_id'],
            username=data.get('username'),
            created_at=data['created_at'],
            is_admin=bool(data['is_admin'])
        )
