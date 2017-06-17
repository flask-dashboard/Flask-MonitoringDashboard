from flask import Flask, redirect, url_for
import dashboard
import os

user_app = Flask(__name__)
here = os.path.abspath(os.path.dirname(__file__))
dashboard.config.from_file(here + '/config.cfg')


def get_session_id():
    # implement here your own custom function
    return "1234"

dashboard.config.get_group_by = get_session_id
dashboard.bind(app=user_app)


@user_app.route('/')
def main():
    import time
    time.sleep(1)
    return redirect(url_for('dashboard.index'))


if __name__ == '__main__':
    user_app.run(debug=True, host='0.0.0.0')
