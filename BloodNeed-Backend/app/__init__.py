# app/__init__.py

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from flask_socketio import SocketIO

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
socketio = SocketIO()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    
    if db_user and db_host and db_name:
        app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password or ''}@{db_host}/{db_name}"
    else:
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'blood_need.db')}"
        print(f"WARNING: MySQL config incomplete. Falling back to SQLite: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400))
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Register blueprints (routes)
    from app.auth.routes import auth_bp
    from app.donor.routes import donor_bp
    from app.request.routes import request_bp
    from app.matching.routes import matching_bp
    from app.ml.routes import ml_bp
    from app.gamification.routes import gamification_bp
    from app.notification.routes import notification_bp
    from app.hospital.routes import hospital_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(donor_bp, url_prefix='/api/donor')
    app.register_blueprint(request_bp, url_prefix='/api/request')
    app.register_blueprint(matching_bp, url_prefix='/api/matching')
    app.register_blueprint(ml_bp, url_prefix='/api/ml')
    app.register_blueprint(gamification_bp, url_prefix='/api/gamification')
    app.register_blueprint(notification_bp, url_prefix='/api/notifications')
    app.register_blueprint(hospital_bp, url_prefix='/api/hospital')
    
    @app.route('/')
    def home():
        return {
            'message': '🩸 Blood Need API',
            'status': 'running',
            'version': '1.0.0'
        }
    
    @app.route('/health')
    def health():
        db_status = 'disconnected'
        try:
            with app.app_context():
                db.session.execute(db.text('SELECT 1'))
                db_status = 'connected'
        except Exception as exc:
            db_status = f'error: {exc}'

        return {
            'status': 'healthy' if db_status == 'connected' else 'degraded',
            'database': db_status
        }
    
    return app