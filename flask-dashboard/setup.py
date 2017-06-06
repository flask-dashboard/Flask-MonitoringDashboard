import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


# Returns a recursive-list with tuples (directory, [file-list]) from a given directory
def tuple_list(directory):
    l = [(directory,
          [directory + '/' + f for f in os.listdir(directory)
           if os.path.isfile(directory + '/' + f)])]
    files = os.listdir(directory)
    for f in files:
        name = directory + '/' + f
        if not os.path.isfile(name):
            l.extend(tuple_list(name))
    return l


try:
    README = open(os.path.join(here, 'README.md')).read()
except IOError:
    README = ''

# Copy all data_files from the 'static'- and 'templates'-folder into their destination
data_files_list = tuple_list('static')
data_files_list.extend(tuple_list('templates'))
# TODO: also add config-file to data_files_list

setup(
    name='flask_dashboard',
    version='0.3',
    packages=find_packages(),
    data_files=data_files_list,
    url='https://github.com/FlyingBird95/flask-dashboard',
    author='Patrick Vogel & Thijs Klooster',
    author_email='p.p.vogel@student.rug.nl',
    description='A dashboard for automatic monitoring of python web services',
    long_description=README,
    install_requires=['flask>=0.9',
                      'sqlalchemy>=1.1.9',
                      'wtforms>=2.1',
                      'flask_wtf',
                      'pygal>=2.3.1',
                      'configparser'],
    zip_safe=False
)