import tensorflow as tf
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from dotenv import load_dotenv

load_dotenv()

MODEL_PATH = os.getenv('MODEL_PATH')

def load_model(MODEL_PATH):
    return tf.keras.models.load_model(MODEL_PATH)
