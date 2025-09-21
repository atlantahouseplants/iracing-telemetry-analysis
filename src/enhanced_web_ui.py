"""
Enhanced web UI using real telemetry parsing
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
print("Initializing Enhanced iRacing Telemetry Coach...")
try:
    from enhanced_telemetry_processor import EnhancedTelemetryProcessor
    from ai_coach_enhanced import EnhancedDriveCoach
    from file_monitor import TelemetryFileMonitor
    from performance_analytics import PerformanceAnalytics
    from setup_optimizer import SetupOptimizer
    from race_strategist import RaceStrategist
    from driver_comparator import DriverComparator
    from advanced_metrics import AdvancedMetrics

    processor = EnhancedTelemetryProcessor()
    coach = EnhancedDriveCoach("../data/processed_sessions")
    analytics_engine = PerformanceAnalytics(coach)
    setup_optimizer = SetupOptimizer(coach)
    race_strategist = RaceStrategist(coach)
    driver_comparator = DriverComparator(coach)
    advanced_metrics = AdvancedMetrics(coach)

    # Initialize file monitoring
    telemetry_dir = Path(__file__).parent.parent
    file_monitor = TelemetryFileMonitor(processor, coach, [telemetry_dir])

    # Auto-start monitoring
    file_monitor.start_monitoring()
    print(f"+ File monitoring active on: {telemetry_dir}")

    # Process existing files on startup
    telemetry_dir = Path(__file__).parent.parent
    ibt_files = list(telemetry_dir.glob("*.ibt"))

    print(f"Found {len(ibt_files)} IBT files to process with enhanced parser...")

    for ibt_file in ibt_files:
        try:
            print(f"Processing: {ibt_file.name}")
            processed_data = processor.process_telemetry_file(str(ibt_file))
            if processed_data:
                coach.add_session(processed_data)
                print(f"  + Added session with real telemetry data")

                # Show enhanced info
                session_info = processed_data.get('session_info', {})
                lap_analysis = processed_data.get('lap_analysis', {})
                print(f"  Track: {session_info.get('track')} | Car: {session_info.get('car')}")
                print(f"  Laps: {lap_analysis.get('total_laps')} | Fastest: {lap_analysis.get('fastest_lap', 'N/A')}")
                print(f"  Consistency: {lap_analysis.get('consistency_rating', 'N/A')}/10")
            else:
                print(f"  - Failed to process")
        except Exception as e:
            print(f"  - Error: {e}")

    stats = coach.get_summary_stats()
    print(f"Enhanced initialization complete! {stats}")

except Exception as e:
    print(f"Error during initialization: {e}")
    # Create dummy objects so the app doesn't crash
    class DummyCoach:
        def answer_question(self, q):
            return f"Error: Enhanced system not properly initialized. {e}"
        def get_summary_stats(self):
            return {"message": f"System error: {e}"}

    class DummyMonitor:
        def get_monitoring_status(self):
            return {"is_monitoring": False, "error": str(e)}

    class DummyAnalytics:
        def generate_dashboard_data(self):
            return {"error": True, "message": str(e)}

    class DummySetupOptimizer:
        def analyze_setup_performance(self, car, track):
            return {"error": True, "message": str(e)}

    class DummyRaceStrategist:
        def analyze_race_strategy(self, car, track, race_length, tire_compound="medium", weather="dry"):
            return {"error": True, "message": str(e)}

    coach = DummyCoach()
    file_monitor = DummyMonitor()
    analytics_engine = DummyAnalytics()
    setup_optimizer = DummySetupOptimizer()
    race_strategist = DummyRaceStrategist()

# Enhanced HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced iRacing AI Telemetry Coach</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1400px;
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

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .header .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }

        .enhanced-badge {
            background: #ff6b6b;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
            margin-left: 10px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: white;
            color: black;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-card h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.1em;
        }

        .stat-value {
            font-size: 2.2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }

        .stat-label {
            color: #666;
            font-size: 0.9em;
        }

        .quality-indicator {
            background: #4caf50;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.7em;
            margin-top: 5px;
        }

        .catalog-section {
            background: rgba(255, 255, 255, 0.12);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            backdrop-filter: blur(6px);
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.25);
        }

        .catalog-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 15px;
        }

        .catalog-header h2 {
            margin: 0;
            font-size: 1.6em;
        }

        .catalog-subtitle {
            font-size: 0.95em;
            opacity: 0.85;
        }

        .catalog-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 20px;
        }

        .catalog-meta .meta-item {
            background: rgba(255, 255, 255, 0.15);
            padding: 10px 15px;
            border-radius: 10px;
            min-width: 150px;
        }

        .catalog-meta .meta-label {
            display: block;
            font-size: 0.75em;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            opacity: 0.8;
        }

        .catalog-meta .meta-value {
            font-size: 1.3em;
            font-weight: 600;
        }

        .catalog-refresh {
            padding: 10px 18px;
            border-radius: 10px;
            border: none;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            cursor: pointer;
            transition: background 0.2s ease;
        }

        .catalog-refresh:hover {
            background: rgba(255, 255, 255, 0.35);
        }

        .catalog-filters {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: flex-end;
            margin-bottom: 20px;
        }

        .catalog-filters label {
            display: flex;
            flex-direction: column;
            font-size: 0.8em;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .catalog-filters select {
            margin-top: 4px;
            padding: 8px 12px;
            border-radius: 10px;
            border: none;
            background: rgba(255, 255, 255, 0.9);
            color: #333;
            min-width: 160px;
        }

        .catalog-reset-btn {
            padding: 10px 18px;
            border-radius: 10px;
            border: none;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            cursor: pointer;
            transition: background 0.2s ease;
        }

        .catalog-reset-btn:hover {
            background: rgba(255, 255, 255, 0.35);
        }

        .catalog-reset-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .catalog-table-wrapper {
            overflow-x: auto;
        }

        .catalog-table {
            width: 100%;
            border-collapse: collapse;
            color: white;
        }

        .catalog-table th,
        .catalog-table td {
            padding: 10px 12px;
            text-align: left;
        }

        .catalog-table thead {
            background: rgba(255, 255, 255, 0.2);
        }

        .catalog-table tbody tr:nth-child(even) {
            background: rgba(255, 255, 255, 0.05);
        }

        .catalog-table .empty-row td {
            text-align: center;
            opacity: 0.7;
            padding: 20px 12px;
        }

        @media (max-width: 768px) {
            .catalog-meta {
                flex-direction: column;
                align-items: stretch;
            }
            .catalog-filters {
                flex-direction: column;
                align-items: stretch;
            }
            .catalog-filters select, .catalog-reset-btn {
                width: 100%;
            }
        }

        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }

        .chat-section {
            background: white;
            color: black;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }

        .chat-header {
            background: linear-gradient(135deg, #667eea, #5a67d8);
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
            padding: 12px;
            border-radius: 10px;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .user-message {
            background: #e3f2fd;
            text-align: right;
            margin-left: 20%;
        }

        .coach-message {
            background: #f1f8e9;
            margin-right: 20%;
        }

        .enhanced-insights {
            background: white;
            color: black;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }

        .insights-header {
            background: linear-gradient(135deg, #ff6b6b, #ff5252);
            color: white;
            margin: -20px -20px 20px -20px;
            padding: 20px;
            border-radius: 15px 15px 0 0;
        }

        .insight-category {
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }

        .insight-category h4 {
            margin: 0 0 10px 0;
            color: #667eea;
        }

        .insight-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .insight-list li {
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }

        .insight-list li:last-child {
            border-bottom: none;
        }

        .example-questions {
            background: white;
            color: black;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }

        .question-btn {
            display: inline-block;
            margin: 8px;
            padding: 12px 18px;
            background: linear-gradient(135deg, #f0f4ff, #e8f0ff);
            border: 2px solid #667eea;
            border-radius: 25px;
            color: #667eea;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9em;
            font-weight: 500;
        }

        .question-btn:hover {
            background: linear-gradient(135deg, #667eea, #5a67d8);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        .chat-input {
            padding: 20px;
            background: white;
            display: flex;
            gap: 10px;
        }

        .chat-input input {
            flex: 1;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 25px;
            font-size: 1em;
            outline: none;
            transition: border-color 0.3s ease;
        }

        .chat-input input:focus {
            border-color: #667eea;
        }

        .chat-input button {
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea, #5a67d8);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .chat-input button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        .loading {
            display: none;
            text-align: center;
            padding: 15px;
            color: #666;
            font-style: italic;
        }

        @media (max-width: 1024px) {
            .main-content {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 768px) {
            body {
                padding: 10px;
            }

            .header h1 {
                font-size: 2em;
            }

            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
        .chart-container {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .chart-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }

        .chart-full-width {
            grid-column: 1 / -1;
        }

        .chart-title {
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
            color: #fff;
        }

        canvas {
            max-height: 400px;
        }

        @media (max-width: 768px) {
            .chart-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="header">
        <h1>Enhanced iRacing AI Coach<span class="enhanced-badge">REAL DATA</span></h1>
        <p class="subtitle">Advanced telemetry analysis with realistic lap times and insights</p>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <h3>Sessions Analyzed</h3>
            <div class="stat-value" id="session-count">
                {% if stats.get('total_sessions') %}{{ stats.total_sessions }}{% else %}0{% endif %}
            </div>
            <div class="stat-label">Total Sessions</div>
            <div class="quality-indicator">Real Telemetry</div>
        </div>
        <div class="stat-card">
            <h3>Tracks Mastered</h3>
            <div class="stat-value" id="track-count">
                {% if stats.get('tracks') %}{{ stats.tracks|length }}{% else %}0{% endif %}
            </div>
            <div class="stat-label">Different Tracks</div>
        </div>
        <div class="stat-card">
            <h3> Cars Driven</h3>
            <div class="stat-value" id="car-count">
                {% if stats.get('cars') %}{{ stats.cars|length }}{% else %}0{% endif %}
            </div>
            <div class="stat-label">Different Cars</div>
        </div>
        <div class="stat-card">
            <h3> Personal Best</h3>
            <div class="stat-value" id="best-lap">
                {% if stats.get('best_lap_time') %}{{ "%.3f"|format(stats.best_lap_time) }}s{% else %}--{% endif %}
            </div>
            <div class="stat-label">Fastest Lap</div>
        </div>
    </div>

    <div class="example-questions">
        <h3> Enhanced Analysis Questions:</h3>
        <div class="question-btn" onclick="askQuestion('What\\'s my fastest lap time and how can I improve it?')">Lap Time Analysis</div>
        <div class="question-btn" onclick="askQuestion('How consistent am I and where should I focus?')">Consistency Analysis</div>
        <div class="question-btn" onclick="askQuestion('What are my strengths at Road Atlanta?')">Track Performance</div>
        <div class="question-btn" onclick="askQuestion('How does my Porsche performance compare to Toyota?')">Car Comparison</div>
        <div class="question-btn" onclick="askQuestion('What should I practice in my next session?')">Practice Plan</div>
        <div class="question-btn" onclick="loadProfessionalAnalysis()" style="background: linear-gradient(135deg, #ff6b6b, #ff5252); color: white;">Professional Analysis</div>
        <div class="question-btn" onclick="loadAnalyticsDashboard()" style="background: linear-gradient(135deg, #4caf50, #45a049); color: white;">Analytics Dashboard</div>
        <div class="question-btn" onclick="toggleCharts()" style="background: linear-gradient(135deg, #9c27b0, #8e24aa); color: white;">Interactive Charts</div>
        <div class="question-btn" onclick="loadSetupOptimizer()" style="background: linear-gradient(135deg, #ff9800, #f57c00); color: white;">Setup Optimizer</div>
        <div class="question-btn" onclick="loadRaceStrategy()" style="background: linear-gradient(135deg, #2196f3, #1976d2); color: white;">Race Strategy</div>
        <div class="question-btn" onclick="loadDriverComparison()" style="background: linear-gradient(135deg, #e91e63, #c2185b); color: white;">Driver Comparison</div>
        <div class="question-btn" onclick="loadAdvancedMetrics()" style="background: linear-gradient(135deg, #795548, #5d4037); color: white;">Advanced Metrics</div>
    </div>

<div class="catalog-section">
    <div class="catalog-header">
        <div>
            <h2>Session Catalog</h2>
            <p class="catalog-subtitle">Latest processed telemetry sessions</p>
        </div>
        <button class="catalog-refresh" id="catalog-refresh-btn" type="button">Refresh</button>
    </div>
    <div class="catalog-meta">
        <div class="meta-item">
            <span class="meta-label">Total Sessions</span>
            <span class="meta-value" id="catalog-total-sessions">0</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">Tracks</span>
            <span class="meta-value" id="catalog-track-count">0</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">Cars</span>
            <span class="meta-value" id="catalog-car-count">0</span>
        </div>
        <div class="meta-item">
            <span class="meta-label">Best Lap</span>
            <span class="meta-value" id="catalog-best-lap">--</span>
        </div>
    </div>
    <div class="catalog-filters">
        <label>Track
            <select id="catalog-track-filter">
                <option value="">All Tracks</option>
            </select>
        </label>
        <label>Car
            <select id="catalog-car-filter">
                <option value="">All Cars</option>
            </select>
        </label>
        <button class="catalog-reset-btn" id="catalog-reset-btn" type="button" disabled>Reset Filters</button>
    </div>
    <div class="catalog-table-wrapper">
        <table class="catalog-table">
            <thead>
                <tr>
                    <th>When</th>
                    <th>Track</th>
                    <th>Car</th>
                    <th>Laps</th>
                    <th>Fastest Lap</th>
                    <th>Average Lap</th>
                    <th>Consistency</th>
                </tr>
            </thead>
            <tbody id="catalog-table-body">
                <tr class="empty-row">
                    <td colspan="7">No sessions cataloged yet. Process telemetry to see history here.</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>

    <div class="main-content">
        <div class="chat-section">
            <div class="chat-header">
                <h2> AI Coach Chat</h2>
                <p>Ask detailed questions about your performance</p>
            </div>
            <div class="chat-messages" id="chat-messages">
                <div class="message coach-message">
                    <strong> Enhanced AI Coach:</strong> Hello! I've analyzed your telemetry with realistic lap times and detailed insights. I can now provide much more accurate coaching based on your actual driving data. What would you like to know?
                </div>
            </div>
            <div class="loading" id="loading"> Analyzing your telemetry data...</div>
            <div class="chat-input">
                <input type="text" id="question-input" placeholder="Ask about your driving performance..." onkeypress="handleKeyPress(event)">
                <button onclick="sendQuestion()" id="send-btn">Analyze</button>
            </div>
        </div>

        <div class="enhanced-insights">
            <div class="insights-header">
                <h2> Real-Time Insights</h2>
                <p>Based on your actual telemetry data</p>
            </div>

            <div class="insight-category">
                <h4> Performance Highlights</h4>
                <ul class="insight-list" id="performance-insights">
                    <li>Enhanced telemetry parsing active</li>
                    <li>Realistic lap time analysis available</li>
                    <li>Track-specific insights generated</li>
                </ul>
            </div>

            <div class="insight-category">
                <h4> Focus Areas</h4>
                <ul class="insight-list" id="focus-insights">
                    <li>Consistency development opportunities</li>
                    <li>Track-specific improvement areas</li>
                    <li>Car-specific optimization tips</li>
                </ul>
            </div>

            <div class="insight-category">
                <h4> Data Quality</h4>
                <ul class="insight-list" id="quality-insights">
                    <li> Real telemetry file analysis</li>
                    <li> Accurate lap time extraction</li>
                    <li> Enhanced coaching algorithms</li>
                </ul>
            </div>

            <div class="insight-category">
                <h4> File Monitoring</h4>
                <ul class="insight-list" id="monitoring-insights">
                    <li id="monitoring-status">Loading monitoring status...</li>
                    <li id="files-processed">Files processed: 0</li>
                    <li id="last-processed">Last file: None</li>
                </ul>
            </div>
        </div>
    </div>

    <!-- Interactive Charts Section -->
    <div class="chart-grid" id="charts-section" style="display: none;">
        <div class="chart-container chart-full-width">
            <div class="chart-title">Performance Trends Over Time</div>
            <canvas id="performanceChart"></canvas>
        </div>

        <div class="chart-container">
            <div class="chart-title">Lap Time Distribution</div>
            <canvas id="lapTimeChart"></canvas>
        </div>

        <div class="chart-container">
            <div class="chart-title">Consistency by Track</div>
            <canvas id="consistencyChart"></canvas>
        </div>

        <div class="chart-container">
            <div class="chart-title">Track Performance Comparison</div>
            <canvas id="trackChart"></canvas>
        </div>

        <div class="chart-container">
            <div class="chart-title">Car Performance Analysis</div>
            <canvas id="carChart"></canvas>
        </div>

        <div class="chart-container chart-full-width">
            <div class="chart-title">Session Timeline</div>
            <canvas id="timelineChart"></canvas>
        </div>
    </div>

    <script>
const CATALOG_STORAGE_KEY = 'enhancedTelemetryCatalogFilters';
const CATALOG_PAGE_LIMIT = 50;
let currentTrackFilter = '';
let currentCarFilter = '';

function normalizeFilterValue(value) {
    if (typeof value !== 'string') {
        return '';
    }
    const trimmed = value.trim();
    if (!trimmed) {
        return '';
    }
    const lower = trimmed.toLowerCase();
    if (lower === 'all tracks' || lower === 'all cars' || lower === 'all') {
        return '';
    }
    return trimmed;
}

function buildFilterQueryParams(initial = {}) {
    const params = new URLSearchParams(initial);
    const track = normalizeFilterValue(currentTrackFilter);
    const car = normalizeFilterValue(currentCarFilter);
    if (track) {
        params.append('track', track);
    }
    if (car) {
        params.append('car', car);
    }
    return params;
}

function loadStoredFilters() {
    if (typeof window === 'undefined' || !window.localStorage) {
        return { track: '', car: '' };
    }
    try {
        const raw = window.localStorage.getItem(CATALOG_STORAGE_KEY);
        if (!raw) {
            return { track: '', car: '' };
        }
        const parsed = JSON.parse(raw);
        return {
            track: normalizeFilterValue(parsed.track),
            car: normalizeFilterValue(parsed.car)
        };
    } catch (error) {
        console.warn('Unable to read stored catalog filters', error);
        return { track: '', car: '' };
    }
}

function storeFilters(track, car) {
    if (typeof window === 'undefined' || !window.localStorage) {
        return;
    }
    try {
        window.localStorage.setItem(
            CATALOG_STORAGE_KEY,
            JSON.stringify({
                track: normalizeFilterValue(track),
                car: normalizeFilterValue(car)
            })
        );
    } catch (error) {
        console.warn('Unable to persist catalog filters', error);
    }
}

function persistCurrentFilters() {
    storeFilters(currentTrackFilter, currentCarFilter);
}

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

            console.log('Sending enhanced question:', question);

            // Add user message
            addMessage(' <strong>You:</strong> ' + question, 'user-message');

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

                console.log('Enhanced response status:', response.status);

                if (!response.ok) {
                    throw new Error('Network response was not ok: ' + response.status);
                }

                const data = await response.json();
                console.log('Enhanced response data:', data);

                if (data.success) {
                    addMessage(' <strong>Enhanced AI Coach:</strong> ' + data.answer, 'coach-message');
                } else {
                    addMessage(' <strong>AI Coach:</strong> Sorry, I encountered an error: ' + data.error, 'coach-message');
                }
            } catch (error) {
                console.error('Enhanced error:', error);
                addMessage(' <strong>AI Coach:</strong> Sorry, I couldn\\'t process your question. Error: ' + error.message, 'coach-message');
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

        // Auto-focus on input
        document.getElementById('question-input').focus();

        // Show enhanced startup message
        setTimeout(() => {
            addMessage(' <strong>Enhanced AI Coach:</strong> System ready with real telemetry analysis! Try asking: "How consistent am I?" or "What should I practice next?"', 'coach-message');
            updateMonitoringStatus();
        }, 1000);

        // Update monitoring status periodically
        setInterval(updateMonitoringStatus, 30000); // Every 30 seconds

        // Professional Analysis function
        async function loadProfessionalAnalysis() {
            console.log('Loading professional analysis...');

            // Add loading message
            addMessage('<strong>Professional Analysis:</strong> Loading Cosworth Pi Toolbox-style analysis...', 'coach-message');

            try {
                const response = await fetch('/api/professional-analysis');
                console.log('Professional analysis response status:', response.status);

                if (!response.ok) {
                    throw new Error('Professional analysis not available: ' + response.status);
                }

                const data = await response.json();
                console.log('Professional analysis data:', data);

                if (data.success) {
                    const analysis = data.analysis;

                    // Format professional analysis response
                    let analysisText = '<strong>PROFESSIONAL TELEMETRY ANALYSIS</strong><br><br>';

                    // Session Overview
                    if (analysis.session_overview) {
                        const overview = analysis.session_overview;
                        analysisText += `<strong>SESSION OVERVIEW:</strong><br>`;
                        analysisText += `Track: ${overview.track} | Vehicle: ${overview.vehicle}<br>`;
                        analysisText += `Laps: ${overview.total_laps} | Duration: ${overview.session_duration_estimate}<br>`;
                        analysisText += `Data Quality: ${overview.telemetry_quality}<br><br>`;
                    }

                    // Performance Metrics
                    if (analysis.performance_metrics) {
                        const perf = analysis.performance_metrics;
                        analysisText += `<strong>PERFORMANCE METRICS:</strong><br>`;
                        analysisText += `Fastest Lap: ${perf.fastest_lap?.toFixed(3)}s<br>`;
                        analysisText += `Theoretical Best: ${perf.theoretical_best?.toFixed(3)}s<br>`;
                        analysisText += `Consistency Coefficient: ${(perf.consistency_coefficient * 100)?.toFixed(1)}%<br>`;
                        analysisText += `Performance Level: ${perf.performance_percentiles ? 'P95: ' + perf.performance_percentiles.p95?.toFixed(3) + 's' : 'N/A'}<br><br>`;
                    }

                    // Professional Insights
                    if (analysis.professional_insights) {
                        const insights = analysis.professional_insights;
                        analysisText += `<strong>PROFESSIONAL INSIGHTS:</strong><br>`;
                        analysisText += `${insights.performance_summary}<br><br>`;

                        if (insights.strategic_recommendations) {
                            analysisText += `<strong>RECOMMENDATIONS:</strong><br>`;
                            insights.strategic_recommendations.forEach((rec, i) => {
                                analysisText += `${i + 1}. ${rec}<br>`;
                            });
                            analysisText += `<br>`;
                        }
                    }

                    // Improvement Opportunities
                    if (analysis.improvement_opportunities) {
                        const opps = analysis.improvement_opportunities;
                        analysisText += `<strong>IMPROVEMENT OPPORTUNITIES:</strong><br>`;
                        analysisText += `Potential Gain: ${opps.total_potential_gain}<br>`;

                        if (opps.priority_ranking && opps.priority_ranking.length > 0) {
                            opps.priority_ranking.slice(0, 3).forEach((opp, i) => {
                                analysisText += `${i + 1}. [${opp.priority}] ${opp.description}<br>`;
                            });
                        }
                    }

                    analysisText += `<br><em>Analysis powered by professional-grade algorithms</em>`;

                    addMessage(analysisText, 'coach-message');
                } else {
                    addMessage('<strong>Professional Analysis:</strong> ' + data.error, 'coach-message');
                }
            } catch (error) {
                console.error('Professional analysis error:', error);
                addMessage('<strong>Professional Analysis:</strong> Analysis not available - ' + error.message, 'coach-message');
            }
        }

        // Monitoring Status function
        async function updateMonitoringStatus() {
            try {
                const response = await fetch('/api/monitoring-status');
                if (response.ok) {
                    const data = await response.json();
                    if (data.success && data.status) {
                        const status = data.status;

                        // Update monitoring status
                        const statusText = status.is_monitoring ? 'Active - Watching for new IBT files' : 'Inactive';
                        document.getElementById('monitoring-status').textContent = statusText;

                        // Update files processed
                        document.getElementById('files-processed').textContent = `Files processed: ${status.files_processed}`;

                        // Update last processed file
                        if (status.last_processed_file) {
                            const lastFile = status.last_processed_file.filename || 'Unknown';
                            document.getElementById('last-processed').textContent = `Last file: ${lastFile}`;
                        } else {
                            document.getElementById('last-processed').textContent = 'Last file: None';
                        }
                    }
                }
            } catch (error) {
                console.error('Error updating monitoring status:', error);
                document.getElementById('monitoring-status').textContent = 'Status check failed';
            }
        }

        // Analytics Dashboard function
        async function loadAnalyticsDashboard() {
            console.log('Loading analytics dashboard...');

            // Add loading message
            addMessage('<strong>Analytics Dashboard:</strong> Generating comprehensive performance analytics...', 'coach-message');

            try {
                const response = await fetch('/api/analytics-dashboard');
                console.log('Analytics dashboard response status:', response.status);

                if (!response.ok) {
                    throw new Error('Analytics dashboard not available: ' + response.status);
                }

                const data = await response.json();
                console.log('Analytics dashboard data:', data);

                if (data.success && data.dashboard) {
                    const dashboard = data.dashboard;

                    // Format comprehensive analytics dashboard
                    let dashboardHTML = '<strong>PERFORMANCE ANALYTICS DASHBOARD</strong><br><br>';

                    // Overview Metrics
                    if (dashboard.overview_metrics && dashboard.overview_metrics.status !== 'no_data') {
                        const metrics = dashboard.overview_metrics;
                        dashboardHTML += '<strong>OVERVIEW METRICS:</strong><br>';
                        dashboardHTML += `Sessions: ${metrics.total_sessions} | Laps: ${metrics.total_laps}<br>`;
                        dashboardHTML += `Tracks: ${metrics.tracks_driven} | Cars: ${metrics.cars_driven}<br>`;
                        if (metrics.fastest_overall) {
                            dashboardHTML += `Personal Best: ${metrics.fastest_overall.toFixed(3)}s<br>`;
                        }
                        if (metrics.average_consistency) {
                            dashboardHTML += `Avg Consistency: ${metrics.average_consistency.toFixed(1)}/10<br>`;
                        }
                        dashboardHTML += '<br>';
                    }

                    // Performance Trends
                    if (dashboard.performance_trends && dashboard.performance_trends.status !== 'insufficient_data') {
                        const trends = dashboard.performance_trends;
                        dashboardHTML += '<strong>PERFORMANCE TRENDS:</strong><br>';
                        if (trends.performance_summary) {
                            const summary = trends.performance_summary;
                            dashboardHTML += `Trend: ${summary.improvement_trend}<br>`;
                            if (summary.lap_time_improvement !== undefined) {
                                const improvement = summary.lap_time_improvement > 0 ? 'declining' : 'improving';
                                dashboardHTML += `Lap Time Trend: ${improvement}<br>`;
                            }
                        }
                        dashboardHTML += '<br>';
                    }

                    // Track Analysis
                    if (dashboard.track_analysis && Object.keys(dashboard.track_analysis).length > 0) {
                        dashboardHTML += '<strong>TRACK PERFORMANCE:</strong><br>';
                        Object.entries(dashboard.track_analysis).forEach(([track, data]) => {
                            dashboardHTML += `${track}: `;
                            if (data.best_lap_time) {
                                dashboardHTML += `${data.best_lap_time.toFixed(3)}s best`;
                            }
                            dashboardHTML += ` (${data.session_count} sessions)<br>`;
                        });
                        dashboardHTML += '<br>';
                    }

                    // Car Comparison
                    if (dashboard.car_comparison && Object.keys(dashboard.car_comparison).length > 0) {
                        dashboardHTML += '<strong>CAR COMPARISON:</strong><br>';
                        Object.entries(dashboard.car_comparison).forEach(([car, data]) => {
                            dashboardHTML += `${car}: `;
                            if (data.best_lap_time) {
                                dashboardHTML += `${data.best_lap_time.toFixed(3)}s best`;
                            }
                            if (data.average_consistency) {
                                dashboardHTML += ` | ${data.average_consistency.toFixed(1)}/10 consistency`;
                            }
                            dashboardHTML += `<br>`;
                        });
                        dashboardHTML += '<br>';
                    }

                    // Professional Insights
                    if (dashboard.professional_insights) {
                        const insights = dashboard.professional_insights;
                        dashboardHTML += '<strong>PROFESSIONAL INSIGHTS:</strong><br>';
                        dashboardHTML += `Performance Rating: ${insights.performance_rating}/10<br>`;

                        if (insights.recommendations && insights.recommendations.length > 0) {
                            dashboardHTML += '<strong>Recommendations:</strong><br>';
                            insights.recommendations.slice(0, 3).forEach((rec, i) => {
                                dashboardHTML += `${i + 1}. ${rec}<br>`;
                            });
                        }
                        dashboardHTML += '<br>';
                    }

                    // Lap Time Comparison
                    if (dashboard.lap_time_comparison && dashboard.lap_time_comparison.statistical_analysis) {
                        const lapComp = dashboard.lap_time_comparison;
                        dashboardHTML += '<strong>LAP TIME ANALYSIS:</strong><br>';

                        // Statistical overview
                        if (lapComp.statistical_analysis) {
                            const stats = lapComp.statistical_analysis;
                            if (stats.overall_best_lap) {
                                dashboardHTML += `Overall Best: ${stats.overall_best_lap.toFixed(3)}s<br>`;
                            }
                            if (stats.average_best_lap) {
                                dashboardHTML += `Average Best: ${stats.average_best_lap.toFixed(3)}s<br>`;
                            }
                            if (stats.improvement_trend !== undefined) {
                                const trend = stats.improvement_trend < 0 ? 'Improving' : stats.improvement_trend > 0 ? 'Declining' : 'Stable';
                                dashboardHTML += `Trend: ${trend}<br>`;
                            }
                        }

                        // Track bests
                        if (lapComp.track_best_times && Object.keys(lapComp.track_best_times).length > 0) {
                            dashboardHTML += '<strong>Track Records:</strong><br>';
                            Object.entries(lapComp.track_best_times).slice(0, 3).forEach(([track, data]) => {
                                dashboardHTML += `${track}: ${data.best_time.toFixed(3)}s<br>`;
                            });
                        }

                        dashboardHTML += '<br>';
                    }

                    // Trend Analysis
                    if (dashboard.trend_analysis && dashboard.trend_analysis.trend_summary) {
                        const trendAnalysis = dashboard.trend_analysis;
                        dashboardHTML += '<strong>TREND ANALYSIS:</strong><br>';

                        // Overall trend summary
                        if (trendAnalysis.trend_summary) {
                            const summary = trendAnalysis.trend_summary;
                            dashboardHTML += `Direction: ${summary.overall_direction}<br>`;
                            dashboardHTML += `Confidence: ${summary.confidence_rating}/10<br>`;

                            if (summary.key_insights && summary.key_insights.length > 0) {
                                dashboardHTML += '<strong>Key Insights:</strong><br>';
                                summary.key_insights.slice(0, 2).forEach((insight, i) => {
                                    dashboardHTML += `• ${insight}<br>`;
                                });
                            }
                        }

                        // Performance trends
                        if (trendAnalysis.performance_trends && trendAnalysis.performance_trends.trend_direction) {
                            const perfTrends = trendAnalysis.performance_trends;
                            dashboardHTML += `Performance: ${perfTrends.trend_direction}<br>`;
                            if (perfTrends.improvement_rate_per_session !== undefined) {
                                const rate = (perfTrends.improvement_rate_per_session * 100).toFixed(1);
                                dashboardHTML += `Rate: ${rate}% per session<br>`;
                            }
                        }

                        // Track-specific improvements
                        if (trendAnalysis.track_specific_trends && Object.keys(trendAnalysis.track_specific_trends).length > 0) {
                            const improving = Object.entries(trendAnalysis.track_specific_trends)
                                .filter(([track, data]) => data.improvement_trend < -0.01)
                                .slice(0, 2);
                            if (improving.length > 0) {
                                dashboardHTML += '<strong>Improving at:</strong><br>';
                                improving.forEach(([track, data]) => {
                                    dashboardHTML += `• ${track}<br>`;
                                });
                            }
                        }

                        dashboardHTML += '<br>';
                    }

                    // Session Timeline
                    if (dashboard.session_timeline && dashboard.session_timeline.timeline) {
                        const timeline = dashboard.session_timeline;
                        dashboardHTML += '<strong>RECENT SESSIONS:</strong><br>';
                        timeline.timeline.slice(-3).forEach((session, i) => {
                            dashboardHTML += `${session.track} (${session.car}): `;
                            if (session.fastest_lap) {
                                dashboardHTML += `${session.fastest_lap.toFixed(3)}s`;
                            }
                            dashboardHTML += ` | ${session.laps} laps<br>`;
                        });
                        dashboardHTML += '<br>';
                    }

                    dashboardHTML += '<em>Dashboard powered by advanced analytics engine</em>';

                    addMessage(dashboardHTML, 'coach-message');
                } else {
                    addMessage('<strong>Analytics Dashboard:</strong> ' + (data.error || 'Dashboard generation failed'), 'coach-message');
                }
            } catch (error) {
                console.error('Analytics dashboard error:', error);
                addMessage('<strong>Analytics Dashboard:</strong> Dashboard not available - ' + error.message, 'coach-message');
            }
        }

        // Interactive Charts Functions
        let chartsVisible = false;
        let chartInstances = {};

        async function toggleCharts() {
            const chartsSection = document.getElementById('charts-section');

            if (!chartsVisible) {
                chartsSection.style.display = 'grid';
                chartsVisible = true;
                await loadChartsData();
            } else {
                chartsSection.style.display = 'none';
                chartsVisible = false;
                // Destroy existing charts
                Object.values(chartInstances).forEach(chart => chart.destroy());
                chartInstances = {};
            }
        }

        async function loadChartsData() {
            try {
                addMessage('<strong>Interactive Charts:</strong> Loading chart data...', 'coach-message');

                const response = await fetch('/api/analytics-dashboard');
                if (!response.ok) {
                    throw new Error('Failed to load chart data');
                }

                const data = await response.json();
                if (data.success && data.dashboard) {
                    createCharts(data.dashboard);
                    addMessage('<strong>Interactive Charts:</strong> Charts loaded successfully!', 'coach-message');
                } else {
                    throw new Error('Invalid chart data received');
                }
            } catch (error) {
                console.error('Charts loading error:', error);
                addMessage('<strong>Interactive Charts:</strong> Failed to load charts - ' + error.message, 'coach-message');
            }
        }

        function createCharts(dashboard) {
            // Performance Trends Chart
            if (dashboard.performance_trends && dashboard.performance_trends.lap_time_progression) {
                createPerformanceChart(dashboard.performance_trends);
            }

            // Lap Time Distribution Chart
            if (dashboard.track_analysis) {
                createLapTimeChart(dashboard.track_analysis);
            }

            // Consistency Chart
            if (dashboard.consistency_analysis) {
                createConsistencyChart(dashboard.consistency_analysis);
            }

            // Track Performance Chart
            if (dashboard.track_analysis) {
                createTrackChart(dashboard.track_analysis);
            }

            // Car Performance Chart
            if (dashboard.car_comparison) {
                createCarChart(dashboard.car_comparison);
            }

            // Session Timeline Chart
            if (dashboard.session_timeline && dashboard.session_timeline.timeline) {
                createTimelineChart(dashboard.session_timeline);
            }
        }

        function createPerformanceChart(performanceData) {
            const ctx = document.getElementById('performanceChart').getContext('2d');

            if (chartInstances.performance) {
                chartInstances.performance.destroy();
            }

            const lapTimes = performanceData.lap_time_progression || [];
            const labels = lapTimes.map((_, index) => `Session ${index + 1}`);

            chartInstances.performance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Lap Times (seconds)',
                        data: lapTimes,
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            labels: { color: '#fff' }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            ticks: { color: '#fff' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        },
                        x: {
                            ticks: { color: '#fff' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        }
                    }
                }
            });
        }

        function createLapTimeChart(trackData) {
            const ctx = document.getElementById('lapTimeChart').getContext('2d');

            if (chartInstances.lapTime) {
                chartInstances.lapTime.destroy();
            }

            const tracks = Object.keys(trackData);
            const lapTimes = tracks.map(track => trackData[track].best_lap_time);

            chartInstances.lapTime = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: tracks,
                    datasets: [{
                        label: 'Best Lap Time (seconds)',
                        data: lapTimes,
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.8)',
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 206, 86, 0.8)',
                            'rgba(75, 192, 192, 0.8)',
                            'rgba(153, 102, 255, 0.8)'
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            labels: { color: '#fff' }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            ticks: { color: '#fff' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        },
                        x: {
                            ticks: { color: '#fff' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        }
                    }
                }
            });
        }

        function createConsistencyChart(consistencyData) {
            const ctx = document.getElementById('consistencyChart').getContext('2d');

            if (chartInstances.consistency) {
                chartInstances.consistency.destroy();
            }

            const scores = consistencyData.consistency_scores || [];
            const labels = consistencyData.session_labels || scores.map((_, i) => `Session ${i + 1}`);

            chartInstances.consistency = new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Consistency Rating',
                        data: scores,
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        pointBackgroundColor: 'rgba(255, 99, 132, 1)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(255, 99, 132, 1)'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            labels: { color: '#fff' }
                        }
                    },
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 10,
                            ticks: { color: '#fff' },
                            grid: { color: 'rgba(255,255,255,0.1)' },
                            angleLines: { color: 'rgba(255,255,255,0.1)' }
                        }
                    }
                }
            });
        }

        function createTrackChart(trackData) {
            const ctx = document.getElementById('trackChart').getContext('2d');

            if (chartInstances.track) {
                chartInstances.track.destroy();
            }

            const tracks = Object.keys(trackData);
            const sessions = tracks.map(track => trackData[track].session_count);
            const avgTimes = tracks.map(track => trackData[track].average_lap_time);

            chartInstances.track = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: tracks,
                    datasets: [{
                        label: 'Sessions per Track',
                        data: sessions,
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.8)',
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 206, 86, 0.8)',
                            'rgba(75, 192, 192, 0.8)'
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            labels: { color: '#fff' }
                        }
                    }
                }
            });
        }

        function createCarChart(carData) {
            const ctx = document.getElementById('carChart').getContext('2d');

            if (chartInstances.car) {
                chartInstances.car.destroy();
            }

            const cars = Object.keys(carData);
            const bestTimes = cars.map(car => carData[car].best_lap_time);
            const consistency = cars.map(car => carData[car].average_consistency);

            chartInstances.car = new Chart(ctx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Car Performance',
                        data: cars.map((car, index) => ({
                            x: bestTimes[index],
                            y: consistency[index],
                            label: car
                        })),
                        backgroundColor: 'rgba(75, 192, 192, 0.6)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        pointRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            labels: { color: '#fff' }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `${context.raw.label}: ${context.parsed.x.toFixed(2)}s, ${context.parsed.y.toFixed(1)} consistency`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Best Lap Time (seconds)',
                                color: '#fff'
                            },
                            ticks: { color: '#fff' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Consistency Rating',
                                color: '#fff'
                            },
                            ticks: { color: '#fff' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        }
                    }
                }
            });
        }

        function createTimelineChart(timelineData) {
            const ctx = document.getElementById('timelineChart').getContext('2d');

            if (chartInstances.timeline) {
                chartInstances.timeline.destroy();
            }

            const timeline = timelineData.timeline || [];
            const dates = timeline.map(session => new Date(session.date).toLocaleDateString());
            const fastestLaps = timeline.map(session => session.fastest_lap);

            chartInstances.timeline = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Session Progress',
                        data: fastestLaps,
                        borderColor: 'rgb(255, 206, 86)',
                        backgroundColor: 'rgba(255, 206, 86, 0.2)',
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: 'rgb(255, 206, 86)',
                        pointBorderColor: '#fff',
                        pointRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            labels: { color: '#fff' }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: {
                                display: true,
                                text: 'Fastest Lap (seconds)',
                                color: '#fff'
                            },
                            ticks: { color: '#fff' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Session Date',
                                color: '#fff'
                            },
                            ticks: { color: '#fff' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        }
                    }
                }
            });
        }

        // Setup Optimizer function
        async function loadSetupOptimizer() {
            console.log('Loading setup optimizer...');

            // Add loading message
            addMessage('<strong>Setup Optimizer:</strong> Analyzing car setup and generating recommendations...', 'coach-message');

            try {
                // Get available car/track combinations
                const response = await fetch('/api/setup-optimizer');
                console.log('Setup optimizer response status:', response.status);

                if (!response.ok) {
                    throw new Error('Setup optimizer not available: ' + response.status);
                }

                const data = await response.json();
                console.log('Setup optimizer data:', data);

                if (data.success && data.setup_analysis) {
                    displaySetupAnalysis(data.setup_analysis);
                } else {
                    addMessage('<strong>Setup Optimizer:</strong> ' + (data.error || 'Setup analysis failed'), 'coach-message');
                }
            } catch (error) {
                console.error('Setup optimizer error:', error);
                addMessage('<strong>Setup Optimizer:</strong> Setup optimizer not available - ' + error.message, 'coach-message');
            }
        }

        function displaySetupAnalysis(analyses) {
            let setupHTML = '<strong>CAR SETUP OPTIMIZATION ANALYSIS</strong><br><br>';

            analyses.forEach((analysis, index) => {
                const car = analysis.car;
                const track = analysis.track;

                setupHTML += `<strong>═══ ${car.toUpperCase()} AT ${track.toUpperCase()} ═══</strong><br><br>`;

                // Performance Analysis
                if (analysis.performance_analysis && Object.keys(analysis.performance_analysis).length > 0) {
                    const perf = analysis.performance_analysis;
                    setupHTML += '<strong>📊 CURRENT PERFORMANCE:</strong><br>';

                    if (perf.lap_time_analysis) {
                        const lapAnalysis = perf.lap_time_analysis;
                        if (lapAnalysis.best_time) {
                            setupHTML += `Best Time: ${lapAnalysis.best_time.toFixed(3)}s<br>`;
                        }
                        if (lapAnalysis.improvement_potential) {
                            setupHTML += `Improvement Potential: ${lapAnalysis.improvement_potential.toFixed(3)}s<br>`;
                        }
                    }

                    if (perf.consistency_analysis) {
                        const consAnalysis = perf.consistency_analysis;
                        if (consAnalysis.average_consistency) {
                            setupHTML += `Consistency Rating: ${consAnalysis.average_consistency.toFixed(1)}/10<br>`;
                        }
                        if (consAnalysis.consistency_rating) {
                            setupHTML += `Consistency Level: ${consAnalysis.consistency_rating}<br>`;
                        }
                    }

                    if (perf.strengths && perf.strengths.length > 0) {
                        setupHTML += '<strong>Strengths:</strong><br>';
                        perf.strengths.forEach(strength => {
                            setupHTML += `• ${strength}<br>`;
                        });
                    }

                    if (perf.weaknesses && perf.weaknesses.length > 0) {
                        setupHTML += '<strong>Areas to Improve:</strong><br>';
                        perf.weaknesses.forEach(weakness => {
                            setupHTML += `• ${weakness}<br>`;
                        });
                    }
                    setupHTML += '<br>';
                }

                // Setup Recommendations
                if (analysis.setup_recommendations && Object.keys(analysis.setup_recommendations).length > 0) {
                    const recs = analysis.setup_recommendations;
                    setupHTML += '<strong>🔧 SETUP RECOMMENDATIONS:</strong><br>';

                    if (recs.immediate_changes && recs.immediate_changes.length > 0) {
                        setupHTML += '<strong>Immediate Changes:</strong><br>';
                        recs.immediate_changes.forEach(change => {
                            setupHTML += `• ${change.category}: ${change.change}<br>`;
                            if (change.expected_gain) {
                                setupHTML += `  Expected gain: ${change.expected_gain}<br>`;
                            }
                        });
                    }

                    if (recs.setup_categories && Object.keys(recs.setup_categories).length > 0) {
                        setupHTML += '<strong>Setup Categories:</strong><br>';
                        Object.entries(recs.setup_categories).forEach(([category, details]) => {
                            setupHTML += `<strong>${category.charAt(0).toUpperCase() + category.slice(1)}:</strong><br>`;
                            if (details.rationale) {
                                setupHTML += `  ${details.rationale}<br>`;
                            }
                            if (details.settings && Object.keys(details.settings).length > 0) {
                                Object.entries(details.settings).forEach(([setting, value]) => {
                                    setupHTML += `  - ${setting}: ${value}<br>`;
                                });
                            }
                        });
                    }

                    if (recs.track_specific_advice && Object.keys(recs.track_specific_advice).length > 0) {
                        const trackAdvice = recs.track_specific_advice;
                        setupHTML += '<strong>Track-Specific Advice:</strong><br>';
                        if (trackAdvice.track_characteristics) {
                            setupHTML += `Track type: ${trackAdvice.track_characteristics}<br>`;
                        }
                        if (trackAdvice.recommended_approach) {
                            setupHTML += `Approach: ${trackAdvice.recommended_approach}<br>`;
                        }
                    }
                    setupHTML += '<br>';
                }

                // Optimization Priorities
                if (analysis.optimization_priorities && analysis.optimization_priorities.length > 0) {
                    setupHTML += '<strong>🎯 OPTIMIZATION PRIORITIES:</strong><br>';
                    analysis.optimization_priorities.forEach((priority, i) => {
                        setupHTML += `${i + 1}. <strong>${priority.area}</strong> (${priority.priority})<br>`;
                        if (priority.potential_gain) {
                            setupHTML += `   Potential gain: ${priority.potential_gain}<br>`;
                        }
                        if (priority.description) {
                            setupHTML += `   ${priority.description}<br>`;
                        }
                    });
                    setupHTML += '<br>';
                }

                // Expected Improvements
                if (analysis.expected_improvements && Object.keys(analysis.expected_improvements).length > 0) {
                    const improvements = analysis.expected_improvements;
                    setupHTML += '<strong>📈 EXPECTED IMPROVEMENTS:</strong><br>';

                    if (improvements.lap_time_potential && Object.keys(improvements.lap_time_potential).length > 0) {
                        const lapPotential = improvements.lap_time_potential;
                        setupHTML += 'Lap Time Potential:<br>';
                        if (lapPotential.realistic) {
                            setupHTML += `  Realistic gain: ${lapPotential.realistic}<br>`;
                        }
                        if (lapPotential.target_time) {
                            setupHTML += `  Target time: ${lapPotential.target_time.toFixed(3)}s<br>`;
                        }
                    }

                    if (improvements.consistency_potential && Object.keys(improvements.consistency_potential).length > 0) {
                        const consPotential = improvements.consistency_potential;
                        setupHTML += 'Consistency Potential:<br>';
                        if (consPotential.potential_gain) {
                            setupHTML += `  Potential gain: +${consPotential.potential_gain.toFixed(1)} points<br>`;
                        }
                        if (consPotential.target_rating) {
                            setupHTML += `  Target rating: ${consPotential.target_rating.toFixed(1)}/10<br>`;
                        }
                    }
                    setupHTML += '<br>';
                }

                // Confidence Level
                if (analysis.confidence_level) {
                    setupHTML += `<strong>Confidence Level:</strong> ${analysis.confidence_level}<br><br>`;
                }

                if (index < analyses.length - 1) {
                    setupHTML += '<hr><br>';
                }
            });

            setupHTML += '<em>Analysis powered by professional setup optimization engine</em>';

            addMessage(setupHTML, 'coach-message');
        }

        // Race Strategy function
        async function loadRaceStrategy() {
            console.log('Loading race strategy...');

            // Add loading message
            addMessage('<strong>Race Strategy:</strong> Analyzing fuel consumption, tire wear, and pit strategy...', 'coach-message');

            try {
                // Use default race parameters (can be made configurable later)
                const raceLength = 30; // 30 minute race
                const tireCompound = 'medium';
                const weather = 'dry';

                const response = await fetch(`/api/race-strategy?race_length=${raceLength}&tire_compound=${tireCompound}&weather=${weather}`);
                console.log('Race strategy response status:', response.status);

                if (!response.ok) {
                    throw new Error('Race strategy not available: ' + response.status);
                }

                const data = await response.json();
                console.log('Race strategy data:', data);

                if (data.success && data.race_strategies) {
                    displayRaceStrategy(data.race_strategies);
                } else {
                    addMessage('<strong>Race Strategy:</strong> ' + (data.error || 'Strategy analysis failed'), 'coach-message');
                }
            } catch (error) {
                console.error('Race strategy error:', error);
                addMessage('<strong>Race Strategy:</strong> Race strategy not available - ' + error.message, 'coach-message');
            }
        }

        function displayRaceStrategy(strategies) {
            let strategyHTML = '<strong>RACE STRATEGY ANALYSIS</strong><br><br>';

            strategies.forEach((strategy, index) => {
                const car = strategy.car;
                const track = strategy.track;
                const raceLength = strategy.race_length_minutes;

                strategyHTML += `<strong>═══ ${car.toUpperCase()} AT ${track.toUpperCase()} (${raceLength} MIN) ═══</strong><br><br>`;

                // Race Overview
                strategyHTML += '<strong>RACE OVERVIEW:</strong><br>';
                if (strategy.estimated_total_laps) {
                    strategyHTML += `Estimated Laps: ${strategy.estimated_total_laps}<br>`;
                }
                if (strategy.average_lap_time) {
                    strategyHTML += `Average Lap Time: ${strategy.average_lap_time.toFixed(3)}s<br>`;
                }
                strategyHTML += '<br>';

                // Fuel Strategy
                if (strategy.fuel_strategy && Object.keys(strategy.fuel_strategy).length > 0) {
                    const fuel = strategy.fuel_strategy;
                    strategyHTML += '<strong>FUEL STRATEGY:</strong><br>';
                    if (fuel.consumption_per_lap) {
                        strategyHTML += `Consumption: ${fuel.consumption_per_lap} L/lap<br>`;
                    }
                    if (fuel.total_fuel_needed) {
                        strategyHTML += `Total Fuel Needed: ${fuel.total_fuel_needed} L<br>`;
                    }
                    if (fuel.pit_stops_required !== undefined) {
                        strategyHTML += `Fuel Stops Required: ${fuel.pit_stops_required}<br>`;
                    }
                    if (fuel.max_stint_length) {
                        strategyHTML += `Max Stint Length: ${fuel.max_stint_length} laps<br>`;
                    }
                    if (fuel.fuel_strategy_type) {
                        strategyHTML += `Strategy Type: ${fuel.fuel_strategy_type.replace('_', ' ')}<br>`;
                    }
                    strategyHTML += '<br>';
                }

                // Tire Strategy
                if (strategy.tire_strategy && Object.keys(strategy.tire_strategy).length > 0) {
                    const tire = strategy.tire_strategy;
                    strategyHTML += '<strong>TIRE STRATEGY:</strong><br>';
                    if (tire.compound) {
                        strategyHTML += `Compound: ${tire.compound}<br>`;
                    }
                    if (tire.effective_tire_life) {
                        strategyHTML += `Tire Life: ${tire.effective_tire_life} laps<br>`;
                    }
                    if (tire.tire_changes_needed !== undefined) {
                        strategyHTML += `Tire Changes Needed: ${tire.tire_changes_needed}<br>`;
                    }
                    if (tire.optimal_stint_length) {
                        strategyHTML += `Optimal Stint: ${tire.optimal_stint_length} laps<br>`;
                    }
                    strategyHTML += '<br>';
                }

                // Pit Strategy
                if (strategy.pit_strategy && Object.keys(strategy.pit_strategy).length > 0) {
                    const pit = strategy.pit_strategy;
                    strategyHTML += '<strong>PIT STRATEGY:</strong><br>';
                    if (pit.strategy_type) {
                        strategyHTML += `Strategy: ${pit.strategy_type.replace('_', ' ')}<br>`;
                    }
                    if (pit.total_stops !== undefined) {
                        strategyHTML += `Total Stops: ${pit.total_stops}<br>`;
                    }
                    if (pit.total_pit_time) {
                        strategyHTML += `Total Pit Time: ${pit.total_pit_time.toFixed(1)}s<br>`;
                    }

                    if (pit.pit_windows && pit.pit_windows.length > 0) {
                        strategyHTML += '<strong>Pit Windows:</strong><br>';
                        pit.pit_windows.forEach(window => {
                            strategyHTML += `  Stop ${window.stop_number}: Laps ${window.window_start}-${window.window_end} (optimal: ${window.optimal_lap})<br>`;
                        });
                    }
                    strategyHTML += '<br>';
                }

                // Lap Time Projections
                if (strategy.lap_time_projections && strategy.lap_time_projections.race_time) {
                    const projections = strategy.lap_time_projections;
                    strategyHTML += '<strong>RACE PROJECTIONS:</strong><br>';
                    strategyHTML += `Projected Race Time: ${projections.race_time} minutes<br>`;
                    if (projections.average_race_pace) {
                        strategyHTML += `Average Race Pace: ${projections.average_race_pace.toFixed(3)}s/lap<br>`;
                    }
                    if (projections.fastest_projected_lap) {
                        strategyHTML += `Fastest Projected Lap: ${projections.fastest_projected_lap.toFixed(3)}s<br>`;
                    }
                    if (projections.slowest_projected_lap) {
                        strategyHTML += `Slowest Projected Lap: ${projections.slowest_projected_lap.toFixed(3)}s<br>`;
                    }
                    strategyHTML += '<br>';
                }

                // Alternative Strategies
                if (strategy.alternative_strategies && strategy.alternative_strategies.length > 0) {
                    strategyHTML += '<strong>ALTERNATIVE STRATEGIES:</strong><br>';
                    strategy.alternative_strategies.forEach(alt => {
                        strategyHTML += `<strong>${alt.name}:</strong> ${alt.description}<br>`;
                        strategyHTML += `  Risk Level: ${alt.risk_level}<br>`;
                        if (alt.time_delta) {
                            strategyHTML += `  Time Delta: ${alt.time_delta}<br>`;
                        }
                        if (alt.pros && alt.pros.length > 0) {
                            strategyHTML += `  Pros: ${alt.pros.join(', ')}<br>`;
                        }
                        strategyHTML += '<br>';
                    });
                }

                // Risk Assessment
                if (strategy.risk_assessment && Object.keys(strategy.risk_assessment).length > 0) {
                    const risks = strategy.risk_assessment;
                    strategyHTML += '<strong>RISK ASSESSMENT:</strong><br>';
                    if (risks.overall_risk) {
                        strategyHTML += `Overall Risk: ${risks.overall_risk}<br>`;
                    }
                    if (risks.fuel_risk) {
                        strategyHTML += `Fuel Risk: ${risks.fuel_risk}<br>`;
                    }
                    if (risks.tire_risk) {
                        strategyHTML += `Tire Risk: ${risks.tire_risk}<br>`;
                    }
                    strategyHTML += '<br>';
                }

                // Recommendations
                if (strategy.recommendations && strategy.recommendations.length > 0) {
                    strategyHTML += '<strong>STRATEGIC RECOMMENDATIONS:</strong><br>';
                    strategy.recommendations.forEach((rec, i) => {
                        strategyHTML += `${i + 1}. ${rec}<br>`;
                    });
                    strategyHTML += '<br>';
                }

                if (index < strategies.length - 1) {
                    strategyHTML += '<hr><br>';
                }
            });

            strategyHTML += '<em>Analysis powered by professional race strategy system</em>';

            addMessage(strategyHTML, 'coach-message');
        }

        // Driver Comparison function
        async function loadDriverComparison() {
            console.log('Loading driver comparison...');

            // Add loading message
            addMessage('<strong>Driver Comparison:</strong> Analyzing driver performance and generating comparisons...', 'coach-message');

            try {
                const response = await fetch('/api/driver-comparison');
                const data = await response.json();

                console.log('Driver comparison response:', data);

                if (data.success) {
                    displayDriverComparison(data);
                } else {
                    addMessage('<strong>Driver Comparison:</strong> ' + (data.error || 'Driver comparison failed'), 'coach-message');
                }
            } catch (error) {
                console.error('Driver comparison error:', error);
                addMessage('<strong>Driver Comparison:</strong> Driver comparison not available - ' + error.message, 'coach-message');
            }
        }

        function displayDriverComparison(data) {
            let comparisonHTML = '<strong>MULTI-DRIVER PERFORMANCE COMPARISON</strong><br><br>';

            if (!data.drivers || data.drivers.length < 2) {
                comparisonHTML += '<em>Need at least 2 drivers for comparison analysis</em>';
                addMessage(comparisonHTML, 'coach-message');
                return;
            }

            comparisonHTML += `<strong>DRIVERS ANALYZED: ${data.drivers.join(', ')}</strong><br><br>`;

            // Driver Rankings
            if (data.rankings && data.rankings.length > 0) {
                comparisonHTML += '<strong>═══ OVERALL RANKINGS ═══</strong><br>';
                data.rankings.forEach((ranking, index) => {
                    comparisonHTML += `${index + 1}. <strong>${ranking.driver}</strong> - Score: ${ranking.overall_score.toFixed(2)}<br>`;
                    if (ranking.specializations && ranking.specializations.length > 0) {
                        comparisonHTML += `   Strengths: ${ranking.specializations.join(', ')}<br>`;
                    }
                });
                comparisonHTML += '<br>';
            }

            // Driver Profiles
            if (data.driver_profiles) {
                comparisonHTML += '<strong>═══ DRIVER PROFILES ═══</strong><br>';
                Object.entries(data.driver_profiles).forEach(([driver, profile]) => {
                    comparisonHTML += `<strong>${driver.toUpperCase()}:</strong><br>`;

                    if (profile.classification) {
                        comparisonHTML += `Type: ${profile.classification}<br>`;
                    }

                    if (profile.performance_metrics) {
                        const metrics = profile.performance_metrics;
                        comparisonHTML += 'Performance Metrics:<br>';
                        if (metrics.avg_lap_time) comparisonHTML += `  Average Lap Time: ${metrics.avg_lap_time.toFixed(3)}s<br>`;
                        if (metrics.consistency_score) comparisonHTML += `  Consistency: ${(metrics.consistency_score * 100).toFixed(1)}%<br>`;
                        if (metrics.improvement_rate) comparisonHTML += `  Improvement Rate: ${(metrics.improvement_rate * 100).toFixed(1)}%<br>`;
                    }

                    if (profile.track_specializations && profile.track_specializations.length > 0) {
                        comparisonHTML += `Track Specializations: ${profile.track_specializations.join(', ')}<br>`;
                    }

                    if (profile.car_specializations && profile.car_specializations.length > 0) {
                        comparisonHTML += `Car Specializations: ${profile.car_specializations.join(', ')}<br>`;
                    }

                    comparisonHTML += '<br>';
                });
            }

            // Head-to-Head Comparisons
            if (data.comparisons && Object.keys(data.comparisons).length > 0) {
                comparisonHTML += '<strong>═══ HEAD-TO-HEAD COMPARISONS ═══</strong><br>';
                Object.entries(data.comparisons).forEach(([comparison_key, comparison]) => {
                    if (comparison && comparison.faster_driver) {
                        const drivers = comparison_key.split('_vs_');
                        comparisonHTML += `<strong>${drivers[0]} vs ${drivers[1]}:</strong><br>`;
                        comparisonHTML += `Faster Driver: ${comparison.faster_driver}<br>`;
                        if (comparison.time_difference) {
                            comparisonHTML += `Time Difference: ${comparison.time_difference.toFixed(3)}s per lap<br>`;
                        }
                        if (comparison.percentage_difference) {
                            comparisonHTML += `Performance Gap: ${(comparison.percentage_difference * 100).toFixed(2)}%<br>`;
                        }
                        comparisonHTML += '<br>';
                    }
                });
            }

            // Insights and Recommendations
            if (data.insights && data.insights.length > 0) {
                comparisonHTML += '<strong>═══ INSIGHTS & RECOMMENDATIONS ═══</strong><br>';
                data.insights.forEach(insight => {
                    comparisonHTML += `• ${insight}<br>`;
                });
                comparisonHTML += '<br>';
            }

            comparisonHTML += '<em>Analysis powered by professional driver comparison system</em>';

            addMessage(comparisonHTML, 'coach-message');
        }

        // Advanced Metrics function
        async function loadAdvancedMetrics() {
            console.log('Loading advanced metrics...');

            // Add loading message
            addMessage('<strong>Advanced Metrics:</strong> Analyzing G-forces, cornering speeds, and braking points...', 'coach-message');

            try {
                const response = await fetch('/api/advanced-metrics');
                const data = await response.json();

                console.log('Advanced metrics response:', data);

                if (data.success && data.metrics_analysis) {
                    displayAdvancedMetrics(data.metrics_analysis);
                } else {
                    addMessage('<strong>Advanced Metrics:</strong> ' + (data.error || 'Advanced metrics analysis failed'), 'coach-message');
                }
            } catch (error) {
                console.error('Advanced metrics error:', error);
                addMessage('<strong>Advanced Metrics:</strong> Advanced metrics not available - ' + error.message, 'coach-message');
            }
        }

        function displayAdvancedMetrics(analysis) {
            let metricsHTML = '<strong>ADVANCED TELEMETRY METRICS ANALYSIS</strong><br><br>';

            metricsHTML += `<strong>SESSIONS ANALYZED: ${analysis.session_count}</strong><br><br>`;

            // Individual session analysis
            if (analysis.individual_sessions && analysis.individual_sessions.length > 0) {
                metricsHTML += '<strong>═══ SESSION BREAKDOWN ═══</strong><br>';

                analysis.individual_sessions.forEach((session, index) => {
                    metricsHTML += `<strong>${session.car.toUpperCase()} AT ${session.track.toUpperCase()}</strong> (${session.lap_count} laps)<br>`;

                    // G-Force Analysis
                    if (session.g_force_analysis) {
                        const gforce = session.g_force_analysis;
                        metricsHTML += '<strong>G-Force Analysis:</strong><br>';

                        if (gforce.lateral) {
                            metricsHTML += `  Lateral G - Max: ${gforce.lateral.max.toFixed(2)}g, Avg: ${gforce.lateral.average.toFixed(2)}g<br>`;
                            metricsHTML += `  High-G Time: ${gforce.lateral.sustained_high.toFixed(1)}%<br>`;
                        }

                        if (gforce.longitudinal) {
                            metricsHTML += `  Max Acceleration: ${gforce.longitudinal.max_acceleration.toFixed(2)}g<br>`;
                            metricsHTML += `  Max Deceleration: ${Math.abs(gforce.longitudinal.max_deceleration).toFixed(2)}g<br>`;
                            metricsHTML += `  Braking Efficiency: ${gforce.longitudinal.braking_efficiency.toFixed(1)}%<br>`;
                        }

                        if (gforce.combined) {
                            metricsHTML += `  Combined G-Force: ${gforce.combined.max_combined.toFixed(2)}g<br>`;
                            metricsHTML += `  Consistency Score: ${gforce.combined.consistency_score.toFixed(1)}%<br>`;
                        }
                        metricsHTML += '<br>';
                    }

                    // Cornering Analysis
                    if (session.cornering_analysis) {
                        const cornering = session.cornering_analysis;
                        metricsHTML += '<strong>Cornering Analysis:</strong><br>';
                        metricsHTML += `  Total Corners: ${cornering.total_corners}<br>`;

                        if (cornering.overall_cornering) {
                            const overall = cornering.overall_cornering;
                            metricsHTML += `  Avg Entry Speed: ${overall.average_entry_speed.toFixed(1)} km/h<br>`;
                            metricsHTML += `  Avg Apex Speed: ${overall.average_apex_speed.toFixed(1)} km/h<br>`;
                            metricsHTML += `  Avg Exit Speed: ${overall.average_exit_speed.toFixed(1)} km/h<br>`;
                            metricsHTML += `  Cornering Efficiency: ${overall.cornering_efficiency.toFixed(1)}%<br>`;
                        }

                        if (cornering.corner_types) {
                            metricsHTML += '  Corner Type Breakdown:<br>';
                            Object.entries(cornering.corner_types).forEach(([type, data]) => {
                                metricsHTML += `    ${type.charAt(0).toUpperCase() + type.slice(1)}: ${data.count} corners, `;
                                metricsHTML += `${data.speed_maintained.toFixed(1)}% speed maintained<br>`;
                            });
                        }
                        metricsHTML += '<br>';
                    }

                    // Braking Analysis
                    if (session.braking_analysis) {
                        const braking = session.braking_analysis;
                        metricsHTML += '<strong>Braking Analysis:</strong><br>';
                        metricsHTML += `  Braking Zones: ${braking.total_braking_zones}<br>`;

                        if (braking.braking_performance) {
                            const perf = braking.braking_performance;
                            metricsHTML += `  Avg Deceleration: ${perf.average_deceleration.toFixed(2)}g<br>`;
                            metricsHTML += `  Avg Brake Pressure: ${perf.average_brake_pressure.toFixed(1)}%<br>`;
                            metricsHTML += `  Avg Braking Distance: ${perf.braking_distance.toFixed(1)}m<br>`;
                            metricsHTML += `  Braking Consistency: ${perf.consistency.toFixed(1)}%<br>`;
                        }

                        if (braking.braking_zones_by_intensity) {
                            const zones = braking.braking_zones_by_intensity;
                            metricsHTML += '  Braking Intensity:<br>';
                            Object.entries(zones).forEach(([intensity, count]) => {
                                metricsHTML += `    ${intensity.charAt(0).toUpperCase() + intensity.slice(1)}: ${count} zones<br>`;
                            });
                        }
                        metricsHTML += '<br>';
                    }

                    // Performance Envelope
                    if (session.performance_envelope) {
                        const envelope = session.performance_envelope;
                        metricsHTML += '<strong>Performance Envelope:</strong><br>';
                        metricsHTML += `  Overall Score: ${envelope.overall_score.toFixed(1)}%<br>`;

                        if (envelope.strengths && envelope.strengths.length > 0) {
                            metricsHTML += `  Strengths: ${envelope.strengths.join(', ')}<br>`;
                        }

                        if (envelope.areas_for_improvement && envelope.areas_for_improvement.length > 0) {
                            metricsHTML += `  Areas for Improvement: ${envelope.areas_for_improvement.join(', ')}<br>`;
                        }
                        metricsHTML += '<br>';
                    }

                    metricsHTML += '<br>';
                });
            }

            // Performance Insights
            if (analysis.performance_insights && analysis.performance_insights.length > 0) {
                metricsHTML += '<strong>═══ PERFORMANCE INSIGHTS ═══</strong><br>';
                analysis.performance_insights.forEach(insight => {
                    metricsHTML += `• ${insight}<br>`;
                });
                metricsHTML += '<br>';
            }

            // Improvement Areas
            if (analysis.improvement_areas && analysis.improvement_areas.length > 0) {
                metricsHTML += '<strong>═══ IMPROVEMENT RECOMMENDATIONS ═══</strong><br>';
                analysis.improvement_areas.forEach(area => {
                    metricsHTML += `• ${area}<br>`;
                });
                metricsHTML += '<br>';
            }

            // Professional Benchmarks
            if (analysis.professional_benchmarks) {
                const benchmarks = analysis.professional_benchmarks;
                metricsHTML += '<strong>═══ PROFESSIONAL BENCHMARKS ═══</strong><br>';

                if (benchmarks.lateral_g_targets) {
                    metricsHTML += '<strong>Lateral G-Force Targets:</strong><br>';
                    Object.entries(benchmarks.lateral_g_targets).forEach(([level, target]) => {
                        metricsHTML += `  ${level.replace('_', ' ').toUpperCase()}: ${target}<br>`;
                    });
                }

                if (benchmarks.braking_g_targets) {
                    metricsHTML += '<strong>Braking G-Force Targets:</strong><br>';
                    Object.entries(benchmarks.braking_g_targets).forEach(([level, target]) => {
                        metricsHTML += `  ${level.replace('_', ' ').toUpperCase()}: ${target}<br>`;
                    });
                }

                if (benchmarks.consistency_targets) {
                    metricsHTML += '<strong>Consistency Targets:</strong><br>';
                    Object.entries(benchmarks.consistency_targets).forEach(([level, target]) => {
                        metricsHTML += `  ${level.replace('_', ' ').toUpperCase()}: ${target}<br>`;
                    });
                }
            }

            metricsHTML += '<br><em>Analysis powered by professional advanced metrics system</em>';

            addMessage(metricsHTML, 'coach-message');
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Main page with enhanced features"""
    try:
        stats = coach.get_summary_stats()
        return render_template_string(HTML_TEMPLATE, stats=stats)
    except Exception as e:
        error_stats = {'message': f'Error loading enhanced stats: {e}'}
        return render_template_string(HTML_TEMPLATE, stats=error_stats)

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Enhanced API endpoint for asking questions"""
    try:
        print("Received enhanced ask request")
        data = request.get_json()
        question = data.get('question', '')

        print(f"Enhanced question: {question}")

        if not question:
            return jsonify({'error': 'No question provided', 'success': False}), 400

        # Get answer from enhanced coach
        answer = coach.answer_question(question)
        print(f"Enhanced answer: {answer[:100]}...")

        return jsonify({
            'question': question,
            'answer': answer,
            'success': True,
            'enhanced': True
        })

    except Exception as e:
        print(f"Error in enhanced ask_question: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/stats')
def get_stats():
    """Get enhanced system statistics"""
    try:
        stats = coach.get_summary_stats()
        return jsonify({'stats': stats, 'success': True, 'enhanced': True})
    except Exception as e:
        print(f"Error in enhanced get_stats: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/professional-analysis')
def get_professional_analysis():
    """Get Cosworth Pi Toolbox-style professional analysis"""
    try:
        print("Received professional analysis request")

        # Get latest session with professional analysis
        if not coach.sessions:
            return jsonify({'error': 'No session data available', 'success': False}), 404

        latest_session = coach.sessions[-1]
        professional_analysis = latest_session.get('professional_analysis', {})

        if not professional_analysis or professional_analysis.get('status') == 'failed':
            return jsonify({'error': 'Professional analysis not available', 'success': False}), 404

        return jsonify({
            'analysis': professional_analysis,
            'session_info': latest_session.get('session_info', {}),
            'success': True,
            'professional': True
        })

    except Exception as e:
        print(f"Error in professional analysis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/monitoring-status')
def get_monitoring_status():
    """Get file monitoring status"""
    try:
        print("Received monitoring status request")
        status = file_monitor.get_monitoring_status()
        return jsonify({
            'status': status,
            'success': True
        })
    except Exception as e:
        print(f"Error getting monitoring status: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/analytics-dashboard')
def get_analytics_dashboard():
    """Get comprehensive analytics dashboard data"""
    try:
        print("Received analytics dashboard request")
        dashboard_data = analytics_engine.generate_dashboard_data()
        return jsonify({
            'dashboard': dashboard_data,
            'success': True,
            'analytics': True
        })
    except Exception as e:
        print(f"Error generating analytics dashboard: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/setup-optimizer')
def get_setup_optimizer():
    """Get car setup optimization analysis"""
    try:
        print("Received setup optimizer request")

        # Get unique car/track combinations from sessions
        car_track_combinations = set()
        for session in coach.sessions:
            session_info = session.get('session_info', {})
            car = session_info.get('car', '').lower()
            track = session_info.get('track', '').lower()
            if car and track:
                car_track_combinations.add((car, track))

        if not car_track_combinations:
            return jsonify({'error': 'No session data available for setup analysis', 'success': False}), 404

        # Generate setup analysis for each car/track combination
        setup_analyses = []
        for car, track in car_track_combinations:
            analysis = setup_optimizer.analyze_setup_performance(car, track)
            if not analysis.get('error'):
                setup_analyses.append(analysis)

        if not setup_analyses:
            return jsonify({'error': 'Unable to generate setup analysis', 'success': False}), 500

        return jsonify({
            'setup_analysis': setup_analyses,
            'total_combinations': len(setup_analyses),
            'success': True
        })
    except Exception as e:
        print(f"Error generating setup analysis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/race-strategy')
def get_race_strategy():
    """Get comprehensive race strategy analysis"""
    try:
        print("Received race strategy request")

        # Get parameters from query string
        race_length = int(request.args.get('race_length', 30))  # minutes
        tire_compound = request.args.get('tire_compound', 'medium')
        weather = request.args.get('weather', 'dry')

        print(f"Race parameters: {race_length} min, {tire_compound} tires, {weather} weather")

        # Get unique car/track combinations from sessions
        car_track_combinations = set()
        for session in coach.sessions:
            session_info = session.get('session_info', {})
            car = session_info.get('car', '').lower()
            track = session_info.get('track', '').lower()
            if car and track:
                car_track_combinations.add((car, track))

        if not car_track_combinations:
            return jsonify({'error': 'No session data available for race strategy analysis', 'success': False}), 404

        # Generate race strategy for each car/track combination
        race_strategies = []
        for car, track in car_track_combinations:
            strategy = race_strategist.analyze_race_strategy(car, track, race_length, tire_compound, weather)
            if not strategy.get('error'):
                race_strategies.append(strategy)

        if not race_strategies:
            return jsonify({'error': 'Unable to generate race strategies', 'success': False}), 500

        return jsonify({
            'race_strategies': race_strategies,
            'total_combinations': len(race_strategies),
            'race_parameters': {
                'race_length_minutes': race_length,
                'tire_compound': tire_compound,
                'weather': weather
            },
            'success': True
        })
    except Exception as e:
        print(f"Error generating race strategy: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/driver-comparison')
def get_driver_comparison():
    """Get comprehensive driver comparison analysis"""
    try:
        print("Received driver comparison request")

        # Get all available drivers from sessions
        drivers = driver_comparator.get_available_drivers()
        print(f"Found drivers: {list(drivers.keys())}")

        if len(drivers) < 2:
            return jsonify({
                'error': 'Need at least 2 drivers for comparison. Only found: ' + ', '.join(drivers.keys()),
                'success': False
            }), 400

        # Get driver profiles and analysis
        driver_profiles = driver_comparator.analyze_driver_profiles(drivers)

        # Perform head-to-head comparisons
        comparison_results = {}
        driver_list = list(drivers.keys())

        for i, driver1 in enumerate(driver_list):
            for j, driver2 in enumerate(driver_list[i+1:], i+1):
                comparison_key = f"{driver1}_vs_{driver2}"
                comparison_results[comparison_key] = driver_comparator.compare_drivers_head_to_head(
                    drivers[driver1], drivers[driver2], driver1, driver2
                )

        # Get rankings and insights
        rankings = driver_comparator.rank_drivers(drivers)
        insights = driver_comparator.generate_insights(driver_profiles, comparison_results, rankings)

        return jsonify({
            'drivers': list(drivers.keys()),
            'driver_profiles': driver_profiles,
            'comparisons': comparison_results,
            'rankings': rankings,
            'insights': insights,
            'success': True
        })
    except Exception as e:
        print(f"Error generating driver comparison: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/advanced-metrics')
def get_advanced_metrics():
    """Get comprehensive advanced metrics analysis"""
    try:
        print("Received advanced metrics request")

        # Get parameters from query string
        car_filter = request.args.get('car', None)
        track_filter = request.args.get('track', None)

        session_filter = {}
        if car_filter:
            session_filter['car'] = car_filter
        if track_filter:
            session_filter['track'] = track_filter

        print(f"Advanced metrics filters: {session_filter}")

        # Get advanced metrics analysis
        metrics_analysis = advanced_metrics.analyze_advanced_metrics(session_filter)

        if 'error' in metrics_analysis:
            return jsonify({
                'error': metrics_analysis['error'],
                'success': False
            }), 400

        return jsonify({
            'metrics_analysis': metrics_analysis,
            'success': True
        })
    except Exception as e:
        print(f"Error generating advanced metrics: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500

if __name__ == '__main__':
    print("\\n" + "="*60)
    print("   Enhanced iRacing Telemetry Coach Web UI")
    print("   Now with REAL telemetry parsing!")
    print("="*60)
    print("Features:")
    print("+ Real lap time extraction")
    print("+ Accurate consistency analysis")
    print("+ Enhanced coaching insights")
    print("+ Track-specific recommendations")
    print("+ OpenAI integration ready")
    print("+ Automatic file monitoring")
    print("+ Performance analytics dashboard")
    print("+ Professional car setup optimization")
    print("+ Race strategy with fuel and tire analysis")
    print("+ Multi-driver comparison and analysis")
    print("+ Advanced metrics: G-force, cornering, and braking analysis")
    print("="*60)
    print("Starting server...")
    print("Open your browser to: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("="*60)

    app.run(debug=True, host='0.0.0.0', port=5000)