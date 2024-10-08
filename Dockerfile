FROM python:3.11-alpine

# This prevents Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# This keeps Python from buffering stdin/stdout
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["/src/docker-entrypoint.sh", "-n"]
