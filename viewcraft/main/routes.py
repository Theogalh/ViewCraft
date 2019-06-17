from viewcraft.main import bp
from viewcraft import db
from flask import render_template, flash, redirect, url_for, request, current_app
from viewcraft.main.forms import EditProfileForm, PostForm, RosterForm, CharacterForm
from flask_login import current_user, logout_user, login_required
from viewcraft.models import User, UserPost, Roster
from datetime import datetime
from viewcraft.email import send_email


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = UserPost(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Home', form=form, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = UserPost.query.order_by(UserPost.creation_date.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(UserPost.creation_date.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items, prev_url=prev_url, next_url=next_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(original_username=current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your change have been saved.')
        send_email(('[ViewCraft] Edit Your Profile'),
                   sender=current_app.config['ADMINS'][0],
                   recipients=[current_user.email],
                   text_body=render_template('email/startup.txt'),
                   html_body=render_template('email/startup.html'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('main.index'))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('main.user', username=username))


@bp.route('/follow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.index'))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are unfollowing {}!'.format(username))
    return redirect(url_for('main.user', username=username))


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/rosters', methods=['POST', 'GET'])
@login_required
def rosters():
    form = RosterForm()

    if form.validate_on_submit():
        for roster in current_user.rosters:
            if roster.name == form.rosterName.data.capitalize():
                flash('A roster with this name already exists.')
                return redirect(url_for('main.rosters'))
        roster = Roster(name=form.rosterName.data.capitalize(), owner=current_user)
        db.session.add(roster)
        db.session.commit()
        flash('You create a roster {}'.format(form.rosterName.data))

    return render_template('rosters.html', title='Rosters', form=form, rosters=current_user.rosters)


@bp.route('/rosters/<rosterName>', methods=['POST', 'GET'])
@login_required
def roster(rosterName):
    form = CharacterForm()
    roster = Roster.query.filter_by(name=rosterName, user_id=current_user.id).first_or_404()
    if form.validate_on_submit():
        pass
    return render_template('roster.html', roster=roster, form=form)
