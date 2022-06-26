import os
import time
import utils
from hop import stream, io
from datetime import datetime
import json

log = utils.get_logger(os.path.basename(__file__))

WAIT_TIME = float(os.getenv('SOURCE_DATA_PUBLISH_WAIT_TIME', 0.01))
hop_kafka_url = os.getenv('HOP_URL_SOURCE')

stream = io.Stream(auth=True)
with stream.open(hop_kafka_url, "w") as hop_stream:
    # get all DECam data and sort it
    decam_g_band, decam_r_band, decam_i_band = utils.get_photometry('DECam')
    decam_data = sorted(decam_g_band + decam_r_band + decam_i_band, key=lambda e: e['time'])
    log.info("Publishing source alerts")
    # headers = {
    #     'sender': 'alert-integration-demo',
    #     'time': f'{datetime.utcnow()}',
    #     'schema': 'scimma.alert-integration-demo/v1',
    # }
    ## Iterate over all data points and publish them as hop messages
    for num, data in enumerate(decam_data, 1):
        alert = {
            'time': float(data['time']),
            'magnitude': float(data['magnitude']),
            'e_magnitude': float(data['e_magnitude']),
            'band': data['band'],
            'candidate': 'GW170817',
            'ra': float(utils.gw_170817_coord.ra.deg),
            'dec': float(utils.gw_170817_coord.dec.deg),
        }
        ## Publish to hop topic
        # hop_stream.write(alert, headers=headers)
        hop_stream.write(alert)
        if num % 100 == 0:
            log.info(f"Alert published: {json.dumps(alert)}")
            log.info("Published %s source alerts" % (num,))
        ## Separate the alerts in time as desired
        time.sleep(WAIT_TIME)
