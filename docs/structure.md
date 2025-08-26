# Jira AI Chatbot - Project Structure

This document describes the professional folder structure of the Jira AI Chatbot application.

## 📁 Directory Structure

```
jira-ai-chatbot/
├── src/                          # Source code
│   ├── core/                     # Core application logic
│   │   ├── __init__.py
│   │   └── chatbot.py           # Main JiraChatbot class
│   ├── agents/                   # AI agents
│   │   ├── __init__.py
│   │   └── jira_agent.py        # JiraAgent for LLM interactions
│   ├── clients/                  # External service clients
│   │   ├── __init__.py
│   │   └── jira_client.py       # Jira API client wrapper
│   ├── tools/                    # LangChain tools
│   │   ├── __init__.py
│   │   └── jira_tools.py        # Jira-specific tools
│   ├── llm/                      # LLM integrations (future)
│   │   └── __init__.py
│   ├── ui/                       # User interfaces
│   │   ├── __init__.py
│   │   └── app.py               # Streamlit web application
│   └── utils/                    # Utilities and configuration
│       ├── __init__.py
│       ├── config.py            # Configuration management
│       └── debug_utils.py       # Logging and debug utilities
├── tests/                        # Test files
│   ├── __init__.py
│   └── test_structure.py        # Structure validation tests
├── docs/                         # Documentation
│   ├── __init__.py
│   └── structure.md             # This file
├── scripts/                      # Utility scripts
│   └── list_projects.py         # Project listing utility
├── main.py                       # Main entry point
├── setup.py                      # Package setup
├── requirements.txt              # Dependencies
├── .env.example                  # Environment variables template
├── .gitignore                   # Git ignore rules
└── README.md                     # Project overview
```

## 🏗️ Architecture Overview

### Core Components

1. **`src/core/chatbot.py`** - Main orchestration class
   - Integrates all components
   - Manages chat history
   - Handles system commands
   - Provides health checks

2. **`src/agents/jira_agent.py`** - AI agent for tool management
   - Handles LLM interactions
   - Manages tool calling
   - Supports OpenAI and Ollama

3. **`src/clients/jira_client.py`** - Jira API wrapper
   - Handles authentication
   - Provides data transformation
   - Manages project scoping

4. **`src/tools/jira_tools.py`** - LangChain tools collection
   - 8 specialized Jira tools
   - Issue retrieval and analysis
   - Search and filtering

### Supporting Components

5. **`src/ui/app.py`** - Streamlit web interface
   - Chat-based interaction
   - Sidebar controls
   - History management

6. **`src/utils/config.py`** - Configuration management
   - Environment variables
   - Validation
   - Default values

7. **`src/utils/debug_utils.py`** - Logging and debugging
   - Enhanced logging setup
   - Debug information collection
   - Performance monitoring

## 🚀 Running the Application

### Web Interface
```bash
python main.py
```

### Direct Streamlit
```bash
streamlit run src/ui/app.py
```

## 🧪 Testing

Run the structure validation test:
```bash
python tests/test_structure.py
```

## 📦 Installation

### Development Installation
```bash
pip install -e .
```

### Production Installation
```bash
pip install .
```

### With Development Dependencies
```bash
pip install -e ".[dev]"
```

## 🔧 Configuration

1. Copy `.env.example` to `.env`
2. Configure your Jira credentials:
   ```
   JIRA_SERVER_URL=https://your-domain.atlassian.net
   JIRA_USERNAME=your-email@domain.com
   JIRA_API_TOKEN=your-api-token
   ```
3. Configure LLM settings (OpenAI or Ollama)

## 🎯 Key Benefits of This Structure

1. **Modularity** - Clear separation of concerns
2. **Scalability** - Easy to add new components
3. **Testability** - Isolated components for testing
4. **Maintainability** - Logical organization
5. **Professional** - Industry-standard structure
6. **Extensibility** - Easy to add new LLM providers
7. **Documentation** - Self-documenting structure

## 📝 Import Patterns

All imports now use absolute paths from the project root:

```python
# Core components
from src.core.chatbot import JiraChatbot

# Agents
from src.agents.jira_agent import JiraAgent

# Clients
from src.clients.jira_client import JiraClient

# Tools
from src.tools.jira_tools import JIRA_TOOLS, initialize_tools

# Utilities
from src.utils.config import Config
from src.utils.debug_utils import setup_logging
```

## 🔮 Future Extensions

The structure is designed to accommodate:

- Additional LLM providers in `src/llm/`
- New agent types in `src/agents/`
- Additional external clients in `src/clients/`
- New tool collections in `src/tools/`
- Alternative UIs in `src/ui/`
- Extended utilities in `src/utils/`

This structure follows Python packaging best practices and provides a solid foundation for scaling the application.
