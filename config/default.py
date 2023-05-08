import os
from dotenv import load_dotenv

# load environment variables from .env file
DOTENV_PATH = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(DOTENV_PATH)
# define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CERTIFICATE_DIR = os.path.join(BASE_DIR, os.environ.get('SSL_CERT'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_size': 10, 'pool_recycle': 299}
    CERTIFICATE = CERTIFICATE_DIR
    TIME_ZONE = 'Africa/Nairobi'
    TIME_FORMAT = '%Y%m%d%H%M%S'
    # Daraja/MPESA Status Codes
    MPESA_B2B_SUCCESS_CODE = '0'
    MPESA_B2B_FAILURE_CODE = '1'
    GENERIC_FAILURE_CODE = '999'

    @staticmethod
    def init_app(app):
        pass


class TestingConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI_TEST')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI_DEV')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')


config = {
    'default': DevelopmentConfig,
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
