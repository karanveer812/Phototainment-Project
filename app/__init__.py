from flask import Flask

from flask_bootstrap import Bootstrap
import os

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    Bootstrap(app)

    return app


app = create_app()


from .phototainment.views import custom_bp
app.register_blueprint(custom_bp, url_prefix='/phototainment')


