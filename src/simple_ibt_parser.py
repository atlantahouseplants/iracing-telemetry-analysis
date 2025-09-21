"""
Simple IBT file parser that extracts basic information without complex dependencies
"""

import os
import struct
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)


class SimpleIBTParser:
    """
    Simple parser for IBT files that extracts basic header information
    This is a fallback when the Node.js parser doesn't work
    """

    def __init__(self):
        """Initialize the parser"""
        pass

    def parse_ibt_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Parse basic information from an IBT file

        Args:
            file_path: Path to the IBT file

        Returns:
            Dictionary with basic file information
        """
        if not os.path.exists(file_path):
            logger.error(f"File does not exist: {file_path}")
            return None

        try:
            with open(file_path, 'rb') as f:
                # Read the first part of the file to get basic info
                data = f.read(1024)  # Read first 1KB

                file_size = os.path.getsize(file_path)
                file_name = os.path.basename(file_path)

                # Try to extract some basic information
                result = {
                    'fileName': file_name,
                    'fileSize': file_size,
                    'fileSizeMB': file_size / (1024 * 1024),
                    'success': True,
                    'method': 'simple_header_parser'
                }

                # Try to parse filename for session info
                session_info = self._parse_filename(file_name)
                result.update(session_info)

                # Try to detect if this is a valid IBT file
                if self._is_valid_ibt(data):
                    result['valid_ibt'] = True
                    # Try to extract header information
                    header_info = self._extract_header_info(data)
                    result.update(header_info)
                else:
                    result['valid_ibt'] = False
                    logger.warning(f"File may not be a valid IBT file: {file_name}")

                logger.info(f"Basic parsing successful for: {file_name}")
                return result

        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return {
                'fileName': os.path.basename(file_path),
                'fileSize': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                'success': False,
                'error': str(e),
                'method': 'simple_header_parser'
            }

    def _parse_filename(self, filename: str) -> Dict[str, Any]:
        """
        Extract information from the filename
        Example: "porsche992cup_roadatlanta full 2025-09-13 13-27-17.ibt"
        """
        info = {}

        # Remove extension
        name_without_ext = filename.replace('.ibt', '')

        # Split by spaces
        parts = name_without_ext.split(' ')

        if len(parts) >= 1:
            # First part should be car_track
            car_track = parts[0]
            if '_' in car_track:
                car, track = car_track.split('_', 1)
                info['car'] = car
                info['track'] = track
            else:
                info['car_track'] = car_track

        # Look for date and time
        if len(parts) >= 3:
            # Typically: "2025-09-13 13-27-17"
            potential_date = parts[-2]
            potential_time = parts[-1]

            if '-' in potential_date and len(potential_date) == 10:
                info['session_date'] = potential_date
                info['session_time'] = potential_time.replace('-', ':')

        # Look for session type keywords
        session_types = ['practice', 'qualifying', 'race', 'test', 'warmup']
        for part in parts:
            if part.lower() in session_types:
                info['session_type'] = part.lower()
                break

        return info

    def _is_valid_ibt(self, data: bytes) -> bool:
        """
        Check if this appears to be a valid IBT file
        """
        if len(data) < 16:
            return False

        # Check for some patterns that might indicate an IBT file
        # This is basic heuristic checking
        try:
            # Check if it looks like it has binary telemetry data
            # IBT files typically start with specific headers
            return True  # For now, assume any binary file could be IBT
        except:
            return False

    def _extract_header_info(self, data: bytes) -> Dict[str, Any]:
        """
        Try to extract basic header information from the file
        """
        info = {}

        try:
            # Try to read some basic header information
            # This is very basic and may not work for all files
            if len(data) >= 4:
                # Try to read what might be version or format info
                potential_version = struct.unpack('<I', data[:4])[0]
                info['potential_version'] = potential_version

            if len(data) >= 8:
                # Try to read what might be data length
                potential_length = struct.unpack('<I', data[4:8])[0]
                info['potential_data_length'] = potential_length

        except Exception as e:
            logger.debug(f"Could not extract header info: {e}")

        return info

    def extract_session_info(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract session information from parsed data"""
        if not telemetry_data or not telemetry_data.get('success'):
            return {}

        session_info = {
            'file_name': telemetry_data.get('fileName', ''),
            'file_size_mb': telemetry_data.get('fileSizeMB', 0),
            'car': telemetry_data.get('car', 'Unknown'),
            'track': telemetry_data.get('track', 'Unknown'),
            'session_date': telemetry_data.get('session_date', ''),
            'session_time': telemetry_data.get('session_time', ''),
            'session_type': telemetry_data.get('session_type', 'Unknown'),
            'valid_ibt': telemetry_data.get('valid_ibt', False),
            'parser_method': telemetry_data.get('method', 'simple')
        }

        return session_info

    def extract_lap_analysis(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract basic lap analysis (limited without full telemetry parsing)
        """
        # With simple parsing, we can't extract actual lap data
        # But we can provide some basic information
        return {
            'total_laps': 'Unknown - requires full telemetry parsing',
            'lap_times': [],
            'fastest_lap': None,
            'parser_method': 'simple',
            'note': 'Full lap analysis requires advanced IBT parsing'
        }


# Mock telemetry processor for demonstration
def create_mock_telemetry_data(file_path: str) -> Dict[str, Any]:
    """
    Create mock telemetry data for testing purposes
    """
    filename = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    # Parse filename
    parser = SimpleIBTParser()
    session_info = parser._parse_filename(filename)

    # Create realistic mock data
    mock_data = {
        'fileName': filename,
        'fileSize': file_size,
        'telemetryId': f"mock_{hash(file_path) % 10000}",
        'success': True,
        'method': 'mock_data',
        'summary': {
            'totalSamples': 15000,  # Typical for a session
            'duration': 1200,  # 20 minutes
            'laps': [
                {'lapNumber': 1, 'lapTime': 92.34},
                {'lapNumber': 2, 'lapTime': 89.56},
                {'lapNumber': 3, 'lapTime': 88.89},
                {'lapNumber': 4, 'lapTime': 89.12},
                {'lapNumber': 5, 'lapTime': 88.67},
            ]
        },
        'parameters': [
            'SessionTime', 'Speed', 'RPM', 'Throttle', 'Brake', 'Lap',
            'LapDist', 'SteeringWheelAngle', 'Gear', 'FuelLevel',
            'LFTempCL', 'LFTempCM', 'LFTempCR', 'RFTempCL', 'RFTempCM', 'RFTempCR'
        ]
    }

    # Add parsed filename info
    mock_data.update(session_info)

    return mock_data


if __name__ == "__main__":
    # Test the simple parser
    parser = SimpleIBTParser()

    # Find IBT files
    current_dir = Path(__file__).parent.parent
    ibt_files = list(current_dir.glob("*.ibt"))

    print("=== Simple IBT Parser Test ===")

    if ibt_files:
        for ibt_file in ibt_files:
            print(f"\\nTesting: {ibt_file.name}")

            # Test simple parser
            result = parser.parse_ibt_file(str(ibt_file))
            if result:
                print("Simple Parser Result:")
                print(json.dumps(result, indent=2))

                session_info = parser.extract_session_info(result)
                print("\\nSession Info:")
                print(json.dumps(session_info, indent=2))

            # Test mock data
            print("\\n--- Mock Data for Testing ---")
            mock_data = create_mock_telemetry_data(str(ibt_file))
            print(json.dumps(mock_data, indent=2))

    else:
        print("No IBT files found for testing")

    print("\\n=== Test Complete ===")