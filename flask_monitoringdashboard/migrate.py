#!/usr/bin/env python3
"""
    Use this file for migrating the Database from v1.X.X to v2.X.X
    Before you can execute this script, change the DB_PATH on line 9.
"""

import sqlite3

DB_PATH = '/home/bogdan/flask_monitoringdashboard_copy.db'

sql_drop_temp = """DROP TABLE IF EXISTS temp"""
sql_drop_fc = """DROP TABLE IF EXISTS functionCalls"""

sql_create_fc_temp = """CREATE TABLE temp(
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    endpoint text,
                                    execution_time real,
                                    time text,
                                    version text,
                                    group_by text,
                                    ip text
                                );"""

sql_copy_into_fc_temp = """INSERT INTO temp 
                            SELECT id, endpoint, execution_time, time, version, group_by, ip 
                            FROM functionCalls"""

sql_create_requests_new = """CREATE TABLE requests(
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    endpoint text,
                                    execution_time real,
                                    time text,
                                    version text,
                                    group_by text,
                                    ip text,
                                    is_outlier integer DEFAULT 0
                                );"""


sql_copy_from_fc_temp = """INSERT INTO requests (id, endpoint, execution_time, time, version, group_by, ip)
                        SELECT id, endpoint, execution_time, time, version, group_by, ip 
                        FROM temp"""


sql_create_rules_temp = """CREATE TABLE temp(
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    endpoint text,
                                    execution_time real,
                                    time text,
                                    version text,
                                    group_by text,
                                    ip text
                                );"""


def update_requests(connection):
    c = connection.cursor()
    c.execute(sql_drop_temp)
    c.execute(sql_create_fc_temp)
    c.execute(sql_copy_into_fc_temp)
    c.execute(sql_drop_fc)
    c.execute(sql_create_requests_new)
    c.execute(sql_copy_from_fc_temp)
    c.execute(sql_drop_temp)
    connection.commit()


def update_rules(connection):
    c = connection.cursor()


def main():
    conn = sqlite3.connect(DB_PATH)
    update_requests(conn)


if __name__ == "__main__":
    main()
