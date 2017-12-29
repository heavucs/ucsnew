import os, sys, logging
from flask import Flask, render_template, request
from flask_restplus import Api, Resource
from flask_sqlalchemy import SQLAlchemy

class BasicConfig(object):
    SQLALCHEMY_DATABASE_URI = ''
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    IGNORE_SQLITE_WARNINGS = False

    WEB_ENABLED = False
    WEB_HELP_URL = 'http://localhost/'
    WEB_SESSION_TIMEOUT = 3600
    WEB_SESSION_TIMEOUT_WARN = 60
    WEB_SESSION_KEEPALIVE = 300

    LOGGING = True
    LOGGING_LEVEL = logging.INFO

def load_configuration(app):
    config_file = os.environ.get('APP_CONF_FILE', None)

    if config_file:
       app.config.from_pyfile(config_file)
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

def create_app(app):
    from .api import api
    from .models import db

    load_configuration(app)
    configure_logging(app)
    db.init_app(app)
    db.create_all()
    api.init_app(app)

    return app

app = Flask(__name__)
app = create_app(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0:5000')

