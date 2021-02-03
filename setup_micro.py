import json
import os

import setuptools

loc = os.path.dirname(os.path.abspath(__file__))


def get_description():
    with open(loc + '/docs/README.rst') as readme:
        info = readme.read()
    with open(loc + '/docs/changelog.rst') as changelog:
        return info + '\n\n' + changelog.read()


with open(loc + '/requirements-micro.txt') as f:
    required = f.read().splitlines()

with open('flask_monitoringdashboard/constants.json', 'r') as f:
    constants = json.load(f)

setuptools.setup(
    name="Flask-MonitoringDashboard-Micro",
    version=constants['version'],
    setup_requires=['setuptools_scm'],
    packages=setuptools.find_packages(include=[
        'flask_monitoringdashboard',
        'flask_monitoringdashboard.database',
        'flask_monitoringdashboard.core',
        'flask_monitoringdashboard.core.config',
        'flask_monitoringdashboard.core.custom_graph',
        'flask_monitoringdashboard.core.profiler',
        'flask_monitoringdashboard.core.profiler.*',
    ],
        exclude=['flask_monitoringdashboard.controllers.*',
                 'flask_monitoringdashboard.frontend.*',
                 'flask_monitoringdashboard.views.*',
                 'flask_monitoringdashboard.static.*',
                 'tests', 'test.*']
    ),
    include_package_data=False,  # This is all the html files and things
    platforms='Any',
    zip_safe=False,
    test_suite='tests.get_test_suite',
    url='https://github.com/flask-dashboard/Flask-MonitoringDashboard',
    author=constants['author'],
    author_email=constants['email'],
    description="Automatically monitor the evolving performance of Flask/Python web services.",
    long_description=get_description(),
    install_requires=required,
    entry_points={'flask.commands': ['fmd=flask_monitoringdashboard.cli:fmd']},
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Framework :: Flask',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/flask-dashboard/Flask-MonitoringDashboard/issues',
        'PyPi': 'https://pypi.org/project/Flask-MonitoringDashboard/',
        'Documentation': 'http://flask-monitoringdashboard.readthedocs.io/',
        'Source': 'https://github.com/flask-dashboard/Flask-MonitoringDashboard/',
    },
)
