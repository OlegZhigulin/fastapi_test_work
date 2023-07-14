FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip3 install -r /app/requirements.txt --no-cache-dir

CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]