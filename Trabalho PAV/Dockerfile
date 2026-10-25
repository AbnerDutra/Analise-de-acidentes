FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY projeto_API/requeriments.txt ./requeriments.txt
RUN pip install --no-cache-dir -r requeriments.txt

COPY projeto_API ./projeto_API

EXPOSE 8000

CMD ["uvicorn", "projeto_API.app:app", "--host", "0.0.0.0", "--port", "8000"]
