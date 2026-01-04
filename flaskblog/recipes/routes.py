from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.models import Post, Comment, Rating, Favorite
from flaskblog.recipes.forms import PostForm, CommentForm

posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, ingredients=form.ingredients.data, instructions=form.instructions.data,
                    prep_time=form.prep_time.data, cook_time=form.cook_time.data, servings=form.servings.data,
                    cuisine=form.cuisine.data, difficulty=form.difficulty.data, tags=form.tags.data,
                    author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your recipe has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Recipe',
                           form=form, legend='New Recipe')


@posts.route("/post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You must be logged in to comment.', 'danger')
            return redirect(url_for('users.login'))
        comment = Comment(content=form.content.data, author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    return render_template('post.html', title=post.title, post=post, form=form)


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.ingredients = form.ingredients.data
        post.instructions = form.instructions.data
        post.prep_time = form.prep_time.data
        post.cook_time = form.cook_time.data
        post.servings = form.servings.data
        post.cuisine = form.cuisine.data
        post.difficulty = form.difficulty.data
        post.tags = form.tags.data
        db.session.commit()
        flash('Your recipe has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.ingredients.data = post.ingredients
        form.instructions.data = post.instructions
        form.prep_time.data = post.prep_time
        form.cook_time.data = post.cook_time
        form.servings.data = post.servings
        form.cuisine.data = post.cuisine
        form.difficulty.data = post.difficulty
        form.tags.data = post.tags
    return render_template('create_post.html', title='Update Recipe',
                           form=form, legend='Update Recipe')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))


@posts.route("/post/<int:post_id>/rate/<int:rating>", methods=['POST'])
@login_required
def rate_post(post_id, rating):
    if rating < 1 or rating > 5:
        abort(400)
    post = Post.query.get_or_404(post_id)
    existing_rating = Rating.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing_rating:
        existing_rating.value = rating
    else:
        new_rating = Rating(value=rating, author=current_user, post=post)
        db.session.add(new_rating)
    db.session.commit()
    flash(f'Rated {rating} stars!', 'success')
    return redirect(url_for('posts.post', post_id=post_id))


@posts.route("/post/<int:post_id>/favorite", methods=['POST'])
@login_required
def favorite_post(post_id):
    post = Post.query.get_or_404(post_id)
    existing_fav = Favorite.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing_fav:
        db.session.delete(existing_fav)
        flash('Removed from favorites!', 'info')
    else:
        fav = Favorite(author=current_user, post=post)
        db.session.add(fav)
        flash('Added to favorites!', 'success')
    db.session.commit()
    return redirect(url_for('posts.post', post_id=post_id))
