FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install flask tensorflow

CMD ["python", "run.py"]
