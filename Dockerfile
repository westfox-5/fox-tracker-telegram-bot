FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "fox_tracker.py"]