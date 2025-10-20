"""
Setup script to help configure Gemini API key
"""

import os
from pathlib import Path

def setup_gemini_key():
    """Interactive setup for Gemini API key"""
    
    print("\n" + "="*70)
    print("🔧 GEMINI API KEY SETUP")
    print("="*70)
    print()
    print("To use this chatbot, you need a Google Gemini API key.")
    print()
    print("📝 How to get your API key:")
    print("   1. Go to: https://makersuite.google.com/app/apikey")
    print("   2. Sign in with your Google account")
    print("   3. Click 'Create API Key'")
    print("   4. Copy the generated key")
    print()
    print("="*70)
    print()
    
    # Check if .env exists
    env_path = Path(__file__).parent / ".env"
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            content = f.read()
            if 'GEMINI_API_KEY=' in content and 'your_gemini_api_key_here' not in content:
                print("✓ API key already configured in .env file")
                change = input("\nDo you want to update it? (y/n): ").strip().lower()
                if change != 'y':
                    print("\nKeeping existing configuration.")
                    return
    
    print("Please enter your Gemini API key:")
    print("(or press Enter to skip and configure manually later)")
    print()
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("\n⚠️  Skipped. You can add your key to the .env file manually.")
        print(f"   Edit: {env_path}")
        print("   Change: GEMINI_API_KEY=your_gemini_api_key_here")
        print("   To: GEMINI_API_KEY=<your_actual_key>")
        return
    
    # Update .env file
    env_content = f"""# Google Gemini API Configuration
GEMINI_API_KEY={api_key}

# This key is for Google Gemini AI
# Keep it secret and don't share it publicly
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print()
    print("="*70)
    print("✅ SUCCESS! Gemini API key configured")
    print("="*70)
    print()
    print("You can now run the chatbot:")
    print("   python server.py")
    print()
    print("Or test it with:")
    print("   python main.py")
    print()


if __name__ == "__main__":
    try:
        setup_gemini_key()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")









