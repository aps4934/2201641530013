from flask import Blueprint, request, redirect, jsonify, current_app
from src.services.url_service import get_url_record, log_click, is_expired
from src.middleware.logging_middleware import logger

redirect_short_url_bp = Blueprint('redirect_short_url', __name__)

@redirect_short_url_bp.route('/<string:shortcode>', methods=['GET'])
def redirect_short_url(shortcode):
    """
    Redirect to original URL for given shortcode.
    Expects an optional SQLAlchemy session available as current_app.config['DB_SESSION'].
    """
    db_session = current_app.config.get('DB_SESSION')  # may be None for in-memory/stub setups
    record = get_url_record(shortcode, db_session=db_session)

    if not record:
        return jsonify({'error': 'Shortcode not found'}), 404

    if is_expired(record):
        return jsonify({'error': 'Shortcode expired'}), 410

    # Log click (best-effort — don't block redirect on failure)
    try:
        ref = request.referrer
        ip = request.remote_addr
        log_click(shortcode, ref, ip, db_session=db_session)
    except Exception as exc:
        logger.exception("Failed to log click for %s: %s", shortcode, str(exc))

    # record.original_url assumed present on ORM object
    try:
        target = record.original_url if hasattr(record, "original_url") else record.get("original_url")
    except Exception:
        return jsonify({'error': 'Invalid URL record'}), 500

    return redirect(target, code=302)