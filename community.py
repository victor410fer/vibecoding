from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from database import db, Post, Comment, CTFChallenge
from datetime import datetime

community_bp = Blueprint('community', __name__)

@community_bp.route('/community')
def community_home():
    """Community forum homepage"""
    page = request.args.get('page', 1, type=int)
    post_type = request.args.get('type', 'all')
    
    query = Post.query.filter_by(is_locked=False)
    
    if post_type != 'all':
        query = query.filter_by(post_type=post_type)
    
    # Get pinned posts first
    pinned_posts = Post.query.filter_by(is_pinned=True).order_by(Post.created_at.desc()).all()
    
    # Get regular posts
    posts = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    
    return render_template('community.html',
                         posts=posts,
                         pinned_posts=pinned_posts,
                         post_type=post_type)

@community_bp.route('/community/post/<int:post_id>')
def view_post(post_id):
    """View individual post"""
    post = Post.query.get_or_404(post_id)
    post.views += 1  # Track views
    db.session.commit()
    
    return render_template('post_detail.html', post=post)

@community_bp.route('/community/new', methods=['GET', 'POST'])
@login_required
def new_post():
    """Create new post"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        post_type = request.form.get('type', 'discussion')
        
        if not title or not content:
            flash('Title and content are required!', 'danger')
            return redirect(url_for('community.new_post'))
        
        post = Post(
            title=title,
            content=content,
            post_type=post_type,
            user_id=current_user.id
        )
        
        db.session.add(post)
        db.session.commit()
        
        flash('Post created successfully!', 'success')
        return redirect(url_for('community.view_post', post_id=post.id))
    
    return render_template('new_post.html')

@community_bp.route('/community/comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    """Add comment to post"""
    content = request.form.get('content')
    parent_id = request.form.get('parent_id', type=int)
    
    if not content:
        flash('Comment cannot be empty!', 'danger')
        return redirect(url_for('community.view_post', post_id=post_id))
    
    comment = Comment(
        content=content,
        user_id=current_user.id,
        post_id=post_id,
        parent_id=parent_id if parent_id else None
    )
    
    db.session.add(comment)
    db.session.commit()
    
    flash('Comment added!', 'success')
    return redirect(url_for('community.view_post', post_id=post_id))

@community_bp.route('/ctf')
def ctf_challenges():
    """CTF challenges list"""
    challenges = CTFChallenge.query.filter_by(is_active=True).order_by(CTFChallenge.difficulty).all()
    
    # Group by category
    challenges_by_category = {}
    for challenge in challenges:
        if challenge.category not in challenges_by_category:
            challenges_by_category[challenge.category] = []
        challenges_by_category[challenge.category].append(challenge)
    
    return render_template('ctf.html', challenges_by_category=challenges_by_category)

@community_bp.route('/ctf/submit/<int:challenge_id>', methods=['POST'])
@login_required
def submit_ctf_flag(challenge_id):
    """Submit CTF flag"""
    challenge = CTFChallenge.query.get_or_404(challenge_id)
    flag = request.form.get('flag', '').strip()
    
    if flag == challenge.flag:
        # In a real app, you'd record the solve in a database
        flash(f'Correct! You earned {challenge.points} points!', 'success')
    else:
        flash('Incorrect flag! Try again.', 'danger')
    
    return redirect(url_for('community.ctf_challenges'))
