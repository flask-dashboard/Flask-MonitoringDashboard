Configuration
=============
Once you have successfully installed the Flask Monitoring Dashboard with information from 
`this page <installation.html>`_, you can use the advanced features by correctly configuring the Dashboard.

Using a configuration file
--------------------------
You can use a single configuration file for all options below.
This is explained in the following section.
In order to configure the Dashboard with a configuration-file, you can use the following function:

.. code-block:: python

   dashboard.config.init_from(file='/<path to file>/config.cfg')

Thus, it becomes:

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

Instead of having a hard-coded string containing the location of the config file in the code above, it is also possible
to define an environment variable that specifies the location of this config file.
The line should then be:

.. code-block:: python

   dashboard.config.init_from(envvar='DASHBOARD_CONFIG')

This will configure the Dashboard based on the file provided in the environment variable called `DASHBOARD_CONFIG`.

The content of the configuration file
-------------------------------------
Once the setup is complete, a configuration file (e.g. 'config.cfg') should be set next to the python file that 
contains the entry point of the app. The following things can be configured:

.. code-block:: python

   [dashboard]
   APP_VERSION=1.0
   CUSTOM_LINK=dashboard
   DATABASE=sqlite:////<path to your project>/dashboard.db
   TIMEZONE='Europe/Amsterdam'
   USERNAME=admin
   PASSWORD=admin
   GUEST_USERNAME=guest
   GUEST_PASSWORD=['dashboardguest!', 'second_pw!']
   GIT=/<path to your project>/.git/
   OUTLIER_DETECTION_CONSTANT=2.5
   DASHBOARD_ENABLED = True
   TEST_DIR=/<path to your project>/tests/
   COLORS={'main':'[0,97,255]',
           'static':'[255,153,0]'}

This might look a bit overwhelming, but the following list explains everything in detail:

- **APP_VERSION:** The version of the application that you use.
  Updating the version helps in showing differences in execution times of a function over a period of time.

- **CUSTOM_LINK:** The Dashboard can be visited at localhost:5000/{{CUSTOM_LINK}}.

- **DATABASE:** Suppose you have multiple projects where you're working on and want to separate the results.
  Then you can specify different database_names, such that the result of each project is stored in its own database.

- **TIMEZONE:** The timezone for converting a UTC timestamp to a local timestamp. For a list of all
  timezones, use the following:

  .. code-block:: python

     import pytz  # pip install pytz
     print(pytz.all_timezones)

  The dashboard saves the time of every request by default in a UTC-timestamp. However, if you want to display
  it in a local timestamp, you need this property.

- **USERNAME** and **PASSWORD:** Must be used for logging into the Dashboard.
  Thus both are required.

- **GUEST_USERNAME** and **GUEST_PASSWORD:** A guest can only see the results, but cannot configure/download any data.

- **GIT:** Since updating the version in the configuration-file when updating code isn't very useful,
  it is a better idea to provide the location of the git-folder.
  From the git-folder,
  The version is automatically retrieved by reading the commit-id (hashed value).
  The location is relative to the configuration-file.

- **OUTLIER_DETECTION_CONSTANT:** When the execution time is more than this :math:`constant * average`,
  extra information is logged into the database.
  A default value for this variable is :math:`2.5`.

- **OUTLIERS_ENABLED:** Whether you want to collect information about outliers. If you set this to true,
  the expected overhead of the Dashboard is a bit larger, as you can find
  `here <https://github.com/flask-dashboard/Testing-Dashboard-Overhead>`_.

- **TEST_DIR:** Specifies where the unit tests reside. This will show up in the configuration in the Dashboard.

- **COLORS:** The endpoints are automatically hashed into a color.
  However, if you want to specify a different color for an endpoint, you can set this variable.
  It must be a dictionary with the endpoint-name as a key, and a list of length 3 with the RGB-values. For example:

  .. code-block:: python

     COLORS={'main':'[0,97,255]', 
             'static':'[255,153,0]'}

What have you configured?
-------------------------
A lot of configuration options, but you might wonder what functionality is now supported in your Flask application?
Have a look at `this file <functionality.html>`_ to find the answer.
