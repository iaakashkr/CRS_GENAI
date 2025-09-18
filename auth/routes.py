from flask import Blueprint, request, jsonify
 
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
import bcrypt
from pipeline.modules.extensions import jwt_blacklist

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# In-memory user DB (hashed passwords)
USER_DB = {
    "admin": bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode(),
    "user1": bcrypt.hashpw("password1".encode(), bcrypt.gensalt()).decode()
}

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400
    stored_hash = USER_DB.get(username)
    if not stored_hash or not bcrypt.checkpw(password.encode(), stored_hash.encode()):
        return jsonify({"msg": "Bad credentials"}), 401
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    return jsonify(access_token=access_token, refresh_token=refresh_token)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    jwt_blacklist.add(jti)
    return jsonify(msg="Access token revoked")

@auth_bp.route('/logout_refresh', methods=['POST'])
@jwt_required(refresh=True)
def logout_refresh():
    jti = get_jwt()["jti"]
    jwt_blacklist.add(jti)
    return jsonify(msg="Refresh token revoked")

