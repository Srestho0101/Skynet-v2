from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Post, User, Like
from app.forms import PostForm
from app.utils import save_upload_file, delete_post_file

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/feed')
@login_required
def feed():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('feed.html', posts=posts)

@main_bp.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()
    return render_template('profile.html', user=user, posts=posts)

@main_bp.route('/profile')
@login_required
def my_profile():
    return redirect(url_for('main.profile', user_id=current_user.id))

@main_bp.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        image_path = None
        if form.image.data:
            image_path = save_upload_file(form.image.data, current_app.config)
        post = Post(
            user_id=current_user.id,
            content=form.content.data,
            image_path=image_path
        )
        try:
            db.session.add(post)
            db.session.commit()
            flash('Post created successfully!', 'success')
            return redirect(url_for('main.feed'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating post: {str(e)}', 'error')
    return render_template('create_post.html', form=form)

@main_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash('You can only edit your own posts', 'error')
        return redirect(url_for('main.feed'))
    form = PostForm()
    if form.validate_on_submit():
        if form.image.data:
            delete_post_file(post.image_path, current_app.config)
            post.image_path = save_upload_file(form.image.data, current_app.config)
        post.content = form.content.data
        try:
            db.session.commit()
            flash('Post updated successfully!', 'success')
            return redirect(url_for('main.feed'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating post: {str(e)}', 'error')
    elif request.method == 'GET':
        form.content.data = post.content
    return render_template('create_post.html', form=form, post=post)

@main_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash('You can only delete your own posts', 'error')
        return redirect(url_for('main.feed'))
    try:
        delete_post_file(post.image_path, current_app.config)
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting post: {str(e)}', 'error')
    return redirect(url_for('main.feed'))

@main_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    existing_like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    try:
        if existing_like:
            db.session.delete(existing_like)
            message = 'Post unliked'
        else:
            like = Like(user_id=current_user.id, post_id=post_id)
            db.session.add(like)
            message = 'Post liked'
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Error liking post: {str(e)}', 'error')
        return redirect(url_for('main.feed'))
    return redirect(request.referrer or url_for('main.feed'))
