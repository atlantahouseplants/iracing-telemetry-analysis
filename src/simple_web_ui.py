"""
Simple web-based UI for the iRacing Telemetry Coach (Fixed Version)
"""

import sys
import json
import os
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

app = Flask(__name__)

# Initialize components at startup
print("Initializing telemetry coach...")
try:
    from telemetry_processor import TelemetryProcessor
    from ai_coach import DriveCoach

    processor = TelemetryProcessor()
    coach = DriveCoach("../data/processed_sessions")

    # Process existing files on startup
    telemetry_dir = Path(__file__).parent.parent
    ibt_files = list(telemetry_dir.glob("*.ibt"))

    print(f"Found {len(ibt_files)} IBT files to process...")

    for ibt_file in ibt_files:
        try:
            print(f"Processing: {ibt_file.name}")
            processed_data = processor.process_telemetry_file(str(ibt_file))
            if processed_data:
                coach.add_session(processed_data)
                print(f"  + Added session")
            else:
                print(f"  - Failed to process")
        except Exception as e:
            print(f"  - Error: {e}")

    stats = coach.get_summary_stats()
    print(f"Initialization complete! {stats}")

except Exception as e:
    print(f"Error during initialization: {e}")
    # Create dummy objects so the app doesn't crash
    class DummyCoach:
        def answer_question(self, q):
            return f"Error: System not properly initialized. {e}"
        def get_summary_stats(self):
            return {"message": f"System error: {e}"}

    coach = DummyCoach()

# HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>iRacing AI Telemetry Coach</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .stats {
            background: white;
            color: black;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .chat-container {
            background: white;
            color: black;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .chat-header {
            background: #667eea;
            color: white;
            padding: 20px;
            text-align: center;
        }

        .chat-messages {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }

        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 5px;
        }

        .user-message {
            background: #e3f2fd;
            text-align: right;
        }

        .coach-message {
            background: #f1f8e9;
        }

        .chat-input {
            padding: 20px;
            background: white;
            display: flex;
            gap: 10px;
        }

        .chat-input input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }

        .chat-input button {
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        .example-questions {
            background: white;
            color: black;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .question-btn {
            display: inline-block;
            margin: 5px;
            padding: 8px 15px;
            background: #f0f4ff;
            border: 1px solid #667eea;
            border-radius: 15px;
            color: #667eea;
            cursor: pointer;
            font-size: 14px;
        }

        .question-btn:hover {
            background: #667eea;
            color: white;
        }

        .error {
            color: red;
            font-weight: bold;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 10px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏎️ iRacing AI Telemetry Coach</h1>
        <p>Ask me anything about your racing performance</p>
    </div>

    <div class="stats">
        <h3>📊 Your Statistics</h3>
        <div id="stats-content">
            {{ stats_html | safe }}
        </div>
    </div>

    <div class="example-questions">
        <h3>Try asking me:</h3>
        <div class="question-btn" onclick="askQuestion('What\\'s my fastest lap time?')">What's my fastest lap time?</div>
        <div class="question-btn" onclick="askQuestion('How can I improve at Road Atlanta?')">How can I improve at Road Atlanta?</div>
        <div class="question-btn" onclick="askQuestion('How consistent am I?')">How consistent am I?</div>
        <div class="question-btn" onclick="askQuestion('What tracks have I driven?')">What tracks have I driven?</div>
    </div>

    <div class="chat-container">
        <div class="chat-header">
            <h2>💬 Chat with Your AI Coach</h2>
        </div>
        <div class="chat-messages" id="chat-messages">
            <div class="message coach-message">
                <strong>🤖 AI Coach:</strong> Hello! I'm ready to help you improve your racing. Ask me anything!
            </div>
        </div>
        <div class="loading" id="loading">🤔 Thinking...</div>
        <div class="chat-input">
            <input type="text" id="question-input" placeholder="Ask me about your racing..." onkeypress="handleKeyPress(event)">
            <button onclick="sendQuestion()" id="send-btn">Send</button>
        </div>
    </div>

    <script>
        function askQuestion(question) {
            document.getElementById('question-input').value = question;
            sendQuestion();
        }

        async function sendQuestion() {
            const input = document.getElementById('question-input');
            const question = input.value.trim();

            if (!question) {
                alert('Please enter a question!');
                return;
            }

            console.log('Sending question:', question);

            // Add user message
            addMessage('👤 You: ' + question, 'user-message');

            // Clear input and show loading
            input.value = '';
            document.getElementById('loading').style.display = 'block';
            document.getElementById('send-btn').disabled = true;

            try {
                const response = await fetch('/api/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question: question })
                });

                console.log('Response status:', response.status);

                if (!response.ok) {
                    throw new Error('Network response was not ok: ' + response.status);
                }

                const data = await response.json();
                console.log('Response data:', data);

                if (data.success) {
                    addMessage('🤖 AI Coach: ' + data.answer, 'coach-message');
                } else {
                    addMessage('🤖 AI Coach: Sorry, I encountered an error: ' + data.error, 'coach-message error');
                }
            } catch (error) {
                console.error('Error:', error);
                addMessage('🤖 AI Coach: Sorry, I couldn\\'t process your question. Error: ' + error.message, 'coach-message error');
            }

            // Hide loading and re-enable button
            document.getElementById('loading').style.display = 'none';
            document.getElementById('send-btn').disabled = false;
            input.focus();
        }

        function addMessage(text, className) {
            const messagesContainer = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + className;
            messageDiv.innerHTML = text;
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendQuestion();
            }
        }

        // Test the API connection on page load
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                console.log('Stats loaded:', data);
            })
            .catch(error => {
                console.error('Error loading stats:', error);
                addMessage('🤖 AI Coach: Warning - there may be connection issues. If questions don\\'t work, please restart the application.', 'coach-message error');
            });

        // Auto-focus on input
        document.getElementById('question-input').focus();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Main page"""
    try:
        stats = coach.get_summary_stats()

        # Format stats for display
        if 'message' in stats:
            stats_html = f"<p class='error'>{stats['message']}</p>"
        else:
            stats_html = f"""
            <p><strong>Sessions:</strong> {stats.get('total_sessions', 0)}</p>
            <p><strong>Tracks:</strong> {', '.join(stats.get('tracks', {}).keys()) if stats.get('tracks') else 'None'}</p>
            <p><strong>Cars:</strong> {', '.join(stats.get('cars', {}).keys()) if stats.get('cars') else 'None'}</p>
            <p><strong>Best Lap:</strong> {stats.get('best_lap_time', 'N/A')}</p>
            """

        return render_template_string(HTML_TEMPLATE, stats_html=stats_html)
    except Exception as e:
        error_html = f"<p class='error'>Error loading stats: {e}</p>"
        return render_template_string(HTML_TEMPLATE, stats_html=error_html)

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """API endpoint for asking questions"""
    try:
        print("Received ask request")
        data = request.get_json()
        question = data.get('question', '')

        print(f"Question: {question}")

        if not question:
            return jsonify({'error': 'No question provided', 'success': False}), 400

        # Get answer from coach
        answer = coach.answer_question(question)
        print(f"Answer: {answer[:100]}...")

        return jsonify({
            'question': question,
            'answer': answer,
            'success': True
        })

    except Exception as e:
        print(f"Error in ask_question: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    try:
        stats = coach.get_summary_stats()
        return jsonify({'stats': stats, 'success': True})
    except Exception as e:
        print(f"Error in get_stats: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

if __name__ == '__main__':
    print("\\n" + "="*50)
    print("   iRacing Telemetry Coach Web UI")
    print("="*50)
    print("Starting server...")
    print("Open your browser to: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("="*50)

    app.run(debug=True, host='0.0.0.0', port=5000)