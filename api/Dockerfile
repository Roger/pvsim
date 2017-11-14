FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install -q --no-cache-dir -r requirements.txt

COPY . .

CMD gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 -b 0.0.0.0:4242 main:app
