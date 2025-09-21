"""
Simple web-based UI for the iRacing Telemetry Coach
"""

import sys
import json
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from telemetry_processor import TelemetryProcessor
from ai_coach import DriveCoach

app = Flask(__name__)

# Initialize components
processor = TelemetryProcessor()
coach = DriveCoach("../data/processed_sessions")

# Global state
system_stats = {"initialized": False, "sessions": 0}


def initialize_system():
    """Initialize the system by processing existing files"""
    global system_stats

    if system_stats["initialized"]:
        return

    # Find and process existing IBT files
    telemetry_dir = Path(__file__).parent.parent
    ibt_files = list(telemetry_dir.glob("*.ibt"))

    processed_count = 0
    for ibt_file in ibt_files:
        try:
            processed_data = processor.process_telemetry_file(str(ibt_file))
            if processed_data:
                coach.add_session(processed_data)
                processed_count += 1
        except Exception as e:
            print(f"Error processing {ibt_file}: {e}")

    system_stats["initialized"] = True
    system_stats["sessions"] = processed_count


@app.route('/')
def index():
    """Main page"""
    initialize_system()
    stats = coach.get_summary_stats()
    return render_template('index.html', stats=stats, system_stats=system_stats)


@app.route('/api/ask', methods=['POST'])
def ask_question():
    """API endpoint for asking questions"""
    try:
        data = request.get_json()
        question = data.get('question', '')

        if not question:
            return jsonify({'error': 'No question provided'}), 400

        # Get answer from coach
        answer = coach.answer_question(question)

        return jsonify({
            'question': question,
            'answer': answer,
            'success': True
        })

    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    try:
        stats = coach.get_summary_stats()
        return jsonify({
            'stats': stats,
            'system_stats': system_stats,
            'success': True
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/process_files', methods=['POST'])
def process_files():
    """Process any new IBT files"""
    try:
        telemetry_dir = Path(__file__).parent.parent
        ibt_files = list(telemetry_dir.glob("*.ibt"))

        processed_count = 0
        processed_files = []

        for ibt_file in ibt_files:
            try:
                processed_data = processor.process_telemetry_file(str(ibt_file))
                if processed_data:
                    session_id = coach.add_session(processed_data)
                    processed_count += 1
                    processed_files.append({
                        'filename': ibt_file.name,
                        'session_id': session_id,
                        'track': processed_data.get('session_info', {}).get('track', 'Unknown'),
                        'car': processed_data.get('session_info', {}).get('car', 'Unknown')
                    })
            except Exception as e:
                print(f"Error processing {ibt_file}: {e}")

        system_stats["sessions"] = len(coach.sessions)

        return jsonify({
            'processed_count': processed_count,
            'processed_files': processed_files,
            'success': True
        })

    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)

    print("Starting iRacing Telemetry Coach Web UI...")
    print("Open your browser to: http://localhost:5000")

    app.run(debug=True, host='0.0.0.0', port=5000)