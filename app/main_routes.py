import os
from datetime import datetime
from uuid import uuid4
from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from flask_login import current_user, login_required
from sqlalchemy import case
from werkzeug.utils import secure_filename
from . import db
from .models import Item, Message, Notification, Rating, Transaction, User


main_bp = Blueprint('main', __name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_chat_contacts():
    contacts = User.query.filter(User.id != current_user.id).all()
    for contact in contacts:
        contact.last_message = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == contact.id))
            | ((Message.sender_id == contact.id) & (Message.receiver_id == current_user.id))
        ).order_by(Message.created_at.desc()).first()

    return sorted(
        contacts,
        key=lambda contact: contact.last_message.created_at if contact.last_message else datetime.min,
        reverse=True,
    )


@main_bp.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    category = request.args.get('category', '').strip()
    keyword = request.args.get('keyword', '').strip()
    max_price = request.args.get('max_price', '').strip()
    mine = request.args.get('mine') == '1'

    query = Item.query
    if mine:
        query = query.filter(Item.seller_id == current_user.id)
    if category:
        query = query.filter(Item.category.ilike(f'%{category}%'))
    if keyword:
        query = query.filter((Item.title.ilike(f'%{keyword}%')) | (Item.description.ilike(f'%{keyword}%')))
    if max_price:
        try:
            query = query.filter(Item.price <= float(max_price))
        except ValueError:
            flash('Invalid max price filter.', 'warning')

    items = query.order_by(
        case((Item.seller_id == current_user.id, 0), else_=1),
        Item.created_at.desc(),
    ).all()
    categories = sorted({i.category for i in Item.query.all()})
    my_item_count = Item.query.filter_by(seller_id=current_user.id).count()
    return render_template('items/index.html', items=items, categories=categories, mine=mine, my_item_count=my_item_count)


@main_bp.route('/items/new', methods=['GET', 'POST'])
@login_required
def create_item():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        status = request.form.get('status', 'available').strip()

        try:
            price = float(request.form.get('price', '0'))
        except ValueError:
            flash('Price must be numeric.', 'danger')
            return redirect(url_for('main.create_item'))

        image_file = request.files.get('image')
        image_filename = None

        if image_file and image_file.filename:
            if not allowed_file(image_file.filename):
                flash('Invalid image type. Use png/jpg/jpeg/gif.', 'danger')
                return redirect(url_for('main.create_item'))
            original_name = secure_filename(image_file.filename)
            image_filename = f"{uuid4().hex}_{original_name}"
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)

        if not all([title, description, category]):
            flash('Title, description, and category are required.', 'danger')
            return redirect(url_for('main.create_item'))

        item = Item(
            title=title,
            description=description,
            category=category,
            price=price,
            status=status,
            image_filename=image_filename,
            seller_id=current_user.id,
        )
        db.session.add(item)
        db.session.commit()
        flash('Item created successfully.', 'success')
        return redirect(url_for('main.index'))

    return render_template('items/form.html', item=None)


@main_bp.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.seller_id != current_user.id:
        flash('You can only edit your own item.', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        item.title = request.form.get('title', '').strip()
        item.description = request.form.get('description', '').strip()
        item.category = request.form.get('category', '').strip()
        item.status = request.form.get('status', 'available').strip()

        try:
            item.price = float(request.form.get('price', '0'))
        except ValueError:
            flash('Price must be numeric.', 'danger')
            return redirect(url_for('main.edit_item', item_id=item.id))

        image_file = request.files.get('image')
        if image_file and image_file.filename:
            if not allowed_file(image_file.filename):
                flash('Invalid image type.', 'danger')
                return redirect(url_for('main.edit_item', item_id=item.id))
            original_name = secure_filename(image_file.filename)
            image_filename = f"{uuid4().hex}_{original_name}"
            image_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename))
            item.image_filename = image_filename

        db.session.commit()
        flash('Item updated.', 'success')
        return redirect(url_for('main.index'))

    return render_template('items/form.html', item=item)


@main_bp.route('/items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.seller_id != current_user.id:
        flash('You can only delete your own item.', 'danger')
        return redirect(url_for('main.index'))

    transactions = Transaction.query.filter_by(item_id=item.id).all()
    transaction_ids = [txn.id for txn in transactions]
    if transaction_ids:
        Rating.query.filter(Rating.transaction_id.in_(transaction_ids)).delete(synchronize_session=False)
        for txn in transactions:
            db.session.delete(txn)

    image_filename = item.image_filename
    db.session.delete(item)
    db.session.commit()

    if image_filename:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)

    flash('Item deleted.', 'info')
    return redirect(url_for('main.index'))


@main_bp.route('/chat/<int:user_id>')
@login_required
def chat_with(user_id):
    other_user = User.query.get_or_404(user_id)
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == other_user.id))
        | ((Message.sender_id == other_user.id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()

    contacts = get_chat_contacts()
    return render_template('chat/chat.html', other_user=other_user, messages=messages, contacts=contacts)


@main_bp.route('/chat')
@login_required
def chat_home():
    contacts = get_chat_contacts()
    return render_template('chat/chat_home.html', contacts=contacts)


@main_bp.route('/transactions')
@login_required
def transactions():
    txns = Transaction.query.filter(
        (Transaction.buyer_id == current_user.id) | (Transaction.seller_id == current_user.id)
    ).order_by(Transaction.created_at.desc()).all()
    return render_template('transactions/index.html', transactions=txns)


@main_bp.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    ratings = Rating.query.filter_by(rated_user_id=user.id).order_by(Rating.created_at.desc()).all()
    return render_template('users/profile.html', profile_user=user, ratings=ratings)


@main_bp.route('/notifications')
@login_required
def notifications():
    notes = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('users/notifications.html', notifications=notes)


@main_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    from flask import send_from_directory

    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
