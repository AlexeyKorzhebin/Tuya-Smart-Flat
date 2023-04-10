FROM python:3.10

WORKDIR /home/app
RUN mkdir /var/log/smartflat


COPY main.py .
COPY requirements.txt .
COPY snapshot.json .
COPY devices.json .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]