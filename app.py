# app.py

import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_babel import Babel, gettext as _
from flask_sqlalchemy import SQLAlchemy

# Initialize the app
app = Flask(__name__)

# --- CONFIGURATION ---
# Use a strong secret key in production
app.config['SECRET_KEY'] = 'your_super_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///career_advisor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Babel configuration for multi-language support
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

# --- INITIALIZE EXTENSIONS ---
db = SQLAlchemy(app)
login_manager = LoginManager(app)
babel = Babel(app)

# --- DATABASE MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # You'll need to use a library like Werkzeug's security for password hashing
    # For now, we'll use a simple placeholder
    # from werkzeug.security import generate_password_hash, check_password_hash
    def set_password(self, password):
        self.password_hash = password # Not secure, use generate_password_hash()

    def check_password(self, password):
        return self.password_hash == password # Not secure, use check_password_hash()

    def __repr__(self):
        return f'<User {self.email}>'

class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    universities = db.Column(db.Text)  # Store as JSON string or a separate table
    certifications = db.Column(db.Text)
    guidance = db.Column(db.Text)

# --- USER & LANGUAGE LOADERS ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_locale():
    return request.accept_languages.best_match(['en', 'hi', 'fr', 'es'])

babel.init_app(app, locale_selector=get_locale)
# --- ROUTES ---

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        # In a real app, use user.check_password(password)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash(_('Invalid email or password.'), 'error')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # In a real app, you would add logic to:
        # 1. Check if the email already exists
        # 2. Hash the password securely (e.g., with werkzeug.security)
        # 3. Create a new User object
        # 4. Add and commit the new user to the database
        # 5. Log the new user in and redirect them to the home page
        
        flash(_('Registration successful! Please log in.'), 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/fields_of_study', methods=['POST'])
@login_required
def fields_of_study():
    user_skills = request.form.get('skills')
    
    # --- Dummy data for demonstration ---
    # In a real app, you would use a search algorithm or a database query
    # to match user_skills to fields.
    
    fields = [
        {'name': _('Data Science'), 'description': _('A field that uses scientific methods to extract knowledge and insights from data.')},
        {'name': _('Web Development'), 'description': _('Building and maintaining websites and web applications.')},
        {'name': _('Artificial Intelligence'), 'description': _('The simulation of human intelligence in machines.')}
    ]
    
    return render_template('fields_of_study.html', fields=fields)

@app.route('/field/<field_name>')
@login_required
def field_detail(field_name):
    # --- Dummy data for a specific field ---
    # You would query this from your database in a real app
    
    field_data = {
        'Data Science': {
            'name': _('Data Science'),
            'description': _('A field that uses scientific methods to extract knowledge and insights from data.'),
            'universities': [
                {'name': _('Indian Institute of Technology, Madras'), 'location': 'Chennai', 'link': 'https://www.iitm.ac.in/'},
                {'name': _('Indian Statistical Institute'), 'location': 'Kolkata', 'link': 'https://www.isical.ac.in/'}
            ],
            'certifications': [_('Google Data Analytics Professional Certificate'), _('IBM Data Science Professional Certificate')],
            'guidance': _('Focus on mastering Python, R, and SQL. Build a strong portfolio with projects on Kaggle and GitHub. Stay updated with new algorithms and tools.')
        },
        'Web Development': {
            'name': _('Web Development'),
            'description': _('Building and maintaining websites and web applications.'),
            'universities': [
                {'name': _('Vellore Institute of Technology'), 'location': 'Vellore', 'link': 'https://vit.ac.in/'},
                {'name': _('Birla Institute of Technology and Science'), 'location': 'Pilani', 'link': 'https://www.bits-pilani.ac.in/'}
            ],
            'certifications': [_('FreeCodeCamp Responsive Web Design Certification'), _('The Web Developer Bootcamp by Colt Steele')],
            'guidance': _('Start with HTML, CSS, and JavaScript. Learn a backend framework like Flask or Django. Practice building full-stack projects to showcase your skills.')
        },
        'Artificial Intelligence': {
            'name': _('Artificial Intelligence'),
            'description': _('The simulation of human intelligence in machines.'),
            'universities': [
                {'name': _('IIT Delhi'), 'location': 'New Delhi', 'link': 'https://home.iitd.ac.in/'},
                {'name': _('IISc Bangalore'), 'location': 'Bangalore', 'link': 'https://iisc.ac.in/'}
            ],
            'certifications': [_('Deep Learning Specialization by Andrew Ng'), _('NVIDIA DLI Certificate')],
            'guidance': _('Master linear algebra, calculus, and probability. Get comfortable with Python and its libraries (TensorFlow, PyTorch). Read research papers and join AI communities.')
        }
    }
    
    field = field_data.get(field_name, {})
    return render_template('field_detail.html', field=field)

if __name__ == '__main__':
    # Creates the database tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)