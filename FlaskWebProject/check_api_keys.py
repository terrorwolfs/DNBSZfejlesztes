#!/usr/bin/env python
"""
Script to check if all required API keys are properly configured.
This can be run before starting the application to ensure all integrations will work.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_api_key(key_name, required=True):
    """Check if an API key is properly configured"""
    value = os.environ.get(key_name)
    
    if not value:
        if required:
            print(f"❌ {key_name}: Missing (required)")
            return False
        else:
            print(f"⚠️ {key_name}: Missing (optional)")
            return True
    
    # Check for placeholder values
    placeholder_prefixes = ['your-', 'sk_test_', 'pk_test_', 'SG.', 'AIzaSy']
    if any(value.startswith(prefix) for prefix in placeholder_prefixes) and 'test' not in value:
        print(f"⚠️ {key_name}: Appears to be a placeholder value")
        return False
    
    print(f"✅ {key_name}: Configured")
    return True

def main():
    """Main function to check all API keys"""
    print("Checking API keys configuration...\n")
    
    # Define required and optional API keys
    required_keys = ['MAPS_API_KEY', 'WEATHER_API_KEY']
    optional_keys = ['STRIPE_API_KEY', 'STRIPE_PUBLIC_KEY', 'EMAIL_API_KEY']
    
    all_required_valid = all(check_api_key(key) for key in required_keys)
    all_optional_valid = all(check_api_key(key, required=False) for key in optional_keys)
    
    print("\nSummary:")
    if all_required_valid:
        print("✅ All required API keys are configured")
    else:
        print("❌ Some required API keys are missing or invalid")
    
    if not all_optional_valid:
        print("⚠️ Some optional API keys are missing or have placeholder values")
        print("   Some features may not work correctly")
    
    print("\nTo fix missing or invalid API keys:")
    print("1. Open the .env file in the project root directory")
    print("2. Add or update the API keys with valid values")
    print("3. Restart the application")
    
    return 0 if all_required_valid else 1

if __name__ == "__main__":
    sys.exit(main())
