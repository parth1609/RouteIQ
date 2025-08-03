#!/usr/bin/env python3
"""
Simple script to test Zendesk authentication and diagnose issues.
Run this script to check if your Zendesk credentials are working correctly.
"""

import os
import sys
from dotenv import load_dotenv

def test_env_variables():
    """Test if environment variables are loaded correctly"""
    print("🔍 Checking environment variables...")
    
    load_dotenv()
    
    email = os.getenv('ZENDESK_EMAIL')
    token = os.getenv('ZENDESK_TOKEN')
    subdomain = os.getenv('ZENDESK_SUBDOMAIN')
    
    print(f"ZENDESK_EMAIL: {'✅ Set' if email else '❌ Missing'}")
    print(f"ZENDESK_TOKEN: {'✅ Set' if token else '❌ Missing'}")
    print(f"ZENDESK_SUBDOMAIN: {'✅ Set' if subdomain else '❌ Missing'}")
    
    if email:
        print(f"   Email value: {email}")
    if subdomain:
        print(f"   Subdomain value: {subdomain}")
    if token:
        print(f"   Token value: {'*' * (len(token) - 4) + token[-4:] if len(token) > 4 else '***'}")
    
    return all([email, token, subdomain])

def test_zendesk_connection():
    """Test actual Zendesk connection"""
    print("\n🔐 Testing Zendesk connection...")
    
    try:
        from zenpy import Zenpy
        
        creds = {
            'email': os.getenv('ZENDESK_EMAIL'),
            'token': os.getenv('ZENDESK_TOKEN'),
            'subdomain': os.getenv('ZENDESK_SUBDOMAIN')
        }
        
        print("Attempting to connect to Zendesk...")
        print(f"   URL: https://{creds['subdomain']}.zendesk.com")
        print(f"   Email: {creds['email']}")
        print(f"   Token: {'*' * (len(creds['token']) - 4) + creds['token'][-4:] if len(creds['token']) > 4 else '***'}")
        
        zenpy_client = Zenpy(**creds)
        
        # Test authentication by getting current user
        current_user = zenpy_client.users.me()
        print(f"✅ Successfully connected to Zendesk!")
        print(f"   Connected as: {current_user.name} ({current_user.email})")
        print(f"   User ID: {current_user.id}")
        print(f"   Role: {current_user.role}")
        
        # Check if we're getting anonymous user (indicates auth issue)
        if current_user.name == "Anonymous user" or current_user.email == "invalid@example.com":
            print("⚠️  Warning: Connected as anonymous user. This indicates an authentication issue.")
            print("   Possible causes:")
            print("   1. Invalid API token")
            print("   2. Token doesn't have sufficient permissions")
            print("   3. Email doesn't match the token owner")
            print("   4. Account is suspended or inactive")
            return False
        
        return True
        
    except ImportError:
        print("❌ Zenpy library not installed. Run: pip install zenpy")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔍 Common issues and solutions:")
        print("1. Invalid API token - Generate a new token in Zendesk Admin > Channels > API")
        print("2. Wrong subdomain - Use only the subdomain part (e.g., 'company' for company.zendesk.com)")
        print("3. Incorrect email - Use the email associated with your Zendesk account")
        print("4. Token permissions - Ensure the token has the necessary permissions")
        print("5. Account status - Check if your Zendesk account is active")
        return False

def main():
    print("🚀 Zendesk Authentication Test")
    print("=" * 40)
    
    # Test environment variables
    env_ok = test_env_variables()
    
    if not env_ok:
        print("\n❌ Environment variables are missing!")
        print("Please create a .env file in the backend directory with:")
        print("ZENDESK_EMAIL=your-email@domain.com")
        print("ZENDESK_TOKEN=your-api-token")
        print("ZENDESK_SUBDOMAIN=your-subdomain")
        return False
    
    # Test Zendesk connection
    connection_ok = test_zendesk_connection()
    
    if connection_ok:
        print("\n✅ All tests passed! Your Zendesk integration should work correctly.")
        return True
    else:
        print("\n❌ Authentication failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 