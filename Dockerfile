FROM python:3

COPY driver.py .
COPY ingestion_handler.py .

CMD [ "python3", "driver.py" ]