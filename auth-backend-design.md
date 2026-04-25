# Authentication Backend — Design Document
**Version:** 1.0  
**Stack:** Python · FastAPI · PostgreSQL · SQLAlchemy · JWT  
**Status:** Draft  

---

## 1. Architecture Overview

This service follows a **Layered Architecture** pattern. Each layer has a single responsibility and only talks to the layer directly below it.

```
┌──────────────────────────────────────────────┐
│                   CLIENT                     │
└───────────────────┬──────────────────────────┘
                    │ HTTP Request
┌───────────────────▼──────────────────────────┐
│               ROUTES  (routers/)             │  ← Defines URL paths, HTTP methods
└───────────────────┬──────────────────────────┘
                    │
┌───────────────────▼──────────────────────────┐
│           MIDDLEWARE  (middleware/)           │  ← JWT verification on protected routes
└───────────────────┬──────────────────────────┘
                    │
┌───────────────────▼──────────────────────────┐
│          CONTROLLERS  (api/v1/)              │  ← Handles request/response, calls service
└───────────────────┬──────────────────────────┘
                    │
┌───────────────────▼──────────────────────────┐
│            SERVICES  (services/)             │  ← Business logic: hash, compare, tokenize
└───────────────────┬──────────────────────────┘
                    │
┌───────────────────▼──────────────────────────┐
│          REPOSITORIES  (repositories/)       │  ← All DB queries live here
└───────────────────┬──────────────────────────┘
                    │
┌───────────────────▼──────────────────────────┐
│            DATABASE  (PostgreSQL)            │  ← Persistent storage
└──────────────────────────────────────────────┘
```

> **Rule:** A layer can only call the layer directly below it.  
> A Controller never queries the DB directly. A Service never touches HTTP request objects.

---

## 2. Project Structure

```
app/
├── main.py                     # FastAPI app instance, router registration
├── config.py                   # Settings loaded from .env (pydantic BaseSettings)
├── database.py                 # SQLAlchemy engine, session factory
│
├── models/                     # SQLAlchemy ORM models (DB table definitions)
│   └── user.py
│
├── schemas/                    # Pydantic schemas (request bodies & response shapes)
│   └── auth.py
│
├── repositories/               # DB query functions only — no business logic
│   └── user_repository.py
│
├── services/                   # Business logic — hashing, token generation, etc.
│   └── auth_service.py
│
├── api/
│   └── v1/
│       └── auth.py             # Route handlers (controllers)
│
├── middleware/
│   └── auth_middleware.py      # JWT verification dependency
│
└── exceptions/
    └── handlers.py             # Global exception → HTTP response mapping
```

---

## 3. Database Design

### 3.1 Table: `users`

| Column       | Type                     | Constraints                     |
|--------------|--------------------------|---------------------------------|
| id           | UUID                     | PK, default: uuid_generate_v4() |
| email        | VARCHAR(255)             | UNIQUE, NOT NULL                |
| hashed_password | TEXT                  | NOT NULL                        |
| is_active    | BOOLEAN                  | DEFAULT TRUE                    |
| created_at   | TIMESTAMP WITH TIME ZONE | DEFAULT NOW()                   |
| updated_at   | TIMESTAMP WITH TIME ZONE | DEFAULT NOW(), auto-update      |

> **Note:** The column is named `hashed_password`, not `password`.  
> This is intentional — it reminds every developer that what's stored is never plain text.

### 3.2 SQLAlchemy Model (Sketch)

```python
class User(Base):
    __tablename__ = "users"

    id           = Column(UUID, primary_key=True, default=uuid4)
    email        = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(Text, nullable=False)
    is_active    = Column(Boolean, default=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    updated_at   = Column(DateTime(timezone=True), onupdate=func.now())
```

---

## 4. Pydantic Schemas (Contracts)

These define the "contracts" between your API and the outside world.

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│   RegisterRequest   │     │    LoginRequest       │     │   TokenResponse      │
│─────────────────────│     │──────────────────────│     │─────────────────────│
│ email: EmailStr     │     │ email: EmailStr       │     │ access_token: str    │
│ password: str       │     │ password: str         │     │ token_type: str      │
│   (min 8 chars)     │     │                       │     │   ("bearer")         │
└─────────────────────┘     └──────────────────────┘     └─────────────────────┘

┌─────────────────────┐     ┌──────────────────────┐
│   UserResponse      │     │   ErrorResponse       │
│─────────────────────│     │──────────────────────│
│ id: UUID            │     │ detail: str           │
│ email: str          │     │                       │
│ is_active: bool     │     │ (FastAPI default)     │
│ created_at: datetime│     │                       │
│                     │     │                       │
│ ❌ NO password field │     │                       │
└─────────────────────┘     └──────────────────────┘
```

---

## 5. API Endpoint Design

### POST `/api/v1/auth/register`

**Purpose:** Create a new user account.

| | |
|---|---|
| **Auth required** | No |
| **Request body** | `RegisterRequest` |
| **Success response** | `201 Created` → `UserResponse` |

**Flow:**
1. Validate request body (Pydantic does this automatically)
2. Check if email already exists → `409 Conflict` if so
3. Hash the password using bcrypt
4. Insert user into DB
5. Return `UserResponse` (no password)

**Error cases:**

| Condition | HTTP Code | Message |
|---|---|---|
| Invalid email format | 422 | (Pydantic auto-handles) |
| Password < 8 chars | 422 | (Pydantic auto-handles) |
| Email already exists | 409 | "Email already registered" |
| DB failure | 500 | "Internal server error" |

---

### POST `/api/v1/auth/login`

**Purpose:** Authenticate a user and issue a JWT.

| | |
|---|---|
| **Auth required** | No |
| **Request body** | `LoginRequest` |
| **Success response** | `200 OK` → `TokenResponse` |

**Flow:**
1. Look up user by email
2. If user not found → `401` (generic message — don't reveal email existence)
3. Compare submitted password against `hashed_password` using bcrypt
4. If mismatch → `401`
5. Generate JWT with payload: `{ sub: user_id, exp: now + 60min }`
6. Return `TokenResponse`

**Error cases:**

| Condition | HTTP Code | Message |
|---|---|---|
| User not found | 401 | "Invalid credentials" |
| Wrong password | 401 | "Invalid credentials" |

> **Security note:** Both "user not found" and "wrong password" return the *same* message and *same* HTTP code. This prevents attackers from using login errors to enumerate valid emails.

---

### GET `/api/v1/auth/me`

**Purpose:** Return the currently authenticated user's profile.

| | |
|---|---|
| **Auth required** | Yes (Bearer token) |
| **Request body** | None |
| **Success response** | `200 OK` → `UserResponse` |

**Flow:**
1. Middleware extracts token from `Authorization: Bearer <token>` header
2. Verifies signature and expiry
3. Decodes `sub` (user_id) from payload
4. Fetches user from DB by id
5. Returns `UserResponse`

**Error cases:**

| Condition | HTTP Code | Message |
|---|---|---|
| Missing header | 401 | "Not authenticated" |
| Malformed token | 401 | "Invalid token" |
| Token expired | 401 | "Token has expired" |
| User not found in DB | 404 | "User not found" |

---

### POST `/api/v1/auth/logout`

**Purpose:** Logout the current user.

| | |
|---|---|
| **Auth required** | Yes |
| **Success response** | `200 OK` → `{ "message": "Logged out successfully" }` |

> **Design decision:** JWTs are stateless — the server has no session to destroy. For MVP, logout is  
> acknowledged on the server and the client is responsible for discarding the token.  
> A token blocklist can be added in a later layer.

---

## 6. Authentication Middleware Design

The middleware is implemented as a **FastAPI Dependency** (not a true middleware class). This is the idiomatic FastAPI approach.

```
Request arrives at protected route
         │
         ▼
get_current_user(token: str = Depends(oauth2_scheme))
         │
         ├─ Extract Bearer token from Authorization header
         │
         ├─ Decode JWT → verify signature + expiry
         │         └─ on failure → raise HTTPException(401)
         │
         ├─ Read `sub` (user_id) from token payload
         │
         ├─ Fetch user from DB by user_id
         │         └─ not found → raise HTTPException(404)
         │
         └─ Return User object → injected into route handler
```

**Usage in a route:**
```python
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

---

## 7. Security Design

| Concern | Approach |
|---|---|
| Password storage | bcrypt with cost factor 12 |
| Token type | JWT (HS256 signing algorithm) |
| Token expiry | 60 minutes (configurable via env) |
| Secret storage | Environment variables only (never in code) |
| Login error messages | Always generic — never reveal email existence |
| Input validation | Pydantic schemas on all request bodies |
| SQL injection | Prevented by SQLAlchemy ORM parameterized queries |

---

## 8. Environment Configuration

All secrets and environment-specific values live in `.env`. Never commit this file.

```
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/auth_db
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Loaded in `config.py` via **Pydantic BaseSettings**:

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 9. Data Flow Diagrams

### Registration Flow

```
Client
  │  POST /register { email, password }
  ▼
Router → auth.py
  │
  ▼
Controller (register handler)
  │  calls
  ▼
AuthService.register(email, password)
  │  1. user_repo.find_by_email(email)  ──→ Repository ──→ DB
  │     └─ exists? raise 409
  │  2. bcrypt.hash(password)
  │  3. user_repo.create(email, hashed_pw) ──→ Repository ──→ DB
  │
  ▼
Controller returns UserResponse (201)
  │
  ▼
Client receives { id, email, is_active, created_at }
```

### Login Flow

```
Client
  │  POST /login { email, password }
  ▼
Controller (login handler)
  │  calls
  ▼
AuthService.login(email, password)
  │  1. user_repo.find_by_email(email)  ──→ Repository ──→ DB
  │     └─ not found? raise 401 "Invalid credentials"
  │  2. bcrypt.verify(password, user.hashed_password)
  │     └─ mismatch? raise 401 "Invalid credentials"
  │  3. create_access_token({ sub: user.id, exp: now+60min })
  │
  ▼
Controller returns TokenResponse (200)
  │
  ▼
Client receives { access_token, token_type: "bearer" }
```

---

## 10. Key Design Decisions & Rationale

| Decision | Why |
|---|---|
| Layered architecture | Each layer is testable in isolation. Easy to reason about. |
| Repository pattern | DB queries are centralized. Swap PostgreSQL for SQLite in tests without changing service logic. |
| FastAPI Depends for auth | Idiomatic FastAPI. Cleaner than middleware class for route-level auth. |
| Pydantic BaseSettings for config | Type-safe config. Fails loudly at startup if env vars are missing. |
| UUID as primary key | Harder to enumerate than integer IDs. No information leakage. |
| Versioned API path (`/api/v1/`) | Prepares for future breaking changes without disrupting existing clients. |

---

## 11. What This Design Does NOT Include (Yet)

| Feature | When to add |
|---|---|
| Refresh tokens | After core auth is solid (Layer 7) |
| Token blocklist (true logout) | After refresh tokens |
| Email verification | Layer 2 of the project |
| Rate limiting | Before any production deployment |
| RBAC (roles/permissions) | When multiple user types are needed |

---

*This design document is the blueprint. Any code written should be traceable back to a decision made here.*
