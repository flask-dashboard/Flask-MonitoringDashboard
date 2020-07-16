Known Issues
===============

This page provides an overview of known bugs, workarounds, and limitations of the
Flask Monitoring Dashboard.

Deploying with mod_wsgi (Apache)
---------------------------------


The FMD relies on the ``scipy`` package for some of the statistical tests
used in the *Reports* feature. This package is incompatible with
``mod_wsgi`` by default, causing the deployment to fail. This is a common
issue `[1] <https://serverfault.com/questions/514242/non-responsive-apache-mod-wsgi-after-installing-scipy>`_
`[2] <https://stackoverflow.com/questions/16823388/using-scipy-in-django-with-apache-and-mod-wsgi>`_
and can be solved by setting the

.. code-block:: xml

    WSGIApplicationGroup %{GLOBAL}

directive in your WSGI configuration file, as described in the linked posts.