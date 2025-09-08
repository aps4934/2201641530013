from flask import Blueprint, jsonify
from src.services.url_service import get_url_record
import json

stats_short_url_bp = Blueprint('stats_short_url', __name__)

@stats_short_url_bp.route('/shorturls/<string:shortcode>', methods=['GET'])
def stats_short_url(shortcode):
    """
    Return statistics for a shortcode:
    - total clicks
    - original URL
    - creation date
    - expiry date
    - detailed click logs (list)
    """
    record = get_url_record(shortcode)
    if not record:
        return jsonify({'error': 'Shortcode not found'}), 404

    # support both ORM object and dict-like record
    try:
        original = record.original_url
        created = record.created_at.isoformat() if record.created_at else None
        expiry = record.expiry.isoformat() if record.expiry else None
        clicks = record.click_count
        logs = record.click_logs
    except Exception:
        original = record.get('original_url')
        created = record.get('created_at').isoformat() if record.get('created_at') else None
        expiry = record.get('expiry').isoformat() if record.get('expiry') else None
        clicks = record.get('click_count', 0)
        logs = record.get('click_logs', [])

    # if logs stored as JSON string, try to decode
    if isinstance(logs, str):
        try:
            logs = json.loads(logs)
        except Exception:
            logs = []

    return jsonify({
        'original_url': original,
        'creation_date': created,
        'expiry': expiry,
        'click_count': clicks,
        'click_logs': logs
    }), 200