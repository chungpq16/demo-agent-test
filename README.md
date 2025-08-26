# Jira AI Chatbot

An agentic AI chatbot for Jira issue management built with LangGraph and Streamlit. This application provides a conversational interface to interact with Jira issues, retrieve information, and perform AI-powered analysis.

## 🏗️ Professional Architecture

This application follows a professional folder structure for maintainability and scalability:

```
jira-ai-chatbot/
├── src/                     # Source code
│   ├── core/               # Core application logic
│   ├── agents/             # AI agents
│   ├── clients/            # External service clients  
│   ├── tools/              # LangChain tools
│   ├── ui/                 # User interfaces
│   └── utils/              # Utilities and configuration
├── tests/                  # Test files
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── main.py                 # Main entry point
```

See [docs/structure.md](docs/structure.md) for detailed architecture documentation.

## 🚀 Quick Start

### Run the Web Interface
```bash
python main.py
```

### Alternative: Direct Streamlit
```bash
streamlit run src/ui/app.py
```

## ✨ Features

- 🔍 **Retrieve Issues by Status**: Get all issues with specific statuses (TO-DO, In Progress, Done, etc.)
- 📋 **Detailed Issue Information**: Get comprehensive details about specific Jira issues
- 📊 **AI-Powered Analysis & Insights**: Analyze all tickets with intelligent summaries, identify patterns, bottlenecks, and priority clusters
- 💬 **Interactive Chat Interface**: User-friendly Streamlit-based conversational interface
- 🤖 **Simple Agent**: Streamlined agent workflow with tool integration
- 🔎 **Advanced Search**: JQL-based searching with natural language input
- 📁 **Project Management**: Access and analyze multiple Jira projects
- 🎯 **Project Scoping**: Optional project-specific filtering for focused searches
- 🧠 **Context Awareness**: Maintains conversation history for better interactions

## 🤖 LLM Providers

The chatbot currently supports multiple LLM providers with easy switching:

### Currently Active: Ollama (Local)
- **Model**: Llama3.1:8b (configurable)
- **Benefits**: 
  - ✅ Free and privacy-focused
  - ✅ Runs locally on your machine
  - ✅ No API costs or rate limits
  - ✅ Full data control
- **Requirements**: Ollama installation and model download

### Available: OpenAI (Commented)
- **Models**: GPT-4o-mini and others
- **Benefits**: 
  - ⚡ Fast response times
  - 🎯 High-quality reasoning
  - 🔄 Easy to enable
- **Requirements**: OpenAI API key and subscription
- **Status**: Code ready, just uncomment and configure

### Switching LLM Providers
To switch from Ollama back to OpenAI:
1. Uncomment OpenAI imports in `jira_agent.py`
2. Comment out Ollama configuration
3. Add `OPENAI_API_KEY` to your `.env` file
4. Update `requirements.txt` dependencies

## 🏗️ Architecture

### System Overview

The Jira AI Chatbot is a sophisticated conversational interface that bridges natural language queries with Jira API operations using AI. The system employs a streamlined architecture focused on simplicity and reliability.

### Core Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │◄──►│   JiraChatbot    │◄──►│ SimpleJiraAgent │
│   (Frontend)    │    │  (Orchestrator)  │    │   (AI Engine)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                ▲                        ▲
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Debug Utils    │    │   Jira Tools    │
                       │   (Logging)     │    │ (Tool Functions)│
                       └─────────────────┘    └─────────────────┘
                                                        ▲
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  Jira Client    │
                                               │  (API Wrapper)  │
                                               └─────────────────┘
                                                        ▲
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   Jira API      │
                                               │ (Atlassian)     │
                                               └─────────────────┘
```

#### 1. **Frontend Layer** (`app.py`)
- **Streamlit Web Interface**: Provides the chat-based user interface
- **Session Management**: Handles chat history and application state
- **Input/Output Handling**: Processes user input and displays responses
- **Sidebar Controls**: Quick actions and system status display

#### 2. **Orchestration Layer** (`chatbot.py`)
- **JiraChatbot**: Main coordinator that manages the conversation flow
- **System Commands**: Handles special commands (help, status, debug)
- **History Management**: Maintains conversation context
- **Error Handling**: Provides graceful error recovery

#### 3. **AI Agent Layer** (`simple_jira_agent.py`)
- **SimpleJiraAgent**: Core AI engine using OpenAI GPT-4
- **Tool Integration**: Binds AI model with Jira operation tools
- **Natural Language Processing**: Interprets user queries and generates responses
- **Tool Orchestration**: Decides which tools to call based on user intent

#### 4. **Tools Layer** (`jira_tools.py`)
- **LangChain Tools**: Individual functions for specific Jira operations
- **Data Processing**: Formats and structures Jira data for AI consumption
- **Error Handling**: Provides robust error handling for each operation

#### 5. **API Layer** (`jira_client.py`)
- **Jira Client**: Wrapper around Atlassian Python API
- **Data Transformation**: Converts Jira API responses to pandas DataFrames
- **Connection Management**: Handles authentication and API connections

## 🔄 How It Works

### Request/Response Flow

```
User Query: "Show me all To Do issues"
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                           │
├─────────────────────────────────────────────────────────────────┤
│ 1. User types query in chat interface                          │
│ 2. Input captured via st.chat_input()                          │
│ 3. Query added to session messages                             │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CHATBOT ORCHESTRATOR                        │
├─────────────────────────────────────────────────────────────────┤
│ 1. Receives user input from Streamlit                          │
│ 2. Checks for system commands (help, status, debug)            │
│ 3. If regular query, passes to SimpleJiraAgent                 │
│ 4. Manages conversation history                                 │
│ 5. Handles errors and provides fallback responses              │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI AGENT PROCESSING                       │
├─────────────────────────────────────────────────────────────────┤
│ 1. SimpleJiraAgent receives query                              │
│ 2. Builds conversation context with system prompt              │
│ 3. Sends to OpenAI GPT-4 with available tools                  │
│ 4. LLM analyzes query and decides which tools to call          │
│ 5. If tools needed, executes tool calls                        │
│ 6. Processes tool results and generates final response         │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│                        TOOL EXECUTION                          │
├─────────────────────────────────────────────────────────────────┤
│ For "Show me To Do issues":                                    │
│ 1. Agent calls get_issues_by_status("To Do")                   │
│ 2. Tool validates inputs and calls JiraClient                  │
│ 3. JiraClient executes JQL: status = "To Do"                   │
│ 4. Jira API returns raw JSON data                              │
│ 5. Client converts to pandas DataFrame                         │
│ 6. Tool formats data as JSON string for AI                     │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RESPONSE GENERATION                       │
├─────────────────────────────────────────────────────────────────┤
│ 1. Agent receives formatted tool results                       │
│ 2. Sends results back to GPT-4 with context                    │
│ 3. LLM generates user-friendly response with insights          │
│ 4. Response includes issue count, summaries, and key info      │
│ 5. Agent returns formatted response to Chatbot                 │
└─────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND DISPLAY                          │
├─────────────────────────────────────────────────────────────────┤
│ 1. Chatbot returns response to Streamlit                       │
│ 2. Response displayed in chat interface                        │
│ 3. Message added to conversation history                       │
│ 4. User can ask follow-up questions with context               │
└─────────────────────────────────────────────────────────────────┘

Final Response: "I found 15 To Do issues in your project..."
```

### Detailed Component Interactions

#### 1. **User Input Processing**
```python
# app.py - Streamlit captures user input
if prompt := st.chat_input("Ask me about Jira issues..."):
    # Add to session state and process
    response = st.session_state.chatbot.chat(prompt)
```

#### 2. **Agent Decision Making**
```python
# simple_jira_agent.py - AI decides which tools to use
response = self.llm_with_tools.invoke(messages)
if response.tool_calls:
    # Execute each tool call
    for tool_call in response.tool_calls:
        result = self.tools[tool_name].invoke(tool_args)
```

#### 3. **Jira API Integration**
```python
# jira_client.py - API wrapper
def get_issues_by_status(self, status: str):
    jql = f'status = "{status}" ORDER BY created DESC'
    result = self.jira.jql(jql, limit=limit)
    return pd.DataFrame(issues_data)
```

#### 4. **Tool Processing**
```python
# jira_tools.py - Individual tool functions
@tool
def get_issues_by_status(status: str) -> str:
    df = jira_client.get_issues_by_status(status)
    return json.dumps(result, indent=2)
```

### Data Flow Examples

#### Example 1: Status Query
```
Input: "Show me In Progress issues"
├── Agent: Calls get_issues_by_status("In Progress")
├── Client: Executes JQL query
├── API: Returns issue data
├── Tool: Formats as JSON
└── AI: Generates user-friendly summary
```

#### Example 2: Issue Details
```
Input: "Tell me about PROJ-123"
├── Agent: Calls get_issue_details("PROJ-123")
├── Client: Fetches specific issue
├── API: Returns detailed issue data
├── Tool: Includes comments, assignee, etc.
└── AI: Creates comprehensive summary
```

#### Example 3: Analysis Query
```
Input: "Analyze all tickets"
├── Agent: Calls get_all_issues_for_analysis()
├── Client: Fetches all accessible issues
├── Tool: Generates statistics and insights
├── AI: Processes patterns and trends
└── Response: Detailed analysis with recommendations
```

#### Example 4: Create Issue
```
Input: "Create a task to fix the login bug with high priority"
├── Agent: Calls create_jira_issue(
│              summary="Fix login bug",
│              description="Login functionality issue",
│              issue_type="Task",
│              priority="High"
│          )
├── Client: Prepares issue data with project scoping
├── API: Creates new issue in Jira
├── Tool: Returns created issue details
└── Response: Confirmation with issue key and URL
```

### File Structure
```
jira-summarization/
├── app.py                 # Main Streamlit application
├── chatbot.py            # Main chatbot orchestrator
├── simple_jira_agent.py  # Simple agent implementation
├── jira_tools.py         # LangGraph tools for Jira operations
├── jira_client.py        # Jira API client wrapper
├── config.py             # Configuration management
├── debug_utils.py        # Logging and debugging utilities
├── requirements.txt      # Python dependencies
├── setup.py             # Setup and installation script
├── .env.example         # Environment variables template
└── README.md            # This file
```

## 🚀 Prerequisites

- Python 3.8 or higher
- Jira account with API access
- **Ollama installed and running** with Llama3.1:8b model
  ```bash
  # Install Ollama (macOS/Linux)
  curl -fsSL https://ollama.ai/install.sh | sh
  
  # Pull the Llama3.1:8b model
  ollama pull llama3.1:8b
  
  # Start Ollama server (usually runs automatically)
  ollama serve
  ```
- Required Python packages (automatically installed via setup)

**Note**: OpenAI support is available but commented out for future use

## ⚙️ Installation

### Option 1: Automatic Setup (Recommended)

1. **Navigate to the project directory**:
   ```bash
   cd jira-summarization
   ```

2. **Run the automated setup script**:
   ```bash
   python setup.py
   ```

3. **Configure your credentials**:
   Edit the `.env` file with your actual values:
   ```env
   JIRA_SERVER_URL=https://your-domain.atlassian.net
   JIRA_USERNAME=your-email@example.com
   JIRA_API_TOKEN=your-api-token
   JIRA_PROJECT_KEY=PROJ (optional - scope searches to specific project)
   
   # Ollama Configuration (currently active)
   OLLAMA_MODEL=llama3.1:8b
   OLLAMA_BASE_URL=http://localhost:11434
   
   # OpenAI Configuration (commented for future use)
   # OPENAI_API_KEY=your-openai-api-key
   ```

### Option 2: Manual Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

3. **Configure credentials** (edit `.env` with your values)

## 🔑 Configuration

### Jira API Setup

1. **Get Jira Server URL**: Your Atlassian instance URL (e.g., `https://yourcompany.atlassian.net`)

2. **Create API Token**:
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens
   - Click "Create API token"
   - Copy the generated token

3. **Get Username**: Your email address associated with Jira account

### OpenAI API Setup

1. **Get API Key**: Sign up at https://platform.openai.com/
2. **Copy API Key**: From your OpenAI dashboard

## 🚀 Usage

### Start the Application

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

### User Interface Guide

#### Main Chat Interface
- **Chat Input**: Located at the bottom, stays fixed during scrolling
- **Message History**: Scrollable conversation view
- **System Messages**: Color-coded responses (user/assistant/system)

#### Sidebar Features
- **System Status**: Real-time health check and connection status
- **Quick Actions**: Pre-defined buttons for common queries
- **Configuration Display**: Shows current Jira and API settings
- **Chat Controls**: Clear history and help options

### Example Interactions

#### Basic Status Queries
```
User: "Show me all To Do issues"
Assistant: I found 12 To Do issues in your project:
• PROJ-101: Fix login authentication bug (High Priority)
• PROJ-102: Update user dashboard UI (Medium Priority)
• PROJ-103: Add email notifications (Low Priority)
[... continues with full list and summary]
```

#### Issue Detail Requests
```
User: "Tell me about PROJ-123"
Assistant: Here are the details for PROJ-123:

📋 **Summary**: Implement user authentication system
🏷️ **Status**: In Progress
👤 **Assignee**: John Doe
⚡ **Priority**: High
📅 **Created**: 2024-01-15
🏗️ **Components**: Backend, Security
🔖 **Labels**: security, authentication, backend

📝 **Description**: Implementation of secure user authentication...
💬 **Recent Comments**: 
• Jane Smith (2024-01-20): "Started working on OAuth integration"
• Mike Johnson (2024-01-18): "Requirements clarified"
```

#### Analysis and Insights
```
User: "Analyze all tickets"
Assistant: 📊 **Project Analysis Summary**

**Overview**: 45 total issues across 3 projects

**Status Distribution**:
• To Do: 15 issues (33%)
• In Progress: 12 issues (27%)
• Done: 18 issues (40%)

**Priority Breakdown**:
• High: 8 issues (18%)
• Medium: 22 issues (49%)
• Low: 15 issues (33%)

**Key Insights**:
🔍 Most active contributor: John Doe (12 issues)
⚠️ Potential bottleneck: 5 high-priority issues in "To Do"
📈 Completion rate: 40% (healthy progress)
🏷️ Most common labels: bug (8), feature (12), enhancement (6)

**Recommendations**:
1. Address high-priority backlog items
2. Consider load balancing for John Doe
3. Review bug resolution process
```

### Advanced Queries

#### Natural Language Search
- **"Find all bugs assigned to me"**
- **"Show high priority issues created this month"**  
- **"List overdue tasks"**
- **"What issues are blocking the release?"**

#### Project Management
- **"Give me a project overview"**
- **"Which projects am I involved in?"**
- **"Show me team workload distribution"**

### System Commands

#### Help and Information
- `help` or `what can you do` - Show available commands
- `system status` - Check application health
- `debug info` - Technical diagnostics (when DEBUG=true)

#### Session Management  
- `clear history` - Reset conversation
- `reset` - Clear chat and start fresh

## 🔧 Available Tools & Operations

The system provides 7 core tools that handle different aspects of Jira interaction:

### 1. **get_issues_by_status**
- **Purpose**: Retrieve issues filtered by specific status
- **Usage**: "Show me all To Do issues", "List In Progress tickets"
- **Process**: JQL query → DataFrame → JSON formatting → AI summary
- **Output**: Issue list with key details (key, summary, assignee, priority)

### 2. **get_issue_details**
- **Purpose**: Get comprehensive information about a specific issue
- **Usage**: "Tell me about PROJ-123", "Show details for ABC-456"
- **Process**: Issue key → API call → Full issue data → Formatted response
- **Output**: Detailed view including description, comments, labels, components

### 3. **get_all_issues_for_analysis**
- **Purpose**: Retrieve all accessible issues for statistical analysis
- **Usage**: "Analyze all tickets", "Give me project insights"
- **Process**: Bulk fetch → Statistical processing → Pattern analysis
- **Output**: Comprehensive analysis with charts, trends, and recommendations

### 4. **search_issues_by_jql**
- **Purpose**: Advanced searching using Jira Query Language
- **Usage**: "Find high priority bugs", "Issues created this week"
- **Process**: Natural language → JQL translation → Search execution
- **Output**: Filtered results based on complex criteria

### 5. **get_project_summary**
- **Purpose**: Overview of accessible Jira projects
- **Usage**: "What projects do I have access to?"
- **Process**: Project enumeration → Metadata collection
- **Output**: Project list with keys, names, leads, and types

### 6. **get_all_issues**
- **Purpose**: Retrieve all issues without status filtering
- **Usage**: "Show me all issues", "List everything"
- **Process**: Bulk query → All issues → Formatted list
- **Output**: Complete issue list with basic details

### 7. **create_jira_issue**
- **Purpose**: Create new Jira issues
- **Usage**: "Create a task for...", "Add a bug report for..."
- **Process**: Requirements analysis → Issue data preparation → API creation
- **Output**: Created issue details with key, URL, and confirmation

### Tool Selection Logic

The AI agent uses the following decision tree:

```
User Query Analysis
├── Contains issue key (PROJ-123)? → get_issue_details
├── Requests status-based list? → get_issues_by_status  
├── Asks for analysis/insights? → get_all_issues_for_analysis
├── Complex search criteria? → search_issues_by_jql
├── Asks about projects? → get_project_summary
├── Wants to create issue? → create_jira_issue
├── General list request? → get_all_issues
└── General question? → Direct AI response
```

## 🧪 Development & Customization

### Development Environment Setup

#### Prerequisites
- Python 3.8+ with pip
- Git for version control
- Code editor (VS Code recommended)
- Access to Jira instance and OpenAI account

#### Local Development
```bash
# Clone and setup
git clone <repository-url>
cd jira-summarization

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your credentials

# Enable debug mode
echo "DEBUG=true" >> .env

# Run application
streamlit run app.py
```

### Architecture Deep Dive

#### Component Responsibilities

**📱 Frontend Layer (`app.py`)**
```python
# Key functions:
- initialize_chatbot()     # Setup and health checks
- handle_user_input()      # Process chat interactions  
- display_chat_history()   # Render conversation
- sidebar_content()        # Quick actions and status
```

**🧠 Orchestration Layer (`chatbot.py`)**
```python
# Key methods:
- chat()                   # Main conversation handler
- handle_system_commands() # Process special commands
- get_system_info()        # Health and status checks
- clear_history()          # Session management
```

**🤖 AI Engine (`simple_jira_agent.py`)**
```python
# Core functionality:
- chat()                   # Process single queries
- chat_with_history()      # Context-aware conversations
- Tool binding and execution
- Response generation and formatting
```

#### Configuration Management

**Environment Variables**
```env
# Required
JIRA_SERVER_URL=https://company.atlassian.net
JIRA_USERNAME=user@company.com  
JIRA_API_TOKEN=your-token

# LLM Configuration (Ollama - currently active)
OLLAMA_MODEL=llama3.1:8b       # Ollama model to use
OLLAMA_BASE_URL=http://localhost:11434  # Ollama server URL

# OpenAI Configuration (commented for future use)
# OPENAI_API_KEY=your-key

# Optional
JIRA_PROJECT_KEY=PROJ          # Scope searches to specific project
DEBUG=false                    # Enable detailed logging
APP_TITLE=Custom Chatbot       # Browser tab title
DEFAULT_ISSUE_LIMIT=100        # Default query limit
MAX_CHAT_HISTORY=20            # Conversation memory
```

**Configuration Class (`config.py`)**
- Centralized settings management
- Environment validation
- Default value handling
- Configuration summaries for debugging

### Customization Options

#### Adding New Tools
```python
# In jira_tools.py
@tool
def your_custom_tool(parameter: str) -> str:
    """Your tool description for the AI."""
    # Your implementation
    return json.dumps(result)

# Add to JIRA_TOOLS list
JIRA_TOOLS.append(your_custom_tool)
```

#### Modifying AI Behavior
```python
# In simple_jira_agent.py - Update system prompt
self.system_prompt = """
Your custom instructions for the AI agent...
Available tools: ...
Guidelines: ...
"""
```

#### UI Customization
```python
# In app.py - Modify CSS styles
st.markdown("""
<style>
    .your-custom-class {
        /* Your styles */
    }
</style>
""", unsafe_allow_html=True)
```

### Debug Mode

Enable comprehensive logging:
```env
DEBUG=true
```

Features when enabled:
- Detailed console logging
- File logging to `jira_chatbot_debug.log`  
- Extended error messages
- Tool execution tracing
- Performance metrics

### Project Structure Details

```
jira-summarization/
├── 📱 Frontend
│   └── app.py                    # Streamlit web interface
│       ├── Page configuration
│       ├── CSS styling  
│       ├── Chat interface
│       ├── Sidebar components
│       └── Session management
│
├── 🧠 Core Logic  
│   ├── chatbot.py               # Main orchestrator
│   │   ├── Conversation management
│   │   ├── System commands
│   │   ├── History handling
│   │   └── Error recovery
│   │
│   ├── simple_jira_agent.py     # AI engine
│   │   ├── OpenAI integration
│   │   ├── Tool orchestration
│   │   ├── Context management
│   │   └── Response generation
│   │
│   ├── jira_client.py           # API wrapper
│   │   ├── Authentication
│   │   ├── Query execution
│   │   ├── Data transformation
│   │   └── Error handling
│   │
│   └── jira_tools.py            # Tool definitions
│       ├── Status queries
│       ├── Issue details
│       ├── Analysis functions
│       ├── Search operations
│       └── Project management
│
├── ⚙️ Configuration
│   ├── config.py                # Settings management
│   ├── debug_utils.py           # Logging utilities
│   └── .env.example            # Environment template
│
└── 📚 Documentation
    ├── README.md               # This comprehensive guide
    └── PRD.md                  # Product requirements
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting & FAQ

### Common Issues & Solutions

#### Connection Problems

**❌ "Missing Jira credentials"**
```bash
# Check your .env file has all required variables
cat .env | grep JIRA
JIRA_SERVER_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@example.com  
JIRA_API_TOKEN=your-api-token
```

**❌ "Failed to initialize Jira client"**
- Verify your Jira server URL is correct and accessible
- Ensure API token is valid (regenerate if needed)
- Check if your account has proper permissions

**❌ "OpenAI API error"**  
```bash
# Verify API key format
echo $OPENAI_API_KEY | cut -c1-10
# Should start with "sk-"
```

#### Runtime Issues

**❌ "No issues found"**
- Check your Jira permissions and project access
- Verify query syntax and status names
- Try broader search terms

**❌ "Tool execution failed"**
- Enable debug mode: `DEBUG=true`
- Check logs: `tail -f jira_chatbot_debug.log`
- Verify Jira API limits haven't been exceeded

**❌ "Streamlit connection error"**
```bash
# Check if port 8501 is available
netstat -tulpn | grep :8501
# If occupied, use different port:
streamlit run app.py --server.port 8502
```

### Diagnostic Commands

Use these in the chat interface:

#### System Health Check
```
system status
```
**Expected Output**:
```
✅ System Status: Healthy
🔗 Jira Connection: Connected
📁 Accessible Projects: 3
💬 Chat History: 4 messages
🤖 Agent Status: Initialized
🔧 Available Tools: 5
```

#### Debug Information
```
debug info
```
**Shows**:
- Platform and Python version
- Configuration validation
- Environment variable status
- Missing requirements

### Performance Optimization

#### Query Optimization
- Use specific status names instead of partial matches
- Limit large result sets with focused queries
- Use issue keys for direct lookups when possible

#### Memory Management
- Chat history auto-trims to last 20 messages
- Large datasets are processed in chunks
- Session state is managed efficiently

#### API Rate Limiting
- Default limits: 100 issues per query
- Analysis queries: 200 issues maximum  
- Implement delays between bulk operations if needed

### Logging and Monitoring

#### Log Levels
```python
# In .env file
DEBUG=true    # Enables debug logging
LOG_LEVEL=INFO  # Optional: DEBUG, INFO, WARNING, ERROR
```

#### Log Files
- **Console**: Real-time output during development
- **File**: `jira_chatbot_debug.log` (when DEBUG=true)
- **Streamlit**: Built-in error display in web interface

#### Monitoring Queries
```python
# Example debug output
2024-01-20 10:30:15 - simple_jira_agent - DEBUG - Processing user input: Show me To Do issues
2024-01-20 10:30:15 - jira_tools - DEBUG - Executing tool: get_issues_by_status
2024-01-20 10:30:16 - jira_client - INFO - Retrieved 12 issues with status: To Do
```

### FAQ

**Q: Can I use this with Jira Server (on-premise)?**
A: Yes, just update JIRA_SERVER_URL to your internal server address.

**Q: How do I add custom Jira fields?**
A: Modify `_extract_issue_data()` in `jira_client.py` to include additional fields.

**Q: Can I integrate with other ticketing systems?**
A: The architecture supports this - create a new client class following the same interface.

**Q: How secure are my credentials?**
A: Credentials are stored in environment variables and never logged. Use secure token storage in production.

**Q: Can multiple users use the same instance?**
A: Currently single-user. For multi-user, implement session isolation and user-specific authentication.

**Q: How do I backup conversation history?**
A: Currently in-memory only. Implement persistent storage by modifying session management.

### Getting Help

1. **Check logs**: Enable DEBUG mode and review error messages
2. **System status**: Use built-in diagnostic commands  
3. **Documentation**: Review this README and PRD.md
4. **Community**: Check Streamlit and LangChain documentation
5. **Issues**: Report bugs with full error logs and steps to reproduce

## 🚀 What's Next

- Multi-language support
- Advanced analytics
- Issue creation capabilities
- Custom dashboards
- Integration with other tools
