#!/usr/bin/env python3

from importlib.metadata import metadata
import os
import json
import db_utils
import utils
from hop import stream, io

log = utils.get_logger(os.path.basename(__file__))

hop_kafka_url = os.getenv('HOP_URL_SOURCE', 1)

start_at = io.StartPosition.EARLIEST
# stream = io.Stream(auth=True, start_at=start_at, until_eos=False)
stream = io.Stream(until_eos=False)
with stream.open(hop_kafka_url, "r") as hop_stream:
    conn = db_utils.DbConnector(
        db_utils.MARIADB_HOSTNAME, db_utils.MARIADB_USER,
        db_utils.MARIADB_PASSWORD, db_utils.MARIADB_DATABASE)
    conn.open_db_connection()

    for message, metadata in hop_stream.read(metadata=True):
        ## Parse headers
        try:
            headers = {}
            for header in metadata.headers:
                headers[header[0]] = header[1].decode('utf-8')
            log.debug(json.dumps(headers))
        except Exception as e:
            log.error(f'''Error parsing headers: "{e}". metadata.headers: {metadata.headers}''')
        ## Construct alert object
        alert = {
            'headers': headers,
            'message': message,
        }
        log.info(f'''Alert: {json.dumps(alert['message'])}''')
        try:
            ## Insert alert data into the database
            if 'sender' in headers and 'schema' in headers \
                and headers['sender'] == 'alert-integration-demo' \
                and headers['schema'] == 'scimma.alert-integration-demo/source/v1':
                conn.insert_photometry_data(message)
            else:
                log.info('Invalid alert message. Skipping...')
                continue
        except Exception as e:
            log.error(f'''Error parsing alert: {e}. Alert: {json.dumps(alert['message'])}''')

    conn.close_db_connection()
