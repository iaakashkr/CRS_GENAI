from flask import Flask
from utils.config import Config
from pipeline.modules.extensions import jwt, jwt_blacklist
from auth.routes import auth_bp
from query.routes_new import query_bp   # <-- updated import

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # JWT init
    jwt.init_app(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload["jti"] in jwt_blacklist

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(query_bp)  

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
