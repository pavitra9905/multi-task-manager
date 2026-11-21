from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from extensions import db, migrate, jwt
import models  # noqa: F401
from routes.auth import auth_bp
from routes.categories import categories_bp
from routes.tasks import tasks_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    CORS(app, origins=["http://localhost:5173"])
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(tasks_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

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