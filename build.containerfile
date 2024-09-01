FROM python:3.11-slim as python-base
LABEL authors="wsiddall"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTIONS=1 \
    APP_PATH="/opt/syntrend" \
    VENV_PATH="/opt/syntrend/.venv"
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
WORKDIR $APP_PATH
RUN apt-get update && \
    apt-get install --no-install-recommends -y curl build-essential
RUN curl -sSL https://install.python-poetry.org | python3 -
COPY poetry.lock pyproject.toml README.md ./

FROM python-base as build-test
RUN <<EOF
poetry install
for task in lint format unit integration docs coverage; do
  echo "  - ${task}" >> errors
  poe ${task}-test >> errors 2>&1
  echo "  ! ${?}" >> errors
  echo ""
done
cat errors
EOF

FROM python-base as build-run
VOLUME ["/dist"]
RUN poetry install --without=dev && poe build -o /dist
