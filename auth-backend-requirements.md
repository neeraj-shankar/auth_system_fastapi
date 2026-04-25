# Authentication Backend — Requirements Document
**Version:** 1.0  
**Status:** Draft  
**Audience:** Self-learning / Personal Project  

---

## 1. Project Overview

Build a RESTful authentication backend that handles user registration, login, session management, and basic access control. The goal is to understand how authentication works from the ground up — no magic, no black boxes.

---

## 2. Goals

- Understand the full auth lifecycle: register → login → access → logout
- Learn how passwords are securely stored (hashing)
- Learn how sessions/tokens work (JWT)
- Build each layer independently before wiring them together
- Keep the codebase simple and readable

---

## 3. Tech Stack (Suggested)

| Layer        | Choice              | Why                                      |
|--------------|---------------------|------------------------------------------|
| Language     | Python | Widely used, easy to read                |
| Framework    | Flask               | Minimal, unopinionated                   |
| Database     | PostgreSQL          | Standard relational DB                   |
| ORM          | Prisma              | Simple schema-first, great for learning  |
| Auth         | JWT (jsonwebtoken)  | Industry standard, stateless             |
| Hashing      | bcrypt              | Standard password hashing                |
| Validation   | Zod                 | Clean input validation                   |
| Environment  | dotenv              | Manage secrets/config                    |

> You can swap any of these. The concepts remain the same.

---

## 4. Core Features (MVP)

### 4.1 User Registration
- Accept `email` and `password` from the client
- Validate that email is a valid format
- Validate that password meets minimum requirements (min 8 chars)
- Check if email already exists in the database
- Hash the password before storing
- Save the user to the database
- Return a success response (do **not** return the password)

### 4.2 User Login
- Accept `email` and `password`
- Find the user by email in the database
- Compare the submitted password with the stored hash
- If valid, generate a JWT access token
- Return the token to the client

### 4.3 Protected Route (Auth Middleware)
- A sample protected endpoint (e.g., `GET /me`)
- Middleware reads the JWT from the `Authorization` header
- Verifies the token signature and expiry
- Attaches the decoded user info to the request
- If token is invalid or missing → return `401 Unauthorized`

### 4.4 Logout
- For JWT (stateless): logout is handled client-side by discarding the token
- Optional server-side: maintain a token blocklist in-memory or in DB

---

## 5. API Endpoints

| Method | Endpoint        | Auth Required | Description              |
|--------|-----------------|---------------|--------------------------|
| POST   | /auth/register  | No            | Register a new user      |
| POST   | /auth/login     | No            | Login and receive token  |
| GET    | /auth/me        | Yes           | Get current user profile |
| POST   | /auth/logout    | Yes           | Logout (invalidate token)|

---

## 6. Data Model

### User Table

| Field        | Type      | Notes                          |
|--------------|-----------|--------------------------------|
| id           | UUID      | Primary key, auto-generated    |
| email        | String    | Unique, lowercase              |
| password     | String    | Hashed (never plain text)      |
| created_at   | Timestamp | Auto-set on insert             |
| updated_at   | Timestamp | Auto-updated on change         |

---

## 7. Security Requirements

- **Never store plain text passwords** — always hash with bcrypt (salt rounds ≥ 10)
- **JWT secrets** must live in environment variables, never in code
- **Token expiry** — access tokens should expire (e.g., 15 minutes to 1 hour)
- **Input validation** — always validate and sanitize incoming request data
- **Error messages** — do not reveal whether an email exists during login failures (return generic "Invalid credentials")
- **HTTPS** — assumed in production (out of scope for local dev)

---

## 8. Error Handling

All error responses should follow a consistent shape:

```json
{
  "status": "error",
  "message": "A human-readable description",
  "code": 400
}
```

| Scenario                    | HTTP Status |
|-----------------------------|-------------|
| Validation failure          | 400         |
| Email already registered    | 409         |
| Invalid credentials         | 401         |
| Missing / invalid token     | 401         |
| Resource not found          | 404         |
| Server error                | 500         |

---

## 9. Project Structure (Recommended)

```
src/
├── routes/
│   └── auth.routes.ts        # Route definitions
├── controllers/
│   └── auth.controller.ts    # Request/response logic
├── services/
│   └── auth.service.ts       # Business logic (hashing, token gen)
├── middleware/
│   └── auth.middleware.ts    # JWT verification
├── validators/
│   └── auth.validator.ts     # Zod schemas for input validation
├── prisma/
│   └── schema.prisma         # Database schema
├── config/
│   └── env.ts                # Environment variable loader
└── app.ts                    # Express app setup
```

---

## 10. Build Layers (Learning Roadmap)

Build in this order — each layer is testable on its own:

| Layer | What You Build                             | What You Learn                       |
|-------|--------------------------------------------|--------------------------------------|
| 1     | Project setup, Express server, health check | Node/Express basics, env config      |
| 2     | Database + Prisma schema                    | DB setup, migrations, ORM basics     |
| 3     | Register endpoint                           | Hashing, validation, DB writes       |
| 4     | Login endpoint                              | Password comparison, JWT generation  |
| 5     | Auth middleware + `/me` route               | Token verification, protected routes |
| 6     | Error handling + cleanup                    | Consistent responses, edge cases     |
| 7     | (Optional) Refresh tokens                   | Token rotation, security depth       |

---

## 11. Out of Scope (for now)

- OAuth / Social login (Google, GitHub)
- Email verification
- Password reset flow
- Rate limiting / brute force protection
- Role-based access control (RBAC)
- Refresh token rotation

> These are great **Layer 2** additions once the core is solid.

---

## 12. Definition of Done

The MVP is complete when:

- [ ] A new user can register with email + password
- [ ] A registered user can log in and receive a JWT
- [ ] A protected route returns user data when a valid token is provided
- [ ] Invalid or missing tokens are rejected with a 401
- [ ] Passwords are never stored or returned in plain text
- [ ] All endpoints return consistent JSON responses

---

*This document is a living guide. Update it as you progress through each layer.*
