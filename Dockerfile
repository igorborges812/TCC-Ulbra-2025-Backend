FROM python:3.11-alpine

# This prevents Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# This keeps Python from buffering stdin/stdout
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

# Extra dependecies required for psycopg2 package
RUN \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps

COPY . .

RUN ["chmod", "+x", "./docker-entrypoint.sh"]

CMD ["./docker-entrypoint.sh"]
