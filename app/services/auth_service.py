import bcrypt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.repositories.user_respositories import UserRespository


class AuthService:
    """
    Business logic for authentication.
 
    This layer answers the "what should happen" questions:
      - Should this registration be allowed?
      - Is this password correct?
      - What token should we issue?
 
    It delegates "how do I query the DB" to UserRepository,
    and "how do I make an HTTP response" back up to the route.
 
    The service never imports FastAPI routing things (Request, APIRouter).
    The service never writes raw SQL.
    It sits cleanly in the middle.
    """

    def __init__(self, db: Session):
        self.user_repo = UserRespository(db)

    @staticmethod
    def hash_password(plain_password: str)-> str:
        """
        Hash a plain text password using bcrypt.
 
        How bcrypt works:
          1. Generates a random "salt" (random bytes added to the password)
          2. Runs an expensive hashing algorithm (cost factor = 12 rounds)
          3. Returns a string like: $2b$12$<salt><hash>
 
        The salt is embedded IN the hash string — you don't store it separately.
        Two calls with the same password produce DIFFERENT hashes (different salts).
        This means even if two users have the same password, their stored hashes differ.
 
        Cost factor 12: takes ~250ms on modern hardware.
        That's intentional — makes brute-force attacks 250ms per attempt.
        """

        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str)-> bool:
        """
        Compare a plain password against a stored bcrypt hash.
 
        bcrypt.checkpw() extracts the salt from hashed_password,
        re-hashes the plain_password with that same salt,
        and compares the result. You never see or touch the salt directly.
 
        Returns True if they match, False otherwise.
        Never raises — always returns a boolean.
        """

        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )


    # ── Registration ──────────────────────────────────────────────────────────

    def register(self, email: str, password: str)-> User:

        # Duplicate Check
        if self.user_repo.exists_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        
        # hash before storing
        hashed_password = self.hash_password(password)


        # save user info
        user = self.user_repo.create(email=email, hashed_password=hashed_password)

        # return ORM object (route will wrap it in UserResponse)
        return user

