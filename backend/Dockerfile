# Dibangun dari root repo (context: .) supaya engine/, models/, dan data/results/ ikut masuk image.
FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY engine engine
COPY backend backend
COPY models/v1 models/v1
COPY data/results data/results
RUN mkdir -p logs
EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
