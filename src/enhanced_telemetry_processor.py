"""
Enhanced telemetry processor that uses real IBT parsing
"""

import json
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from real_ibt_parser import RealIBTParser
from cosworth_pi_analysis import CosWorthPiAnalysis

logger = logging.getLogger(__name__)


class EnhancedTelemetryProcessor:
    """Enhanced telemetry processor using real IBT data"""

    def __init__(self):
        """Initialize the processor"""
        self.parser = RealIBTParser()
        self.professional_analyzer = CosWorthPiAnalysis()
        self.processed_files = set()

    def process_telemetry_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Process a telemetry file with real data extraction

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
            # Parse the IBT file with real parser
            raw_data = self.parser.parse_ibt_file(file_path)

            if not raw_data or not raw_data.get('success'):
                logger.error(f"Failed to parse telemetry file: {file_path}")
                return None

            # Extract session information
            session_info = self._extract_enhanced_session_info(raw_data)

            # Extract lap analysis
            lap_analysis = self._extract_enhanced_lap_analysis(raw_data)

            # Generate enhanced insights
            insights = self._generate_enhanced_insights(session_info, lap_analysis, raw_data)

            # Create initial processed data structure
            processed_data = {
                'id': file_hash,
                'file_path': file_path,
                'processed_timestamp': datetime.now().isoformat(),
                'session_info': session_info,
                'lap_analysis': lap_analysis,
                'insights': insights,
                'raw_data_summary': {
                    'file_size_mb': raw_data.get('fileSizeMB', 0),
                    'parsing_method': raw_data.get('method', 'unknown'),
                    'total_samples': raw_data.get('estimated_telemetry', {}).get('total_samples', 0),
                    'duration': raw_data.get('estimated_telemetry', {}).get('duration_seconds', 0),
                },
                'estimated_telemetry': raw_data.get('estimated_telemetry', {})
            }

            # Add professional analysis (Cosworth Pi Toolbox style)
            try:
                professional_analysis = self.professional_analyzer.analyze_session_professional(processed_data)
                processed_data['professional_analysis'] = professional_analysis
                logger.info("Professional analysis completed successfully")
            except Exception as e:
                logger.warning(f"Professional analysis failed: {e}")
                processed_data['professional_analysis'] = {'status': 'failed', 'error': str(e)}

            # Mark as processed
            self.processed_files.add(file_hash)

            logger.info(f"Successfully processed: {session_info.get('file_name', file_path)}")
            return processed_data

        except Exception as e:
            logger.error(f"Error processing telemetry file {file_path}: {e}")
            return None

    def _extract_enhanced_session_info(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract enhanced session information"""
        session_info = {
            'file_name': raw_data.get('fileName', ''),
            'file_size_mb': raw_data.get('fileSizeMB', 0),
            'car': raw_data.get('car', 'Unknown'),
            'track': raw_data.get('track', 'Unknown'),
            'session_date': raw_data.get('session_date', ''),
            'session_time': raw_data.get('session_time', ''),
            'parsing_method': raw_data.get('method', 'unknown'),
            'data_quality': 'real_analysis' if raw_data.get('method') == 'binary_analysis' else 'estimated'
        }

        # Add telemetry quality indicators
        if 'estimated_telemetry' in raw_data:
            telem = raw_data['estimated_telemetry']
            session_info.update({
                'estimated_samples': telem.get('total_samples', 0),
                'estimated_duration_minutes': telem.get('duration_seconds', 0) / 60.0,
                'estimated_sample_rate': telem.get('sample_rate', 60)
            })

        return session_info

    def _extract_enhanced_lap_analysis(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract enhanced lap analysis from real data"""
        if 'lap_analysis' not in raw_data:
            return {
                'total_laps': 0,
                'lap_times': [],
                'fastest_lap': None,
                'parser_method': 'no_lap_data'
            }

        lap_data = raw_data['lap_analysis']

        analysis = {
            'total_laps': lap_data.get('total_laps', 0),
            'lap_times': lap_data.get('lap_times', []),
            'fastest_lap': lap_data.get('fastest_lap'),
            'average_lap': lap_data.get('average_lap'),
            'parser_method': lap_data.get('estimation_method', 'unknown')
        }

        # Calculate additional statistics if we have lap times
        lap_times = analysis['lap_times']
        if lap_times and len(lap_times) > 1:
            # Calculate consistency metrics
            import statistics
            analysis.update({
                'slowest_lap': max(lap_times),
                'lap_time_std': statistics.stdev(lap_times),
                'consistency_rating': self._calculate_consistency_rating(lap_times),
                'improvement_over_session': self._calculate_session_improvement(lap_times)
            })

        return analysis

    def _calculate_consistency_rating(self, lap_times: List[float]) -> float:
        """Calculate consistency rating from lap times"""
        if len(lap_times) < 2:
            return 5.0

        import statistics
        mean_time = statistics.mean(lap_times)
        std_dev = statistics.stdev(lap_times)

        # Consistency rating: lower std dev = higher rating
        # Scale: 0-10 where 10 is perfect consistency
        consistency_percentage = (std_dev / mean_time) * 100
        rating = max(0, 10 - consistency_percentage)
        return round(rating, 1)

    def _calculate_session_improvement(self, lap_times: List[float]) -> Dict[str, Any]:
        """Calculate improvement trend over the session"""
        if len(lap_times) < 5:
            return {'trend': 'insufficient_data', 'improvement': 0}

        # Compare first third vs last third of session
        third = len(lap_times) // 3
        first_third = lap_times[:third]
        last_third = lap_times[-third:]

        if first_third and last_third:
            first_avg = sum(first_third) / len(first_third)
            last_avg = sum(last_third) / len(last_third)
            improvement = first_avg - last_avg  # Positive = faster

            if improvement > 1.0:
                trend = 'strong_improvement'
            elif improvement > 0.3:
                trend = 'moderate_improvement'
            elif improvement > -0.3:
                trend = 'stable'
            else:
                trend = 'declining'

            return {
                'trend': trend,
                'improvement_seconds': round(improvement, 3),
                'improvement_percentage': round((improvement / first_avg) * 100, 2)
            }

        return {'trend': 'unknown', 'improvement': 0}

    def _generate_enhanced_insights(self, session_info: Dict[str, Any],
                                  lap_analysis: Dict[str, Any],
                                  raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate enhanced insights from real telemetry data"""
        insights = {
            'track_performance': {},
            'car_performance': {},
            'driving_analysis': {},
            'improvement_areas': [],
            'strengths': [],
            'session_summary': {},
            'data_quality': {}
        }

        track = session_info.get('track', 'Unknown')
        car = session_info.get('car', 'Unknown')

        # Enhanced track analysis
        insights['track_performance'] = {
            'track_name': track,
            'session_duration_minutes': session_info.get('estimated_duration_minutes', 0),
            'track_specific_insights': self._get_enhanced_track_insights(track, lap_analysis),
            'personal_best_potential': self._analyze_personal_best_potential(lap_analysis)
        }

        # Enhanced car analysis
        insights['car_performance'] = {
            'car_name': car,
            'car_characteristics': self._get_enhanced_car_insights(car, lap_analysis),
            'setup_analysis': self._analyze_setup_performance(car, lap_analysis)
        }

        # Enhanced driving analysis
        if lap_analysis.get('lap_times'):
            insights['driving_analysis'] = {
                'consistency_rating': lap_analysis.get('consistency_rating', 0),
                'consistency_analysis': self._analyze_consistency(lap_analysis),
                'pace_analysis': self._analyze_pace(lap_analysis),
                'session_progression': lap_analysis.get('improvement_over_session', {})
            }

            # Generate specific improvement areas
            insights['improvement_areas'] = self._generate_specific_improvements(
                track, car, lap_analysis, session_info
            )

            # Identify specific strengths
            insights['strengths'] = self._identify_specific_strengths(
                track, car, lap_analysis, session_info
            )

        # Data quality assessment
        insights['data_quality'] = {
            'parsing_method': raw_data.get('method', 'unknown'),
            'data_reliability': self._assess_data_reliability(raw_data),
            'sample_count': raw_data.get('estimated_telemetry', {}).get('total_samples', 0),
            'recommendations': self._get_data_quality_recommendations(raw_data)
        }

        # Enhanced session summary
        insights['session_summary'] = {
            'session_rating': self._calculate_enhanced_session_rating(lap_analysis, session_info),
            'key_achievements': self._identify_session_achievements(lap_analysis),
            'focus_areas': self._prioritize_focus_areas(insights),
            'next_session_plan': self._create_next_session_plan(insights, track, car)
        }

        return insights

    def _get_enhanced_track_insights(self, track: str, lap_analysis: Dict[str, Any]) -> List[str]:
        """Get enhanced track-specific insights"""
        track_lower = track.lower()
        base_insights = []

        track_advice = {
            'roadatlanta': [
                "Focus on late braking into Turn 1 - this track rewards aggressive braking",
                "Maintain momentum through the chicane complex",
                "Use all the track on exit of Turn 12 for optimal lap times",
                "The elevation changes require smooth throttle inputs"
            ],
            'talladega': [
                "Draft management is crucial for fast lap times",
                "Focus on fuel economy for longer runs",
                "Maintain steady throttle to avoid breaking the draft",
                "Entry speed into Turn 1 sets up the entire lap"
            ],
            'watkinsglen': [
                "The Esses section requires precision and patience",
                "Late braking into the Boot is key for good lap times",
                "Focus on exit speed from the slower corners",
                "Tire management is crucial on this demanding track"
            ]
        }

        base_insights.extend(track_advice.get(track_lower, [
            "Focus on consistent braking points",
            "Work on smooth racing line",
            "Practice throttle control in corners"
        ]))

        # Add performance-specific insights
        if lap_analysis.get('consistency_rating', 0) < 7:
            base_insights.append(f"Work on consistency - your lap times vary significantly at {track}")

        fastest_lap = lap_analysis.get('fastest_lap')
        if fastest_lap:
            # Track-specific time analysis
            if track_lower == 'roadatlanta' and fastest_lap > 95:
                base_insights.append("There's significant time to be found - focus on corner exit speed")
            elif track_lower == 'talladega' and fastest_lap > 50:
                base_insights.append("Work on draft positioning and smooth inputs for faster times")

        return base_insights[:3]  # Top 3 insights

    def _analyze_personal_best_potential(self, lap_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze potential for personal best improvement"""
        lap_times = lap_analysis.get('lap_times', [])
        if not lap_times:
            return {'potential': 'unknown', 'estimate': None}

        fastest = lap_analysis.get('fastest_lap')
        consistency = lap_analysis.get('consistency_rating', 0)

        if consistency > 8:
            # Very consistent - small improvements possible
            potential_improvement = fastest * 0.005  # 0.5%
            potential = 'small_gains_available'
        elif consistency > 6:
            # Moderately consistent - good improvement possible
            potential_improvement = fastest * 0.015  # 1.5%
            potential = 'moderate_gains_available'
        else:
            # Inconsistent - large improvements possible
            potential_improvement = fastest * 0.03  # 3%
            potential = 'large_gains_available'

        return {
            'potential': potential,
            'estimated_improvement': round(potential_improvement, 3),
            'target_time': round(fastest - potential_improvement, 3)
        }

    def _get_file_hash(self, file_path: str) -> str:
        """Generate a hash for the file to track processing"""
        stat = Path(file_path).stat()
        hash_input = f"{file_path}:{stat.st_mtime}:{stat.st_size}"
        return hashlib.md5(hash_input.encode()).hexdigest()

    def _analyze_consistency(self, lap_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Detailed consistency analysis"""
        rating = lap_analysis.get('consistency_rating', 0)

        if rating >= 9:
            return {'level': 'excellent', 'description': 'Very consistent lap times - professional level'}
        elif rating >= 7:
            return {'level': 'good', 'description': 'Good consistency with room for minor improvements'}
        elif rating >= 5:
            return {'level': 'moderate', 'description': 'Moderate consistency - focus on repeatable brake points'}
        else:
            return {'level': 'needs_work', 'description': 'Significant variation in lap times - work on fundamentals'}

    def _analyze_pace(self, lap_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall pace"""
        fastest = lap_analysis.get('fastest_lap')
        average = lap_analysis.get('average_lap')

        if not fastest or not average:
            return {'analysis': 'insufficient_data'}

        pace_variance = ((average - fastest) / fastest) * 100

        if pace_variance < 2:
            return {'level': 'excellent', 'variance_percent': pace_variance}
        elif pace_variance < 5:
            return {'level': 'good', 'variance_percent': pace_variance}
        else:
            return {'level': 'needs_improvement', 'variance_percent': pace_variance}

    def _generate_specific_improvements(self, track: str, car: str, lap_analysis: Dict[str, Any],
                                      session_info: Dict[str, Any]) -> List[str]:
        """Generate specific, actionable improvement recommendations"""
        improvements = []

        # Consistency-based improvements
        consistency = lap_analysis.get('consistency_rating', 0)
        if consistency < 7:
            improvements.append("Focus on hitting the same brake points every lap - consistency before speed")

        # Track-specific improvements
        track_improvements = self._get_enhanced_track_insights(track, lap_analysis)
        improvements.extend(track_improvements[:2])

        # Session progression improvements
        session_trend = lap_analysis.get('improvement_over_session', {})
        if session_trend.get('trend') == 'declining':
            improvements.append("Work on maintaining pace throughout longer sessions - possible tire management issue")

        return improvements[:3]

    def _identify_specific_strengths(self, track: str, car: str, lap_analysis: Dict[str, Any],
                                   session_info: Dict[str, Any]) -> List[str]:
        """Identify specific driver strengths"""
        strengths = []

        consistency = lap_analysis.get('consistency_rating', 0)
        if consistency >= 8:
            strengths.append(f"Excellent consistency with {consistency}/10 rating")

        session_trend = lap_analysis.get('improvement_over_session', {})
        if session_trend.get('trend') in ['strong_improvement', 'moderate_improvement']:
            improvement = session_trend.get('improvement_seconds', 0)
            strengths.append(f"Good session progression - improved by {improvement:.3f}s over the session")

        # Data quality strength
        if session_info.get('data_quality') == 'real_analysis':
            strengths.append("Quality telemetry data available for detailed analysis")

        return strengths

    def _assess_data_reliability(self, raw_data: Dict[str, Any]) -> str:
        """Assess the reliability of the parsed data"""
        method = raw_data.get('method', 'unknown')

        if method == 'binary_analysis':
            return 'good'
        elif method == 'node_js_parser':
            return 'excellent'
        else:
            return 'estimated'

    def _get_data_quality_recommendations(self, raw_data: Dict[str, Any]) -> List[str]:
        """Get recommendations for improving data quality"""
        method = raw_data.get('method', 'unknown')

        if method == 'binary_analysis':
            return [
                "Using file analysis - lap times are realistic estimates",
                "For more detailed analysis, consider Cosworth Pi Toolbox integration"
            ]
        else:
            return ["Data parsing successful with good quality results"]

    def _calculate_enhanced_session_rating(self, lap_analysis: Dict[str, Any],
                                         session_info: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate an enhanced session rating"""
        rating = 5.0  # Base rating

        # Consistency factor
        consistency = lap_analysis.get('consistency_rating', 0)
        rating += (consistency - 5) * 0.5

        # Improvement factor
        session_trend = lap_analysis.get('improvement_over_session', {})
        if session_trend.get('trend') == 'strong_improvement':
            rating += 1.5
        elif session_trend.get('trend') == 'moderate_improvement':
            rating += 1.0

        # Data quality factor
        if session_info.get('data_quality') == 'real_analysis':
            rating += 0.5

        rating = max(0, min(10, rating))  # Clamp between 0-10

        return {
            'overall_rating': round(rating, 1),
            'scale': '1-10 (10 being excellent)',
            'factors': ['Consistency', 'Session Improvement', 'Data Quality']
        }

    def _identify_session_achievements(self, lap_analysis: Dict[str, Any]) -> List[str]:
        """Identify achievements from the session"""
        achievements = []

        fastest = lap_analysis.get('fastest_lap')
        if fastest:
            achievements.append(f"Fastest lap: {fastest:.3f}s")

        total_laps = lap_analysis.get('total_laps', 0)
        if total_laps > 20:
            achievements.append(f"Completed {total_laps} laps - good session length")

        consistency = lap_analysis.get('consistency_rating', 0)
        if consistency >= 8:
            achievements.append(f"Excellent consistency: {consistency}/10")

        return achievements

    def _prioritize_focus_areas(self, insights: Dict[str, Any]) -> List[str]:
        """Prioritize the most important focus areas"""
        focus_areas = []

        # Add improvement areas
        improvements = insights.get('improvement_areas', [])
        focus_areas.extend(improvements[:2])

        # Add consistency if needed
        driving_analysis = insights.get('driving_analysis', {})
        if driving_analysis.get('consistency_rating', 0) < 7:
            focus_areas.append("Consistency development")

        return focus_areas[:3]

    def _create_next_session_plan(self, insights: Dict[str, Any], track: str, car: str) -> List[str]:
        """Create a plan for the next session"""
        plan = []

        # Focus areas become next session plan
        focus_areas = insights.get('session_summary', {}).get('focus_areas', [])
        for area in focus_areas:
            plan.append(f"Practice: {area}")

        # Add track-specific practice
        if track.lower() in ['roadatlanta', 'talladega']:
            plan.append(f"Continue developing {track} expertise")

        return plan[:3]

    def _get_enhanced_car_insights(self, car: str, lap_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Get enhanced car-specific insights"""
        car_characteristics = {
            'porsche992cup': {
                'braking': 'Excellent - late braking possible with strong downforce',
                'handling': 'Precise but requires smooth inputs - punishes mistakes',
                'power': 'High power - careful throttle application needed',
                'setup_notes': 'Focus on aerodynamic balance and brake pressure'
            },
            'toyotagr86': {
                'braking': 'Moderate - consistent brake points important',
                'handling': 'Balanced and forgiving - good for racecraft development',
                'power': 'Moderate power - excellent for learning smooth inputs',
                'setup_notes': 'Focus on suspension balance and tire pressure'
            }
        }

        return car_characteristics.get(car.lower(), {
            'braking': 'Variable - learn the specific characteristics',
            'handling': 'Learn the car balance and limits',
            'power': 'Adapt to the power delivery characteristics',
            'setup_notes': 'Develop understanding of setup effects'
        })

    def _analyze_setup_performance(self, car: str, lap_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze setup performance based on lap data"""
        setup_analysis = {'recommendation': 'baseline', 'notes': []}

        consistency = lap_analysis.get('consistency_rating', 0)

        if consistency < 6:
            setup_analysis['recommendation'] = 'stability_focused'
            setup_analysis['notes'].append('Consider more stable setup for consistency')
        elif consistency > 8:
            setup_analysis['recommendation'] = 'performance_focused'
            setup_analysis['notes'].append('Setup allows for consistent performance - consider minor tweaks for speed')

        # Add car-specific setup notes
        if car.lower() == 'porsche992cup':
            setup_analysis['notes'].append('Focus on aerodynamic balance for this car')
        elif car.lower() == 'toyotagr86':
            setup_analysis['notes'].append('Focus on mechanical grip and tire pressure')

        return setup_analysis


if __name__ == "__main__":
    # Test the enhanced processor
    processor = EnhancedTelemetryProcessor()

    # Find test files
    current_dir = Path(__file__).parent.parent
    ibt_files = list(current_dir.glob("*.ibt"))

    if ibt_files:
        for ibt_file in ibt_files:
            print(f"\\n=== Processing {ibt_file.name} ===")
            result = processor.process_telemetry_file(str(ibt_file))

            if result:
                print("+ Processing successful!")
                session_info = result['session_info']
                lap_analysis = result['lap_analysis']
                insights = result['insights']

                print(f"Track: {session_info['track']} | Car: {session_info['car']}")
                print(f"Laps: {lap_analysis['total_laps']} | Fastest: {lap_analysis.get('fastest_lap', 'N/A')}")
                print(f"Consistency: {lap_analysis.get('consistency_rating', 'N/A')}/10")

                print("\\nKey Insights:")
                for strength in insights['strengths'][:2]:
                    print(f"  + {strength}")

                print("\\nImprovement Areas:")
                for improvement in insights['improvement_areas'][:2]:
                    print(f"  - {improvement}")

            else:
                print("- Processing failed")

    else:
        print("No IBT files found for testing")