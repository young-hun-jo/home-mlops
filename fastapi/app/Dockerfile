FROM python:3.10-slim-bullseye

ENV APP_HOME /app
RUN apt update && apt -y install git vim curl
COPY . ${APP_HOME}
WORKDIR ${APP_HOME}
RUN pip install --upgrade pip && pip install --no-cache -r requirements.txt
EXPOSE 8000
CMD ["main:app", "--workers", "4", "--worker-class", "main.CustomUvicornWorker", "--bind", "0.0.0.0:8000"]
ENTRYPOINT ["gunicorn"]