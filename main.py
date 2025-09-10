"""
Main entry point for the Philosopher Chat application.
"""
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ui.console_ui import ConsoleUI
from config.settings import settings

def setup_logging():
    """Setup logging configuration."""
    # Set up file logging for all messages
    file_handler = logging.FileHandler('agora.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    # Set up console logging only for warnings and errors (unless debug mode)
    console_handler = logging.StreamHandler(sys.stdout)
    if settings.debug:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.WARNING)  # Only show warnings and errors in console
    console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler]
    )

def main():
    """Main entry point."""
    try:
        setup_logging()
        
        # Create and start the console UI
        ui = ConsoleUI()
        ui.start()
        
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"Fatal error: {e}")
        if settings.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
