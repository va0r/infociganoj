FROM python:3.11

LABEL authors="viktorlov"

WORKDIR /code

EXPOSE 8000

COPY ./requirements.txt /code/
RUN pip install -r requirements.txt

COPY . .

RUN pip install python-dotenv
COPY .env /code/

CMD ["sh", "-c", "python3 manage.py migrate"]
