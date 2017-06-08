import setuptools

packages = ['flask_dashboard.' + p for p in setuptools.find_packages('./flask_dashboard')] + \
           ['flask_dashboard']

setuptools.setup(
    name="flask_dashboard",
    version="1.3",
    packages=packages,
    include_package_data=True,
    zip_safe=False,
    url='https://github.com/mircealungu/automatic-monitoring-dasboard',
    author="Patrick Vogel & Thijs Klooster",
    author_email="p.p.vogel@student.rug.nl",
    description="A dashboard for automatic monitoring of python web services",
    install_requires=['flask>=0.9',
                      'sqlalchemy>=1.1.9',
                      'wtforms>=2.1',
                      'flask_wtf',
                      'pygal>=2.3.1',
                      'plotly',
                      'configparser']
)
