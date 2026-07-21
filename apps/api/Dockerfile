FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY apps/api /app/apps/api
RUN python -m pip install --no-cache-dir -e '/app/apps/api[agents]'

EXPOSE 8000
CMD ["uvicorn", "retailmind_api.main:app", "--app-dir", "apps/api/src", "--host", "0.0.0.0", "--port", "8000"]
