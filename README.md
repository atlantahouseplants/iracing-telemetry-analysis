# iRacing Telemetry Analysis System

A comprehensive professional-grade telemetry analysis system for iRacing, providing advanced motorsport analytics and coaching insights.

## Features

### 🏁 Core Analytics
- **Real Telemetry Parsing** - Direct IBT file processing with enhanced telemetry extraction
- **Performance Analytics Dashboard** - Comprehensive performance metrics and trends
- **Interactive Charts & Visualizations** - Chart.js powered interactive data visualization
- **Professional Analysis** - Advanced coaching insights and recommendations

### 🔧 Advanced Systems
- **Car Setup Optimization** - Professional-grade setup analysis and recommendations
- **Race Strategy Planning** - Fuel consumption, tire wear, and pit strategy optimization
- **Multi-Driver Comparison** - Performance analysis between different drivers
- **Advanced Metrics** - G-force analysis, cornering speeds, and braking points

### 📊 Technical Capabilities
- **G-Force Analysis** - Lateral, longitudinal, and combined G-force metrics
- **Cornering Analysis** - Corner classification, speed analysis, and efficiency scoring
- **Braking Analysis** - Braking zones, deceleration rates, and consistency analysis
- **Performance Envelope** - Overall performance scoring with improvement recommendations

## Installation

### Prerequisites
- Python 3.8 or higher
- Flask
- NumPy
- ibtparser (for IBT file parsing)

### Setup
1. Clone the repository:
```bash
git clone https://github.com/[username]/iracing-telemetry-analysis.git
cd iracing-telemetry-analysis
```

2. Install dependencies:
```bash
pip install flask numpy ibtparser
```

3. Run the application:
```bash
cd src
python enhanced_web_ui.py
```

4. Open your browser to `http://localhost:5000`

## Usage

### Adding Telemetry Data
1. Place your iRacing IBT files in the root directory
2. The system automatically monitors and processes new files
3. Access the web interface for analysis

### Available Features
- **Analytics Dashboard** - Overview of performance metrics
- **Interactive Charts** - Detailed data visualizations
- **Setup Optimizer** - Car setup recommendations
- **Race Strategy** - Strategic planning tools
- **Driver Comparison** - Multi-driver performance analysis
- **Advanced Metrics** - Professional telemetry analysis

## System Architecture

### Core Components
- `enhanced_web_ui.py` - Main web application and API endpoints
- `enhanced_telemetry_processor.py` - IBT file processing and telemetry extraction
- `ai_coach_enhanced.py` - AI-powered coaching insights
- `performance_analytics.py` - Performance metrics and analytics engine

### Advanced Analysis Modules
- `setup_optimizer.py` - Car setup optimization algorithms
- `race_strategist.py` - Race strategy and fuel/tire analysis
- `driver_comparator.py` - Multi-driver comparison system
- `advanced_metrics.py` - G-force, cornering, and braking analysis

### Utilities
- `file_monitor.py` - Automatic file monitoring and processing
- `ibt_parser.py` - IBT file parsing utilities

## API Endpoints

- `/api/stats` - Session statistics
- `/api/professional-analysis` - Advanced coaching analysis
- `/api/analytics-dashboard` - Performance analytics data
- `/api/setup-optimizer` - Car setup recommendations
- `/api/race-strategy` - Race strategy analysis
- `/api/driver-comparison` - Multi-driver comparison
- `/api/advanced-metrics` - Advanced telemetry metrics

## Professional Features

### Setup Optimization
- Track-specific setup recommendations
- Aerodynamic balance analysis
- Suspension tuning suggestions
- Risk assessment and improvement estimation

### Race Strategy
- Fuel consumption modeling
- Tire wear simulation
- Pit strategy optimization
- Alternative strategy generation

### Advanced Metrics
- Professional motorsport benchmarks
- G-force envelope analysis
- Corner classification and optimization
- Braking performance assessment

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Guidelines
- Follow Python PEP 8 style guidelines
- Add comprehensive docstrings for new functions
- Include unit tests for new features
- Update documentation for API changes

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- iRacing for providing excellent telemetry data
- Professional motorsport techniques and algorithms
- Open source community for inspiration and tools

## Support

For support, please open an issue on GitHub or contact the development team.

---

**Professional-grade telemetry analysis for competitive sim racing**
