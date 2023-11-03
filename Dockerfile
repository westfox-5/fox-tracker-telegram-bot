FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN apt update && apt install -y gcc 
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "fox_tracker.py"]