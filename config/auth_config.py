import os
import pathlib
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("APP_SECRET")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET")
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 604800  # 1 day
    GOOGLE_CLIENT_ID = os.getenv("CLIENT_ID")
    OAUTHLIB_INSECURE_TRANSPORT = os.getenv("OAUTHLIB_INSECURE_TRANSPORT", '1')
    CLIENT_SECRETS_FILE= os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

config = Config()
