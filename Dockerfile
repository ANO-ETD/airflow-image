FROM apache/airflow:3.0.6

COPY requirements.txt .
COPY install_missing.py .

RUN python install_missing.py
