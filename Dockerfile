# docker build .
FROM python:3.12-alpine
LABEL maintainer="chlendyd7.com"

WORKDIR /app
EXPOSE 8000

# 시스템 의존성 먼저 설치
RUN apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev gcc python3-dev musl-dev linux-headers

ARG DEV=false
ENV DEV=${DEV}

# 먼저 requirements 파일들만 복사
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Python 의존성 설치
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; then \
        /venv/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps

ENV PATH="/venv/bin:$PATH"

USER root

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

