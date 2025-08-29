# import os
# from dotenv import load_dotenv

# load_dotenv()

# class Config:
#     """Base configuration class."""
#     SECRET_KEY = os.environ.get('SECRET_KEY') or 'prod-secret-key'
#     AZURE_OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
#     AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT')
#     AZURE_OPENAI_DEPLOYMENT = os.environ.get('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o')
#     # Use latest stable API version
#     AZURE_API_VERSION = "2024-07-01-preview"

# class ProductionConfig(Config):
#     """Production configuration."""
#     DEBUG = False
#     LOG_LEVEL = 'INFO'

# config = {
#     'production': ProductionConfig,
#     'default': ProductionConfig
# }
import os

class Config:
    """Base configuration class."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'prod-secret-key')
    AZURE_OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o')
    # Use latest stable API version
    AZURE_API_VERSION = "2024-07-01-preview"

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = 'INFO'

config = {
    'production': ProductionConfig,
    'default': ProductionConfig
}
