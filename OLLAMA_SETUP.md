# 🦙 Ollama Setup Guide

This project now uses **Ollama with Llama3.1:8b** as the default LLM provider for privacy and cost-effectiveness.

## 📋 Quick Setup

### 1. Install Ollama

#### macOS/Linux:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Windows:
Download and install from: https://ollama.ai/download

### 2. Pull the Llama3.1:8b Model
```bash
ollama pull llama3.1:8b
```

### 3. Start Ollama Server
```bash
ollama serve
```
*Note: Ollama usually starts automatically after installation*

### 4. Verify Installation
```bash
ollama list
# Should show llama3.1:8b in the list

curl http://localhost:11434/api/version
# Should return version information
```

### 5. Configure Environment Variables
Update your `.env` file:
```env
# Ollama Configuration (currently active)
OLLAMA_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434

# Other required variables...
JIRA_SERVER_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@example.com
JIRA_API_TOKEN=your-api-token
```

### 6. Install Python Dependencies
```bash
pip install langchain-ollama
```

## 🔄 Switching Back to OpenAI (If Needed)

1. **Uncomment OpenAI code** in `jira_agent.py`:
   ```python
   # Uncomment these lines:
   from langchain_openai import ChatOpenAI
   
   # In __init__ method, uncomment:
   openai_key = os.getenv("OPENAI_API_KEY")
   if not openai_key:
       raise ValueError("OPENAI_API_KEY is required")
   
   self.llm = ChatOpenAI(
       model="gpt-4o-mini",
       api_key=openai_key,
       temperature=0.1
   )
   ```

2. **Comment out Ollama code** in `jira_agent.py`:
   ```python
   # Comment these lines:
   # from langchain_ollama import ChatOllama
   # self.llm = ChatOllama(...)
   ```

3. **Update requirements.txt**:
   ```
   # Uncomment:
   langchain-openai>=0.1.0
   
   # Comment:
   # langchain-ollama>=0.1.0
   ```

4. **Add OpenAI API key** to `.env`:
   ```env
   OPENAI_API_KEY=your-openai-api-key
   ```

## 🎯 Benefits of Ollama

- ✅ **Free**: No API costs or usage limits
- ✅ **Private**: All processing happens locally
- ✅ **Fast**: Once model is loaded, responses are quick
- ✅ **Reliable**: No network dependency for inference
- ✅ **Flexible**: Easy to switch models or providers

## 🚨 Troubleshooting

### Issue: "Connection refused" error
**Solution**: Make sure Ollama server is running:
```bash
ollama serve
```

### Issue: Model not found
**Solution**: Pull the model first:
```bash
ollama pull llama3.1:8b
```

### Issue: Slow first response
**Solution**: This is normal - first query loads the model into memory. Subsequent queries will be faster.

### Issue: Out of memory
**Solution**: Try a smaller model:
```env
OLLAMA_MODEL=llama3.2:3b  # Smaller, uses less RAM
```

## 📊 Performance Comparison

| Provider | Cost | Privacy | Speed | Setup |
|----------|------|---------|-------|--------|
| Ollama | Free | 🟢 Local | 🟡 Good | 🟡 Medium |
| OpenAI | Paid | 🔴 Cloud | 🟢 Fast | 🟢 Easy |

Choose based on your priorities: privacy & cost (Ollama) vs convenience & speed (OpenAI).
