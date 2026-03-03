import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

def _env(key, default=""):
    """Get env var and strip any whitespace / carriage-return characters."""
    return os.getenv(key, default).strip()

class Config:
    SECRET_KEY     = _env("SECRET_KEY",     "dev-secret")
    JWT_SECRET_KEY = _env("JWT_SECRET_KEY", "jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES  = 15 * 60        # 15 minutes
    JWT_REFRESH_TOKEN_EXPIRES = 7 * 24 * 3600  # 7 days

    _DB_HOST = _env("DB_HOST",     "127.0.0.1")
    _DB_PORT = _env("DB_PORT",     "3306")
    _DB_USER = _env("DB_USER",     "root")
    _DB_PASS = _env("DB_PASSWORD", "")
    _DB_NAME = _env("DB_NAME",     "library_db")

    # quote_plus encodes any special chars (@ # etc.) in the password
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{_DB_USER}:{quote_plus(_DB_PASS)}"
        f"@{_DB_HOST}:{_DB_PORT}/{_DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config_map = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
}

