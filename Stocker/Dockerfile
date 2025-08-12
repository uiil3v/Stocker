
FROM python:3.12-slim


RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libgobject-2.0-0 \
    libffi-dev \
    libcairo2 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


ENV PORT=8000


RUN python manage.py collectstatic --noinput


CMD ["gunicorn", "Stocker.wsgi:application", "--bind", "0.0.0.0:${PORT}"]
