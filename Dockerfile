FROM python:3.11-slim
# Use the official Python base image

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for psycopg2 (PostgreSQL) and Poetry
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Configure Poetry to not create virtual environments (we're already in a container)
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Install dependencies using Poetry
# --no-root: Don't install the project itself, just dependencies
# --only main: Only install main dependencies, not dev dependencies (for production)
RUN poetry install --no-root --only main && rm -rf $POETRY_CACHE_DIR

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
