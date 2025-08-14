"""
Function calling implementation for OpenAI with SERPER search and Dockerfile generation
"""
import os
import json
import requests
import streamlit as st
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def serper_search(query: str) -> str:
    """
    Search Google using SERPER API and return snippets and links from organic results.
    
    Args:
        query: The search query
        
    Returns:
        JSON string containing search results with snippets and links
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return json.dumps({"error": "SERPER_API_KEY not found in environment variables"})
    
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "q": query,
        "num": 5
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract organic results
            organic_results = data.get("organic", [])
            
            # Format results with snippet and link
            search_results = []
            for result in organic_results[:5]:
                search_results.append({
                    "snippet": result.get("snippet", "No snippet available"),
                    "link": result.get("link", "")
                })
            
            return json.dumps({
                "query": query,
                "results": search_results
            })
            
        else:
            return json.dumps({"error": f"Search API error: HTTP {response.status_code}"})
            
    except Exception as e:
        return json.dumps({"error": f"Search error: {str(e)}"})


def generate_dockerfile(
    application_name: str,
    application_type: str = "python",
    port: int = 8000,
    additional_requirements: str = ""
) -> str:
    """
    Generate a Dockerfile using LLM and prompting with corporate settings.
    
    Args:
        application_name: Name of the application
        application_type: Type of application (python, node, java, etc.)
        port: Port number for the application
        additional_requirements: Additional requirements or packages
        
    Returns:
        JSON string containing the generated Dockerfile
    """
    try:
        import openai
        
        # Get corporate settings from environment variables
        base_image = os.getenv("CORPORATE_BASE_IMAGE", "your-private-registry.com/base-images/python:3.11-slim")
        proxy_host = os.getenv("CORPORATE_PROXY_HOST", "proxy.yourcompany.com")
        proxy_port = os.getenv("CORPORATE_PROXY_PORT", "8080")
        
        # Create detailed prompt for LLM
        prompt = f"""You are an expert DevOps engineer specializing in creating enterprise-grade Dockerfiles for corporate environments.

Generate a production-ready Dockerfile for the following specifications:

**Application Details:**
- Application Name: {application_name}
- Application Type: {application_type}
- Port: {port}
- Additional Requirements: {additional_requirements if additional_requirements else "None specified"}

**Corporate Environment Requirements:**
- Base Image: {base_image}
- Corporate Proxy Host: {proxy_host}
- Corporate Proxy Port: {proxy_port}
- Must include corporate root certificate installation
- Must use non-root user for security
- Must include health check
- Must configure package managers for corporate proxy

**Dockerfile Best Practices to Include:**
1. Multi-stage builds if beneficial
2. Minimal attack surface
3. Security best practices
4. Proper caching optimization
5. Corporate proxy configuration for package managers
6. Root certificate installation and configuration
7. Non-root user creation and usage
8. Health check implementation
9. Proper environment variable handling
10. Efficient layer ordering

**Special Instructions:**
- For Python: Configure pip for corporate proxy and trusted hosts
- For Node.js: Configure npm for corporate proxy and disable strict SSL
- For Java: Configure Maven/Gradle for corporate proxy
- For Go: Configure GOPROXY and certificate handling
- Include comments explaining each major section
- Use environment variables for proxy configuration

Generate ONLY the Dockerfile content without any additional explanation or markdown formatting. Start directly with the FROM instruction."""

        # Call OpenAI API
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert DevOps engineer who creates enterprise-grade Dockerfiles. Generate only the Dockerfile content without any additional text, explanations, or markdown formatting."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temperature for more consistent output
            max_tokens=2000
        )
        
        dockerfile_content = response.choices[0].message.content.strip()
        
        # Ensure the Dockerfile has proper structure
        if not dockerfile_content.startswith("FROM"):
            dockerfile_content = f"# Generated Dockerfile for {application_name}\n" + dockerfile_content
        
        return json.dumps({
            "application_name": application_name,
            "application_type": application_type,
            "dockerfile": dockerfile_content,
            "generation_method": "LLM-generated",
            "notes": [
                f"🚀 LLM-generated Dockerfile for {application_name} ({application_type})",
                f"📦 Base image: {base_image}",
                f"🌐 Configured for corporate proxy: {proxy_host}:{proxy_port}",
                f"� Application will run on port {port}",
                "🔒 Security best practices implemented",
                "📁 Remember to place corporate-root-ca.crt in build context",
                f"🛠️ Build command: docker build -t {application_name.lower().replace(' ', '-')} ."
            ]
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Dockerfile generation failed: {str(e)}",
            "application_name": application_name,
            "application_type": application_type
        })


# Tools format for OpenAI API function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "serper_search",
            "description": "Search Google using SERPER API to find relevant information. Use this for search queries, finding information, or when user asks to search for something.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find information on Google"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_dockerfile",
            "description": "Generate a Dockerfile using LLM and intelligent prompting with corporate settings including private base image, proxy, and root certificate. The LLM creates optimized, production-ready Dockerfiles based on application requirements.",
            "parameters": {
                "type": "object",
                "properties": {
                    "application_name": {
                        "type": "string",
                        "description": "Name of the application for the Dockerfile"
                    },
                    "application_type": {
                        "type": "string",
                        "description": "Type of application (python, node, java, go, other)",
                        "enum": ["python", "node", "java", "go", "other"]
                    },
                    "port": {
                        "type": "integer",
                        "description": "Port number for the application",
                        "default": 8000
                    },
                    "additional_requirements": {
                        "type": "string",
                        "description": "Additional packages, dependencies, or specific requirements to include"
                    }
                },
                "required": ["application_name", "application_type"]
            }
        }
    }
]


def format_function_result(function_name: str, result: str) -> str:
    """
    Format function results for better display in Streamlit chat interface.
    
    Args:
        function_name: Name of the executed function
        result: Raw result from the function
        
    Returns:
        Formatted result string optimized for Streamlit
    """
    try:
        result_data = json.loads(result)
        
        if function_name == "serper_search":
            if "error" in result_data:
                return f"❌ **Search Error:** {result_data['error']}"
            
            query = result_data.get('query', 'Unknown')
            results = result_data.get('results', [])
            
            if not results:
                return f"🔍 **No results found for:** '{query}'"
            
            formatted = f"🔍 **Search Results for:** *{query}*\n\n"
            
            for i, item in enumerate(results, 1):
                snippet = item.get('snippet', 'No snippet available').strip()
                link = item.get('link', '')
                
                formatted += f"**{i}.** {snippet}\n\n"
                if link:
                    formatted += f"🔗 **Source:** [{link}]({link})\n\n"
                formatted += "---\n\n"
            
            return formatted
            
        elif function_name == "generate_dockerfile":
            if "error" in result_data:
                return f"❌ **Dockerfile Generation Error:** {result_data['error']}"
            
            app_name = result_data.get('application_name', 'Unknown')
            app_type = result_data.get('application_type', 'Unknown')
            dockerfile = result_data.get('dockerfile', '')
            notes = result_data.get('notes', [])
            
            formatted = f"🤖 **LLM-Generated Dockerfile**\n\n"
            formatted += f"**Application:** {app_name}\n"
            formatted += f"**Type:** {app_type.title()}\n\n"
            formatted += "---\n\n"
            
            # Add the dockerfile in a code block
            formatted += "**📄 Dockerfile Content:**\n\n"
            formatted += "```dockerfile\n"
            formatted += dockerfile
            formatted += "\n```\n\n"
            
            # Add notes section
            if notes:
                formatted += "---\n\n"
                formatted += "📝 **Notes:**\n\n"
                for i, note in enumerate(notes, 1):
                    formatted += f"{i}. {note}\n"
            
            return formatted
            
    except json.JSONDecodeError:
        return f"⚠️ **Function Result:**\n\n```\n{result}\n```"
    except Exception as e:
        return f"❌ **Formatting Error:** {str(e)}\n\n**Raw Result:**\n```\n{result}\n```"
    
    return result


# ================================
# STREAMLIT UI
# ================================

def main():
    """Main Streamlit application"""
    import streamlit as st
    import openai
    
    # Page configuration
    st.set_page_config(
        page_title="AI Assistant", 
        page_icon="🤖",
        layout="wide"
    )
    
    # Title
    st.title("🤖 AI Assistant")
    st.markdown("*Your intelligent assistant with search and Dockerfile generation capabilities*")
        
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything or request search/Dockerfile generation..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            try:
                # Create a placeholder for response
                message_placeholder = st.empty()
                full_response = ""
                
                # Initialize OpenAI client
                client = openai.OpenAI()
                
                # Always use function calling - let OpenAI decide what to do
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a helpful AI assistant with access to search and Dockerfile generation tools. Use the appropriate tool when needed to provide comprehensive and accurate responses. For general conversation, respond directly without using tools."
                        },
                        *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    ],
                    tools=TOOLS,
                    tool_choice="auto",  # Let OpenAI decide when to use functions
                    temperature=0.7
                )
                
                message = response.choices[0].message
                
                # Check if tool was called
                if message.tool_calls:
                    tool_call = message.tool_calls[0]
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Show function execution
                    message_placeholder.markdown(f"🔄 Executing **{function_name}**...")
                    
                    # Direct function call - OpenAI already decided!
                    try:
                        if function_name == "serper_search":
                            function_result = serper_search(**function_args)
                        elif function_name == "generate_dockerfile":
                            function_result = generate_dockerfile(**function_args)
                        else:
                            function_result = json.dumps({"error": f"Unknown function: {function_name}"})
                    except Exception as e:
                        function_result = json.dumps({"error": f"Execution error in {function_name}: {str(e)}"})
                    
                    # Format and display the result
                    full_response = format_function_result(function_name, function_result)
                    message_placeholder.markdown(full_response)
                    
                else:
                    # No function call, use regular response
                    full_response = message.content if message.content else "I'm ready to help!"
                    message_placeholder.markdown(full_response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                error_message = f"❌ **Error:** {str(e)}"
                st.error(error_message)
                message_placeholder.markdown(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})


if __name__ == "__main__":
    main()
