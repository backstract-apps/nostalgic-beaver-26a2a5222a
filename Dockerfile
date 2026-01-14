# Use the official Backstract Python slim image for the build
FROM kathyrussells/backstract-python-app:slim3.11

WORKDIR /usr/src/app

# To use env locally, rename .env.example to .env
# COPY .env to .env
COPY .env.example .env

# Copy and install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copy the project files
COPY . .

# Run the application
#CMD ["gunicorn", "main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
CMD ["gunicorn", "main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:7070"]
