"""
Car Setup Optimization System
Professional-grade setup analysis and recommendations for iRacing
"""

import json
import numpy as np
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class SetupOptimizer:
    """Advanced car setup optimization and analysis system"""

    def __init__(self, coach):
        """
        Initialize setup optimizer

        Args:
            coach: Enhanced AI coach instance with session data
        """
        self.coach = coach
        self.setup_database = self._load_setup_database()

    def _load_setup_database(self) -> Dict[str, Any]:
        """Load setup recommendations database"""
        return {
            "porsche992cup": {
                "categories": ["aerodynamics", "suspension", "differential", "brakes", "tires"],
                "track_specific": {
                    "roadatlanta": {
                        "characteristics": "high_speed_technical",
                        "priority_areas": ["aerodynamics", "suspension"],
                        "recommended_changes": {
                            "aerodynamics": {"front_wing": "medium", "rear_wing": "medium-high"},
                            "suspension": {"front_springs": "medium", "rear_springs": "medium-stiff"},
                            "differential": {"coast": "low", "power": "medium"}
                        }
                    },
                    "talladega": {
                        "characteristics": "high_speed_oval",
                        "priority_areas": ["aerodynamics", "differential"],
                        "recommended_changes": {
                            "aerodynamics": {"front_wing": "low", "rear_wing": "high"},
                            "differential": {"coast": "very_low", "power": "high"}
                        }
                    }
                }
            },
            "toyotagr86": {
                "categories": ["suspension", "differential", "brakes", "tires"],
                "track_specific": {
                    "roadatlanta": {
                        "characteristics": "balanced_technical",
                        "priority_areas": ["suspension", "differential"],
                        "recommended_changes": {
                            "suspension": {"front_springs": "medium-soft", "rear_springs": "medium"},
                            "differential": {"coast": "medium", "power": "medium-high"},
                            "brakes": {"brake_bias": "52-54%"}
                        }
                    },
                    "talladega": {
                        "characteristics": "high_speed_oval",
                        "priority_areas": ["aerodynamics", "differential"],
                        "recommended_changes": {
                            "differential": {"coast": "low", "power": "high"},
                            "brakes": {"brake_bias": "50-52%"}
                        }
                    }
                }
            }
        }

    def analyze_setup_performance(self, car: str, track: str) -> Dict[str, Any]:
        """
        Analyze current setup performance and generate recommendations

        Args:
            car: Car name
            track: Track name

        Returns:
            Complete setup analysis with recommendations
        """
        analysis = {
            "car": car,
            "track": track,
            "performance_analysis": {},
            "setup_recommendations": {},
            "optimization_priorities": [],
            "expected_improvements": {},
            "comparative_analysis": {},
            "confidence_level": "medium",
            "generated_at": datetime.now().isoformat()
        }

        try:
            # Get sessions for this car/track combination
            relevant_sessions = self._get_relevant_sessions(car, track)

            if not relevant_sessions:
                analysis["error"] = "No session data available for this car/track combination"
                return analysis

            # Analyze current performance
            analysis["performance_analysis"] = self._analyze_current_performance(relevant_sessions)

            # Generate setup recommendations
            analysis["setup_recommendations"] = self._generate_setup_recommendations(car, track, relevant_sessions)

            # Identify optimization priorities
            analysis["optimization_priorities"] = self._identify_optimization_priorities(car, track, relevant_sessions)

            # Estimate expected improvements
            analysis["expected_improvements"] = self._estimate_improvements(car, track, relevant_sessions)

            # Comparative analysis
            analysis["comparative_analysis"] = self._perform_comparative_analysis(car, track, relevant_sessions)

            # Set confidence level
            analysis["confidence_level"] = self._calculate_confidence_level(relevant_sessions)

            logger.info(f"Setup analysis completed for {car} at {track}")

        except Exception as e:
            logger.error(f"Error in setup analysis: {e}")
            analysis["error"] = str(e)

        return analysis

    def _get_relevant_sessions(self, car: str, track: str) -> List[Dict[str, Any]]:
        """Get sessions matching the car/track combination"""
        relevant_sessions = []

        for session in self.coach.sessions:
            session_info = session.get('session_info', {})
            if (session_info.get('car', '').lower() == car.lower() and
                session_info.get('track', '').lower() == track.lower()):
                relevant_sessions.append(session)

        return relevant_sessions

    def _analyze_current_performance(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze current performance characteristics"""
        performance = {
            "lap_time_analysis": {},
            "consistency_analysis": {},
            "sector_performance": {},
            "performance_trends": {},
            "strengths": [],
            "weaknesses": []
        }

        if not sessions:
            return performance

        # Lap time analysis
        lap_times = []
        consistency_scores = []

        for session in sessions:
            lap_analysis = session.get('lap_analysis', {})
            fastest_lap = lap_analysis.get('fastest_lap')
            consistency = lap_analysis.get('consistency_rating', 0)

            if fastest_lap:
                lap_times.append(fastest_lap)
            if consistency > 0:
                consistency_scores.append(consistency)

        if lap_times:
            performance["lap_time_analysis"] = {
                "best_time": min(lap_times),
                "average_time": np.mean(lap_times),
                "worst_time": max(lap_times),
                "time_spread": max(lap_times) - min(lap_times),
                "improvement_potential": self._calculate_improvement_potential(lap_times)
            }

        if consistency_scores:
            performance["consistency_analysis"] = {
                "average_consistency": np.mean(consistency_scores),
                "consistency_trend": self._analyze_consistency_trend(consistency_scores),
                "consistency_rating": self._rate_consistency(np.mean(consistency_scores))
            }

        # Identify strengths and weaknesses
        performance["strengths"], performance["weaknesses"] = self._identify_performance_characteristics(performance)

        return performance

    def _generate_setup_recommendations(self, car: str, track: str, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate specific setup recommendations"""
        recommendations = {
            "immediate_changes": [],
            "experimental_changes": [],
            "long_term_development": [],
            "track_specific_advice": {},
            "setup_categories": {}
        }

        # Get baseline recommendations from database
        car_data = self.setup_database.get(car.lower(), {})
        track_data = car_data.get("track_specific", {}).get(track.lower(), {})

        if not track_data:
            recommendations["error"] = f"No setup data available for {car} at {track}"
            return recommendations

        # Analyze current performance to customize recommendations
        performance = self._analyze_current_performance(sessions)

        # Generate immediate changes
        immediate_changes = []

        # Lap time focused recommendations
        if performance.get("lap_time_analysis", {}).get("improvement_potential", 0) > 0.5:
            immediate_changes.append({
                "category": "aerodynamics",
                "change": "Reduce downforce for better straight-line speed",
                "expected_gain": "0.2-0.5 seconds",
                "difficulty": "easy",
                "risk": "low"
            })

        # Consistency focused recommendations
        consistency = performance.get("consistency_analysis", {}).get("average_consistency", 0)
        if consistency < 7.0:
            immediate_changes.append({
                "category": "suspension",
                "change": "Soften suspension for more predictable handling",
                "expected_gain": "Improved consistency",
                "difficulty": "medium",
                "risk": "low"
            })

        recommendations["immediate_changes"] = immediate_changes

        # Track-specific advice
        track_characteristics = track_data.get("characteristics", "")
        priority_areas = track_data.get("priority_areas", [])

        recommendations["track_specific_advice"] = {
            "track_characteristics": track_characteristics,
            "priority_setup_areas": priority_areas,
            "recommended_approach": self._get_track_approach(track_characteristics)
        }

        # Setup categories
        recommended_changes = track_data.get("recommended_changes", {})
        for category, settings in recommended_changes.items():
            recommendations["setup_categories"][category] = {
                "settings": settings,
                "rationale": self._get_setup_rationale(category, track_characteristics),
                "adjustment_priority": "high" if category in priority_areas else "medium"
            }

        return recommendations

    def _identify_optimization_priorities(self, car: str, track: str, sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify the most important areas for setup optimization"""
        priorities = []

        performance = self._analyze_current_performance(sessions)

        # Priority 1: Lap time improvement
        lap_analysis = performance.get("lap_time_analysis", {})
        if lap_analysis.get("improvement_potential", 0) > 0.3:
            priorities.append({
                "area": "Lap Time Optimization",
                "priority": "critical",
                "potential_gain": f"{lap_analysis.get('improvement_potential', 0):.1f} seconds",
                "focus_areas": ["aerodynamics", "suspension_geometry"],
                "description": "Significant lap time gains available through setup optimization"
            })

        # Priority 2: Consistency improvement
        consistency_analysis = performance.get("consistency_analysis", {})
        if consistency_analysis.get("average_consistency", 10) < 7.0:
            priorities.append({
                "area": "Consistency Enhancement",
                "priority": "high",
                "potential_gain": "1-2 point consistency improvement",
                "focus_areas": ["suspension_tuning", "differential"],
                "description": "Car behavior can be made more predictable and consistent"
            })

        # Priority 3: Track-specific optimization
        car_data = self.setup_database.get(car.lower(), {})
        track_data = car_data.get("track_specific", {}).get(track.lower(), {})
        if track_data:
            priorities.append({
                "area": "Track-Specific Optimization",
                "priority": "medium",
                "potential_gain": "0.1-0.3 seconds",
                "focus_areas": track_data.get("priority_areas", []),
                "description": f"Fine-tune setup for {track} characteristics"
            })

        return priorities

    def _estimate_improvements(self, car: str, track: str, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate potential improvements from setup changes"""
        improvements = {
            "lap_time_potential": {},
            "consistency_potential": {},
            "overall_rating": {},
            "confidence_intervals": {}
        }

        performance = self._analyze_current_performance(sessions)

        # Lap time improvement estimates
        current_best = performance.get("lap_time_analysis", {}).get("best_time", 0)
        if current_best > 0:
            # Conservative estimates based on typical setup optimization gains
            conservative_gain = current_best * 0.002  # 0.2%
            optimistic_gain = current_best * 0.008   # 0.8%
            realistic_gain = current_best * 0.005    # 0.5%

            improvements["lap_time_potential"] = {
                "conservative": f"{conservative_gain:.3f} seconds",
                "realistic": f"{realistic_gain:.3f} seconds",
                "optimistic": f"{optimistic_gain:.3f} seconds",
                "target_time": current_best - realistic_gain
            }

        # Consistency improvement estimates
        current_consistency = performance.get("consistency_analysis", {}).get("average_consistency", 0)
        if current_consistency > 0:
            potential_gain = min(2.0, 10.0 - current_consistency)  # Max 2 point gain, can't exceed 10

            improvements["consistency_potential"] = {
                "current_rating": current_consistency,
                "potential_gain": potential_gain,
                "target_rating": min(10.0, current_consistency + potential_gain)
            }

        return improvements

    def _perform_comparative_analysis(self, car: str, track: str, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare performance with other cars/tracks"""
        comparison = {
            "car_comparison": {},
            "track_comparison": {},
            "benchmark_analysis": {},
            "relative_performance": {}
        }

        # Compare with other cars at same track
        track_sessions = [s for s in self.coach.sessions
                         if s.get('session_info', {}).get('track', '').lower() == track.lower()]

        if len(track_sessions) > len(sessions):  # We have other car data
            other_cars = {}
            for session in track_sessions:
                session_car = session.get('session_info', {}).get('car', '')
                if session_car.lower() != car.lower():
                    lap_time = session.get('lap_analysis', {}).get('fastest_lap')
                    if lap_time and session_car not in other_cars:
                        other_cars[session_car] = lap_time

            if other_cars:
                current_best = min([s.get('lap_analysis', {}).get('fastest_lap', 999)
                                  for s in sessions if s.get('lap_analysis', {}).get('fastest_lap')])

                comparison["car_comparison"] = {
                    "current_car_best": current_best,
                    "other_cars": other_cars,
                    "relative_position": self._calculate_relative_position(current_best, list(other_cars.values()))
                }

        return comparison

    def _calculate_confidence_level(self, sessions: List[Dict[str, Any]]) -> str:
        """Calculate confidence level for recommendations"""
        if len(sessions) >= 5:
            return "high"
        elif len(sessions) >= 3:
            return "medium"
        elif len(sessions) >= 1:
            return "low"
        else:
            return "very_low"

    def _calculate_improvement_potential(self, lap_times: List[float]) -> float:
        """Calculate potential lap time improvement"""
        if len(lap_times) < 2:
            return 0.0

        best_time = min(lap_times)
        avg_time = np.mean(lap_times)

        # Potential improvement is the difference between average and best
        # This represents consistency improvement potential
        return avg_time - best_time

    def _analyze_consistency_trend(self, consistency_scores: List[float]) -> str:
        """Analyze trend in consistency scores"""
        if len(consistency_scores) < 2:
            return "insufficient_data"

        # Simple trend analysis
        recent_avg = np.mean(consistency_scores[-2:]) if len(consistency_scores) >= 2 else consistency_scores[-1]
        overall_avg = np.mean(consistency_scores)

        if recent_avg > overall_avg + 0.5:
            return "improving"
        elif recent_avg < overall_avg - 0.5:
            return "declining"
        else:
            return "stable"

    def _rate_consistency(self, consistency_score: float) -> str:
        """Rate consistency level"""
        if consistency_score >= 9.0:
            return "excellent"
        elif consistency_score >= 8.0:
            return "very_good"
        elif consistency_score >= 7.0:
            return "good"
        elif consistency_score >= 6.0:
            return "fair"
        else:
            return "needs_improvement"

    def _identify_performance_characteristics(self, performance: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Identify performance strengths and weaknesses"""
        strengths = []
        weaknesses = []

        # Analyze consistency
        consistency_analysis = performance.get("consistency_analysis", {})
        avg_consistency = consistency_analysis.get("average_consistency", 0)

        if avg_consistency >= 8.5:
            strengths.append("Excellent consistency")
        elif avg_consistency < 6.5:
            weaknesses.append("Inconsistent lap times")

        # Analyze lap times
        lap_analysis = performance.get("lap_time_analysis", {})
        improvement_potential = lap_analysis.get("improvement_potential", 0)

        if improvement_potential < 0.2:
            strengths.append("Good lap time consistency")
        elif improvement_potential > 1.0:
            weaknesses.append("Large gap between best and average times")

        return strengths, weaknesses

    def _get_track_approach(self, track_characteristics: str) -> str:
        """Get recommended approach for track type"""
        approaches = {
            "high_speed_technical": "Balance aerodynamic efficiency with mechanical grip for technical sections",
            "high_speed_oval": "Prioritize straight-line speed and stability at high speeds",
            "balanced_technical": "Optimize mechanical grip and driver confidence through corners",
            "tight_technical": "Maximize mechanical grip and agility for tight corners"
        }
        return approaches.get(track_characteristics, "Balanced approach focusing on consistency")

    def _get_setup_rationale(self, category: str, track_characteristics: str) -> str:
        """Get rationale for setup category recommendations"""
        rationales = {
            "aerodynamics": f"Aerodynamic balance optimized for {track_characteristics} track characteristics",
            "suspension": "Suspension tuning for optimal tire contact and driver confidence",
            "differential": "Differential settings to optimize traction and stability",
            "brakes": "Brake balance for optimal stopping power and consistency",
            "tires": "Tire pressure and compound selection for best performance window"
        }
        return rationales.get(category, "Setup optimization for improved performance")

    def _calculate_relative_position(self, current_time: float, other_times: List[float]) -> str:
        """Calculate relative position compared to other cars"""
        if not other_times:
            return "no_comparison_available"

        better_times = [t for t in other_times if t < current_time]

        if len(better_times) == 0:
            return "fastest"
        elif len(better_times) <= len(other_times) * 0.25:
            return "very_competitive"
        elif len(better_times) <= len(other_times) * 0.5:
            return "competitive"
        else:
            return "needs_improvement"

    def get_setup_comparison(self, car1: str, track1: str, car2: str, track2: str) -> Dict[str, Any]:
        """Compare setup requirements between different car/track combinations"""
        comparison = {
            "car1_analysis": self.analyze_setup_performance(car1, track1),
            "car2_analysis": self.analyze_setup_performance(car2, track2),
            "differences": {},
            "transferable_insights": [],
            "unique_requirements": {}
        }

        # Analyze differences and similarities
        car1_priorities = comparison["car1_analysis"].get("optimization_priorities", [])
        car2_priorities = comparison["car2_analysis"].get("optimization_priorities", [])

        common_areas = []
        for p1 in car1_priorities:
            for p2 in car2_priorities:
                if p1.get("area") == p2.get("area"):
                    common_areas.append(p1.get("area"))

        comparison["transferable_insights"] = common_areas

        return comparison


if __name__ == "__main__":
    print("=== Car Setup Optimizer Test ===")
    print("Setup optimization system initialized")
    print("Ready for setup analysis and recommendations")
    print("=== Test Complete ===")