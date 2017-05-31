from flask import Flask, redirect, url_for
import dashboard
import os

user_app = Flask(__name__)
here = os.path.abspath(os.path.dirname(__file__))
dashboard.config.from_file(here + '/config.cfg')
dashboard.bind(app=user_app)


@user_app.route('/')
def main():
    return "hello_world"


if __name__ == '__main__':
    user_app.run(debug=True, host='0.0.0.0')
