import setuptools

setuptools.setup(
    name="flask_monitoring_dashboard",
    version="1.6",
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    url='https://github.com/mircealungu/automatic-monitoring-dashboard',
    author="Patrick Vogel & Thijs Klooster",
    author_email="p.p.vogel@student.rug.nl",
    description="A dashboard for automatic monitoring of python web-services",
    install_requires=['flask>=0.9',         # for monitoring the web-service
                      'sqlalchemy>=1.1.9',  # for database support
                      'wtforms>=2.1',       # for generating forms
                      'flask_wtf',          # also for generating forms
                      'plotly',             # for generating graphs
                      'configparser',       # for parsing the config-file
                      'psutil',             # for logging extra CPU-info
                      'colorhash']          # for hashing a string into a color
)
