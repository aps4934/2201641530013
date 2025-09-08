from flask import Flask
from src.middleware.logging_middleware import init_logging, logger
from src.api.endpoints.create_short_url import create_short_url_bp
from src.api.endpoints.redirect_short_url import redirect_short_url_bp
from src.api.endpoints.stats_short_url import stats_short_url_bp
import os

app = Flask(__name__)

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# initialize logging middleware (must be done before handling requests)
init_logging(app)

# Register blueprints
app.register_blueprint(create_short_url_bp)
app.register_blueprint(redirect_short_url_bp)
app.register_blueprint(stats_short_url_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)