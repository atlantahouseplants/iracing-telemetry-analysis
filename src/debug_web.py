"""
Debug script to test web UI components
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

print("=== Testing Web UI Components ===")

try:
    print("1. Testing telemetry processor import...")
    from telemetry_processor import TelemetryProcessor
    processor = TelemetryProcessor()
    print("   ✓ TelemetryProcessor imported successfully")

    print("2. Testing AI coach import...")
    from ai_coach import DriveCoach
    coach = DriveCoach("../data/processed_sessions")
    print("   ✓ DriveCoach imported successfully")

    print("3. Testing coach initialization...")
    stats = coach.get_summary_stats()
    print(f"   ✓ Coach stats: {stats}")

    print("4. Testing a simple question...")
    answer = coach.answer_question("What's my fastest lap time?")
    print(f"   ✓ Answer: {answer[:100]}...")

    print("5. Testing Flask import...")
    from flask import Flask
    print("   ✓ Flask imported successfully")

    print("\n=== All components working! ===")
    print("The issue might be in the web UI JavaScript or network requests.")

except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()