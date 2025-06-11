FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set port
EXPOSE 8050

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "app:create_app()"] 