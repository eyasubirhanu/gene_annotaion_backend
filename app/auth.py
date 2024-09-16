import logging
import re
from flask import Blueprint, Flask, abort, session, redirect, request, render_template, flash, jsonify
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
from app import app
import requests
import cachecontrol
from config.auth_config import Config
from app.lib.auth_utils import generate_tokens, verify_password, verify_jwt
from app.lib.auth_db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

# app = Flask(__name__)
# app.config.from_object(Config)

# auth_bp = Blueprint('auth', __name__)

flow = Flow.from_client_secrets_file(
    Config.CLIENT_SECRETS_FILE,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ],
    redirect_uri="http://localhost:5000/callback"
)

def handle_google_auth(id_info, is_registration):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_email = ?", (id_info.get("email"),))
    row = cursor.fetchone()

    if row:
        if not row.get('user_oauth_id'):  # Ensure the `user_oauth_id` field is checked
            cursor.execute("UPDATE users SET user_oauth_id = ? WHERE user_email = ?",
                           (id_info.get("sub"), id_info.get("email")))
            conn.commit()
        session['logged_in'] = True
        session["google_id"] = id_info.get("sub")
        session["username"] = id_info.get("name")
        session["email"] = id_info.get("email")
        access_token, refresh_token = generate_tokens(row['id'])
        conn.close()
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
    else:
        if is_registration:
            cursor.execute("INSERT INTO users (username, user_email, user_oauth_id) VALUES (?, ?, ?)",
                           (id_info.get("name"), id_info.get("email"), id_info.get("sub")))
            conn.commit()
            session['logged_in'] = True
            session["google_id"] = id_info.get("sub")
            session["username"] = id_info.get("name")
            session["email"] = id_info.get("email")
            access_token, refresh_token = generate_tokens(cursor.lastrowid)
            conn.close()
            return jsonify({
                'access_token': access_token,
                'refresh_token': refresh_token
            })
        else:
            conn.close()
            return jsonify({"error": "No account found with this Google login. Please register."}), 404

@app.route('/googlelogin', methods=['GET'])
def google_login():
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    print(f"Authorization URL: {authorization_url}")
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback", methods=['GET'])
def callback():
    flow.fetch_token(authorization_response=request.url)

    if session["state"] != request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=Config.GOOGLE_CLIENT_ID
    )

    return handle_google_auth(id_info, is_registration=True)

@app.route("/googlelogin_callback", methods=['GET'])
def google_login_callback():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/login/callback", methods=['GET'])
def login_callback():
    if "google_id" in session:
        return abort(404)

    flow.fetch_token(authorization_response=request.url)

    if session["state"] != request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=Config.GOOGLE_CLIENT_ID
    )

    return handle_google_auth(id_info, is_registration=False)

@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session
    session.clear()  
    return jsonify({"msg": "Logged out successfully."}), 200

@app.route('/', methods=['GET'])
def index():
    if 'logged_in' in session and session['logged_in']:
        username = session.get('username', 'Guest')
        return jsonify({
            'logged_in': True,
            'username': username,
            'show_registration': False
        }), 200
    else:
        return jsonify({
            'logged_in': False,
            'show_registration': True
        }), 200

@app.route("/register", methods=["POST"])
def register():
    # Log the incoming request for debugging purposes
    logging.debug("Incoming request body: %s", request.data)
    
    # Parse the incoming JSON data
    data = request.get_json()
    logging.debug("Parsed JSON data: %s", data)

    # Validate the required fields are present in the request
    if not data or 'username' not in data or 'email' not in data or 'password' not in data or 'confirm_password' not in data:
        return jsonify({"msg": "Missing required fields (username, email, password, confirm_password)"}), 400

    username = data['username']
    email = data['email']
    password = data['password']
    confirm_password = data['confirm_password']

    # Password validations
    if not password:
        return jsonify({"msg": "Password is required"}), 400

    if len(password) < 8:
        return jsonify({"msg": "Password must be at least 8 characters long"}), 400

    if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
        return jsonify({"msg": "Password must contain both letters and numbers"}), 400

    if password != confirm_password:
        return jsonify({"msg": "Passwords do not match"}), 400

    # Hash the password for secure storage
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

    # Check if the email is already registered
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_email = ?", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()  # Close the connection if user already exists
        return jsonify({"msg": "Email already registered. Please log in."}), 409

    # Insert the new user into the database
    cursor.execute("INSERT INTO users (username, user_email, user_password) VALUES (?, ?, ?)",
                   (username, email, hashed_password))
    conn.commit()
    conn.close()

    # Set session data after successful registration
    session['username'] = username
    session['email'] = email

    # Return success message
    return jsonify({"msg": "Registration successful! You can now log in.", "username": username}), 201

@app.route('/signin', methods=["POST"])
def sign_in():
    if request.method == "POST":
        # Parse JSON data from the request body
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"msg": "Missing email or password"}), 400
        
        email = data['email']
        password = data['password']

        # Fetch user from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        # Check if the user exists
        if not user:
            return jsonify({"msg": "Incorrect email or password"}), 401

        # Verify password
        if verify_password(user['user_password'], password):
            session['logged_in'] = True
            session['username'] = user['username']
            session['email'] = user['user_email']

            # Generate tokens
            access_token, refresh_token = generate_tokens(user['id'])
            return jsonify({
                'msg': 'Login successful',
                'access_token': access_token,
                'refresh_token': refresh_token
            }), 200
        else:
            return jsonify({"msg": "Incorrect email or password"}), 401

    # Return error if the request method is not POST
    return jsonify({"msg": "Method not allowed"}), 405



@app.route('/refresh_token', methods=['POST'])
def refresh_token():
    # Parse JSON data from the request body
    data = request.get_json()

    if not data or 'refresh_token' not in data:
        return jsonify({'error': 'Missing refresh token'}), 400

    refresh_token = data['refresh_token']

    # Check if the refresh token is valid
    user_data = verify_jwt(refresh_token)

    if not user_data:
        return jsonify({'error': 'Invalid or expired refresh token'}), 401

    # Extract user ID from token data and generate new tokens
    user_id = user_data.get('user_id')
    access_token, new_refresh_token = generate_tokens(user_id)

    return jsonify({
        'access_token': access_token,
        'refresh_token': new_refresh_token
    }), 200


