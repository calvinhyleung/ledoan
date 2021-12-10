# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
from flask_talisman import Talisman
from flask_mongoengine import MongoEngine
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()

# from .routes import main
from .products.routes import products 
from .users.routes import users
from .admin.routes import admin

def page_not_found(e):
    return render_template("404.html"), 404

def create_app(test_config=None):
    app = Flask(__name__)
    csp = {
        'default-src': [
            '\'self\'',
        ],
        'img-src': ['*', '\'self\'', 'data:'],
        'style-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            'code.jquery.com',
            'cdn.jsdelivr.net',
            'stackpath.bootstrapcdn.com',
            'cdn.plot.ly',
            'cdnjs.cloudflare.com'
        ],
        'script-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            '\'unsafe-eval\'',
            'code.jquery.com',
            'cdn.jsdelivr.net',
            'stackpath.bootstrapcdn.com',
            'cdn.plot.ly',
            'cdnjs.cloudflare.com'
        ],
    }
    Talisman(app, content_security_policy=csp)
    app.config.from_pyfile("config.py", silent=False)
    # app.config[MONGODB_HOST:atlas address]
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(users)
    app.register_blueprint(products)
    app.register_blueprint(admin)
    app.register_error_handler(404, page_not_found)

    login_manager.login_view = "users.login"

    return app