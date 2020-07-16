.. figure :: img/header.png
   :width: 100%

**Automatically monitor the evolving performance of Flask/Python web services**

What is Flask-MonitoringDashboard?
---------------------------------------
The Flask Monitoring Dashboard is designed to easily monitor your Flask application.


Functionality
-------------
The Flask Monitoring Dashboard is an extension that offers 4 main functionalities with little effort from the Flask developer:

- **Monitor the performance and utilization:**
  The Dashboard allows you to see which endpoints process a lot of requests and how fast. 
  Additionally, it provides information about the evolving performance of an endpoint throughout different versions if you're using git.

- **Profile requests and endpoints:**
  The execution path of every request is tracked and stored into the database. This allows you to gain
  insight over which functions in your code take the most time to execute. Since all requests for an 
  endpoint are also merged together, the Dashboard provides an overview of which functions are used in
  which endpoint.

- **Collect extra information about outliers:**
  Outliers are requests that take much longer to process than regular requests. 
  The Dashboard automatically detects that a request is an outlier and stores extra information about it (stack trace, request values, Request headers, Request environment).

- **Collect additional information about your Flask-application:**
  Suppose you have an User-table and you want to know how many users are registered on your Flask-application.
  Then, you can run the following query: 'SELECT Count(*) FROM USERS;'. But this is just annoying to do regularly.
  Therefore, you can configure this in the Flask-MonitoringDashboard, which will provide you this information per day (or other time interval).

For more advanced documentation, have a look at the `the detailed functionality page <http://flask-monitoringdashboard.readthedocs.io/en/latest/functionality.html>`_.

User's Guide
------------
If you are interested in the Flask-MonitoringDashboard, you can find more information in the links below:

.. toctree::
   :maxdepth: 2

   installation
   
   configuration
   
   functionality

   known_issues

Developer information
---------------------
.. toctree::
   :maxdepth: 2

   contact

   developing

   migration

   todo
   
   changelog
