"""
Automatic IBT file monitoring system
Watches for new telemetry files and processes them automatically
"""

import os
import time
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Callable, Optional
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)


class IBTFileHandler(FileSystemEventHandler):
    """File system event handler for IBT files"""

    def __init__(self, processor_callback: Callable[[str], None],
                 coach_callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        """
        Initialize the IBT file handler

        Args:
            processor_callback: Function to call when processing a new IBT file
            coach_callback: Function to call to add processed session to coach
        """
        super().__init__()
        self.processor_callback = processor_callback
        self.coach_callback = coach_callback
        self.processing_files = set()
        self.cooldown_period = 5  # seconds to wait before processing

    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return

        file_path = event.src_path
        if self._is_ibt_file(file_path):
            logger.info(f"New IBT file detected: {os.path.basename(file_path)}")
            # Add delay to ensure file is fully written
            threading.Timer(self.cooldown_period, self._process_file, [file_path]).start()

    def on_moved(self, event):
        """Handle file move events (common with iRacing saves)"""
        if event.is_directory:
            return

        dest_path = event.dest_path
        if self._is_ibt_file(dest_path):
            logger.info(f"IBT file moved to monitoring location: {os.path.basename(dest_path)}")
            threading.Timer(self.cooldown_period, self._process_file, [dest_path]).start()

    def _is_ibt_file(self, file_path: str) -> bool:
        """Check if file is an IBT telemetry file"""
        return file_path.lower().endswith('.ibt')

    def _process_file(self, file_path: str):
        """Process the IBT file with cooldown protection"""
        try:
            # Prevent duplicate processing
            if file_path in self.processing_files:
                return

            # Check if file exists and is readable
            if not os.path.exists(file_path):
                logger.warning(f"File no longer exists: {file_path}")
                return

            # Check file size (ensure it's not empty or still being written)
            file_size = os.path.getsize(file_path)
            if file_size < 1000:  # Less than 1KB, likely incomplete
                logger.info(f"File too small, waiting longer: {os.path.basename(file_path)}")
                threading.Timer(10, self._process_file, [file_path]).start()
                return

            self.processing_files.add(file_path)
            logger.info(f"Processing new IBT file: {os.path.basename(file_path)} ({file_size / 1024 / 1024:.1f} MB)")

            # Call the processor
            result = self.processor_callback(file_path)

            if result and self.coach_callback:
                # Add to coach knowledge
                self.coach_callback(result)
                logger.info(f"Successfully added new session to AI coach")

            self.processing_files.discard(file_path)

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            self.processing_files.discard(file_path)


class TelemetryFileMonitor:
    """Automatic telemetry file monitoring system"""

    def __init__(self, processor, coach, watch_directories: list = None):
        """
        Initialize the file monitor

        Args:
            processor: TelemetryProcessor instance
            coach: DriveCoach instance
            watch_directories: List of directories to monitor (default: current dir)
        """
        self.processor = processor
        self.coach = coach
        self.watch_directories = watch_directories or [Path.cwd()]
        self.observers = []
        self.is_monitoring = False

        # Statistics
        self.files_processed = 0
        self.monitoring_start_time = None
        self.last_processed_file = None

    def start_monitoring(self):
        """Start monitoring for new IBT files"""
        if self.is_monitoring:
            logger.warning("File monitoring is already active")
            return

        logger.info("Starting automatic IBT file monitoring...")

        # Create file handler
        file_handler = IBTFileHandler(
            processor_callback=self._process_new_file,
            coach_callback=self._add_to_coach
        )

        # Start observers for each directory
        for watch_dir in self.watch_directories:
            if not os.path.exists(watch_dir):
                logger.warning(f"Watch directory does not exist: {watch_dir}")
                continue

            observer = Observer()
            observer.schedule(file_handler, str(watch_dir), recursive=False)
            observer.start()
            self.observers.append(observer)

            logger.info(f"Monitoring directory: {watch_dir}")

        self.is_monitoring = True
        self.monitoring_start_time = datetime.now()

        logger.info(f"File monitoring active on {len(self.observers)} directories")

    def stop_monitoring(self):
        """Stop monitoring for new IBT files"""
        if not self.is_monitoring:
            return

        logger.info("Stopping automatic IBT file monitoring...")

        for observer in self.observers:
            observer.stop()
            observer.join()

        self.observers.clear()
        self.is_monitoring = False

        duration = datetime.now() - self.monitoring_start_time if self.monitoring_start_time else None
        logger.info(f"File monitoring stopped. Processed {self.files_processed} files" +
                   (f" in {duration}" if duration else ""))

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            'is_monitoring': self.is_monitoring,
            'watch_directories': [str(d) for d in self.watch_directories],
            'files_processed': self.files_processed,
            'monitoring_duration': str(datetime.now() - self.monitoring_start_time) if self.monitoring_start_time else None,
            'last_processed_file': self.last_processed_file,
            'active_observers': len(self.observers)
        }

    def add_watch_directory(self, directory: str):
        """Add a new directory to monitor"""
        new_dir = Path(directory)
        if new_dir not in self.watch_directories:
            self.watch_directories.append(new_dir)

            # If monitoring is active, start watching this directory too
            if self.is_monitoring and os.path.exists(new_dir):
                file_handler = IBTFileHandler(
                    processor_callback=self._process_new_file,
                    coach_callback=self._add_to_coach
                )

                observer = Observer()
                observer.schedule(file_handler, str(new_dir), recursive=False)
                observer.start()
                self.observers.append(observer)

                logger.info(f"Added new watch directory: {new_dir}")

    def _process_new_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Process a new IBT file"""
        try:
            logger.info(f"Auto-processing: {os.path.basename(file_path)}")

            result = self.processor.process_telemetry_file(file_path)

            if result:
                self.files_processed += 1
                self.last_processed_file = {
                    'filename': os.path.basename(file_path),
                    'processed_at': datetime.now().isoformat(),
                    'track': result.get('session_info', {}).get('track', 'Unknown'),
                    'car': result.get('session_info', {}).get('car', 'Unknown'),
                    'laps': result.get('lap_analysis', {}).get('total_laps', 0)
                }

                logger.info(f"Auto-processed: {self.last_processed_file['filename']} - " +
                           f"{self.last_processed_file['track']} ({self.last_processed_file['car']}) - " +
                           f"{self.last_processed_file['laps']} laps")

                return result
            else:
                logger.warning(f"Failed to auto-process: {os.path.basename(file_path)}")
                return None

        except Exception as e:
            logger.error(f"Error in auto-processing {file_path}: {e}")
            return None

    def _add_to_coach(self, processed_data: Dict[str, Any]):
        """Add processed session to the AI coach"""
        try:
            session_id = self.coach.add_session(processed_data)
            logger.info(f"Added auto-processed session to coach: {session_id}")
        except Exception as e:
            logger.error(f"Error adding session to coach: {e}")


if __name__ == "__main__":
    # Test the file monitoring system
    print("=== Automatic IBT File Monitoring Test ===")

    # Import required modules for testing
    import sys
    sys.path.append('.')

    try:
        from enhanced_telemetry_processor import EnhancedTelemetryProcessor
        from ai_coach_enhanced import EnhancedDriveCoach

        processor = EnhancedTelemetryProcessor()
        coach = EnhancedDriveCoach("../data/processed_sessions")

        # Set up monitoring for current directory
        monitor = TelemetryFileMonitor(processor, coach, [Path.cwd().parent])

        print(f"Monitor initialized")
        print(f"Watch directories: {[str(d) for d in monitor.watch_directories]}")

        # Show status
        status = monitor.get_monitoring_status()
        print(f"Status: {status}")

        print("\nFile monitoring system ready!")
        print("To start monitoring: monitor.start_monitoring()")
        print("To stop monitoring: monitor.stop_monitoring()")

    except ImportError as e:
        print(f"Could not import required modules: {e}")
        print("Run this from the telemetry project directory")

    print("\n=== Test Complete ===")