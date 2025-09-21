"""
Vercel-compatible Flask app for iRacing Telemetry Analysis System
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask, render_template_string, jsonify

# Create Flask app
app = Flask(__name__)

# Simple HTML template for Vercel deployment
SIMPLE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>iRacing Telemetry Analysis System</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .feature-card {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .feature-card h3 {
            color: #ffd700;
            margin-top: 0;
        }
        .status {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-top: 20px;
        }
        .warning {
            background: rgba(255,193,7,0.2);
            border: 1px solid #ffc107;
            color: #fff3cd;
        }
        .github-link {
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background: #333;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.3s;
        }
        .github-link:hover {
            background: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏁 iRacing Telemetry Analysis System</h1>
            <p>Professional-grade telemetry analysis for competitive sim racing</p>
        </div>

        <div class="features">
            <div class="feature-card">
                <h3>📊 Advanced Analytics</h3>
                <ul>
                    <li>Real telemetry parsing from IBT files</li>
                    <li>Performance analytics dashboard</li>
                    <li>Interactive charts and visualizations</li>
                    <li>Professional coaching insights</li>
                </ul>
            </div>

            <div class="feature-card">
                <h3>🔧 Setup Optimization</h3>
                <ul>
                    <li>Professional car setup analysis</li>
                    <li>Track-specific recommendations</li>
                    <li>Aerodynamic balance optimization</li>
                    <li>Risk assessment and improvement</li>
                </ul>
            </div>

            <div class="feature-card">
                <h3>🏁 Race Strategy</h3>
                <ul>
                    <li>Fuel consumption modeling</li>
                    <li>Tire wear simulation</li>
                    <li>Pit strategy optimization</li>
                    <li>Alternative strategy generation</li>
                </ul>
            </div>

            <div class="feature-card">
                <h3>📈 Advanced Metrics</h3>
                <ul>
                    <li>G-force analysis (lateral/longitudinal)</li>
                    <li>Cornering speed optimization</li>
                    <li>Braking point analysis</li>
                    <li>Professional benchmarking</li>
                </ul>
            </div>

            <div class="feature-card">
                <h3>👥 Driver Comparison</h3>
                <ul>
                    <li>Multi-driver performance analysis</li>
                    <li>Head-to-head comparisons</li>
                    <li>Driver rankings and insights</li>
                    <li>Specialization identification</li>
                </ul>
            </div>

            <div class="feature-card">
                <h3>🎯 Professional Features</h3>
                <ul>
                    <li>Real-time file monitoring</li>
                    <li>REST API endpoints</li>
                    <li>Professional motorsport algorithms</li>
                    <li>Comprehensive documentation</li>
                </ul>
            </div>
        </div>

        <div class="status warning">
            <h3>⚠️ Deployment Notice</h3>
            <p><strong>This is a demo page for the iRacing Telemetry Analysis System.</strong></p>
            <p>The full application requires local installation with telemetry file access and cannot run fully on Vercel due to:</p>
            <ul style="text-align: left; max-width: 600px; margin: 0 auto;">
                <li>Need for local IBT file processing</li>
                <li>File system access requirements</li>
                <li>Large telemetry data processing</li>
                <li>Real-time file monitoring capabilities</li>
            </ul>
            <p><strong>For full functionality, please install locally following the GitHub instructions.</strong></p>
        </div>

        <div style="text-align: center;">
            <a href="https://github.com/wallgig/iracing-telemetry-analysis" class="github-link">
                📖 View on GitHub & Installation Instructions
            </a>
        </div>

        <div class="status">
            <h3>🚀 Local Installation</h3>
            <p>To use the full system locally:</p>
            <pre style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 5px; text-align: left; max-width: 500px; margin: 0 auto;">
git clone https://github.com/wallgig/iracing-telemetry-analysis.git
cd iracing-telemetry-analysis
pip install -r requirements.txt
cd src
python enhanced_web_ui.py</pre>
            <p>Then open <code>http://localhost:5000</code> in your browser</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    """Landing page explaining the system"""
    return render_template_string(SIMPLE_TEMPLATE)

@app.route('/api/status')
def api_status():
    """Simple API status endpoint"""
    return jsonify({
        'status': 'online',
        'message': 'iRacing Telemetry Analysis System API',
        'deployment': 'vercel',
        'note': 'Full functionality requires local installation',
        'github': 'https://github.com/wallgig/iracing-telemetry-analysis'
    })

@app.route('/api/features')
def api_features():
    """List available features"""
    return jsonify({
        'features': [
            'Real telemetry parsing from IBT files',
            'Performance analytics dashboard',
            'Interactive charts and visualizations',
            'Professional car setup optimization',
            'Race strategy planning',
            'Multi-driver comparison',
            'Advanced G-force and cornering analysis',
            'Professional coaching insights'
        ],
        'note': 'These features require local installation with telemetry files'
    })

if __name__ == '__main__':
    app.run(debug=True)