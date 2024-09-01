FROM python:3.11-slim as python-base
LABEL authors="wsiddall"

ARG WHL_PACKAGE="syntrend.whl"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    APP_PATH="/opt/syntrend" \
    VENV_PATH="/opt/syntrend/.venv"
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
WORKDIR $APP_PATH
RUN apt-get update && \
    apt-get install --no-install-recommends -y curl build-essential

FROM python-base as run
COPY $WHL_PACKAGE /opt/syntrend.whl
RUN python -m pip install $APP_PATH/dist/syntrend.whl

ENTRYPOINT ["syntrend"]
