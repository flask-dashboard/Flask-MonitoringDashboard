import setuptools


with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="flask_monitoring_dashboard",
    version="1.9",
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='dashboard.test.start_testing',
    url='https://github.com/mircealungu/automatic-monitoring-dashboard',
    author="Patrick Vogel & Thijs Klooster",
    author_email="p.p.vogel@student.rug.nl",
    description="A dashboard for automatic monitoring of python web-services",
    install_requires=required
)
