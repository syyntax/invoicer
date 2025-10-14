from flask import Flask, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so Flask-Migrate can detect them
    from app import models

    # Register the main blueprint containing all routes
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        # Initialize company settings if they don't exist
        from app.models import CompanySettings
        if not CompanySettings.query.first():
            try:
                default_settings = CompanySettings(
                    name="StormKeep Inc.",
                    address_line1="123 Corporate Blvd",
                    address_line2="Suite 400",
                    city="Capital City",
                    state="ST",
                    zip_code="12345",
                    email="info@stormkeep.com",
                    phone="555-123-4567"
                )
                db.session.add(default_settings)
                db.session.commit()
                app.logger.info("Default CompanySettings created.")
            except Exception as e:
                app.logger.error(f"Error creating default CompanySettings: {e}")
                db.session.rollback()

    return app