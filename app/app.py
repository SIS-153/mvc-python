# app.py
from flask import Flask
from config import Config
from database import db
from controllers.usuario_controller import usuario_bp
from controllers.prenda_controller import prenda_bp

app = Flask(__name__, template_folder='views/templates', static_folder='views/static')
app.config.from_object(Config)

db.init_app(app)

# Registrar los blueprints
app.register_blueprint(usuario_bp, url_prefix='/usuarios')


@app.route('/')
def index():
    return "Bienvenido a la Tienda de Ropa"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)