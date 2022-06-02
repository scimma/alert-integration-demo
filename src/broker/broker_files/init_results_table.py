#!/usr/bin/env python3
import os
import db_utils, utils

MARIADB_HOSTNAME = os.getenv('MARIADB_SERVICE_NAME')
MARIADB_DATABASE = os.getenv('MARIADB_DATABASE')
MARIADB_USER = os.getenv('MARIADB_USER')
MARIADB_PASSWORD = os.getenv('MARIADB_PASSWORD')

log = utils.get_logger(os.path.basename(__file__))

conn = db_utils.DbConnector(MARIADB_HOSTNAME, MARIADB_USER,
                            MARIADB_PASSWORD, MARIADB_DATABASE)
conn.open_db_connection()
log.info("Creating results table...")
create_result_table_query = """
CREATE OR REPLACE TABLE results(
    id int(5) NOT NULL AUTO_INCREMENT,
    time FLOAT NOT NULL,
    kn_score FLOAT NOT NULL,
    other_score FLOAT NOT NULL,
    PRIMARY KEY(id)
)
"""
conn.cur.execute(create_result_table_query)
conn.cnx.commit()
conn.close_db_connection()
log.info("Done creating results table.")
