# # app_new.py

# from flask import Flask
# from utils.config import Config
# from pipeline.modules.extensions import jwt, jwt_blacklist
# from auth.routes import auth_bp
# from query.routes_new import query_bp   # <-- updated import

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)

#     # JWT init
#     jwt.init_app(app)

#     @jwt.token_in_blocklist_loader
#     def check_if_token_revoked(jwt_header, jwt_payload):
#         return jwt_payload["jti"] in jwt_blacklist

#     # Register blueprints
#     app.register_blueprint(auth_bp)
#     app.register_blueprint(query_bp)  

#     return app

# if __name__ == "__main__":
#     app = create_app()
#     app.run(debug=True)


# app_new.py
import os
import logging
from flask import Flask
from utils.config import Config
from pipeline.modules.extensions import jwt, jwt_blacklist
from auth.routes import auth_bp
from query.routes_new import query_bp   # <-- updated import

# ------------------ Logging Setup ------------------
if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    # configure root logger here
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Clear existing handlers to prevent duplicates
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Add single StreamHandler
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root_logger.addHandler(ch)

# Avoid werkzeug double logs
logging.getLogger('werkzeug').propagate = False

# ------------------ Flask App ------------------
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
    # keep reloader but avoid double logs
    app.run(debug=True, use_reloader=True)
