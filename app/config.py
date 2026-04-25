from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    All configuration is loaded from environment variables (or .env file).
 
    Pydantic will:
    - Read values from .env automatically
    - Validate types (e.g., ACCESS_TOKEN_EXPIRE_MINUTES must be an int)
    - Raise a clear error at startup if a required variable is missing
 
    This means your app fails LOUDLY at boot time if misconfigured,
    rather than silently at runtime.
    """

    # App 
    APP_NAME: str = "Auth System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str 

    # JWT 
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

# Single shared instance — import this everywhere
settings = Settings()
