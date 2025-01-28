from flask import Flask
from app.api.ec2_discovery import ec2_discovery_bp
from loguru import logger
import sys
import os

# Get command line arguments
if len(sys.argv) < 7:
    print("Usage: python main.py <resourceAccount> <resourceRegion> <resourceType> <resourceAttribute> <argument_name> <argument_value>")
    sys.exit(1)

# Command line arguments
resourceAccount = sys.argv[1]
resourceRegion = sys.argv[2]
resourceType = sys.argv[3]
resourceAttribute = sys.argv[4]
argument_name = sys.argv[5]
argument_value = sys.argv[6]

# Environment variables
GITLAB_URL = os.environ.get("GITLAB_URL", "https://gitlab.com")
API_KEY = os.environ.get("API_KEY", "default_api_key")

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure logging
    logger.add(
        "logs/discover_ec2_app.log",
        level="INFO",
        format="{time} {level} {message}",
        rotation="500 MB",
        retention="10 days"
    )

    # Register blueprints
    app.register_blueprint(ec2_discovery_bp)

    # Add command line arguments to app config
    app.config.update(
        RESOURCE_ACCOUNT=resourceAccount,
        RESOURCE_REGION=resourceRegion,
        RESOURCE_TYPE=resourceType,
        RESOURCE_ATTRIBUTE=resourceAttribute,
        ARGUMENT_NAME=argument_name,
        ARGUMENT_VALUE=argument_value,
        GITLAB_URL=GITLAB_URL,
        API_KEY=API_KEY
    )

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8443, debug=True) 