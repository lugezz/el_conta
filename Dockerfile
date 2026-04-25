FROM python:3.14-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working dir
WORKDIR /app

# Git commit hash (for versioning)
ARG GIT_COMMIT=unknown
ENV GIT_COMMIT=$GIT_COMMIT

# Install system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    bash \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (for caching)
COPY pyproject.toml uv.lock ./

# Install Python deps using uv
# Place venv outside /app to avoid being masked by the docker-compose volume mount (./el_conta:/app)
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
RUN uv sync --frozen --dev

# Extract app version from pyproject.toml and store outside /app so it survives the volume mount
RUN python -c "import tomllib; fh=open('pyproject.toml','rb'); v=tomllib.load(fh)['project']['version']; fh.close(); open('/usr/local/etc/app_version','w').write(v)"

# Put the virtual environment binaries on PATH
ENV PATH="/opt/venv/bin:$PATH"

# Copy the project (copy script first for caching and to avoid being masked by later COPY)
COPY . .
COPY --chmod=755 dev/server/devserver.sh /devserver.sh

CMD ["bash", "/devserver.sh"]
