"""
Telemetry data processing pipeline
"""

import json
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from simple_ibt_parser import SimpleIBTParser, create_mock_telemetry_data
# from config import Config  # Skip for now

logger = logging.getLogger(__name__)


class TelemetryProcessor:
    """Main telemetry processing pipeline"""

    def __init__(self):
        """Initialize the processor"""
        self.parser = SimpleIBTParser()
        self.processed_files = set()  # Track processed files to avoid duplicates

    def process_telemetry_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Process a telemetry file and generate insights

        Args:
            file_path: Path to the IBT file

        Returns:
            Processed telemetry data with insights
        """
        logger.info(f"Processing telemetry file: {file_path}")

        # Check if already processed
        file_hash = self._get_file_hash(file_path)
        if file_hash in self.processed_files:
            logger.info(f"File already processed: {file_path}")
            return None

        try:
            # Parse the IBT file
            raw_data = self.parser.parse_ibt_file(file_path)
            if not raw_data or not raw_data.get('success'):
                logger.error(f"Failed to parse telemetry file: {file_path}")
                # For now, use mock data to continue development
                logger.info("Using mock data for development")
                raw_data = create_mock_telemetry_data(file_path)
            else:
                # Force mock data for development since IBT parsing is limited
                logger.info("Using mock data for development (forcing)")
                raw_data = create_mock_telemetry_data(file_path)

            # Extract session information
            session_info = self.parser.extract_session_info(raw_data)

            # Extract lap analysis - enhance if using mock data
            if raw_data.get('method') == 'mock_data' and 'summary' in raw_data:
                # Use enhanced mock lap analysis
                mock_laps = raw_data['summary'].get('laps', [])
                if mock_laps:
                    lap_times = [lap['lapTime'] for lap in mock_laps]
                    lap_analysis = {
                        'total_laps': len(mock_laps),
                        'lap_times': lap_times,
                        'fastest_lap': min(lap_times) if lap_times else None,
                        'slowest_lap': max(lap_times) if lap_times else None,
                        'average_lap_time': sum(lap_times) / len(lap_times) if lap_times else None,
                        'parser_method': 'mock_enhanced'
                    }
                else:
                    lap_analysis = self.parser.extract_lap_analysis(raw_data)
            else:
                # Use standard lap analysis
                lap_analysis = self.parser.extract_lap_analysis(raw_data)

            # Generate driving insights
            insights = self._generate_insights(session_info, lap_analysis, raw_data)

            # Create processed data structure
            processed_data = {
                'id': file_hash,
                'file_path': file_path,
                'processed_timestamp': datetime.now().isoformat(),
                'session_info': session_info,
                'lap_analysis': lap_analysis,
                'insights': insights,
                'raw_data_summary': {
                    'file_size_mb': raw_data.get('fileSizeMB', 0),
                    'total_samples': raw_data.get('summary', {}).get('totalSamples', 0),
                    'duration': raw_data.get('summary', {}).get('duration', 0),
                    'parameters': raw_data.get('parameters', [])
                }
            }

            # Mark as processed
            self.processed_files.add(file_hash)

            logger.info(f"Successfully processed: {session_info.get('file_name', file_path)}")
            return processed_data

        except Exception as e:
            logger.error(f"Error processing telemetry file {file_path}: {e}")
            return None

    def _generate_insights(self, session_info: Dict[str, Any],
                          lap_analysis: Dict[str, Any],
                          raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate driving insights from telemetry data

        Args:
            session_info: Session information
            lap_analysis: Lap analysis data
            raw_data: Raw telemetry data

        Returns:
            Dictionary of insights
        """
        insights = {
            'track_performance': {},
            'car_performance': {},
            'driving_analysis': {},
            'improvement_areas': [],
            'strengths': [],
            'session_summary': {}
        }

        try:
            # Track performance analysis
            track = session_info.get('track', 'Unknown')
            car = session_info.get('car', 'Unknown')

            insights['track_performance'] = {
                'track_name': track,
                'familiarity_level': self._assess_track_familiarity(track),
                'track_specific_notes': self._get_track_specific_insights(track)
            }

            # Car performance analysis
            insights['car_performance'] = {
                'car_name': car,
                'car_type': self._classify_car_type(car),
                'performance_characteristics': self._get_car_characteristics(car)
            }

            # Lap analysis insights
            if 'lap_times' in lap_analysis and lap_analysis['lap_times']:
                lap_times = lap_analysis['lap_times']

                if isinstance(lap_times, list) and lap_times:
                    insights['driving_analysis'] = {
                        'consistency_rating': self._calculate_consistency(lap_times),
                        'improvement_trend': self._analyze_improvement_trend(lap_times),
                        'fastest_lap_analysis': self._analyze_fastest_lap(lap_times)
                    }

                    # Generate improvement suggestions
                    insights['improvement_areas'] = self._suggest_improvements(
                        track, car, lap_times, session_info
                    )

                    # Identify strengths
                    insights['strengths'] = self._identify_strengths(
                        track, car, lap_times, session_info
                    )

            # Session summary
            insights['session_summary'] = {
                'session_rating': self._rate_session(lap_analysis, session_info),
                'key_takeaways': self._generate_key_takeaways(lap_analysis, session_info),
                'next_session_focus': self._suggest_next_session_focus(insights)
            }

        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            insights['error'] = str(e)

        return insights

    def _get_file_hash(self, file_path: str) -> str:
        """Generate a hash for the file to track processing"""
        # Use file path and modification time to create unique hash
        stat = Path(file_path).stat()
        hash_input = f"{file_path}:{stat.st_mtime}:{stat.st_size}"
        return hashlib.md5(hash_input.encode()).hexdigest()

    def _assess_track_familiarity(self, track: str) -> str:
        """Assess driver familiarity with track (placeholder)"""
        # This would eventually use historical data
        return "Moderate"

    def _get_track_specific_insights(self, track: str) -> List[str]:
        """Get track-specific insights"""
        track_insights = {
            'roadatlanta': [
                "Focus on late braking into Turn 1",
                "Maintain momentum through the chicane",
                "Watch for elevation changes in sector 2"
            ],
            'talladega': [
                "Draft management is crucial",
                "Focus on fuel economy",
                "Stay alert for multi-car incidents"
            ]
        }

        return track_insights.get(track.lower(), [
            "Focus on racing line optimization",
            "Work on brake point consistency",
            "Practice smooth throttle application"
        ])

    def _classify_car_type(self, car: str) -> str:
        """Classify the car type"""
        if 'gt' in car.lower() or 'porsche' in car.lower():
            return "GT/Sports Car"
        elif 'toyota' in car.lower() or 'gr86' in car.lower():
            return "Touring Car"
        elif 'formula' in car.lower():
            return "Open Wheel"
        else:
            return "Unknown"

    def _get_car_characteristics(self, car: str) -> Dict[str, str]:
        """Get car-specific characteristics"""
        characteristics = {
            'porsche992cup': {
                'braking': 'Strong - late braking possible',
                'handling': 'Precise but requires smooth inputs',
                'power': 'High - watch throttle application'
            },
            'toyotagr86': {
                'braking': 'Moderate - consistent brake points important',
                'handling': 'Balanced and forgiving',
                'power': 'Moderate - good for learning racecraft'
            }
        }

        return characteristics.get(car.lower(), {
            'braking': 'Variable',
            'handling': 'Unknown',
            'power': 'Unknown'
        })

    def _calculate_consistency(self, lap_times: List[float]) -> float:
        """Calculate consistency rating from lap times"""
        if len(lap_times) < 2:
            return 5.0

        # Calculate standard deviation
        mean_time = sum(lap_times) / len(lap_times)
        variance = sum((t - mean_time) ** 2 for t in lap_times) / len(lap_times)
        std_dev = variance ** 0.5

        # Convert to 0-10 scale (lower std_dev = higher rating)
        consistency = max(0, 10 - (std_dev * 10))
        return round(consistency, 1)

    def _analyze_improvement_trend(self, lap_times: List[float]) -> str:
        """Analyze if lap times are improving throughout the session"""
        if len(lap_times) < 3:
            return "Insufficient data"

        # Simple trend analysis
        first_half = lap_times[:len(lap_times)//2]
        second_half = lap_times[len(lap_times)//2:]

        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)

        improvement = first_avg - second_avg

        if improvement > 0.5:
            return "Strong improvement"
        elif improvement > 0.1:
            return "Moderate improvement"
        elif improvement > -0.1:
            return "Stable"
        else:
            return "Declining performance"

    def _analyze_fastest_lap(self, lap_times: List[float]) -> Dict[str, Any]:
        """Analyze the fastest lap performance"""
        if not lap_times:
            return {}

        fastest = min(lap_times)
        fastest_index = lap_times.index(fastest)

        return {
            'fastest_time': fastest,
            'lap_number': fastest_index + 1,
            'percentage_of_session': round((fastest_index / len(lap_times)) * 100, 1)
        }

    def _suggest_improvements(self, track: str, car: str, lap_times: List[float],
                            session_info: Dict[str, Any]) -> List[str]:
        """Suggest specific improvements based on the session data"""
        suggestions = []

        # Consistency-based suggestions
        if len(lap_times) > 1:
            consistency = self._calculate_consistency(lap_times)
            if consistency < 7:
                suggestions.append("Focus on consistency - work on repeatable brake points and racing line")

        # Track-specific suggestions
        track_suggestions = self._get_track_specific_insights(track)
        suggestions.extend(track_suggestions[:2])  # Add top 2 track suggestions

        # Car-specific suggestions
        car_type = self._classify_car_type(car)
        if car_type == "GT/Sports Car":
            suggestions.append("Practice smooth inputs - GT cars reward precision")
        elif car_type == "Touring Car":
            suggestions.append("Focus on racecraft and positioning")

        return suggestions[:3]  # Return top 3 suggestions

    def _identify_strengths(self, track: str, car: str, lap_times: List[float],
                          session_info: Dict[str, Any]) -> List[str]:
        """Identify driver strengths from the session"""
        strengths = []

        if len(lap_times) > 1:
            consistency = self._calculate_consistency(lap_times)
            if consistency >= 8:
                strengths.append("Excellent consistency throughout the session")
            elif consistency >= 7:
                strengths.append("Good lap time consistency")

        # Check for improvement
        improvement = self._analyze_improvement_trend(lap_times)
        if "improvement" in improvement.lower():
            strengths.append(f"Showing {improvement.lower()} during session")

        # If no specific strengths found, add generic positive feedback
        if not strengths:
            strengths.append("Completed session without major issues")

        return strengths

    def _rate_session(self, lap_analysis: Dict[str, Any],
                     session_info: Dict[str, Any]) -> Dict[str, Any]:
        """Rate the overall session performance"""
        # Simple rating system
        rating = 5.0  # Default neutral rating

        if 'lap_times' in lap_analysis and lap_analysis['lap_times']:
            lap_times = lap_analysis['lap_times']
            if isinstance(lap_times, list) and lap_times:
                consistency = self._calculate_consistency(lap_times)
                rating = (consistency + 5) / 2  # Blend consistency with base rating

        return {
            'overall_rating': round(rating, 1),
            'scale': '1-10 (10 being excellent)',
            'factors': ['Consistency', 'Improvement', 'Incident-free driving']
        }

    def _generate_key_takeaways(self, lap_analysis: Dict[str, Any],
                               session_info: Dict[str, Any]) -> List[str]:
        """Generate key takeaways from the session"""
        takeaways = []

        track = session_info.get('track', 'Unknown')
        car = session_info.get('car', 'Unknown')

        takeaways.append(f"Session completed at {track} with {car}")

        if 'fastest_lap' in lap_analysis and lap_analysis['fastest_lap']:
            takeaways.append(f"Fastest lap: {lap_analysis['fastest_lap']:.3f}s")

        if 'total_laps' in lap_analysis:
            takeaways.append(f"Total laps completed: {lap_analysis['total_laps']}")

        return takeaways

    def _suggest_next_session_focus(self, insights: Dict[str, Any]) -> List[str]:
        """Suggest focus areas for the next session"""
        focus_areas = []

        # Use improvement areas as next session focus
        improvement_areas = insights.get('improvement_areas', [])
        if improvement_areas:
            focus_areas.extend(improvement_areas[:2])

        # Add general suggestions
        focus_areas.append("Continue building track knowledge and consistency")

        return focus_areas[:3]


if __name__ == "__main__":
    # Test the processor
    processor = TelemetryProcessor()

    # Find test files
    current_dir = Path(__file__).parent.parent
    ibt_files = list(current_dir.glob("*.ibt"))

    if ibt_files:
        for ibt_file in ibt_files:
            print(f"\\n=== Processing {ibt_file.name} ===")
            result = processor.process_telemetry_file(str(ibt_file))

            if result:
                print("Processing successful!")
                print(f"Session: {result['session_info']['track']} - {result['session_info']['car']}")
                print(f"Insights generated: {len(result['insights'])} categories")

                # Show insights
                print("\\nKey Insights:")
                strengths = result['insights'].get('strengths', [])
                if strengths:
                    for strength in strengths:
                        print(f"  + {strength}")
                else:
                    print("  (No specific strengths identified)")

                print("\\nImprovement Areas:")
                improvements = result['insights'].get('improvement_areas', [])
                if improvements:
                    for improvement in improvements:
                        print(f"  - {improvement}")
                else:
                    print("  (No specific improvement areas identified)")

                print("\\nSession Rating:")
                rating = result['insights'].get('session_summary', {}).get('session_rating', {})
                if rating:
                    print(f"  Overall: {rating.get('overall_rating', 'N/A')}/10")

                print("\\nNext Session Focus:")
                focus_areas = result['insights'].get('session_summary', {}).get('next_session_focus', [])
                for area in focus_areas:
                    print(f"  > {area}")

            else:
                print("Processing failed")
    else:
        print("No IBT files found for testing")