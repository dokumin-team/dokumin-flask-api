from flask import Blueprint, request, jsonify
from app.model.load_model import load_model
from app.utils.preprocess import preprocess_image
import io
from reportlab.pdfgen import canvas
import numpy as np
import base64
import os
from PIL import Image
from werkzeug.utils import secure_filename
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

# Label map harus didefinisikan di awal
label_map = {'document': 0, 'KTP': 1, 'KK': 2, 'SIM': 3}

def is_image(image_file):
    """Memeriksa apakah file yang diberikan adalah gambar valid."""
    try:
        image = Image.open(image_file)
        image.verify()
        return image.format.lower() in ['jpg', 'jpeg', 'png', 'heic']
    except Exception as e:
        logging.error(f"File verification error: {e}")
        return False

def generate_pdf(image_file):
    """Menghasilkan PDF dengan hasil prediksi, menyesuaikan ukuran gambar dengan halaman PDF."""
    pdf_buffer = io.BytesIO()

    # Ukuran halaman PDF standar A4 dalam points (1 inch = 72 points)
    PAGE_WIDTH = 595.27
    PAGE_HEIGHT = 841.89

    # Buat canvas dengan ukuran A4
    c = canvas.Canvas(pdf_buffer, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    # Tentukan nama file yang aman dan lokasi sementara
    secure_name = secure_filename(image_file.filename)
    temp_image_path = f"./tmp/{secure_name}"

    try:
        # Pastikan direktori ./tmp ada
        os.makedirs("./tmp", exist_ok=True)

        # Simpan file sementara
        image_file.seek(0)
        image_file.save(temp_image_path)

        # Gunakan Pillow untuk mendapatkan ukuran gambar
        with Image.open(temp_image_path) as img:
            img_width, img_height = img.size

            # Hitung rasio aspek gambar
            aspect_ratio = img_width / img_height

            # Tentukan margin (dalam points)
            MARGIN = 40
            max_width = PAGE_WIDTH - (2 * MARGIN)
            max_height = PAGE_HEIGHT - (2 * MARGIN)

            # Hitung ukuran gambar yang disesuaikan
            if img_width > max_width or img_height > max_height:
                if img_width / max_width > img_height / max_height:
                    new_width = max_width
                    new_height = new_width / aspect_ratio
                else:
                    new_height = max_height
                    new_width = new_height * aspect_ratio
            else:
                new_width = img_width
                new_height = img_height

            # Hitung posisi untuk memusatkan gambar
            x = (PAGE_WIDTH - new_width) / 2
            y = (PAGE_HEIGHT - new_height) / 2

            # Tambahkan gambar ke PDF dengan ukuran yang sudah disesuaikan
            c.drawImage(temp_image_path, x, y, width=new_width, height=new_height)

    except Exception as e:
        raise RuntimeError(f"Error generating PDF: {e}")
    finally:
        # Hapus file sementara
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)

    # Simpan PDF
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer.read()

@bp.route('/process-image', methods=['POST'])
def process_image():
    try:
        # Periksa apakah ada file yang dikirim
        if 'file' in request.files:
            image_file = request.files['file']
            # Simpan file sementara ke folder tmp
            temp_path = '../tmp/temp_image.jpg'
            # Pastikan folder tmp ada
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            image_file.save(temp_path)
        else:
            return jsonify({"error": "No image file provided"}), 400

        # Validasi apakah file adalah gambar
        if not is_image(image_file):
            return jsonify({"error": "Invalid image format. Only PNG, JPG, and HEIC are allowed."}), 400

        # Proses gambar
        input_data = preprocess_image(temp_path)

        os.remove(temp_path)

        predictions = model.predict(input_data)
        predicted_label = np.argmax(predictions)
        confidence = np.max(predictions)

        # Dapatkan nama label berdasarkan indeks
        label_name = [k for k, v in label_map.items() if v == predicted_label][0]

        logging.info(f"Prediksi: {label_name} (Confidence: {confidence:.2f})")

        # Tentukan folder berdasarkan label
        if label_name in ['KTP', 'KK', 'SIM']:
            folder_name = "Pribadi"
        else:
            folder_name = "Lainnya"

        # Buat PDF
        pdf_data = generate_pdf(image_file)

        # Konversi PDF ke Base64 untuk dikembalikan
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

        # Berikan respons JSON
        return jsonify({
            "predicted_label": label_name,
            "confidence": float(confidence),
            "pdfData": pdf_base64,
            "folder_name": folder_name
        })

    except Exception as e:
        logging.error(f"Processing error: {e}")
        return jsonify({"error": str(e)}), 500


# from flask import Blueprint, request, jsonify
# from app.model.load_model import load_model
# from app.utils.preprocess import preprocess_image
# import io
# from reportlab.pdfgen import canvas
# import numpy as np
# import base64
# import os
# from PIL import Image
# from werkzeug.utils import secure_filename
# import logging

# # Konfigurasi logging
# logging.basicConfig(level=logging.INFO)

# # Memuat variabel lingkungan
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# from dotenv import load_dotenv
# load_dotenv()

# # Konstanta dan model
# MODEL_PATH = os.getenv('MODEL_PATH')
# logging.info(f"MODEL_PATH: {MODEL_PATH}")

# bp = Blueprint('routes', __name__)

# # Muat model saat aplikasi dimulai
# model = load_model(MODEL_PATH)

# def is_image(file_bytes):
#     """Memeriksa apakah file yang diberikan adalah gambar valid."""
#     try:
#         image = Image.open(io.BytesIO(file_bytes))
#         image.verify()
#         return image.format.lower() in ['jpg', 'jpeg', 'png', 'heic']
#     except Exception as e:
#         logging.error(f"File verification error: {e}")
#         return False


# def generate_pdf(image_file):
#     """Menghasilkan PDF dengan hasil prediksi, menyesuaikan ukuran gambar dengan halaman PDF."""
#     pdf_buffer = io.BytesIO()
    
#     # Ukuran halaman PDF standar A4 dalam points (1 inch = 72 points)
#     PAGE_WIDTH = 595.27
#     PAGE_HEIGHT = 841.89
    
#     # Buat canvas dengan ukuran A4
#     c = canvas.Canvas(pdf_buffer, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    
#     # Tentukan nama file yang aman dan lokasi sementara
#     secure_name = secure_filename(image_file.filename)
#     temp_image_path = f"./tmp/{secure_name}"
    
#     try:
#         # Pastikan direktori ./tmp ada
#         os.makedirs("./tmp", exist_ok=True)
        
#         # Simpan file sementara
#         image_file.seek(0)
#         image_file.save(temp_image_path)
        
#         # Gunakan Pillow untuk mendapatkan ukuran gambar
#         with Image.open(temp_image_path) as img:
#             img_width, img_height = img.size
            
#             # Hitung rasio aspek gambar
#             aspect_ratio = img_width / img_height
            
#             # Tentukan margin (dalam points)
#             MARGIN = 40
#             max_width = PAGE_WIDTH - (2 * MARGIN)
#             max_height = PAGE_HEIGHT - (2 * MARGIN)
            
#             # Hitung ukuran gambar yang disesuaikan
#             if img_width > max_width or img_height > max_height:
#                 # Jika gambar terlalu lebar
#                 if img_width/max_width > img_height/max_height:
#                     new_width = max_width
#                     new_height = new_width / aspect_ratio
#                 # Jika gambar terlalu tinggi
#                 else:
#                     new_height = max_height
#                     new_width = new_height * aspect_ratio
#             else:
#                 new_width = img_width
#                 new_height = img_height
            
#             # Hitung posisi untuk memusatkan gambar
#             x = (PAGE_WIDTH - new_width) / 2
#             y = (PAGE_HEIGHT - new_height) / 2
            
#             # Tambahkan gambar ke PDF dengan ukuran yang sudah disesuaikan
#             c.drawImage(temp_image_path, x, y, width=new_width, height=new_height)
            
#     except Exception as e:
#         raise RuntimeError(f"Error generating PDF: {e}")
#     finally:
#         # Hapus file sementara
#         if os.path.exists(temp_image_path):
#             os.remove(temp_image_path)
    
#     # Simpan PDF
#     c.save()
#     pdf_buffer.seek(0)
#     return pdf_buffer.read()

# @bp.route('/process-image', methods=['POST'])
# def process_image():
#     try:
#         # Periksa apakah ada file yang dikirim
#         if 'file' in request.files:
#             image_file = request.files['file']
#             image_bytes = image_file.read()
#         elif 'image' in request.json:
#             # Gambar dikirim dalam bentuk base64
#             base64_image = request.json['image']
#             image_bytes = base64.b64decode(base64_image)
#         else:
#             return jsonify({"error": "No image file or base64 image provided"}), 400

#         # Validasi apakah file adalah gambar
#         if not is_image(image_bytes):
#             return jsonify({"error": "Invalid image format. Only PNG, JPG, and HEIC are allowed."}), 400

#         # Proses gambar
#         input_data = preprocess_image(image_bytes)
#         predictions = model.predict(input_data)
#         predicted_label_idx = np.argmax(predictions)
#         confidence = np.max(predictions)

#         # Dapatkan nama label berdasarkan indeks
#         label_name = [k for k, v in label_map.items() if v == predicted_label_idx][0]
#         print(f"Prediksi: {label_name} (Confidence: {confidence:.2f})")

#         label_map = {'document': 0, 'KTP': 1, 'KK': 2, 'SIM': 3}

#         # Tentukan folder berdasarkan label
#         if label_name in ['KTP', 'KK', 'SIM']:
#             folder_name = "Pribadi"
#         else:
#             folder_name = "Lainnya"

#         # Buat PDF
#         pdf_data = generate_pdf(image_file)

#         # Konversi PDF ke Base64 untuk dikembalikan
#         pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

#         # Berikan respons JSON
#         return jsonify({
#             "predicted_label": label_name,
#             "confidence": float(confidence),
#             "pdfData": pdf_base64,
#             "folder_name": folder_name
#         })

#     except Exception as e:
#         logging.error(f"Processing error: {e}")
#         return jsonify({"error": str(e)}), 500
