from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///court.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    court = db.Column(db.String(100))

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(100))
    case_name = db.Column(db.String(200))
    case_category = db.Column(db.String(100))
    legal_section = db.Column(db.String(100))
    parties = db.Column(db.String(200))
    status = db.Column(db.String(100))
    next_hearing = db.Column(db.String(100))
    judge = db.Column(db.String(100))
    filing_date = db.Column(db.String(100))
    description = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
@login_required
def dashboard():
    cases = Case.query.filter_by(judge=current_user.name).all()
    return render_template('dashboard.html', user=current_user, cases=cases)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/cases')
@login_required
def cases():
    cases = Case.query.filter_by(judge=current_user.name).all()
    return render_template('cases.html', cases=cases)

# NEW: Case Details Page
@app.route('/case/<int:case_id>')
@login_required
def case_details(case_id):
    case = Case.query.get_or_404(case_id)
    return render_template('case_details.html', case=case)

# NEW: Legal Search Results
@app.route('/search-legal', methods=['POST'])
@login_required
def search_legal():
    query = request.form.get('query', '')
    act = request.form.get('act', '')
    section = request.form.get('section', '')
    
    # Sample search results
    search_results = [
        {
            'title': 'Indian Kanoon - Legal Search',
            'link': f'https://indiankanoon.org/search/?formInput={query}',
            'description': f'Search results for {query} on Indian Kanoon'
        },
        {
            'title': 'Supreme Court Cases',
            'link': f'https://main.sci.gov.in/judgments?query={query}',
            'description': f'Supreme Court judgments related to {query}'
        },
        {
            'title': f'{act} Section {section}',
            'link': f'https://www.google.com/search?q={act}+section+{section}',
            'description': f'Detailed information about {act} Section {section}'
        },
        {
            'title': 'Legal Database',
            'link': f'https://www.lawctopus.com/?s={query}',
            'description': f'Legal articles and resources about {query}'
        }
    ]
    
    return render_template(
        'legal_results.html', 
        results=search_results, 
        query=query, 
        act=act, 
        section=section
    )

@app.route('/cause-lists')
@login_required
def cause_lists():
    # ✅ FIX: Pass cases to template
    cases = Case.query.filter_by(judge=current_user.name).all()
    return render_template('cause_lists.html', cases=cases)

@app.route('/legal-research')
@login_required
def legal_research():
    return render_template('legal_research.html')

# Initialize database with sample data
def init_db():
    with app.app_context():
        db.create_all()
        
        # Create sample user if not exists
        if not User.query.first():
            user = User(
                username='judge1',
                password='password123',
                name='Justice Sharma',
                court='Delhi High Court'
            )
            db.session.add(user)
            
            # Sample cases with detailed information
            cases_data = [
                {
                    'number': 'CRL/2024/125', 
                    'name': 'State vs Rajesh Kumar Murder Case',
                    'category': 'Criminal',
                    'section': 'IPC 302',
                    'parties': 'State of Delhi vs Rajesh Kumar',
                    'status': 'Trial Stage',
                    'next_hearing': '15 Dec 2024',
                    'filing_date': '15 Jan 2024',
                    'description': 'Murder case under IPC Section 302. The accused is charged with the murder of Mr. Amit Verma. Currently in trial stage with 5 witnesses examined.'
                },
                {
                    'number': 'CIVIL/2024/89', 
                    'name': 'ABC Corporation vs XYZ Ltd Contract Dispute',
                    'category': 'Civil',
                    'section': 'Contract Act Section 73',
                    'parties': 'M/S ABC Corporation vs M/S XYZ Ltd',
                    'status': 'Evidence Stage',
                    'next_hearing': '20 Dec 2024',
                    'filing_date': '20 Feb 2024',
                    'description': 'Commercial contract dispute involving breach of agreement. Damages claimed: ₹50 lakhs. Currently in evidence recording stage.'
                },
                {
                    'number': 'BAIL/2024/45', 
                    'name': 'Sanjay Mehta Bail Application',
                    'category': 'Criminal',
                    'section': 'CrPC 439',
                    'parties': 'Sanjay Mehta vs State of Delhi',
                    'status': 'Arguments',
                    'next_hearing': '10 Dec 2024',
                    'filing_date': '10 Mar 2024',
                    'description': 'Bail application in money laundering case. Arguments completed, judgment reserved.'
                },
                {
                    'number': 'MAT/2024/67', 
                    'name': 'Priya Sharma Divorce Case',
                    'category': 'Family',
                    'section': 'HMA Section 13',
                    'parties': 'Priya Sharma vs Raj Sharma',
                    'status': 'Mediation',
                    'next_hearing': '25 Dec 2024',
                    'filing_date': '25 Jan 2024',
                    'description': 'Divorce petition on grounds of cruelty. Currently in mediation process.'
                }
            ]
            
            for case_data in cases_data:
                case = Case(
                    case_number=case_data['number'],
                    case_name=case_data['name'],
                    case_category=case_data['category'],
                    legal_section=case_data['section'],
                    parties=case_data['parties'],
                    status=case_data['status'],
                    next_hearing=case_data['next_hearing'],
                    filing_date=case_data['filing_date'],
                    description=case_data['description'],
                    judge='Justice Sharma'
                )
                db.session.add(case)
            
            db.session.commit()
            print("✅ Database initialized with sample data!")
            print("👤 Login with: judge1 / password123")

if __name__ == '__main__':
    init_db()
    print("🚀 Starting Court Management System...")
    print("🌐 Open: http://localhost:5000")
    app.run(debug=True, port=5000)
