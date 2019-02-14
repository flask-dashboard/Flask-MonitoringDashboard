Developing
==========
This page provides information about contributing to the Flask Monitoring Dashboard.
Furthermore, a number of useful tools for improving the quality of the code are discussed.


Implementation
--------------
The Dashboard is implemented in the following 6 directories: core, database, static, templates, test 
and views. Together this forms a Model-View-Controller-pattern:

- **Model**: The model consists of the database-code. To be more specific, it is defined in
  'Flask-MonitoringDashboard/database.__init__.py'.

- **View**: The view is a combination of the following three directories:
  
  - **static**: contains some CSS and JS files.

  - **templates**: contains the HTML files for rendering the Dashboard. The HTML files are rendered
    using the `Jinja2 templating language`. Jinja2 allows a HTML-template to inherit from another HTML-
    template. The hierarchy of all templates is:

    .. _`Jinja2 templating language`: http://jinja.pocoo.org/docs/

    ::

       fmd_base.html
       ├──fmd_dashboard/overview.html
       │  └──fmd_dashboard/graph.html
       │     ├──fmd_dashboard/graph-details.html
       │     │  └──fmd_dashboard/outliers.html
       │     ├──fmd_dashboard/profiler.html
       │     │  └──fmd_dashboard/grouped_profiler.html
       │     └──fmd_testmonitor/endpoint.html
       ├──fmd_testmonitor/testmonitor.html
       ├──fmd_config.html
       ├──fmd_login.html
       └──fmd_rules.html
       fmd_export-data.html


    - **fmd_base.html**: For rendering the container of the Dashboard, and load all required CSS and JS scripts.
    - **fmd_config.html**: For rendering the `Configuration-page`_.
    - **fmd_login.html**: For rendering the `Login-page`_.
    - **fmd_urles.html**: For rendering the `Rules-page`_.
    - **fmd_dashboard/overview.html**: For rendering the `Overview-page`_.
    - **fmd_dashboard/graph.html**: For rendering the following graphs:

      - Hourly load
      - Version Usage
      - Requests per endpoint
      - Time per endpoint

    - **fmd_dashboard/graph-details.html**: For rendering the following graphs:

      - Hourly load
      - Time per version per user
      - Time per version per ip
      - Time per version
      - Time per user

    - **fmd_dashboard/outliers.html**: For rendering the Outlier-page.

    - **fmd_testmonitor/testmonitor.html**: For rendering the `Testmonitor-page`_.

    - **fmd_testmonitor/endpoint.html**: For rendering the results of the Testmonitor.

    .. _`Configuration-page`: http://localhost:5000/dashboard/configuration
    .. _`Login-page`: http://localhost:5000/dashboard/login
    .. _`Rules-page`: http://localhost:5000/dashboard/rules
    .. _`Overview-page`: http://localhost:5000/dashboard/overview
    .. _`Testmonitor-page`: http://localhost:5000/dashboard/testmonitor

  - **views**: Contains all Flask route-functions that the Dashboard defines.

- **Controller**: The Controller contains all Dashboard Logic. It is defined in the **core**-folder.

Tools
-----
The following tools are used for helping the development of the Dashboard:

- **Branches**: The Dashboard uses the following branches:
  
  - **Master**: This is the branch that will ensure a working version of the Dashboard. It is 
    shown as the default branch on Github. The Master branch will approximately be updated every 
    week. Every push to the master will be combined with a new version that is released in 
    `PyPi <https://pypi.org/project/Flask-MonitoringDashboard>`_. This branch is also used to 
    compute the `Code coverage`_ and build the documentation_. In case of a PR from development
    into master, take care of the following two things:

    1. The version must be updated in flask_monitoringdashboard/constants.json

    2. The changelog should be updated in docs/changelog.rst

    .. _`Code coverage`: https://codecov.io/gh/flask-dashboard/Flask-MonitoringDashboard

    .. _documentation: http://flask-monitoringdashboard.readthedocs.io

  - **Development**: This branch contains the current working version of the Dashboard. This branch 
    contains the most recent version of the Dashboard, but there might be a few bugs in this version.

  - **Feature branch**: This branch is specific per feature, and will be removed after the 
    corresponding feature has been merged into the development branch. It is recommended to often 
    merge development into this branch, to keep the feature branch up to date.  

- **Unit testing**: The code is tested before a Pull Request is accepted. If you want to run the unit 
  tests locally, you can use the following command:

  *Use this command while being in the root of the Flask-MonitoringDashboard folder.*

  .. code-block:: python

     python setup.py test

- **Travis**: Travis CI is a hosted, distributed continuous integration service used to build 
  and test software projects hosted at GitHub. The Dashboard uses Travis to ensure that all
  tests are passed before a change in the code reaches the Master branch.

- **Documentation**: The documentation is generated using Sphinx_ and hosted on ReadTheDocs_. If you 
  want to build the documentation locally, you can use the following commands:

  *Use the commands while being in the docs folder (Flask-MonitoringDashboard/docs).*

  .. code-block:: bash

     pip install -r requirements.txt
     make html

  The generated html files can be found in the following folder: Flask-MonitoringDashboard/docs/build.

  Using the make command, you can build more, than only HTML-files. For a list of all possible options,
  use the following command:

  .. code-block:: bash

     make help

  .. _Sphinx: www.sphinx-doc.org
  .. _ReadTheDocs: http://flask-monitoringdashboard.readthedocs.io

Database Scheme
---------------
If you're interested in the data that the Flask-MonitoringDashboard stores, have a look at the database scheme below.

Note the following:

  - A key represents the Primary Key of the corresponding table. In the StackLine-table, the Primary Key consists 
    of a combination of two fields (request_id and position).

  - The blue arrow points to the Foreign Key that is used to combine the results of multiple tables. 

.. figure :: img/database_scheme.png
   :width: 100%



Versions
--------
The Dashboard uses `Semantic-versioning`_. Therefore, it is specified in a **Major** . **Minor** . **Patch** -format:

- **Major**: Increased when the Dashboard contains incompatible API changes with the previous version.

- **Minor**: Increased when the Dashboard has new functionality in a backwards-compatible manner.

- **Patch**: Increased when a bug-fix is made.


.. _`Semantic-versioning`: https://semver.org/
