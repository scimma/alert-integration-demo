#!/usr/bin/env python3

import os
import db_utils

print("Initializing tables...")

MARIADB_HOSTNAME = os.getenv('MARIADB_SERVICE_NAME')
MARIADB_DATABASE = os.getenv('MARIADB_DATABASE')
MARIADB_USER = os.getenv('MARIADB_USER')
MARIADB_PASSWORD = os.getenv('MARIADB_PASSWORD')


conn = db_utils.DbConnector(MARIADB_HOSTNAME, MARIADB_USER,
                            MARIADB_PASSWORD, MARIADB_DATABASE)
conn.open_db_connection()

create_phot_table_query = """CREATE OR REPLACE TABLE photometry (id int(5) NOT NULL AUTO_INCREMENT, mjd FLOAT NOT NULL, mag FLOAT NOT NULL, mag_err FLOAT NOT NULL, upper_lim BOOL NOT NULL, PRIMARY KEY(id))"""

conn.cur.execute(create_phot_table_query)
conn.cnx.commit()
