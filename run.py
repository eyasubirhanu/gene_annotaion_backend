import logging
from app import app
from flask import Flask
from config.auth_config import config
from app.lib.auth_db import init_db

app.config.from_object(config)

logging.basicConfig(level=logging.DEBUG)

with app.app_context():
    logging.debug("Initializing database...")
    init_db()
    logging.debug("Database initialized successfully.")



if __name__ == '__main__':
    logging.debug("Starting the application")
    app.run(debug=True, host='0.0.0.0', port=5000)
