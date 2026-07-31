"""Simple peewee-based DB models for Trading-AI.
This module provides a lightweight SQLite-backed ORM using peewee (already in requirements).
It defines User, Portfolio, Watchlist models and helper init function.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from peewee import SqliteDatabase, Model, CharField, TextField, DateTimeField, FloatField, IntegerField
import datetime

DB_PATH = Path("data") / "trading_ai.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
_db = SqliteDatabase(str(DB_PATH))

class BaseModel(Model):
    class Meta:
        database = _db

class User(BaseModel):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password_hash = CharField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)

class Portfolio(BaseModel):
    user = IntegerField()  # simple FK to User.id
    name = CharField(default='Main')
    cash = FloatField(default=100000.0)
    created_at = DateTimeField(default=datetime.datetime.utcnow)

class Watchlist(BaseModel):
    user = IntegerField()
    name = CharField(default='Default')
    symbols = TextField(default='')  # comma separated
    created_at = DateTimeField(default=datetime.datetime.utcnow)

def init_db():
    _db.connect(reuse_if_open=True)
    _db.create_tables([User, Portfolio, Watchlist])

# expose simple helpers
def get_db():
    return _db

if __name__ == '__main__':
    init_db()
    print('Initialized DB at', DB_PATH)
