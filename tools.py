from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from database import db, Tool, UserTool
import json

tools_bp = Blueprint('tools', __name__)

@tools_bp.route('/tools')
def tools_list():
    """Browse all tools"""
    page = request.args.get('page', 1, type=int)
    platform = request.args.get('platform', 'all')
    category = request.args.get('category', 'all')
    difficulty = request.args.get('difficulty', 'all')
    search = request.args.get('search', '')
    
    query = Tool.query
    
    # Apply filters
    if platform != 'all':
        query = query.filter_by(platform=platform)
    if category != 'all':
        query = query.filter_by(category=category)
    if difficulty != 'all':
        query = query.filter_by(difficulty=difficulty)
    if search:
        query = query.filter(Tool.name.ilike(f'%{search}%') | Tool.description.ilike(f'%{search}%'))
    
    # Get unique values for filter dropdowns
    platforms = [p[0] for p in db.session.query(Tool.platform).distinct().all()]
    categories = [c[0] for c in db.session.query(Tool.category).distinct().all()]
    difficulties = ['beginner', 'intermediate', 'advanced']
    
    # Paginate results
    tools = query.order_by(Tool.name).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('tools.html',
                         tools=tools,
                         platforms=platforms,
                         categories=categories,
                         difficulties=difficulties,
                         current_filters={
                             'platform': platform,
                             'category': category,
                             'difficulty': difficulty,
                             'search': search
                         })

@tools_bp.route('/tools/<int:tool_id>')
def tool_detail(tool_id):
    """View tool details"""
    tool = Tool.query.get_or_404(tool_id)
    
    # Check if user follows this tool
    is_following = False
    if current_user.is_authenticated:
        is_following = UserTool.query.filter_by(user_id=current_user.id, tool_id=tool.id).first() is not None
    
    # Increment view count (or download count)
    tool.downloads += 1
    db.session.commit()
    
    # Get related tools
    related_tools = Tool.query.filter_by(platform=tool.platform, category=tool.category).filter(Tool.id != tool.id).limit(4).all()
    
    return render_template('tool_detail.html',
                         tool=tool,
                         is_following=is_following,
                         related_tools=related_tools)

@tools_bp.route('/tools/follow/<int:tool_id>', methods=['POST'])
@login_required
def follow_tool(tool_id):
    """Follow or unfollow a tool"""
    tool = Tool.query.get_or_404(tool_id)
    
    existing = UserTool.query.filter_by(user_id=current_user.id, tool_id=tool.id).first()
    
    if existing:
        # Unfollow
        db.session.delete(existing)
        action = 'unfollowed'
    else:
        # Follow
        user_tool = UserTool(user_id=current_user.id, tool_id=tool.id)
        db.session.add(user_tool)
        action = 'followed'
    
    db.session.commit()
    
    if request.is_json:
        return jsonify({'success': True, 'action': action})
    
    flash(f'Tool {action}!', 'success')
    return redirect(url_for('tools.tool_detail', tool_id=tool_id))

@tools_bp.route('/my-tools')
@login_required
def my_tools():
    """User's followed tools"""
    user_tools = UserTool.query.filter_by(user_id=current_user.id).all()
    tools = [ut.tool for ut in user_tools]
    
    return render_template('my_tools.html', tools=tools)

@tools_bp.route('/api/tools/random')
def random_tools():
    """Get random tools for homepage"""
    import random
    tools = Tool.query.filter_by(is_verified=True).all()
    random_tools = random.sample(tools, min(6, len(tools)))
    
    tools_data = []
    for tool in random_tools:
        tools_data.append({
            'id': tool.id,
            'name': tool.name,
            'platform': tool.platform,
            'difficulty': tool.difficulty,
            'description': tool.description[:100] + '...' if len(tool.description) > 100 else tool.description
        })
    
    return jsonify(tools_data)

@tools_bp.route('/api/tools/search')
def api_search():
    """API endpoint for tool search"""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 10, type=int)
    
    if not query or len(query) < 2:
        return jsonify([])
    
    tools = Tool.query.filter(
        Tool.name.ilike(f'%{query}%') |
        Tool.description.ilike(f'%{query}%') |
        Tool.category.ilike(f'%{query}%') |
        Tool.subcategory.ilike(f'%{query}%')
    ).limit(limit).all()
    
    results = []
    for tool in tools:
        results.append({
            'id': tool.id,
            'name': tool.name,
            'platform': tool.platform,
            'category': tool.category,
            'difficulty': tool.difficulty,
            'description': tool.description[:150]
        })
    
    return jsonify(results)
