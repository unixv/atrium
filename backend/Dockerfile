FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY atrium ./atrium
CMD ["python", "-m", "atrium.main"]
