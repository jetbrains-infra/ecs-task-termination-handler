FROM python:3-alpine

# Install curl and certificates
RUN apk add --no-cache curl openssl ca-certificates

COPY docker-entrypoint.py /
COPY requirements.txt /

RUN pip install -r /requirements.txt

ENTRYPOINT ["python", "-u", "docker-entrypoint.py"]
