FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install -q --no-cache-dir -r requirements.txt

COPY . .
RUN pytest --cov=.

CMD [ "python", "./main.py" ]
