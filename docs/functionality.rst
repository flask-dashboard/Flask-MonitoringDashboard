Detailed Functionality
======================
The functionality of the Dashboard is divided into 4 main components.
You can find detailed information about every component below:

Endpoint Monitoring
-------------------
The core functionality of the Dashboard is monitoring which Endpoints are heavily used and which are not.
If you have successfully configured the Dashboard from `this page <configuration.html>`_, then you are ready to use it.
In order to monitor a number of endpoints, you have to do the following:

1. Log into the Dashboard at: http://localhost:5000/dashboard/login

2. Go to the Rules-tab in the left menu: http://localhost:5000/dashboard/rules

3. Select the rules that you want to monitor.

4. Wait until a request to this endpoint is being made.

5. Go to the Dashboard Overview in the left menu: http://localhost:5000/measurements/overview

Collected data
~~~~~~~~~~~~~~
For each request that is being to a monitored endpoint, the following data is recorded:

- **Execution time:** measured in ms.

- **Time:** the current timestamp of when the request is being made.

- **Version:** the version of the Flask-application.
  This can either be retrieved via the `CUSTOM_VERSION` value, or via the `GIT` value.
  If both are configured, the `GIT` value is used.

- **group_by:** An option to group the collected results.
  As most Flask applications have some kind of user management,
  this variable can be used to track the performance between different users.
  It is configured using the following command:

  .. code-block:: python

     def get_user_id():
         return 1234  # replace with a function to retrieve the id of the
                        # user within a request.

     dashboard.config.group_by = get_user_id
     # Note that the function itself is passed, not the result of the function.

  Thus, it becomes:

  .. code-block:: python

     from flask import Flask
     import flask_monitoringdashboard as dashboard

     app = Flask(__name__)
     dashboard.config.init_from(file='/<path to file>/config.cfg')

     def get_user_id():
         return '1234'  # replace with a function to retrieve the id of the
                        # user within a request.

     dashboard.config.group_by = get_user_id
     dashboard.bind(app)

     @app.route('/')
     def index():
         return 'Hello World!'

     if __name__ == '__main__':
         app.run(debug=True)

  The group_by-function must be a function that either returns a primitive (bool, bytes, float, int, str), or a function, or a tuple/list. Below is a list with a few valid examples:

  +---------------------------------------------------------------------------------------------+--------------------------------+
  | Code                                                                                        | Result                         |
  +=============================================================================================+================================+
  | dashboard.config.group_by = lambda: 3                                                       | 3                              |
  +---------------------------------------------------------------------------------------------+--------------------------------+
  | dashboard.config.group_by = lambda: ('User', 3)                                             | (User,3)                       |
  +---------------------------------------------------------------------------------------------+--------------------------------+
  | dashboard.config.group_by = lambda: lambda: 3                                               | 3                              |
  +---------------------------------------------------------------------------------------------+--------------------------------+
  | dashboard.config.group_by = ('User', lambda: 3)                                             | (User,3)                       |
  +---------------------------------------------------------------------------------------------+--------------------------------+
  | dashboard.config.group_by = lambda: 'username'                                              | username                       |
  +---------------------------------------------------------------------------------------------+--------------------------------+
  | dashboard.config.group_by = lambda: ['Username', 'username']                                | (Username,username)            |
  +---------------------------------------------------------------------------------------------+--------------------------------+
  | dashboard.config.group_by = lambda: [('User', lambda: 3), ('Username', lambda: 'username')] | ((User,3),(Username,username)) |
  +---------------------------------------------------------------------------------------------+--------------------------------+

- **IP:** The IP-address from which the request is made. The IP is retrieved by the following code:

.. code-block:: python

     from flask import request
     print(request.environ['REMOTE_ADDR'])

Observations
~~~~~~~~~~~~
Using the collected data, a number of observations can be made:

- Is there a difference in execution time between different versions of the application?

- Is there a difference in execution time between different users of the application?

- Is there a difference in execution time between different IP addresses?
  *As tracking the performance between different users requires more configuration, this can be a quick alternative.*

- On which moments of the day does the Flask application process the most requests?

- What are the users that produce the most requests?

- Do users experience different execution times in different version of the application?

Monitoring Unit Test Performance
------------------------
In addition to monitoring the performance of a live deployed version of some web service,
the performance of such a web service can also be monitored by making use of its unit tests.
This of course assumes that several unit tests were written for the web service project it concerns.
Also, since this monitoring should be done in an automated way, a Travis setup for the project is a prerequisite.

To enable Travis to run your unit tests and send the obtained results to the Dashboard, two steps have to be taken:

1. In the `setup.py` file of your web service, the Dashboard has to be added as a requirement:

    .. code-block:: python

       install_requires=('flask_monitoringdashboard')

2. In the `.travis.yml` file, a script command has to be added:

    .. code-block:: bash

       python -m flask_monitoringdashboard.collect_performance \
       --test_folder=./tests \
       --times=5 \
       --url=https://yourdomain.org/dashboard

The `test_folder` argument specifies where the performance collection process can find the unit tests to use.
The `times` argument (optional, default: 5) specifies how many times to run each of the unit tests.
The `url` argument (optional) specifies where the Dashboard is that needs to receive the performance results.
When the last argument is omitted, the performance testing will run, but without publishing the results.

Now Travis will monitor the performance of the unit tests automatically after every commit that is made.
These results will then show up in the Dashboard, under 'Testmonitor'.
Here, all tests that have been run will show up, along with the endpoints of the web service that they test.
Visualizations of the performance evolution of the unit tests are also available here.
This may give the developer of the web service insight in the expected performance change when the new version of the
web service should be deployed.

Outliers
--------
It is useful to investigate why certain requests take way longer to process than other requests.
If this is the case, a request is seen as an outlier.
Mathematically an outlier is determined if the execution of the request is longer than:

:math:`> average * constant`

Where `average` is the average execution time per endpoint, and `constant` is given in the configuration by OUTLIER_DETECTION_CONSTANT
(its default value is :math:`2.5`).

When a request is an outlier, the Dashboard stores more information, such as:

- The stack-trace in which it got stuck.

- The percentage of the CPU's that are in use.

- The current amount of memory that is used.

- Request values.

- Request headers.

- Request environment.

The data that is collected from outliers, can be seen by the following procedure:

1. Go to the Dashboard Overview: http://localhost:5000/measurements/overview

2. Click on the Details-button (on the right side) for which endpoint you want to see the Outlier information.

3. Go to the Outliers-tab: http://localhost:5000/dashboard/<endpoint-name>/main/outliers

Visualizations
--------------
There are a number of visualization generated to view the results that have been collected in (Endpoint-Monitoring)
and (Test-Coverage Monitoring).

The main difference is that visualizations from (Endpoint-Monitoring) can be found in the menu 'Dashboard' (in the
left menu), while visualizations from (Test-Coverage Monitoring) can be found in the menu 'Test Monitor' (below the
'Dashboard'-menu).

The 'Dashboard'-menu contains the following content:

1. **Overview:** A table with the all the endpoints that are being monitored (or have been monitored in the past).
   This table provides information about when the endpoint is last being requested, how often it is requested and what 
   the median execution time is. Furthermore, it has a 'Details' button on the right. This is explained further in (6).

2. **Hourly load:** This graph provides information for each hour of the day of how often the endpoint is being requested. In 
   this graph it is possible to detect popular hours during the day.

3. **Version Usage**: This graph provides information about the distribution of the utilization of the requests per version.
   That is, how often (in percentages) is a certain endpoint requested in a certain version.

4. **Requests per endpoint:** This graph provides a row of information per day. In this graph, you can find
   whether the total number of requests grows over days.

5. **Time per endpoint:** This graph provides a row of information per endpoint. In that row, you can find all the
   requests for that endpoint. This provides information whether certain endpoints perform better (in terms of
   execution time) than other endpoints.

6. For each endpoint, there is a 'Details'-button (alternatively, you can click on the row itself). This provides the following 
   information (thus, all information below is specific for a single endpoint):

   - **Hourly load:** The same hourly load as explained in (2), but this time it is focused on the data of that particular
     endpoint only.

   - **Time per version per user:** A circle plot with the average execution time per user per version. Thus, this
     graph consists of 3 dimensions (execution time, users, versions). A larger circle represents a higher execution
     time.

   - **Time per version per ip:** The same type of plot as 'Time per version per user', but now that users are replaced
     by IP-addresses.

   - **Time per version:** A horizontal box plot with the execution times for a specific version. This graph is
     equivalent to (4.), but now it is focused on the data of that particular endpoint only.

   - **Time per user:** A horizontal box plot with the execution time per user. In this graph, it is possible
     to detect if there is a difference in the execution time between users.

   - **Outliers:** See Section (Outliers) above.

Need more information?
----------------------
See the `contact page <contact.html>`_ to see how you can contribute on the project.
Furthermore you can request this page for questions, bugs, or other information. 