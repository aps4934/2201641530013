from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.models.url_model import Url
from src.services.url_service import generate_shortcode, save_url_record, is_url_unique

create_short_url_bp = Blueprint('create_short_url', __name__)

@create_short_url_bp.route('/shorturls', methods=['POST'])
def create_short_url():
    data = request.json
    original_url = data.get('url')
    shortcode = data.get('shortcode')
    expiry = data.get('expiry')

    if not original_url:
        return jsonify({'error': 'URL is required'}), 400

    if not is_url_unique(original_url, shortcode):
        return jsonify({'error': 'Shortcode must be unique'}), 400

    if not shortcode:
        shortcode = generate_shortcode()

    expiry_time = None
    if expiry:
        expiry_time = datetime.utcnow() + timedelta(days=expiry)

    url_record = Url(
        original_url=original_url,
        shortcode=shortcode,
        expiry=expiry_time,
        created_at=datetime.utcnow(),
        click_count=0,
        click_logs=[]
    )

    save_url_record(url_record)

    return jsonify({
        'shortcode': shortcode,
        'original_url': original_url,
        'expiry': expiry_time.isoformat() if expiry_time else None,
        'created_at': url_record.created_at.isoformat()
    }), 201