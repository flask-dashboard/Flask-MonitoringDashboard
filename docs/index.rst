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
The Flask Monitoring Dashboard provides 4 main functionalities:

- **Monitor the Flask application:**
  This Flask extensions finds all your endpoints.
  You can choose which endpoints you want to monitor and which not.
  Monitoring and endpoint allows you to see which endpoints are being processed quickly, and which are not.
  Additionally, it provides information about the performance of the endpoint throughout different versions and different users.

- **Monitor your test coverage:**
  Find out what endpoints are covered by unittest.
  For more information, `see this file <http://flask-monitoringdashboard.readthedocs.io/en/latest/functionality.html#test-coverage-monitoring>`_.

- **Collect extra information about outliers:**
  Outliers are requests that take way longer to process than regular requests.
  The dashboard stores more information about outliers, such as:
    
    - The stacktrace in which it got stuck.
    - Request values.
    - Request headers.
    - Request environment.


- **Visualize the collected data in a number useful graphs:**
  The dashboard is automatically added to your existing Flask application.
  When running your app, the dashboard van be viewed by default in the route:
  `/dashboard <localhost:5000/dashboard>`_

For an detailed overview of the functionality in the dashboard, you `have a look at this page <functionality.html>`_.

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
   :maxdepth: 1

   contact
   changelog