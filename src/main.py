"""
Main iRacing Telemetry Coach system
"""

import os
import sys
import logging
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from file_monitor import TelemetryFileMonitor
from telemetry_processor import TelemetryProcessor
from ai_coach import DriveCoach

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/telemetry_coach.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class TelemetryCoachSystem:
    """Main system that coordinates all components"""

    def __init__(self):
        """Initialize the telemetry coach system"""
        # Ensure directories exist
        Path('../data').mkdir(exist_ok=True)
        Path('../logs').mkdir(exist_ok=True)

        # Initialize components
        self.processor = TelemetryProcessor()
        self.coach = DriveCoach("../data/processed_sessions")
        self.monitor = TelemetryFileMonitor(self.process_new_file)

        logger.info("Telemetry Coach System initialized")

    def process_new_file(self, file_path: str):
        """
        Process a new telemetry file when detected

        Args:
            file_path: Path to the new IBT file
        """
        logger.info(f"Processing new telemetry file: {os.path.basename(file_path)}")

        try:
            # Process the telemetry file
            processed_data = self.processor.process_telemetry_file(file_path)

            if processed_data:
                # Add to coach's knowledge base
                session_id = self.coach.add_session(processed_data)

                # Log summary
                session_info = processed_data.get('session_info', {})
                insights = processed_data.get('insights', {})

                logger.info(f"Successfully processed session {session_id}")
                logger.info(f"Track: {session_info.get('track', 'Unknown')}")
                logger.info(f"Car: {session_info.get('car', 'Unknown')}")

                # Show key insights
                strengths = insights.get('strengths', [])
                improvements = insights.get('improvement_areas', [])

                if strengths:
                    logger.info(f"Strengths: {', '.join(strengths[:2])}")
                if improvements:
                    logger.info(f"Improvement areas: {', '.join(improvements[:2])}")

                print(f"\\n=== New Session Processed ===")
                print(f"File: {os.path.basename(file_path)}")
                print(f"Track: {session_info.get('track', 'Unknown')}")
                print(f"Car: {session_info.get('car', 'Unknown')}")
                print(f"Session ID: {session_id}")
                print("Ready for questions!")

            else:
                logger.error(f"Failed to process {file_path}")

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")

    def process_existing_files(self, folder_path: str = None):
        """
        Process any existing telemetry files in the folder

        Args:
            folder_path: Path to folder containing IBT files
        """
        if folder_path is None:
            folder_path = "."  # Current directory

        folder = Path(folder_path)
        ibt_files = list(folder.glob("*.ibt"))

        if ibt_files:
            print(f"\\nFound {len(ibt_files)} existing IBT files to process...")

            for ibt_file in ibt_files:
                self.process_new_file(str(ibt_file))

        else:
            print("No existing IBT files found.")

    def start_monitoring(self, watch_folder: str = None):
        """
        Start monitoring for new telemetry files

        Args:
            watch_folder: Folder to monitor (defaults to current directory)
        """
        if watch_folder is None:
            watch_folder = "."

        print(f"\\nStarting file monitoring on: {os.path.abspath(watch_folder)}")
        print("The system will automatically process new IBT files.")

        self.monitor.start(watch_folder)

    def interactive_mode(self):
        """
        Run in interactive mode for asking questions
        """
        print("\\n" + "="*50)
        print("     iRacing AI Driving Coach")
        print("="*50)

        # Show current stats
        stats = self.coach.get_summary_stats()
        if 'message' not in stats:
            print(f"\\nLoaded {stats['total_sessions']} sessions")
            print(f"Tracks: {', '.join(stats['tracks'].keys())}")
            print(f"Cars: {', '.join(stats['cars'].keys())}")
            if stats.get('best_lap_time'):
                print(f"Best lap time: {stats['best_lap_time']:.3f}s")

        print("\\nExample questions:")
        print("• 'What are my best turn ones at Road Atlanta?'")
        print("• 'How can I improve at this track?'")
        print("• 'What's my fastest lap time?'")
        print("• 'How consistent am I?'")
        print("\\nType 'quit' to exit")

        while True:
            try:
                question = input("\\nAsk me anything: ").strip()

                if question.lower() in ['quit', 'exit', 'q']:
                    break

                if not question:
                    continue

                # Get answer from coach
                answer = self.coach.answer_question(question)
                print(f"\\nCoach: {answer}")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

        print("\\nThanks for using the iRacing AI Coach!")

    def stop(self):
        """Stop the system"""
        if self.monitor:
            self.monitor.stop()
        logger.info("Telemetry Coach System stopped")


def main():
    """Main entry point"""
    print("iRacing Telemetry AI Coach")
    print("="*30)

    try:
        # Initialize system
        system = TelemetryCoachSystem()

        # Process existing files
        system.process_existing_files()

        # Start file monitoring in background
        system.start_monitoring()

        # Run interactive mode
        system.interactive_mode()

    except KeyboardInterrupt:
        print("\\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"System error: {e}")
    finally:
        if 'system' in locals():
            system.stop()


if __name__ == "__main__":
    main()