###############################################
# Base Image
###############################################
FROM python:3.10-slim as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.1.13 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/app/backend" \
    VENV_PATH="/app/backend/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

###############################################
# Backend Builder Image
###############################################
FROM --platform=$BUILDPLATFORM python-base as backend-builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

# copy project requirement files here to ensure they will be cached.
WORKDIR /app/backend
COPY src/backend/poetry.lock src/backend/pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --no-dev

###############################################
# Frontend Builder Image
###############################################
FROM --platform=$BUILDPLATFORM node:17 as frontend-builder-base

# copy project requirement files here to ensure they will be cached.
WORKDIR /app/frontend

# install runtime deps
COPY src/frontend/package.json src/frontend/package-lock.json ./
RUN npm install

COPY src/frontend /app/frontend

RUN npm run build

###############################################
# Production Image
###############################################
FROM --platform=$BUILDPLATFORM python-base as production

WORKDIR /app

COPY ./src/backend /app/backend
COPY --from=backend-builder-base $PYSETUP_PATH /app/backend

COPY --from=frontend-builder-base /app/frontend/dist /app/frontend/dist

WORKDIR /app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]