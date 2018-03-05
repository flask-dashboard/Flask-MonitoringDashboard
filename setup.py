import setuptools


def desc():
    info = open('README.md').read()
    try:
        return info + '\n\n' + open('CHANGELOG.rst').read()
    except IOError:
        return info

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="Flask-MonitoringDashboard",
    version="1.10.4",
    packages=setuptools.find_packages(),
    include_package_data=True,
    platforms='Any',
    zip_safe=False,
    test_suite='flask_monitoringdashboard.test.start_testing',
    url='https://github.com/flask-dashboard/Flask-MonitoringDashboard',
    author="Patrick Vogel & Thijs Klooster",
    author_email="p.p.vogel@student.rug.nl",
    description="A dashboard for automatic monitoring of Flask web-services",
    long_description=desc(),
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
        'Programming Language :: Python :: 3.6'],
    project_urls={
        'Bug Reports': 'https://github.com/flask-dashboard/Flask-MonitoringDashboard/issues',
        'PyPi': 'https://pypi.org/project/Flask-MonitoringDashboard/',
        'Documentation': 'http://flask-monitoringdashboard.readthedocs.io/',
        'Source': 'https://github.com/flask-dashboard/Flask-MonitoringDashboard/',
    },
)
