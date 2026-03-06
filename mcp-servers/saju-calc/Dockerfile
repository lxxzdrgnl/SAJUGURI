FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml .

# Install dependencies (no dev group)
RUN uv sync --no-dev

# Copy source
COPY . .

EXPOSE 8000

# Run FastMCP in HTTP/SSE mode
CMD ["uv", "run", "fastmcp", "run", "main.py", "--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]
