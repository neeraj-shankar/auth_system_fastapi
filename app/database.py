from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

# ── Engine ────────────────────────────────────────────────────────────────────
#
# The engine is the single connection to your database.
# It manages a "connection pool" — a set of reusable DB connections
# so you're not opening/closing a new connection on every request.
#
# `pool_pre_ping=True` means SQLAlchemy will verify a connection is still
# alive before handing it to you. Prevents "stale connection" errors after
# DB restarts or network hiccups.
#
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)

# ── Session Factory ───────────────────────────────────────────────────────────
#
# SessionLocal is a CLASS (a factory), not a session instance.
# Every time you call SessionLocal(), you get a fresh session object.
#
# autocommit=False → You manually control when to commit.
#                    This is what you want — don't let changes save silently.
# autoflush=False  → Don't auto-sync pending changes to DB before each query.
#                    Gives you explicit control.
#

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

# ── Declarative Base ──────────────────────────────────────────────────────────
#
# Every ORM model you create will inherit from this Base class.
# SQLAlchemy uses it to keep a registry of all your models,
# which Alembic reads to generate migrations.
#
# There is ONE Base for the whole app — imported everywhere models are defined.
#
class Base(DeclarativeBase):
    pass

# ── DB Dependency ─────────────────────────────────────────────────────────────
#
# This is a FastAPI "dependency" — a function injected into route handlers.
# It follows the "context manager" pattern:
#   1. Open a session (yield db)
#   2. Route handler runs and uses db
#   3. Finally block always runs — closes session even if an exception occurred
#
# Usage in a route:
#   def my_route(db: Session = Depends(get_db)):
#       users = db.query(User).all()
#

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
