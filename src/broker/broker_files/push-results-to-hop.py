#!/usr/bin/env python3
import os
import time

import numpy as np
from hop import Stream
from hop.auth import Auth

import db_utils

hop_auth = Auth(os.getenv('HOP_USERNAME'), os.getenv('HOP_PASSWORD'))
hop_stream = Stream(auth=hop_auth)

s = hop_stream.open("kafka://kafka.scimma.org/circuses-demo.alert-integration-results", "w")

conn = db_utils.DbConnector(
    db_utils.MARIADB_HOSTNAME, db_utils.MARIADB_USER,
    db_utils.MARIADB_PASSWORD, db_utils.MARIADB_DATABASE)
conn.open_db_connection()

timeout = time.time() + 100

previous_max_id = 0
while time.time() < timeout:
    # FIXME not good practice
    conn.cur.execute(
        f"SELECT * FROM results WHERE id > {previous_max_id}"
    )
    new_data_raw = [
        dict((conn.cur.description[i][0], value)
        for i, value in enumerate(row)) for row in conn.cur.fetchall()] 
    
    for data in new_data_raw:
        s.write(data)
    # read using
    # hop subscribe kafka://kafka.scimma.org/circuses-demo.alert-integration-result
    conn.cur.execute(
        """SELECT MAX(id) FROM results"""
    )
    previous_max_id, = conn.cur.fetchall()[0]
    print(new_data_raw, flush=True)
    print(previous_max_id, flush=True)
    time.sleep(10)

s.close()