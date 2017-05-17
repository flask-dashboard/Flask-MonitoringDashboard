from flask import Flask, redirect, url_for
import dashboard

user_app = Flask(__name__)
dashboard.config(app=user_app)


@user_app.route('/')
def main():
    return redirect(url_for('dashboard_index'))


if __name__ == '__main__':
    user_app.run(debug=True, host='0.0.0.0')
