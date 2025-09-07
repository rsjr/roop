FROM python:3.13-slim

WORKDIR /app

# Install dependencies directly
RUN pip install fastapi uvicorn[standard] sqlalchemy asyncpg psycopg2-binary

# Copy only the app code
COPY app/ ./app/

# Simple run command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]