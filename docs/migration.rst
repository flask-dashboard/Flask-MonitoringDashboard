Migration
=========

Migrating from 1.X.X to 2.0.0
-----------------------------
Version 2.0.0 offers a lot more functionality, including Request- and Endpoint-profiling.

There are two migrations that you have to do, before you can use version 2.0.0.

1. **Migrate the database:** Since version 2.0.0 has a different database scheme, the 
   Flask-MonitoringDashboard cannot automatically migrate to this version.

   We have created a script for you that can achieve this. It migrates the data in the existing 
   database into a new database, without removing the existing database.

   You can find `the migration script here`_.

   .. _`the migration script here`: https://github.com/flask-dashboard/Flask-MonitoringDashboard/tree/master/migration/migrate_v1_to_v2.py

   If you want to run this script, you need to be aware of the following:

   - If you already have version 1.X.X of the Flask-MonitoringDashboard installed, first update to 
     2.0.0 before running this script. You can update a package by:

     .. code-block:: bash
 
        pip install flask_monitoringdashboard --upgrade

   - set **OLD_DB_URL** on line 16, such that it points to your existing database.

   - set **NEW_DB_URL** on line 17, to a new database name version. Note that they can't be the same.

   - Once you have migrated your database, you have to update the database location in your configuration-file.


2. **Migrate the configuration file**: You also have to update the configuration file completely, since we've 
   re factored this to make it more clear. The main difference is that several properties have been re factored
   to a new header-name. 

   For an example of a new configuration file, see `this configuration file`_.

   .. _`this configuration file`: https://github.com/flask-dashboard/Flask-MonitoringDashboard/tree/master/config.cfg


Migrating from 2.X.X to 3.0.0
-----------------------------
Version 3.0.0 adds functionality for tracking return status codes for each endpoint.

This requires a minimal change to the database: adding the 'status_code' (INT) field to the Request table.

You can add the field by hand, or you can run `the corresponding migration script`_:

   .. _`the corresponding migration script`: https://github.com/flask-dashboard/Flask-MonitoringDashboard/tree/master/migration/migrate_v2_to_v3.py

