#################### Imports #####################
from flask import Flask
from flask_bootstrap import Bootstrap
import os


#################### Create flask application #####################
def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
    
    uri = os.getenv("DATABASE_URL")  # or other relevant config var
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    Bootstrap(app)

    return app


#################### Create app instance #####################
app = create_app()


#################### Create custom path #####################
from app.phototainment.views import custom_bp
app.register_blueprint(custom_bp, url_prefix='/phototainment')


