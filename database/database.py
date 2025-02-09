import sqlite3
from config import DB_PATH
import aiosqlite
import datetime
import asyncio
import motor.motor_asyncio

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS approved_users (user_id INTEGER PRIMARY KEY)")
    cursor.execute("CREATE TABLE IF NOT EXISTS user_violations (user_id INTEGER, category TEXT, count INTEGER, PRIMARY KEY(user_id, category))")
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()

def is_approved(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM approved_users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def update_violations(user_id, category):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_violations (user_id, category, count) VALUES (?, ?, 1) ON CONFLICT(user_id, category) DO UPDATE SET count = count + 1", (user_id, category))
    conn.commit()
    conn.close()

def add_approved_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO approved_users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def remove_approved_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM approved_users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_user_violations(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT category, count FROM user_violations WHERE user_id = ?", (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM approved_users")
    result = cursor.fetchall()
    conn.close()
    return [user[0] for user in result]




class Database:
    """SQLite3 database handler for managing Telegram bot users & groups."""

    def __init__(self, db_path="users.db"):
        self.db_path = db_path

    async def init_db(self):
        """Initialize the database and ensure all necessary columns exist."""
        async with aiosqlite.connect(self.db_path) as db:
            # ✅ Create users table with started_bot column
            await db.execute(
                """CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    started_bot INTEGER DEFAULT 0
                )"""
            )

            # ✅ Ensure `started_bot` column exists (for old databases)
            try:
                await db.execute("SELECT started_bot FROM users LIMIT 1")
            except aiosqlite.OperationalError:
                print("🛠 Adding missing 'started_bot' column to users table...")
                await db.execute("ALTER TABLE users ADD COLUMN started_bot INTEGER DEFAULT 0")

            # ✅ Create groups table
            await db.execute(
                """CREATE TABLE IF NOT EXISTS groups (
                    id INTEGER PRIMARY KEY,
                    title TEXT
                )"""
            )

            await db.commit()

    async def add_user(self, user_id: int, username: str = None):
        """Add a user when they interact with the bot (avoid duplicates)."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)",
                (user_id, username),
            )
            await db.commit()

    async def mark_user_started(self, user_id: int):
        """Mark a user as having started the bot."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET started_bot = 1 WHERE id = ?",
                (user_id,),
            )
            await db.commit()

    async def add_group(self, group_id: int, title: str):
        """Add a new group when a message is sent there (avoiding duplicates)."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO groups (id, title) VALUES (?, ?)",
                (group_id, title),
            )
            await db.commit()

    async def get_all_users(self) -> list[int]:
        """Get all user IDs stored in the database."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT id FROM users")
            users = await cursor.fetchall()
            return [row[0] for row in users] if users else []

    async def get_users_who_started(self) -> list[int]:
        """Get all users who have started the bot."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT id FROM users WHERE started_bot = 1")
            users = await cursor.fetchall()
            return [row[0] for row in users] if users else []

    async def get_all_groups(self) -> list[int]:
        """Get all stored group IDs."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT id FROM groups")
            groups = await cursor.fetchall()
            return [row[0] for row in groups] if groups else []

    async def delete_user(self, user_id: int):
        """Delete a user from the database."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM users WHERE id = ?", (user_id,))
            await db.commit()

    async def get_all_notif_user(self) -> list[int]:
        """Retrieve all user IDs who have started the bot."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT id FROM users WHERE started_bot = 1")
            users = await cursor.fetchall()
            return [row[0] for row in users] if users else []

    async def get_total_counts(self) -> dict:
        """Get the total count of users and groups in the database."""
        async with aiosqlite.connect(self.db_path) as db:
            user_cursor = await db.execute("SELECT COUNT(*) FROM users")
            total_users = (await user_cursor.fetchone())[0]

            group_cursor = await db.execute("SELECT COUNT(*) FROM groups")
            total_groups = (await group_cursor.fetchone())[0]

        return {"users": total_users, "groups": total_groups}

