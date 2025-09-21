"""
iRacing IBT file parser using Node.js subprocess
"""

import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger(__name__)


class IBTParser:
    """Parser for iRacing IBT telemetry files"""

    def __init__(self):
        """Initialize the IBT parser"""
        self.node_script_path = None
        self._setup_node_parser()

    def _setup_node_parser(self):
        """Set up the Node.js parser script"""
        # Create a Node.js script that works around the regenerator runtime issue
        node_script_content = '''
const fs = require('fs');
const path = require('path');

// Polyfill for regeneratorRuntime
if (typeof regeneratorRuntime === 'undefined') {
    global.regeneratorRuntime = require('@babel/runtime/regenerator');
}

let Telemetry;
try {
    Telemetry = require('ibt-telemetry');
} catch (error) {
    console.error('Error loading ibt-telemetry:', error.message);
    process.exit(1);
}

async function parseIBTFile(filePath) {
    try {
        const telemetry = Telemetry.fromFile(filePath);

        const result = {
            fileName: path.basename(filePath),
            telemetryId: telemetry.uniqueId(),
            fileSize: fs.statSync(filePath).size,
            samples: [],
            parameters: [],
            summary: {
                totalSamples: 0,
                duration: 0,
                laps: []
            }
        };

        let sampleCount = 0;
        let firstSample = null;
        let lastSample = null;
        const sampleData = [];

        // Process samples (limit to reasonable number for initial analysis)
        for (const sample of telemetry.samples()) {
            const sampleJson = sample.toJSON();

            if (sampleCount === 0) {
                firstSample = sampleJson;
                result.parameters = Object.keys(sampleJson);
            }

            if (sampleCount < 1000) { // Store first 1000 samples for analysis
                sampleData.push(sampleJson);
            }

            lastSample = sampleJson;
            sampleCount++;

            // Break after reasonable number to avoid memory issues
            if (sampleCount > 50000) break;
        }

        result.samples = sampleData;
        result.summary.totalSamples = sampleCount;

        if (firstSample && lastSample && firstSample.SessionTime !== undefined && lastSample.SessionTime !== undefined) {
            result.summary.duration = lastSample.SessionTime - firstSample.SessionTime;
        }

        // Analyze laps
        const laps = new Map();
        let currentLap = -1;
        let lapStartTime = 0;

        sampleData.forEach(sample => {
            if (sample.Lap !== undefined && sample.Lap !== currentLap) {
                if (currentLap >= 0 && sample.SessionTime !== undefined) {
                    const lapTime = sample.SessionTime - lapStartTime;
                    laps.set(currentLap, lapTime);
                }
                currentLap = sample.Lap;
                lapStartTime = sample.SessionTime || 0;
            }
        });

        result.summary.laps = Array.from(laps.entries()).map(([lap, time]) => ({
            lapNumber: lap,
            lapTime: time
        }));

        return result;

    } catch (error) {
        throw new Error(`Failed to parse IBT file: ${error.message}`);
    }
}

// Main execution
async function main() {
    const filePath = process.argv[2];

    if (!filePath) {
        console.error('Usage: node ibt_parser.js <path_to_ibt_file>');
        process.exit(1);
    }

    if (!fs.existsSync(filePath)) {
        console.error(`File does not exist: ${filePath}`);
        process.exit(1);
    }

    try {
        const result = await parseIBTFile(filePath);
        console.log(JSON.stringify(result, null, 2));
    } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
    }
}

main().catch(error => {
    console.error('Unhandled error:', error);
    process.exit(1);
});
'''

        # Write the Node.js script to a temporary file
        script_dir = Path(__file__).parent.parent
        self.node_script_path = script_dir / 'ibt_parser_node.js'

        with open(self.node_script_path, 'w') as f:
            f.write(node_script_content)

        logger.info(f"Node.js parser script created at: {self.node_script_path}")

    def parse_ibt_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Parse an IBT file and return telemetry data

        Args:
            file_path: Path to the IBT file

        Returns:
            Dictionary containing telemetry data or None if parsing failed
        """
        if not os.path.exists(file_path):
            logger.error(f"IBT file does not exist: {file_path}")
            return None

        if not self.node_script_path or not os.path.exists(self.node_script_path):
            logger.error("Node.js parser script not found")
            return None

        try:
            logger.info(f"Parsing IBT file: {os.path.basename(file_path)}")

            # Run the Node.js parser
            result = subprocess.run(
                ['node', str(self.node_script_path), file_path],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=str(self.node_script_path.parent.parent)  # Run from project root where node_modules is
            )

            if result.returncode != 0:
                logger.error(f"Node.js parser failed with return code {result.returncode}")
                logger.error(f"stderr: {result.stderr}")
                return None

            # Parse the JSON output
            try:
                telemetry_data = json.loads(result.stdout)
                logger.info(f"Successfully parsed {os.path.basename(file_path)}")
                logger.info(f"  Samples: {telemetry_data.get('summary', {}).get('totalSamples', 0)}")
                logger.info(f"  Parameters: {len(telemetry_data.get('parameters', []))}")
                logger.info(f"  Duration: {telemetry_data.get('summary', {}).get('duration', 0):.1f}s")

                return telemetry_data

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON output: {e}")
                logger.error(f"stdout: {result.stdout}")
                return None

        except subprocess.TimeoutExpired:
            logger.error(f"Parsing timeout for file: {file_path}")
            return None

        except Exception as e:
            logger.error(f"Error parsing IBT file {file_path}: {e}")
            return None

    def extract_session_info(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract session information from telemetry data"""
        if not telemetry_data:
            return {}

        # Extract basic info
        session_info = {
            'file_name': telemetry_data.get('fileName', ''),
            'telemetry_id': telemetry_data.get('telemetryId', ''),
            'file_size_mb': telemetry_data.get('fileSize', 0) / (1024 * 1024),
            'total_samples': telemetry_data.get('summary', {}).get('totalSamples', 0),
            'duration_seconds': telemetry_data.get('summary', {}).get('duration', 0),
            'parameters': telemetry_data.get('parameters', [])
        }

        # Try to extract track and car info from filename
        filename = session_info['file_name']
        if filename:
            # Parse filename like "porsche992cup_roadatlanta full 2025-09-13 13-27-17.ibt"
            parts = filename.replace('.ibt', '').split(' ')
            if len(parts) >= 1:
                car_track = parts[0]
                if '_' in car_track:
                    car, track = car_track.split('_', 1)
                    session_info['car'] = car
                    session_info['track'] = track

                # Try to extract date/time
                if len(parts) >= 3:
                    try:
                        date_str = parts[-2]  # e.g., "2025-09-13"
                        time_str = parts[-1]  # e.g., "13-27-17"
                        session_info['session_date'] = date_str
                        session_info['session_time'] = time_str.replace('-', ':')
                    except:
                        pass

        return session_info

    def extract_lap_analysis(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract lap analysis from telemetry data"""
        if not telemetry_data or 'summary' not in telemetry_data:
            return {}

        laps = telemetry_data['summary'].get('laps', [])

        if not laps:
            return {'total_laps': 0, 'lap_times': [], 'fastest_lap': None}

        lap_times = [lap['lapTime'] for lap in laps if lap['lapTime'] > 0]

        analysis = {
            'total_laps': len(laps),
            'lap_times': lap_times,
            'fastest_lap': min(lap_times) if lap_times else None,
            'slowest_lap': max(lap_times) if lap_times else None,
            'average_lap_time': sum(lap_times) / len(lap_times) if lap_times else None
        }

        # Calculate consistency (standard deviation)
        if len(lap_times) > 1:
            import statistics
            analysis['lap_time_std'] = statistics.stdev(lap_times)
            analysis['consistency_rating'] = max(0, 10 - (analysis['lap_time_std'] * 10))

        return analysis


# Example usage and testing
if __name__ == "__main__":
    # Test the parser
    parser = IBTParser()

    # Test with existing files
    current_dir = Path(__file__).parent.parent
    ibt_files = list(current_dir.glob("*.ibt"))

    if ibt_files:
        for ibt_file in ibt_files:
            print(f"\\nTesting with: {ibt_file.name}")
            data = parser.parse_ibt_file(str(ibt_file))

            if data:
                session_info = parser.extract_session_info(data)
                lap_analysis = parser.extract_lap_analysis(data)

                print("Session Info:", json.dumps(session_info, indent=2))
                print("Lap Analysis:", json.dumps(lap_analysis, indent=2))
            else:
                print("Failed to parse file")
    else:
        print("No IBT files found for testing")