# GenAI Application with LLM Farm Integration

A GenAI application that leverages LLM Farm for natural language processing to interact with Jira through conversational prompts.

## Features

- 🤖 **Natural Language Processing**: Interact with Jira using natural language queries
- 🌐 **Modern Web Interface**: Beautiful Streamlit UI with real-time chat
- 🔧 **LLM Farm Integration**: Powered by LLM Farm for advanced prompt orchestration
- 📋 **Comprehensive Jira Operations**:
  - Get all issues from your project
  - Filter issues by status (Open, In Progress, Done, etc.)
  - Get detailed information for specific issues
  - Search issues using text or JQL queries
- � **Visual Data Presentation**: 
  - Interactive tables and charts
  - Issue status distributions
  - Real-time metrics and summaries
- �🛡️ **Secure Configuration**: Environment-based credential management
- 🏥 **Health Monitoring**: Real-time system status and diagnostics
- 📊 **Debug Logging**: Comprehensive logging for monitoring and troubleshooting
- 🏗️ **Modular Architecture**: Scalable and maintainable code structure
- 🚀 **Multiple Interfaces**: Web UI, CLI, and API access

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd genai-app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   - Copy `.env` file and update with your credentials:
   ```bash
   cp .env .env.local
   # Edit .env.local with your actual values
   ```

## Configuration

Update the `.env` file with your credentials:

```env
# LLM Farm Configuration
API_KEY=your-llm-farm-api-key
LLM_FARM_URL=https://aoai-farm.example.com/api/openai/deployments/your-deployment

# Jira Configuration
JIRA_URL=https://your-jira-instance.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_TOKEN=your-jira-api-token
JIRA_PROJECT=YOUR-PROJECT-KEY

# Logging Configuration (optional)
LOG_LEVEL=DEBUG
```

### Getting Jira API Token

1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Label it (e.g., "GenAI App")
4. Copy the generated token

## Usage

### 🌐 Web Interface (Recommended)

Launch the Streamlit web interface:

```bash
# Direct Streamlit command (recommended)
streamlit run app.py

# Alternative: Module command
python -m streamlit run app.py
```

The web interface provides:
- 💬 **Interactive chat** with your Jira assistant
- 📊 **Visual data presentation** with charts and tables
- 🏥 **Real-time health monitoring**
- 🚀 **Quick action buttons** for common queries
- ❓ **Built-in help and examples**

### 🖥️ Command Line Interface

#### Interactive Mode
```bash
python main.py
```

This starts an interactive session where you can ask questions naturally:

```
🤖 GenAI Jira Assistant
==================================================
Type 'help' for available commands, 'quit' to exit

➤ Show me all open issues
➤ Get details for PROJ-123
➤ Find issues related to authentication
➤ What issues are in progress?
```

#### Single Query Mode
```bash
python main.py --query "Show me all open issues"
python main.py --query "Get details for PROJ-123"
```

#### Health Check
```bash
python main.py --health
```

#### Help
```bash
python main.py --help
```

## Example Queries

### Getting Issues
- "Show me all issues"
- "Get all open issues"
- "What issues are in progress?"
- "Show me completed tasks"

### Searching
- "Find issues about login"
- "Search for bug reports"
- "Issues related to authentication"
- "Show me high priority issues"

### Issue Details
- "Get details for PROJ-123"
- "Tell me about issue PROJ-456"
- "What's the status of PROJ-789?"

## Architecture

```
genai-app/
├── llm_farm_client/     # LLM Farm API client
│   └── __init__.py
├── jira_client/         # Jira API client
│   └── __init__.py
├── orchestrator/        # Prompt orchestration logic
│   └── __init__.py
├── logger/              # Logging configuration
│   └── __init__.py
├── ui/                  # Streamlit UI components (optional)
│   └── [UI modules]
├── app.py              # Streamlit web interface
├── main.py             # CLI application entry point
├── .env                # Environment configuration
├── .gitignore          # Git ignore patterns
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Components

- **LLM Farm Client**: Handles communication with LLM Farm API
- **Jira Client**: Manages Jira REST API interactions using atlassian-python-api
- **Orchestrator**: Implements prompt-based orchestration and function calling
- **Logger**: Provides centralized logging with file and console output
- **Main App**: Application entry point with multiple run modes

## Logging

The application generates detailed logs in:
- **Console**: INFO level and above
- **File**: `genai_app_YYYYMMDD.log` with DEBUG level

Log levels can be controlled via the `LOG_LEVEL` environment variable.

## Error Handling

- Comprehensive error handling with user-friendly messages
- Automatic retry logic for transient failures
- Health checks for all external dependencies
- Graceful degradation when services are unavailable

## Development

### Adding New Jira Operations

1. Add method to `JiraClient` class
2. Add function definition to `JiraOrchestrator._define_jira_functions()`
3. Add function execution logic to `JiraOrchestrator._execute_function_call()`

### Testing

Run basic health checks:
```bash
python main.py --health
```

Test individual components:
```python
from jira_client import JiraClient
from llm_farm_client import LLMFarmClient

# Test Jira connection
jira = JiraClient()
print(jira.health_check())

# Test LLM Farm connection  
llm = LLMFarmClient()
print(llm.health_check())
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify Jira URL, username, and API token
   - Check LLM Farm API key and URL
   - Ensure Jira user has necessary permissions

2. **Connection Issues**
   - Check network connectivity
   - Verify URLs are accessible
   - Check firewall settings

3. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Debug Mode

Enable debug logging:
```env
LOG_LEVEL=DEBUG
```

Check logs in `genai_app_YYYYMMDD.log` for detailed information.

## Security Considerations

- Store credentials in `.env` file, never in code
- Use Jira API tokens, not passwords
- Restrict Jira user permissions to minimum required
- Keep LLM Farm API keys secure
- Review logs for sensitive information before sharing

## License

[Add your license information here]

## Support

[Add support contact information here]
