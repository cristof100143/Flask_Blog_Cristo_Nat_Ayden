from flask import render_template, request, Blueprint, flash, redirect, url_for
from flask_login import login_required, current_user
from flaskblog import db
from flaskblog.models import Post, Favorite, BlogPost, CommunityPost, CommunityReply, User
from flaskblog.forms import CommunityPostForm, CommunityReplyForm

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    
    # First, get Mr Zhukov's recipes (prioritize them)
    zhukov_user = User.query.filter_by(username='Mr Zhukov').first()
    if zhukov_user:
        zhukov_posts = Post.query.filter_by(user_id=zhukov_user.id).order_by(Post.date_posted.desc()).all()
        other_posts = Post.query.filter(Post.user_id != zhukov_user.id).order_by(Post.date_posted.desc()).all()
        # Combine with Zhukov's posts first
        all_posts = zhukov_posts + other_posts
    else:
        all_posts = Post.query.order_by(Post.date_posted.desc()).all()
    
    # Paginate the combined list
    per_page = 12  # Show more recipes on home page
    start = (page - 1) * per_page
    end = start + per_page
    posts = all_posts[start:end]
    
    # Create a simple pagination object
    total_posts = len(all_posts)
    total_pages = (total_posts + per_page - 1) // per_page
    
    class SimplePagination:
        def __init__(self, items, page, per_page, total, total_pages):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = total_pages
            self.has_next = page < total_pages
            self.has_prev = page > 1
            self.next_num = page + 1 if self.has_next else None
            self.prev_num = page - 1 if self.has_prev else None
    
    posts_paginated = SimplePagination(posts, page, per_page, total_posts, total_pages)
    
    # Get recipe of the day (highest rated or random)
    featured = Post.query.filter(Post.ratings.any()).order_by(db.func.random()).first()
    if not featured:
        featured = Post.query.order_by(db.func.random()).first()
    
    return render_template('home.html', posts=posts_paginated, featured=featured)


@main.route("/search")
def search():
    query = request.args.get('q', '')
    cuisine = request.args.get('cuisine', '')
    difficulty = request.args.get('difficulty', '')
    page = request.args.get('page', 1, type=int)
    
    posts_query = Post.query
    if query:
        posts_query = posts_query.filter(Post.title.contains(query) | Post.ingredients.contains(query) | Post.tags.contains(query))
    if cuisine:
        posts_query = posts_query.filter_by(cuisine=cuisine)
    if difficulty:
        posts_query = posts_query.filter_by(difficulty=difficulty)
    
    posts = posts_query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts, search_query=query, selected_cuisine=cuisine, selected_difficulty=difficulty)


@main.route("/shopping-list")
@login_required
def shopping_list():
    favorites = Favorite.query.filter_by(author=current_user).all()
    favorite_posts = [fav.post for fav in favorites]
    ingredients = []
    for post in favorite_posts:
        ingredients.extend(post.ingredients.split('\n'))
    # Remove duplicates and clean
    unique_ingredients = list(set(ing.strip() for ing in ingredients if ing.strip()))
    return render_template('shopping_list.html', ingredients=unique_ingredients)


@main.route("/about")
def about():
    return render_template('about.html', title='About')


@main.route("/recipes")
def recipes():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=12)
    return render_template('recipes.html', posts=posts, title='Recipes')


@main.route("/smart-search")
def smart_search():
    return render_template('smart_search.html', title='Smart Search')


@main.route("/cultures")
def cultures():
    cuisines = db.session.query(Post.cuisine).distinct().all()
    cuisine_list = [c[0] for c in cuisines if c[0]]
    return render_template('cultures.html', cuisines=cuisine_list, title='Cultures')


@main.route("/challenges")
def challenges():
    return render_template('challenges.html', title='Challenges')


@main.route("/blog")
def blog():
    page = request.args.get('page', 1, type=int)
    blog_posts = BlogPost.query.order_by(BlogPost.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('blog.html', title='Blog', blog_posts=blog_posts)


@main.route("/blog/<int:blog_id>")
def blog_post(blog_id):
    blog_post = BlogPost.query.get_or_404(blog_id)
    blog_posts = BlogPost.query.order_by(BlogPost.date_posted.desc()).limit(4).all()
    return render_template('blog_post.html', title=blog_post.title, blog_post=blog_post, blog_posts=blog_posts)


@main.route("/community")
@login_required
def community():
    page = request.args.get('page', 1, type=int)
    posts = CommunityPost.query.order_by(CommunityPost.date_posted.desc()).paginate(page=page, per_page=10)
    form = CommunityPostForm()
    return render_template('community.html', title='Community', posts=posts, form=form)


@main.route("/community/new", methods=['GET', 'POST'])
@login_required
def new_community_post():
    form = CommunityPostForm()
    if form.validate_on_submit():
        post = CommunityPost(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.community'))
    return render_template('create_community_post.html', title='New Community Post', form=form, legend='New Community Post')


@main.route("/community/<int:post_id>")
@login_required
def community_post(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    replies = CommunityReply.query.filter_by(post_id=post_id).order_by(CommunityReply.date_posted.asc()).all()
    form = CommunityReplyForm()
    return render_template('community_post.html', title=post.title, post=post, replies=replies, form=form)


@main.route("/community/<int:post_id>/reply", methods=['POST'])
@login_required
def reply_community_post(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    form = CommunityReplyForm()
    if form.validate_on_submit():
        reply = CommunityReply(content=form.content.data, author=current_user, parent_post=post)
        db.session.add(reply)
        db.session.commit()
        flash('Your reply has been posted!', 'success')
    return redirect(url_for('main.community_post', post_id=post_id))


@main.route("/admin")
@login_required
def admin():
    if current_user.username != 'admin':
        abort(403)
    users_count = User.query.count()
    posts_count = Post.query.count()
    comments_count = Comment.query.count()
    return render_template('admin.html', title='Admin', users_count=users_count, posts_count=posts_count, comments_count=comments_count)
