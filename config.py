import os
from pathlib import Path

class Config:
    """Business Dashboard Configuration"""
    
    # Security - Generate a strong secret key for development
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'girasoul-dev-key-2024-change-in-production'
    
    # Database Configuration
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / 'data'
    
    # Business Database (SQLite)
    DATABASE_URL = os.environ.get('DATABASE_URL') or f'sqlite:///{DATA_DIR}/business.db'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO', 'False').lower() == 'true'
    
    # Application Settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    TESTING = False
    
    # Pagination
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', '50'))
    
    # File Upload Settings (for future features)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = DATA_DIR / 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xlsx'}
    
    # Business Settings
    DEFAULT_CURRENCY = os.environ.get('DEFAULT_CURRENCY', 'USD')
    TAX_RATE = float(os.environ.get('TAX_RATE', '0.08'))  # 8% default tax rate
    
    # Email Settings (for future notifications)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Backup Settings
    BACKUP_ENABLED = os.environ.get('BACKUP_ENABLED', 'False').lower() == 'true'
    BACKUP_INTERVAL_HOURS = int(os.environ.get('BACKUP_INTERVAL_HOURS', '24'))
    
    @staticmethod
    def init_app(app):
        """Initialize app with configuration"""
        
        # Ensure data directory exists
        Config.DATA_DIR.mkdir(exist_ok=True)
        
        # Ensure upload directory exists if file uploads are used
        if Config.UPLOAD_FOLDER:
            Config.UPLOAD_FOLDER.mkdir(exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    # Use a development-specific secret key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'girasoul-dev-secret-2024-not-for-production'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # For production, use environment variable or generate a warning
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        import secrets
        SECRET_KEY = secrets.token_hex(32)
        print("⚠️ WARNING: Using auto-generated SECRET_KEY. Set SECRET_KEY environment variable for production!")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'testing-secret-key'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}