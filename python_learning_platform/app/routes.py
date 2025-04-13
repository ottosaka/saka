from flask import render_template, redirect, url_for, flash, request, send_from_directory
import os
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db
from app.forms import RegisterForm, LoginForm
from app.models import User, Resource, Post, Comment

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('auth/login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/resources')
def resources():
    search_query = request.args.get('search', '')
    selected_category = request.args.get('category', '')

    query = Resource.query
    if search_query:
        query = query.filter(Resource.title.contains(search_query))
    if selected_category:
        query = query.filter(Resource.category == selected_category)

    resources = query.order_by(Resource.created_at.desc()).all()
    categories = [category[0] for category in db.session.query(Resource.category).distinct()]
    return render_template('resources/index.html', resources=resources, categories=categories, selected_category=selected_category)

@app.route('/resources/download/<int:resource_id>')
def download_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    file_path = resource.file_path
    if file_path:
        # 假设文件存储在 app/static/resources 目录下
        base_dir = os.path.join(app.root_path, 'static', 'resources')
        return send_from_directory(base_dir, os.path.basename(file_path), as_attachment=True)
    else:
        flash('File not available for download.', 'danger')
        return redirect(url_for('resources'))

@app.route('/forum')
def forum():
    sort_option = request.args.get('sort', 'newest')
    if sort_option == 'newest':
        posts = Post.query.order_by(Post.created_at.desc()).all()
    elif sort_option == 'oldest':
        posts = Post.query.order_by(Post.created_at.asc()).all()
    elif sort_option == 'most_votes':
        posts = Post.query.order_by(Post.votes.desc()).all()
    return render_template('forum/posts.html', posts=posts, sort_option=sort_option)

@app.route('/forum/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
    return render_template('forum/post_detail.html', post=post, comments=comments)

@app.route('/forum/<int:post_id>/vote/<string:action>')
@login_required
def vote_post(post_id, action):
    post = Post.query.get_or_404(post_id)
    if action == 'up':
        post.votes += 1
    elif action == 'down':
        post.votes -= 1
    db.session.commit()
    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/forum/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content')
    if content:
        comment = Comment(content=content, user=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for('post_detail', post_id=post_id))