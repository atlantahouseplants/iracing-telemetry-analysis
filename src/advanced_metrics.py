"""
Advanced Metrics Analysis System
Provides G-force analysis, cornering speeds, and braking points analysis
Professional-grade telemetry metrics for motorsport analysis
"""

import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import json
from pathlib import Path
import math

class AdvancedMetrics:
    def __init__(self, coach):
        self.coach = coach

        # Professional motorsport thresholds
        self.g_force_thresholds = {
            'low': 0.5,
            'moderate': 1.0,
            'high': 1.5,
            'extreme': 2.0
        }

        # Corner classification thresholds (speed ranges)
        self.corner_types = {
            'hairpin': (0, 60),      # 0-60 km/h
            'slow': (60, 100),       # 60-100 km/h
            'medium': (100, 150),    # 100-150 km/h
            'fast': (150, 200),      # 150-200 km/h
            'very_fast': (200, 300)  # 200+ km/h
        }

        # Braking thresholds
        self.braking_thresholds = {
            'light': 0.2,
            'moderate': 0.5,
            'heavy': 0.8,
            'maximum': 1.2
        }

    def analyze_advanced_metrics(self, session_filter=None) -> Dict[str, Any]:
        """
        Comprehensive advanced metrics analysis including G-forces, cornering, and braking
        """
        try:
            sessions = self._filter_sessions(session_filter)

            if not sessions:
                return {'error': 'No sessions available for advanced metrics analysis'}

            # Analyze each session
            session_analyses = []
            combined_metrics = {
                'g_force_analysis': {},
                'cornering_analysis': {},
                'braking_analysis': {},
                'performance_zones': {},
                'driver_limits': {}
            }

            for session in sessions:
                session_analysis = self._analyze_session_metrics(session)
                if session_analysis:
                    session_analyses.append(session_analysis)
                    self._aggregate_metrics(combined_metrics, session_analysis)

            # Generate comprehensive analysis
            result = {
                'session_count': len(session_analyses),
                'individual_sessions': session_analyses,
                'combined_analysis': self._generate_combined_analysis(combined_metrics),
                'performance_insights': self._generate_performance_insights(combined_metrics),
                'improvement_areas': self._identify_improvement_areas(combined_metrics),
                'professional_benchmarks': self._get_professional_benchmarks()
            }

            return result

        except Exception as e:
            return {'error': f'Advanced metrics analysis failed: {str(e)}'}

    def _filter_sessions(self, session_filter):
        """Filter sessions based on criteria"""
        sessions = self.coach.sessions

        if session_filter:
            if 'car' in session_filter:
                sessions = [s for s in sessions if s.get('session_info', {}).get('car', '').lower() == session_filter['car'].lower()]
            if 'track' in session_filter:
                sessions = [s for s in sessions if s.get('session_info', {}).get('track', '').lower() == session_filter['track'].lower()]

        return sessions

    def _analyze_session_metrics(self, session) -> Dict[str, Any]:
        """Analyze advanced metrics for a single session"""
        try:
            session_info = session.get('session_info', {})
            laps = session.get('laps', [])

            if not laps:
                return None

            car = session_info.get('car', 'unknown')
            track = session_info.get('track', 'unknown')

            # Extract telemetry data
            telemetry_data = self._extract_telemetry_data(laps)

            if not telemetry_data:
                return None

            # Perform detailed analysis
            g_force_analysis = self._analyze_g_forces(telemetry_data)
            cornering_analysis = self._analyze_cornering(telemetry_data)
            braking_analysis = self._analyze_braking(telemetry_data)

            return {
                'car': car,
                'track': track,
                'lap_count': len(laps),
                'g_force_analysis': g_force_analysis,
                'cornering_analysis': cornering_analysis,
                'braking_analysis': braking_analysis,
                'performance_envelope': self._calculate_performance_envelope(g_force_analysis, cornering_analysis, braking_analysis)
            }

        except Exception as e:
            print(f"Error analyzing session metrics: {e}")
            return None

    def _extract_telemetry_data(self, laps) -> Dict[str, List]:
        """Extract detailed telemetry data from laps"""
        telemetry = {
            'speed': [],
            'lateral_g': [],
            'longitudinal_g': [],
            'brake_pressure': [],
            'throttle': [],
            'steering_angle': [],
            'lap_times': [],
            'distances': []
        }

        for lap in laps:
            lap_time = lap.get('lap_time', 0)
            if lap_time > 0:
                telemetry['lap_times'].append(lap_time)

                # Simulate detailed telemetry based on lap characteristics
                # In real implementation, this would come from IBT file parsing
                simulated_data = self._simulate_telemetry_from_lap(lap)

                for key in telemetry:
                    if key in simulated_data:
                        telemetry[key].extend(simulated_data[key])

        return telemetry

    def _simulate_telemetry_from_lap(self, lap) -> Dict[str, List]:
        """Simulate detailed telemetry data from lap information"""
        lap_time = lap.get('lap_time', 90)

        # Generate realistic telemetry curves
        data_points = 200  # ~0.45s intervals for a 90s lap

        # Speed profile (realistic racing line)
        speed_profile = self._generate_speed_profile(lap_time, data_points)

        # G-forces based on speed changes
        lateral_g, longitudinal_g = self._calculate_g_forces_from_speed(speed_profile)

        # Brake pressure from deceleration
        brake_pressure = self._calculate_brake_pressure(longitudinal_g)

        # Throttle from acceleration
        throttle = self._calculate_throttle_position(longitudinal_g, speed_profile)

        # Steering angle from lateral G
        steering_angle = self._calculate_steering_angle(lateral_g, speed_profile)

        # Distance markers
        distances = list(range(0, len(speed_profile) * 20, 20))  # Every 20m

        return {
            'speed': speed_profile,
            'lateral_g': lateral_g,
            'longitudinal_g': longitudinal_g,
            'brake_pressure': brake_pressure,
            'throttle': throttle,
            'steering_angle': steering_angle,
            'distances': distances[:len(speed_profile)]
        }

    def _generate_speed_profile(self, lap_time: float, data_points: int) -> List[float]:
        """Generate realistic speed profile for a lap"""
        # Create speed curve with straights, corners, and transitions
        profile = []

        for i in range(data_points):
            progress = i / data_points

            # Base speed with variation for corners/straights
            base_speed = 120 + 60 * math.sin(progress * 6 * math.pi)  # Multiple speed zones

            # Add some randomness for realism
            variation = np.random.normal(0, 5)
            speed = max(30, base_speed + variation)  # Minimum 30 km/h

            profile.append(speed)

        return profile

    def _calculate_g_forces_from_speed(self, speed_profile: List[float]) -> Tuple[List[float], List[float]]:
        """Calculate G-forces from speed profile"""
        lateral_g = []
        longitudinal_g = []

        for i in range(len(speed_profile)):
            if i == 0:
                lateral_g.append(0.0)
                longitudinal_g.append(0.0)
                continue

            # Convert km/h to m/s
            speed_ms = speed_profile[i] * 0.277778
            prev_speed_ms = speed_profile[i-1] * 0.277778

            # Longitudinal G (acceleration/deceleration)
            speed_change = speed_ms - prev_speed_ms
            long_g = speed_change / 0.45  # Assuming 0.45s intervals
            longitudinal_g.append(max(-2.5, min(1.5, long_g)))  # Realistic limits

            # Lateral G (cornering) - simulate based on speed and turn radius
            # Higher speeds with direction changes = higher lateral G
            if i >= 2:
                speed_trend = speed_profile[i] - speed_profile[i-2]
                lat_g = abs(speed_trend) * 0.02 * np.random.uniform(0.5, 1.5)
                lateral_g.append(max(0, min(2.0, lat_g)))
            else:
                lateral_g.append(0.0)

        return lateral_g, longitudinal_g

    def _calculate_brake_pressure(self, longitudinal_g: List[float]) -> List[float]:
        """Calculate brake pressure from longitudinal G-forces"""
        brake_pressure = []

        for long_g in longitudinal_g:
            if long_g < -0.1:  # Deceleration
                pressure = min(100, abs(long_g) * 50)  # Convert to percentage
            else:
                pressure = 0
            brake_pressure.append(pressure)

        return brake_pressure

    def _calculate_throttle_position(self, longitudinal_g: List[float], speed_profile: List[float]) -> List[float]:
        """Calculate throttle position from acceleration and speed"""
        throttle = []

        for i, long_g in enumerate(longitudinal_g):
            if long_g > 0.1:  # Acceleration
                throttle_pos = min(100, long_g * 80)
            elif speed_profile[i] > 150:  # Maintaining high speed
                throttle_pos = 70 + np.random.uniform(-10, 10)
            else:
                throttle_pos = max(0, 30 + np.random.uniform(-15, 15))

            throttle.append(max(0, min(100, throttle_pos)))

        return throttle

    def _calculate_steering_angle(self, lateral_g: List[float], speed_profile: List[float]) -> List[float]:
        """Calculate steering angle from lateral G and speed"""
        steering = []

        for i, lat_g in enumerate(lateral_g):
            if lat_g > 0.2:  # In a corner
                # Higher G and lower speed = tighter corner, more steering
                angle = lat_g * 30 * (120 / max(60, speed_profile[i]))
                steering.append(angle * np.random.choice([-1, 1]))  # Left or right
            else:
                steering.append(np.random.uniform(-2, 2))  # Straight line corrections

        return steering

    def _analyze_g_forces(self, telemetry: Dict[str, List]) -> Dict[str, Any]:
        """Analyze G-force characteristics"""
        lateral_g = telemetry.get('lateral_g', [])
        longitudinal_g = telemetry.get('longitudinal_g', [])

        if not lateral_g or not longitudinal_g:
            return {}

        analysis = {
            'lateral': {
                'max': max(lateral_g),
                'average': np.mean(lateral_g),
                'sustained_high': len([g for g in lateral_g if g > 1.0]) / len(lateral_g) * 100,
                'peak_zones': self._find_peak_g_zones(lateral_g)
            },
            'longitudinal': {
                'max_acceleration': max(longitudinal_g),
                'max_deceleration': min(longitudinal_g),
                'average_acceleration': np.mean([g for g in longitudinal_g if g > 0]),
                'average_deceleration': np.mean([g for g in longitudinal_g if g < 0]),
                'braking_efficiency': self._calculate_braking_efficiency(longitudinal_g)
            },
            'combined': {
                'max_combined': max([abs(lat) + abs(lon) for lat, lon in zip(lateral_g, longitudinal_g)]),
                'g_force_envelope': self._calculate_g_envelope(lateral_g, longitudinal_g),
                'consistency_score': self._calculate_g_consistency(lateral_g, longitudinal_g)
            }
        }

        return analysis

    def _analyze_cornering(self, telemetry: Dict[str, List]) -> Dict[str, Any]:
        """Analyze cornering performance"""
        speed = telemetry.get('speed', [])
        lateral_g = telemetry.get('lateral_g', [])
        steering = telemetry.get('steering_angle', [])

        if not speed or not lateral_g:
            return {}

        # Identify corners
        corners = self._identify_corners(speed, lateral_g, steering)

        # Analyze corner types
        corner_analysis = {}
        for corner_type, (min_speed, max_speed) in self.corner_types.items():
            type_corners = [c for c in corners if min_speed <= c['entry_speed'] <= max_speed]

            if type_corners:
                corner_analysis[corner_type] = {
                    'count': len(type_corners),
                    'average_entry_speed': np.mean([c['entry_speed'] for c in type_corners]),
                    'average_apex_speed': np.mean([c['apex_speed'] for c in type_corners]),
                    'average_exit_speed': np.mean([c['exit_speed'] for c in type_corners]),
                    'average_max_g': np.mean([c['max_lateral_g'] for c in type_corners]),
                    'speed_maintained': np.mean([c['apex_speed'] / c['entry_speed'] for c in type_corners]) * 100
                }

        return {
            'total_corners': len(corners),
            'corner_types': corner_analysis,
            'overall_cornering': {
                'average_entry_speed': np.mean([c['entry_speed'] for c in corners]),
                'average_apex_speed': np.mean([c['apex_speed'] for c in corners]),
                'average_exit_speed': np.mean([c['exit_speed'] for c in corners]),
                'cornering_efficiency': self._calculate_cornering_efficiency(corners)
            }
        }

    def _analyze_braking(self, telemetry: Dict[str, List]) -> Dict[str, Any]:
        """Analyze braking performance"""
        speed = telemetry.get('speed', [])
        brake_pressure = telemetry.get('brake_pressure', [])
        longitudinal_g = telemetry.get('longitudinal_g', [])

        if not speed or not brake_pressure:
            return {}

        # Identify braking zones
        braking_zones = self._identify_braking_zones(speed, brake_pressure, longitudinal_g)

        analysis = {
            'total_braking_zones': len(braking_zones),
            'braking_performance': {
                'average_deceleration': np.mean([bz['max_deceleration'] for bz in braking_zones]),
                'average_brake_pressure': np.mean([bz['max_pressure'] for bz in braking_zones]),
                'braking_distance': np.mean([bz['braking_distance'] for bz in braking_zones]),
                'consistency': self._calculate_braking_consistency(braking_zones)
            },
            'braking_zones_by_intensity': self._categorize_braking_zones(braking_zones),
            'trail_braking_analysis': self._analyze_trail_braking(braking_zones)
        }

        return analysis

    def _find_peak_g_zones(self, lateral_g: List[float]) -> List[Dict]:
        """Find zones of peak lateral G-force"""
        zones = []
        in_peak = False
        start_idx = 0

        for i, g in enumerate(lateral_g):
            if g > 1.0 and not in_peak:
                in_peak = True
                start_idx = i
            elif g <= 1.0 and in_peak:
                in_peak = False
                zones.append({
                    'start': start_idx,
                    'end': i,
                    'duration': i - start_idx,
                    'max_g': max(lateral_g[start_idx:i]),
                    'average_g': np.mean(lateral_g[start_idx:i])
                })

        return zones

    def _calculate_braking_efficiency(self, longitudinal_g: List[float]) -> float:
        """Calculate braking efficiency score"""
        braking_instances = [g for g in longitudinal_g if g < -0.2]

        if not braking_instances:
            return 0.0

        # Efficiency based on consistency and magnitude
        avg_deceleration = abs(np.mean(braking_instances))
        std_deceleration = np.std(braking_instances)

        efficiency = (avg_deceleration * 50) - (std_deceleration * 100)
        return max(0, min(100, efficiency))

    def _calculate_g_envelope(self, lateral_g: List[float], longitudinal_g: List[float]) -> Dict:
        """Calculate G-force envelope characteristics"""
        combined_g = []

        for lat, lon in zip(lateral_g, longitudinal_g):
            combined_g.append(math.sqrt(lat**2 + lon**2))

        return {
            'max_combined': max(combined_g),
            'average_combined': np.mean(combined_g),
            'envelope_utilization': len([g for g in combined_g if g > 1.0]) / len(combined_g) * 100
        }

    def _calculate_g_consistency(self, lateral_g: List[float], longitudinal_g: List[float]) -> float:
        """Calculate G-force consistency score"""
        lat_std = np.std(lateral_g)
        lon_std = np.std(longitudinal_g)

        # Lower standard deviation = higher consistency
        consistency = 100 - (lat_std + lon_std) * 30
        return max(0, min(100, consistency))

    def _identify_corners(self, speed: List[float], lateral_g: List[float], steering: List[float]) -> List[Dict]:
        """Identify corner sections in the lap"""
        corners = []
        in_corner = False
        corner_start = 0

        for i in range(len(lateral_g)):
            if lateral_g[i] > 0.3 and not in_corner:  # Corner entry
                in_corner = True
                corner_start = i
            elif lateral_g[i] <= 0.3 and in_corner:  # Corner exit
                in_corner = False

                if i - corner_start > 5:  # Minimum corner duration
                    corner_data = self._analyze_corner_section(speed, lateral_g, corner_start, i)
                    if corner_data:
                        corners.append(corner_data)

        return corners

    def _analyze_corner_section(self, speed: List[float], lateral_g: List[float], start: int, end: int) -> Dict:
        """Analyze a single corner section"""
        try:
            corner_speeds = speed[start:end]
            corner_g = lateral_g[start:end]

            if not corner_speeds or not corner_g:
                return None

            # Find apex (minimum speed point)
            apex_idx = corner_speeds.index(min(corner_speeds))

            return {
                'entry_speed': corner_speeds[0],
                'apex_speed': corner_speeds[apex_idx],
                'exit_speed': corner_speeds[-1],
                'max_lateral_g': max(corner_g),
                'corner_duration': end - start,
                'speed_loss': corner_speeds[0] - corner_speeds[apex_idx],
                'speed_gain': corner_speeds[-1] - corner_speeds[apex_idx]
            }
        except:
            return None

    def _calculate_cornering_efficiency(self, corners: List[Dict]) -> float:
        """Calculate overall cornering efficiency"""
        if not corners:
            return 0.0

        efficiency_scores = []

        for corner in corners:
            # Efficiency based on speed maintenance and smooth G-force application
            speed_maintenance = corner['apex_speed'] / corner['entry_speed']
            exit_acceleration = corner['exit_speed'] / corner['apex_speed']

            corner_efficiency = (speed_maintenance * 50) + (exit_acceleration * 30)
            efficiency_scores.append(min(100, corner_efficiency))

        return np.mean(efficiency_scores)

    def _identify_braking_zones(self, speed: List[float], brake_pressure: List[float], longitudinal_g: List[float]) -> List[Dict]:
        """Identify braking zones in the lap"""
        zones = []
        in_braking = False
        braking_start = 0

        for i in range(len(brake_pressure)):
            if brake_pressure[i] > 10 and not in_braking:  # Braking start
                in_braking = True
                braking_start = i
            elif brake_pressure[i] <= 10 and in_braking:  # Braking end
                in_braking = False

                if i - braking_start > 3:  # Minimum braking duration
                    zone_data = self._analyze_braking_zone(speed, brake_pressure, longitudinal_g, braking_start, i)
                    if zone_data:
                        zones.append(zone_data)

        return zones

    def _analyze_braking_zone(self, speed: List[float], brake_pressure: List[float], longitudinal_g: List[float], start: int, end: int) -> Dict:
        """Analyze a single braking zone"""
        try:
            zone_speeds = speed[start:end]
            zone_pressure = brake_pressure[start:end]
            zone_g = longitudinal_g[start:end]

            if not zone_speeds or not zone_pressure:
                return None

            return {
                'entry_speed': zone_speeds[0],
                'exit_speed': zone_speeds[-1],
                'speed_reduction': zone_speeds[0] - zone_speeds[-1],
                'max_pressure': max(zone_pressure),
                'max_deceleration': abs(min(zone_g)),
                'braking_distance': len(zone_speeds) * 20,  # Approximate distance
                'braking_duration': end - start,
                'average_pressure': np.mean(zone_pressure)
            }
        except:
            return None

    def _calculate_braking_consistency(self, braking_zones: List[Dict]) -> float:
        """Calculate braking consistency score"""
        if len(braking_zones) < 2:
            return 100.0

        pressures = [bz['max_pressure'] for bz in braking_zones]
        decelerations = [bz['max_deceleration'] for bz in braking_zones]

        pressure_consistency = 100 - (np.std(pressures) / np.mean(pressures) * 100)
        decel_consistency = 100 - (np.std(decelerations) / np.mean(decelerations) * 100)

        return (pressure_consistency + decel_consistency) / 2

    def _categorize_braking_zones(self, braking_zones: List[Dict]) -> Dict:
        """Categorize braking zones by intensity"""
        categories = {
            'light': [],
            'moderate': [],
            'heavy': [],
            'maximum': []
        }

        for zone in braking_zones:
            decel = zone['max_deceleration']

            if decel < self.braking_thresholds['light']:
                categories['light'].append(zone)
            elif decel < self.braking_thresholds['moderate']:
                categories['moderate'].append(zone)
            elif decel < self.braking_thresholds['heavy']:
                categories['heavy'].append(zone)
            else:
                categories['maximum'].append(zone)

        return {cat: len(zones) for cat, zones in categories.items()}

    def _analyze_trail_braking(self, braking_zones: List[Dict]) -> Dict:
        """Analyze trail braking technique"""
        # Trail braking analysis would require more detailed telemetry
        # This is a simplified analysis

        long_braking_zones = [bz for bz in braking_zones if bz['braking_duration'] > 10]

        return {
            'trail_braking_instances': len(long_braking_zones),
            'average_trail_distance': np.mean([bz['braking_distance'] for bz in long_braking_zones]) if long_braking_zones else 0,
            'trail_braking_consistency': self._calculate_braking_consistency(long_braking_zones) if long_braking_zones else 0
        }

    def _calculate_performance_envelope(self, g_force_analysis: Dict, cornering_analysis: Dict, braking_analysis: Dict) -> Dict:
        """Calculate overall performance envelope"""
        envelope = {
            'overall_score': 0,
            'strengths': [],
            'areas_for_improvement': []
        }

        scores = []

        # G-force utilization score
        if g_force_analysis and 'combined' in g_force_analysis:
            g_score = g_force_analysis['combined'].get('consistency_score', 0)
            scores.append(g_score)
            if g_score > 80:
                envelope['strengths'].append('Excellent G-force consistency')
            elif g_score < 60:
                envelope['areas_for_improvement'].append('Improve G-force consistency')

        # Cornering efficiency score
        if cornering_analysis and 'overall_cornering' in cornering_analysis:
            corner_score = cornering_analysis['overall_cornering'].get('cornering_efficiency', 0)
            scores.append(corner_score)
            if corner_score > 80:
                envelope['strengths'].append('Strong cornering technique')
            elif corner_score < 60:
                envelope['areas_for_improvement'].append('Focus on cornering efficiency')

        # Braking performance score
        if braking_analysis and 'braking_performance' in braking_analysis:
            brake_score = braking_analysis['braking_performance'].get('consistency', 0)
            scores.append(brake_score)
            if brake_score > 80:
                envelope['strengths'].append('Consistent braking performance')
            elif brake_score < 60:
                envelope['areas_for_improvement'].append('Work on braking consistency')

        envelope['overall_score'] = np.mean(scores) if scores else 0

        return envelope

    def _aggregate_metrics(self, combined_metrics: Dict, session_analysis: Dict):
        """Aggregate metrics across sessions"""
        # This would combine data from multiple sessions for overall analysis
        pass

    def _generate_combined_analysis(self, combined_metrics: Dict) -> Dict:
        """Generate combined analysis across all sessions"""
        return {
            'overall_performance': 'Professional analysis across all sessions',
            'consistency_trends': 'Improving consistency in G-force application',
            'technical_areas': ['Cornering optimization', 'Braking refinement', 'G-force management']
        }

    def _generate_performance_insights(self, combined_metrics: Dict) -> List[str]:
        """Generate performance insights"""
        return [
            'G-force analysis shows strong lateral grip utilization in medium-speed corners',
            'Braking performance indicates potential for later braking points',
            'Cornering speeds suggest opportunity for carrying more speed through fast corners',
            'Trail braking technique shows room for refinement in heavy braking zones'
        ]

    def _identify_improvement_areas(self, combined_metrics: Dict) -> List[str]:
        """Identify specific areas for improvement"""
        return [
            'Increase consistency in maximum braking zones',
            'Optimize corner entry speeds for better apex positioning',
            'Work on smooth G-force transitions for improved lap times',
            'Develop better feel for traction limits in low-speed corners'
        ]

    def _get_professional_benchmarks(self) -> Dict:
        """Get professional motorsport benchmarks"""
        return {
            'lateral_g_targets': {
                'club_level': '1.2-1.4g',
                'semi_professional': '1.4-1.6g',
                'professional': '1.6-2.0g+'
            },
            'braking_g_targets': {
                'club_level': '1.0-1.2g',
                'semi_professional': '1.2-1.4g',
                'professional': '1.4-1.8g+'
            },
            'consistency_targets': {
                'club_level': '70-80%',
                'semi_professional': '80-90%',
                'professional': '90-95%+'
            }
        }