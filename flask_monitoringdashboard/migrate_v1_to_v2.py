#!/usr/bin/env python3
"""
    Use this file for migrating the Database from v1.X.X to v2.X.X
    Before you can execute this script, change the DB_PATH on line 9.
"""

import sqlite3

DB_PATH = '/home/bogdan/flask_monitoringdashboard.db'
# DB_PATH = '/home/bogdan/school_tmp/RI/stacktrace_view/flask-dashboard_copy.db'

sql_drop_temp = """DROP TABLE IF EXISTS temp"""
sql_drop_fc = """DROP TABLE IF EXISTS functionCalls"""
sql_drop_rules = """DROP TABLE IF EXISTS rules"""

sql_create_fc_temp = """CREATE TABLE temp(
                                    id integer PRIMARY KEY,
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
                                    id integer PRIMARY KEY,
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
                                    endpoint text PRIMARY KEY,
                                    monitor text,
                                    time_added text,
                                    version_added text,
                                    last_accessed text
                                );"""

sql_copy_into_rules_temp = """INSERT INTO temp 
                            SELECT endpoint, monitor, time_added, version_added, last_accessed 
                            FROM rules"""

sql_create_rules_new = """CREATE TABLE rules(
                                    endpoint text PRIMARY KEY,
                                    monitor_level integer,
                                    time_added text,
                                    version_added text,
                                    last_accessed text
                                );"""

sql_copy_from_rules_temp = """INSERT INTO rules (endpoint, monitor_level, time_added, version_added, last_accessed)
                        SELECT endpoint, monitor, time_added, version_added, last_accessed 
                        FROM temp"""


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
    c.execute(sql_drop_temp)
    c.execute(sql_create_rules_temp)
    c.execute(sql_copy_into_rules_temp)
    c.execute(sql_drop_rules)
    c.execute(sql_create_rules_new)
    c.execute(sql_copy_from_rules_temp)
    c.execute(sql_drop_temp)
    connection.commit()


def main():
    conn = sqlite3.connect(DB_PATH)
    update_requests(conn)
    update_rules(conn)


if __name__ == "__main__":
    main()
