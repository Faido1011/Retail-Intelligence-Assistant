FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Data/ /app/Data/

WORKDIR /app/Data/online+retail

CMD ["python", "agentic_assistant.py"]
