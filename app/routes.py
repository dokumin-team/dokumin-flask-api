from flask import Blueprint, request, jsonify
from .models.model import predict_image
from .utils.pdf_converter import create_pdf_from_image

main = Blueprint('main', __name__)

@main.route('/process-image', methods=['POST'])
def process_image():
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        # Prediksi menggunakan model ML
        label, confidence = predict_image(file)

        # Konversi gambar ke PDF
        pdf_data = create_pdf_from_image(file.read())

        return jsonify({
            "folderName": label,
            "confidence": confidence,
            "pdfData": pdf_data.decode('utf-8')  # Convert ke base64
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
