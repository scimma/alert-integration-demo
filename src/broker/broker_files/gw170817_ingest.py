#!/usr/bin/env python3

import os, time
import db_utils, utils

## Simulate the database being populated by incoming source alerts
## by waiting some time between successive database inserts
INGEST_WAIT_TIME = float(os.getenv('INGEST_WAIT_TIME', 0.01))

log = utils.get_logger(os.path.basename(__file__))

conn = db_utils.DbConnector(
    db_utils.MARIADB_HOSTNAME, db_utils.MARIADB_USER,
    db_utils.MARIADB_PASSWORD, db_utils.MARIADB_DATABASE)
conn.open_db_connection()

# get all data and sort it
decam_g_band, decam_r_band, decam_i_band = utils.get_photometry('DECam')
decam_data = sorted(decam_g_band + decam_r_band + decam_i_band, key=lambda e: e['time'])
log.info("Inserting data into photometry table")
for num, data in enumerate(decam_data, 1):
    # log.info(f'''decam data: {data}''')
    # assert conn.photometry_table_cols.issubset(set(data))
    datum = {
        'time': float(data['time']),
        'magnitude': float(data['magnitude']),
        'e_magnitude': float(data['e_magnitude']),
        'band': data['band'],
        'candidate': 'GW170817',
        'ra': float(utils.gw_170817_coord.ra.deg),
        'dec': float(utils.gw_170817_coord.dec.deg),
    }
    # log.info(f'''decam datum: {datum}''')
    conn.insert_photometry_data(datum)
    time.sleep(INGEST_WAIT_TIME)
    if num % 100 == 0:
        log.info("Inserted %s entries" % (num,))

conn.close_db_connection()
