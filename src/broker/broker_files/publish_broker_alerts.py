import os
import time
import db_utils
import utils
from hop import stream, io
from datetime import datetime
import json

log = utils.get_logger(os.path.basename(__file__))

WAIT_TIME = float(os.getenv('ALERT_DATA_PUBLISH_WAIT_TIME', 1.0))
hop_kafka_url = os.getenv('HOP_URL_RESULTS')
stream = io.Stream(auth=True)

conn = db_utils.DbConnector(
    db_utils.MARIADB_HOSTNAME, db_utils.MARIADB_USER,
    db_utils.MARIADB_PASSWORD, db_utils.MARIADB_DATABASE)

## Track latest fetched id of results database records to minimize queries
results_id = 0

with stream.open(hop_kafka_url, "w") as hop_stream:
    while True:
        ## Wait before querying the database
        time.sleep(WAIT_TIME)
        try:
            conn.open_db_connection()
            results = conn.get_results_data(min_id=results_id)
            conn.close_db_connection()
        except Exception as e:
            log.error(f'''Error querying results table: {e}''')
            conn.close_db_connection()
            continue
        try:
            for result in results:
                id = result[0]
                uuid = result[1]
                candidate = result[2]
                ra = result[3]
                dec = result[4]
                time_obs = result[5]
                kn_score = result[6]
                other_score = result[7]
                ## Advance results_id
                if id >= results_id:
                    results_id = id + 1
                ## Publish to hop topic
                alert_message = {
                    'id': uuid,
                    'candidate': candidate,
                    'ra': ra,
                    'dec': dec,
                    'time_obs': time_obs,
                    'kn_score': kn_score,
                    'other_score': other_score,
                }
                log.info(f"Alert published: {json.dumps(alert_message)}")
                hop_stream.write(alert_message)
                ## Separate the alerts in time as desired
                time.sleep(WAIT_TIME)
        except Exception as e:
            log.error(f'''Error publishing alert: {e}''')
