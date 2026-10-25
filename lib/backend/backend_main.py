import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Load local environment variables from .env if present
load_dotenv()

from extension import db
from aws_service import load_config_from_ssm

logger = logging.getLogger("roadsense.backend")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def seed_initial_data(app):
    """Seed default administrator and demo road hazards if database is fresh"""
    from auth import User
    from models import IssueReport
    from werkzeug.security import generate_password_hash
    from datetime import datetime

    with app.app_context():
        # 1. Seed Default Administrator
        admin_email = "admin@roadsense.gov"
        existing_admin = User.query.filter_by(email=admin_email).first()
        if not existing_admin:
            logger.info("Seeding default administrator account...")
            admin = User(
                username="admin_authority",
                email=admin_email,
                password_hash=generate_password_hash("12345678"),
                is_administrator=True
            )
            db.session.add(admin)
            db.session.commit()
            logger.info(f"Default admin created ({admin_email} / 12345678)")

        # 2. Seed Demo Road Hazards if DB is empty (for live faculty demo)
        if IssueReport.query.count() == 0:
            logger.info("Seeding initial road hazards for demonstration...")
            demo_issues = [
                {
                    "username": "citizen_rahul",
                    "location": {"lat": 27.6198, "lng": 85.5385},
                    "label": "Potholes",
                    "severity": "critical",
                    "status": "reported",
                    "confidence_score": 0.94,
                    "description": "Deep 15cm pothole on main avenue causing vehicle damage near bus stop.",
                    "image_url": "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=600&auto=format&fit=crop"
                },
                {
                    "username": "citizen_priya",
                    "location": {"lat": 27.6234, "lng": 85.5420},
                    "label": "Waterlogging",
                    "severity": "critical",
                    "status": "deployed",
                    "confidence_score": 0.88,
                    "description": "Severe road flooding after monsoon rain; drainage is completely blocked.",
                    "image_url": "https://images.unsplash.com/photo-1547683905-f686c993aae5?w=600&auto=format&fit=crop"
                },
                {
                    "username": "citizen_amit",
                    "location": {"lat": 27.6150, "lng": 85.5340},
                    "label": "Damaged Road",
                    "severity": "medium",
                    "status": "underprocessed",
                    "confidence_score": 0.82,
                    "description": "Surface erosion and asphalt cracks spreading across right driving lane.",
                    "image_url": "https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=600&auto=format&fit=crop"
                },
                {
                    "username": "citizen_sarah",
                    "location": {"lat": 27.6210, "lng": 85.5310},
                    "label": "Broken Streetlight",
                    "severity": "low",
                    "status": "resolved",
                    "confidence_score": 0.96,
                    "description": "Streetlight pole wiring short-circuited; light was flickering then went dark.",
                    "image_url": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=600&auto=format&fit=crop"
                }
            ]

            for d in demo_issues:
                report = IssueReport(
                    username=d["username"],
                    location=d["location"],
                    label=d["label"],
                    severity=d["severity"],
                    status=d["status"],
                    confidence_score=d["confidence_score"],
                    description=d["description"],
                    image_url=d["image_url"],
                    segmented_image="",
                    created_at=datetime.utcnow()
                )
                db.session.add(report)
            db.session.commit()
            logger.info("Demo road hazards seeded successfully.")


def create_app():
    app = Flask(__name__)

    # Default local configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "roadsense_jwt_secret_dev_key_2026")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Pull AWS parameters (RDS host, secrets, S3 bucket) if on AWS EC2
    load_config_from_ssm(app)

    db.init_app(app)

    # CORS configuration to allow Flutter Mobile App & Web Admin Dashboard
    CORS(app, resources={r"/*": {"origins": "*"}},
         expose_headers=["Content-Type", "Authorization"],
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"])

    # Register API Blueprints
    from auth import auth_bp
    from admin_endpoint import admin_bp
    from inference import inference_bp, citizen_report, health_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(inference_bp)
    app.register_blueprint(citizen_report)
    app.register_blueprint(health_bp)

    # Initialize tables and seed defaults
    with app.app_context():
        db.create_all()
        seed_initial_data(app)

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 6969))
    debug_mode = os.getenv("FLASK_ENV", "development").lower() == "development"

    logger.info(f"Starting RoadSense Cloud Backend on port {port} (Debug: {debug_mode})")
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug_mode
    )