# DockerForge Chat Assistant & Agent System User Guide

## Introduction

The DockerForge AI Chat Assistant and Agent System provide intelligent automation and context-aware assistance to help you manage your Docker environment more efficiently. This comprehensive guide explains how to use these powerful features to streamline your Docker workflow.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Chat Interface](#chat-interface)
3. [Chat Commands](#chat-commands)
4. [Agent System](#agent-system)
5. [Context-Aware Assistance](#context-aware-assistance)
6. [Customization Options](#customization-options)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Getting Started

### Accessing the Chat Assistant

The AI Chat Assistant is available from any page in DockerForge:

1. Click the chat icon (💬) in the top-right corner of the application to open the chat sidebar
2. Type your question or command in the input box at the bottom of the sidebar
3. Press Enter or click the send button to submit your message

The assistant will respond with relevant information, suggestions, or actions based on your input and current context.

### First-Time Setup

When you first use the Chat Assistant, you may want to:

1. Familiarize yourself with available [commands](#chat-commands)
2. Configure [chat preferences](#customization-options) to suit your workflow
3. Take the guided tour for a comprehensive introduction to all features

## Chat Interface

### Components

The chat interface consists of several components:

- **Chat Messages**: The main area displaying the conversation history
- **Chat Input**: The text field at the bottom for entering messages
- **Chat Header**: Contains options for managing conversations and accessing preferences
- **Feedback Controls**: Buttons on messages to provide feedback on responses

### Message Types

The chat displays different types of messages:

- **User Messages**: Your questions and commands
- **Assistant Responses**: Text replies from the AI
- **System Messages**: Notifications and status updates
- **Action Messages**: Interactive elements that perform specific functions
- **Resource Messages**: Links to documentation or external resources
- **Agent Messages**: Communications from specialized agents
- **Error Messages**: Information about failed operations

### Conversation Management

You can manage your conversations using the options in the chat header:

- **New Conversation**: Start a fresh conversation
- **Search History**: Find previous conversations
- **Export Conversation**: Save the current conversation as a text or HTML file
- **Clear History**: Remove all conversation history

## Chat Commands

Chat commands provide quick access to specific functions. To use a command, type a forward slash (/) followed by the command name and any required parameters.

### General Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/help [topic]` | Display help information | `/help security` |
| `/clear` | Clear the current conversation | `/clear` |
| `/search <term>` | Search through documentation and help resources | `/search volume mounting` |

### Container Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/logs <container> [options]` | Display container logs | `/logs web-server --tail 50` |
| `/restart <container>` | Restart a container | `/restart postgres` |
| `/stats [container]` | Show container resource usage | `/stats` |
| `/exec <container> <command>` | Execute a command in a container | `/exec web-server ls -la` |

### Security Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/scan <target> [type]` | Run a security scan | `/scan nginx vulnerability` |
| `/fix <vulnerability-id>` | Apply a fix for a vulnerability | `/fix CVE-2022-27664` |

### Agent Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/agent <agent-type> <task>` | Assign a task to a specific agent | `/agent container diagnose web-server` |
| `/agents [status]` | List available agents and their status | `/agents active` |

### System Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/checkpoint [name]` | Create a system checkpoint | `/checkpoint before-update` |
| `/restore <checkpoint-id>` | Restore to a previous checkpoint | `/restore checkpoint-20250315` |
| `/audit [options]` | Show system audit log | `/audit --since 2d` |

For a complete reference of all available commands, type `/help commands` in the chat.

## Agent System

The Agent System provides specialized AI agents that can perform complex tasks autonomously.

### Available Agents

DockerForge includes several specialized agents:

- **Container Agent**: Manages container operations and troubleshooting
- **Security Agent**: Handles vulnerability scanning and remediation
- **Optimization Agent**: Monitors and improves resource utilization
- **Documentation Agent**: Provides contextual help and information

### How Agents Work

Agents follow a standard workflow:

1. **Task Assignment**: You assign a task through chat or a direct request
2. **Task Planning**: The agent analyzes the request and creates a plan
3. **Approval**: You review and approve the proposed actions
4. **Execution**: The agent performs the approved actions
5. **Reporting**: The agent provides results and recommendations

### Agent Permissions

Agent actions require different levels of permission based on their impact:

| Permission Level | Description | Example Actions | Default Setting |
|------------------|-------------|----------------|-----------------|
| Read-Only | Actions that only read information | Viewing logs, scanning | Auto-approve |
| Low Impact | Minimal risk actions | Pulling images, creating volumes | Ask for approval |
| Medium Impact | Actions affecting container state | Starting/stopping containers | Ask for approval |
| High Impact | Actions that could affect data | Removing containers, applying patches | Detailed approval |
| Critical | Actions with significant impact | Removing volumes with data | Detailed approval with warnings |

You can configure permission settings in the Settings page under Agents & Automation.

### Using Agents Effectively

For the best experience with agents:

1. Be specific about the task you want to accomplish
2. Provide relevant context (container names, error messages)
3. Review proposed actions carefully before approval
4. Provide feedback on agent performance

## Context-Aware Assistance

The Chat Assistant adapts to your current context in the application to provide more relevant assistance.

### Contextual Understanding

The assistant understands your current:

- **Page context**: Which section of DockerForge you're viewing
- **Selected resource**: Which container, image, or other resource you're working with
- **Recent actions**: What operations you've recently performed
- **Conversation history**: Previous messages in the current conversation

### "Chat About This" Feature

Throughout the interface, you'll find "Chat About This" buttons that set specific context for the assistant:

- On container details pages
- On image information panels
- Next to error messages
- On security vulnerability reports

Clicking these buttons opens the chat with the relevant context pre-loaded.

## Customization Options

You can customize the Chat Assistant and Agent System to suit your preferences.

### Chat Preferences

Access chat preferences by clicking the settings icon in the chat header:

- **Message Display**: Control message density and formatting
- **Notification Settings**: Configure alert preferences
- **History Retention**: Set how long to keep conversation history
- **Response Verbosity**: Adjust the detail level of responses

### Agent Preferences

Configure agent behavior in the Settings page under Agents & Automation:

- **Permission Levels**: Set approval requirements for different action types
- **Execution Mode**: Control how agents execute tasks
- **Automation Level**: Determine how proactive agents should be
- **Reporting Detail**: Configure the depth of agent reports

## Troubleshooting

### Common Issues

| Issue | Possible Solution |
|-------|-------------------|
| Chat assistant doesn't understand my question | Try rephrasing with more specific details |
| Agent action fails | Check logs for details and try breaking the task into smaller steps |
| Command not recognized | Verify command syntax or type `/help commands` for reference |
| Context detection not working | Explicitly set context with "Chat About This" button |

### Getting Help

If you encounter issues with the Chat Assistant or Agent System:

1. Type `/help troubleshooting` in the chat for common solutions
2. Check the System Status page for any service disruptions
3. Review the application logs for detailed error information
4. Contact DockerForge support for persistent issues

## Best Practices

### Effective Communication

- Be specific in your requests and questions
- Provide necessary context and details
- Use plain language rather than specialized syntax
- Break complex tasks into smaller steps

### Security Considerations

- Review agent actions carefully before approval
- Create checkpoints before making significant changes
- Use detailed approval for high-impact operations
- Regularly check the audit log to monitor system changes

### Performance Optimization

- Close long-running conversations to free up resources
- Use specific commands for common tasks
- Set appropriate permission levels to reduce approval fatigue
- Provide feedback to help improve assistant responses

---

## Additional Resources

- [Command Reference](../reference/commands.md)
- [Agent System Technical Documentation](../technical/agent_system.md)
- [Security Best Practices](../security/best_practices.md)
- [Video Tutorials](https://dockerforge.example.com/tutorials)

---

*Last Updated: March 2025*
