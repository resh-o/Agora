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
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('agora.log'),
            logging.StreamHandler(sys.stdout) if settings.debug else logging.NullHandler()
        ]
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
