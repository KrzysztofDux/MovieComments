FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . .

RUN adduser myuser
USER myuser

CMD gunicorn moviecomments.wsgi:application --bind 0.0.0.0:$PORT
