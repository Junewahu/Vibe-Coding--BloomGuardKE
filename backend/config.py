import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import secrets

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "BloomGuardKE"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security Settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database Settings
    DATABASE_URL: str = "sqlite:///./bloomguard.db"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # File Upload Settings
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png", "pdf", "xlsx"}
    
    # WhatsApp Settings
    WHATSAPP_API_URL: Optional[str] = None
    WHATSAPP_API_KEY: Optional[str] = None
    
    # IVR Settings
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # USSD Settings
    USSD_SERVICE_CODE: str = "*384*"
    USSD_SESSION_TIMEOUT: int = 60  # seconds
    
    # Email Settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Redis Settings (for caching and session management)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Communication service settings
    WHATSAPP_API_KEY: str = ""
    SMS_API_KEY: str = ""
    VOICE_API_KEY: str = ""
    SMS_API_URL: str = "https://api.sms.com/v1"
    VOICE_API_URL: str = "https://api.voice.com/v1"
    
    # NHIF settings
    NHIF_API_KEY: str = ""
    NHIF_API_URL: str = "https://api.nhif.or.ke/v1"
    
    # Analytics settings
    ENABLE_ANALYTICS: bool = True
    ANALYTICS_DB_URL: Optional[str] = None
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Create settings instance
settings = Settings()

# Create upload directory if it doesn't exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True) 