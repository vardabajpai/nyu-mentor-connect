import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database configuration
database_url = os.environ.get('DATABASE_URL', 'sqlite:///registrations.db')
# Railway uses postgres:// but SQLAlchemy needs postgresql://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model for registrations
class Registration(db.Model):
    __tablename__ = 'registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    graduation_year = db.Column(db.String(4), nullable=False)
    school = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Registration {self.first_name} {self.last_name}>'

# Create tables on startup
with app.app_context():
    db.create_all()

# Home page with registration form
@app.route('/')
def index():
    return render_template('index.html')

# Handle form submission
@app.route('/register', methods=['POST'])
def register():
    try:
        new_registration = Registration(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            email=request.form['email'],
            phone=request.form['phone'],
            graduation_year=request.form['graduation_year'],
            school=request.form['school']
        )
        
        db.session.add(new_registration)
        db.session.commit()
        
        return redirect(url_for('success'))
    
    except Exception as e:
        db.session.rollback()
        # If email already exists
        if 'unique constraint' in str(e).lower() or 'duplicate' in str(e).lower():
            return render_template('index.html', error='This email is already registered!')
        return render_template('index.html', error='Something went wrong. Please try again.')

# Success page
@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
