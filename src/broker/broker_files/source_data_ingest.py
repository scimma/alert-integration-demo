#!/usr/bin/env python3

import os
import json
import db_utils
import utils
from hop import stream, io

log = utils.get_logger(os.path.basename(__file__))

hop_kafka_url = os.getenv('HOP_URL_SOURCE')

start_at = io.StartPosition.LATEST
stream = io.Stream(auth=True, start_at=start_at, until_eos=False)
with stream.open(hop_kafka_url, "r") as hop_stream:
    conn = db_utils.DbConnector(
        db_utils.MARIADB_HOSTNAME, db_utils.MARIADB_USER,
        db_utils.MARIADB_PASSWORD, db_utils.MARIADB_DATABASE)
    conn.open_db_connection()

    for message, metadata in hop_stream.read(metadata=True):
        alert = {
            'metadata': metadata,
            'message': message,
        }
        log.info(f'''alert: {json.dumps(alert)}''')
        try:
            if 'sender' in metadata and 'schema' in metadata \
                and metadata['sender'] == 'alert-integration-demo' \
                and metadata['schema'] == 'scimma.alert-integration-demo/v1':
                ## Insert alert data into the database
                conn.insert_photometry_data(message)
        except Exception as e:
            log.error(f'''Error parsing alert: {e}''')

    conn.close_db_connection()
