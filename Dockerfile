FROM python:3.9-slim

WORKDIR /app

# Salin file ke dalam container
COPY . /app

# Install dependensi
RUN pip install --no-cache-dir -r requirements.txt

# Jalankan aplikasi
CMD ["python", "run.py"]
