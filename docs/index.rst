Flask-Monitoring-Dashboard
==========================
Dashboard for automatic monitoring of Flask web services.

What is the Flask-Monitoring-Dashboard?
---------------------------------------
The Flask Monitoring Dashboard is designed to monitor your existing Flask application.
You can find a brief overview of the functionality `here <#functionality>`_.

Or you can watch the video below:

.. raw:: html

   <iframe width="560" height="315" src="https://www.youtube.com/embed/1S3-G4pSoAk" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>


Functionality
-------------
The Flask Monitoring Dashboard is an extension that offers 4 main functionalities with little effort from the Flask developer:

- **Monitor the Flask application:**
  Our Dashboard allows you to see which endpoints process a lot of request and how fast. 
  Additionally, it provides information about the evolving performance of an endpoint throughout different versions if you’re using git.

- **Monitor your test coverage:**
  The dashboard allows you to find out which endpoints are covered by unit tests, allowing also for integration with Travis for automation purposes. 
  For more information, see `this file <http://flask-monitoringdashboard.readthedocs.io/en/latest/functionality.html#test-coverage-monitoring>`_.

- **Collect extra information about outliers:**
  Outliers are requests that take much longer to process than regular requests. 
  The dashboard automatically detects that a request is an outlier and stores extra information about it (stack trace, request values, Request headers, Request environment).

- **Visualize the collected data in a number useful graphs:**
  The dashboard is automatically added to your existing Flask application.
  You can view the results by default using the default endpoint (this can be configured to another route): `dashboard <http://localhost:5000/dashboard>`_.

For a more advanced documentation, take a look at the information on `this page <http://flask-monitoringdashboard.readthedocs.io/en/latest/functionality.html>`_.

User's Guide
------------
If you are interested in the Flask Monitoring Dashboard, you can find more information in the links below:

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
   
   changelog