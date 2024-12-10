from flask import Blueprint, request, jsonify
from app.model.load_model import load_model
from app.utils.preprocess import preprocess_image
import io
from reportlab.pdfgen import canvas
import numpy as np
import base64
import os
from PIL import Image
import logging

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)

# Memuat variabel lingkungan
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from dotenv import load_dotenv
load_dotenv()

# Konstanta dan model
MODEL_PATH = os.getenv('MODEL_PATH')
logging.info(f"MODEL_PATH: {MODEL_PATH}")

bp = Blueprint('routes', __name__)

# Muat model saat aplikasi dimulai
model = load_model(MODEL_PATH)
LABEL_MAP = {'document': 0, 'KTP': 1, 'KK': 2, 'SIM': 3}
LABEL_MAP_REVERSE = {v: k for k, v in LABEL_MAP.items()}

def is_image(file_bytes):
    """Memeriksa apakah file yang diberikan adalah gambar valid."""
    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()
        return image.format.lower() in ['jpg', 'jpeg', 'png', 'heic']
    except Exception as e:
        logging.error(f"File verification error: {e}")
        return False

def generate_pdf(predicted_label, confidence):
    """Menghasilkan PDF dengan hasil prediksi."""
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer)
    c.drawString(100, 750, f"Predicted Label: {predicted_label}")
    c.drawString(100, 730, f"Confidence: {confidence:.2f}")
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer.read()

@bp.route('/process-image', methods=['POST'])
def process_image():
    try:
        # Periksa apakah ada file yang dikirim
        if 'file' in request.files:
            image_file = request.files['file']
            image_bytes = image_file.read()
        elif 'image' in request.json:
            # Gambar dikirim dalam bentuk base64
            base64_image = request.json['image']
            image_bytes = base64.b64decode(base64_image)
        else:
            return jsonify({"error": "No image file or base64 image provided"}), 400

        # Validasi apakah file adalah gambar
        if not is_image(image_bytes):
            return jsonify({"error": "Invalid image format. Only PNG, JPG, and HEIC are allowed."}), 400

        # Proses gambar
        input_data = preprocess_image(image_bytes)
        predictions = model.predict(input_data)
        predicted_label_idx = np.argmax(predictions)
        confidence = np.max(predictions)

        # Dapatkan nama label berdasarkan indeks
        label_name = LABEL_MAP_REVERSE.get(predicted_label_idx, "Unknown")

        # Buat PDF
        pdf_data = generate_pdf(label_name, confidence)

        # Konversi PDF ke Base64 untuk dikembalikan
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

        # Berikan respons JSON
        return jsonify({
            "predicted_label": label_name,
            "confidence": float(confidence),
            "pdfData": pdf_base64
        })

    except Exception as e:
        logging.error(f"Processing error: {e}")
        return jsonify({"error": str(e)}), 500
