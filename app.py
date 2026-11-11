from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import init_db, register_user, verify_user, get_fake_data_from_db, search_fake_data, delete_fake_record, delete_all_fake_records
from utils import shorten_url, send_email, send_sms, generate_and_store_fake_data
import functools

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

init_db()

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if verify_user(username, password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if not username or not password or not confirm_password:
            flash('All fields are required', 'error')
            return render_template('register.html')
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        if register_user(username, password):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists', 'error')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    active_tab = request.args.get('tab', 'url')
    return render_template('dashboard.html', username=session['username'], short_url="", active_tab=active_tab)

@app.route('/shorten_url', methods=['POST'])
@login_required
def shorten_url_route():
    long_url = request.form['long_url']
    short_url = ""
    if long_url:
        short_url = shorten_url(long_url)
    return render_template('dashboard.html', username=session['username'], short_url=short_url, active_tab='url')

@app.route('/send_email', methods=['POST'])
@login_required
def send_email_route():
    to_email = request.form['to_email']
    subject = request.form['subject']
    body = request.form['body']
    if to_email and subject and body:
        result = send_email(to_email, subject, body)
        flash(result, 'success' if 'successfully' in result else 'error')
    else:
        flash('All fields are required', 'error')
    return redirect(url_for('dashboard', tab='email'))

@app.route('/send_sms', methods=['POST'])
@login_required
def send_sms_route():
    to_phone = request.form['to_phone']
    message = request.form['message']
    if to_phone and message:
        result = send_sms(to_phone, message)
        flash(result, 'success' if 'successfully' in result else 'error')
    else:
        flash('All fields are required', 'error')
    return redirect(url_for('dashboard', tab='sms'))

@app.route('/generate_fake_data', methods=['POST'])
@login_required
def generate_fake_data_route():
    generate_and_store_fake_data()
    flash('Generated and stored 10 fake records!', 'success')
    return redirect(url_for('dashboard', tab='fake'))

# --- UPDATED VIEW FAKE DATA WITH SEARCH ---
@app.route('/view_fake_data')
@login_required
def view_fake_data():
    search_query = request.args.get('search', '')
    
    if search_query:
        records = search_fake_data(search_query)
    else:
        records = get_fake_data_from_db()
        
    return render_template('fake_data.html', records=records, username=session['username'], search_query=search_query)

@app.route('/delete_fake_data/<int:id>', methods=['POST'])
@login_required
def delete_fake_data(id):
    delete_fake_record(id)
    flash('Record deleted successfully!', 'success')
    return redirect(url_for('view_fake_data'))

@app.route('/delete_all_fake_data', methods=['POST'])
@login_required
def delete_all_fake_data_route():
    delete_all_fake_records()
    flash('All records deleted!', 'success')
    return redirect(url_for('view_fake_data'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)