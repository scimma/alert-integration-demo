#!/usr/bin/env python3
print("Inserting data from DECam to photometry table...")

import os, time

import utils, db_utils


MARIADB_HOSTNAME = os.getenv('MARIADB_SERVICE_NAME')
MARIADB_DATABASE = os.getenv('MARIADB_DATABASE')
MARIADB_USER = os.getenv('MARIADB_USER')
MARIADB_PASSWORD = os.getenv('MARIADB_PASSWORD')

WAIT_TIME = 0.1

conn = db_utils.DbConnector(MARIADB_HOSTNAME, MARIADB_USER,
                            MARIADB_PASSWORD, MARIADB_DATABASE)
conn.open_db_connection()

# get all data and sort it
decam_g_band, decam_r_band, decam_i_band = utils.get_photometry('DECam')
decam_data = sorted(decam_g_band + decam_r_band + decam_i_band,
                    key=lambda e: e['time'])

# for data in decam_data:
#     assert conn.photometry_table_cols.issubset(set(data))
#     conn.insert_photometry_data(
#         {k:data[k] for k in conn.photometry_table_cols})
#     time.sleep(WAIT_TIME)