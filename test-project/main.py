from flask import Flask, render_template, request, redirect, session

import database
from forms import LoginForm, RegisterForm, QuoteForm


# Create tables (if not exists)
database.create_tables()

# Create Flask module
app = Flask(__name__)
app.secret_key = 'my-secret-key'  # secret key is used for session-variables


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    # on form submitted
    if request.method == 'POST' and form.validate():
        if database.user_exists(form.email.data):
            user = database.select_user(form.email.data)
            if user[2] != form.password.data:
                form.password.errors.append("Incorrect password. Try again!")
            else:
                session['user_id'] = user[0]
                return redirect('/logged_in')
        else:
            form.email.errors.append("Email has not been found in the database. Try another one!")
    return render_template('login.html', form=form)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    # on form submitted
    if request.method == 'POST' and form.validate():
        if database.user_exists(form.email.data):
            form.email.errors.append('Username already exists. Choose another one!')
        else:
            user = (form.email.data, form.password.data)
            database.add_user(user)
            return redirect('/logged_in')
    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    del session['user_id']
    return redirect('/')


@app.route('/logged_in', methods=['GET', 'POST'])
def logged_in():
    form = QuoteForm(request.form)
    if session['user_id'] is None:
        return redirect('/')

    if request.method=='POST' and form.validate():
        database.add_quote(session['user_id'], form.quote.data)

    quotes = database.get_quotes(session['user_id'])
    return render_template('quote.html', form=form,
                           quote=database.get_random_quote(session['user_id']),
                           quotes=quotes)


if __name__ == "__main__":
    app.run(debug=True)