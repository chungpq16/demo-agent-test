# AI Assistant with Function Calling

A Streamlit chatbot with OpenAI function calling capabilities, featuring Google search via SERPER API and Dockerfile generation with corporate settings.

## Features

- 🤖 **Smart Function Calling**: Automatically detects when to use tools vs direct LLM response
- 🔍 **Google Search**: Search the web using SERPER API and get formatted results with snippets and links
- 🐳 **Dockerfile Generator**: Generate enterprise-ready Dockerfiles with private base images, corporate proxy, and root certificates
- 💬 **General Q&A**: Direct LLM responses for conversational queries
- ⚡ **Streaming Responses**: Real-time streaming for general questions
- 🎨 **Clean UI**: Intuitive Streamlit interface with conversation history

## Function Capabilities

### 1. Google Search Tool
- Searches Google using SERPER API
- Returns top 5 organic results
- Provides snippets and clickable links
- **Triggers**: Keywords like "search", "find", "look up", "what is"

### 2. Dockerfile Generator
- Generates corporate-compliant Dockerfiles
- Supports Python, Node.js, Java, and other application types
- Includes private base image configuration
- Configures corporate proxy settings
- Adds root certificate installation
- Implements security best practices
- **Triggers**: Keywords like "dockerfile", "docker", "container", "build"

### 3. General Q&A
- Direct LLM responses for casual conversation
- No function calling overhead
- Streaming responses for better UX

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   Make sure your `.env` file contains:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   SERPER_API_KEY=your_serper_api_key_here
   OPENAI_MODEL=gpt-3.5-turbo  # Optional, defaults to gpt-3.5-turbo
   
   # Corporate Dockerfile settings
   CORPORATE_BASE_IMAGE=your-private-registry.com/base-images/python:3.11-slim
   CORPORATE_PROXY_HOST=proxy.yourcompany.com
   CORPORATE_PROXY_PORT=8080
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser:**
   The app will automatically open at `http://localhost:8501`

## Usage

### Search Example
```
User: "Search for best Python web frameworks"
AI: 🔄 Executing serper_search...
    🔍 Search Results for 'best Python web frameworks':
    1. Django is a high-level Python web framework...
       🔗 View Source
    2. Flask is a lightweight WSGI web application framework...
       🔗 View Source
```

### Dockerfile Generation Example
```
User: "Create a Dockerfile for my Python API application"
AI: 🔄 Executing generate_dockerfile...
    🐳 Dockerfile for Python API (python)
    [Generated Dockerfile with corporate settings]
```

### General Q&A Example
```
User: "What's the weather like?"
AI: I don't have access to real-time weather data...
    (Direct LLM response without function calling)
```

## How It Works

1. **Intent Detection**: The app analyzes user input to determine intent
2. **Function Routing**: 
   - Search keywords → Google Search function
   - Docker keywords → Dockerfile Generator function
   - General questions → Direct LLM response
3. **Smart Responses**: Functions return formatted results, general questions get streaming responses

## File Structure

```
function-calling/
├── app.py              # Main Streamlit application
├── function.py         # Function calling implementation
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (API keys)
└── README.md          # This file
```

## Notes

- The app uses session state to maintain conversation history
- Responses are streamed in real-time for better user experience
- Error handling is included for API failures
- The current model being used is displayed in the sidebar
# demo-agent-test
