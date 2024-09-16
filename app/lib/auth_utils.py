from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from config.auth_config import Config

def generate_tokens(user_id):
    access_token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.now() + timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
    }, Config.JWT_SECRET_KEY, algorithm='HS256')

    refresh_token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.now() + timedelta(seconds=Config.JWT_REFRESH_TOKEN_EXPIRES)
    }, Config.JWT_SECRET_KEY, algorithm='HS256')

    return access_token, refresh_token

def verify_password(stored_password, provided_password):
    return check_password_hash(stored_password, provided_password)

def verify_jwt(token):
    try:
        return jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None
