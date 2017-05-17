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

install_requires = ["Flask"]

# Copy all data_files from the 'static'- and 'templates'-folder into their destination
data_files_list = tuple_list('static')
data_files_list.extend(tuple_list('templates'))

setup(
    name='Flask-Dashboard',
    version='0.2',
    packages=find_packages(),
    data_files=data_files_list,
    url='https://github.com/FlyingBird95/flask-dashboard',
    license='Apache',
    author='Patrick Vogel',
    author_email='p.p.vogel@student.rug.nl',
    description='A dashboard for automatic monitoring of python web services',
    long_description=README,
    install_requires=['flask', 'sqlalchemy', 'wtforms', 'pygal'],
    zip_safe=False
)