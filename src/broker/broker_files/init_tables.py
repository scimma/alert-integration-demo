#!/usr/bin/env python3
import os
import db_utils, utils

log = utils.get_logger(os.path.basename(__file__))

conn = db_utils.DbConnector(
    db_utils.MARIADB_HOSTNAME, db_utils.MARIADB_USER,
    db_utils.MARIADB_PASSWORD, db_utils.MARIADB_DATABASE)
conn.open_db_connection()
log.info("Creating photometry table...")
create_phot_table_query = """
CREATE OR REPLACE TABLE photometry(
    id int(5) NOT NULL AUTO_INCREMENT,
    time FLOAT NOT NULL,
    magnitude FLOAT NOT NULL,
    e_magnitude FLOAT NOT NULL,
    band CHAR(1) NOT NULL, PRIMARY KEY(id)
)
"""
conn.cur.execute(create_phot_table_query)
conn.cnx.commit()
conn.close_db_connection()
log.info("Done creating photometry table.")