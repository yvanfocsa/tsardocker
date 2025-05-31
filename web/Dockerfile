FROM python:3.12-slim

WORKDIR /app

# 1. Déps système
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      gcc python3-dev build-essential wkhtmltopdf && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 2. Déps Python
COPY web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir transformers torch

# 3. Code
COPY web/ /app
COPY modules/ /app/modules

# 4. Env & ports
ENV FLASK_APP=app:create_app \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=5373
EXPOSE 5373

# 5. Lancement
CMD ["flask", "run", "--reload"]
