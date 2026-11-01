"""Flask API.  Local run:  python app.py     Production:  gunicorn -c gunicorn.conf.py app:app"""
import os

from flask import Flask, jsonify, request

import config
from routes import games, health, sessions


def create_app():
    app = Flask(__name__, static_folder=None)

    app.register_blueprint(health.bp)
    app.register_blueprint(games.bp)
    app.register_blueprint(sessions.bp)

    # ---- CORS: lets a frontend on another domain call this API ----------------
    allowed = [o.strip() for o in config.CORS_ORIGINS.split(",") if o.strip()]

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin")
        if origin and ("*" in allowed or origin in allowed):
            response.headers["Access-Control-Allow-Origin"] = "*" if "*" in allowed else origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            response.headers["Vary"] = "Origin"
        return response

    @app.get("/")
    def root():
        return jsonify({"name": "PyArcade API", "games": "/api/games", "health": "/api/health"})

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Not found"}), 404

    return app


app = create_app()

if __name__ == "__main__":
    from werkzeug.serving import WSGIRequestHandler

    # Keep-alive: reuse one connection instead of opening a new one per key press
    WSGIRequestHandler.protocol_version = "HTTP/1.1"

    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, threaded=True, debug=False)
