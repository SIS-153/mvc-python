from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import time
from sqlalchemy.exc import OperationalError

# Crear la instancia de SQLAlchemy
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=None):
    app = Flask(__name__, template_folder='views/templates', static_folder='views/static')
    
    # Cargar configuración
    if config_class is None:
        from app.config import Config
        app.config.from_object(Config)
    else:
        app.config.from_object(config_class)
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Configurar Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'
    
    # Registrar blueprints
    from app.controllers.usuario_controller import usuario_bp
    from app.controllers.auth_controller import auth_bp
    
    app.register_blueprint(usuario_bp, url_prefix='/usuarios')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Definir la ruta principal
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')
    
    # Crear tablas y usuario admin con reintentos
    with app.app_context():
        max_retries = 5
        for attempt in range(max_retries):
            try:
                db.create_all()
                crear_usuario_admin()
                break
            except OperationalError as e:
                if attempt < max_retries - 1:
                    print(f"Intento {attempt + 1}/{max_retries}: Esperando a la base de datos...")
                    time.sleep(5)
                else:
                    raise RuntimeError("No se pudo conectar a la base de datos") from e
    
    return app

def crear_usuario_admin():
    from app.models.usuario import Usuario
    
    admin = Usuario.query.filter_by(email='admin@example.com').first()
    if not admin:
        nuevo_admin = Usuario(
            nombre='Admin',
            apellido='Sistema',
            email='admin@example.com',
            telefono='123456789',
            direccion='Dirección Administrativa',
            es_admin=True
        )
        nuevo_admin.set_password('admin123')  
        try:
            db.session.add(nuevo_admin)
            db.session.commit()
            print("✅ Usuario administrador creado exitosamente!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear administrador: {str(e)}")

# Importar modelos
from app.models.usuario import Usuario

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))