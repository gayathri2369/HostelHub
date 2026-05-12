from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from . import db
from .models import Item, Message, Notification, Rating, Transaction, User


api_bp = Blueprint('api', __name__)


def notify(user_id, message):
    note = Notification(user_id=user_id, message=message)
    db.session.add(note)


def message_to_dict(message):
    return {
        'id': message.id,
        'sender_id': message.sender_id,
        'receiver_id': message.receiver_id,
        'sender_name': message.sender.name,
        'content': message.content,
        'created_at': message.created_at.isoformat(),
    }


@api_bp.route('/items', methods=['GET'])
@login_required
def api_items():
    category = request.args.get('category', '')
    keyword = request.args.get('keyword', '')
    max_price = request.args.get('max_price', '')

    query = Item.query
    if category:
        query = query.filter(Item.category.ilike(f'%{category}%'))
    if keyword:
        query = query.filter((Item.title.ilike(f'%{keyword}%')) | (Item.description.ilike(f'%{keyword}%')))
    if max_price:
        try:
            query = query.filter(Item.price <= float(max_price))
        except ValueError:
            return jsonify({'error': 'Invalid max_price'}), 400

    items = query.order_by(Item.created_at.desc()).all()
    return jsonify([
        {
            'id': i.id,
            'title': i.title,
            'description': i.description,
            'category': i.category,
            'price': i.price,
            'status': i.status,
            'seller': i.seller.name,
            'hostel_name': i.seller.hostel_name,
            'room_number': i.seller.room_number,
        }
        for i in items
    ])


@api_bp.route('/messages/<int:user_id>', methods=['GET'])
@login_required
def get_messages(user_id):
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id))
        | ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()

    return jsonify([message_to_dict(m) for m in messages])


@api_bp.route('/messages/<int:user_id>', methods=['POST'])
@login_required
def send_message(user_id):
    receiver = User.query.get_or_404(user_id)
    content = (request.json or {}).get('content', '').strip()
    if not content:
        return jsonify({'error': 'Message cannot be empty'}), 400

    msg = Message(sender_id=current_user.id, receiver_id=receiver.id, content=content)
    db.session.add(msg)
    notify(receiver.id, f'{current_user.name} sent you a message.')
    db.session.commit()
    return jsonify({'success': True, 'message': message_to_dict(msg)})


@api_bp.route('/transactions/request/<int:item_id>', methods=['POST'])
@login_required
def request_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.seller_id == current_user.id:
        return jsonify({'error': 'You cannot request your own item'}), 400
    if item.status != 'available':
        return jsonify({'error': 'Item is not available'}), 400

    txn = Transaction(item_id=item.id, buyer_id=current_user.id, seller_id=item.seller_id, status='requested')
    db.session.add(txn)
    notify(item.seller_id, f'{current_user.name} requested your item "{item.title}".')
    db.session.commit()
    return jsonify({'success': True, 'transaction_id': txn.id})


@api_bp.route('/transactions/<int:txn_id>/status', methods=['POST'])
@login_required
def update_transaction_status(txn_id):
    txn = Transaction.query.get_or_404(txn_id)
    new_status = (request.json or {}).get('status', '').strip().lower()

    if current_user.id != txn.seller_id:
        return jsonify({'error': 'Only seller can update status'}), 403

    if new_status not in {'accepted', 'rejected', 'completed'}:
        return jsonify({'error': 'Invalid status'}), 400

    txn.status = new_status
    if new_status == 'completed':
        txn.item.status = 'sold'
    notify(txn.buyer_id, f'Transaction for "{txn.item.title}" is now {new_status}.')
    db.session.commit()
    return jsonify({'success': True})


@api_bp.route('/ratings', methods=['POST'])
@login_required
def submit_rating():
    data = request.json or {}
    rated_user_id = data.get('rated_user_id')
    score = data.get('score')
    comment = (data.get('comment') or '').strip()
    transaction_id = data.get('transaction_id')

    if not rated_user_id or score is None:
        return jsonify({'error': 'rated_user_id and score are required'}), 400

    try:
        score = int(score)
    except (ValueError, TypeError):
        return jsonify({'error': 'Score must be an integer'}), 400

    if score < 1 or score > 5:
        return jsonify({'error': 'Score must be between 1 and 5'}), 400

    if int(rated_user_id) == current_user.id:
        return jsonify({'error': 'Cannot rate yourself'}), 400

    rating = Rating(
        rater_user_id=current_user.id,
        rated_user_id=int(rated_user_id),
        transaction_id=transaction_id,
        score=score,
        comment=comment,
    )
    db.session.add(rating)
    db.session.commit()
    return jsonify({'success': True})


@api_bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    notes = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(20).all()
    return jsonify([
        {
            'id': n.id,
            'message': n.message,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat(),
        }
        for n in notes
    ])


@api_bp.route('/notifications/<int:note_id>/read', methods=['POST'])
@login_required
def mark_notification_read(note_id):
    note = Notification.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        return jsonify({'error': 'Forbidden'}), 403
    note.is_read = True
    db.session.commit()
    return jsonify({'success': True})
