FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY lab8.py .

EXPOSE 5000

CMD ["python", "lab8.py"]