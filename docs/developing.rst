Developing
==========
Fixing a bug, implementing a new feature, or just improving the quality of the
code, we always appreciate contributions! We understand that getting accustomed to a
new project takes some time and effort, but we're trying to make this process as smooth
and intuitive as possible.

Whereas until now, we've discussed FMD from the point of view of the user,
this page shows FMD from the point of view of the developer. We explain the
architecture of the project, take a look at the main components, and then
present some useful tools that we use during development.

Getting started
----------------
In order to get started with the environment of the FMD, run the following script

.. code-block:: bash

     . ./config/install.sh

Note the '. ' before the script. This will activate your virtual environment. This script is
responsible for setting up the project, and installing the following pre-commit hooks:

- `Black`_: for automatic formatting the code. Note that we use a width-length of 100 characters.
- `Flake8`_: for checking style error.
- Auto increase the Python version. This can either be a major, minor, or patch version increase. For more info, see
  the Versions-section below.

Architecture
--------------

From an architectural perspective, the Flask Monitoring Dashboard uses the
Layers pattern. There are 3 layers: data layer, logic layer, presentation layer.
Each of these is discussed in detail in this section.

The diagram below shows how FMD interacts with the monitored application. We
assumed that the application uses a database and a web interface, but these
components are not mandatory. Also, the FMD DB can be the same as the Application
DB.

.. figure :: img/architecture.png
   :width: 100%

Data layer
~~~~~~~~~~~~

This layer is responsible for the data collected by FMD about the monitored
application. The database schema is shown below.

.. figure :: img/fmd_db.png
   :width: 100%

The Data layer is technology-agnostic: you can use any RDBMS system you like, as
long as it is supported by `SQLAlchemy`_, the Object Relational Mapper used
by FMD! We mostly use SQLite for development purposes, but regularly test FMD
with MySQL and PostgreSQL.

Logic layer
~~~~~~~~~~~~

This layer is responsible for implementing all the features of FMD, storing and
retrieving the collected data to and from the Data layer, and providing a REST
API to be used by the Presentation layer. The Logic layer is written in Python and
contains the following 4 directories: controllers, core, database, views.

- **database:** contains all the functions that access the Data layer.
  No function from outside this directory should make queries to the database
  directly.

- **views:** contains the REST API. The Presentation layer uses the REST API to
  get the data that it has to show in the web interface.

- **controllers:** contains the business logic that transforms the objects from
  the database into objects that can be used by the Presentation layer. It
  represents the link between **database** and **views**.

- **core:** this is where the magic of FMD happens. Measuring the performance of
  monitored endpoints, profiling requests, and detecting outliers are all
  implemented in this directory.

Presentation layer
~~~~~~~~~~~~~~~~~~~

This layer is responsible for showing the data collected by FMD in a user-friendly
web interface. It is written using AngularJS 1.7.5 framework and Jinja2 templating
language, and contains 2 directories: static and templates.

- **templates:** only contains 2 Jinja2 templates. They represent the entry point
  for the web interface and request all the Javascript files required.

- **static:** contains the JavaScript, HTML, and CSS files. The code follows
  the Model-View-Controller pattern. The main components of this directory
  are described below:

  - app.js: defines the app and implements the routing mechanism. For each route,
    a JS controller and HTML template are specified.
  - controllers: JS files that make calls to the REST API of FMD and implement
    the logic of how the data is visualized.
  - services: JS files that contain cross-controller logic.
  - directives.js: file that declares custom HTML tags.
  - filters.js: contains functions used for nicely formatting the data.
  - pages: HTML files for building the web interface.


Frontend environment
~~~~~~~~~~~~~~~~~~~~~~

To run the frontend, these versions of Node and NPM are known to work:
-NPM v10.1.0
-Node v20.9.0

*Use the commands while being in the frontend folder (Flask-MonitoringDashboard/flask_monitoringdashboard/frontend).*

To install the packages:

.. code-block:: bash

    npm i
     
To run the testing environment:

.. code-block:: bash

    npm run dev

Any changes made in the code will now be reflected on the dashboard.


Tools
--------------

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

- **Heroku deployment**: The following branches are automatically deployed to Heroku. This is useful for quickly
  testing, without running any code locally.

   - **Master**: The master branch is deployed at: `<https://fmd-master.herokuapp.com>`_.
   - **Development**: The development is deployed at: `<https://fmd-development.herokuapp.com>`_.
   - **Pull requests**: Pull requests are also automatically build with a unique URL.


- **Unit testing**: The code is tested before a Pull Request is accepted. If you want to run the unit
  tests locally, you can use the following command from the root of Flask-MonitoringDashboard
  directory:

  .. code-block:: python

     python setup.py test

  All the tests are in the **test** directory and follow the naming convetion
  :code:`test_*.py`.

- **Travis**: Travis CI is a hosted, distributed continuous integration service used to build
  and test software projects hosted at GitHub. The Dashboard uses Travis to ensure that all
  tests are passed before a change in the code reaches the Master branch.

- **Documentation**: The documentation is generated using Sphinx_ and hosted on ReadTheDocs_. If you
  want to build the documentation locally, you can use the following commands:

  *Use the commands while being in the docs folder (Flask-MonitoringDashboard/docs).*

  .. code-block:: bash

     linux:
     pip install -r requirements.txt
     make html

  .. code-block:: bash

     windows:
     pip install -r requirements.txt
     sphinx-build -b html . _build

  The generated html files can be found in the following folder: Flask-MonitoringDashboard/docs/build.

  Using the make command, you can build more, than only HTML-files. For a list of all possible options,
  use the following command:

  .. code-block:: bash

     make help

- **Versions:** The Dashboard uses `Semantic-versioning`_. Therefore, it is specified in a **Major** . **Minor** . **Patch** -format:

  - **Major**: Increased when the Dashboard contains incompatible API changes with the previous version.

  - **Minor**: Increased when the Dashboard has new functionality in a backwards-compatible manner.

  - **Patch**: Increased when a bug-fix is made.


.. _`Semantic-versioning`: https://semver.org/
.. _`SQLAlchemy`: https://www.sqlalchemy.org/
.. _Sphinx: www.sphinx-doc.org
.. _ReadTheDocs: http://flask-monitoringdashboard.readthedocs.io
.. _Black: https://github.com/psf/black
.. _Flake8: https://pypi.org/project/flake8
