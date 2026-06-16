"""
John & Eniola Financial Consultancy Website
Flask Application Entry Point
"""

from datetime import datetime
import os
from flask import Flask, render_template
from extensions import db, login_manager, mail, migrate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
# db = SQLAlchemy()
# login_manager = LoginManager()
# mail = Mail()




def create_app():
    """Application factory pattern"""
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'john_eniola_consultancy')
    
    # Use PyMySQL for MySQL connection
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # === MAIL CONFIGURATION ===
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = (
        os.getenv('MAIL_DEFAULT_SENDER_NAME', 'John & Eniola Consultancy'),
        os.getenv('MAIL_DEFAULT_SENDER')
    )

    # Celery Config
    app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    # Initialize Celery
    from celery_config import make_celery
    celery = make_celery(app)
    app.celery = celery

    # === CELERY CONFIGURATION ===
    # app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    # app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    # app.config['CELERY_TASK_SERIALIZER'] = 'json'
    # app.config['CELERY_RESULT_SERIALIZER'] = 'json'
    # app.config['CELERY_ACCEPT_CONTENT'] = ['json']
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    mail.init_app(app)
    migrate.init_app(app, db)


    from celery_config import celery as celery_app, make_celery
    celery = make_celery(app)           # Configure it
    app.celery = celery                 # Optional: attach to app


    from models import SiteSettings

    from forms import NewsletterForm

    @app.context_processor
    def inject_newsletter_form():
        return {
            'newsletter_form': NewsletterForm()
        }

    @app.context_processor
    def inject_globals():

        return {
            'current_year': datetime.now().year
        }

    @app.context_processor
    def inject_site_settings():
        """Inject global site settings into all templates"""

        site_settings = SiteSettings.query.first()

        return dict(site_settings=site_settings)
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes.public_routes import public_bp
    from routes.admin_routes import admin_bp
    
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')




    @app.errorhandler(404)
    def not_found_error(error):
        """404 Page Not Found"""
        return render_template('errors/404.html'), 404


    @app.errorhandler(500)
    def internal_error(error):
        """500 Internal Server Error"""

        db.session.rollback()

        return render_template('errors/500.html'), 500
    
    # Create tables and seed data
    with app.app_context():
        from models import User, SiteSettings, Service
        # db.create_all()
        init_default_data()
    
    return app


def init_default_data():
    """Initialize default site settings if they don't exist"""
    from models import SiteSettings
    
    if SiteSettings.query.first() is None:
        default_settings = SiteSettings(
            company_name='John & Eniola Consultancy',
            company_description='Your trusted partner in financial excellence. We provide comprehensive financial solutions that drive business success and sustainable growth.',
            phone_primary='+2349096702222',
            phone_secondary='+2349133333478',
            email='info@johneniola.com',
            address='40, 1st Crescent, Lugbe FHA, Abuja, Federal Capital Territory, Nigeria',
            logo_image_path='/static/images/logo.png',
            logo_dark_image_path='/static/images/logo-dark.png',
            favicon_path='/static/images/favicon.ico'
        )
        db.session.add(default_settings)
        db.session.commit()
