"""
Test script for the complete telemetry coach system
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from telemetry_processor import TelemetryProcessor
from ai_coach import DriveCoach


def test_system():
    """Test the complete system with existing files"""
    print("=== Testing iRacing Telemetry Coach System ===\\n")

    # Initialize components
    print("1. Initializing components...")
    processor = TelemetryProcessor()
    coach = DriveCoach("../data/processed_sessions")

    # Find IBT files
    current_dir = Path(__file__).parent.parent
    ibt_files = list(current_dir.glob("*.ibt"))

    if not ibt_files:
        print("No IBT files found for testing")
        return

    print(f"Found {len(ibt_files)} IBT files to process\\n")

    # Process each file
    print("2. Processing telemetry files...")
    for ibt_file in ibt_files:
        print(f"Processing: {ibt_file.name}")

        # Process the file
        processed_data = processor.process_telemetry_file(str(ibt_file))

        if processed_data:
            # Add to coach
            session_id = coach.add_session(processed_data)
            print(f"  + Added to coach as session: {session_id}")

            # Show summary
            session_info = processed_data['session_info']
            print(f"  Track: {session_info.get('track', 'Unknown')}")
            print(f"  Car: {session_info.get('car', 'Unknown')}")

            # Show insights
            insights = processed_data['insights']
            strengths = insights.get('strengths', [])
            improvements = insights.get('improvement_areas', [])

            if strengths:
                print(f"  Strengths: {strengths[0]}")
            if improvements:
                print(f"  Improvement: {improvements[0]}")
        else:
            print(f"  - Failed to process")

        print()

    # Test coach queries
    print("3. Testing AI Coach queries...\\n")

    test_questions = [
        "What's my fastest lap time?",
        "How can I improve at Road Atlanta?",
        "How consistent am I?",
        "What tracks have I driven?",
        "How many sessions do I have?"
    ]

    for question in test_questions:
        print(f"Q: {question}")
        answer = coach.answer_question(question)
        print(f"A: {answer}\\n")

    # Show summary stats
    print("4. System Summary:")
    stats = coach.get_summary_stats()

    if 'message' not in stats:
        print(f"  Total sessions: {stats['total_sessions']}")
        print(f"  Tracks: {', '.join(stats['tracks'].keys())}")
        print(f"  Cars: {', '.join(stats['cars'].keys())}")
        if stats.get('best_lap_time'):
            print(f"  Best lap time: {stats['best_lap_time']:.3f}s")
        print(f"  Total laps: {stats.get('total_laps', 0)}")
    else:
        print(f"  {stats['message']}")

    print("\\n=== Test Complete ===")
    print("The system is ready to use!")
    print("\\nTo start the full system with file monitoring and interactive mode:")
    print("python main.py")


if __name__ == "__main__":
    test_system()