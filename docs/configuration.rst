Configuration
=============
Once you have successfully installed the Flask-MonitoringDashboard using the instructions from 
`the installation page <installation.html>`_, you can use the advanced features by correctly configuring the Dashboard.

Using a configuration file
--------------------------
You can use a single configuration file for all options below.
This is explained in the following section.
In order to configure the Dashboard with a configuration-file, you can use the following function:

.. code-block:: python

   dashboard.config.init_from(file='/<path to file>/config.cfg')

Your app then becomes:

.. code-block:: python

   from flask import Flask
   import flask_monitoringdashboard as dashboard

   app = Flask(__name__)
   dashboard.config.init_from(file='/<path to file>/config.cfg')
   # Make sure that you first configure the dashboard, before binding it to your Flask application
   dashboard.bind(app)
   ...

   @app.route('/')
   def index():
       return 'Hello World!'

   if __name__ == '__main__':
     app.run(debug=True)

Instead of having a hard-coded string containing the location of the config file in the code above, 
it is also possible to define an environment variable that specifies the location of this config file.
The line should then be:

.. code-block:: python

   dashboard.config.init_from(envvar='FLASK_MONITORING_DASHBOARD_CONFIG')

This will configure the Dashboard based on the file provided in the environment variable called `FLASK_MONITORING_DASHBOARD_CONFIG`.

The content of the configuration file
-------------------------------------
Once the setup is complete, a `configuration file`_ (e.g. 'config.cfg') should be set next to the python 
file that contains the entry point of the app. The following properties can be configured:

.. _`configuration file`: https://github.com/flask-dashboard/Flask-MonitoringDashboard/tree/master/config.cfg

.. code-block:: python

   [dashboard]
   APP_VERSION=1.0
   GIT=/<path to your project>/.git/
   CUSTOM_LINK=dashboard
   MONITOR_LEVEL=3
   OUTLIER_DETECTION_CONSTANT=2.5
   SAMPLING_PERIOD=20
   ENABLE_LOGGING=True
   BRAND_NAME=Flask Monitoring Dashboard
   TITLE_NAME=Flask-MonitoringDashboard
   DESCRIPTION=Automatically monitor the evolving performance of Flask/Python web services
   SHOW_LOGIN_BANNER=True
   SHOW_LOGIN_FOOTER=True

   [authentication]
   USERNAME=admin
   PASSWORD=admin
   SECURITY_TOKEN=cc83733cb0af8b884ff6577086b87909

   [database]
   TABLE_PREFIX=fmd
   DATABASE=sqlite:////<path to your project>/dashboard.db

   [visualization]
   TIMEZONE=Europe/Amsterdam
   COLORS={'main':'[0,97,255]',
           'static':'[255,153,0]'}


As can be seen above, the configuration is split into 4 headers:

Dashboard
~~~~~~~~~

- **APP_VERSION:** The version of the application that you use.
  Updating the version allows seeing the changes in the execution time of requests over multiple versions.

- **GIT:** Since updating the version in the configuration-file when updating code isn't very convenient,
  another way is to provide the location of the git-folder. From the git-folder,
  the version is automatically retrieved by reading the commit-id (hashed value).
  The specified value is the location to the git-folder. This is relative to the configuration-file.

- **CUSTOM_LINK:** The Dashboard can be visited at localhost:5000/{{CUSTOM_LINK}}.

- **MONITOR_LEVEL**: The level for monitoring your endpoints. The default value is 3. For more information, see the
  Overview page of the Dashboard.

- **OUTLIER_DETECTION_CONSTANT:** When the execution time is greater than :math:`constant * average`,
  extra information is logged into the database. A default value for this variable is :math:`2.5`.

- **SAMPLING_PERIOD:** Time between two profiler-samples. The time must be specified in ms.
  If this value is not set, the profiler monitors continuously.

- **ENABLE_LOGGING:** Boolean if you want additional logs to be printed to the console. Default
  value is False.

- **BRAND_NAME:** The name displayed in the Dashboard Navbar. Default value is 'Flask Monitoring Dashboard'.

- **TITLE_NAME:** The name displayed in the browser tab. Default value is 'Flask-MonitoringDashboard'.

- **DESCRIPTION:** The text displayed in center of the Dashboard Navbar. Default value is 
  'Automatically monitor the evolving performance of Flask/Python web services'.

- **SHOW_LOGIN_BANNER:** Boolean if you want the login page to show the 'Flask Monitoring Dashboard' logo and title. 
  Default value is True.

- **SHOW_LOGIN_FOOTER:** Boolean if you want the login page to show a link to the official documentation. 
  Default value is True.

Authentication
~~~~~~~~~~~~~~

- **USERNAME** and **PASSWORD:** Must be used for logging into the Dashboard. Both are required.

- **SECURITY_TOKEN:** The token that is used for exporting the data to other services. If you leave this unchanged,
  any service is able to retrieve the data from the database.

Database
~~~~~~~~

- **TABLE_PREFIX:** A prefix to every table that the Flask-MonitoringDashboard uses, to ensure that there are no
  conflicts with the other tables, that are specified by the user of the dashboard.

- **DATABASE:** Suppose you have multiple projects that you're working on and want to separate the results.
  Then you can specify different database_names, such that the result of each project is stored in its own database.

Visualization
~~~~~~~~~~~~~

- **TIMEZONE:** The timezone for converting a UTC timestamp to a local timestamp. For a list of all
  timezones, use the following:

  .. code-block:: python

     import pytz  # pip install pytz
     print(pytz.all_timezones)

  The dashboard saves the time of every request by default in a UTC-timestamp. However, if you want to display
  it in a local timestamp, you need this property.

- **COLORS:** The endpoints are automatically hashed into a color.
  However, if you want to specify a different color for an endpoint, you can set this variable.
  It must be a dictionary with the endpoint-name as a key, and a list of length 3 with the RGB-values. For example:

  .. code-block:: python

     COLORS={'main':'[0,97,255]', 
             'static':'[255,153,0]'}

What have you configured?
-------------------------
We've shown a bunch of configuration settings, but what features are now supported in your Flask
application and how are they related to the config options?
Have a look at `the detailed functionality page <functionality.html>`_ to find the answer.
