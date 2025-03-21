# 本番配信用dockerfile
# Stage 1: Build the frontend
FROM node:23-bookworm-slim AS frontend-builder

WORKDIR /app
COPY ./frontend/package.json ./frontend/package-lock.json ./
RUN npm install
COPY ./frontend ./
RUN npm run build

# Stage 2: Build the backend
FROM python:3.11-slim
WORKDIR /app
# Install dependencies for OpenCV
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0
COPY ./backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
RUN mkdir -p /app/captureImage && chmod -R 777 /app/captureImage

# Copy the frontend build artifacts from the frontend-builder stage
COPY --from=frontend-builder /app/dist /app/frontend/dist

# Copy the backend source code
COPY ./backend/src /app/src

# Start the FastAPI application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]