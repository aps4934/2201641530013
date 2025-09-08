from datetime import datetime, timedelta
import random
import string
import json
from typing import Optional, Any, Dict, List
from sqlalchemy.orm import Session
from urllib.parse import urlparse
from src.models.url_model import Url

# IMPORTANT: use your logging middleware instance here (do not use print or built-in logging)
from src.middleware.logging_middleware import logger  # adjust import to match your middleware file


def generate_shortcode(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def generate_unique_shortcode(db_session: Optional[Session], length: int = 6, max_attempts: int = 10) -> str:
    """
    Generate a shortcode and ensure uniqueness when a db_session is provided.
    If db_session is None, just returns a random shortcode.
    """
    for attempt in range(max_attempts):
        code = generate_shortcode(length)
        if db_session is None:
            logger.debug("Generated shortcode (no DB check): %s", code)
            return code
        exists = db_session.query(Url).filter(Url.shortcode == code).first()
        if not exists:
            logger.debug("Generated unique shortcode on attempt %d: %s", attempt + 1, code)
            return code
        logger.warning("Shortcode collision on attempt %d: %s", attempt + 1, code)
    logger.error("Failed to generate unique shortcode after %d attempts", max_attempts)
    raise RuntimeError("Unable to generate unique shortcode")


def validate_url(url: str) -> bool:
    parsed = urlparse(url)
    valid = bool(parsed.scheme and parsed.netloc and parsed.scheme in ("http", "https"))
    logger.debug("Validating URL '%s' -> %s", url, valid)
    return valid


def save_url_record(url_record: Dict[str, Any] or Url, db_session: Session) -> Url:
    """
    Persist a url record (either a dict or an ORM Url instance) and return the ORM Url instance.
    """
    if not isinstance(db_session, Session):
        raise ValueError("db_session must be a sqlalchemy.orm.Session instance")

    try:
        if isinstance(url_record, Url):
            db_session.add(url_record)
            db_session.commit()
            db_session.refresh(url_record)
            logger.info("Saved ORM Url record with shortcode %s", url_record.shortcode)
            return url_record

        click_logs = url_record.get("click_logs", [])
        try:
            click_logs_json = json.dumps(click_logs)
        except Exception:
            click_logs_json = json.dumps([])

        orm = Url(
            original_url=url_record["original_url"],
            shortcode=url_record["shortcode"],
            expiry=url_record.get("expiry"),
            created_at=url_record.get("created_at", datetime.utcnow()),
            click_count=url_record.get("click_count", 0),
            click_logs=click_logs_json
        )
        db_session.add(orm)
        db_session.commit()
        db_session.refresh(orm)
        logger.info("Saved URL record (dict) with shortcode %s", orm.shortcode)
        return orm
    except Exception as exc:
        db_session.rollback()
        logger.error("Error saving URL record: %s", str(exc))
        raise


def is_url_unique(shortcode: str, db_session: Optional[Session] = None) -> bool:
    """
    Return True if shortcode does not exist in DB.
    If db_session is None, return True (caller must ensure uniqueness in-memory).
    """
    if db_session is None:
        logger.debug("is_url_unique: no db_session provided, assuming unique for '%s'", shortcode)
        return True

    exists = db_session.query(Url).filter(Url.shortcode == shortcode).first()
    unique = exists is None
    logger.debug("is_url_unique('%s') -> %s", shortcode, unique)
    return unique


def get_url_record(shortcode: str, db_session: Optional[Session] = None) -> Optional[Url]:
    """
    Fetch Url ORM instance by shortcode. Returns None if not found or db_session is None.
    """
    if db_session is None:
        logger.debug("get_url_record: no db_session provided for '%s'", shortcode)
        return None
    record = db_session.query(Url).filter(Url.shortcode == shortcode).first()
    logger.debug("get_url_record('%s') -> %s", shortcode, "found" if record else "not found")
    return record


def log_click(shortcode: str, referrer: Optional[str], geo_location: Optional[str], db_session: Session) -> None:
    """
    Record a click: increment count, append a click log entry (stored as JSON string), commit.
    """
    if not isinstance(db_session, Session):
        raise ValueError("db_session must be a sqlalchemy.orm.Session instance")

    record = db_session.query(Url).filter(Url.shortcode == shortcode).first()
    if not record:
        logger.warning("log_click: shortcode not found %s", shortcode)
        return

    try:
        logs: List[Dict[str, Any]] = []
        if record.click_logs:
            try:
                logs = json.loads(record.click_logs)
            except Exception:
                logs = []

        click_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "referrer": referrer,
            "geo_location": geo_location
        }
        logs.append(click_entry)

        record.click_count = (record.click_count or 0) + 1
        record.click_logs = json.dumps(logs)
        db_session.add(record)
        db_session.commit()
        logger.info("Logged click for shortcode %s (total=%d)", shortcode, record.click_count)
    except Exception as exc:
        db_session.rollback()
        logger.error("Failed to log click for %s: %s", shortcode, str(exc))
        raise


def is_expired(record: Any) -> bool:
    """
    Accepts ORM Url instance or dict-like record. Returns True if expired or record is None.
    """
    if record is None:
        logger.debug("is_expired: record is None -> expired")
        return True

    expiry = None
    if hasattr(record, "expiry"):
        expiry = getattr(record, "expiry")
    elif isinstance(record, dict):
        expiry = record.get("expiry")

    if expiry and isinstance(expiry, datetime):
        expired = datetime.utcnow() > expiry
        logger.debug("is_expired: expiry=%s -> %s", expiry.isoformat(), expired)
        return expired
    return False