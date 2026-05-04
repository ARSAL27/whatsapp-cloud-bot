from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ceo-secret-key-123'
app.config['SQLALCHEMY_DATABASE_PATH'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ceo_database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['SQLALCHEMY_DATABASE_PATH']
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- DATABASE MODELS ---

class CEO(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class BotUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hwid = db.Column(db.String(100), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    expiry_date = db.Column(db.String(100), nullable=True)

# --- AUTH LOGIC ---

@login_manager.user_loader
def load_user(user_id):
    return CEO.query.get(int(user_id))

# --- ROUTES ---

@app.route('/')
@login_required
def dashboard():
    users = BotUser.query.all()
    total_users = len(users)
    active_users = len([u for u in users if u.is_active])
    return render_template('dashboard.html', users=users, total=total_users, active=active_users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = CEO.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid CEO Credentials!', 'danger')
    return render_template('login.html')

@app.route('/add_user', methods=['POST'])
@login_required
def add_user():
    name = request.form.get('name')
    hwid = request.form.get('hwid')
    if name and hwid:
        new_user = BotUser(name=name, hwid=hwid)
        db.session.add(new_user)
        db.session.commit()
        flash(f'User {name} added successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/toggle_user/<int:id>')
@login_required
def toggle_user(id):
    user = BotUser.query.get(id)
    if user:
        user.is_active = not user.is_active
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete_user/<int:id>')
@login_required
def delete_user(id):
    user = BotUser.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('dashboard'))

# --- API FOR THE BOT ---

@app.route('/api/verify/<hwid>')
def verify_hwid(hwid):
    user = BotUser.query.filter_by(hwid=hwid).first()
    if user:
        return jsonify({
            "status": "success",
            "is_active": user.is_active,
            "name": user.name
        })
    return jsonify({"status": "error", "message": "HWID Not Found"}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create default CEO if not exists
        if not CEO.query.filter_by(username='admin').first():
            hashed_pw = generate_password_hash('ceo123', method='pbkdf2:sha256')
            admin = CEO(username='admin', password=hashed_pw)
            db.session.add(admin)
            db.session.commit()
    
    # Support cloud hosting ports (Hugging Face / Heroku)
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
