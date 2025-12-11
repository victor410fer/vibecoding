"""
Hacker Hub - Complete Web Application
Production-ready with all console features
"""

import os
import json
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_mail import Mail
from config import Config
from database import db, User, Tool, UserTool, Post, Comment, CTFChallenge

# Initialize extensions
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Import blueprints
    from auth import auth_bp
    from tools import tools_bp
    from community import community_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(tools_bp)
    app.register_blueprint(community_bp)
    
    # ==================== CORE ROUTES ====================
    
    @app.route('/')
    def index():
        """Landing page"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Main dashboard"""
        user = current_user
        
        # Get user stats
        stats = {
            'followed_tools': len(user.followed_tools),
            'posts': len(user.posts),
            'comments': len(user.comments)
        }
        
        # Get recent tools
        recent_tools = Tool.query.order_by(Tool.created_at.desc()).limit(5).all()
        
        # Get recommended tools based on experience
        if user.experience == 'beginner':
            recommended = Tool.query.filter_by(difficulty='beginner').limit(3).all()
        elif user.experience == 'intermediate':
            recommended = Tool.query.filter(Tool.difficulty.in_(['beginner', 'intermediate'])).limit(3).all()
        else:
            recommended = Tool.query.limit(3).all()
        
        return render_template('dashboard.html', 
                             user=user, 
                             stats=stats,
                             recent_tools=recent_tools,
                             recommended_tools=recommended)
    
    @app.route('/experience', methods=['GET', 'POST'])
    @login_required
    def experience():
        """Set experience level"""
        if request.method == 'POST':
            experience_level = request.form.get('experience')
            if experience_level in ['beginner', 'intermediate', 'advanced', 'elite']:
                current_user.experience = experience_level
                db.session.commit()
                flash('Experience level updated!', 'success')
                return redirect(url_for('resources'))
        
        return render_template('experience.html')
    
    @app.route('/resources', methods=['GET', 'POST'])
    @login_required
    def resources():
        """Set available resources"""
        if request.method == 'POST':
            resources = request.form.getlist('resources')
            current_user.set_resources(resources)
            db.session.commit()
            flash('Resources updated!', 'success')
            return redirect(url_for('dashboard'))
        
        return render_template('resources.html')
    
    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        """User profile"""
        if request.method == 'POST':
            # Update profile
            username = request.form.get('username')
            email = request.form.get('email')
            bio = request.form.get('bio', '')
            
            # Check if username is taken (excluding current user)
            if username != current_user.username:
                existing = User.query.filter_by(username=username).first()
                if existing:
                    flash('Username already taken!', 'danger')
                    return redirect(url_for('profile'))
            
            current_user.username = username
            current_user.email = email
            db.session.commit()
            flash('Profile updated!', 'success')
            return redirect(url_for('profile'))
        
        return render_template('profile.html', user=current_user)
    
    @app.route('/search')
    def search():
        """Search across tools, posts, and users"""
        query = request.args.get('q', '')
        results = {
            'tools': [],
            'posts': [],
            'users': []
        }
        
        if query:
            # Search tools
            tools = Tool.query.filter(
                Tool.name.ilike(f'%{query}%') | 
                Tool.description.ilike(f'%{query}%') |
                Tool.category.ilike(f'%{query}%')
            ).limit(10).all()
            results['tools'] = tools
            
            # Search posts
            posts = Post.query.filter(
                Post.title.ilike(f'%{query}%') |
                Post.content.ilike(f'%{query}%')
            ).limit(10).all()
            results['posts'] = posts
            
            # Search users
            users = User.query.filter(User.username.ilike(f'%{query}%')).limit(10).all()
            results['users'] = users
        
        return render_template('search.html', query=query, results=results)
    
    @app.route('/api/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'users': User.query.count(),
            'tools': Tool.query.count(),
            'posts': Post.query.count()
        })
    
    # ==================== ERROR HANDLERS ====================
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return render_template('500.html'), 500
    
    # ==================== CONTEXT PROCESSORS ====================
    
    @app.context_processor
    def inject_user():
        """Inject current user into all templates"""
        return dict(current_user=current_user)
    
    @app.context_processor
    def inject_tools_categories():
        """Inject tool categories for navigation"""
        categories = {}
        if Tool.query.first():  # Only if database has tools
            platforms = db.session.query(Tool.platform).distinct().all()
            for platform in platforms:
                cats = db.session.query(Tool.category).filter_by(platform=platform[0]).distinct().all()
                categories[platform[0]] = [cat[0] for cat in cats]
        return dict(tool_categories=categories)
    
    # ==================== INITIAL DATA ====================
    
    @app.before_first_request
    def create_tables_and_seed():
        """Create tables and seed initial data"""
        db.create_all()
        
        # Seed tools if empty
        if Tool.query.count() == 0:
            seed_tools()
            print("✅ Tools database seeded!")
        
        print("✅ Database initialized!")
    
    def seed_tools():
        """Seed initial tools from console prototype"""
        tools_data = [
            # Linux - Kali
            ("Nmap", "Linux", "Information Gathering", "Kali Linux", 
             "Network discovery and security auditing", "Beginner"),
            ("Metasploit Framework", "Linux", "Exploitation Tools", "Kali Linux",
             "Penetration testing platform", "Intermediate"),
            ("Wireshark", "Linux", "Sniffing & Spoofing", "Kali Linux",
             "Network protocol analyzer", "Beginner"),
            ("Burp Suite", "Linux", "Web Application Analysis", "Kali Linux",
             "Web vulnerability scanner", "Intermediate"),
            ("John the Ripper", "Linux", "Password Attacks", "Kali Linux",
             "Password cracker", "Intermediate"),
            ("Aircrack-ng", "Linux", "Wireless Attacks", "Kali Linux",
             "WiFi security auditing tools", "Intermediate"),
            ("Ghidra", "Linux", "Reverse Engineering", "Kali Linux",
             "Software reverse engineering suite", "Advanced"),
            ("Autopsy", "Linux", "Forensics", "Kali Linux",
             "Digital forensics platform", "Intermediate"),
            
            # Phone - Android
            ("JADX", "Phone", "Reverse Engineering", "Android",
             "Dex to Java decompiler", "Beginner"),
            ("APKTool", "Phone", "Reverse Engineering", "Android",
             "Reverse engineering APK files", "Intermediate"),
            ("MobSF", "Phone", "Forensics", "Android",
             "Mobile Security Framework", "Intermediate"),
            
            # Windows
            ("IDA Pro", "Windows", "Reverse Engineering", "General",
             "Interactive disassembler", "Advanced"),
            ("x64dbg", "Windows", "Reverse Engineering", "General",
             "Open-source debugger", "Intermediate"),
            
            # Web
            ("Burp Suite Professional", "Web", "Bug Bounty", "General",
             "Web vulnerability scanner", "Intermediate"),
            ("OWASP ZAP", "Web", "Bug Bounty", "General",
             "Web app security scanner", "Beginner"),
            ("Sublist3r", "Web", "Reconnaissance", "General",
             "Subdomain enumeration tool", "Beginner"),
        ]
        
        for name, platform, category, subcategory, description, difficulty in tools_data:
            tool = Tool(
                name=name,
                platform=platform,
                category=category,
                subcategory=subcategory,
                description=description,
                difficulty=difficulty.lower(),
                is_verified=True
            )
            db.session.add(tool)
        
        db.session.commit()
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
