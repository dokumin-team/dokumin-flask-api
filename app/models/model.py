import tensorflow as tf
import numpy as np
import cv2
import os
from dotenv import load_dotenv

load_dotenv()
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Memuat model ML
MODEL_PATH = os.getenv("MODEL_PATH")

if os.path.exists(MODEL_PATH):
    print(f"File model ditemukan di: {MODEL_PATH}")
else:
    print(f"File model tidak ditemukan di file .env")

model = tf.keras.models.load_model(MODEL_PATH)

# Label mapping
LABEL_MAP = {0: "document", 1: "KTP", 2: "KK", 3: "SIM"}

def preprocess_image(image):
    img = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)
    img = cv2.resize(img, (256, 256))
    img = img.astype('float32') / 255.0
    img = np.expand_dims(img, axis=0)
    return img

def predict_image(image):
    try:
        input_data = preprocess_image(image)
        predictions = model.predict(input_data)
        predicted_label = np.argmax(predictions)
        confidence = np.max(predictions)
        return LABEL_MAP.get(predicted_label, "unknown"), confidence
    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        return "error", 0.0
