from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db
from models import User, BlogPost, Comment

@app.route('/')
def index():
    posts = BlogPost.query.order_by(BlogPost.timestamp.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.timestamp.asc()).all()

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('Please log in to comment.')
            return redirect(url_for('login'))

        comment_text = request.form['comment']
        new_comment = Comment(content=comment_text, user_id=current_user.id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('post', post_id=post_id))

    return render_template('post.html', post=post, comments=comments)

@app.route('/admin/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if not current_user.is_admin:
        flash('Unauthorized: Only admins can post.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_post = BlogPost(title=title, content=content, author_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        flash('Blog posted successfully!')
        return redirect(url_for('index'))

    return render_template('admin_dashboard.html')
