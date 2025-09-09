# 🏛️ Agora - Philosopher Chat Application

An AI-powered application that allows users to engage in philosophical conversations with history's greatest thinkers. Built with clean architecture principles and modern Python practices.

## 🌟 Features

- **One-on-One Conversations**: Chat with 10 famous philosophers including Socrates, Plato, Aristotle, and more
- **Philosophical Debates**: Set up multi-philosopher debates on any topic
- **Authentic Responses**: Each philosopher responds in their unique style with historical context
- **Session Management**: Contextual dialogue with conversation history
- **Interactive Console UI**: Beautiful, colorful terminal interface
- **Extensible Architecture**: Easy to add new philosophers or features

## 🧠 Available Philosophers

1. **Socrates** (470-399 BCE) - The father of Western philosophy
2. **Plato** (428-348 BCE) - Student of Socrates, founder of the Academy
3. **Aristotle** (384-322 BCE) - Student of Plato, tutor to Alexander the Great
4. **Confucius** (551-479 BCE) - Chinese philosopher and teacher
5. **Marcus Aurelius** (121-180 CE) - Roman Emperor and Stoic philosopher
6. **Immanuel Kant** (1724-1804) - German Enlightenment philosopher
7. **Friedrich Nietzsche** (1844-1900) - German philosopher and cultural critic
8. **René Descartes** (1596-1650) - French philosopher and mathematician
9. **John Locke** (1632-1704) - English philosopher and physician
10. **Karl Marx** (1818-1883) - German philosopher and economist

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Agora
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment:
```bash
cp .env.example .env
```

4. Add your OpenAI API key to the `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

### Running the Application

```bash
python main.py
```

## 🏗️ Architecture

The application follows clean architecture principles with clear separation of concerns:

```
Agora/
├── config/          # Configuration and settings
├── models/          # Data models and domain logic
│   ├── philosopher.py   # Philosopher base class and implementations
│   ├── dialogue.py      # Dialogue session management
│   └── debate.py        # Multi-philosopher debate sessions
├── services/        # Business logic and external integrations
│   ├── ai_service.py    # OpenAI API integration
│   ├── dialogue_service.py  # Dialogue management
│   ├── debate_service.py    # Debate management
│   └── session_manager.py   # Session lifecycle management
├── ui/              # User interface components
│   └── console_ui.py    # Terminal-based interface
├── utils/           # Utilities and helpers
│   ├── validators.py    # Input validation
│   └── exceptions.py    # Custom exceptions
└── main.py          # Application entry point
```

## 💬 Usage Examples

### Starting a Conversation

1. Run the application
2. Select "Start Philosopher Dialogue"
3. Choose a philosopher from the list
4. Begin your philosophical discussion!

Example conversation with Socrates:
```
Socrates: Greetings, my friend! I am Socrates of Athens. I know nothing, yet I am eager to learn through our dialogue. What questions trouble your mind today?

You: What is the meaning of life?

Socrates: Ah, my dear friend, you ask perhaps the most important question of all! But tell me, before we can discover what life means, must we not first examine what we mean by "meaning" itself? And what do you suppose makes a life worth living? Is it pleasure, as some claim, or virtue, or perhaps something else entirely?
```

### Creating a Debate

1. Select "Create Philosophical Debate"
2. Enter your debate topic (e.g., "Is free will an illusion?")
3. Select 2-5 philosophers to participate
4. Watch as they engage in authentic philosophical discourse!

## ⚙️ Configuration

The application can be configured through environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `APP_NAME`: Application name (default: "Agora")
- `DEBUG`: Enable debug mode (default: False)
- `LOG_LEVEL`: Logging level (default: INFO)

## 🎨 Features in Detail

### Authentic Philosopher Personalities

Each philosopher is implemented with:
- **Unique conversation style** based on historical records
- **Core philosophical beliefs** that guide their responses
- **Historical context** and references to their era
- **Characteristic response patterns** for different topics

### Session Management

- **Contextual conversations** that remember previous exchanges
- **Session persistence** during the application runtime
- **History management** to prevent memory overflow
- **Graceful session cleanup** and timeout handling

### Input Validation

- **Comprehensive input sanitization** to prevent harmful content
- **Topic validation** for debates and discussions
- **Command validation** for UI interactions
- **API key validation** for proper configuration

## 🔧 Development

### Adding New Philosophers

1. Create a new philosopher class inheriting from `Philosopher`
2. Implement the required abstract methods
3. Add the philosopher to the `PhilosopherFactory`
4. Update the `PhilosopherType` enum

Example:
```python
class NewPhilosopher(Philosopher):
    def __init__(self):
        profile = PhilosopherProfile(
            name="New Philosopher",
            era="Time Period",
            nationality="Nationality",
            key_concepts=["Concept 1", "Concept 2"],
            famous_works=["Work 1", "Work 2"],
            philosophical_school="School",
            brief_description="Description"
        )
        super().__init__(profile)
    
    def _define_conversation_style(self) -> str:
        return "Conversation style description"
    
    def _define_core_beliefs(self) -> List[str]:
        return ["Belief 1", "Belief 2"]
    
    def _define_response_patterns(self) -> Dict[str, str]:
        return {"topic": "response pattern"}
```

### Testing

Run the application with debug mode enabled:
```bash
DEBUG=True python main.py
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions, please open an issue on the repository.

---

*"The unexamined life is not worth living." - Socrates*
