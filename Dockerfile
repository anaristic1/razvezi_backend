FROM python:3.12.0-slim-bookworm AS builder

RUN mkdir /app

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libcairo2-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

COPY requirements.txt  /app/

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12.0-slim-bookworm

RUN useradd -m -r appuser && \
   mkdir /app && \
   chown -R appuser /app

COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

WORKDIR /app

COPY --chown=appuser:appuser . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER appuser

# Expose the Django port
EXPOSE 8000

# Run Django’s development server
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "razvezi_backend.wsgi:application"]

CMD ["uvicorn", "razvezi_backend.asgi:application", "--host", "0.0.0.0", "--port", "8000"]