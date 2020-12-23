FROM python:3.8.7-slim-buster as builder
RUN pip install PyPtt

FROM builder
WORKDIR /app
CMD ["python", "main.py"]