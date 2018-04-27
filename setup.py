import setuptools
import os
loc = os.path.dirname(os.path.abspath(__file__))


def get_description():
    with open(loc + '/README.md') as readme:
        info = readme.read()
    with open(loc + '/CHANGELOG.rst') as changelog:
        return info + '\n\n' + changelog.read()


with open(loc + '/requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="Flask-MonitoringDashboard",
    version='1.12.0',
    packages=setuptools.find_packages(),
    include_package_data=True,
    platforms='Any',
    zip_safe=False,
    test_suite='flask_monitoringdashboard.test.get_test_suite',
    url='https://github.com/flask-dashboard/Flask-MonitoringDashboard',
    author="Patrick Vogel & Thijs Klooster",
    author_email="p.p.vogel@student.rug.nl",
    description="A dashboard for automatic monitoring of Flask web-services",
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
