import os
import db_utils, utils
from time import sleep

log = utils.get_logger(os.path.basename(__file__))

while True:
    try:
        conn = db_utils.DbConnector(
            db_utils.MARIADB_HOSTNAME, db_utils.MARIADB_USER,
            db_utils.MARIADB_PASSWORD, db_utils.MARIADB_DATABASE)
        conn.open_db_connection()
        log.info('Database is online!')
        with open('/tmp/db_ready', 'w') as ready_file:
            ready_file.write('Database is ready.')
        break
    except:
        log.info('Waiting for database...')
    sleep(5.0)
