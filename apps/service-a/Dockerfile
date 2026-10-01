FROM python:3.12-alpine

WORKDIR /app

COPY src/app.py .

ENV SERVICE_NAME=service-a

EXPOSE 8080

CMD ["python", "app.py"]