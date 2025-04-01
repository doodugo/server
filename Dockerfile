FROM python:3.12-alpine
LABEL maintainer="chlendyd7.com"

WORKDIR /app
EXPOSE 8000

# 시스템 의존성 먼저 설치
RUN apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev gcc python3-dev musl-dev linux-headers

# ARG와 ENV를 올바르게 사용
ARG DEV
ENV DEV=${DEV}

RUN echo "Dev is ${DEV}"  # DEV 환경변수 확인을 위한 출력

# 먼저 requirements 파일들만 복사
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# 나중에 전체 프로젝트 파일 복사
COPY . /app

# Python 의존성 설치
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "True" ]; then \
        /venv/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps

ENV PATH="/venv/bin:$PATH"

USER root

# CMD는 주석 처리된 두 줄 중 하나를 선택
# CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
