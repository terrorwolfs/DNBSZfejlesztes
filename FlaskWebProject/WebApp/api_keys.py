"""
Module for securely handling API keys and external service integrations.
"""
import os
from dotenv import load_dotenv
from flask import current_app
import logging

# Load environment variables from .env file
load_dotenv()

# Ensure environment variables are loaded properly
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
        key = os.getenv(key_name, default)
        
        # Log warning if key is missing or appears to be a placeholder
        if not key:
            current_app.logger.warning(f"{key_name} is not configured") if 'current_app' in globals() else print(f"Warning: {key_name} is not configured")
        elif key and key.startswith(('your-', 'sk_test_', 'pk_test_')) and 'test' not in key:
            current_app.logger.warning(f"{key_name} appears to be a placeholder value")
            
        return key
    
    @staticmethod
    def stripe_api_key():
        """Get Stripe API key"""
        key = APIKeys.get_key('STRIPE_API_KEY')
        if not key and not current_app.config['TESTING']:
            current_app.logger.warning("Stripe API key not configured or invalid")
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
        key = APIKeys.get_key('MAPS_API_KEY')
        if not key and not current_app.config.get('TESTING', False):
            current_app.logger.warning("Google Maps API key not configured or invalid")
        return key
    
    @staticmethod
    def is_configured(key_name):
        """Check if a specific API key is configured"""
        key = APIKeys.get_key(key_name)
        return key is not None and key != f"your-{key_name.lower().replace('_', '-')}"

    @staticmethod
    def weather_api_key():
        """Get weather API key"""
        return APIKeys.get_key('WEATHER_API_KEY')
    
    @staticmethod
    def validate_all_keys():
        """Validate all API keys and log warnings for missing ones"""
        keys_to_check = ['STRIPE_API_KEY', 'STRIPE_PUBLIC_KEY', 'MAPS_API_KEY', 'WEATHER_API_KEY']
        missing_keys = []
        
        for key in keys_to_check:
            if not APIKeys.is_configured(key):
                missing_keys.append(key)
                
        if missing_keys:
            current_app.logger.warning(f"Missing or invalid API keys: {', '.join(missing_keys)}")
            
        return len(missing_keys) == 0
