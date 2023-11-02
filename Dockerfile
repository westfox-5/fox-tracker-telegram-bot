FROM python:3.8-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY fox_tracker.py .

CMD ["python", "fox_tracker.py"]