FROM python:3.10-slim-bullseye

ARG FASTAPI_SVC_NAME
ARG BENTO_SVC_NAME

ENV BENTO_SVC_NAME ${BENTO_SVC_NAME}
ENV APP_HOME /${FASTAPI_SVC_NAME}/app

RUN apt update && apt -y install git vim curl

COPY ./app ${APP_HOME}
WORKDIR ${APP_HOME}
RUN pip install --upgrade pip && pip install --no-cache -r requirements.txt
EXPOSE 8000
CMD ["main:app", "--workers", "4", "--worker-class", "main.CustomUvicornWorker", "--bind", "0.0.0.0:8000"]
ENTRYPOINT ["gunicorn"]