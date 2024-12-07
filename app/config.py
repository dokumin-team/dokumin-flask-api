import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')  # Jika tidak ada, gunakan 'default_secret_key'

DEBUG = True