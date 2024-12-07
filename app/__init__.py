import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Optionally set a default config file path
CONFIG_FILE_PATH = os.getenv("CONFIG_FILE_PATH", "config.py")

print ("Path config.py :", CONFIG_FILE_PATH)

def create_app():
    app = Flask(__name__)
    
    # Load configuration from a Python file
    if os.path.isfile(CONFIG_FILE_PATH):
        app.config.from_pyfile(CONFIG_FILE_PATH)
    else:
        raise FileNotFoundError(f"Configuration file not found: {CONFIG_FILE_PATH}")
    
    # Import and register blueprints
    from .routes import main
    app.register_blueprint(main)
    
    return app
