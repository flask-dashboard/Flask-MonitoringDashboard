import setuptools
import os
import json
loc = os.path.dirname(os.path.abspath(__file__))


def get_description():
    with open(loc + '/README.md') as readme:
        info = readme.read()
    with open(loc + '/docs/changelog.rst') as changelog:
        return info + '\n\n' + changelog.read()


with open(loc + '/requirements.txt') as f:
    required = f.read().splitlines()

with open('flask_monitoringdashboard/constants.json', 'r') as f:
    constants = json.load(f)

setuptools.setup(
    name="Flask-MonitoringDashboard",
    version=constants['version'],
    packages=setuptools.find_packages(),
    include_package_data=True,
    platforms='Any',
    zip_safe=False,
    test_suite='flask_monitoringdashboard.test.get_test_suite',
    url='https://github.com/flask-dashboard/Flask-MonitoringDashboard',
    author=constants['author'],
    author_email=constants['email'],
    description="Automatically monitor the evolving performance of Flask/Python web services.",
    long_description=get_description(),
    install_requires=required,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Flask'],
    project_urls={
        'Bug Reports': 'https://github.com/flask-dashboard/Flask-MonitoringDashboard/issues',
        'PyPi': 'https://pypi.org/project/Flask-MonitoringDashboard/',
        'Documentation': 'http://flask-monitoringdashboard.readthedocs.io/',
        'Source': 'https://github.com/flask-dashboard/Flask-MonitoringDashboard/',
    },
)
