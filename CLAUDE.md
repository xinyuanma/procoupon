# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Telegram bot for collecting and dispensing coupon codes. Users request coupon codes via Telegram commands, and admins can manage (CRUD) coupons through the bot.

**Tech Stack**: Python, python-telegram-bot, SQLite

## Commands

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py

# Run tests
pytest
```

## Architecture

```
├── main.py              # Bot entry point, handlers
├── database.py          # SQLite operations (coupons, users)
├── models.py            # Data models (Coupon, User)
├── config.py            # Configuration (tokens, DB path)
└── tests/
```

## Database Schema

**coupons table**: id, brand, code, description, is_active, created_at, expires_at, used_count
**users table**: id, telegram_id, username, created_at, is_admin

## Development Phases

| Phase | Focus | Key Features |
|-------|-------|---------------|
| Sprint 1 | Bot MVP + Simple API | `/nike` returns coupon code |
| Sprint 2 | Database + CRUD | Manual entry, validity tracking |
| Sprint 3 | Deployment | 24/7 runtime |
| Sprint 4 | UX Improvements | Command list, help text |

## Telegram Bot Commands

**User-facing** (to implement):
- `/brand` - Get coupon for specific brand
- `/list` - Show available brands
- `/help` - Show help text

**Admin-facing** (to implement):
- `/addcoupon <brand> <code>` - Add new coupon
- `/deactivate <id>` - Disable a coupon
- `/stats` - Show usage statistics

## Implementation Order

1. Create config.py with bot token and DB path
2. Set up SQLite database with coupons/users tables
3. Implement Coupon model with CRUD methods
4. Build basic bot handlers (start, help)
5. Implement coupon lookup by brand
6. Add admin commands for coupon management
7. Add validity checking (expired, depleted)
