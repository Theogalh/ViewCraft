from flask import Flask
from viewcraft.config import Config
import logging
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel
from logging.handlers import SMTPHandler, RotatingFileHandler
from .utils.bnetrequests import BnetRequests

# Init Flask's module.
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page'
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
babel = Babel()
# TODO Integrer BnetRequests
bnet = BnetRequests()


def create_app(config_class=Config):
    """
    Flask Application Factory
    :param config_class: Configuration Class.
    :return: A Flask Application.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)
    bnet.init_app(app)

    from viewcraft.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from viewcraft.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from viewcraft.main import bp as main_bp
    app.register_blueprint(main_bp)

    from viewcraft.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='ViewCraft Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/viewcraft.log',
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)

    app.logger.info('ViewCraft startup')
    return app
