# config.py you can put this file anywhere in the project
class Config(object):
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """
    Development configurations
    """
    MYSQL_DATABASE_USER = 'root'
    MYSQL_DATABASE_PASSWORD = ''
    MYSQL_DATABASE_HOST = 'localhost'
    MYSQL_DATABASE_PORT = 3306
    MYSQL_DATABASE_DB = 'projet'  # can be any

    DEBUG = True


class ProductionConfig(Config):
    """
    Production configurations
    """
    MYSQL_DATABASE_USER = 'yourusername'
    MYSQL_DATABASE_PASSWORD = 'yourpassword'
    MYSQL_DATABASE_HOST = 'linktoyourdb' # eg to amazone db :- yourdbname.xxxxxxxxxx.us-east-2.rds.amazonaws.com
    MYSQL_DATABASE_PORT = 'yourport'
    MYSQL_DATABASE_DB = 'yourdbname'

    DEBUG = False
