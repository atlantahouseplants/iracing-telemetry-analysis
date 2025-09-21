"""
AI Driving Coach for iRacing telemetry analysis
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# For now, we'll create a simple coach without external AI APIs
# This can be extended to use OpenAI, Claude, or other LLMs later

logger = logging.getLogger(__name__)


class DriveCoach:
    """AI Driving Coach that analyzes telemetry and provides insights"""

    def __init__(self, telemetry_data_path: str = "./data/processed_sessions"):
        """
        Initialize the AI coach

        Args:
            telemetry_data_path: Path to store processed telemetry data
        """
        self.data_path = Path(telemetry_data_path)
        self.data_path.mkdir(parents=True, exist_ok=True)

        # Simple in-memory storage for now (can be replaced with vector DB later)
        self.sessions = []
        self.load_existing_sessions()

        logger.info(f"AI Coach initialized with {len(self.sessions)} existing sessions")

    def load_existing_sessions(self):
        """Load existing processed sessions from disk"""
        try:
            session_files = list(self.data_path.glob("*.json"))
            for session_file in session_files:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                    self.sessions.append(session_data)

            logger.info(f"Loaded {len(self.sessions)} existing sessions")

        except Exception as e:
            logger.error(f"Error loading existing sessions: {e}")

    def add_session(self, processed_data: Dict[str, Any]) -> str:
        """
        Add a new processed session to the coach's knowledge

        Args:
            processed_data: Processed telemetry data

        Returns:
            Session ID
        """
        try:
            # Generate session ID
            session_id = processed_data.get('id', f"session_{len(self.sessions)}")

            # Add to memory
            self.sessions.append(processed_data)

            # Save to disk
            session_file = self.data_path / f"{session_id}.json"
            with open(session_file, 'w') as f:
                json.dump(processed_data, f, indent=2)

            logger.info(f"Added session {session_id} to coach knowledge")
            return session_id

        except Exception as e:
            logger.error(f"Error adding session: {e}")
            return ""

    def answer_question(self, question: str) -> str:
        """
        Answer a driving-related question based on telemetry data

        Args:
            question: User's question

        Returns:
            Coach's response
        """
        question_lower = question.lower()

        try:
            # Route question to appropriate handler
            if any(word in question_lower for word in ['best', 'fastest', 'turn 1', 'turn one']):
                return self._answer_performance_question(question)

            elif any(word in question_lower for word in ['how many', 'times', 'finished', 'third', 'position']):
                return self._answer_statistics_question(question)

            elif any(word in question_lower for word in ['improve', 'better', 'work on', 'practice']):
                return self._answer_improvement_question(question)

            elif any(word in question_lower for word in ['track', 'car', 'setup']):
                return self._answer_track_car_question(question)

            elif any(word in question_lower for word in ['consistency', 'lap time', 'sector']):
                return self._answer_analysis_question(question)

            else:
                return self._answer_general_question(question)

        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return "I'm sorry, I encountered an error processing your question. Please try again."

    def _answer_performance_question(self, question: str) -> str:
        """Answer questions about performance (fastest laps, best turns, etc.)"""

        if not self.sessions:
            return "I don't have any session data yet. Please process some telemetry files first."

        # Extract track information if mentioned
        track = self._extract_track_from_question(question)

        # Find relevant sessions
        relevant_sessions = []
        if track:
            relevant_sessions = [s for s in self.sessions
                               if s.get('session_info', {}).get('track', '').lower() == track.lower()]
        else:
            relevant_sessions = self.sessions

        if not relevant_sessions:
            if track:
                return f"I don't have any data for {track} yet. Try asking about a different track."
            else:
                return "I don't have enough data to answer that question yet."

        # Analyze fastest laps
        best_times = []
        for session in relevant_sessions:
            lap_analysis = session.get('lap_analysis', {})
            fastest_lap = lap_analysis.get('fastest_lap')
            if fastest_lap and fastest_lap > 0:
                session_info = session.get('session_info', {})
                best_times.append({
                    'time': fastest_lap,
                    'track': session_info.get('track', 'Unknown'),
                    'car': session_info.get('car', 'Unknown'),
                    'date': session_info.get('session_date', 'Unknown')
                })

        if not best_times:
            return "I don't have any valid lap time data to analyze yet."

        # Sort by fastest time
        best_times.sort(key=lambda x: x['time'])

        response = []
        if track:
            response.append(f"Based on your sessions at {track}:")
        else:
            response.append("Based on your telemetry data:")

        response.append(f"\\nYour fastest lap time: {best_times[0]['time']:.3f}s")
        response.append(f"Car: {best_times[0]['car']}")
        response.append(f"Date: {best_times[0]['date']}")

        if len(best_times) > 1:
            response.append(f"\\nOther fast laps:")
            for i, lap in enumerate(best_times[1:4], 2):  # Show top 3 additional
                response.append(f"{i}. {lap['time']:.3f}s ({lap['car']} on {lap['date']})")

        return "\\n".join(response)

    def _answer_statistics_question(self, question: str) -> str:
        """Answer questions about statistics (how many times, positions, etc.)"""

        if not self.sessions:
            return "I don't have any session data yet. Please process some telemetry files first."

        track = self._extract_track_from_question(question)

        # Count sessions
        if track:
            track_sessions = [s for s in self.sessions
                            if s.get('session_info', {}).get('track', '').lower() == track.lower()]
            count = len(track_sessions)

            if count == 0:
                return f"You haven't raced at {track} yet in the data I have."
            elif count == 1:
                return f"You have 1 session at {track} in your telemetry data."
            else:
                return f"You have {count} sessions at {track} in your telemetry data."

        else:
            total_sessions = len(self.sessions)
            unique_tracks = len(set(s.get('session_info', {}).get('track', 'Unknown')
                                  for s in self.sessions))
            unique_cars = len(set(s.get('session_info', {}).get('car', 'Unknown')
                                for s in self.sessions))

            return (f"You have {total_sessions} total sessions across {unique_tracks} "
                   f"different tracks with {unique_cars} different cars.")

    def _answer_improvement_question(self, question: str) -> str:
        """Answer questions about improvement areas"""

        if not self.sessions:
            return "I don't have any session data yet. Please process some telemetry files first."

        track = self._extract_track_from_question(question)
        car = self._extract_car_from_question(question)

        # Filter sessions based on track/car
        relevant_sessions = self.sessions
        if track:
            relevant_sessions = [s for s in relevant_sessions
                               if s.get('session_info', {}).get('track', '').lower() == track.lower()]
        if car:
            relevant_sessions = [s for s in relevant_sessions
                               if s.get('session_info', {}).get('car', '').lower() == car.lower()]

        if not relevant_sessions:
            return "I don't have data for that specific track/car combination yet."

        # Gather improvement suggestions from recent sessions
        all_improvements = []
        for session in relevant_sessions[-3:]:  # Last 3 sessions
            improvements = session.get('insights', {}).get('improvement_areas', [])
            all_improvements.extend(improvements)

        if not all_improvements:
            return "Your recent sessions don't show specific improvement areas. Keep focusing on consistency!"

        # Remove duplicates while preserving order
        unique_improvements = []
        seen = set()
        for improvement in all_improvements:
            if improvement not in seen:
                unique_improvements.append(improvement)
                seen.add(improvement)

        response = []
        context = ""
        if track and car:
            context = f" at {track} with the {car}"
        elif track:
            context = f" at {track}"
        elif car:
            context = f" with the {car}"

        response.append(f"Based on your recent sessions{context}, here are the top areas to work on:")

        for i, improvement in enumerate(unique_improvements[:3], 1):
            response.append(f"{i}. {improvement}")

        return "\\n".join(response)

    def _answer_track_car_question(self, question: str) -> str:
        """Answer questions about specific tracks or cars"""

        if not self.sessions:
            return "I don't have any session data yet. Please process some telemetry files first."

        track = self._extract_track_from_question(question)
        car = self._extract_car_from_question(question)

        if track:
            track_sessions = [s for s in self.sessions
                            if s.get('session_info', {}).get('track', '').lower() == track.lower()]

            if not track_sessions:
                return f"I don't have any data for {track} yet."

            # Get track-specific insights
            response = [f"Here's what I know about your performance at {track}:"]

            # Best lap time
            best_lap = min((s.get('lap_analysis', {}).get('fastest_lap', float('inf'))
                          for s in track_sessions if s.get('lap_analysis', {}).get('fastest_lap')),
                         default=None)

            if best_lap and best_lap != float('inf'):
                response.append(f"\\nBest lap time: {best_lap:.3f}s")

            # Recent improvements
            recent_session = track_sessions[-1]
            improvements = recent_session.get('insights', {}).get('improvement_areas', [])
            if improvements:
                response.append(f"\\nAreas to focus on:")
                for improvement in improvements[:2]:
                    response.append(f"• {improvement}")

            return "\\n".join(response)

        elif car:
            car_sessions = [s for s in self.sessions
                          if s.get('session_info', {}).get('car', '').lower() == car.lower()]

            if not car_sessions:
                return f"I don't have any data for the {car} yet."

            response = [f"Here's your performance data with the {car}:"]
            response.append(f"Total sessions: {len(car_sessions)}")

            # Track variety
            tracks = set(s.get('session_info', {}).get('track', 'Unknown') for s in car_sessions)
            response.append(f"Tracks driven: {', '.join(sorted(tracks))}")

            return "\\n".join(response)

        else:
            # General track/car summary
            tracks = set(s.get('session_info', {}).get('track', 'Unknown') for s in self.sessions)
            cars = set(s.get('session_info', {}).get('car', 'Unknown') for s in self.sessions)

            response = ["Here's a summary of your driving data:"]
            response.append(f"Tracks: {', '.join(sorted(tracks))}")
            response.append(f"Cars: {', '.join(sorted(cars))}")

            return "\\n".join(response)

    def _answer_analysis_question(self, question: str) -> str:
        """Answer questions about driving analysis (consistency, sectors, etc.)"""

        if not self.sessions:
            return "I don't have any session data yet. Please process some telemetry files first."

        # Get latest session for analysis
        latest_session = self.sessions[-1]
        session_info = latest_session.get('session_info', {})
        insights = latest_session.get('insights', {})

        response = [f"Based on your latest session at {session_info.get('track', 'Unknown')}:"]

        # Consistency analysis
        driving_analysis = insights.get('driving_analysis', {})
        consistency = driving_analysis.get('consistency_rating')
        if consistency:
            response.append(f"\\nConsistency rating: {consistency}/10")

            if consistency >= 8:
                response.append("Excellent consistency! You're hitting your marks well.")
            elif consistency >= 6:
                response.append("Good consistency. Focus on repeating your best laps.")
            else:
                response.append("Work on consistency - focus on brake points and racing line.")

        # Improvement trend
        trend = driving_analysis.get('improvement_trend')
        if trend:
            response.append(f"Session trend: {trend}")

        return "\\n".join(response)

    def _answer_general_question(self, question: str) -> str:
        """Answer general questions about driving"""

        if not self.sessions:
            return "I don't have any session data yet. Please process some telemetry files first."

        # Provide general summary
        total_sessions = len(self.sessions)
        tracks = set(s.get('session_info', {}).get('track', 'Unknown') for s in self.sessions)
        cars = set(s.get('session_info', {}).get('car', 'Unknown') for s in self.sessions)

        response = [
            f"I have analyzed {total_sessions} of your racing sessions.",
            f"You've driven on {len(tracks)} different tracks with {len(cars)} different cars.",
            "",
            "You can ask me questions like:",
            "• 'What are my best turn ones at Road Atlanta?'",
            "• 'How can I improve at Talladega?'",
            "• 'What's my fastest lap time?'",
            "• 'How consistent am I?'"
        ]

        return "\\n".join(response)

    def _extract_track_from_question(self, question: str) -> Optional[str]:
        """Extract track name from question"""
        question_lower = question.lower()

        # Common track names
        tracks = {
            'road atlanta': 'roadatlanta',
            'roadatlanta': 'roadatlanta',
            'talladega': 'talladega',
            'daytona': 'daytona',
            'charlotte': 'charlotte',
            'watkins glen': 'watkinsglen',
            'laguna seca': 'lagunaseca'
        }

        for track_phrase, track_name in tracks.items():
            if track_phrase in question_lower:
                return track_name

        return None

    def _extract_car_from_question(self, question: str) -> Optional[str]:
        """Extract car name from question"""
        question_lower = question.lower()

        # Common car names
        cars = {
            'porsche': 'porsche992cup',
            'porsche 992': 'porsche992cup',
            '992 cup': 'porsche992cup',
            'toyota': 'toyotagr86',
            'gr86': 'toyotagr86',
            'toyota gr86': 'toyotagr86'
        }

        for car_phrase, car_name in cars.items():
            if car_phrase in question_lower:
                return car_name

        return None

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics of all sessions"""
        if not self.sessions:
            return {'message': 'No sessions available'}

        tracks = {}
        cars = {}
        total_laps = 0
        best_lap = float('inf')

        for session in self.sessions:
            session_info = session.get('session_info', {})
            lap_analysis = session.get('lap_analysis', {})

            # Track stats
            track = session_info.get('track', 'Unknown')
            if track not in tracks:
                tracks[track] = 0
            tracks[track] += 1

            # Car stats
            car = session_info.get('car', 'Unknown')
            if car not in cars:
                cars[car] = 0
            cars[car] += 1

            # Lap stats
            session_laps = lap_analysis.get('total_laps', 0)
            if isinstance(session_laps, int):
                total_laps += session_laps

            fastest_lap = lap_analysis.get('fastest_lap')
            if fastest_lap and fastest_lap < best_lap:
                best_lap = fastest_lap

        return {
            'total_sessions': len(self.sessions),
            'tracks': tracks,
            'cars': cars,
            'total_laps': total_laps,
            'best_lap_time': best_lap if best_lap != float('inf') else None
        }


if __name__ == "__main__":
    # Test the AI coach
    coach = DriveCoach()

    print("=== AI Driving Coach Test ===")

    # Test questions
    test_questions = [
        "What are my best turn ones at Road Atlanta?",
        "How many times have I finished third here?",
        "What three things can I work on to improve at Road Atlanta in the Porsche 992?",
        "How consistent am I?",
        "What's my fastest lap time?"
    ]

    for question in test_questions:
        print(f"\\nQ: {question}")
        print(f"A: {coach.answer_question(question)}")

    # Show summary stats
    stats = coach.get_summary_stats()
    print(f"\\n=== Summary Stats ===")
    print(json.dumps(stats, indent=2))

    print("\\n=== Test Complete ===")