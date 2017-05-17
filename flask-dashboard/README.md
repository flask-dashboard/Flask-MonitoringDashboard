# flask-dashboard
Dashboard for automatic monitoring of python web services

This is a flask extension that can be added to your existing flask application.

It measures which python functions are heavily used and which aren't. Moreover, you can see the execution time per function.

Installation
============
To install from source, download the source code, then run this:

    python3 setup.py install

If you don't have permission, than run with sudo
    
Setup
=====
Adding the extension is simple:

    from flask import Flask
    import dashboard

    app = Flask(__name__)
    dashboard.config(app)
    
Usage
=====
Once the setup is done, you can view the dashboard at: 

    localhost:5000/dashboard
