#!/usr/bin/env python3
"""
    Use this file for migrating the Database from v1.X.X to v2.X.X
    Before you can execute this script, change the DB_PATH on line 9.
"""

import sqlite3

DB_PATH = 'path_to_db/flask_monitoringdashboard.db'

sql_drop_temp = """DROP TABLE IF EXISTS temp"""
sql_drop_functionCalls = """DROP TABLE IF EXISTS functionCalls"""

sql_create_temp_table = """CREATE TABLE temp(
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    endpoint text,
                                    execution_time real,
                                    time text,
                                    version text,
                                    group_by text,
                                    ip text
                                );"""

sql_copy_into_temp = """INSERT INTO temp SELECT * FROM functionCalls"""

sql_create_functionCalls_new = """CREATE TABLE functionCalls(
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    endpoint text,
                                    execution_time real,
                                    time text,
                                    version text,
                                    group_by text,
                                    ip text,
                                    is_outlier integer DEFAULT 0
                                );"""


sql_copy_from_temp = """INSERT INTO functionCalls (id, endpoint, execution_time, time, version, group_by, ip)
                        SELECT id, endpoint, execution_time, time, version, group_by, ip 
                        FROM temp"""


def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(sql_drop_temp)
    c.execute(sql_create_temp_table)
    c.execute(sql_copy_into_temp)
    c.execute(sql_drop_functionCalls)
    c.execute(sql_create_functionCalls_new)
    c.execute(sql_copy_from_temp)
    c.execute(sql_drop_temp)
    conn.commit()


if __name__ == "__main__":
    main()
