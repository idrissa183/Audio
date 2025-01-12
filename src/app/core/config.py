from pydantic import PostgresDsn, validator, MySQLDsn, FilePath
from typing import Any, Dict, Optional, Literal, Union
from datetime import datetime, timezone
from typing import List
from pydantic_settings import BaseSettings


APP_NAME = "VoiceQualityAI"
VERSION = "v1.0.0"


class Settings(BaseSettings):
    """Global Settings"""

    # Application
    APP_NAME: str = APP_NAME
    VERSION: str = VERSION
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"


    # Database Configuration
    DATABASE_TYPE: Literal['mysql', 'postgresql', 'sqlite']


    # Postgresql Configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "root"
    POSTGRES_DB: str = "voice_quality_ai"
    POSTGRES_PORT: int = 5432


    # MySQL Configuration
    MYSQL_SERVER: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DB: str = "voice_quality_ai"


    SQLITE_DB_FILE: Optional[FilePath] = "voice_quality_ai.sqlite"


    # JWT CONFIG
    TOKEN_SECRET_KEY: str = "PVDlqCIiAso7KQPrh2aMhILs8JNKMz6L9QzEmEUnsCA"
    ALGORITHM: str = "HS256"
    FRONTEND_URL: str = "http://localhost:5173/"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


    # STMP configuration
    MAIL_USERNAME: str = "uedraogoidrissa7108@gmail.com"
    MAIL_PASSWORD: str = "keedgrvkcqfpjtrd"
    MAIL_FROM: str = "ouedraogoidrissa7108@gmail.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    MAIL_FROM_NAME: str = "VoiceQualityAI"

    # GitHub OAuth
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:5173/auth"

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = (
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",
    )
    ALLOWED_METHODS: List[str] = ("GET", "POST", "PUT", "DELETE", "OPTIONS")
    ALLOWED_HEADERS: List[str] = ("*",)

    
    # Datetime Configuration
    TIMEZONE: str = "UTC"
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    DATE_FORMAT: str = "%Y-%m-%d"

    
    # Database URIs
    POSTGRES_URI: Optional[PostgresDsn] = None
    MYSQL_URI: Optional[MySQLDsn] = None
    SQLITE_URI: Optional[str] = None


    @validator("POSTGRES_URI", pre=True)
    def assemble_postgres_uri(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        if values.get("DATABASE_TYPE") != "postgresql":
            return None
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"{values.get('POSTGRES_DB') or ''}",
        )


    @validator("MYSQL_URI", pre=True)
    def assemble_mysql_uri(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        if values.get("DATABASE_TYPE") != "mysql":
            return None
        return MySQLDsn.build(
            scheme="mysql+pymysql",
            username=values.get("MYSQL_USER"),
            password=values.get("MYSQL_PASSWORD"),
            host=values.get("MYSQL_SERVER"),
            port=values.get("MYSQL_PORT"),
            path=f"/{values.get('MYSQL_DB') or ''}"
        )

    @validator("SQLITE_URI", pre=True)
    def assemble_sqlite_uri(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        if values.get("DATABASE_TYPE") != "sqlite":
            return None
        db_file = values.get("SQLITE_DB_FILE")
        if db_file:
            return f"sqlite:///{db_file}"
        raise ValueError("SQLITE_DB_FILE must be set when using SQLite.")


    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return list(set(v))


    @staticmethod
    def get_current_datetime() -> datetime:
        """Return current datetime in configured timezone"""
        return datetime.now(timezone.utc)


    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
