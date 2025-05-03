# __init__.py
from datetime import datetime

from flask import Flask
from flask_login import LoginManager
from .database import create_database, get_user_by_id


""""
this script is for initialising the app. the script was taken from techwithtim's flask tutorial which is cited in the ReadMe
"""


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

    # IMPORTANT: Create database at startup
    create_database()

    from .views import views
    from .auth import auth

    def datetimeformat(value, fmt='%B %d, %Y at %I:%M %p'):
        # expects an ISO-format string like '2025-04-30T17:06'
        try:
            dt = datetime.fromisoformat(value)
        except ValueError:
            dt = datetime.strptime(value, '%Y-%m-%dT%H:%M')
        return dt.strftime(fmt)

    app.jinja_env.filters['datetimeformat'] = datetimeformat

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(user_id)

    return app
