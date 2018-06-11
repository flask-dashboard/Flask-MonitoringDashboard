.. figure :: img/header.png
   :width: 100%

**Automatically monitor the evolving performance of Flask/Python web services**

What is Flask-MonitoringDashboard?
---------------------------------------
The Flask Monitoring Dashboard is designed to easily monitor your existing Flask application.
You can find a brief overview of the functionality `here <#functionality>`_.

Or you can watch the video below:

.. raw:: html

   <iframe width="560" height="315" src="https://www.youtube.com/embed/1S3-G4pSoAk" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>


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

- **Monitor your test coverage:**
  The Dashboard allows you to find out which endpoints are covered by unit tests, allowing also for integration with Travis for automation purposes. 
  For more information, see `this file <http://flask-monitoringdashboard.readthedocs.io/en/latest/functionality.html#test-coverage-monitoring>`_.

- **Collect extra information about outliers:**
  Outliers are requests that take much longer to process than regular requests. 
  The Dashboard automatically detects that a request is an outlier and stores extra information about it (stack trace, request values, Request headers, Request environment).

For more advanced documentation, take a look at the information on `this page <http://flask-monitoringdashboard.readthedocs.io/en/latest/functionality.html>`_.

User's Guide
------------
If you are interested in the Flask-MonitoringDashboard, you can find more information in the links below:

.. toctree::
   :maxdepth: 2

   installation
   
   configuration
   
   functionality

Developer information
---------------------
.. toctree::
   :maxdepth: 2

   contact

   developing

   migration

   todo
   
   changelog
