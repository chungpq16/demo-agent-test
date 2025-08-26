# Custom LLM Farm Integration

This document describes the integration with your custom LLM farm API endpoint.

## 🏭 LLM Farm Architecture

Your LLM farm provides an OpenAI-compatible API endpoint but with custom authentication and without automatic tool choice support. Our integration handles this through:

1. **Custom LLM Client** (`src/llm/custom_llm_client.py`)
2. **Prompt-based Tool Orchestration** (in `src/agents/jira_agent.py`)
3. **SSL Configuration Options** (for development environments)

## 🔧 Configuration

### Environment Variables

```bash
# Custom LLM Farm Configuration
LLM_API_URL=https://dummy.chat/it/application/llamashared/prod/v1/chat/completions
LLM_API_KEY=your-llm-api-key
LLM_MODEL=meta-llama/Meta-Llama-3-70B-Instruct
LLM_MAX_TOKENS=2048
LLM_TEMPERATURE=0.7
LLM_VERIFY_SSL=true  # Set to false for development
```

### API Endpoint Details

- **URL Format**: Ends with `/chat/completions` (OpenAI-compatible)
- **Authentication**: Uses `KeyId` header instead of `Authorization: Bearer`
- **Models**: Supports Llama models (3-70B-Instruct recommended)
- **Tool Support**: Manual tool orchestration (no auto tool choice)

## 🛠️ How It Works

### 1. Custom LLM Client

The `CustomLLMClient` class handles:
- HTTP requests with custom `KeyId` authentication
- SSL verification options
- Request/response formatting
- Error handling and logging

### 2. Prompt-based Tool Orchestration

Since your API doesn't support `--enable-auto-tool-choice`, we use prompt engineering:

```python
# The LLM receives instructions like:
"""
Available Tools:
- get_issues_by_status: Get all issues with a specific status
- get_issue_details: Get detailed information about a specific issue

Instructions:
1. When you need to use a tool, respond with: TOOL_CALL: tool_name(param1="value1")
2. Otherwise, respond directly
"""
```

### 3. Tool Execution Flow

1. **User Input** → LLM receives prompt with tool descriptions
2. **LLM Decision** → Responds with either direct answer or `TOOL_CALL: ...`
3. **Tool Execution** → If tool call detected, execute the tool
4. **Final Response** → LLM generates final answer with tool results

## 📝 Example API Call

Your LLM farm receives requests like this:

```json
{
  "messages": [
    {
      "role": "system", 
      "content": "You are a Jira AI assistant..."
    },
    {
      "role": "user", 
      "content": "Show me all To Do issues"
    }
  ],
  "model": "meta-llama/Meta-Llama-3-70B-Instruct",
  "max_tokens": 2048,
  "temperature": 0.7,
  "top_p": 1,
  "stream": false
}
```

Headers:
```
Content-Type: application/json
KeyId: your-llm-api-key
```

## 🔍 Tool Call Detection

The agent parses LLM responses for patterns like:

```
TOOL_CALL: get_issues_by_status(status="To Do")
TOOL_CALL: get_issue_details(issue_key="PROJ-123")
```

## 🐛 Debugging

Enable debug logging to see the full request/response flow:

```bash
DEBUG=true
```

This will log:
- Full API requests to your LLM farm
- LLM responses
- Tool call parsing
- Tool execution results

## 🔒 SSL Configuration

For development environments where SSL certificates might not be valid:

```bash
LLM_VERIFY_SSL=false
```

⚠️ **Warning**: Only disable SSL verification in development environments.

## 🧪 Testing

Test the integration:

```bash
# Test imports and configuration
python tests/test_custom_llm.py

# Test the full application
python main.py
```

## 🔄 Migration from OpenAI/Ollama

The integration maintains the same interface as the previous OpenAI/Ollama setup:

- Same tool definitions
- Same conversation flow  
- Same Streamlit UI
- Only the LLM backend changed

## 📈 Performance Considerations

1. **Token Limits**: Configured via `LLM_MAX_TOKENS` (default: 2048)
2. **Temperature**: Configured via `LLM_TEMPERATURE` (default: 0.7)
3. **Conversation History**: Limited to last 20 messages to stay within token limits
4. **Tool Results**: Summarized to avoid token overflow

## 🔮 Future Enhancements

When your LLM farm supports automatic tool choice:

1. Update `custom_llm_client.py` to use `tools` parameter
2. Modify `jira_agent.py` to handle native tool calls
3. Remove prompt-based tool orchestration

This architecture is designed to be easily upgradeable when your API capabilities expand.
