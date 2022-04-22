import csv
import re
import json
from sys import stderr, argv
from os.path import join, isfile
from ingestion_handler import V2Handler
import requests
from codecs import iterdecode
from os import getenv

token = getenv("TOKEN")
file = getenv("MSG")

#token should be passed as a default env var to container
tapis_config = {
    "tenant_url": "https://agaveauth.its.hawaii.edu/meta/v2/data",
    "token": token,
    "retry": 3,
    "db_write_api_url": "https://cistore.its.hawaii.edu"
}
prop_translations = {
    "SKN": "skn",
    "Station.Name": "name",
    "Observer": "observer",
    "Network": "network",
    "Island": "island",
    "ELEV.m.": "elevation_m",
    "LAT": "lat",
    "LON": "lng",
    "NCEI.id": "ncei_id",
    "NWS.id": "nws_id",
    "NESDIS.id": "nesdis_id",
    "SCAN.id": "scan_id",
    "SMART_NODE_RF.id": "smart_node_rf_id"
}
nodata = "NA"
id_field = "skn"
station_group = "hawaii_climate_primary"

tapis_handler = V2Handler(tapis_config)

def handle_file(reader):
    header = None
    for row in reader:
        if header is None:
            header = row
            for i in range(len(header)):
                prop = header[i]
                trans = prop_translations.get(prop)
                if trans is not None:
                    header[i] = trans
                if header[i] == id_field:
                    station_id_index = i
        else:
            data = {
                "station_group": station_group,
                "id_field": id_field,
            }
            for i in range(len(row)):       
                prop = header[i]
                value = row[i]
                if value != nodata:
                    data[prop] = value

            doc = {
                "name": "hcdp_station_metadata",
                "value": data
            }
            key_fields = ["station_group", id_field]
            print(doc)
            # tapis_handler.create_check_duplicates(doc, key_fields, replace = True)



##################################
##################################

#file should be changed to come from whatever env variable the message is passed to
if isfile(file):
    with open(file, "r") as fd:
        reader = csv.reader(fd)
        handle_file(reader)
else:
    with requests.get(file, stream = True) as res:
        res.raise_for_status()
        lines = iterdecode(res.iter_lines(), "utf-8")
        reader = csv.reader(lines)
        handle_file(reader)

##################################
##################################


print("Complete!")
                        