# -------- Build stage --------
FROM python:3.12-slim AS build

WORKDIR /code

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

COPY . .

FROM python:3.12-slim

WORKDIR /code

COPY --from=build /install /usr/local
COPY --from=build /code /code

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8050
CMD ["gunicorn", "main:app", "-b", "0.0.0.0:8050", "--workers", "1", "--threads", "1", "--timeout", "120"]
