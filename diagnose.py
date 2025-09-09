"""
Diagnostic script to identify OpenAI API issues.
"""
import os
import openai
from dotenv import load_dotenv

load_dotenv()

def test_api_key():
    """Test the OpenAI API key and configuration."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    print("🔍 Diagnosing OpenAI API Issues...")
    print(f"API Key: {api_key[:20]}...{api_key[-10:] if api_key else 'NOT SET'}")
    
    if not api_key:
        print("❌ No API key found in .env file")
        return False
    
    if not api_key.startswith('sk-'):
        print("❌ API key doesn't start with 'sk-'")
        return False
    
    # Test with OpenAI client
    client = openai.OpenAI(api_key=api_key)
    
    # Test 1: Try GPT-3.5 (cheaper, more accessible)
    print("\n📋 Testing GPT-3.5-turbo...")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        print("✅ GPT-3.5-turbo works!")
        print(f"Response: {response.choices[0].message.content}")
    except openai.AuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        return False
    except openai.RateLimitError as e:
        print(f"❌ Rate limit or quota exceeded: {e}")
        return False
    except openai.PermissionDeniedError as e:
        print(f"❌ Permission denied: {e}")
        return False
    except Exception as e:
        print(f"❌ GPT-3.5 error: {e}")
    
    # Test 2: Try GPT-4 (what the app uses)
    print("\n📋 Testing GPT-4...")
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        print("✅ GPT-4 works!")
        print(f"Response: {response.choices[0].message.content}")
        return True
    except openai.PermissionDeniedError as e:
        print(f"⚠️  GPT-4 access denied: {e}")
        print("💡 Solution: Use GPT-3.5-turbo instead")
        return "gpt-3.5-turbo"
    except Exception as e:
        print(f"❌ GPT-4 error: {e}")
        return False

def main():
    result = test_api_key()
    
    if result == "gpt-3.5-turbo":
        print("\n🔧 SOLUTION: Change model to GPT-3.5-turbo")
        print("Edit config/settings.py and change:")
        print('self.model_name = "gpt-3.5-turbo"')
    elif result:
        print("\n✅ API is working correctly!")
    else:
        print("\n❌ API key issues detected. Check:")
        print("1. API key is valid and has credits")
        print("2. API key has correct permissions")
        print("3. No rate limiting issues")

if __name__ == "__main__":
    main()
