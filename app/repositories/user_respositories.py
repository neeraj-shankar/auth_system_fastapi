from sqlalchemy.orm import Session
from app.models.user import User

class UserRespository:
    """
    All database operations for the User model live here.
    No business logic. No password hashing. No HTTP concepts.
    Just: ask DB a question, get an answer.
 
    Why a class instead of plain functions?
    The Session is injected once in __init__ and reused across all methods.
    This keeps each method focused and makes the repository easy to test —
    you can pass a fake session in tests without touching a real database.
    """

    def __init__(self, db:Session):
        self.db = db 

    
    def find_by_email(self, email:str)-> User | None:
        """
        Look up a user by email.
        Returns the User object if found, None if not.
 
        We use .first() instead of .one() because:
        - .one() raises an exception if no result is found
        - .first() returns None — which is what we want to check in the service
        """

        return (
            self.db.query(User).filter(User.email==email.lower()).first()
        )
    
    def find_by_id(self, user_id: str)-> User | None:
        """Look up a user by their UUID primary key."""
        return (
            self.db.query(User).filter(User.id == user_id).first()
        )
    
    def create(self, email: str, hashed_password: str)-> User:
        """
        Insert a new user row into the database.
 
        Three-step pattern for all SQLAlchemy inserts:
          1. Create the model instance (in memory only)
          2. db.add() — stage it (like git add)
          3. db.commit() — write to DB (like git commit)
          4. db.refresh() — reload from DB to get server-generated values
                            (created_at, updated_at, any DB defaults)
 
        If commit() fails (e.g. duplicate email race condition),
        SQLAlchemy automatically rolls back, keeping the DB consistent.
        """

        user = User(
            email = email.lower(),
            hashed_password = hashed_password
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user
    
    def exists_by_email(self, email: str) -> bool:
        from sqlalchemy import func

        count = (
            self.db.query(func.count(User.id)).filter(User.email == email.lower()).scalar()
        )

        return count > 0




