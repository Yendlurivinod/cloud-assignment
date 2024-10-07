from flask import Flask, request, render_template, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = ')(*&^%$#@!'  # Change this to a random secret key

def get_db_connection():
    conn = sqlite3.connect('/var/www/html/users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Store plain text password
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']

        try:
            conn = get_db_connection()
            conn.execute("INSERT INTO users (username, password, first_name, last_name, email) VALUES (?, ?, ?, ?, ?)",
                         (username, password, first_name, last_name, email))  # Insert plain text password
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email or username already exists', 'danger')
            return redirect(url_for('register'))
        except Exception as e:
            flash(f'An error occurred: {e}', 'danger')
            return redirect(url_for('register'))
        finally:
            conn.close()

    return render_template('registration.html')

@app.route('/user_details', methods=['GET'])
def user_details():
    user = session.get('user')
    if user:
        return render_template('user_details.html', user=user)
    else:
        flash('You need to log in first', 'warning')
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        # Check if the user exists and the password matches
        if user and user['password'] == password:  # Compare with plain text password
            user_dict = {key: user[key] for key in user.keys()}  # Convert to dictionary
            session['user'] = user_dict  # Store user information in session
            return redirect(url_for('user_details'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)