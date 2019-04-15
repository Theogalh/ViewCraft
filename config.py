import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecret'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    # 'postgresql://{}:{}@{}:{}/{}'.format(
    #     'pgsql',  # USERNAME
    #     'pgsql',  # PASSWORD
    #     'localhost',  # HOSTNAME
    #     '5432',  # PORT
    #     'test',  # DB NAME
    # )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', True) is not None
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'theogalh.dev@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'toto'
    ADMINS = ['theogalh.dev@gmail.com']
    POSTS_PER_PAGE = 25
    LANGUAGES = ['en', 'fr']

    BNET_ID = os.environ.get('BNET_ID') or None
    BNET_SECRET = os.environ.get('BNET_SECRET') or None
    BNET_REGION = os.environ.get('BNET_REGION') or 'eu'
    BNET_LOCALE = os.environ.get('BNET_LOCALE') or 'fr_FR'



