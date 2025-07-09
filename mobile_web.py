#!/usr/bin/env python3
"""
Mobile Web Interface for Suna Desktop
A simple web server providing mobile access to Suna functionality.
"""

from flask import Flask, render_template, request, jsonify, session
import requests
import json
import os
import uuid
from datetime import datetime
import threading
import time
import re
import secrets
from urllib.parse import urlparse

class SunaMobileWeb:
    """Mobile web interface for Suna."""
    
    def __init__(self, host='0.0.0.0', port=5000, suna_api_url='http://localhost:8000'):
        self.app = Flask(__name__)
        # Security: Use cryptographically secure random key
        self.app.secret_key = secrets.token_bytes(32)
        self.host = host
        self.port = port
        self.suna_api_url = suna_api_url
        
        # Active conversations
        self.conversations = {}
        
        # Security: Input validation patterns
        self.uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
        
        self.setup_routes()
        
    def _validate_uuid(self, uuid_string):
        """Validate UUID format for security."""
        if not isinstance(uuid_string, str):
            return False
        return bool(self.uuid_pattern.match(uuid_string.lower()))
    
    def _validate_message(self, message):
        """Validate message content."""
        if not isinstance(message, str):
            return False, "Message must be a string"
        
        message = message.strip()
        if not message:
            return False, "Message cannot be empty"
        
        if len(message) > 10000:
            return False, "Message too long (max 10,000 characters)"
        
        return True, message
    
    def _safe_request_to_suna(self, endpoint, method='GET', data=None, timeout=30):
        """Make a safe request to Suna API with validation."""
        try:
            # Validate endpoint
            if not endpoint.startswith('/'):
                endpoint = '/' + endpoint
            
            url = self.suna_api_url + endpoint
            parsed_url = urlparse(url)
            
            # Security: Ensure we're only making requests to the configured Suna API
            if parsed_url.hostname not in ['localhost', '127.0.0.1']:
                expected_host = urlparse(self.suna_api_url).hostname
                if parsed_url.hostname != expected_host:
                    raise ValueError("Invalid API endpoint")
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'SunaMobileWeb/1.0'
            }
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
            
        except requests.exceptions.Timeout:
            raise Exception("Request to Suna API timed out")
        except requests.exceptions.ConnectionError:
            raise Exception("Could not connect to Suna API")
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def setup_routes(self):
        """Set up Flask routes."""
        
        @self.app.route('/')
        def index():
            """Main mobile interface."""
            return render_template('mobile_index.html')
        
        @self.app.route('/api/health')
        def health():
            """Health check for the mobile interface."""
            return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})
        
        @self.app.route('/api/suna/health')
        def suna_health():
            """Check Suna backend health."""
            try:
                response = self._safe_request_to_suna('/api/health', timeout=5)
                return jsonify({
                    "status": "connected" if response.status_code == 200 else "disconnected",
                    "suna_response": response.json() if response.status_code == 200 else None
                })
            except Exception as e:
                return jsonify({"status": "disconnected", "suna_response": None})
        
        @self.app.route('/api/chat/new', methods=['POST'])
        def new_chat():
            """Start a new chat conversation."""
            chat_id = str(uuid.uuid4())
            self.conversations[chat_id] = {
                "id": chat_id,
                "created_at": datetime.now().isoformat(),
                "messages": [],
                "thread_id": None,
                "agent_run_id": None
            }
            session['current_chat'] = chat_id
            return jsonify({"chat_id": chat_id, "status": "created"})
        
        @self.app.route('/api/chat/<chat_id>/messages')
        def get_messages(chat_id):
            """Get messages for a chat."""
            # Security: Validate chat_id
            if not self._validate_uuid(chat_id):
                return jsonify({"error": "Invalid chat ID"}), 400
            
            if chat_id in self.conversations:
                return jsonify({"messages": self.conversations[chat_id]["messages"]})
            return jsonify({"error": "Chat not found"}), 404
        
        @self.app.route('/api/chat/<chat_id>/send', methods=['POST'])
        def send_message(chat_id):
            """Send a message in a chat."""
            # Security: Validate chat_id
            if not self._validate_uuid(chat_id):
                return jsonify({"error": "Invalid chat ID"}), 400
            
            if chat_id not in self.conversations:
                return jsonify({"error": "Chat not found"}), 404
            
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No JSON data provided"}), 400
            except Exception:
                return jsonify({"error": "Invalid JSON data"}), 400
            
            # Validate message
            raw_message = data.get('message', '')
            is_valid, message = self._validate_message(raw_message)
            if not is_valid:
                return jsonify({"error": message}), 400
            
            # Add user message to conversation
            user_msg = {
                "id": str(uuid.uuid4()),
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            }
            self.conversations[chat_id]["messages"].append(user_msg)
            
            # Process message with Suna
            try:
                result = self._process_with_suna(chat_id, message)
                return jsonify(result)
            except Exception as e:
                error_msg = {
                    "id": str(uuid.uuid4()),
                    "role": "error",
                    "content": f"Error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
                self.conversations[chat_id]["messages"].append(error_msg)
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/conversations')
        def list_conversations():
            """List all conversations."""
            conv_list = []
            for conv_id, conv in self.conversations.items():
                conv_summary = {
                    "id": conv_id,
                    "created_at": conv["created_at"],
                    "message_count": len(conv["messages"]),
                    "last_message": conv["messages"][-1]["content"][:50] + "..." if conv["messages"] else "No messages"
                }
                conv_list.append(conv_summary)
            
            # Sort by creation time, newest first
            conv_list.sort(key=lambda x: x["created_at"], reverse=True)
            return jsonify({"conversations": conv_list})
    
    def _process_with_suna(self, chat_id, message):
        """Process message with Suna backend."""
        conversation = self.conversations[chat_id]
        
        # If this is the first message, initiate agent
        if not conversation["thread_id"]:
            response = self._safe_request_to_suna(
                '/api/agent/initiate',
                method='POST',
                data={
                    'prompt': message,
                    'model_name': 'claude-3-5-sonnet-20241022',
                    'enable_thinking': 'false',
                    'reasoning_effort': 'low',
                    'stream': 'false',  # No streaming for mobile
                    'enable_context_manager': 'false'
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                conversation["thread_id"] = result.get("thread_id")
                conversation["agent_run_id"] = result.get("agent_run_id")
                
                # Add system message
                system_msg = {
                    "id": str(uuid.uuid4()),
                    "role": "system",
                    "content": f"Conversation started (Thread: {conversation['thread_id'][:8]}...)",
                    "timestamp": datetime.now().isoformat()
                }
                conversation["messages"].append(system_msg)
                
                # Wait for response and add it
                response_text = self._wait_for_response(conversation["agent_run_id"])
                if response_text:
                    assistant_msg = {
                        "id": str(uuid.uuid4()),
                        "role": "assistant",
                        "content": response_text,
                        "timestamp": datetime.now().isoformat()
                    }
                    conversation["messages"].append(assistant_msg)
                
                return {"status": "success", "thread_id": conversation["thread_id"]}
            else:
                raise Exception(f"Failed to initiate agent: {response.status_code}")
        
        return {"status": "success"}
    
    def _wait_for_response(self, agent_run_id, timeout=60):
        """Wait for agent response (simplified for mobile)."""
        # Security: Validate agent_run_id
        if not self._validate_uuid(agent_run_id):
            return "Invalid agent run ID"
        
        # This is a simplified implementation
        # In a real application, you'd want to implement proper streaming or polling
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check agent run status
                response = self._safe_request_to_suna(f'/api/agent-run/{agent_run_id}')
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "completed":
                        # Try to get the response (this would need to be implemented in Suna API)
                        return "Response received from Suna agent"
                    elif data.get("status") == "failed":
                        return f"Agent failed: {data.get('error', 'Unknown error')}"
                
                time.sleep(2)  # Poll every 2 seconds
            except Exception as e:
                print(f"Error checking agent status: {e}")
                time.sleep(2)
        
        return "Response timeout"
    
    def create_templates(self):
        """Create HTML templates for the mobile interface."""
        templates_dir = "templates"
        os.makedirs(templates_dir, exist_ok=True)
        
        # Mobile index template
        mobile_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Suna Mobile</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 100%;
            margin: 0 auto;
            background: white;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: #4f46e5;
            color: white;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .status-bar {
            background: #f3f4f6;
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .chat-area {
            flex: 1;
            padding: 1rem;
            overflow-y: auto;
            background: #f9fafb;
        }
        
        .message {
            margin-bottom: 1rem;
            padding: 0.75rem;
            border-radius: 12px;
            max-width: 85%;
        }
        
        .message.user {
            background: #4f46e5;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        
        .message.assistant {
            background: white;
            border: 1px solid #e5e7eb;
            margin-right: auto;
        }
        
        .message.system {
            background: #fef3c7;
            border: 1px solid #f59e0b;
            margin: 0 auto;
            text-align: center;
            font-style: italic;
            font-size: 0.9rem;
        }
        
        .message.error {
            background: #fee2e2;
            border: 1px solid #ef4444;
            color: #dc2626;
        }
        
        .input-area {
            padding: 1rem;
            background: white;
            border-top: 1px solid #e5e7eb;
        }
        
        .input-container {
            display: flex;
            gap: 0.5rem;
        }
        
        .message-input {
            flex: 1;
            padding: 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font-size: 1rem;
            resize: none;
            min-height: 44px;
        }
        
        .send-btn {
            background: #4f46e5;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            font-size: 1rem;
            cursor: pointer;
            min-width: 60px;
        }
        
        .send-btn:disabled {
            background: #9ca3af;
            cursor: not-allowed;
        }
        
        .controls {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
        }
        
        .control-btn {
            background: #6b7280;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.5rem 0.75rem;
            font-size: 0.9rem;
            cursor: pointer;
        }
        
        .control-btn:hover {
            background: #4b5563;
        }
        
        .timestamp {
            font-size: 0.8rem;
            color: #6b7280;
            margin-top: 0.25rem;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #4f46e5;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (min-width: 768px) {
            .container {
                max-width: 768px;
                margin: 0 auto;
                border-radius: 12px;
                margin-top: 2rem;
                margin-bottom: 2rem;
                min-height: calc(100vh - 4rem);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Suna Mobile</h1>
            <p>AI Agent Platform</p>
        </div>
        
        <div class="status-bar">
            <span id="status">Connecting...</span>
        </div>
        
        <div class="chat-area" id="chatArea">
            <div class="message system">
                Welcome to Suna Mobile! Start a conversation by sending a message.
            </div>
        </div>
        
        <div class="input-area">
            <div class="controls">
                <button class="control-btn" onclick="newChat()">New Chat</button>
                <button class="control-btn" onclick="clearChat()">Clear</button>
            </div>
            <div class="input-container">
                <textarea 
                    id="messageInput" 
                    class="message-input" 
                    placeholder="Type your message..."
                    rows="1"
                ></textarea>
                <button id="sendBtn" class="send-btn" onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        let currentChatId = null;
        let isLoading = false;

        // Auto-resize textarea
        document.getElementById('messageInput').addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });

        // Send on Enter (but allow Shift+Enter for new line)
        document.getElementById('messageInput').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        async function checkStatus() {
            try {
                const response = await fetch('/api/suna/health');
                const data = await response.json();
                const statusEl = document.getElementById('status');
                
                if (data.status === 'connected') {
                    statusEl.textContent = '🟢 Connected to Suna';
                    statusEl.style.color = 'green';
                } else {
                    statusEl.textContent = '🔴 Disconnected from Suna';
                    statusEl.style.color = 'red';
                }
            } catch (error) {
                document.getElementById('status').textContent = '🔴 Connection Error';
                document.getElementById('status').style.color = 'red';
            }
        }

        async function newChat() {
            try {
                const response = await fetch('/api/chat/new', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                const data = await response.json();
                currentChatId = data.chat_id;
                clearChatDisplay();
                addMessage('system', 'New conversation started!');
            } catch (error) {
                addMessage('error', 'Failed to start new chat: ' + error.message);
            }
        }

        function clearChat() {
            clearChatDisplay();
            addMessage('system', 'Chat cleared. Messages are still saved on server.');
        }

        function clearChatDisplay() {
            const chatArea = document.getElementById('chatArea');
            chatArea.innerHTML = '';
        }

        async function sendMessage() {
            if (isLoading) return;
            
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            if (!currentChatId) {
                await newChat();
            }
            
            // Add user message to UI
            addMessage('user', message);
            input.value = '';
            input.style.height = 'auto';
            
            // Disable input
            setLoading(true);
            
            try {
                const response = await fetch(`/api/chat/${currentChatId}/send`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                });
                
                if (response.ok) {
                    // Add loading indicator
                    const loadingId = addMessage('system', '<span class="loading"></span> Suna is thinking...');
                    
                    // Wait a bit then try to get the response
                    setTimeout(async () => {
                        try {
                            const messagesResponse = await fetch(`/api/chat/${currentChatId}/messages`);
                            const messagesData = await messagesResponse.json();
                            
                            // Remove loading message
                            removeMessage(loadingId);
                            
                            // Add any new messages
                            const messages = messagesData.messages || [];
                            const lastMessage = messages[messages.length - 1];
                            
                            if (lastMessage && lastMessage.role === 'assistant') {
                                addMessage('assistant', lastMessage.content);
                            } else {
                                addMessage('assistant', 'Response received from Suna.');
                            }
                        } catch (error) {
                            removeMessage(loadingId);
                            addMessage('error', 'Failed to get response: ' + error.message);
                        }
                        
                        setLoading(false);
                    }, 2000);
                } else {
                    const errorData = await response.json();
                    addMessage('error', errorData.error || 'Failed to send message');
                    setLoading(false);
                }
            } catch (error) {
                addMessage('error', 'Failed to send message: ' + error.message);
                setLoading(false);
            }
        }

        function addMessage(role, content) {
            const chatArea = document.getElementById('chatArea');
            const messageEl = document.createElement('div');
            const messageId = 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            
            messageEl.id = messageId;
            messageEl.className = `message ${role}`;
            
            const timestamp = new Date().toLocaleTimeString();
            messageEl.innerHTML = `
                ${content}
                <div class="timestamp">${timestamp}</div>
            `;
            
            chatArea.appendChild(messageEl);
            chatArea.scrollTop = chatArea.scrollHeight;
            
            return messageId;
        }

        function removeMessage(messageId) {
            const messageEl = document.getElementById(messageId);
            if (messageEl) {
                messageEl.remove();
            }
        }

        function setLoading(loading) {
            isLoading = loading;
            const sendBtn = document.getElementById('sendBtn');
            const input = document.getElementById('messageInput');
            
            if (loading) {
                sendBtn.disabled = true;
                sendBtn.textContent = '...';
                input.disabled = true;
            } else {
                sendBtn.disabled = false;
                sendBtn.textContent = 'Send';
                input.disabled = false;
                input.focus();
            }
        }

        // Initialize
        checkStatus();
        setInterval(checkStatus, 10000); // Check status every 10 seconds
        
        // Auto-start a chat
        newChat();
    </script>
</body>
</html>"""
        
        with open(os.path.join(templates_dir, 'mobile_index.html'), 'w') as f:
            f.write(mobile_html)
    
    def run(self):
        """Run the mobile web server."""
        self.create_templates()
        print(f"Starting Suna Mobile Web Interface on http://{self.host}:{self.port}")
        
        # Security: Disable debug mode in production
        self.app.run(
            host=self.host, 
            port=self.port, 
            debug=False,
            threaded=True,
            use_reloader=False
        )

def main():
    """Main function to run the mobile web interface."""
    mobile_web = SunaMobileWeb()
    mobile_web.run()

if __name__ == "__main__":
    main()