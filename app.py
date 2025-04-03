from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import re
import smtplib
from email.mime.text import MIMEText
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import random
import string
import threading
import time
import shutil

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
BIN_FOLDER = 'bin'  # Folder to move files after 2 minutes
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['BIN_FOLDER'] = BIN_FOLDER
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the bin folder if it doesn't exist
if not os.path.exists(BIN_FOLDER):
    os.makedirs(BIN_FOLDER)

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    otp = db.Column(db.String(6), nullable=True)  # Store OTP temporarily

    # Relationship with SMTPConfig
    smtp_config = db.relationship('SMTPConfig', backref='user', uselist=False)

    def set_password(self, password):
        """Hash and store the password."""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, password):
        """Verify the password."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)

# SMTP Configuration Model
class SMTPConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    smtp_server = db.Column(db.String(120), nullable=False)
    smtp_port = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Create the database
with app.app_context():
    db.create_all()

# Function to move files from uploads to bin
def move_files_to_bin():
    """
    Moves all files from the uploads folder to the bin folder.
    """
    try:
        # Get all files in the uploads folder
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        for file_name in files:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
            if os.path.isfile(file_path):  # Ensure it's a file
                # Move the file to the bin folder
                shutil.move(file_path, os.path.join(app.config['BIN_FOLDER'], file_name))
                print(f"Moved file: {file_name} to bin folder.")
    except Exception as e:
        print(f"Error moving files to bin: {str(e)}")
    # Schedule the function to run again after 2 minutes
    threading.Timer(120, move_files_to_bin).start()

# Start the periodic file-moving task when the app starts
move_files_to_bin()

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.")
            return redirect(url_for('signup'))

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("Email already registered. Please use a different email.")
            return redirect(url_for('signup'))

        # Create a new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please log in.")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find the user by username
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # Log the user in
            session['user_id'] = user.id
            session['username'] = user.username
            flash("Login successful!")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.")

    return render_template('login.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        # Find the user by email
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("No account found with this email.")
            return redirect(url_for('forgot_password'))

        # Generate OTP
        otp = ''.join(random.choices(string.digits, k=6))
        user.otp = otp
        db.session.commit()

        # Send OTP via email
        try:
            send_otp_email(user.email, otp)
            flash("An OTP has been sent to your email. Please check your inbox.")
            return redirect(url_for('reset_password', email=user.email))
        except Exception as e:
            flash(f"Failed to send OTP: {str(e)}")
            return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')

@app.route('/reset-password/<email>', methods=['GET', 'POST'])
def reset_password(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Invalid email address.")
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        otp = request.form['otp']
        new_password = request.form['new_password']
        
        if otp != user.otp:
            flash("Invalid OTP. Please try again.", "error")  # Add category for styling
            return redirect(url_for('reset_password', email=email))
        
        # Update password
        user.set_password(new_password)
        user.otp = None  # Clear OTP after successful password reset
        db.session.commit()
        
        # Redirect without adding a new flash message
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', email=email)

def send_otp_email(to_email, otp):
    """Send an OTP email using Gmail's SMTP server."""
    gmail_user = os.getenv('GMAIL_USER')
    gmail_password = os.getenv('GMAIL_PASSWORD')
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))

    if not all([gmail_user, gmail_password, smtp_server, smtp_port]):
        raise ValueError("Missing SMTP credentials. Please check your .env file.")

    subject = "Your OTP for Password Reset"
    body = f"Your One-Time Password (OTP) is: {otp}. Please do not share it with anyone."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = f'"BulkMail OTP" <{gmail_user}>'
    msg['To'] = to_email

    try:
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable TLS encryption
        server.login(gmail_user, gmail_password)  # Log in using the user's credentials
        server.sendmail(gmail_user, [to_email], msg.as_string())  # Send the email
        server.quit()
        print(f"OTP sent successfully to {to_email}")
    except smtplib.SMTPAuthenticationError as auth_error:
        print(f"SMTP Authentication failed: {auth_error.smtp_code} - {auth_error.smtp_error.decode('utf-8')}")
        raise Exception("Failed to authenticate with the SMTP server. Check your credentials.")
    except smtplib.SMTPException as smtp_error:
        print(f"SMTP error occurred: {smtp_error}")
        raise Exception(f"SMTP error occurred: {smtp_error}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise Exception(f"An unexpected error occurred: {e}")

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash("You have been logged out.")
    return redirect(url_for('login'))

@app.route('/account', methods=['GET', 'POST'])
def account():
    if 'user_id' not in session:
        flash("You need to log in to access your account.")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        if not user.check_password(current_password):
            flash("Current password is incorrect.")
            return redirect(url_for('account'))

        # Update the password
        user.set_password(new_password)
        db.session.commit()

        flash("Password updated successfully!")
        return redirect(url_for('account'))

    return render_template('account.html', email=user.email)

@app.route('/config', methods=['GET', 'POST'])
def config():
    if 'user_id' not in session:
        flash("You need to log in to access this page.")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    smtp_config = user.smtp_config  # Get the user's SMTP configuration

    if request.method == 'POST':
        smtp_server = request.form.get('smtp_server')
        smtp_port = request.form.get('smtp_port')
        email = request.form.get('email')
        password = request.form.get('password')

        # Validate SMTP port
        if not smtp_port.isdigit() or not (1 <= int(smtp_port) <= 65535):
            flash("Error: SMTP Port must be a numeric value between 1 and 65535.")
            return redirect(url_for('config'))

        # Save or update SMTP configuration
        if not smtp_config:
            # Create a new SMTPConfig entry
            smtp_config = SMTPConfig(
                user_id=user.id,
                smtp_server=smtp_server,
                smtp_port=int(smtp_port),
                email=email,
                password=password
            )
            db.session.add(smtp_config)
        else:
            # Update existing SMTPConfig entry
            smtp_config.smtp_server = smtp_server
            smtp_config.smtp_port = int(smtp_port)
            smtp_config.email = email
            smtp_config.password = password

        db.session.commit()
        flash("SMTP configuration updated successfully!")
        return redirect(url_for('index'))

    return render_template(
        'config.html',
        smtp_config=smtp_config
    )

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/sendEmails', methods=['POST'])
def send_emails():
    if 'user_id' not in session:
        return jsonify({'error': 'You need to log in to send emails.'}), 401

    user = User.query.get(session['user_id'])
    smtp_config = user.smtp_config

    if not smtp_config:
        return jsonify({'error': 'SMTP configuration not found. Please configure your SMTP settings.'}), 400

    try:
        subject = request.form['subject']
        body = request.form['body']
        file = request.files['file']
        sender_name = request.form.get('sender_name', 'BulkMail Pro')

        if not file:
            return jsonify({'error': 'No file uploaded'}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        emails = extract_emails_from_file(file_path)

        success_log = []
        failure_log = []

        for email in emails:
            try:
                send_email(
                    to_email=email,
                    subject=subject,
                    body=body,
                    sender_name=sender_name,
                    smtp_server=smtp_config.smtp_server,
                    smtp_port=smtp_config.smtp_port,
                    gmail_user=smtp_config.email,
                    gmail_password=smtp_config.password
                )
                success_log.append(f"Email sent to: {email}")
            except Exception as e:
                failure_log.append(f"Failed to send email to: {email} - {str(e)}")

        return jsonify({
            'success': success_log,
            'failure': failure_log
        })

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': f"An unexpected error occurred: {str(e)}"}), 500

def extract_emails_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', content)

    if not emails:
        raise ValueError("No valid email addresses found in the uploaded file.")

    return emails

def send_email(to_email, subject, body, sender_name, smtp_server, smtp_port, gmail_user, gmail_password):
    """Send an email using the configured SMTP server."""
    try:
        # Create the email message
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = f'"{sender_name}" <{gmail_user}>'
        msg['To'] = to_email

        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable TLS encryption
        server.login(gmail_user, gmail_password)  # Log in using the user's credentials
        server.sendmail(gmail_user, [to_email], msg.as_string())  # Send the email
        server.quit()

        print(f"Email sent successfully to {to_email}")
    except smtplib.SMTPAuthenticationError as auth_error:
        print(f"SMTP Authentication failed: {auth_error.smtp_code} - {auth_error.smtp_error.decode('utf-8')}")
        raise Exception("Failed to authenticate with the SMTP server. Check your credentials.")
    except smtplib.SMTPException as smtp_error:
        print(f"SMTP error occurred: {smtp_error}")
        raise Exception(f"SMTP error occurred: {smtp_error}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise Exception(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)