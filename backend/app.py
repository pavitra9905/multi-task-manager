from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from extensions import db, migrate, jwt, limiter
import models  # noqa: F401
from routes.auth import auth_bp
from routes.categories import categories_bp
from routes.tasks import tasks_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    # Behind Render's proxy, read the real client IP from X-Forwarded-For
    # (trust only 1 proxy, so a fake header sent by a client is ignored)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

    CORS(app, origins=app.config["FRONTEND_ORIGINS"])
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(tasks_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.errorhandler(429)
    def too_many_requests(e):
        return jsonify({"error": "Too many attempts. Please wait a few minutes and try again."}), 429

    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify({"error": "Missing or invalid token."}), 401

    @jwt.expired_token_loader
    def expired_token(header, payload):
        return jsonify({"error": "Token expired. Please log in again."}), 401

    @jwt.invalid_token_loader
    def bad_token(reason):
        return jsonify({"error": "Invalid token."}), 401

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)