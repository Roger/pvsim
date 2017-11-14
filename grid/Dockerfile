FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -q -r requirements.txt

COPY . .
RUN pytest --cov=.

CMD [ "python", "./main.py" ]
