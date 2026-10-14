# ---BASE IMAGE---
FROM python:3.14-slim

# ---WORKING DIRECTORY---
WORKDIR /app

# ---INSTALL DEPENDENCIES---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---COPY APPLICATION---
COPY main.py .
COPY quota.py .
COPY cleanup.py .

# ---CREATE DATA DIRECTORY---
RUN mkdir -p /app/generated

# ---EXPOSE API PORT---
EXPOSE 8000

# ---START API SERVER---
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]