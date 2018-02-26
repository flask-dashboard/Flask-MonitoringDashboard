import setuptools


def desc():
    info = open('README.md').read()
    try:
        return info + '\n\n' + open('CHANGELOG.md').read()
    except IOError:
        return info

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="flask_monitoring_dashboard",
    version="1.10.0",
    packages=setuptools.find_packages(),
    include_package_data=True,
    platforms='Any',
    zip_safe=False,
    test_suite='dashboard.test.start_testing',
    url='https://github.com/flask-dashboard/Flask-Monitoring-Dashboard',
    author="Patrick Vogel & Thijs Klooster",
    author_email="p.p.vogel@student.rug.nl",
    description="A dashboard for automatic monitoring of python web-services",
    long_description=desc(),
    install_requires=required,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6']
)
