FROM python:3.10.12
WORKDIR /code
RUN pip install --upgrade pip
COPY . .
RUN pip install wheel
RUN pip install -r requirements.txt
CMD gunicorn qoutes_app.wsgi:application --bind 0.0.0.0:8000