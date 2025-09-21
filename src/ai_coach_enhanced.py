"""
Enhanced AI Driving Coach with OpenAI integration
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class EnhancedDriveCoach:
    """Enhanced AI Coach using OpenAI for intelligent responses"""

    def __init__(self, telemetry_data_path: str = "./data/processed_sessions"):
        """
        Initialize the enhanced AI coach

        Args:
            telemetry_data_path: Path to store processed telemetry data
        """
        self.data_path = Path(telemetry_data_path)
        self.data_path.mkdir(parents=True, exist_ok=True)

        self.sessions = []
        self.config = self._load_config()

        # Initialize OpenAI client if enabled
        self.openai_client = None
        self.use_openai = False

        if self.config.get('ai_coaching_enabled', True):
            try:
                import openai

                # Get API key from config file
                api_key = self.config.get('openai_api_key', '').strip()

                if api_key:
                    self.openai_client = openai.OpenAI(api_key=api_key)
                    self.use_openai = True
                    logger.info("OpenAI client initialized successfully")
                else:
                    logger.info("No OpenAI API key configured. Using intelligent rule-based coaching.")

            except ImportError:
                logger.info("OpenAI library not available. Using rule-based coaching.")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}. Using rule-based coaching.")

        self.load_existing_sessions()
        logger.info(f"Enhanced AI Coach initialized with {len(self.sessions)} sessions, OpenAI: {self.use_openai}")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json"""
        try:
            config_path = Path(__file__).parent.parent / "config.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load config: {e}")

        # Return default config
        return {
            "openai_api_key": "",
            "openai_model": "gpt-4o-mini",
            "ai_coaching_enabled": True,
            "fallback_to_rules": True,
            "max_tokens": 500,
            "temperature": 0.7
        }

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
            session_id = processed_data.get('id', f"session_{len(self.sessions)}")
            self.sessions.append(processed_data)

            # Save to disk
            session_file = self.data_path / f"{session_id}.json"
            with open(session_file, 'w') as f:
                json.dump(processed_data, f, indent=2)

            logger.info(f"Added session {session_id} to enhanced coach knowledge")
            return session_id

        except Exception as e:
            logger.error(f"Error adding session: {e}")
            return ""

    def answer_question(self, question: str) -> str:
        """
        Answer a driving-related question using enhanced AI

        Args:
            question: User's question

        Returns:
            Coach's intelligent response
        """
        try:
            if self.use_openai and self.openai_client:
                return self._answer_with_openai(question)
            else:
                return self._answer_with_rules(question)

        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return f"I apologize, but I encountered an error processing your question: {str(e)}. Please try rephrasing your question."

    def _answer_with_openai(self, question: str) -> str:
        """Answer question using OpenAI's GPT model"""
        try:
            # Prepare context from telemetry data
            context = self._prepare_telemetry_context()

            # Create the system prompt for racing coaching
            system_prompt = self._create_coaching_system_prompt()

            # Create the user prompt with context and question
            user_prompt = f"""
            TELEMETRY DATA CONTEXT:
            {context}

            DRIVER QUESTION:
            {question}

            Please provide specific, actionable coaching advice based on the telemetry data above.
            """

            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Using the more capable model for better coaching
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            ai_response = response.choices[0].message.content.strip()

            # Add a note about the AI enhancement
            enhanced_response = f"{ai_response}\n\n---\n Enhanced AI Analysis: This response was generated using advanced AI with your real telemetry data."

            return enhanced_response

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            # Fallback to rule-based system
            return self._answer_with_rules(question) + "\n\n(Note: AI enhancement temporarily unavailable, using rule-based analysis)"

    def _create_coaching_system_prompt(self) -> str:
        """Create the system prompt for OpenAI coaching"""
        return """You are an expert iRacing driving coach with deep knowledge of:

        RACING EXPERTISE:
        - Track-specific driving techniques and optimal racing lines
        - Car setup and handling characteristics
        - Telemetry analysis and performance optimization
        - Consistency development and lap time improvement
        - Race strategy and mental performance

        COMMUNICATION STYLE:
        - Provide specific, actionable advice
        - Use encouraging but honest feedback
        - Focus on 2-3 key improvement areas maximum
        - Explain the "why" behind recommendations
        - Use racing terminology appropriately
        - Be conversational and supportive

        ANALYSIS APPROACH:
        - Always reference the specific telemetry data provided
        - Identify patterns in lap times and consistency
        - Consider track and car characteristics
        - Prioritize safety and gradual improvement
        - Suggest specific practice techniques

        RESPONSE FORMAT:
        - Start with a brief assessment of their performance
        - Provide 2-3 specific recommendations
        - End with encouragement and next steps
        - Keep responses focused and actionable (under 400 words)
        """

    def _prepare_telemetry_context(self) -> str:
        """Prepare telemetry data context for OpenAI"""
        if not self.sessions:
            return "No telemetry sessions available yet."

        # Get the most recent sessions for context
        recent_sessions = self.sessions[-3:]  # Last 3 sessions

        context_parts = []
        context_parts.append(f"DRIVER PROFILE: {len(self.sessions)} total sessions analyzed")

        # Overall statistics
        all_tracks = set(s.get('session_info', {}).get('track', 'Unknown') for s in self.sessions)
        all_cars = set(s.get('session_info', {}).get('car', 'Unknown') for s in self.sessions)

        context_parts.append(f"EXPERIENCE: {len(all_tracks)} tracks, {len(all_cars)} cars")
        context_parts.append(f"TRACKS: {', '.join(sorted(all_tracks))}")
        context_parts.append(f"CARS: {', '.join(sorted(all_cars))}")

        # Recent session details
        context_parts.append("\nRECENT SESSIONS:")

        for i, session in enumerate(recent_sessions):
            session_info = session.get('session_info', {})
            lap_analysis = session.get('lap_analysis', {})
            insights = session.get('insights', {})

            session_summary = f"""
            Session {i+1}:
            - Track: {session_info.get('track', 'Unknown')}
            - Car: {session_info.get('car', 'Unknown')}
            - Date: {session_info.get('session_date', 'Unknown')}
            - Total Laps: {lap_analysis.get('total_laps', 0)}
            - Fastest Lap: {lap_analysis.get('fastest_lap', 'N/A')}s
            - Consistency Rating: {lap_analysis.get('consistency_rating', 'N/A')}/10
            - Session Trend: {lap_analysis.get('improvement_over_session', {}).get('trend', 'Unknown')}
            """

            # Add key insights
            strengths = insights.get('strengths', [])
            improvements = insights.get('improvement_areas', [])

            if strengths:
                session_summary += f"\n            - Strengths: {'; '.join(strengths[:2])}"
            if improvements:
                session_summary += f"\n            - Areas to improve: {'; '.join(improvements[:2])}"

            context_parts.append(session_summary)

        # Add performance trends
        if len(self.sessions) > 1:
            context_parts.append(self._analyze_performance_trends())

        return '\n'.join(context_parts)

    def _analyze_performance_trends(self) -> str:
        """Analyze performance trends across sessions"""
        trends = ["PERFORMANCE TRENDS:"]

        # Consistency trend
        recent_consistency = []
        for session in self.sessions[-5:]:  # Last 5 sessions
            rating = session.get('lap_analysis', {}).get('consistency_rating', 0)
            if rating > 0:
                recent_consistency.append(rating)

        if len(recent_consistency) >= 2:
            if recent_consistency[-1] > recent_consistency[0]:
                trends.append("- Consistency improving over recent sessions")
            elif recent_consistency[-1] < recent_consistency[0]:
                trends.append("- Consistency declining - may need to focus on fundamentals")
            else:
                trends.append("- Consistency stable")

        # Track-specific performance
        track_performance = {}
        for session in self.sessions:
            track = session.get('session_info', {}).get('track', 'Unknown')
            fastest = session.get('lap_analysis', {}).get('fastest_lap')
            if track != 'Unknown' and fastest:
                if track not in track_performance:
                    track_performance[track] = []
                track_performance[track].append(fastest)

        for track, times in track_performance.items():
            if len(times) > 1:
                improvement = times[0] - times[-1]  # Positive = getting faster
                if improvement > 0.5:
                    trends.append(f"- {track}: Significant improvement ({improvement:.3f}s faster)")
                elif improvement > 0.1:
                    trends.append(f"- {track}: Moderate improvement ({improvement:.3f}s faster)")
                elif improvement < -0.5:
                    trends.append(f"- {track}: Times getting slower - review technique")

        return '\n'.join(trends)

    def _answer_with_rules(self, question: str) -> str:
        """Fallback rule-based answering (enhanced version of original coach)"""
        question_lower = question.lower()

        try:
            # Enhanced rule-based responses with more detailed analysis
            if any(word in question_lower for word in ['best', 'fastest', 'turn 1', 'turn one', 'lap time']):
                return self._enhanced_performance_analysis(question)

            elif any(word in question_lower for word in ['how many', 'times', 'sessions', 'statistics']):
                return self._enhanced_statistics_analysis(question)

            elif any(word in question_lower for word in ['improve', 'better', 'work on', 'practice', 'focus']):
                return self._enhanced_improvement_analysis(question)

            elif any(word in question_lower for word in ['consistent', 'consistency']):
                return self._enhanced_consistency_analysis(question)

            elif any(word in question_lower for word in ['track', 'car', 'setup']):
                return self._enhanced_track_car_analysis(question)

            else:
                return self._enhanced_general_analysis(question)

        except Exception as e:
            logger.error(f"Error in rule-based analysis: {e}")
            return "I apologize, but I'm having trouble analyzing your question right now. Please try asking about your lap times, consistency, or specific tracks."

    def _enhanced_performance_analysis(self, question: str) -> str:
        """Enhanced performance analysis with detailed insights"""
        if not self.sessions:
            return "I don't have any telemetry data to analyze yet. Please ensure your IBT files have been processed."

        # Find best performance across all sessions
        best_times = []
        for session in self.sessions:
            lap_analysis = session.get('lap_analysis', {})
            fastest_lap = lap_analysis.get('fastest_lap')
            if fastest_lap and fastest_lap > 0:
                session_info = session.get('session_info', {})
                best_times.append({
                    'time': fastest_lap,
                    'track': session_info.get('track', 'Unknown'),
                    'car': session_info.get('car', 'Unknown'),
                    'date': session_info.get('session_date', 'Unknown'),
                    'consistency': lap_analysis.get('consistency_rating', 0),
                    'laps': lap_analysis.get('total_laps', 0)
                })

        if not best_times:
            return "I don't have valid lap time data to analyze yet."

        best_times.sort(key=lambda x: x['time'])
        best = best_times[0]

        response = [
            f" PERFORMANCE ANALYSIS:",
            f"",
            f"Your fastest lap time: {best['time']:.3f}s",
            f" Track: {best['track']}",
            f" Car: {best['car']}",
            f" Session date: {best['date']}",
            f" Consistency in that session: {best['consistency']:.1f}/10",
            f" Total laps: {best['laps']}",
            f"",
            f" DETAILED ANALYSIS:"
        ]

        # Add performance context
        if best['consistency'] >= 8:
            response.append(f" Excellent consistency ({best['consistency']:.1f}/10) - you're hitting your marks well")
        elif best['consistency'] >= 6:
            response.append(f" Good consistency ({best['consistency']:.1f}/10) - room for minor improvements")
        else:
            response.append(f" Consistency needs work ({best['consistency']:.1f}/10) - focus on repeatable brake points")

        # Track-specific insights
        track_advice = {
            'roadatlanta': "Road Atlanta rewards late braking and smooth exits from the chicane",
            'talladega': "Talladega success depends on draft management and fuel strategy",
            'watkinsglen': "Watkins Glen requires patience through the Esses and strong exit speed"
        }

        track_tip = track_advice.get(best['track'].lower())
        if track_tip:
            response.append(f" {track_tip}")

        # Show other competitive times
        if len(best_times) > 1:
            response.append(f"")
            response.append(f" OTHER STRONG PERFORMANCES:")
            for i, lap in enumerate(best_times[1:4], 2):
                response.append(f"{i}. {lap['time']:.3f}s ({lap['car']} at {lap['track']})")

        response.append(f"")
        response.append(f" To improve further: Focus on consistency first, then work on finding those extra tenths through better corner exit speeds.")

        return '\n'.join(response)

    def _enhanced_consistency_analysis(self, question: str) -> str:
        """Enhanced consistency analysis"""
        if not self.sessions:
            return "I need telemetry data to analyze your consistency. Please ensure your IBT files are processed."

        # Analyze consistency across sessions
        consistency_data = []
        for session in self.sessions:
            lap_analysis = session.get('lap_analysis', {})
            session_info = session.get('session_info', {})
            rating = lap_analysis.get('consistency_rating', 0)

            if rating > 0:
                consistency_data.append({
                    'rating': rating,
                    'track': session_info.get('track', 'Unknown'),
                    'car': session_info.get('car', 'Unknown'),
                    'date': session_info.get('session_date', 'Unknown'),
                    'laps': lap_analysis.get('total_laps', 0),
                    'fastest': lap_analysis.get('fastest_lap', 0)
                })

        if not consistency_data:
            return "I don't have enough consistency data to analyze yet."

        avg_consistency = sum(d['rating'] for d in consistency_data) / len(consistency_data)
        best_session = max(consistency_data, key=lambda x: x['rating'])

        response = [
            f" CONSISTENCY ANALYSIS:",
            f"",
            f"Overall consistency rating: {avg_consistency:.1f}/10",
            f"",
            f" BEST CONSISTENCY SESSION:",
            f" Rating: {best_session['rating']:.1f}/10",
            f" Track: {best_session['track']} ({best_session['car']})",
            f" Date: {best_session['date']}",
            f" Laps completed: {best_session['laps']}",
            f"",
            f" ANALYSIS:"
        ]

        if avg_consistency >= 8:
            response.extend([
                f" Excellent consistency - you're performing at a high level",
                f" Focus on fine-tuning for those extra tenths",
                f" Consider working on racecraft and strategy"
            ])
        elif avg_consistency >= 6:
            response.extend([
                f" Good consistency with room for improvement",
                f" Work on hitting the same brake points every lap",
                f" Focus on smooth, repeatable inputs"
            ])
        else:
            response.extend([
                f" Consistency needs significant work",
                f" Focus on fundamentals: brake points, racing line, throttle control",
                f" Slower, consistent laps are better than fast, inconsistent ones"
            ])

        # Track-specific consistency advice
        track_counts = {}
        for d in consistency_data:
            track = d['track']
            if track not in track_counts:
                track_counts[track] = []
            track_counts[track].append(d['rating'])

        response.append(f"")
        response.append(f" TRACK-SPECIFIC CONSISTENCY:")
        for track, ratings in track_counts.items():
            avg_rating = sum(ratings) / len(ratings)
            response.append(f" {track}: {avg_rating:.1f}/10 ({len(ratings)} sessions)")

        return '\n'.join(response)

    def _enhanced_improvement_analysis(self, question: str) -> str:
        """Enhanced improvement recommendations"""
        if not self.sessions:
            return "I need your telemetry data to provide improvement recommendations. Please process your IBT files first."

        # Get latest session for focused advice
        latest_session = self.sessions[-1]
        session_info = latest_session.get('session_info', {})
        lap_analysis = latest_session.get('lap_analysis', {})
        insights = latest_session.get('insights', {})

        track = session_info.get('track', 'Unknown')
        car = session_info.get('car', 'Unknown')
        consistency = lap_analysis.get('consistency_rating', 0)

        response = [
            f" PERSONALIZED IMPROVEMENT PLAN:",
            f"",
            f"Based on your latest session: {track} with {car}",
            f"Current consistency: {consistency:.1f}/10",
            f"",
            f" PRIORITY FOCUS AREAS:"
        ]

        # Add specific recommendations based on data
        improvement_areas = insights.get('improvement_areas', [])
        if improvement_areas:
            for i, area in enumerate(improvement_areas[:3], 1):
                response.append(f"{i}. {area}")
        else:
            # Fallback recommendations based on consistency
            if consistency < 6:
                response.extend([
                    "1. Focus on consistency - hit the same brake points every lap",
                    "2. Work on smooth throttle application",
                    "3. Practice maintaining a consistent racing line"
                ])
            else:
                response.extend([
                    "1. Fine-tune your racing line for optimal corner exit speed",
                    "2. Work on late braking points where safe",
                    "3. Focus on setup optimization for your driving style"
                ])

        # Add practice plan
        response.extend([
            f"",
            f" PRACTICE SESSION PLAN:",
            f"1. Start with 5-10 slow, consistent laps to establish rhythm",
            f"2. Gradually increase pace while maintaining consistency",
            f"3. Focus on one corner per session for improvement",
            f"4. End with 3-5 qualifying-style laps"
        ])

        # Track-specific advice
        track_specific = {
            'roadatlanta': [
                " Master the chicane - it's crucial for lap time",
                " Work on late braking into Turn 1",
                " Use all the track on exit of Turn 12"
            ],
            'talladega': [
                " Practice draft positioning",
                " Work on fuel-saving techniques",
                " Focus on smooth, consistent inputs"
            ]
        }

        if track.lower() in track_specific:
            response.append(f"")
            response.append(f" {track.upper()} SPECIFIC TIPS:")
            response.extend(track_specific[track.lower()])

        return '\n'.join(response)

    def _enhanced_statistics_analysis(self, question: str) -> str:
        """Enhanced statistics with trends"""
        total_sessions = len(self.sessions)
        if total_sessions == 0:
            return "No sessions have been processed yet. Please add your IBT files to get started."

        tracks = {}
        cars = {}
        total_laps = 0
        best_lap = float('inf')

        for session in self.sessions:
            session_info = session.get('session_info', {})
            lap_analysis = session.get('lap_analysis', {})

            track = session_info.get('track', 'Unknown')
            car = session_info.get('car', 'Unknown')

            tracks[track] = tracks.get(track, 0) + 1
            cars[car] = cars.get(car, 0) + 1

            laps = lap_analysis.get('total_laps', 0)
            if isinstance(laps, int):
                total_laps += laps

            fastest = lap_analysis.get('fastest_lap', float('inf'))
            if fastest and fastest < best_lap:
                best_lap = fastest

        response = [
            f" COMPREHENSIVE DRIVING STATISTICS:",
            f"",
            f" SESSION OVERVIEW:",
            f" Total sessions: {total_sessions}",
            f" Total laps completed: {total_laps:,}",
            f" Personal best lap: {best_lap:.3f}s" if best_lap != float('inf') else " Personal best: Not yet recorded",
            f"",
            f" TRACK EXPERIENCE:",
        ]

        for track, count in sorted(tracks.items()):
            response.append(f" {track}: {count} sessions")

        response.extend([
            f"",
            f" CAR EXPERIENCE:"
        ])

        for car, count in sorted(cars.items()):
            response.append(f" {car}: {count} sessions")

        # Add recent activity
        if self.sessions:
            latest = self.sessions[-1]
            latest_info = latest.get('session_info', {})
            response.extend([
                f"",
                f" RECENT ACTIVITY:",
                f" Last session: {latest_info.get('track', 'Unknown')} with {latest_info.get('car', 'Unknown')}",
                f" Date: {latest_info.get('session_date', 'Unknown')}"
            ])

        return '\n'.join(response)

    def _enhanced_track_car_analysis(self, question: str) -> str:
        """Enhanced track and car specific analysis"""
        # Extract track/car from question
        track = self._extract_track_from_question(question)
        car = self._extract_car_from_question(question)

        if track:
            return self._analyze_track_performance(track)
        elif car:
            return self._analyze_car_performance(car)
        else:
            return self._analyze_overall_track_car_performance()

    def _analyze_track_performance(self, track: str) -> str:
        """Detailed track performance analysis"""
        track_sessions = [s for s in self.sessions
                         if s.get('session_info', {}).get('track', '').lower() == track.lower()]

        if not track_sessions:
            return f"I don't have any data for {track} yet. Try running some sessions there first!"

        response = [f" {track.upper()} PERFORMANCE ANALYSIS:"]

        # Performance stats
        lap_times = []
        consistency_ratings = []

        for session in track_sessions:
            lap_analysis = session.get('lap_analysis', {})
            fastest = lap_analysis.get('fastest_lap')
            consistency = lap_analysis.get('consistency_rating', 0)

            if fastest:
                lap_times.append(fastest)
            if consistency > 0:
                consistency_ratings.append(consistency)

        if lap_times:
            best_time = min(lap_times)
            avg_time = sum(lap_times) / len(lap_times)
            response.extend([
                f"",
                f" LAP TIME PERFORMANCE:",
                f" Best time: {best_time:.3f}s",
                f" Average best: {avg_time:.3f}s",
                f" Total sessions: {len(track_sessions)}"
            ])

        if consistency_ratings:
            avg_consistency = sum(consistency_ratings) / len(consistency_ratings)
            response.extend([
                f"",
                f" CONSISTENCY:",
                f" Average rating: {avg_consistency:.1f}/10"
            ])

        # Track-specific advice
        track_advice = {
            'roadatlanta': [
                " Focus on late braking into Turn 1 for optimal lap times",
                " The chicane complex requires patience and precision",
                " Use elevation changes to your advantage",
                " Track evolution affects grip levels throughout sessions"
            ],
            'talladega': [
                " Draft management is absolutely crucial",
                " Fuel economy becomes important in longer runs",
                " Consistent throttle application prevents breaking the draft",
                " Entry speed into Turn 1 sets up the entire lap"
            ]
        }

        advice = track_advice.get(track.lower())
        if advice:
            response.extend([f"", f" {track.upper()} SPECIFIC TIPS:"])
            response.extend(advice)

        return '\n'.join(response)

    def _enhanced_general_analysis(self, question: str) -> str:
        """Enhanced general analysis with comprehensive overview"""
        if not self.sessions:
            return ("Welcome to your Enhanced iRacing AI Coach! \n\n"
                   "I'm ready to analyze your telemetry data once you process some IBT files. "
                   "I can help you with:\n\n"
                   " Performance analysis and lap time improvement\n"
                   " Consistency development and racecraft\n"
                   " Track-specific coaching and setup advice\n"
                   " Car-specific techniques and optimization\n\n"
                   "Start by asking me about your lap times, consistency, or specific tracks!")

        total_sessions = len(self.sessions)
        tracks = set(s.get('session_info', {}).get('track', 'Unknown') for s in self.sessions)
        cars = set(s.get('session_info', {}).get('car', 'Unknown') for s in self.sessions)

        # Get latest performance indicators
        latest_session = self.sessions[-1]
        latest_consistency = latest_session.get('lap_analysis', {}).get('consistency_rating', 0)

        response = [
            f" ENHANCED AI COACHING OVERVIEW:",
            f"",
            f" YOUR DRIVING PROFILE:",
            f" {total_sessions} sessions analyzed with real telemetry data",
            f" Experience across {len(tracks)} tracks with {len(cars)} cars",
            f" Latest consistency rating: {latest_consistency:.1f}/10",
            f"",
            f" WHAT I CAN HELP YOU WITH:",
            f" 'How consistent am I?' - Detailed consistency analysis",
            f" 'What's my fastest lap time?' - Performance breakdowns",
            f" 'How can I improve at [track]?' - Track-specific coaching",
            f" 'What should I practice next?' - Personalized training plans",
            f"",
            f" ENHANCED FEATURES:",
            f" Real telemetry data analysis from your IBT files",
            f" Track and car-specific insights",
            f" Consistency ratings and improvement trends",
            f" Personalized practice recommendations"
        ]

        if self.use_openai:
            response.extend([
                f"  AI-powered responses for detailed analysis",
                f" Conversational coaching tailored to your questions"
            ])

        response.extend([
            f"",
            f" Ready to help you get faster and more consistent!"
        ])

        return '\n'.join(response)

    def _extract_track_from_question(self, question: str) -> Optional[str]:
        """Extract track name from question"""
        question_lower = question.lower()
        tracks = {
            'road atlanta': 'roadatlanta',
            'roadatlanta': 'roadatlanta',
            'talladega': 'talladega',
            'watkins glen': 'watkinsglen',
            'laguna seca': 'lagunaseca',
            'sebring': 'sebring'
        }

        for track_phrase, track_name in tracks.items():
            if track_phrase in question_lower:
                return track_name
        return None

    def _extract_car_from_question(self, question: str) -> Optional[str]:
        """Extract car name from question"""
        question_lower = question.lower()
        cars = {
            'porsche': 'porsche992cup',
            '992': 'porsche992cup',
            'toyota': 'toyotagr86',
            'gr86': 'toyotagr86'
        }

        for car_phrase, car_name in cars.items():
            if car_phrase in question_lower:
                return car_name
        return None

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get enhanced summary statistics"""
        if not self.sessions:
            return {'message': 'No sessions available - process some IBT files to get started!'}

        tracks = {}
        cars = {}
        total_laps = 0
        best_lap = float('inf')

        for session in self.sessions:
            session_info = session.get('session_info', {})
            lap_analysis = session.get('lap_analysis', {})

            track = session_info.get('track', 'Unknown')
            car = session_info.get('car', 'Unknown')

            tracks[track] = tracks.get(track, 0) + 1
            cars[car] = cars.get(car, 0) + 1

            laps = lap_analysis.get('total_laps', 0)
            if isinstance(laps, int):
                total_laps += laps

            fastest = lap_analysis.get('fastest_lap')
            if fastest and fastest < best_lap:
                best_lap = fastest

        return {
            'total_sessions': len(self.sessions),
            'tracks': tracks,
            'cars': cars,
            'total_laps': total_laps,
            'best_lap_time': best_lap if best_lap != float('inf') else None,
            'enhanced_features': True,
            'ai_powered': self.use_openai
        }


if __name__ == "__main__":
    # Test the enhanced coach
    coach = EnhancedAICoach()

    print("=== Enhanced AI Coach Test ===")

    # Test without OpenAI first
    test_questions = [
        "How consistent am I?",
        "What's my fastest lap time?",
        "How can I improve at Road Atlanta?"
    ]

    for question in test_questions:
        print(f"\\nQ: {question}")
        print(f"A: {coach.answer_question(question)}")

    print("\\n=== Test Complete ===")