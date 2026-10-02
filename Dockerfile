FROM node:24-bookworm-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --legacy-peer-deps --ignore-scripts
COPY frontend/ ./
ENV REACT_APP_BACKEND_URL=""
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements-hosting.txt /app/backend/requirements-hosting.txt
RUN pip install --no-cache-dir -r backend/requirements-hosting.txt
COPY backend/ /app/backend/
COPY --from=frontend /app/frontend/build /app/frontend/build
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["sh", "-c", "uvicorn backend.server:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
