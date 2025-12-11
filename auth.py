from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            if user.is_active:
                login_user(user, remember=remember)
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                flash('Logged in successfully!', 'success')
                
                # Redirect based on whether user has set experience
                if not user.experience or user.experience == 'none':
                    return redirect(url_for('experience'))
                elif not user.resources or user.resources == '[]':
                    return redirect(url_for('resources'))
                else:
                    return redirect(url_for('dashboard'))
            else:
                flash('Account is deactivated!', 'danger')
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        errors = []
        
        if len(username) < 3:
            errors.append('Username must be at least 3 characters')
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            errors.append('Invalid email address')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters')
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        # Check if username/email exists
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists')
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            # Create new user
            hashed_password = generate_password_hash(password)
            user = User(
                username=username,
                email=email,
                password_hash=hashed_password,
                experience='beginner',  # Default
                resources='[]',
                anonymous=False
            )
            
            db.session.add(user)
            db.session.commit()
            
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('signup.html')

@auth_bp.route('/anonymous')
def anonymous_entry():
    """Anonymous user access"""
    # Create a temporary anonymous user
    from datetime import datetime
    
    # Generate unique anonymous username
    import random
    import string
    anon_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    username = f'Anonymous_{anon_id}'
    
    # Create anonymous user in database
    user = User(
        username=username,
        email=f'{username}@anonymous.hackerhub',
        password_hash=generate_password_hash('anonymous'),  # Random hash
        experience='beginner',
        resources='[]',
        anonymous=True,
        is_active=True
    )
    
    db.session.add(user)
    db.session.commit()
    
    login_user(user)
    flash('Entering as anonymous user. Your data will not be saved permanently.', 'info')
    
    return redirect(url_for('dashboard'))

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@auth_bp.route('/api/check_username')
def check_username():
    """API endpoint to check if username is available"""
    username = request.args.get('username', '')
    if username:
        user = User.query.filter_by(username=username).first()
        return jsonify({'available': user is None})
    return jsonify({'available': False})
