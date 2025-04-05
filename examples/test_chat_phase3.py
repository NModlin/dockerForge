#!/usr/bin/env python3
"""
Test script for DockerForge Chat API (Phase 3).

This script tests the chat API endpoints implemented in Phase 3:
1. Chat session creation and management
2. Message sending and receiving
3. Context-aware responses
4. Suggestions functionality
"""

import os
import sys
import json
import requests
import pytest
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

API_BASE_URL = "http://localhost:54321/api"  # Default FastAPI port for development


@pytest.fixture(scope="module")
def session_id():
    """Create a chat session and return its ID."""
    try:
        # Create a new chat session
        response = requests.post(
            f"{API_BASE_URL}/chat/sessions",
            json={"title": f"Test Session {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
        )
        response.raise_for_status()

        session = response.json()
        print(f"Created Session ID: {session['id']}")

        # Return the session ID for use in tests
        yield session['id']

        # Clean up after tests
        try:
            requests.delete(f"{API_BASE_URL}/chat/sessions/{session['id']}")
        except Exception as e:
            print(f"Error cleaning up test session: {str(e)}")
    except Exception as e:
        print(f"Error creating chat session fixture: {str(e)}")
        pytest.fail(f"Failed to create chat session: {str(e)}")


@pytest.fixture(scope="module")
def message_text():
    """Return a test message."""
    return "Hello, I'm testing the chat API!"

def print_header(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)


def test_api_health():
    """Test API health endpoint."""
    print_header("Testing API Health")

    try:
        response = requests.get(f"{API_BASE_URL}/health")
        response.raise_for_status()

        print(f"API Health Response: {response.json()}")
        print(f"Status Code: {response.status_code}")

        return response.status_code == 200
    except Exception as e:
        print(f"Error testing API health: {str(e)}")
        return False


def test_chat_session_creation():
    """Test chat session creation."""
    print_header("Testing Chat Session Creation")

    try:
        # Create a new chat session
        response = requests.post(
            f"{API_BASE_URL}/chat/sessions",
            json={"title": f"Test Session {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
        )
        response.raise_for_status()

        session = response.json()
        print(f"Created Session ID: {session['id']}")
        print(f"Session Title: {session['title']}")
        print(f"Messages: {len(session['messages'])}")

        # Print the welcome message
        if session['messages']:
            print(f"Welcome Message: {session['messages'][0]['text']}")

        return session
    except Exception as e:
        print(f"Error creating chat session: {str(e)}")
        return None


def test_send_message(session_id, message_text, context=None):
    """Test sending a message and getting a response."""
    print_header(f"Testing Message Sending: '{message_text}'")

    # Prepare context data if provided
    context_data = None
    if context:
        context_data = {
            "current_page": context.get("current_page"),
            "current_container_id": context.get("current_container_id"),
            "current_image_id": context.get("current_image_id")
        }

    # Send a message
    response = requests.post(
        f"{API_BASE_URL}/chat/messages",
        json={
            "text": message_text,
            "session_id": session_id,
            "context": context_data,
            "type": "user"
        }
    )

    # Check response status
    assert response.status_code == 200, f"Failed to send message: {response.text}"

    # Extract the AI response
    result = response.json()
    assert "message" in result, "Response does not contain a message"

    ai_message = result["message"]
    suggestions = result.get("suggestions", [])

    print(f"AI Response: {ai_message['text']}")

    if suggestions:
        print("\nSuggestions:")
        for i, suggestion in enumerate(suggestions):
            print(f"{i+1}. {suggestion}")

    return result


def test_get_sessions():
    """Test getting all chat sessions."""
    print_header("Testing Get All Sessions")

    try:
        response = requests.get(f"{API_BASE_URL}/chat/sessions")
        response.raise_for_status()

        sessions = response.json()["sessions"]
        print(f"Retrieved {len(sessions)} sessions")

        # Print session info
        for i, session in enumerate(sessions[:5]):  # Show up to 5 sessions
            print(f"{i+1}. Session ID: {session['id']}, Title: {session['title']}")

        return sessions
    except Exception as e:
        print(f"Error getting sessions: {str(e)}")
        return []


def test_get_session_messages(session_id):
    """Test getting messages for a specific session."""
    print_header(f"Testing Get Session Messages (Session ID: {session_id})")

    response = requests.get(
        f"{API_BASE_URL}/chat/messages",
        params={"session_id": session_id}
    )

    # Check response status
    assert response.status_code == 200, f"Failed to get session messages: {response.text}"

    result = response.json()
    assert "messages" in result, "Response does not contain messages"

    messages = result["messages"]
    print(f"Retrieved {len(messages)} messages")

    # Print messages
    for i, message in enumerate(messages):
        print(f"{i+1}. [{message['type']}] {message['text'][:100]}...")

    return messages


def test_get_suggestions(session_id):
    """Test getting suggestions for a message."""
    print_header(f"Testing Get Suggestions (Session ID: {session_id})")

    # Send a message that should trigger suggestions
    response = requests.post(
        f"{API_BASE_URL}/chat/messages",
        json={
            "text": "How do I optimize Docker containers?",
            "session_id": session_id,
            "type": "user"
        }
    )

    # Check response status
    assert response.status_code == 200, f"Failed to send message: {response.text}"

    result = response.json()
    assert "suggestions" in result, "Response does not contain suggestions"

    suggestions = result.get("suggestions", [])
    print(f"Retrieved {len(suggestions)} suggestions")

    # Print suggestions
    for i, suggestion in enumerate(suggestions):
        print(f"{i+1}. {suggestion}")

    return suggestions


def test_delete_session(session_id):
    """Test deleting a chat session."""
    print_header(f"Testing Delete Session (Session ID: {session_id})")

    response = requests.delete(f"{API_BASE_URL}/chat/sessions/{session_id}")

    # Check response status
    assert response.status_code == 200, f"Failed to delete session: {response.text}"

    result = response.json()
    print(f"Delete response: {result}")

    assert result.get("success", False), "Session deletion was not successful"

    return result.get("success", False)


def test_context_awareness():
    """Test context-aware responses with different contexts."""
    print_header("Testing Context Awareness")

    try:
        # Create a session for context testing
        session_response = requests.post(
            f"{API_BASE_URL}/chat/sessions",
            json={"title": "Context Testing Session"}
        )
        session_response.raise_for_status()
        session = session_response.json()
        session_id = session["id"]

        print(f"Created context testing session with ID: {session_id}")

        # Test different contexts
        contexts = [
            {
                "name": "Container Context",
                "data": {
                    "current_page": "containers",
                    "current_container_id": "abc123",
                    "current_image_id": None
                },
                "message": "Tell me about this container"
            },
            {
                "name": "Image Context",
                "data": {
                    "current_page": "images",
                    "current_container_id": None,
                    "current_image_id": "def456"
                },
                "message": "Tell me about this image"
            },
            {
                "name": "Troubleshooting Context",
                "data": {
                    "current_page": "logs",
                    "current_container_id": "abc123",
                    "current_image_id": None
                },
                "message": "I'm getting an error with this container"
            }
        ]

        # Test each context
        results = []
        for context in contexts:
            print(f"\nTesting {context['name']}...")
            result = test_send_message(
                session_id=session_id,
                message_text=context["message"],
                context=context["data"]
            )
            results.append(result)

        # Clean up
        test_delete_session(session_id)

        return results
    except Exception as e:
        print(f"Error testing context awareness: {str(e)}")
        return []


def main():
    """Main function to run the tests."""
    print_header("DockerForge Chat API (Phase 3) Test")

    # Test API health
    if not test_api_health():
        print("API health check failed. Is the API server running?")
        return

    # Test chat session creation
    session = test_chat_session_creation()
    if not session:
        print("Failed to create chat session. Aborting tests.")
        return

    session_id = session["id"]

    # Test sending messages with different content
    test_messages = [
        "Hello, I'm testing the chat API!",
        "What can you tell me about Docker containers?",
        "How do I resolve a port conflict in Docker?",
        "Tell me about Docker Compose"
    ]

    for message in test_messages:
        test_send_message(session_id, message)

    # Test getting all sessions
    sessions = test_get_sessions()

    # Test getting messages for the session
    messages = test_get_session_messages(session_id)

    # Test context awareness
    context_results = test_context_awareness()

    # Test deleting the test session
    if test_delete_session(session_id):
        print(f"Successfully deleted test session (ID: {session_id})")

    print_header("Test Complete")
    print(f"Session Created: ID {session_id}")
    print(f"Messages Sent: {len(test_messages)}")
    print(f"Context Tests: {len(context_results)}")
    print(f"All Sessions: {len(sessions)}")


def test_chat_workflow():
    """Test the complete chat workflow using pytest."""
    print_header("DockerForge Chat API Test - Pytest Workflow")

    # Create a new session first
    session = test_chat_session_creation()
    session_id = session['id']
    message_text = "Hello, I'm testing the chat API!"

    # Send a message
    result = test_send_message(session_id, message_text)
    assert result is not None, "Failed to send message"

    # Test context-aware responses
    context = {
        "current_page": "containers",
        "current_container_id": "abc123",
    }
    result = test_send_message(session_id, "What can I do with this container?", context)
    assert result is not None, "Failed to send context-aware message"

    # Get session messages
    messages = test_get_session_messages(session_id)
    assert len(messages) >= 2, "Expected at least 2 messages in the session"

    # Test suggestions
    result = test_get_suggestions(session_id)
    assert result is not None, "Failed to get suggestions"

    print_header("Test Summary")
    print("Tests completed successfully")


if __name__ == "__main__":
    main()
