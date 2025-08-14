"""
Test script for function calling capabilities
"""
import os
from dotenv import load_dotenv
from function import serper_search, generate_dockerfile, should_use_functions, format_function_result

# Load environment variables
load_dotenv()

def test_search_function():
    """Test the SERPER search function"""
    print("🔍 Testing SERPER Search Function...")
    print("-" * 40)
    
    query = "Python web frameworks"
    result = serper_search(query)
    formatted_result = format_function_result("serper_search", result)
    
    print(f"Query: {query}")
    print(f"Result:\n{formatted_result}")
    print()

def test_dockerfile_function():
    """Test the Dockerfile generation function"""
    print("🐳 Testing Dockerfile Generation Function...")
    print("-" * 40)
    
    result = generate_dockerfile(
        application_name="my-python-api",
        application_type="python",
        port=8000,
        additional_requirements="fastapi uvicorn"
    )
    formatted_result = format_function_result("generate_dockerfile", result)
    
    print(f"Generated Dockerfile:\n{formatted_result}")
    print()

def test_intent_detection():
    """Test the intent detection logic"""
    print("🧠 Testing Intent Detection...")
    print("-" * 40)
    
    test_messages = [
        "Search for Python tutorials",
        "Create a Dockerfile for my Node.js app", 
        "What's the meaning of life?",
        "Find information about machine learning",
        "Generate a Docker container for my Java application",
        "How are you today?",
        "Look up best practices for REST APIs"
    ]
    
    for message in test_messages:
        uses_functions = should_use_functions(message)
        print(f"Message: '{message}'")
        print(f"Uses Functions: {uses_functions}")
        print()

def main():
    """Run all tests"""
    print("🚀 Function Calling Test Suite")
    print("=" * 50)
    print()
    
    # Check environment variables
    print("🔧 Environment Check...")
    print("-" * 40)
    openai_key = "✅" if os.getenv("OPENAI_API_KEY") else "❌"
    serper_key = "✅" if os.getenv("SERPER_API_KEY") else "❌"
    print(f"OpenAI API Key: {openai_key}")
    print(f"SERPER API Key: {serper_key}")
    print()
    
    # Run tests
    test_intent_detection()
    
    if os.getenv("SERPER_API_KEY"):
        test_search_function()
    else:
        print("⚠️  Skipping search test - SERPER_API_KEY not found")
        print()
    
    test_dockerfile_function()
    
    print("✅ Tests completed!")

if __name__ == "__main__":
    main()
