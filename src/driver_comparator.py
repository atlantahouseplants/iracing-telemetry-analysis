"""
Multi-Driver Comparison System
Advanced driver performance comparison and analysis
"""

import json
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class DriverComparator:
    """Advanced multi-driver comparison and analysis system"""

    def __init__(self, coach):
        """
        Initialize driver comparator

        Args:
            coach: Enhanced AI coach instance with session data
        """
        self.coach = coach
        self.driver_profiles = {}
        self._build_driver_profiles()

    def _build_driver_profiles(self):
        """Build driver profiles from session data"""
        # Group sessions by driver (based on unique characteristics)
        drivers = {}

        for session in self.coach.sessions:
            # Create a driver identifier based on session patterns
            driver_id = self._identify_driver(session)

            if driver_id not in drivers:
                drivers[driver_id] = {
                    'sessions': [],
                    'characteristics': {},
                    'performance_metrics': {}
                }

            drivers[driver_id]['sessions'].append(session)

        # Analyze each driver's characteristics
        for driver_id, driver_data in drivers.items():
            self.driver_profiles[driver_id] = self._analyze_driver_profile(driver_data['sessions'])

        logger.info(f"Built profiles for {len(self.driver_profiles)} drivers")

    def _identify_driver(self, session: Dict[str, Any]) -> str:
        """
        Identify driver based on session characteristics
        In real implementation, this could use session metadata, IP, user ID, etc.
        For now, we'll simulate different drivers based on performance patterns
        """
        session_info = session.get('session_info', {})
        lap_analysis = session.get('lap_analysis', {})

        # Get key performance indicators
        fastest_lap = lap_analysis.get('fastest_lap', 999)
        consistency = lap_analysis.get('consistency_rating', 5)
        car = session_info.get('car', 'unknown')

        # Create a simple driver classification based on performance
        if consistency >= 9.0:
            driver_type = "consistent_pro"
        elif fastest_lap < 45 and consistency >= 7.5:
            driver_type = "fast_driver"
        elif consistency >= 8.0:
            driver_type = "consistent_amateur"
        else:
            driver_type = "developing_driver"

        # For demonstration, we'll create unique drivers based on car + performance
        driver_id = f"{driver_type}_{car}_{abs(hash(str(fastest_lap + consistency))) % 1000}"

        return driver_id

    def _analyze_driver_profile(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze comprehensive driver profile"""
        profile = {
            'total_sessions': len(sessions),
            'performance_summary': {},
            'driving_characteristics': {},
            'track_specialties': {},
            'car_expertise': {},
            'consistency_profile': {},
            'improvement_trend': {},
            'strengths': [],
            'weaknesses': [],
            'driver_rating': 0.0
        }

        if not sessions:
            return profile

        # Collect performance data
        lap_times = []
        consistency_scores = []
        tracks = {}
        cars = {}

        for session in sessions:
            lap_analysis = session.get('lap_analysis', {})
            session_info = session.get('session_info', {})

            fastest_lap = lap_analysis.get('fastest_lap')
            consistency = lap_analysis.get('consistency_rating', 0)
            track = session_info.get('track', 'unknown')
            car = session_info.get('car', 'unknown')

            if fastest_lap:
                lap_times.append(fastest_lap)
            if consistency > 0:
                consistency_scores.append(consistency)

            # Track performance
            if track not in tracks:
                tracks[track] = {'times': [], 'consistencies': []}
            if fastest_lap:
                tracks[track]['times'].append(fastest_lap)
            if consistency > 0:
                tracks[track]['consistencies'].append(consistency)

            # Car performance
            if car not in cars:
                cars[car] = {'times': [], 'consistencies': []}
            if fastest_lap:
                cars[car]['times'].append(fastest_lap)
            if consistency > 0:
                cars[car]['consistencies'].append(consistency)

        # Performance summary
        if lap_times:
            profile['performance_summary'] = {
                'best_lap_time': min(lap_times),
                'average_lap_time': np.mean(lap_times),
                'worst_lap_time': max(lap_times),
                'lap_time_std': np.std(lap_times),
                'total_laps': sum(s.get('lap_analysis', {}).get('total_laps', 0) for s in sessions)
            }

        if consistency_scores:
            profile['consistency_profile'] = {
                'average_consistency': np.mean(consistency_scores),
                'best_consistency': max(consistency_scores),
                'worst_consistency': min(consistency_scores),
                'consistency_std': np.std(consistency_scores)
            }

        # Driving characteristics
        profile['driving_characteristics'] = self._analyze_driving_style(sessions)

        # Track specialties
        profile['track_specialties'] = self._analyze_track_specialties(tracks)

        # Car expertise
        profile['car_expertise'] = self._analyze_car_expertise(cars)

        # Improvement trend
        profile['improvement_trend'] = self._analyze_improvement_trend(sessions)

        # Strengths and weaknesses
        profile['strengths'], profile['weaknesses'] = self._identify_driver_characteristics(profile)

        # Overall driver rating
        profile['driver_rating'] = self._calculate_driver_rating(profile)

        return profile

    def compare_drivers(self, driver_ids: List[str] = None) -> Dict[str, Any]:
        """
        Compare multiple drivers across various metrics

        Args:
            driver_ids: List of driver IDs to compare (None for all drivers)

        Returns:
            Comprehensive comparison analysis
        """
        if driver_ids is None:
            driver_ids = list(self.driver_profiles.keys())

        if len(driver_ids) < 2:
            return {"error": "Need at least 2 drivers for comparison"}

        comparison = {
            'drivers_compared': driver_ids,
            'comparison_count': len(driver_ids),
            'performance_comparison': {},
            'consistency_comparison': {},
            'track_comparison': {},
            'car_comparison': {},
            'head_to_head': {},
            'rankings': {},
            'driver_insights': {},
            'recommendations': {},
            'generated_at': datetime.now().isoformat()
        }

        try:
            # Performance comparison
            comparison['performance_comparison'] = self._compare_performance(driver_ids)

            # Consistency comparison
            comparison['consistency_comparison'] = self._compare_consistency(driver_ids)

            # Track-specific comparison
            comparison['track_comparison'] = self._compare_track_performance(driver_ids)

            # Car-specific comparison
            comparison['car_comparison'] = self._compare_car_performance(driver_ids)

            # Head-to-head analysis
            comparison['head_to_head'] = self._head_to_head_analysis(driver_ids)

            # Rankings
            comparison['rankings'] = self._generate_rankings(driver_ids)

            # Driver insights
            comparison['driver_insights'] = self._generate_driver_insights(driver_ids)

            # Recommendations
            comparison['recommendations'] = self._generate_comparison_recommendations(comparison)

            logger.info(f"Generated comparison for {len(driver_ids)} drivers")

        except Exception as e:
            logger.error(f"Error in driver comparison: {e}")
            comparison['error'] = str(e)

        return comparison

    def _compare_performance(self, driver_ids: List[str]) -> Dict[str, Any]:
        """Compare raw performance metrics"""
        performance_data = {}

        for driver_id in driver_ids:
            profile = self.driver_profiles.get(driver_id, {})
            perf_summary = profile.get('performance_summary', {})

            performance_data[driver_id] = {
                'best_lap': perf_summary.get('best_lap_time', 999),
                'average_lap': perf_summary.get('average_lap_time', 999),
                'total_laps': perf_summary.get('total_laps', 0),
                'lap_time_variation': perf_summary.get('lap_time_std', 0),
                'driver_rating': profile.get('driver_rating', 0)
            }

        # Find performance leader
        best_driver = min(performance_data.keys(),
                         key=lambda d: performance_data[d]['best_lap'])

        # Calculate gaps to leader
        leader_time = performance_data[best_driver]['best_lap']
        for driver_id in driver_ids:
            gap = performance_data[driver_id]['best_lap'] - leader_time
            performance_data[driver_id]['gap_to_leader'] = gap
            performance_data[driver_id]['gap_percentage'] = (gap / leader_time) * 100 if leader_time > 0 else 0

        return {
            'performance_leader': best_driver,
            'leader_time': leader_time,
            'driver_data': performance_data,
            'performance_spread': max(d['best_lap'] for d in performance_data.values()) - leader_time
        }

    def _compare_consistency(self, driver_ids: List[str]) -> Dict[str, Any]:
        """Compare consistency metrics"""
        consistency_data = {}

        for driver_id in driver_ids:
            profile = self.driver_profiles.get(driver_id, {})
            consistency_profile = profile.get('consistency_profile', {})

            consistency_data[driver_id] = {
                'average_consistency': consistency_profile.get('average_consistency', 0),
                'best_consistency': consistency_profile.get('best_consistency', 0),
                'consistency_variation': consistency_profile.get('consistency_std', 0),
                'sessions_count': profile.get('total_sessions', 0)
            }

        # Find consistency leader
        most_consistent = max(consistency_data.keys(),
                            key=lambda d: consistency_data[d]['average_consistency'])

        return {
            'consistency_leader': most_consistent,
            'leader_consistency': consistency_data[most_consistent]['average_consistency'],
            'driver_data': consistency_data
        }

    def _compare_track_performance(self, driver_ids: List[str]) -> Dict[str, Any]:
        """Compare performance across different tracks"""
        track_comparison = {}

        # Get all tracks
        all_tracks = set()
        for driver_id in driver_ids:
            profile = self.driver_profiles.get(driver_id, {})
            track_specialties = profile.get('track_specialties', {})
            all_tracks.update(track_specialties.keys())

        for track in all_tracks:
            track_comparison[track] = {}
            track_times = {}

            for driver_id in driver_ids:
                profile = self.driver_profiles.get(driver_id, {})
                track_data = profile.get('track_specialties', {}).get(track, {})

                if track_data:
                    best_time = track_data.get('best_time', 999)
                    track_times[driver_id] = best_time
                    track_comparison[track][driver_id] = {
                        'best_time': best_time,
                        'average_time': track_data.get('average_time', 999),
                        'sessions': track_data.get('sessions', 0)
                    }

            # Find track leader
            if track_times:
                track_leader = min(track_times.keys(), key=lambda d: track_times[d])
                track_comparison[track]['leader'] = track_leader
                track_comparison[track]['leader_time'] = track_times[track_leader]

                # Calculate gaps
                leader_time = track_times[track_leader]
                for driver_id in track_times:
                    gap = track_times[driver_id] - leader_time
                    track_comparison[track][driver_id]['gap_to_leader'] = gap

        return track_comparison

    def _compare_car_performance(self, driver_ids: List[str]) -> Dict[str, Any]:
        """Compare performance across different cars"""
        car_comparison = {}

        # Get all cars
        all_cars = set()
        for driver_id in driver_ids:
            profile = self.driver_profiles.get(driver_id, {})
            car_expertise = profile.get('car_expertise', {})
            all_cars.update(car_expertise.keys())

        for car in all_cars:
            car_comparison[car] = {}
            car_times = {}

            for driver_id in driver_ids:
                profile = self.driver_profiles.get(driver_id, {})
                car_data = profile.get('car_expertise', {}).get(car, {})

                if car_data:
                    best_time = car_data.get('best_time', 999)
                    car_times[driver_id] = best_time
                    car_comparison[car][driver_id] = {
                        'best_time': best_time,
                        'average_time': car_data.get('average_time', 999),
                        'sessions': car_data.get('sessions', 0)
                    }

            # Find car specialist
            if car_times:
                car_specialist = min(car_times.keys(), key=lambda d: car_times[d])
                car_comparison[car]['specialist'] = car_specialist
                car_comparison[car]['specialist_time'] = car_times[car_specialist]

        return car_comparison

    def _head_to_head_analysis(self, driver_ids: List[str]) -> Dict[str, Any]:
        """Perform head-to-head analysis between drivers"""
        head_to_head = {}

        for i, driver1 in enumerate(driver_ids):
            for j, driver2 in enumerate(driver_ids[i+1:], i+1):
                matchup_key = f"{driver1}_vs_{driver2}"

                profile1 = self.driver_profiles.get(driver1, {})
                profile2 = self.driver_profiles.get(driver2, {})

                # Performance comparison
                perf1 = profile1.get('performance_summary', {})
                perf2 = profile2.get('performance_summary', {})

                best_lap1 = perf1.get('best_lap_time', 999)
                best_lap2 = perf2.get('best_lap_time', 999)

                consistency1 = profile1.get('consistency_profile', {}).get('average_consistency', 0)
                consistency2 = profile2.get('consistency_profile', {}).get('average_consistency', 0)

                head_to_head[matchup_key] = {
                    'driver1': driver1,
                    'driver2': driver2,
                    'lap_time_advantage': driver1 if best_lap1 < best_lap2 else driver2,
                    'lap_time_gap': abs(best_lap1 - best_lap2),
                    'consistency_advantage': driver1 if consistency1 > consistency2 else driver2,
                    'consistency_gap': abs(consistency1 - consistency2),
                    'overall_advantage': self._determine_overall_advantage(profile1, profile2, driver1, driver2)
                }

        return head_to_head

    def _generate_rankings(self, driver_ids: List[str]) -> Dict[str, Any]:
        """Generate comprehensive driver rankings"""
        rankings = {
            'overall': [],
            'lap_time': [],
            'consistency': [],
            'improvement': [],
            'versatility': []
        }

        # Overall ranking (based on driver rating)
        overall_data = [(driver_id, self.driver_profiles.get(driver_id, {}).get('driver_rating', 0))
                       for driver_id in driver_ids]
        rankings['overall'] = sorted(overall_data, key=lambda x: x[1], reverse=True)

        # Lap time ranking
        lap_time_data = [(driver_id,
                         self.driver_profiles.get(driver_id, {}).get('performance_summary', {}).get('best_lap_time', 999))
                        for driver_id in driver_ids]
        rankings['lap_time'] = sorted(lap_time_data, key=lambda x: x[1])

        # Consistency ranking
        consistency_data = [(driver_id,
                           self.driver_profiles.get(driver_id, {}).get('consistency_profile', {}).get('average_consistency', 0))
                          for driver_id in driver_ids]
        rankings['consistency'] = sorted(consistency_data, key=lambda x: x[1], reverse=True)

        return rankings

    def _generate_driver_insights(self, driver_ids: List[str]) -> Dict[str, Any]:
        """Generate insights about each driver"""
        insights = {}

        for driver_id in driver_ids:
            profile = self.driver_profiles.get(driver_id, {})

            insights[driver_id] = {
                'driving_style': profile.get('driving_characteristics', {}).get('style', 'unknown'),
                'strengths': profile.get('strengths', []),
                'weaknesses': profile.get('weaknesses', []),
                'best_tracks': self._get_best_tracks(profile),
                'best_cars': self._get_best_cars(profile),
                'improvement_areas': self._get_improvement_areas(profile)
            }

        return insights

    def _generate_comparison_recommendations(self, comparison: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on comparison"""
        recommendations = []

        performance_comp = comparison.get('performance_comparison', {})
        consistency_comp = comparison.get('consistency_comparison', {})

        # Performance recommendations
        if performance_comp.get('performance_spread', 0) > 2.0:
            recommendations.append("Significant performance gap exists - slower drivers should focus on fundamental technique")

        # Consistency recommendations
        leader_consistency = consistency_comp.get('leader_consistency', 0)
        if leader_consistency > 8.5:
            recommendations.append("Most consistent driver shows excellent racecraft - others should study their approach")

        # General recommendations
        recommendations.append("Practice together on similar cars/tracks for best learning opportunities")
        recommendations.append("Share telemetry data and setup information for mutual improvement")

        return recommendations

    def _analyze_driving_style(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze driving style characteristics"""
        # Simplified driving style analysis based on consistency patterns
        consistency_scores = []
        lap_time_variations = []

        for session in sessions:
            lap_analysis = session.get('lap_analysis', {})
            consistency = lap_analysis.get('consistency_rating', 0)
            if consistency > 0:
                consistency_scores.append(consistency)

        if not consistency_scores:
            return {'style': 'unknown'}

        avg_consistency = np.mean(consistency_scores)
        consistency_std = np.std(consistency_scores)

        # Determine driving style
        if avg_consistency >= 9.0:
            style = "precise_professional"
        elif avg_consistency >= 8.0 and consistency_std < 0.5:
            style = "consistent_smooth"
        elif avg_consistency >= 7.0:
            style = "competitive_balanced"
        elif consistency_std > 1.0:
            style = "aggressive_inconsistent"
        else:
            style = "developing_amateur"

        return {
            'style': style,
            'consistency_average': avg_consistency,
            'consistency_variation': consistency_std
        }

    def _analyze_track_specialties(self, tracks: Dict[str, Dict]) -> Dict[str, Any]:
        """Analyze performance at different tracks"""
        specialties = {}

        for track, data in tracks.items():
            if data['times']:
                specialties[track] = {
                    'best_time': min(data['times']),
                    'average_time': np.mean(data['times']),
                    'sessions': len(data['times']),
                    'consistency': np.mean(data['consistencies']) if data['consistencies'] else 0
                }

        return specialties

    def _analyze_car_expertise(self, cars: Dict[str, Dict]) -> Dict[str, Any]:
        """Analyze performance with different cars"""
        expertise = {}

        for car, data in cars.items():
            if data['times']:
                expertise[car] = {
                    'best_time': min(data['times']),
                    'average_time': np.mean(data['times']),
                    'sessions': len(data['times']),
                    'consistency': np.mean(data['consistencies']) if data['consistencies'] else 0
                }

        return expertise

    def _analyze_improvement_trend(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze improvement trend over time"""
        if len(sessions) < 3:
            return {'trend': 'insufficient_data'}

        # Sort sessions by date (if available) or use order
        sorted_sessions = sorted(sessions, key=lambda s: s.get('session_info', {}).get('date', ''))

        lap_times = []
        for session in sorted_sessions:
            fastest_lap = session.get('lap_analysis', {}).get('fastest_lap')
            if fastest_lap:
                lap_times.append(fastest_lap)

        if len(lap_times) < 3:
            return {'trend': 'insufficient_data'}

        # Calculate improvement trend
        improvement_rate = self._calculate_improvement_rate(lap_times)

        if improvement_rate < -0.1:
            trend = 'rapidly_improving'
        elif improvement_rate < -0.05:
            trend = 'improving'
        elif improvement_rate > 0.05:
            trend = 'declining'
        else:
            trend = 'stable'

        return {
            'trend': trend,
            'improvement_rate': improvement_rate,
            'sessions_analyzed': len(lap_times)
        }

    def _identify_driver_characteristics(self, profile: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Identify driver strengths and weaknesses"""
        strengths = []
        weaknesses = []

        # Consistency analysis
        consistency = profile.get('consistency_profile', {}).get('average_consistency', 0)
        if consistency >= 9.0:
            strengths.append("Exceptional consistency")
        elif consistency >= 8.0:
            strengths.append("Good consistency")
        elif consistency < 6.0:
            weaknesses.append("Inconsistent performance")

        # Performance analysis
        performance = profile.get('performance_summary', {})
        lap_time_std = performance.get('lap_time_std', 0)
        if lap_time_std < 0.5:
            strengths.append("Repeatable lap times")
        elif lap_time_std > 2.0:
            weaknesses.append("High lap time variation")

        # Experience analysis
        total_sessions = profile.get('total_sessions', 0)
        if total_sessions >= 10:
            strengths.append("Experienced driver")
        elif total_sessions < 3:
            weaknesses.append("Limited experience")

        return strengths, weaknesses

    def _calculate_driver_rating(self, profile: Dict[str, Any]) -> float:
        """Calculate overall driver rating (1-10)"""
        rating = 5.0  # Base rating

        # Consistency contribution (0-3 points)
        consistency = profile.get('consistency_profile', {}).get('average_consistency', 0)
        rating += (consistency / 10.0) * 3.0

        # Experience contribution (0-1 point)
        sessions = profile.get('total_sessions', 0)
        experience_bonus = min(1.0, sessions / 20.0)
        rating += experience_bonus

        # Performance contribution (0-1 point)
        performance = profile.get('performance_summary', {})
        lap_time_std = performance.get('lap_time_std', 10.0)
        if lap_time_std > 0:
            performance_bonus = max(0, 1.0 - (lap_time_std / 5.0))
            rating += performance_bonus

        return min(10.0, rating)

    def _calculate_improvement_rate(self, lap_times: List[float]) -> float:
        """Calculate improvement rate from lap times"""
        if len(lap_times) < 2:
            return 0.0

        # Simple linear regression slope
        x = np.arange(len(lap_times))
        slope = np.polyfit(x, lap_times, 1)[0]
        return float(slope)

    def _determine_overall_advantage(self, profile1: Dict, profile2: Dict, driver1: str, driver2: str) -> str:
        """Determine overall advantage between two drivers"""
        rating1 = profile1.get('driver_rating', 0)
        rating2 = profile2.get('driver_rating', 0)

        if abs(rating1 - rating2) < 0.5:
            return 'even'
        else:
            return driver1 if rating1 > rating2 else driver2

    def _get_best_tracks(self, profile: Dict[str, Any]) -> List[str]:
        """Get driver's best tracks"""
        track_specialties = profile.get('track_specialties', {})
        if not track_specialties:
            return []

        # Sort by consistency (could also use best times)
        sorted_tracks = sorted(track_specialties.items(),
                             key=lambda x: x[1].get('consistency', 0),
                             reverse=True)

        return [track for track, _ in sorted_tracks[:3]]

    def _get_best_cars(self, profile: Dict[str, Any]) -> List[str]:
        """Get driver's best cars"""
        car_expertise = profile.get('car_expertise', {})
        if not car_expertise:
            return []

        # Sort by consistency
        sorted_cars = sorted(car_expertise.items(),
                           key=lambda x: x[1].get('consistency', 0),
                           reverse=True)

        return [car for car, _ in sorted_cars[:3]]

    def _get_improvement_areas(self, profile: Dict[str, Any]) -> List[str]:
        """Get areas where driver should focus improvement"""
        areas = []

        weaknesses = profile.get('weaknesses', [])
        if weaknesses:
            areas.extend(weaknesses)

        # Add specific technical areas based on performance
        consistency = profile.get('consistency_profile', {}).get('average_consistency', 0)
        if consistency < 7.0:
            areas.append("Focus on consistency and smoothness")

        performance = profile.get('performance_summary', {})
        lap_time_std = performance.get('lap_time_std', 0)
        if lap_time_std > 1.5:
            areas.append("Reduce lap time variation")

        return areas[:5]  # Limit to 5 areas


if __name__ == "__main__":
    print("=== Multi-Driver Comparison System Test ===")
    print("Driver comparator initialized")
    print("Ready for multi-driver performance analysis")
    print("=== Test Complete ===")