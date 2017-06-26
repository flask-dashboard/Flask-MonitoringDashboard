import sqlite3
from flask import Flask, render_template, request, session, abort, redirect, url_for, flash

app = Flask(__name__)

app.secret_key = 'secret-key'
con = sqlite3.connect('database.db', check_same_thread=False)

with app.open_resource('schema.sql', mode='r') as f:
    con.cursor().executescript(f.read())


def init_db():
    """Initializes the database."""
    with app.open_resource('schema.sql', mode='r') as f:
        con.cursor().executescript(f.read())
    con.commit()


@app.route('/')
def show_entries():
    cur = con.cursor().execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    con.cursor().execute('insert into entries (title, text) values (?, ?)',
               [request.form['title'], request.form['text']])
    con.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin':
            error = 'Invalid username'
        elif request.form['password'] != 'admin':
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run(debug=True)