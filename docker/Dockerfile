FROM python:3.12-slim

WORKDIR /app

# Install Poetry and the export plugin
RUN pip install --no-cache-dir poetry \
    && pip install --no-cache-dir poetry-plugin-export

# Copy only lockfiles to leverage layer caching
COPY pyproject.toml poetry.lock ./

# Export requirements and install via pip
RUN poetry export \
    --format=requirements.txt \
    --output=requirements.txt \
    --without-hashes \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

EXPOSE 8080
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
