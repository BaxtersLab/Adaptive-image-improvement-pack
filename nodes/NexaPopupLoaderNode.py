import threading
import socket
import http.server
import socketserver
import webbrowser
import atexit
import time
import os
import shutil
import subprocess
import json
import traceback
import requests

# ---- Global state for tags and models ----
_global_semantic_tags = ""
_global_style_tags = ""
_global_models = {"A": None, "B": None}  # Separate models for each chat
_global_gui_lock = threading.Lock()
_captured_responses = {}  # Keyed by chat_id; populated by capture_response()

# ---- Dynamic HTML GUI content ----
def get_html_page(semantic_tags, style_tags):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexa AI Chat - Tag-Enhanced Session</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #2d3748; /* Charcoal gray background */
            min-height: 100vh;
            color: #e2e8f0;
            margin: 20px; /* Charcoal gray margins */
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: #1a202c; /* Darker charcoal */
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            border: 2px solid #4a5568;
        }}

        .header {{
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom: 2px solid #4a5568;
        }}

        .header h1 {{
            font-size: 2.2em;
            margin-bottom: 8px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        .header .subtitle {{
            font-size: 1em;
            opacity: 0.9;
        }}

        .dual-chat-container {{
            display: flex;
            min-height: 600px;
        }}

        .chat-section {{
            flex: 1;
            display: flex;
            flex-direction: column;
            border-right: 1px solid #4a5568;
        }}

        .chat-section:last-child {{
            border-right: none;
        }}

        .chat-header {{
            padding: 15px 20px;
            background: #2d3748;
            border-bottom: 1px solid #4a5568;
            text-align: center;
        }}

        .chat-header h2 {{
            color: #e2e8f0;
            margin: 0;
            font-size: 1.4em;
        }}

        .tags-display {{
            padding: 15px;
            background: #1a202c;
            border-bottom: 1px solid #4a5568;
        }}

        .tags-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }}

        .tag-group {{
            background: #2d3748;
            padding: 12px;
            border-radius: 8px;
            border-left: 3px solid #667eea;
        }}

        .tag-group h3 {{
            color: #e2e8f0;
            margin-bottom: 6px;
            font-size: 0.9em;
        }}

        .tag-content {{
            background: #1a202c;
            padding: 8px;
            border-radius: 4px;
            border: 1px solid #4a5568;
            font-family: 'Courier New', monospace;
            font-size: 0.8em;
            word-wrap: break-word;
            min-height: 30px;
            color: #e2e8f0;
        }}

        .model-section {{
            padding: 15px;
            background: #1a202c;
            border-bottom: 1px solid #4a5568;
        }}

        .file-input-wrapper {{
            position: relative;
            display: inline-block;
            margin-right: 12px;
        }}

        .file-input {{
            display: none;
        }}

        .file-input-label {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 10px 18px;
            border-radius: 6px;
            cursor: pointer;
            display: inline-block;
            transition: all 0.3s ease;
            font-weight: 500;
            font-size: 0.9em;
        }}

        .file-input-label:hover {{
            transform: translateY(-1px);
            box-shadow: 0 3px 12px rgba(102, 126, 234, 0.3);
        }}

        .file-name {{
            margin-left: 8px;
            color: #a0aec0;
            font-style: italic;
            font-size: 0.8em;
        }}

        .load-btn {{
            background: linear-gradient(135deg, #48bb78, #38a169);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
            font-size: 0.9em;
        }}

        .load-btn:hover {{
            transform: translateY(-1px);
            box-shadow: 0 3px 12px rgba(72, 187, 120, 0.3);
        }}

        .load-btn:disabled {{
            background: #4a5568;
            cursor: not-allowed;
            transform: none;
        }}

        .status {{
            margin-top: 12px;
            padding: 8px 12px;
            border-radius: 4px;
            font-weight: 500;
            font-size: 0.85em;
        }}

        .status.loading {{
            background: #2d3748;
            color: #63b3ed;
            border: 1px solid #3182ce;
        }}

        .status.success {{
            background: #2d3748;
            color: #68d391;
            border: 1px solid #38a169;
        }}

        .status.error {{
            background: #2d3748;
            color: #fc8181;
            border: 1px solid #e53e3e;
        }}

        .chat-messages {{
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            background: #1a202c;
        }}

        .message {{
            margin-bottom: 12px;
            padding: 10px 12px;
            border-radius: 8px;
            max-width: 85%;
            animation: fadeIn 0.3s ease-in;
            font-size: 0.9em;
        }}

        .message.user {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 3px;
        }}

        .message.bot {{
            background: #2d3748;
            color: #e2e8f0;
            border-bottom-left-radius: 3px;
            border: 1px solid #4a5568;
        }}

        .message.system {{
            background: #4a5568;
            color: #fbb6ce;
            text-align: center;
            border: 1px solid #718096;
            max-width: 100%;
            font-size: 0.8em;
        }}

        .chat-input-area {{
            display: flex;
            gap: 8px;
            align-items: center;
            padding: 15px;
            background: #2d3748;
            border-top: 1px solid #4a5568;
        }}

        .chat-input {{
            flex: 1;
            padding: 10px 12px;
            border: 1px solid #4a5568;
            border-radius: 20px;
            font-size: 0.9em;
            outline: none;
            transition: border-color 0.3s ease;
            background: #1a202c;
            color: #e2e8f0;
        }}

        .chat-input:focus {{
            border-color: #667eea;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
        }}

        .send-btn {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 10px 18px;
            border-radius: 20px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
            min-width: 70px;
            font-size: 0.9em;
        }}

        .send-btn:hover {{
            transform: translateY(-1px);
            box-shadow: 0 3px 12px rgba(102, 126, 234, 0.3);
        }}

        .send-btn:disabled {{
            background: #4a5568;
            cursor: not-allowed;
            transform: none;
        }}

        .loading-spinner {{
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}

        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .typing-indicator {{
            display: none;
            font-style: italic;
            color: #a0aec0;
            padding: 6px 12px;
            font-size: 0.8em;
        }}

        .model-info {{
            background: #2d3748;
            padding: 8px 12px;
            border-radius: 4px;
            margin-top: 8px;
            font-size: 0.8em;
            color: #e2e8f0;
            border: 1px solid #4a5568;
        }}

        .refresh-btn {{
            background: #4a5568;
            color: #e2e8f0;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8em;
            margin-left: 8px;
            transition: all 0.3s ease;
        }}

        .refresh-btn:hover {{
            background: #718096;
        }}

        @media (max-width: 768px) {{
            body {{
                margin: 10px;
            }}

            .dual-chat-container {{
                flex-direction: column;
                min-height: auto;
            }}

            .chat-section {{
                border-right: none;
                border-bottom: 1px solid #4a5568;
            }}

            .header h1 {{
                font-size: 1.8em;
            }}

            .tags-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Nexa AI Dual Chat Sessions</h1>
            <div class="subtitle">Tag-Enhanced Parallel Conversations</div>
        </div>

        <div class="dual-chat-container">
            <!-- Chat A Section -->
            <div class="chat-section">
                <div class="chat-header">
                    <h2>💬 Chat A</h2>
                </div>

                <div class="tags-display">
                    <div class="tags-grid">
                        <div class="tag-group">
                            <h3>🎵 Semantic Tags</h3>
                            <div class="tag-content" id="semanticTagsA">{semantic_tags}</div>
                        </div>
                        <div class="tag-group">
                            <h3>🎨 Style Tags</h3>
                            <div class="tag-content" id="styleTagsA">{style_tags}</div>
                        </div>
                    </div>
                    <button class="refresh-btn" onclick="refreshTags('A')">🔄 Refresh</button>
                </div>

                <div class="model-section">
                    <div class="file-input-wrapper">
                        <input type="file" id="modelFileA" class="file-input" accept=".gguf,.bin,.safetensors,.pth,.ckpt,.onnx,.pb">
                        <label for="modelFileA" class="file-input-label">📂 Choose Model A</label>
                        <span class="file-name" id="fileNameA">No file selected</span>
                    </div>
                    <button class="load-btn" id="loadBtnA" onclick="loadModel('A')">
                        <span id="loadTextA">⬆️ Load Model</span>
                        <div class="loading-spinner" id="loadSpinnerA" style="display: none;"></div>
                    </button>
                    <div id="statusA" class="status" style="display: none;"></div>
                    <div id="modelInfoA" class="model-info" style="display: none;"></div>
                </div>

                <div class="chat-messages" id="chatMessagesA">
                    <div class="message system">
                        Welcome to Chat A! Load a model and start your tag-enhanced conversation.
                    </div>
                </div>
                <div class="typing-indicator" id="typingIndicatorA">AI A is thinking...</div>
                <div class="chat-input-area">
                    <input type="text" id="messageInputA" class="chat-input" placeholder="Chat with AI A..." onkeypress="handleKeyPress(event, 'A')">
                    <button class="send-btn" id="sendBtnA" onclick="sendMessage('A')">
                        📤 Send
                    </button>
                </div>
            </div>

            <!-- Chat B Section -->
            <div class="chat-section">
                <div class="chat-header">
                    <h2>💬 Chat B</h2>
                </div>

                <div class="tags-display">
                    <div class="tags-grid">
                        <div class="tag-group">
                            <h3>🎵 Semantic Tags</h3>
                            <div class="tag-content" id="semanticTagsB">{semantic_tags}</div>
                        </div>
                        <div class="tag-group">
                            <h3>🎨 Style Tags</h3>
                            <div class="tag-content" id="styleTagsB">{style_tags}</div>
                        </div>
                    </div>
                    <button class="refresh-btn" onclick="refreshTags('B')">🔄 Refresh</button>
                </div>

                <div class="model-section">
                    <div class="file-input-wrapper">
                        <input type="file" id="modelFileB" class="file-input" accept=".gguf,.bin,.safetensors,.pth,.ckpt,.onnx,.pb">
                        <label for="modelFileB" class="file-input-label">📂 Choose Model B</label>
                        <span class="file-name" id="fileNameB">No file selected</span>
                    </div>
                    <button class="load-btn" id="loadBtnB" onclick="loadModel('B')">
                        <span id="loadTextB">⬆️ Load Model</span>
                        <div class="loading-spinner" id="loadSpinnerB" style="display: none;"></div>
                    </button>
                    <div id="statusB" class="status" style="display: none;"></div>
                    <div id="modelInfoB" class="model-info" style="display: none;"></div>
                </div>

                <div class="chat-messages" id="chatMessagesB">
                    <div class="message system">
                        Welcome to Chat B! Load a model and start your tag-enhanced conversation.
                    </div>
                </div>
                <div class="typing-indicator" id="typingIndicatorB">AI B is thinking...</div>
                <div class="chat-input-area">
                    <input type="text" id="messageInputB" class="chat-input" placeholder="Chat with AI B..." onkeypress="handleKeyPress(event, 'B')">
                    <button class="send-btn" id="sendBtnB" onclick="sendMessage('B')">
                        📤 Send
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // State management for dual chats
        let currentModels = { A: null, B: null };
        let isLoading = { A: false, B: false };
        let isTyping = { A: false, B: false };

        // File input handling
        document.getElementById('modelFileA').addEventListener('change', function(e) {{
            const file = e.target.files[0];
            document.getElementById('fileNameA').textContent = file ? file.name : 'No file selected';
        }});

        document.getElementById('modelFileB').addEventListener('change', function(e) {{
            const file = e.target.files[0];
            document.getElementById('fileNameB').textContent = file ? file.name : 'No file selected';
        }});

        function showStatus(chatId, message, type = 'info') {{
            const statusEl = document.getElementById(`status${{chatId}}`);
            statusEl.textContent = message;
            statusEl.className = `status ${{type}}`;
            statusEl.style.display = 'block';
            setTimeout(() => {{
                statusEl.style.display = 'none';
            }}, 5000);
        }}

        function setLoading(chatId, loading) {{
            isLoading[chatId] = loading;
            const loadBtn = document.getElementById(`loadBtn${{chatId}}`);
            const loadText = document.getElementById(`loadText${{chatId}}`);
            const loadSpinner = document.getElementById(`loadSpinner${{chatId}}`);

            loadBtn.disabled = loading;
            loadText.style.display = loading ? 'none' : 'inline';
            loadSpinner.style.display = loading ? 'inline-block' : 'none';
        }}

        function loadModel(chatId) {{
            const fileInput = document.getElementById(`modelFile${{chatId}}`);
            const file = fileInput.files[0];
            if (!file) {{
                showStatus(chatId, 'Please select a model file first', 'error');
                return;
            }}

            setLoading(chatId, true);

            const formData = new FormData();
            formData.append('file', file);
            formData.append('chat_id', chatId);

            fetch('/load', {{ method: 'POST', body: formData }})
            .then(response => response.text())
            .then(result => {{
                setLoading(chatId, false);
                if (result.includes('successfully')) {{
                    currentModels[chatId] = file.name;
                    showStatus(chatId, `✅ Model "${{file.name}}" loaded successfully!`, 'success');
                    updateModelInfo(chatId);
                    addMessage(chatId, 'System', `Model "${{file.name}}" loaded and ready for chat!`, 'system');
                }} else {{
                    showStatus(chatId, `❌ Failed to load model: ${{result}}`, 'error');
                }}
            }})
            .catch(error => {{
                setLoading(chatId, false);
                showStatus(chatId, `❌ Error loading model: ${{error.message}}`, 'error');
            }});
        }}

        function updateModelInfo(chatId) {{
            const modelInfoEl = document.getElementById(`modelInfo${{chatId}}`);
            if (currentModels[chatId]) {{
                modelInfoEl.textContent = `Current Model: ${{currentModels[chatId]}}`;
                modelInfoEl.style.display = 'block';
            }} else {{
                modelInfoEl.style.display = 'none';
            }}
        }}

        function addMessage(chatId, sender, message, type = 'user') {{
            const chatMessages = document.getElementById(`chatMessages${{chatId}}`);
            const messageEl = document.createElement('div');
            messageEl.className = `message ${{type}}`;
            messageEl.innerHTML = `<strong>${{sender}}:</strong> ${{message.replace(/\n/g, '<br>')}}`;
            chatMessages.appendChild(messageEl);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }}

        function setTyping(chatId, typing) {{
            isTyping[chatId] = typing;
            const indicator = document.getElementById(`typingIndicator${{chatId}}`);
            const sendBtn = document.getElementById(`sendBtn${{chatId}}`);

            indicator.style.display = typing ? 'block' : 'none';
            sendBtn.disabled = typing;

            if (typing) {{
                indicator.scrollIntoView({{ behavior: 'smooth' }});
            }}
        }}

        function sendMessage(chatId) {{
            const messageInput = document.getElementById(`messageInput${{chatId}}`);
            const message = messageInput.value.trim();
            if (!message || isTyping[chatId]) return;

            if (!currentModels[chatId]) {{
                showStatus(chatId, 'Please load a model first', 'error');
                return;
            }}

            addMessage(chatId, 'You', message);
            messageInput.value = '';
            setTyping(chatId, true);

            fetch('/chat', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{message: message, chat_id: chatId}})
            }})
            .then(response => response.text())
            .then(result => {{
                setTyping(chatId, false);
                if (result.trim()) {{
                    addMessage(chatId, 'AI', result);
                    // Capture the response for comparison
                    captureResponse(chatId, message, result);
                }} else {{
                    addMessage(chatId, 'System', 'I apologize, but I couldn\\'t generate a response. Please try rephrasing your message.', 'system');
                }}
            }})
            .catch(error => {{
                setTyping(chatId, false);
                addMessage(chatId, 'System', `Error: ${{error.message}}`, 'system');
                showStatus(chatId, `❌ Chat error: ${{error.message}}`, 'error');
            }});
        }}

        function handleKeyPress(event, chatId) {{
            if (event.key === 'Enter' && !event.shiftKey) {{
                event.preventDefault();
                sendMessage(chatId);
            }}
        }}

        function refreshTags(chatId) {{
            fetch('/tags')
            .then(response => response.json())
            .then(data => {{
                document.getElementById(`semanticTags${{chatId}}`).textContent = data.semantic_tags;
                document.getElementById(`styleTags${{chatId}}`).textContent = data.style_tags;
                showStatus(chatId, '🔄 Tags refreshed', 'success');
            }})
            .catch(error => {{
                showStatus(chatId, '❌ Failed to refresh tags', 'error');
            }});
        }}

        function captureResponse(chatId, userMessage, aiResponse) {{
            fetch('/capture', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    chat_id: chatId,
                    message: userMessage,
                    response: aiResponse
                }})
            }})
            .then(response => response.text())
            .then(result => {{
                console.log(`Response captured for chat ${{chatId}}`);
            }})
            .catch(error => {{
                console.error(`Failed to capture response for chat ${{chatId}}:`, error);
            }});
        }}

        // Initialize both chats
        updateModelInfo('A');
        updateModelInfo('B');

        // Auto-focus first chat input
        document.getElementById('messageInputA').focus();
    </script>
</body>
</html>
"""

# ---- HTTP handler ----
class LocalGUIRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/tags':
            self.handle_tags()
        else:
            with _global_gui_lock:
                semantic_tags = _global_semantic_tags
                style_tags = _global_style_tags
            html = get_html_page(semantic_tags, style_tags)
            html_bytes = html.encode('utf-8')
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html_bytes)))
            self.end_headers()
            self.wfile.write(html_bytes)

    def do_POST(self):
        if self.path == '/load':
            self.handle_load()
        elif self.path == '/chat':
            self.handle_chat()
        elif self.path == '/capture':
            self.handle_capture()
        else:
            self.send_error(404)

    def handle_tags(self):
        """Return current tags as JSON"""
        with _global_gui_lock:
            semantic_tags = _global_semantic_tags
            style_tags = _global_style_tags

        import json
        response_data = {
            "semantic_tags": semantic_tags,
            "style_tags": style_tags
        }

        response_json = json.dumps(response_data)
        response_bytes = response_json.encode('utf-8')

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def handle_load(self):
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            # Parse multipart form data
            content_type = self.headers.get('Content-Type', '')
            if 'boundary=' not in content_type:
                self.send_error(400, "Invalid content type")
                return

            boundary = content_type.split('boundary=')[1].encode()
            if not boundary:
                self.send_error(400, "No boundary found")
                return

            # Split multipart data
            parts = body.split(b'--' + boundary)
            file_data = None
            filename = None

            for part in parts:
                if b'filename=' in part:
                    lines = part.split(b'\r\n')
                    content_start = -1

                    for i, line in enumerate(lines):
                        if line.startswith(b'Content-Disposition'):
                            # Extract filename
                            line_str = line.decode('utf-8', errors='ignore')
                            if 'filename=' in line_str:
                                filename_part = line_str.split('filename="')
                                if len(filename_part) > 1:
                                    filename = filename_part[1].split('"')[0]

                        elif line == b'' and content_start == -1:
                            # Start of content
                            content_start = i + 1
                            break

                    if content_start >= 0 and content_start < len(lines):
                        # Extract file data (stop at next boundary)
                        file_data = b'\r\n'.join(lines[content_start:])
                        # Remove trailing boundary markers
                        if b'\r\n--' in file_data:
                            file_data = file_data.split(b'\r\n--')[0]
                        break

            if not file_data or not filename:
                self.send_error(400, "No file data or filename found")
                return

            # Validate file extension
            allowed_extensions = ['.gguf', '.bin', '.safetensors', '.pth', '.ckpt', '.onnx', '.pb']
            if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
                self.send_error(400, f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}")
                return

            # Create models directory
            models_dir = os.path.expanduser("~/.nexa/models")
            os.makedirs(models_dir, exist_ok=True)

            # Save file
            dest_path = os.path.join(models_dir, filename)
            with open(dest_path, 'wb') as f:
                f.write(file_data)

            # Update global state
            with _global_gui_lock:
                chat_id = "A"  # Default to A if not specified
                if hasattr(self, 'headers') and 'Content-Type' in self.headers:
                    # Try to extract chat_id from form data
                    try:
                        # Look for chat_id in the multipart data
                        body_str = body.decode('utf-8', errors='ignore')
                        if 'chat_id' in body_str:
                            if '"B"' in body_str or 'chat_id=B' in body_str:
                                chat_id = "B"
                    except:
                        pass

                _global_models[chat_id] = filename

            # Verify file was saved
            if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(f"Model '{filename}' loaded successfully ({len(file_data)} bytes)".encode('utf-8'))
            else:
                self.send_error(500, "Failed to save model file")

        except Exception as e:
            print(f"Error in handle_load: {e}")
            self.send_error(500, f"Internal server error: {str(e)}")

    def handle_chat(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            message = data.get('message', '').strip()
            chat_id = data.get('chat_id', 'A')

            if not message:
                self.send_error(400, "No message provided")
                return

            with _global_gui_lock:
                model = _global_models.get(chat_id)
                semantic_tags = _global_semantic_tags
                style_tags = _global_style_tags

            if not model:
                response = f"No model loaded for chat {chat_id}. Please load a model first."
                self.send_response(200)
                self.end_headers()
                self.wfile.write(response.encode('utf-8'))
                return

            # Build enhanced prompt with tags
            full_prompt = message
            if semantic_tags.strip():
                full_prompt = f"Semantic context: {semantic_tags}\n\n{full_prompt}"
            if style_tags.strip():
                full_prompt = f"Style guidance: {style_tags}\n\n{full_prompt}"

            try:
                # Run Nexa model
                result = subprocess.run(
                    ['nexa', 'run', model, '-p', full_prompt],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    encoding='utf-8',
                    errors='replace'
                )

                if result.returncode == 0:
                    response = result.stdout.strip()
                    if not response:
                        response = "The model generated an empty response."
                else:
                    response = f"Model execution failed: {result.stderr.strip() or 'Unknown error'}"

            except subprocess.TimeoutExpired:
                response = "Response timeout: The model took too long to respond."
            except FileNotFoundError:
                response = "Error: Nexa CLI not found."
            except Exception as e:
                response = f"Unexpected error: {str(e)}"

            # Ensure response is not empty
            if not response.strip():
                response = "I apologize, but I couldn't generate a meaningful response."

            # Capture the response for comparison
            self.capture_response(chat_id, message, response, semantic_tags, style_tags)

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))

        except Exception as e:
            self.send_error(500, f"Chat error: {str(e)}")

    def handle_capture(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            chat_id = data.get('chat_id')
            message = data.get('message', '')
            response = data.get('response', '')

            if not chat_id or not response:
                self.send_error(400, "Missing chat_id or response")
                return

            with _global_gui_lock:
                semantic_tags = _global_semantic_tags
                style_tags = _global_style_tags

            self.capture_response(chat_id, message, response, semantic_tags, style_tags)

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Response captured")

        except Exception as e:
            self.send_error(500, f"Capture error: {str(e)}")

    def capture_response(self, chat_id, message, response, semantic_tags, style_tags):
        """Capture response for comparison pipeline"""
        global _captured_responses

        # Store response data
        response_data = {
            'timestamp': time.time(),
            'chat_id': chat_id,
            'user_message': message,
            'ai_response': response,
            'semantic_tags': semantic_tags,
            'style_tags': style_tags
        }

        _captured_responses[chat_id] = response_data

        # Note: Automatic comparison removed - use OllamaComparisonNode separately

    def log_message(self, format, *args):
        return

# ---- Server classes ----
class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class LocalGUIServer:
    def __init__(self, host="127.0.0.1", port=None):
        self.host = host
        self.port = port
        self._server = None
        self._thread = None
        self._lock = threading.Lock()
        self._running = False

    def _find_free_port(self):
        if self.port is not None:
            return self.port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, 0))
            return s.getsockname()[1]

    def start(self):
        with self._lock:
            if self._running:
                return
            port = self._find_free_port()
            self.port = port
            self._server = ThreadedHTTPServer((self.host, self.port), LocalGUIRequestHandler)
            def serve():
                try:
                    self._server.serve_forever()
                except Exception:
                    pass
            self._thread = threading.Thread(target=serve, daemon=True)
            self._thread.start()
            self._running = True

    def stop(self):
        with self._lock:
            if not self._running:
                return
            try:
                self._server.shutdown()
                self._server.server_close()
            except Exception:
                pass
            self._server = None
            self._running = False

    def is_running(self):
        """Check if server is running and responsive"""
        if not self._running or not self._server:
            return False
        try:
            # Try to connect to the server
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1.0)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            return result == 0
        except:
            return False

    def url(self):
        if self._running and self.port:
            return f"http://{self.host}:{self.port}"
        return None

    def restart(self):
        # No lock here — stop() and start() each acquire self._lock.
        # Holding the lock here and then calling them would deadlock.
        self.stop()
        time.sleep(0.5)
        self.start()

# ---- Global server ----
_global_gui_server = None

def get_or_create_server(force_restart=False, host="127.0.0.1", port=None):
    global _global_gui_server
    with _global_gui_lock:
        if _global_gui_server is None or force_restart:
            if _global_gui_server is not None:
                _global_gui_server.stop()
            _global_gui_server = LocalGUIServer(host=host, port=port)
            _global_gui_server.start()
        elif _global_gui_server and not _global_gui_server.is_running():
            print("Server not responding, restarting...")
            _global_gui_server.restart()
        return _global_gui_server

def cleanup_server():
    global _global_gui_server
    with _global_gui_lock:
        if _global_gui_server is not None:
            _global_gui_server.stop()
            _global_gui_server = None

atexit.register(cleanup_server)

# ---- ComfyUI node ----
class NexaTagAwarePopupLoaderNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"semantic_tags": ("STRING", {}), "style_tags": ("STRING", {})} }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("url",)
    FUNCTION = "run_gui"
    CATEGORY = "nexa"
    OUTPUT_NODE = False

    def run_gui(self, semantic_tags, style_tags):
        with _global_gui_lock:
            global _global_semantic_tags, _global_style_tags
            _global_semantic_tags = semantic_tags
            _global_style_tags = style_tags

        server = get_or_create_server(force_restart=False)
        url = server.url()

        if url is not None:
            # Give server time to start
            time.sleep(0.5)

            # Try multiple methods to open browser
            opened = False
            try:
                # Try opening new tab first
                webbrowser.open_new_tab(url)
                opened = True
            except Exception as e:
                print(f"Failed to open new tab: {e}")
                try:
                    # Fallback to opening new window
                    webbrowser.open_new(url)
                    opened = True
                except Exception as e2:
                    print(f"Failed to open browser: {e2}")

            if not opened:
                print(f"Could not open browser automatically. Please visit: {url}")

        return (url,)

class NexaComparisonReaderNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {}}

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "FLOAT")
    RETURN_NAMES = ("agreements", "differences", "contradictions", "better_response", "merged_answer", "confidence")
    FUNCTION = "read_latest_comparison"
    CATEGORY = "nexa"
    OUTPUT_NODE = False

    def read_latest_comparison(self):
        """Read the latest comparison result from the JSONL file"""
        try:
            if os.path.exists('comparison_results.jsonl'):
                with open('comparison_results.jsonl', 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        latest_result = json.loads(lines[-1])
                        comparison = latest_result.get('comparison', {})

                        return (
                            comparison.get('agreements', ''),
                            comparison.get('differences', ''),
                            comparison.get('contradictions', ''),
                            comparison.get('better_response', ''),
                            comparison.get('merged_answer', ''),
                            comparison.get('confidence_score', 0.0)
                        )

            # Return defaults if no data
            return ("", "", "", "", "", 0.0)

        except Exception as e:
            print(f"Error reading comparison results: {e}")
            return ("", "", "", "", "", 0.0)