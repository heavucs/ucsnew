import os, sys, logging
from flask import Flask, render_template, request, Response
from flask_restplus import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

from werkzeug.exceptions import BadRequest      # 400
from werkzeug.exceptions import Unauthorized    # 401
from werkzeug.exceptions import Forbidden       # 403
from werkzeug.exceptions import NotFound        # 404

class BasicConfig(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    IGNORE_SQLITE_WARNINGS = False

    ADMIN_PASS_FILE = ''
    PW_HASH = 'pbkdf2:sha1:2000'
    SECRET_KEY = ''

    WEB_ENABLED = False
    WEB_HELP_URL = 'http://localhost/'
    WEB_SESSION_TIMEOUT = 3600
    WEB_SESSION_TIMEOUT_WARN = 60
    WEB_SESSION_KEEPALIVE = 300

    LOGGING = True
    LOGGING_LEVEL = logging.INFO

def load_configuration(app, configfile=[]):
    if configfile:
        os.environ.get(configfile)
        app.config.from_pyfile(configfile)
        print("Configuration file loaded")
    elif os.environ.get('APP_CONF_FILE', None):
        configfile = os.environ.get('APP_CONF_FILE', None)
        app.config.from_pyfile(configfile)
        print("Configuration file loaded")
    else:
        app.config.from_object(BasicConfig)

    return app

def configure_logging(app):
    if app.config['LOGGING']:
        logger = logging.getLogger('basic_logs')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(app.config['LOGGING_LEVEL'])
        ch.setFormatter(formatter)
        app.logger.addHandler(ch)
        #sys.stderr.write('Logger Level: %s' % app.logger.getEffectiveLevel())
        #app.logger.info('Logger Level: %s' % app.logger.getEffectiveLevel())
        #app.logger.debug('debug message')
        #app.logger.info('info message')
        #app.logger.warn('warn message')
        #app.logger.error('error message')
        #app.logger.critical('critical message')

def create_app(app, configfile=[]):
    from .models import db

    load_configuration(app, configfile=configfile)
    configure_logging(app)
    db.init_app(app)
    db.create_all()

    if 'SECRET_KEY_FILE' in app.config: 
        try:
            f = open(app.config['SECRET_KEY_FILE'], 'rb')
            app.secret_key = f.read()
            f.close()
        except IOError as e:
            print("Unable to read secret key file: %s" % app.config['SECRET_KEY_FILE'])
            sys.exit(1)
    else:
        app.logger.warning("SECRET_KEY_FILE setting not found. Using a random secret...")
        app.secret_key = os.urandom(32)

    return app

from flask import g as flask_g
app = Flask(__name__)
load_configuration(app)
http_auth = HTTPBasicAuth()
app = create_app(app)
from .api.v1 import api
api.init_app(app)

@http_auth.verify_password
def verify_password(username, password):
    """Decorator placed on views that require authentication"""
    from .logic import get_users

    if hasattr(flask_g, 'username'):
        if not flask_g.username == '' and username == '':
            username = flask_g.username
    if hasattr(flask_g, 'password'):
        if not flask_g.password == '' and password == '':
            password = flask_g.password

    if username == '':
        app.logger.warning("Unauthorized access attempted!")
        return False

    if username == 'admin':
        if 'ADMIN_PASS_FILE' in app.config:

            try:
                f = open(app.config['ADMIN_PASS_FILE'], 'r')
                app.config['ADMIN_PASS'] = str(f.read()).rstrip("\r\n")
                f.close()
            except IOError as e:
                print("Unable to read admin password file: %s" % app.config['ADMIN_PASS_FILE'])
                return False

            if check_password_hash(app.config['ADMIN_PASS'], str(password)):
                flask_g.username = username
                flask_g.password = password
                return True
            else:
                return False

    if not username == '':
        users_l = get_users(q_username=username, page=1, per_page=1)
        if len(users_l) < 1:
            print("User {} not found".format(username))
            return False
        else:
            user = users_l[0].as_dict()

        if check_password_hash(user['password'], str(password)):
            flask_g.username = user['username']
            flask_g.password = user['password']
            return True
        else:
            return False

def authorized_roles(roles=[]):
    """Decorator placed on views requiring authorization"""

    for role in roles:
        if role in flask_g.roles:
            return f(*args, **kwargs)
        raise Forbidden()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0:5000')

