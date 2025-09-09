"""
Console-based user interface for the Philosopher Chat application.
"""
import os
import sys
from typing import Optional, List, Dict, Any
from colorama import init, Fore, Back, Style
from models.philosopher import PhilosopherType, PhilosopherFactory
from models.dialogue import DialogueSession
from models.debate import DebateSession
from services.gemini_service import GeminiService
from services.dialogue_service import DialogueService
from services.debate_service import DebateService
from services.session_manager import SessionManager
from config.settings import settings

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class ConsoleUI:
    """Console-based user interface for the philosopher chat application."""
    
    def __init__(self):
        """Initialize the console UI."""
        self.ai_service = GeminiService()
        self.dialogue_service = DialogueService(self.ai_service)
        self.debate_service = DebateService(self.ai_service)
        self.session_manager = SessionManager()
        self.current_dialogue_session: Optional[DialogueSession] = None
        self.current_debate_session: Optional[DebateSession] = None
        self.running = True
    
    def start(self) -> None:
        """Start the console UI."""
        try:
            self._validate_setup()
            self._show_welcome()
            self._main_loop()
        except KeyboardInterrupt:
            self._show_goodbye()
        except Exception as e:
            print(f"{Fore.RED}Error: {e}")
            sys.exit(1)
    
    def _validate_setup(self) -> None:
        """Validate that the application is properly configured."""
        try:
            settings.validate()
            # Skip API key validation at startup - will validate when first used
            print(f"{Fore.GREEN}✅ Configuration loaded successfully")
        except Exception as e:
            raise ValueError(f"Configuration error: {e}")
    
    def _show_welcome(self) -> None:
        """Display the welcome message."""
        self._clear_screen()
        print(f"{Fore.CYAN}{Style.BRIGHT}╔═══════════════════════════════════════════════════════════════╗")
        print(f"{Fore.CYAN}{Style.BRIGHT}║                    🏛️        Agora       🏛️                   ║")
        print(f"{Fore.CYAN}{Style.BRIGHT}║              Converse with History's Greatest Minds           ║")
        print(f"{Fore.CYAN}{Style.BRIGHT}╚═══════════════════════════════════════════════════════════════╝")
        print()
        print(f"{Fore.YELLOW}Welcome to Agora - where ancient wisdom meets modern conversation!")
        print(f"{Fore.WHITE}Chat with history's most influential philosophers:")
        print()
        
        # Display available philosophers
        philosophers = PhilosopherFactory.get_available_philosophers()
        for i, philosopher_type in enumerate(philosophers, 1):
            philosopher = PhilosopherFactory.create_philosopher(philosopher_type)
            print(f"{Fore.GREEN}{i:2d}. {philosopher.name} {Fore.CYAN}({philosopher.profile.era})")
        
        print()
        print(f"{Fore.MAGENTA}Features:")
        print(f"{Fore.WHITE}• One-on-one philosophical conversations")
        print(f"{Fore.WHITE}• Multi-philosopher debates on any topic")
        print(f"{Fore.WHITE}• Historical context and authentic responses")
        print(f"{Fore.WHITE}• Session history and contextual dialogue")
        print()
    
    def _main_loop(self) -> None:
        """Main application loop."""
        while self.running:
            try:
                self._show_main_menu()
                choice = self._get_user_input("Enter your choice: ").strip()
                self._handle_main_menu_choice(choice)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"{Fore.RED}Error: {e}")
                input(f"{Fore.YELLOW}Press Enter to continue...")
    
    def _show_main_menu(self) -> None:
        """Display the main menu."""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}═══ MAIN MENU ═══")
        print(f"{Fore.WHITE}1. Start Philosopher Dialogue")
        print(f"{Fore.WHITE}2. Create Philosophical Debate")
        print(f"{Fore.WHITE}3. Resume Session")
        print(f"{Fore.WHITE}4. View Session History")
        print(f"{Fore.WHITE}5. About Philosophers")
        print(f"{Fore.WHITE}6. Settings")
        print(f"{Fore.WHITE}7. Exit")
        print()
    
    def _handle_main_menu_choice(self, choice: str) -> None:
        """Handle main menu selection."""
        if choice == "1":
            self._start_dialogue()
        elif choice == "2":
            self._start_debate()
        elif choice == "3":
            self._resume_session()
        elif choice == "4":
            self._view_session_history()
        elif choice == "5":
            self._show_philosopher_info()
        elif choice == "6":
            self._show_settings()
        elif choice == "7":
            self.running = False
        else:
            print(f"{Fore.RED}Invalid choice. Please try again.")
    
    def _start_dialogue(self) -> None:
        """Start a new dialogue with a philosopher."""
        philosopher_type = self._select_philosopher()
        if not philosopher_type:
            return
        
        try:
            session = self.dialogue_service.start_dialogue(philosopher_type)
            self.session_manager.add_dialogue_session(session)
            self.current_dialogue_session = session
            
            print(f"\n{Fore.GREEN}Starting conversation with {session.philosopher_name}...")
            self._dialogue_loop(session)
            
        except Exception as e:
            print(f"{Fore.RED}Error starting dialogue: {e}")
    
    def _dialogue_loop(self, session: DialogueSession) -> None:
        """Main dialogue loop."""
        # Show welcome message
        if session.messages:
            welcome_msg = session.messages[0]
            print(f"\n{Fore.CYAN}{session.philosopher_name}: {Fore.WHITE}{welcome_msg.content}")
        
        while True:
            print(f"\n{Fore.YELLOW}Commands: /help, /history, /clear, /end")
            user_input = self._get_user_input(f"{Fore.GREEN}You: {Fore.WHITE}").strip()
            
            if not user_input:
                continue
            
            if user_input.startswith('/'):
                if self._handle_dialogue_command(user_input, session):
                    break
                continue
            
            try:
                print(f"{Fore.YELLOW}Thinking...")
                response_msg = self.dialogue_service.send_message(session, user_input)
                print(f"\n{Fore.CYAN}{session.philosopher_name}: {Fore.WHITE}{response_msg.content}")
                
            except Exception as e:
                print(f"{Fore.RED}Error: {e}")
    
    def _handle_dialogue_command(self, command: str, session: DialogueSession) -> bool:
        """Handle dialogue commands. Returns True if session should end."""
        command = command.lower()
        
        if command == "/help":
            self._show_dialogue_help()
        elif command == "/history":
            self._show_dialogue_history(session)
        elif command == "/clear":
            session.clear_history()
            print(f"{Fore.GREEN}Conversation history cleared.")
        elif command == "/end":
            self.session_manager.end_dialogue_session(session.id)
            print(f"{Fore.GREEN}Conversation ended.")
            return True
        else:
            print(f"{Fore.RED}Unknown command: {command}")
        
        return False
    
    def _show_dialogue_help(self) -> None:
        """Show dialogue help."""
        print(f"\n{Fore.CYAN}Dialogue Commands:")
        print(f"{Fore.WHITE}/help    - Show this help message")
        print(f"{Fore.WHITE}/history - Show conversation history")
        print(f"{Fore.WHITE}/clear   - Clear conversation history")
        print(f"{Fore.WHITE}/end     - End the conversation")
    
    def _show_dialogue_history(self, session: DialogueSession) -> None:
        """Show dialogue history."""
        print(f"\n{Fore.CYAN}Conversation History:")
        for i, message in enumerate(session.messages[-10:], 1):  # Show last 10 messages
            if message.type.value == "philosopher":
                print(f"{Fore.CYAN}{i:2d}. {session.philosopher_name}: {Fore.WHITE}{message.content[:100]}...")
            elif message.type.value == "user":
                print(f"{Fore.GREEN}{i:2d}. You: {Fore.WHITE}{message.content[:100]}...")
    
    def _start_debate(self) -> None:
        """Start a new philosophical debate."""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}═══ CREATE PHILOSOPHICAL DEBATE ═══")
        
        topic = self._get_user_input("Enter debate topic: ").strip()
        if not topic:
            print(f"{Fore.RED}Topic is required.")
            return
        
        description = self._get_user_input("Enter description (optional): ").strip()
        
        # Select philosophers for the debate
        philosophers = self._select_multiple_philosophers()
        if len(philosophers) < 2:
            print(f"{Fore.RED}At least 2 philosophers are required for a debate.")
            return
        
        try:
            session = self.debate_service.create_debate(topic, description, philosophers)
            self.session_manager.add_debate_session(session)
            self.current_debate_session = session
            
            print(f"\n{Fore.GREEN}Starting debate on: {topic}")
            self.debate_service.start_debate(session)
            self._debate_loop(session)
            
        except Exception as e:
            print(f"{Fore.RED}Error starting debate: {e}")
    
    def _debate_loop(self, session: DebateSession) -> None:
        """Main debate loop."""
        print(f"\n{Fore.CYAN}Debate participants: {', '.join(p.name for p in session.participants)}")
        print(f"{Fore.YELLOW}The debate will proceed with each philosopher taking turns.")
        print(f"{Fore.YELLOW}Commands: /pause, /resume, /end, /status")
        
        # Show opening statements
        for message in session.messages:
            if message.type.value == "philosopher":
                speaker = message.metadata.get("speaker", "Philosopher")
                print(f"\n{Fore.CYAN}{speaker}: {Fore.WHITE}{message.content}")
        
        while session.status.value == "active":
            user_input = self._get_user_input(f"\n{Fore.GREEN}Your input (or press Enter to continue): {Fore.WHITE}").strip()
            
            if user_input.startswith('/'):
                if self._handle_debate_command(user_input, session):
                    break
                continue
            
            try:
                print(f"{Fore.YELLOW}Generating next response...")
                response = self.debate_service.get_next_response(session, user_input)
                
                if response:
                    current_speaker = session.get_current_speaker()
                    if current_speaker:
                        print(f"\n{Fore.CYAN}{current_speaker.name}: {Fore.WHITE}{response}")
                    else:
                        print(f"\n{Fore.MAGENTA}Moderator: {Fore.WHITE}{response}")
                else:
                    print(f"\n{Fore.GREEN}Debate has concluded.")
                    break
                    
            except Exception as e:
                print(f"{Fore.RED}Error: {e}")
    
    def _handle_debate_command(self, command: str, session: DebateSession) -> bool:
        """Handle debate commands. Returns True if debate should end."""
        command = command.lower()
        
        if command == "/pause":
            self.debate_service.pause_debate(session)
            print(f"{Fore.GREEN}Debate paused.")
        elif command == "/resume":
            self.debate_service.resume_debate(session)
            print(f"{Fore.GREEN}Debate resumed.")
        elif command == "/end":
            session.complete_debate()
            print(f"{Fore.GREEN}Debate ended.")
            return True
        elif command == "/status":
            self._show_debate_status(session)
        else:
            print(f"{Fore.RED}Unknown command: {command}")
        
        return False
    
    def _show_debate_status(self, session: DebateSession) -> None:
        """Show debate status."""
        print(f"\n{Fore.CYAN}Debate Status:")
        print(f"{Fore.WHITE}Topic: {session.topic}")
        print(f"{Fore.WHITE}Status: {session.status.value}")
        print(f"{Fore.WHITE}Participants: {len(session.participants)}")
        for participant in session.participants:
            print(f"{Fore.WHITE}  - {participant.name}: {participant.turn_count} turns")
    
    def _select_philosopher(self) -> Optional[PhilosopherType]:
        """Select a single philosopher."""
        philosophers = PhilosopherFactory.get_available_philosophers()
        
        print(f"\n{Fore.CYAN}Select a philosopher:")
        for i, philosopher_type in enumerate(philosophers, 1):
            philosopher = PhilosopherFactory.create_philosopher(philosopher_type)
            print(f"{Fore.WHITE}{i}. {philosopher.name}")
        
        while True:
            try:
                choice = self._get_user_input("Enter number (or 0 to cancel): ").strip()
                if choice == "0":
                    return None
                
                index = int(choice) - 1
                if 0 <= index < len(philosophers):
                    return philosophers[index]
                else:
                    print(f"{Fore.RED}Invalid choice. Please try again.")
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number.")
    
    def _select_multiple_philosophers(self) -> List[PhilosopherType]:
        """Select multiple philosophers for a debate."""
        philosophers = PhilosopherFactory.get_available_philosophers()
        selected = []
        
        print(f"\n{Fore.CYAN}Select philosophers for the debate (minimum 2):")
        for i, philosopher_type in enumerate(philosophers, 1):
            philosopher = PhilosopherFactory.create_philosopher(philosopher_type)
            print(f"{Fore.WHITE}{i}. {philosopher.name}")
        
        print(f"{Fore.YELLOW}Enter numbers separated by commas (e.g., 1,3,5):")
        
        while True:
            try:
                choices = self._get_user_input("Selection: ").strip()
                if not choices:
                    break
                
                indices = [int(x.strip()) - 1 for x in choices.split(',')]
                selected = [philosophers[i] for i in indices if 0 <= i < len(philosophers)]
                
                if len(selected) >= 2:
                    break
                else:
                    print(f"{Fore.RED}Please select at least 2 philosophers.")
            except (ValueError, IndexError):
                print(f"{Fore.RED}Invalid input. Please enter valid numbers separated by commas.")
        
        return selected
    
    def _resume_session(self) -> None:
        """Resume an existing session."""
        print(f"\n{Fore.CYAN}Feature coming soon: Resume Session")
    
    def _view_session_history(self) -> None:
        """View session history."""
        stats = self.session_manager.get_session_statistics()
        
        print(f"\n{Fore.CYAN}{Style.BRIGHT}═══ SESSION STATISTICS ═══")
        print(f"{Fore.WHITE}Active Dialogue Sessions: {stats['active_dialogue_sessions']}")
        print(f"{Fore.WHITE}Active Debate Sessions: {stats['active_debate_sessions']}")
        print(f"{Fore.WHITE}Total Dialogue Sessions: {stats['total_dialogue_sessions']}")
        print(f"{Fore.WHITE}Total Debate Sessions: {stats['total_debate_sessions']}")
        
        if stats['philosophers_in_use']:
            print(f"\n{Fore.CYAN}Philosophers Currently in Use:")
            for philosopher, count in stats['philosophers_in_use'].items():
                print(f"{Fore.WHITE}  {philosopher}: {count} session(s)")
    
    def _show_philosopher_info(self) -> None:
        """Show detailed information about philosophers."""
        philosopher_type = self._select_philosopher()
        if not philosopher_type:
            return
        
        try:
            info = self.dialogue_service.get_philosopher_info(philosopher_type)
            
            print(f"\n{Fore.CYAN}{Style.BRIGHT}═══ {info['name'].upper()} ═══")
            print(f"{Fore.WHITE}Era: {info['era']}")
            print(f"{Fore.WHITE}Nationality: {info['nationality']}")
            print(f"{Fore.WHITE}School: {info['philosophical_school']}")
            print(f"\n{Fore.CYAN}Description:")
            print(f"{Fore.WHITE}{info['description']}")
            print(f"\n{Fore.CYAN}Key Concepts:")
            for concept in info['key_concepts']:
                print(f"{Fore.WHITE}• {concept}")
            print(f"\n{Fore.CYAN}Famous Works:")
            for work in info['famous_works']:
                print(f"{Fore.WHITE}• {work}")
            
        except Exception as e:
            print(f"{Fore.RED}Error retrieving philosopher info: {e}")
    
    def _show_settings(self) -> None:
        """Show application settings."""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}═══ SETTINGS ═══")
        print(f"{Fore.WHITE}App Name: {settings.app_name}")
        print(f"{Fore.WHITE}Model: {settings.model_name}")
        print(f"{Fore.WHITE}Max Tokens: {settings.max_tokens}")
        print(f"{Fore.WHITE}Temperature: {settings.temperature}")
        print(f"{Fore.WHITE}Max History Length: {settings.max_history_length}")
        print(f"{Fore.WHITE}Session Timeout: {settings.session_timeout}s")
        print(f"{Fore.WHITE}Debug Mode: {settings.debug}")
    
    def _get_user_input(self, prompt: str) -> str:
        """Get user input with prompt."""
        try:
            return input(prompt)
        except KeyboardInterrupt:
            raise
        except EOFError:
            return ""
    
    def _clear_screen(self) -> None:
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _show_goodbye(self) -> None:
        """Show goodbye message."""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}Thank you for visiting the Agora!")
        print(f"{Fore.YELLOW}May wisdom guide your path. Farewell! 🏛️")
        print()
