FROM python:3

COPY driver.py .
COPY ingestion_handler.py .

CMD [ "node", "driver.py" ]