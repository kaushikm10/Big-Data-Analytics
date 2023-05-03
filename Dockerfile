FROM python:3.8-slim-buster

COPY . /Big-Data-Analytics

RUN pip install --upgrade pip

WORKDIR /Big-Data-Analytics

RUN pip install -r requirements.txt

EXPOSE 5000


CMD ["python", "app.py" ]

