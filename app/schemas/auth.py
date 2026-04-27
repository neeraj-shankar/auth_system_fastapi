from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime

# ── Request Schemas (what comes IN from the client) ───────────────────────────

class RegisterRequest(BaseModel):
    """Validated shape of a registration request body.
 
    Pydantic runs these validations automatically before your route
    handler is even called. If anything is wrong, FastAPI returns
    a 422 with a clear error message — you write zero validation code.
    """

    email: EmailStr
    password: str 

    @field_validator(password)
    @classmethod
    def password_strength(cls, v: str)-> str:
        """
        Custom validator — runs after type checking.
        Raise ValueError to trigger a 422 with your message.
        """

        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        
class LoginRequest(BaseModel):
    """Used in Layer 4. Defined here to keep all auth schemas together."""
    email: EmailStr
    password: str


# ── Response Schemas (what goes OUT to the client) ────────────────────────────

class UserResponse(BaseModel):
    """
    The ONLY shape a User is ever returned to a client.
 
    Notice: no `hashed_password` field.
    This is not accidental — it's the guarantee.
    Even if your service accidentally passes a full User ORM object,
    Pydantic will only serialize the fields declared here.
 
    `from_attributes=True` tells Pydantic it can read from SQLAlchemy
    ORM objects (not just plain dicts). Without this, you'd have to
    manually convert every User model to a dict before returning it.
    """

    id: str
    email: str 
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Used in Layer 4. Defined here to keep all auth schemas together."""

    access_token: str 
    token_type: str = "bearer"




