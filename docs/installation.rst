Installation
============
This is the complete overview of installing the Flask Monitoring Dashboard.
It starts from the very basic, but it is likely that you can directly go to
`Installing the Flask Monitoring Dashboard Package <#id1>`_.

Install Python
--------------
You can check if you have Python installed by opening a terminal and execution the following command:

.. code-block:: bash

   python3 --version

It should return something like 'Python 3.6.3', if not,
you probably see something like 'bash: python3: command not found'.
In the former case, you're ok. In the latter, you can follow
`this link <http://docs.python-guide.org/en/latest/starting/installation/>`_ to install Python.

Installing a Virtual Environment (Optional)
-------------------------------------------
Although you don't explicitly need a Virtual Environment, it is highly recommend.
See `this page <https://virtualenv.pypa.io/en/stable/installation/>`_ to install a Virtual Environment.

Configuring the Virtual Environment (Optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you have skipped the previous section, you can also skip this one.
Once you've installed the Virtual Environment, you need to configure it.
This can be done by the following command:

.. code-block:: bash

   virtualenv ENV

Activate the Virtual Environment (Optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This is the last part of the configuring the virtual environment.
You should do this before you want to execute any python script/program.
It is (again) one simple command:

.. code-block:: bash

   source bin/activate

Installing the Flask Monitoring Dashboard Package
-------------------------------------------------
Using the command below, you can install the Flask Monitoring Dashboard:

.. code-block:: bash

   pip install flask_monitoringdashboard

Alternatively, you can install the Flask Monitoring Dashboard from
`Github <https://github.com/flask-dashboard/Flask-MonitoringDashboard>`_:

.. code-block:: bash

   git clone https://github.com/flask-dashboard/Flask-MonitoringDashboard.git
   cd Flask-MonitoringDashboard
   python setup.py install

Setup the Flask Monitoring Dashboard
-------------------------------------
Once you've successfully installed the package, you can use it in your code.
Suppose that you've already a Flask application that looks like this:

.. code-block:: python

   from flask import Flask
   app = Flask(__name__)

   ...

   @app.route('/')
   def index():
       return 'Hello World!'


   if __name__ == '__main__':
     app.run(debug=True)

With only two lines of code, you can add the extension to your Flask application:

.. code-block:: python

   ...
   import flask_monitoringdashboard as dashboard
   dashboard.bind(app)

Together, it becomes:

.. code-block:: python

   from flask import Flask
   import flask_monitoringdashboard as dashboard

   app = Flask(__name__)
   dashboard.bind(app)

   ...

   @app.route('/')
   def index():
       return 'Hello World!'

   if __name__ == '__main__':
     app.run(debug=True)

Further configuration
---------------------
You are now ready for using the Flask Monitoring Dashboard.
For a more advanced used, which we recommend, have a look at `the configuration page <configuration.html>`_.
