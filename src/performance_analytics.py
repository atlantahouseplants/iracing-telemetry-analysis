"""
Performance Analytics Dashboard
Advanced visualizations and analytics for telemetry data
"""

import json
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class PerformanceAnalytics:
    """Advanced performance analytics and visualization generator"""

    def __init__(self, coach):
        """
        Initialize analytics engine

        Args:
            coach: Enhanced AI coach instance with session data
        """
        self.coach = coach
        self.analytics_cache = {}
        self.cache_duration = timedelta(minutes=5)

    def generate_dashboard_data(self) -> Dict[str, Any]:
        """
        Generate comprehensive dashboard data

        Returns:
            Complete analytics data for dashboard visualization
        """
        try:
            # Check cache first
            cache_key = "dashboard_data"
            if self._is_cache_valid(cache_key):
                return self.analytics_cache[cache_key]["data"]

            logger.info("Generating performance analytics dashboard...")

            dashboard_data = {
                'overview_metrics': self._generate_overview_metrics(),
                'performance_trends': self._generate_performance_trends(),
                'track_analysis': self._generate_track_analysis(),
                'car_comparison': self._generate_car_comparison(),
                'consistency_analysis': self._generate_consistency_analytics(),
                'lap_time_comparison': self._generate_lap_time_comparison(),
                'trend_analysis': self._generate_detailed_trend_analysis(),
                'session_timeline': self._generate_session_timeline(),
                'improvement_tracking': self._generate_improvement_tracking(),
                'professional_insights': self._generate_professional_dashboard_insights(),
                'generated_at': datetime.now().isoformat()
            }

            # Cache the results
            self._cache_data(cache_key, dashboard_data)

            logger.info("Dashboard analytics generated successfully")
            return dashboard_data

        except Exception as e:
            logger.error(f"Error generating dashboard data: {e}")
            return self._create_fallback_dashboard()

    def _generate_overview_metrics(self) -> Dict[str, Any]:
        """Generate high-level overview metrics"""
        if not self.coach.sessions:
            return {'status': 'no_data'}

        # Aggregate metrics across all sessions
        total_sessions = len(self.coach.sessions)
        total_laps = 0
        lap_times = []
        consistency_ratings = []
        tracks = set()
        cars = set()

        for session in self.coach.sessions:
            session_info = session.get('session_info', {})
            lap_analysis = session.get('lap_analysis', {})

            # Track and car data
            if session_info.get('track'):
                tracks.add(session_info['track'])
            if session_info.get('car'):
                cars.add(session_info['car'])

            # Lap data
            session_laps = lap_analysis.get('total_laps', 0)
            total_laps += session_laps

            # Lap times
            session_lap_times = lap_analysis.get('lap_times', [])
            lap_times.extend(session_lap_times)

            # Consistency
            consistency = lap_analysis.get('consistency_rating', 0)
            if consistency > 0:
                consistency_ratings.append(consistency)

        # Calculate aggregated metrics
        metrics = {
            'total_sessions': total_sessions,
            'total_laps': total_laps,
            'tracks_driven': len(tracks),
            'cars_driven': len(cars),
            'track_list': list(tracks),
            'car_list': list(cars)
        }

        if lap_times:
            lap_times_array = np.array(lap_times)
            metrics.update({
                'fastest_overall': float(np.min(lap_times_array)),
                'average_lap_time': float(np.mean(lap_times_array)),
                'lap_time_std': float(np.std(lap_times_array)),
                'total_distance_km': self._estimate_total_distance(lap_times, tracks)
            })

        if consistency_ratings:
            metrics.update({
                'average_consistency': float(np.mean(consistency_ratings)),
                'consistency_trend': self._calculate_consistency_trend(consistency_ratings)
            })

        return metrics

    def _generate_performance_trends(self) -> Dict[str, Any]:
        """Generate performance trend analysis"""
        if len(self.coach.sessions) < 2:
            return {'status': 'insufficient_data'}

        # Sort sessions by date
        sorted_sessions = sorted(self.coach.sessions,
                               key=lambda x: x.get('processed_timestamp', ''))

        trends = {
            'lap_time_progression': [],
            'consistency_progression': [],
            'session_dates': [],
            'performance_summary': {}
        }

        for session in sorted_sessions:
            session_info = session.get('session_info', {})
            lap_analysis = session.get('lap_analysis', {})

            # Extract date
            date = session.get('processed_timestamp', '')[:10] if session.get('processed_timestamp') else 'Unknown'
            trends['session_dates'].append(date)

            # Lap time data
            fastest_lap = lap_analysis.get('fastest_lap')
            if fastest_lap:
                trends['lap_time_progression'].append(fastest_lap)

            # Consistency data
            consistency = lap_analysis.get('consistency_rating', 0)
            trends['consistency_progression'].append(consistency)

        # Calculate trend statistics
        if trends['lap_time_progression']:
            lap_times = trends['lap_time_progression']
            trends['performance_summary'] = {
                'lap_time_improvement': self._calculate_improvement_rate(lap_times),
                'best_session_index': int(np.argmin(lap_times)),
                'worst_session_index': int(np.argmax(lap_times)),
                'improvement_trend': 'improving' if lap_times[-1] < lap_times[0] else 'stable'
            }

        return trends

    def _generate_track_analysis(self) -> Dict[str, Any]:
        """Generate track-specific analysis"""
        track_data = {}

        for session in self.coach.sessions:
            session_info = session.get('session_info', {})
            lap_analysis = session.get('lap_analysis', {})

            track = session_info.get('track', 'Unknown')
            if track == 'Unknown':
                continue

            if track not in track_data:
                track_data[track] = {
                    'sessions': [],
                    'best_lap': float('inf'),
                    'total_laps': 0,
                    'cars_used': set(),
                    'consistency_ratings': []
                }

            # Add session data
            fastest_lap = lap_analysis.get('fastest_lap')
            if fastest_lap:
                track_data[track]['sessions'].append(fastest_lap)
                track_data[track]['best_lap'] = min(track_data[track]['best_lap'], fastest_lap)

            track_data[track]['total_laps'] += lap_analysis.get('total_laps', 0)

            car = session_info.get('car')
            if car:
                track_data[track]['cars_used'].add(car)

            consistency = lap_analysis.get('consistency_rating', 0)
            if consistency > 0:
                track_data[track]['consistency_ratings'].append(consistency)

        # Process track data for dashboard
        analytics = {}
        for track, data in track_data.items():
            analytics[track] = {
                'session_count': len(data['sessions']),
                'best_lap_time': data['best_lap'] if data['best_lap'] != float('inf') else None,
                'average_lap_time': float(np.mean(data['sessions'])) if data['sessions'] else None,
                'total_laps': data['total_laps'],
                'cars_used': list(data['cars_used']),
                'average_consistency': float(np.mean(data['consistency_ratings'])) if data['consistency_ratings'] else None,
                'improvement_rate': self._calculate_improvement_rate(data['sessions']) if len(data['sessions']) > 1 else 0
            }

        return analytics

    def _generate_car_comparison(self) -> Dict[str, Any]:
        """Generate car comparison analysis"""
        car_data = {}

        for session in self.coach.sessions:
            session_info = session.get('session_info', {})
            lap_analysis = session.get('lap_analysis', {})

            car = session_info.get('car', 'Unknown')
            if car == 'Unknown':
                continue

            if car not in car_data:
                car_data[car] = {
                    'sessions': [],
                    'tracks': set(),
                    'lap_times': [],
                    'consistency_ratings': []
                }

            # Add session data
            fastest_lap = lap_analysis.get('fastest_lap')
            if fastest_lap:
                car_data[car]['lap_times'].append(fastest_lap)

            track = session_info.get('track')
            if track:
                car_data[car]['tracks'].add(track)

            consistency = lap_analysis.get('consistency_rating', 0)
            if consistency > 0:
                car_data[car]['consistency_ratings'].append(consistency)

            car_data[car]['sessions'].append(session)

        # Process car comparison data
        comparison = {}
        for car, data in car_data.items():
            comparison[car] = {
                'session_count': len(data['sessions']),
                'tracks_driven': list(data['tracks']),
                'best_lap_time': float(np.min(data['lap_times'])) if data['lap_times'] else None,
                'average_lap_time': float(np.mean(data['lap_times'])) if data['lap_times'] else None,
                'average_consistency': float(np.mean(data['consistency_ratings'])) if data['consistency_ratings'] else None,
                'versatility_score': len(data['tracks']) * 10 + len(data['sessions'])  # Custom metric
            }

        return comparison

    def _generate_consistency_analytics(self) -> Dict[str, Any]:
        """Generate detailed consistency analysis"""
        if not self.coach.sessions:
            return {'status': 'no_data'}

        consistency_data = []
        session_labels = []

        for i, session in enumerate(self.coach.sessions):
            lap_analysis = session.get('lap_analysis', {})
            session_info = session.get('session_info', {})

            consistency = lap_analysis.get('consistency_rating', 0)
            if consistency > 0:
                consistency_data.append(consistency)
                session_labels.append(f"{session_info.get('car', 'Unknown')}@{session_info.get('track', 'Unknown')}")

        if not consistency_data:
            return {'status': 'no_data'}

        analytics = {
            'consistency_scores': consistency_data,
            'session_labels': session_labels,
            'average_consistency': float(np.mean(consistency_data)),
            'best_consistency': float(np.max(consistency_data)),
            'worst_consistency': float(np.min(consistency_data)),
            'consistency_std': float(np.std(consistency_data)),
            'consistency_categories': self._categorize_consistency(consistency_data)
        }

        return analytics

    def _generate_session_timeline(self) -> Dict[str, Any]:
        """Generate session timeline for visualization"""
        timeline = []

        for session in self.coach.sessions:
            session_info = session.get('session_info', {})
            lap_analysis = session.get('lap_analysis', {})

            timeline_entry = {
                'date': session.get('processed_timestamp', ''),
                'track': session_info.get('track', 'Unknown'),
                'car': session_info.get('car', 'Unknown'),
                'laps': lap_analysis.get('total_laps', 0),
                'fastest_lap': lap_analysis.get('fastest_lap'),
                'consistency': lap_analysis.get('consistency_rating', 0),
                'session_id': session.get('id', '')
            }
            timeline.append(timeline_entry)

        # Sort by date
        timeline.sort(key=lambda x: x['date'])

        return {
            'timeline': timeline,
            'total_sessions': len(timeline),
            'date_range': {
                'start': timeline[0]['date'][:10] if timeline else None,
                'end': timeline[-1]['date'][:10] if timeline else None
            }
        }

    def _generate_improvement_tracking(self) -> Dict[str, Any]:
        """Generate improvement tracking analysis"""
        if len(self.coach.sessions) < 2:
            return {'status': 'insufficient_data'}

        # Track improvements over time
        improvements = {
            'overall_progress': {},
            'track_specific_progress': {},
            'car_specific_progress': {}
        }

        # Overall progress
        first_session = self.coach.sessions[0]
        latest_session = self.coach.sessions[-1]

        first_lap_time = first_session.get('lap_analysis', {}).get('fastest_lap')
        latest_lap_time = latest_session.get('lap_analysis', {}).get('fastest_lap')

        if first_lap_time and latest_lap_time:
            improvements['overall_progress'] = {
                'initial_best': first_lap_time,
                'current_best': latest_lap_time,
                'improvement_seconds': first_lap_time - latest_lap_time,
                'improvement_percentage': ((first_lap_time - latest_lap_time) / first_lap_time) * 100
            }

        # Track-specific improvements
        track_progress = {}
        for session in self.coach.sessions:
            session_info = session.get('session_info', {})
            lap_analysis = session.get('lap_analysis', {})

            track = session_info.get('track')
            fastest_lap = lap_analysis.get('fastest_lap')

            if track and fastest_lap:
                if track not in track_progress:
                    track_progress[track] = []
                track_progress[track].append(fastest_lap)

        for track, times in track_progress.items():
            if len(times) > 1:
                improvements['track_specific_progress'][track] = {
                    'sessions': len(times),
                    'initial_best': times[0],
                    'current_best': min(times),
                    'improvement_seconds': times[0] - min(times)
                }

        return improvements

    def _generate_professional_dashboard_insights(self) -> Dict[str, Any]:
        """Generate professional insights for dashboard"""
        insights = {
            'performance_rating': self._calculate_overall_performance_rating(),
            'strength_areas': [],
            'improvement_areas': [],
            'recommendations': [],
            'benchmarking': {}
        }

        # Analyze strengths and weaknesses
        if self.coach.sessions:
            # Get latest professional analysis if available
            latest_session = self.coach.sessions[-1]
            professional_analysis = latest_session.get('professional_analysis', {})

            if professional_analysis and professional_analysis.get('professional_insights'):
                prof_insights = professional_analysis['professional_insights']
                insights['recommendations'] = prof_insights.get('strategic_recommendations', [])

            # Calculate performance benchmarking
            insights['benchmarking'] = self._calculate_performance_benchmarking()

        return insights

    def _generate_lap_time_comparison(self) -> Dict[str, Any]:
        """Generate comprehensive lap time comparison analysis"""
        comparison_data = {
            'session_comparisons': [],
            'track_best_times': {},
            'car_best_times': {},
            'improvement_timeline': [],
            'consistency_comparison': {},
            'sector_analysis': {},
            'statistical_analysis': {}
        }

        try:
            if not self.coach.sessions:
                return comparison_data

            # Collect all lap time data
            session_lap_data = []
            track_times = {}
            car_times = {}

            for i, session in enumerate(self.coach.sessions):
                lap_analysis = session.get('lap_analysis', {})
                session_info = session.get('session_info', {})

                track = session_info.get('track', 'Unknown')
                car = session_info.get('car', 'Unknown')
                fastest_lap = lap_analysis.get('fastest_lap')
                avg_lap = lap_analysis.get('average_lap')
                total_laps = lap_analysis.get('total_laps', 0)
                consistency = lap_analysis.get('consistency_rating', 0)

                if fastest_lap and avg_lap:
                    session_data = {
                        'session_index': i,
                        'date': session_info.get('date', ''),
                        'track': track,
                        'car': car,
                        'fastest_lap': fastest_lap,
                        'average_lap': avg_lap,
                        'total_laps': total_laps,
                        'consistency': consistency,
                        'gap_to_average': avg_lap - fastest_lap,
                        'lap_time_spread': lap_analysis.get('lap_time_spread', {})
                    }

                    session_lap_data.append(session_data)

                    # Track best times by track and car
                    if track not in track_times or fastest_lap < track_times[track]['best_time']:
                        track_times[track] = {
                            'best_time': fastest_lap,
                            'session_index': i,
                            'car': car,
                            'date': session_info.get('date', '')
                        }

                    if car not in car_times or fastest_lap < car_times[car]['best_time']:
                        car_times[car] = {
                            'best_time': fastest_lap,
                            'session_index': i,
                            'track': track,
                            'date': session_info.get('date', '')
                        }

            # Generate session-by-session comparisons
            comparison_data['session_comparisons'] = session_lap_data
            comparison_data['track_best_times'] = track_times
            comparison_data['car_best_times'] = car_times

            # Create improvement timeline
            if len(session_lap_data) >= 2:
                improvement_timeline = []
                for i in range(1, len(session_lap_data)):
                    current = session_lap_data[i]
                    previous = session_lap_data[i-1]

                    # Compare only same track sessions for meaningful analysis
                    if current['track'] == previous['track']:
                        improvement = previous['fastest_lap'] - current['fastest_lap']
                        improvement_timeline.append({
                            'session_index': i,
                            'track': current['track'],
                            'improvement_seconds': improvement,
                            'improvement_percentage': (improvement / previous['fastest_lap']) * 100 if previous['fastest_lap'] > 0 else 0,
                            'current_time': current['fastest_lap'],
                            'previous_time': previous['fastest_lap']
                        })

                comparison_data['improvement_timeline'] = improvement_timeline

            # Statistical analysis
            if session_lap_data:
                all_fastest_times = [s['fastest_lap'] for s in session_lap_data]
                all_avg_times = [s['average_lap'] for s in session_lap_data]
                all_consistencies = [s['consistency'] for s in session_lap_data if s['consistency'] > 0]

                comparison_data['statistical_analysis'] = {
                    'overall_best_lap': min(all_fastest_times),
                    'overall_worst_lap': max(all_fastest_times),
                    'average_best_lap': np.mean(all_fastest_times),
                    'lap_time_std_dev': np.std(all_fastest_times),
                    'consistency_average': np.mean(all_consistencies) if all_consistencies else 0,
                    'total_sessions_analyzed': len(session_lap_data),
                    'improvement_trend': self._calculate_improvement_rate(all_fastest_times)
                }

                # Consistency comparison across sessions
                comparison_data['consistency_comparison'] = {
                    'best_consistency_session': max(session_lap_data, key=lambda x: x['consistency']) if session_lap_data else None,
                    'worst_consistency_session': min(session_lap_data, key=lambda x: x['consistency']) if session_lap_data else None,
                    'consistency_trend': self._calculate_consistency_trend(all_consistencies)
                }

        except Exception as e:
            logger.error(f"Error generating lap time comparison: {e}")
            comparison_data['error'] = str(e)

        return comparison_data

    def _generate_detailed_trend_analysis(self) -> Dict[str, Any]:
        """Generate detailed trend analysis for performance metrics"""
        trend_data = {
            'performance_trends': {},
            'consistency_trends': {},
            'track_specific_trends': {},
            'car_specific_trends': {},
            'seasonal_analysis': {},
            'predictive_insights': {},
            'trend_summary': {}
        }

        try:
            if not self.coach.sessions:
                return trend_data

            # Collect chronological data
            sessions_by_date = []
            for session in self.coach.sessions:
                session_info = session.get('session_info', {})
                lap_analysis = session.get('lap_analysis', {})

                date_str = session_info.get('date', '')
                if date_str:
                    try:
                        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        date_obj = datetime.now()
                else:
                    date_obj = datetime.now()

                sessions_by_date.append({
                    'date': date_obj,
                    'track': session_info.get('track', 'Unknown'),
                    'car': session_info.get('car', 'Unknown'),
                    'fastest_lap': lap_analysis.get('fastest_lap'),
                    'average_lap': lap_analysis.get('average_lap_time'),
                    'consistency': lap_analysis.get('consistency_rating', 0),
                    'total_laps': lap_analysis.get('total_laps', 0)
                })

            # Sort by date
            sessions_by_date.sort(key=lambda x: x['date'])

            # Performance trends over time
            if len(sessions_by_date) >= 3:
                fastest_laps = [s['fastest_lap'] for s in sessions_by_date if s['fastest_lap']]
                consistencies = [s['consistency'] for s in sessions_by_date if s['consistency'] > 0]
                dates = [s['date'] for s in sessions_by_date if s['fastest_lap']]

                if fastest_laps:
                    # Calculate moving averages
                    window_size = min(5, len(fastest_laps))
                    moving_avg = []
                    for i in range(len(fastest_laps) - window_size + 1):
                        avg = np.mean(fastest_laps[i:i + window_size])
                        moving_avg.append(avg)

                    trend_data['performance_trends'] = {
                        'raw_times': fastest_laps,
                        'moving_average': moving_avg,
                        'trend_direction': 'improving' if self._calculate_improvement_rate(fastest_laps) < -0.01 else 'stable',
                        'improvement_rate_per_session': self._calculate_improvement_rate(fastest_laps),
                        'best_period': self._find_best_performance_period(fastest_laps, dates),
                        'volatility': np.std(fastest_laps) if len(fastest_laps) > 1 else 0
                    }

                if consistencies:
                    trend_data['consistency_trends'] = {
                        'raw_scores': consistencies,
                        'trend_direction': self._calculate_consistency_trend(consistencies),
                        'improvement_rate': self._calculate_improvement_rate(consistencies),
                        'stability_index': 1 / (1 + np.std(consistencies)) if len(consistencies) > 1 else 1
                    }

            # Track-specific trends
            track_trends = {}
            for track in set(s['track'] for s in sessions_by_date):
                track_sessions = [s for s in sessions_by_date if s['track'] == track]
                if len(track_sessions) >= 2:
                    track_times = [s['fastest_lap'] for s in track_sessions if s['fastest_lap']]
                    if track_times:
                        track_trends[track] = {
                            'sessions_count': len(track_sessions),
                            'best_time': min(track_times),
                            'latest_time': track_times[-1],
                            'improvement_trend': self._calculate_improvement_rate(track_times),
                            'consistency_at_track': np.mean([s['consistency'] for s in track_sessions if s['consistency'] > 0])
                        }
            trend_data['track_specific_trends'] = track_trends

            # Car-specific trends
            car_trends = {}
            for car in set(s['car'] for s in sessions_by_date):
                car_sessions = [s for s in sessions_by_date if s['car'] == car]
                if len(car_sessions) >= 2:
                    car_times = [s['fastest_lap'] for s in car_sessions if s['fastest_lap']]
                    if car_times:
                        car_trends[car] = {
                            'sessions_count': len(car_sessions),
                            'best_time': min(car_times),
                            'latest_time': car_times[-1],
                            'improvement_trend': self._calculate_improvement_rate(car_times),
                            'adaptability_score': 1 / (1 + np.std(car_times)) if len(car_times) > 1 else 1
                        }
            trend_data['car_specific_trends'] = car_trends

            # Seasonal analysis (if date range is sufficient)
            if sessions_by_date and (sessions_by_date[-1]['date'] - sessions_by_date[0]['date']).days > 30:
                trend_data['seasonal_analysis'] = self._analyze_seasonal_patterns(sessions_by_date)

            # Predictive insights
            if len(sessions_by_date) >= 5:
                trend_data['predictive_insights'] = self._generate_predictive_insights(sessions_by_date)

            # Trend summary
            trend_data['trend_summary'] = self._summarize_trends(trend_data)

        except Exception as e:
            logger.error(f"Error generating detailed trend analysis: {e}")
            trend_data['error'] = str(e)

        return trend_data

    # Helper methods

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.analytics_cache:
            return False

        cache_time = self.analytics_cache[cache_key]["timestamp"]
        return datetime.now() - cache_time < self.cache_duration

    def _cache_data(self, cache_key: str, data: Dict[str, Any]):
        """Cache analytics data"""
        self.analytics_cache[cache_key] = {
            "data": data,
            "timestamp": datetime.now()
        }

    def _estimate_total_distance(self, lap_times: List[float], tracks: set) -> float:
        """Estimate total distance driven"""
        # Rough track length estimates (km)
        track_lengths = {
            'roadatlanta': 4.0,
            'talladega': 4.3,
            'watkinsglen': 5.5,
            'sebring': 6.0
        }

        # Use average track length if unknown
        avg_length = 4.5
        total_distance = 0

        for track in tracks:
            length = track_lengths.get(track.lower(), avg_length)
            # Rough estimate of laps per track
            track_laps = len([t for t in lap_times]) // len(tracks)
            total_distance += length * track_laps

        return round(total_distance, 1)

    def _calculate_consistency_trend(self, ratings: List[float]) -> str:
        """Calculate consistency trend"""
        if len(ratings) < 2:
            return 'stable'

        recent_avg = np.mean(ratings[-3:]) if len(ratings) >= 3 else ratings[-1]
        early_avg = np.mean(ratings[:3]) if len(ratings) >= 3 else ratings[0]

        if recent_avg > early_avg + 0.5:
            return 'improving'
        elif recent_avg < early_avg - 0.5:
            return 'declining'
        else:
            return 'stable'

    def _calculate_improvement_rate(self, values: List[float]) -> float:
        """Calculate improvement rate (negative = getting better)"""
        if len(values) < 2:
            return 0.0

        # Linear regression slope
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        return float(slope)

    def _categorize_consistency(self, scores: List[float]) -> Dict[str, int]:
        """Categorize consistency scores"""
        categories = {'excellent': 0, 'good': 0, 'average': 0, 'needs_work': 0}

        for score in scores:
            if score >= 9:
                categories['excellent'] += 1
            elif score >= 7:
                categories['good'] += 1
            elif score >= 5:
                categories['average'] += 1
            else:
                categories['needs_work'] += 1

        return categories

    def _calculate_overall_performance_rating(self) -> float:
        """Calculate overall performance rating (1-10)"""
        if not self.coach.sessions:
            return 5.0

        # Weighted combination of factors
        consistency_scores = []
        lap_count = 0

        for session in self.coach.sessions:
            lap_analysis = session.get('lap_analysis', {})
            consistency = lap_analysis.get('consistency_rating', 0)
            if consistency > 0:
                consistency_scores.append(consistency)
            lap_count += lap_analysis.get('total_laps', 0)

        # Base rating from consistency
        base_rating = np.mean(consistency_scores) if consistency_scores else 5.0

        # Bonus for experience (lap count)
        experience_bonus = min(1.0, lap_count / 500)  # Up to 1 point for 500+ laps

        # Bonus for variety (tracks/cars)
        tracks = len(set(s.get('session_info', {}).get('track') for s in self.coach.sessions))
        variety_bonus = min(0.5, tracks * 0.1)  # Up to 0.5 points

        total_rating = min(10.0, base_rating + experience_bonus + variety_bonus)
        return round(total_rating, 1)

    def _calculate_performance_benchmarking(self) -> Dict[str, Any]:
        """Calculate performance benchmarking"""
        benchmarking = {
            'speed_rating': 'intermediate',
            'consistency_rating': 'good',
            'experience_level': 'developing'
        }

        if self.coach.sessions:
            # Get best lap time for benchmarking
            all_lap_times = []
            for session in self.coach.sessions:
                fastest = session.get('lap_analysis', {}).get('fastest_lap')
                if fastest:
                    all_lap_times.append(fastest)

            if all_lap_times:
                best_time = min(all_lap_times)
                # This is simplified - real benchmarking would use track-specific data
                if best_time < 45:  # Very rough benchmark
                    benchmarking['speed_rating'] = 'advanced'
                elif best_time < 50:
                    benchmarking['speed_rating'] = 'intermediate'
                else:
                    benchmarking['speed_rating'] = 'developing'

        return benchmarking

    def _find_best_performance_period(self, lap_times: List[float], dates: List[datetime]) -> Dict[str, Any]:
        """Find the period with best performance improvement"""
        if len(lap_times) < 3:
            return {'period': 'insufficient_data', 'improvement': 0}

        best_improvement = 0
        best_period = {'start_index': 0, 'end_index': len(lap_times)-1}

        # Look for periods of consistent improvement
        window_size = min(5, len(lap_times))
        for i in range(len(lap_times) - window_size + 1):
            window_times = lap_times[i:i + window_size]
            improvement = window_times[0] - window_times[-1]  # Negative lap time change = improvement
            if improvement > best_improvement:
                best_improvement = improvement
                best_period = {'start_index': i, 'end_index': i + window_size - 1}

        return {
            'period': f"Session {best_period['start_index']} to {best_period['end_index']}",
            'improvement': best_improvement,
            'start_date': dates[best_period['start_index']].isoformat() if best_period['start_index'] < len(dates) else '',
            'end_date': dates[best_period['end_index']].isoformat() if best_period['end_index'] < len(dates) else ''
        }

    def _analyze_seasonal_patterns(self, sessions_by_date: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze seasonal performance patterns"""
        seasonal_data = {
            'monthly_performance': {},
            'day_of_week_patterns': {},
            'time_of_day_patterns': {},
            'consistency_by_period': {}
        }

        try:
            # Group by month
            monthly_times = {}
            for session in sessions_by_date:
                if session['fastest_lap']:
                    month_key = session['date'].strftime('%Y-%m')
                    if month_key not in monthly_times:
                        monthly_times[month_key] = []
                    monthly_times[month_key].append(session['fastest_lap'])

            for month, times in monthly_times.items():
                seasonal_data['monthly_performance'][month] = {
                    'average_time': np.mean(times),
                    'best_time': min(times),
                    'session_count': len(times),
                    'improvement_trend': self._calculate_improvement_rate(times)
                }

            # Day of week patterns
            dow_times = {}
            for session in sessions_by_date:
                if session['fastest_lap']:
                    dow = session['date'].strftime('%A')
                    if dow not in dow_times:
                        dow_times[dow] = []
                    dow_times[dow].append(session['fastest_lap'])

            for day, times in dow_times.items():
                seasonal_data['day_of_week_patterns'][day] = {
                    'average_time': np.mean(times),
                    'session_count': len(times)
                }

        except Exception as e:
            logger.error(f"Error in seasonal analysis: {e}")
            seasonal_data['error'] = str(e)

        return seasonal_data

    def _generate_predictive_insights(self, sessions_by_date: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate predictive insights based on historical data"""
        insights = {
            'projected_improvement': {},
            'consistency_forecast': {},
            'recommendations': [],
            'confidence_level': 'low'
        }

        try:
            # Extract time series data
            fastest_laps = [s['fastest_lap'] for s in sessions_by_date if s['fastest_lap']]
            consistencies = [s['consistency'] for s in sessions_by_date if s['consistency'] > 0]

            if len(fastest_laps) >= 5:
                # Calculate improvement trend
                improvement_rate = self._calculate_improvement_rate(fastest_laps)

                # Project next session performance
                if improvement_rate < 0:  # Improving (lap times getting faster)
                    projected_time = fastest_laps[-1] + improvement_rate
                    insights['projected_improvement'] = {
                        'next_session_projection': projected_time,
                        'improvement_rate_per_session': improvement_rate,
                        'confidence': 'medium' if len(fastest_laps) >= 10 else 'low'
                    }

                # Generate recommendations based on trends
                if improvement_rate > 0.1:  # Getting slower
                    insights['recommendations'].append("Consider reviewing recent setup changes or practice routine")
                elif improvement_rate < -0.1:  # Improving well
                    insights['recommendations'].append("Maintain current practice approach - showing good improvement")
                else:  # Stable
                    insights['recommendations'].append("Try new techniques or track variations to break plateau")

                insights['confidence_level'] = 'medium' if len(fastest_laps) >= 10 else 'low'

        except Exception as e:
            logger.error(f"Error generating predictive insights: {e}")
            insights['error'] = str(e)

        return insights

    def _summarize_trends(self, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize overall trends from detailed analysis"""
        summary = {
            'overall_direction': 'stable',
            'key_insights': [],
            'areas_of_focus': [],
            'confidence_rating': 5.0
        }

        try:
            # Analyze performance trends
            perf_trends = trend_data.get('performance_trends', {})
            if perf_trends.get('improvement_rate_per_session', 0) < -0.05:
                summary['overall_direction'] = 'improving'
                summary['key_insights'].append("Showing consistent lap time improvement")
            elif perf_trends.get('improvement_rate_per_session', 0) > 0.05:
                summary['overall_direction'] = 'declining'
                summary['areas_of_focus'].append("Address recent performance decline")

            # Analyze consistency trends
            consistency_trends = trend_data.get('consistency_trends', {})
            if consistency_trends.get('trend_direction') == 'improving':
                summary['key_insights'].append("Consistency is improving over time")
            elif consistency_trends.get('trend_direction') == 'declining':
                summary['areas_of_focus'].append("Focus on consistency improvement")

            # Track-specific insights
            track_trends = trend_data.get('track_specific_trends', {})
            improving_tracks = [track for track, data in track_trends.items()
                              if data.get('improvement_trend', 0) < -0.02]
            if improving_tracks:
                summary['key_insights'].append(f"Strong improvement at: {', '.join(improving_tracks[:3])}")

            # Calculate confidence based on data availability
            data_points = len(perf_trends.get('raw_times', []))
            if data_points >= 10:
                summary['confidence_rating'] = 8.0
            elif data_points >= 5:
                summary['confidence_rating'] = 6.0
            else:
                summary['confidence_rating'] = 4.0

        except Exception as e:
            logger.error(f"Error summarizing trends: {e}")
            summary['error'] = str(e)

        return summary

    def _create_fallback_dashboard(self) -> Dict[str, Any]:
        """Create fallback dashboard for error cases"""
        return {
            'error': True,
            'message': 'Unable to generate analytics dashboard',
            'overview_metrics': {'status': 'error'},
            'performance_trends': {'status': 'error'},
            'track_analysis': {},
            'car_comparison': {},
            'consistency_analysis': {'status': 'error'},
            'lap_time_comparison': {'status': 'error'},
            'trend_analysis': {'status': 'error'},
            'session_timeline': {'timeline': [], 'total_sessions': 0},
            'improvement_tracking': {'status': 'error'},
            'professional_insights': {'performance_rating': 5.0},
            'generated_at': datetime.now().isoformat()
        }


if __name__ == "__main__":
    print("=== Performance Analytics Test ===")
    print("Analytics engine initialized")
    print("Ready for dashboard generation")
    print("=== Test Complete ===")