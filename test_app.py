"""
Test script to verify the Philosopher Chat application components.
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported successfully."""
    try:
        from config.settings import settings
        from models.philosopher import PhilosopherFactory, PhilosopherType
        from models.dialogue import DialogueSession
        from models.debate import DebateSession
        from services.ai_service import AIService
        from services.dialogue_service import DialogueService
        from services.debate_service import DebateService
        from services.session_manager import SessionManager
        from utils.validators import InputValidator
        from utils.exceptions import AgoraException
        
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_philosopher_factory():
    """Test the philosopher factory."""
    try:
        from models.philosopher import PhilosopherFactory, PhilosopherType
        
        # Test creating philosophers
        socrates = PhilosopherFactory.create_philosopher(PhilosopherType.SOCRATES)
        plato = PhilosopherFactory.create_philosopher(PhilosopherType.PLATO)
        
        print(f"✅ Created philosophers: {socrates.name}, {plato.name}")
        
        # Test getting available philosophers
        available = PhilosopherFactory.get_available_philosophers()
        print(f"✅ Available philosophers: {len(available)}")
        
        return True
    except Exception as e:
        print(f"❌ Philosopher factory error: {e}")
        return False

def test_dialogue_session():
    """Test dialogue session functionality."""
    try:
        from models.dialogue import DialogueSession
        
        session = DialogueSession(philosopher_name="Socrates")
        session.add_user_message("Hello, Socrates!")
        session.add_philosopher_message("Greetings, my friend!")
        
        print(f"✅ Dialogue session created with {len(session.messages)} messages")
        return True
    except Exception as e:
        print(f"❌ Dialogue session error: {e}")
        return False

def test_validators():
    """Test input validation."""
    try:
        from utils.validators import InputValidator
        
        # Test valid inputs
        topic = InputValidator.validate_topic("What is justice?")
        message = InputValidator.validate_message("This is a test message")
        
        print("✅ Input validation working")
        return True
    except Exception as e:
        print(f"❌ Validator error: {e}")
        return False

def test_settings():
    """Test settings configuration."""
    try:
        from config.settings import settings
        
        print(f"✅ Settings loaded - App: {settings.app_name}, Model: {settings.model_name}")
        
        # Check if API key is configured
        if settings.openai_api_key and settings.openai_api_key.startswith('sk-'):
            print("✅ OpenAI API key is configured")
        else:
            print("⚠️  OpenAI API key not properly configured")
        
        return True
    except Exception as e:
        print(f"❌ Settings error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Philosopher Chat Application Components\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Philosopher Factory Test", test_philosopher_factory),
        ("Dialogue Session Test", test_dialogue_session),
        ("Validators Test", test_validators),
        ("Settings Test", test_settings),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to use.")
        print("\nTo start the application, run: python main.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
