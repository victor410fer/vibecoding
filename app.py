"""
Hacker Hub - Web Version
Fixed for Vercel Deployment
"""

import os
import json
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, send_from_directory
from flask_cors import CORS

# ==================== FLASK CONFIGURATION ====================
# Get absolute paths for Vercel compatibility
current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(current_dir, 'static'),
    template_folder=os.path.join(current_dir, 'templates'),
    static_url_path='/static'
)

app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # Disable pretty JSON in production
CORS(app)

# ==================== STATIC FILE HANDLING ====================
@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files directly"""
    try:
        return send_from_directory('static', path)
    except:
        return "", 404

@app.after_request
def add_header(response):
    """Add cache headers for static files"""
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    return response

# ==================== DATABASE SIMULATION ====================
USERS_DB = {}
TOOLS_DB = {}

def load_tools():
    """Load tools from JSON file"""
    try:
        tools_path = os.path.join(current_dir, 'tools.json')
        if os.path.exists(tools_path):
            with open(tools_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading tools: {e}")
    
    # Fallback to default tools
    return initialize_default_tools()

def initialize_default_tools():
    """Initialize with default tools data"""
    return {
        "linux": {
            "kali": {
                "information_gathering": [
                    {"name": "Nmap", "desc": "Network discovery tool", "difficulty": "beginner", "command": "nmap -sV [target]"},
                    {"name": "theHarvester", "desc": "Email/subdomain enumeration", "difficulty": "beginner", "command": "theHarvester -d [domain] -b all"}
                ],
                "vulnerability_analysis": [
                    {"name": "OpenVAS", "desc": "Vulnerability scanner", "difficulty": "intermediate", "command": "gvm-start"},
                    {"name": "Nikto", "desc": "Web server scanner", "difficulty": "beginner", "command": "nikto -h [url]"}
                ]
            },
            "ubuntu": {
                "container_security": [
                    {"name": "Docker Bench", "desc": "Docker security audit", "difficulty": "intermediate", "command": "git clone https://github.com/docker/docker-bench-security.git"}
                ]
            },
            "termux": {
                "mobile_hacking": [
                    {"name": "Termux-API", "desc": "Access phone features", "difficulty": "beginner", "command": "pkg install termux-api"}
                ]
            }
        },
        "windows": {
            "general": {
                "reverse_engineering": [
                    {"name": "IDA Pro", "desc": "Interactive disassembler", "difficulty": "advanced", "command": ""},
                    {"name": "x64dbg", "desc": "Open-source debugger", "difficulty": "intermediate", "command": ""}
                ]
            }
        },
        "web": {
            "general": {
                "bug_bounty": [
                    {"name": "Burp Suite", "desc": "Web vulnerability scanner", "difficulty": "intermediate", "command": ""}
                ]
            }
        }
    }

def save_tools():
    """Save tools to JSON file"""
    try:
        tools_path = os.path.join(current_dir, 'tools.json')
        with open(tools_path, 'w') as f:
            json.dump(TOOLS_DB, f, indent=2)
    except Exception as e:
        print(f"Error saving tools: {e}")

# Initialize tools
TOOLS_DB = load_tools()

# ==================== ROUTES ====================
@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
                
            username = data.get('username')
            email = data.get('email')
            experience = data.get('experience', 'beginner')
            
            if not username or not email:
                return jsonify({'error': 'Username and email required'}), 400
            
            if username in USERS_DB:
                return jsonify({'error': 'Username already exists'}), 400
            
            user = {
                'id': len(USERS_DB) + 1,
                'username': username,
                'email': email,
                'experience': experience,
                'resources': [],
                'followed_tools': [],
                'joined_date': datetime.now().isoformat(),
                'anonymous': False
            }
            
            USERS_DB[username] = user
            session['user'] = username
            
            return jsonify({
                'success': True,
                'user': user,
                'message': 'Account created successfully'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # GET request - render signup page
    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        # Simplified auth for demo
        if username in USERS_DB:
            session['user'] = username
            return jsonify({
                'success': True,
                'user': USERS_DB[username]
            })
        else:
            # Auto-create user for demo
            user = {
                'id': len(USERS_DB) + 1,
                'username': username,
                'experience': 'beginner',
                'resources': [],
                'followed_tools': [],
                'joined_date': datetime.now().isoformat(),
                'anonymous': False
            }
            USERS_DB[username] = user
            session['user'] = username
            
            return jsonify({
                'success': True,
                'user': user,
                'message': 'Auto-created account for demo'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/anonymous')
def anonymous():
    """Anonymous access"""
    session['user'] = 'anonymous_' + str(hash(datetime.now()))[:8]
    session['anonymous'] = True
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    if 'user' not in session:
        return redirect('/')
    
    user_data = USERS_DB.get(session['user'], {
        'username': session['user'],
        'anonymous': session.get('anonymous', False),
        'experience': 'beginner',
        'resources': [],
        'followed_tools': []
    })
    
    return render_template('dashboard.html', user=user_data)

@app.route('/api/tools')
def get_tools():
    """API endpoint for tools"""
    try:
        platform = request.args.get('platform')
        category = request.args.get('category')
        subcategory = request.args.get('subcategory')
        
        if platform:
            if category:
                if subcategory:
                    # Get specific subcategory
                    tools = TOOLS_DB.get(platform, {}).get(category, {}).get(subcategory, [])
                    return jsonify(tools)
                # Get all subcategories in category
                categories = TOOLS_DB.get(platform, {}).get(category, {})
                return jsonify(categories)
            # Get all categories in platform
            platforms = TOOLS_DB.get(platform, {})
            return jsonify(platforms)
        
        # Get all platforms
        return jsonify(TOOLS_DB)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search')
def search_tools():
    """Search tools"""
    try:
        query = request.args.get('q', '').lower()
        if not query or len(query) < 2:
            return jsonify([])
            
        results = []
        
        for platform, categories in TOOLS_DB.items():
            for category, subcategories in categories.items():
                for subcategory, tools in subcategories.items():
                    for tool in tools:
                        if (query in tool['name'].lower() or 
                            query in tool['desc'].lower() or
                            query in platform.lower()):
                            results.append({
                                **tool,
                                'platform': platform,
                                'category': category,
                                'subcategory': subcategory
                            })
        
        return jsonify(results[:20])  # Limit results
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/follow', methods=['POST'])
def follow_tool():
    """Follow a tool"""
    try:
        if 'user' not in session or session.get('anonymous'):
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        tool_name = data.get('tool')
        if not tool_name:
            return jsonify({'error': 'Tool name required'}), 400
        
        user = USERS_DB.get(session['user'])
        if user and tool_name not in user['followed_tools']:
            user['followed_tools'].append(tool_name)
        
        return jsonify({'success': True, 'tool': tool_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/unfollow', methods=['POST'])
def unfollow_tool():
    """Unfollow a tool"""
    try:
        if 'user' not in session or session.get('anonymous'):
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        tool_name = data.get('tool')
        if not tool_name:
            return jsonify({'error': 'Tool name required'}), 400
        
        user = USERS_DB.get(session['user'])
        if user and tool_name in user['followed_tools']:
            user['followed_tools'].remove(tool_name)
        
        return jsonify({'success': True, 'tool': tool_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/profile', methods=['GET', 'PUT'])
def user_profile():
    """Get or update user profile"""
    try:
        if 'user' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        username = session['user']
        
        if request.method == 'GET':
            user = USERS_DB.get(username, {
                'username': username,
                'anonymous': session.get('anonymous', False),
                'experience': 'beginner',
                'resources': [],
                'followed_tools': []
            })
            return jsonify(user)
        
        elif request.method == 'PUT':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
                
            if username in USERS_DB:
                # Update only allowed fields
                allowed_fields = ['experience', 'resources']
                for field in allowed_fields:
                    if field in data:
                        USERS_DB[username][field] = data[field]
                return jsonify({'success': True, 'user': USERS_DB[username]})
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect('/')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'users': len(USERS_DB),
        'tools': sum(
            len(tool) 
            for platform in TOOLS_DB.values() 
            for category in platform.values() 
            for subcategory in category.values() 
            for tool in subcategory
        )
    })

# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Endpoint not found'}), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500

# ==================== FAVICON & ROBOTS ====================
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt', mimetype='text/plain')

# ==================== LOCAL DEVELOPMENT ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Hacker Hub on port {port}")
    print(f"Static folder: {app.static_folder}")
    print(f"Template folder: {app.template_folder}")
    app.run(host='0.0.0.0', port=port, debug=True)
