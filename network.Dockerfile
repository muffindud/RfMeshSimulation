FROM python:3.13-alpine

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
RUN apk add graphviz

COPY . .

CMD ["python3", "network.py"]
