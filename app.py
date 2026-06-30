"""
John & Eniola Financial Consultancy Website
Flask Application Entry Point
"""

from datetime import datetime
import os

from flask import Flask, render_template, request
from dotenv import load_dotenv

from extensions import db, login_manager, mail, migrate

from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
load_dotenv()


# =========================================================
# DEFAULT DATA INITIALIZATION (MUST BE ABOVE create_app)
# =========================================================
def init_default_data(app):
    """Initialize default site settings if the table exists."""

    from models import SiteSettings

    with app.app_context():
        try:
            inspector = inspect(db.engine)

            # Table not created yet (migrations not run)
            if "site_settings" not in inspector.get_table_names():
                return

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
                    favicon_path='/static/images/favicon.ico',
                    hero_title='Financial Excellence Redefined',
                    hero_subtitle='Empowering businesses with strategic financial solutions, comprehensive tax planning, and expert advisory services that drive sustainable growth.',
                    hero_btn_text='Schedule Consultation',
                    hero_btn_url='/contact',
                    social_links={
                        'twitter': 'https://twitter.com/je_consultancy/',
                        'facebook': 'https://www.facebook.com/people/John-Eniola-Consultancy-Limited/61552669754142/',
                        'linkedin': 'https://www.linkedin.com/company/johneniolaltd?_l=en_US',
                        'instagram': 'https://www.instagram.com/je_consultancy/'
                    },
                    meta_title='John & Eniola Consultancy',
                    meta_description='Your trusted partner in financial excellence. We provide comprehensive financial solutions that drive business success and sustainable growth.',
                    og_image='/static/images/og-default.jpg',
                )

                db.session.add(default_settings)
                db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()


# =========================================================
# APPLICATION FACTORY
# =========================================================
def create_app():
    """Application factory pattern"""

    app = Flask(__name__, static_folder='static', static_url_path='/static')

    # -------------------------
    # CONFIG
    # -------------------------
    app.config['SECRET_KEY'] = os.getenv(
        'SECRET_KEY',
        'dev-secret-key-change-in-production'
    )

    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'john_eniola_consultancy')

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # -------------------------
    # MAIL CONFIG
    # -------------------------
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USE_TLS'] = False

    mail_username = os.getenv("MAIL_USERNAME", "")

    app.config['MAIL_USERNAME'] = mail_username
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

    app.config['MAIL_DEFAULT_SENDER'] = (
        f"John & Eniola Consultancy <{mail_username}>"
    )

    app.config['MAIL_DEBUG'] = True
    app.config['MAIL_SUPPRESS_SEND'] = False

    # -------------------------
    # CELERY
    # -------------------------
    from celery_config import make_celery

    celery = make_celery(app)
    app.celery = celery

    # -------------------------
    # INIT EXTENSIONS
    # -------------------------
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    mail.init_app(app)
    migrate.init_app(app, db)

    # -------------------------
    # IMPORTS (AFTER INIT)
    # -------------------------
    from models import SiteSettings
    from forms import SubscribeNewsletterForm

    # -------------------------
    # CONTEXT PROCESSORS
    # -------------------------
    @app.context_processor
    def inject_now():
        return {"now": datetime.now()}

    @app.context_processor
    def inject_globals():
        return {'current_year': datetime.now().year}

    @app.context_processor
    def inject_newsletter_form():
        try:
            if request.method == 'POST':
                return {'newsletter_form': SubscribeNewsletterForm()}
            return {'newsletter_form': SubscribeNewsletterForm(formdata=None)}
        except Exception:
            return {'newsletter_form': SubscribeNewsletterForm(formdata=None)}

    @app.context_processor
    def inject_site_settings():
        """Safe site settings injection"""
        try:
            inspector = inspect(db.engine)

            if "site_settings" not in inspector.get_table_names():
                return {"site_settings": None}

            return {"site_settings": SiteSettings.query.first()}

        except SQLAlchemyError:
            return {"site_settings": None}

    # -------------------------
    # LOGIN MANAGER
    # -------------------------
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    # -------------------------
    # BLUEPRINTS
    # -------------------------
    from routes.public_routes import public_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # -------------------------
    # ERROR HANDLERS
    # -------------------------
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template('errors/400.html'), 400

    # -------------------------
    # SEED DATA (SAFE)
    # -------------------------
    init_default_data(app)

    return app