FROM python:3.11-slim as python-base
LABEL authors="wsiddall"
ARG SYNTREND_VERSION="0.0.1"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    APP_PATH="/opt/syntrend"
ENV PATH="$APP_PATH/bin:$PATH"
RUN apt-get update
WORKDIR $APP_PATH
COPY dist/syntrend-${SYNTREND_VERSION}-py3-none-any.whl /opt/
RUN python -m venv $APP_PATH \
    && pip install /opt/syntrend-${SYNTREND_VERSION}-py3-none-any.whl \
    && python -m compileall -r 3 $APP_PATH/lib/python3.11/site-packages/syntrend

ENTRYPOINT ["syntrend"]
