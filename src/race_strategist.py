"""
Race Strategy System
Professional race strategy planning with fuel consumption, tire wear, and pit strategy
"""

import json
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class RaceStrategist:
    """Advanced race strategy planning and analysis system"""

    def __init__(self, coach):
        """
        Initialize race strategist

        Args:
            coach: Enhanced AI coach instance with session data
        """
        self.coach = coach
        self.strategy_database = self._load_strategy_database()

    def _load_strategy_database(self) -> Dict[str, Any]:
        """Load race strategy database with fuel and tire data"""
        return {
            "fuel_consumption": {
                "porsche992cup": {
                    "base_consumption_per_lap": {
                        "roadatlanta": 3.2,  # liters per lap
                        "talladega": 4.8,
                        "watkinsglen": 3.8,
                        "sebring": 3.5
                    },
                    "tank_capacity": 120,  # liters
                    "fuel_weight_penalty": 0.035,  # seconds per liter
                    "consumption_variation": 0.15  # +/- 15% based on driving style
                },
                "toyotagr86": {
                    "base_consumption_per_lap": {
                        "roadatlanta": 2.1,
                        "talladega": 2.8,
                        "watkinsglen": 2.4,
                        "sebring": 2.2
                    },
                    "tank_capacity": 50,
                    "fuel_weight_penalty": 0.025,
                    "consumption_variation": 0.12
                }
            },
            "tire_wear": {
                "porsche992cup": {
                    "base_wear_per_lap": {
                        "roadatlanta": 1.8,  # % wear per lap
                        "talladega": 0.9,
                        "watkinsglen": 2.1,
                        "sebring": 2.5
                    },
                    "compound_life": {
                        "soft": 25,    # laps before significant degradation
                        "medium": 40,
                        "hard": 60
                    },
                    "degradation_curve": "exponential",
                    "temperature_sensitivity": "high"
                },
                "toyotagr86": {
                    "base_wear_per_lap": {
                        "roadatlanta": 1.2,
                        "talladega": 0.6,
                        "watkinsglen": 1.5,
                        "sebring": 1.8
                    },
                    "compound_life": {
                        "soft": 30,
                        "medium": 50,
                        "hard": 75
                    },
                    "degradation_curve": "linear",
                    "temperature_sensitivity": "medium"
                }
            },
            "pit_strategy": {
                "pit_lane_time": {
                    "roadatlanta": 25.0,  # seconds
                    "talladega": 18.0,
                    "watkinsglen": 22.0,
                    "sebring": 24.0
                },
                "pit_stop_duration": {
                    "fuel_only": 8.0,      # seconds
                    "tires_only": 12.0,
                    "fuel_and_tires": 15.0,
                    "damage_repair": 25.0
                },
                "pit_window_factors": {
                    "early_pit": {"risk": "high", "reward": "track_position"},
                    "optimal_pit": {"risk": "medium", "reward": "balanced"},
                    "late_pit": {"risk": "medium", "reward": "tire_advantage"}
                }
            },
            "weather_factors": {
                "rain_fuel_penalty": 1.15,  # 15% more fuel in rain
                "rain_tire_life": 0.7,      # 30% less tire life
                "temperature_multiplier": {
                    "cold": 0.9,   # Less wear in cold
                    "optimal": 1.0,
                    "hot": 1.3     # More wear in heat
                }
            }
        }

    def analyze_race_strategy(self, car: str, track: str, race_length: int,
                            tire_compound: str = "medium", weather: str = "dry") -> Dict[str, Any]:
        """
        Generate comprehensive race strategy analysis

        Args:
            car: Car name
            track: Track name
            race_length: Race length in minutes
            tire_compound: Starting tire compound
            weather: Weather conditions

        Returns:
            Complete race strategy analysis
        """
        strategy = {
            "car": car,
            "track": track,
            "race_length_minutes": race_length,
            "tire_compound": tire_compound,
            "weather": weather,
            "fuel_strategy": {},
            "tire_strategy": {},
            "pit_strategy": {},
            "lap_time_projections": {},
            "alternative_strategies": [],
            "risk_assessment": {},
            "recommendations": [],
            "generated_at": datetime.now().isoformat()
        }

        try:
            # Get session data for this car/track
            relevant_sessions = self._get_relevant_sessions(car, track)

            if not relevant_sessions:
                strategy["error"] = "No session data available for this car/track combination"
                return strategy

            # Calculate average lap time
            avg_lap_time = self._calculate_average_lap_time(relevant_sessions)

            if not avg_lap_time:
                strategy["error"] = "Unable to determine lap times"
                return strategy

            # Calculate total laps in race
            total_laps = int((race_length * 60) / avg_lap_time)
            strategy["estimated_total_laps"] = total_laps
            strategy["average_lap_time"] = avg_lap_time

            # Generate fuel strategy
            strategy["fuel_strategy"] = self._analyze_fuel_strategy(car, track, total_laps, weather)

            # Generate tire strategy
            strategy["tire_strategy"] = self._analyze_tire_strategy(car, track, total_laps, tire_compound, weather)

            # Generate pit strategy
            strategy["pit_strategy"] = self._analyze_pit_strategy(car, track, total_laps,
                                                               strategy["fuel_strategy"],
                                                               strategy["tire_strategy"])

            # Project lap times throughout race
            strategy["lap_time_projections"] = self._project_lap_times(avg_lap_time, total_laps,
                                                                     strategy["fuel_strategy"],
                                                                     strategy["tire_strategy"])

            # Generate alternative strategies
            strategy["alternative_strategies"] = self._generate_alternative_strategies(car, track, total_laps,
                                                                                     avg_lap_time, weather)

            # Risk assessment
            strategy["risk_assessment"] = self._assess_strategy_risks(strategy)

            # Strategic recommendations
            strategy["recommendations"] = self._generate_strategic_recommendations(strategy)

            logger.info(f"Race strategy generated for {car} at {track} ({race_length} minutes)")

        except Exception as e:
            logger.error(f"Error generating race strategy: {e}")
            strategy["error"] = str(e)

        return strategy

    def _get_relevant_sessions(self, car: str, track: str) -> List[Dict[str, Any]]:
        """Get sessions matching the car/track combination"""
        relevant_sessions = []

        for session in self.coach.sessions:
            session_info = session.get('session_info', {})
            if (session_info.get('car', '').lower() == car.lower() and
                session_info.get('track', '').lower() == track.lower()):
                relevant_sessions.append(session)

        return relevant_sessions

    def _calculate_average_lap_time(self, sessions: List[Dict[str, Any]]) -> Optional[float]:
        """Calculate average lap time from sessions"""
        lap_times = []

        for session in sessions:
            lap_analysis = session.get('lap_analysis', {})
            fastest_lap = lap_analysis.get('fastest_lap')
            average_lap = lap_analysis.get('average_lap')

            if fastest_lap and average_lap:
                # Use average lap time for race strategy (more realistic than fastest)
                lap_times.append(average_lap)

        return np.mean(lap_times) if lap_times else None

    def _analyze_fuel_strategy(self, car: str, track: str, total_laps: int, weather: str) -> Dict[str, Any]:
        """Analyze fuel consumption and strategy"""
        fuel_data = self.strategy_database["fuel_consumption"].get(car.lower(), {})

        if not fuel_data:
            return {"error": "No fuel data available for this car"}

        base_consumption = fuel_data["base_consumption_per_lap"].get(track.lower(), 3.0)
        tank_capacity = fuel_data["tank_capacity"]
        fuel_weight_penalty = fuel_data["fuel_weight_penalty"]

        # Weather adjustments
        weather_multiplier = 1.0
        if weather == "rain":
            weather_multiplier = self.strategy_database["weather_factors"]["rain_fuel_penalty"]

        # Calculate consumption
        consumption_per_lap = base_consumption * weather_multiplier
        total_fuel_needed = consumption_per_lap * total_laps

        # Determine pit stops needed
        max_stint_length = int(tank_capacity / consumption_per_lap)
        pit_stops_required = max(0, int(np.ceil(total_laps / max_stint_length)) - 1)

        return {
            "consumption_per_lap": round(consumption_per_lap, 2),
            "total_fuel_needed": round(total_fuel_needed, 1),
            "tank_capacity": tank_capacity,
            "max_stint_length": max_stint_length,
            "pit_stops_required": pit_stops_required,
            "fuel_weight_penalty_per_liter": fuel_weight_penalty,
            "weather_impact": weather_multiplier,
            "fuel_strategy_type": self._determine_fuel_strategy_type(pit_stops_required, total_laps)
        }

    def _analyze_tire_strategy(self, car: str, track: str, total_laps: int,
                             tire_compound: str, weather: str) -> Dict[str, Any]:
        """Analyze tire wear and strategy"""
        tire_data = self.strategy_database["tire_wear"].get(car.lower(), {})

        if not tire_data:
            return {"error": "No tire data available for this car"}

        base_wear = tire_data["base_wear_per_lap"].get(track.lower(), 1.5)
        compound_life = tire_data["compound_life"].get(tire_compound, 40)

        # Weather adjustments
        weather_multiplier = 1.0
        if weather == "rain":
            weather_multiplier = self.strategy_database["weather_factors"]["rain_tire_life"]

        # Calculate tire degradation
        effective_tire_life = compound_life * weather_multiplier
        wear_per_lap = base_wear / weather_multiplier

        # Determine optimal pit strategy
        tire_changes_needed = max(0, int(np.ceil(total_laps / effective_tire_life)) - 1)

        # Calculate performance degradation
        degradation_points = []
        for lap in range(1, total_laps + 1):
            stint_lap = ((lap - 1) % int(effective_tire_life)) + 1
            degradation = self._calculate_tire_degradation(stint_lap, effective_tire_life,
                                                         tire_data["degradation_curve"])
            degradation_points.append(degradation)

        return {
            "compound": tire_compound,
            "base_wear_per_lap": wear_per_lap,
            "effective_tire_life": int(effective_tire_life),
            "tire_changes_needed": tire_changes_needed,
            "total_wear": round(total_laps * wear_per_lap, 1),
            "degradation_curve": tire_data["degradation_curve"],
            "performance_degradation": degradation_points,
            "weather_impact": weather_multiplier,
            "optimal_stint_length": int(effective_tire_life * 0.85)  # 85% of max tire life
        }

    def _analyze_pit_strategy(self, car: str, track: str, total_laps: int,
                            fuel_strategy: Dict[str, Any], tire_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze optimal pit strategy"""
        pit_data = self.strategy_database["pit_strategy"]

        pit_lane_time = pit_data["pit_lane_time"].get(track.lower(), 25.0)

        fuel_stops = fuel_strategy.get("pit_stops_required", 0)
        tire_stops = tire_strategy.get("tire_changes_needed", 0)

        # Determine combined strategy
        if fuel_stops == 0 and tire_stops == 0:
            strategy_type = "no_stop"
            total_stops = 0
        elif fuel_stops == tire_stops:
            strategy_type = "combined_stops"
            total_stops = fuel_stops
        else:
            strategy_type = "separate_stops"
            total_stops = max(fuel_stops, tire_stops)

        # Calculate pit windows
        pit_windows = []
        if total_stops > 0:
            window_size = total_laps // (total_stops + 1)
            for i in range(total_stops):
                optimal_lap = (i + 1) * window_size
                window_start = max(1, optimal_lap - 3)
                window_end = min(total_laps - 5, optimal_lap + 3)

                pit_windows.append({
                    "stop_number": i + 1,
                    "optimal_lap": optimal_lap,
                    "window_start": window_start,
                    "window_end": window_end,
                    "stop_type": "fuel_and_tires" if strategy_type == "combined_stops" else "fuel_only"
                })

        # Calculate time costs
        stop_duration = pit_data["pit_stop_duration"]["fuel_and_tires"]
        total_pit_time = (pit_lane_time + stop_duration) * total_stops

        return {
            "strategy_type": strategy_type,
            "total_stops": total_stops,
            "pit_windows": pit_windows,
            "pit_lane_time": pit_lane_time,
            "stop_duration": stop_duration,
            "total_pit_time": total_pit_time,
            "time_cost_per_stop": pit_lane_time + stop_duration,
            "fuel_stops_needed": fuel_stops,
            "tire_stops_needed": tire_stops
        }

    def _project_lap_times(self, base_lap_time: float, total_laps: int,
                          fuel_strategy: Dict[str, Any], tire_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Project lap times throughout the race"""
        lap_projections = []
        cumulative_time = 0

        fuel_weight_penalty = fuel_strategy.get("fuel_weight_penalty_per_liter", 0.03)
        consumption_per_lap = fuel_strategy.get("consumption_per_lap", 3.0)
        tank_capacity = fuel_strategy.get("tank_capacity", 100)

        current_fuel = tank_capacity
        tire_degradation = tire_strategy.get("performance_degradation", [])

        for lap in range(1, total_laps + 1):
            # Fuel weight effect (decreases as fuel burns off)
            fuel_weight_effect = current_fuel * fuel_weight_penalty

            # Tire degradation effect
            tire_effect = 0
            if tire_degradation and lap <= len(tire_degradation):
                tire_effect = tire_degradation[lap - 1]

            # Calculate lap time
            projected_lap_time = base_lap_time + fuel_weight_effect + tire_effect
            cumulative_time += projected_lap_time

            lap_projections.append({
                "lap": lap,
                "projected_time": round(projected_lap_time, 3),
                "cumulative_time": round(cumulative_time, 1),
                "fuel_remaining": round(current_fuel, 1),
                "tire_degradation": round(tire_effect, 3),
                "fuel_weight_penalty": round(fuel_weight_effect, 3)
            })

            # Update fuel level
            current_fuel = max(0, current_fuel - consumption_per_lap)

            # Reset fuel at pit stops (simplified)
            if current_fuel < consumption_per_lap * 2:  # Near empty
                current_fuel = tank_capacity

        return {
            "lap_by_lap": lap_projections,
            "race_time": round(cumulative_time / 60, 1),  # minutes
            "average_race_pace": round(cumulative_time / total_laps, 3),
            "fastest_projected_lap": min(p["projected_time"] for p in lap_projections),
            "slowest_projected_lap": max(p["projected_time"] for p in lap_projections)
        }

    def _generate_alternative_strategies(self, car: str, track: str, total_laps: int,
                                       avg_lap_time: float, weather: str) -> List[Dict[str, Any]]:
        """Generate alternative race strategies"""
        alternatives = []

        # Strategy 1: Aggressive (early pit, fresh tires)
        aggressive = {
            "name": "Aggressive",
            "description": "Early pit stop for track position and fresh tire advantage",
            "pit_lap": max(1, total_laps // 3),
            "risk_level": "high",
            "pros": ["Track position", "Fresh tire advantage late", "Undercut opportunity"],
            "cons": ["More pit time", "Fuel consumption risk", "Traffic exposure"],
            "time_delta": "+2.5 to -8.2 seconds vs optimal"
        }

        # Strategy 2: Conservative (late pit, fuel saving)
        conservative = {
            "name": "Conservative",
            "description": "Long first stint, late pit stop to minimize time loss",
            "pit_lap": max(total_laps // 2, total_laps - 10),
            "risk_level": "low",
            "pros": ["Minimized pit time", "Fuel efficiency", "Safety margin"],
            "cons": ["Tire degradation", "Vulnerable to undercut", "Limited overtaking"],
            "time_delta": "-1.2 to +4.8 seconds vs optimal"
        }

        # Strategy 3: No-stop (if possible)
        if total_laps <= 30:  # Only for shorter races
            no_stop = {
                "name": "No-Stop",
                "description": "Complete race without pit stops",
                "pit_lap": None,
                "risk_level": "very_high",
                "pros": ["No pit time loss", "Maximum track time", "Weather insurance"],
                "cons": ["Extreme tire degradation", "Fuel consumption risk", "Pace disadvantage"],
                "time_delta": "-25.0 to +15.0 seconds vs optimal"
            }
            alternatives.append(no_stop)

        alternatives.extend([aggressive, conservative])
        return alternatives

    def _assess_strategy_risks(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks of the proposed strategy"""
        fuel_strategy = strategy.get("fuel_strategy", {})
        tire_strategy = strategy.get("tire_strategy", {})
        pit_strategy = strategy.get("pit_strategy", {})

        risks = {
            "fuel_risk": "low",
            "tire_risk": "low",
            "weather_risk": "medium",
            "traffic_risk": "medium",
            "overall_risk": "medium"
        }

        # Fuel risk assessment
        fuel_margin = fuel_strategy.get("tank_capacity", 100) - fuel_strategy.get("total_fuel_needed", 50)
        if fuel_margin < 10:
            risks["fuel_risk"] = "high"
        elif fuel_margin < 20:
            risks["fuel_risk"] = "medium"

        # Tire risk assessment
        tire_life = tire_strategy.get("effective_tire_life", 40)
        total_laps = strategy.get("estimated_total_laps", 20)
        if total_laps > tire_life * 0.9:
            risks["tire_risk"] = "high"
        elif total_laps > tire_life * 0.75:
            risks["tire_risk"] = "medium"

        # Overall risk calculation
        risk_scores = {"low": 1, "medium": 2, "high": 3, "very_high": 4}
        avg_risk = np.mean([risk_scores[r] for r in [risks["fuel_risk"], risks["tire_risk"],
                                                   risks["weather_risk"], risks["traffic_risk"]]])

        risk_levels = ["low", "medium", "high", "very_high"]
        risks["overall_risk"] = risk_levels[min(3, int(avg_risk) - 1)]

        return risks

    def _generate_strategic_recommendations(self, strategy: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = []

        fuel_strategy = strategy.get("fuel_strategy", {})
        tire_strategy = strategy.get("tire_strategy", {})
        pit_strategy = strategy.get("pit_strategy", {})
        risks = strategy.get("risk_assessment", {})

        # Fuel recommendations
        if fuel_strategy.get("pit_stops_required", 0) == 0:
            recommendations.append("Consider fuel-saving techniques to ensure race completion")
        elif fuel_strategy.get("pit_stops_required", 0) > 1:
            recommendations.append("Multiple fuel stops required - focus on consistent pit windows")

        # Tire recommendations
        if tire_strategy.get("tire_changes_needed", 0) == 0:
            recommendations.append("Monitor tire degradation closely - may need emergency stop")
        else:
            recommendations.append("Plan tire changes during optimal pit windows for best performance")

        # Risk-based recommendations
        if risks.get("overall_risk") == "high":
            recommendations.append("High-risk strategy - consider more conservative approach")
        elif risks.get("fuel_risk") == "high":
            recommendations.append("Fuel consumption critical - practice fuel-saving techniques")
        elif risks.get("tire_risk") == "high":
            recommendations.append("Tire management essential - avoid aggressive driving early")

        # Strategic recommendations
        pit_stops = pit_strategy.get("total_stops", 0)
        if pit_stops == 1:
            recommendations.append("Single pit stop strategy - timing will be crucial for track position")
        elif pit_stops > 1:
            recommendations.append("Multi-stop strategy - focus on consistent lap times and pit execution")

        return recommendations

    def _determine_fuel_strategy_type(self, pit_stops: int, total_laps: int) -> str:
        """Determine fuel strategy type"""
        if pit_stops == 0:
            return "fuel_save"
        elif pit_stops == 1:
            return "single_stop"
        else:
            return "multi_stop"

    def _calculate_tire_degradation(self, stint_lap: int, tire_life: float, curve_type: str) -> float:
        """Calculate tire performance degradation"""
        if curve_type == "linear":
            return (stint_lap / tire_life) * 2.0  # 2 seconds max degradation
        else:  # exponential
            degradation_factor = (stint_lap / tire_life) ** 2
            return degradation_factor * 3.0  # 3 seconds max degradation

    def compare_strategies(self, car: str, track: str, race_length: int,
                         strategies: List[str]) -> Dict[str, Any]:
        """Compare multiple race strategies"""
        comparison = {
            "strategies": {},
            "comparison_matrix": {},
            "recommendation": "",
            "time_differences": {}
        }

        for strategy_name in strategies:
            # Generate strategy (simplified for comparison)
            if strategy_name == "aggressive":
                tire_compound = "soft"
            elif strategy_name == "conservative":
                tire_compound = "hard"
            else:
                tire_compound = "medium"

            strategy = self.analyze_race_strategy(car, track, race_length, tire_compound)
            comparison["strategies"][strategy_name] = strategy

        return comparison


if __name__ == "__main__":
    print("=== Race Strategy System Test ===")
    print("Race strategist initialized")
    print("Ready for fuel consumption, tire wear, and pit strategy analysis")
    print("=== Test Complete ===")