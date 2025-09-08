from flask import Blueprint

api = Blueprint('api', __name__)

# Keep this file minimal to avoid circular imports.
# Do NOT import endpoint modules here — import blueprints directly in app.py.
__all__ = []