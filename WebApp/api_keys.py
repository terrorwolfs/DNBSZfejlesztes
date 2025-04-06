"""
Module for securely handling API keys and external service integrations.
"""
import os
from dotenv import load_dotenv
from flask import current_app

# Load environment variables from .env file
load_dotenv()

class APIKeys:
    """Class to manage API keys and credentials for external services"""
    
    @staticmethod
    def get_key(key_name, default=None):
        """
        Get an API key from environment variables
        
        Args:
            key_name (str): Name of the API key to retrieve
            default: Default value if key is not found
            
        Returns:
            str: The API key value or default if not found
        """
        return os.environ.get(key_name, default)
    
    @staticmethod
    def stripe_api_key():
        """Get Stripe API key"""
        key = APIKeys.get_key('STRIPE_API_KEY')
        if not key and not current_app.config['TESTING']:
            current_app.logger.warning("Stripe API key not configured")
        return key
    
    @staticmethod
    def stripe_public_key():
        """Get Stripe public key"""
        return APIKeys.get_key('STRIPE_PUBLIC_KEY')
    
    @staticmethod
    def email_api_key():
        """Get email service API key"""
        return APIKeys.get_key('EMAIL_API_KEY')
    
    @staticmethod
    def maps_api_key():
        """Get maps API key"""
        return APIKeys.get_key('MAPS_API_KEY')
    
    @staticmethod
    def is_configured(key_name):
        """Check if a specific API key is configured"""
        key = APIKeys.get_key(key_name)
        return key is not None and key != f"your-{key_name.lower().replace('_', '-')}"
