FROM python:3.8

WORKDIR /hn-filter
COPY . /hn-filter/
RUN pip install -r requirements.txt

CMD ["python", "server.py"]
