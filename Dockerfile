FROM apache/airflow:3.1.0

COPY requirements.txt .
COPY install_missing.py .

RUN python install_missing.py
