# 1. Base image & unbuffered output
FROM python:3.11-slim AS base
ENV PYTHONUNBUFFERED=1

# 2. Set working dir
WORKDIR /app

# 3. Copy & install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 4. Copy your application code
COPY . .

# 5. Create a non-root user for security
RUN useradd --create-home appuser \
    && chown -R appuser /app
USER appuser

# 6. Expose the port
EXPOSE 8000

# 7. Default command—note module path points at app/main.py
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
