FROM apache/airflow:3.0.6

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

COPY requirements.txt .
COPY install_missing.py .

RUN python install_missing.py
