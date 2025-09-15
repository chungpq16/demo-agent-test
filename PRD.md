# Product Requirements Document (PRD): GenAI Application with LLM Farm Integration

## Overview

Develop a GenAI application leveraging LLM Farm as the backend for prompt-based orchestration, enabling seamless interaction with Jira. The application will support key Jira operations and be designed for scalability, maintainability, and robust debugging.

## Objectives

- Integrate LLM Farm for natural language processing and orchestration.
- Provide prompt-based access to Jira functionalities.
- Ensure secure and configurable deployment using environment variables.
- Implement comprehensive debug logging for troubleshooting and monitoring.
- Structure codebase for scalability and maintainability.

## Features

### 1. LLM Farm Integration

- Use LLM Farm as the core engine for prompt orchestration.
- Support customizable system and user prompts.
- Read LLM Farm API key and URL from `.env` file.

Example of using LLM Farm:

```python
from openai import OpenAI

class llmfarminf():
    def __init__(self, model = "gpt-4o-mini") -> None:
        self.client = OpenAI(
            api_key="abcxyz-key",
            base_url="https://aoai-farm.example.com/api/openai/deployments/askbosch-prod-farm-openai-gpt-4o-mini-2024-07-18",
            default_headers = {"genaiplatform-farm-subscription-key": "abcxyz-key "}
        )

    def _gen_message(self, sysprompt, userprompt):
        return [
            {"role" : "system", "content" : sysprompt},
            {"role" : "user", "content" : userprompt}
        ]

    def _completion(self, usertext, sysprompt):
        messages = self._gen_message(sysprompt, usertext)
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            extra_query={"api-version": "2024-08-01-preview"}
        )
        return response.choices[0].message.content

if __name__ == "__main__":
    obj = llmfarminf()
    prompt = "5 facts about earh"
    print(obj._completion(prompt, "You are a helpful assistant"))


```

### 2. Jira Integration

- Connect to Jira using the [atlassian-python-api](https://github.com/atlassian-api/atlassian-python-api) SDK for streamlined REST API interactions.
- Read Jira URL, username, token, and project from the `.env` file.
- Support the following operations:
    - Get all Jira issues.
    - Get Jira issues by status (open, in-progress, done).
    - Get detailed information of a specific issue.
- Leverage the SDK for simplified authentication, error handling, and data retrieval.

### 3. Prompt-Based Orchestration

- Design prompts to trigger Jira operations via LLM Farm.
- Allow easy extension for new tools and operations.

### 4. Configuration Management

- Store all sensitive and environment-specific parameters in a `.env` file:
    - `API_KEY`
    - `LLM_FARM_URL`
    - `JIRA_URL`
    - `JIRA_USERNAME`
    - `JIRA_TOKEN`
    - `JIRA_PROJECT`

### 5. Debug Logging

- Implement debug-level logging throughout the application.
- Log key events, API requests/responses, and errors for traceability.

### 6. Code Organization

- Modularize code into logical components:
    - `llm_farm_client.py`: Handles LLM Farm communication.
    - `jira_client.py`: Manages Jira API interactions.
    - `orchestrator.py`: Implements prompt-based orchestration logic.
    - `logger.py`: Configures and manages logging.
    - `main.py`: Application entry point.
- Follow best practices for scalability and maintainability (e.g., dependency injection, clear interfaces, error handling).

## Non-Functional Requirements

- Secure handling of credentials and sensitive data.
- Clear documentation and inline code comments.
- Unit and integration tests for core modules.

## Example Directory Structure

```
genai-app/
├── llm_farm_client/
│   └── __init__.py
├── jira_client/
│   └── __init__.py
├── orchestrator/
│   └── __init__.py
├── logger/
│   └── __init__.py
├── main.py
├── .env
├── requirements.txt
└── README.md
```

- Each core module (`llm_farm_client`, `jira_client`, `orchestrator`, `logger`) resides in its own sub-folder as a Python package.
- Additional module files can be added within each sub-folder as needed.
- The application entry point remains `main.py` at the root level.

## Future Enhancements

- Add support for additional tools and integrations.
- Implement user authentication and role-based access.
- Provide a web-based UI for prompt management.