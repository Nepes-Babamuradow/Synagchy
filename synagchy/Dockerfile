# Python 3.12 bazasynda guruýar
FROM python:3.12-slim

# System paketlerini gurnamak (psycopg2 üçin)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Iş katalogyny döretmek
WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# requirements.txt-ni ilki göçürmek (cache üçin)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proýekti göçürmek
COPY . .

# Static files toplamak üçin staticfiles katalogyny döretmegi üpjün et
RUN mkdir -p staticfiles && python manage.py collectstatic --noinput

# Gunicorn bilen işledýärin
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
