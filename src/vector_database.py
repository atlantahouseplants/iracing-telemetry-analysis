"""
Vector database for storing and retrieving telemetry insights using RAG
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class TelemetryVectorDB:
    """Vector database for telemetry insights using ChromaDB"""

    def __init__(self, db_path: str = "./data/chroma_db", collection_name: str = "iracing_telemetry"):
        """
        Initialize the vector database

        Args:
            db_path: Path to the ChromaDB database
            collection_name: Name of the collection to store telemetry data
        """
        self.db_path = Path(db_path)
        self.collection_name = collection_name
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        # Ensure database directory exists
        self.db_path.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "iRacing telemetry insights for AI coaching"}
        )

        logger.info(f"Vector database initialized at: {self.db_path}")
        logger.info(f"Collection: {collection_name}")

    def store_telemetry_insights(self, processed_data: Dict[str, Any]) -> str:
        """
        Store processed telemetry insights in the vector database

        Args:
            processed_data: Processed telemetry data with insights

        Returns:
            Document ID for the stored insights
        """
        try:
            # Create searchable text from the insights
            searchable_text = self._create_searchable_text(processed_data)

            # Generate embedding
            embedding = self.embedding_model.encode(searchable_text).tolist()

            # Create metadata
            metadata = self._create_metadata(processed_data)

            # Create document ID
            doc_id = processed_data.get('id', f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

            # Store in ChromaDB
            self.collection.add(
                documents=[searchable_text],
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[doc_id]
            )

            logger.info(f"Stored telemetry insights with ID: {doc_id}")
            return doc_id

        except Exception as e:
            logger.error(f"Error storing telemetry insights: {e}")
            raise

    def _create_searchable_text(self, processed_data: Dict[str, Any]) -> str:
        """
        Create searchable text from processed telemetry data

        Args:
            processed_data: Processed telemetry data

        Returns:
            Searchable text string
        """
        session_info = processed_data.get('session_info', {})
        lap_analysis = processed_data.get('lap_analysis', {})
        insights = processed_data.get('insights', {})

        # Build searchable text
        text_parts = []

        # Session details
        track = session_info.get('track', 'Unknown')
        car = session_info.get('car', 'Unknown')
        session_date = session_info.get('session_date', '')

        text_parts.append(f"Racing session at {track} with {car} on {session_date}")

        # Lap performance
        if 'fastest_lap' in lap_analysis and lap_analysis['fastest_lap']:
            text_parts.append(f"Fastest lap time: {lap_analysis['fastest_lap']:.3f} seconds")

        if 'total_laps' in lap_analysis:
            text_parts.append(f"Completed {lap_analysis['total_laps']} laps")

        # Driving analysis
        driving_analysis = insights.get('driving_analysis', {})
        if 'consistency_rating' in driving_analysis:
            rating = driving_analysis['consistency_rating']
            text_parts.append(f"Consistency rating: {rating}/10")

        if 'improvement_trend' in driving_analysis:
            trend = driving_analysis['improvement_trend']
            text_parts.append(f"Performance trend: {trend}")

        # Strengths
        strengths = insights.get('strengths', [])
        if strengths:
            text_parts.append("Strengths: " + ", ".join(strengths))

        # Improvement areas
        improvement_areas = insights.get('improvement_areas', [])
        if improvement_areas:
            text_parts.append("Areas to improve: " + ", ".join(improvement_areas))

        # Track and car specific insights
        track_performance = insights.get('track_performance', {})
        if 'track_specific_notes' in track_performance:
            notes = track_performance['track_specific_notes']
            if notes:
                text_parts.append("Track-specific advice: " + ", ".join(notes))

        car_performance = insights.get('car_performance', {})
        characteristics = car_performance.get('performance_characteristics', {})
        if characteristics:
            char_text = ", ".join([f"{k}: {v}" for k, v in characteristics.items()])
            text_parts.append(f"Car characteristics: {char_text}")

        # Session summary
        session_summary = insights.get('session_summary', {})
        if 'key_takeaways' in session_summary:
            takeaways = session_summary['key_takeaways']
            if takeaways:
                text_parts.append("Key takeaways: " + ", ".join(takeaways))

        return " | ".join(text_parts)

    def _create_metadata(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create metadata for the document

        Args:
            processed_data: Processed telemetry data

        Returns:
            Metadata dictionary
        """
        session_info = processed_data.get('session_info', {})
        lap_analysis = processed_data.get('lap_analysis', {})
        insights = processed_data.get('insights', {})

        metadata = {
            'track': session_info.get('track', 'Unknown'),
            'car': session_info.get('car', 'Unknown'),
            'session_date': session_info.get('session_date', ''),
            'session_time': session_info.get('session_time', ''),
            'processed_timestamp': processed_data.get('processed_timestamp', ''),
            'total_laps': lap_analysis.get('total_laps', 0),
            'fastest_lap': lap_analysis.get('fastest_lap', 0.0) if lap_analysis.get('fastest_lap') else 0.0,
            'consistency_rating': insights.get('driving_analysis', {}).get('consistency_rating', 0.0),
            'session_rating': insights.get('session_summary', {}).get('session_rating', {}).get('overall_rating', 0.0),
            'file_path': processed_data.get('file_path', ''),
        }

        # Convert any None values to appropriate defaults
        for key, value in metadata.items():
            if value is None:
                if key in ['total_laps']:
                    metadata[key] = 0
                elif key in ['fastest_lap', 'consistency_rating', 'session_rating']:
                    metadata[key] = 0.0
                else:
                    metadata[key] = ''

        return metadata

    def search_similar_sessions(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar sessions based on query

        Args:
            query: Search query
            n_results: Number of results to return

        Returns:
            List of similar sessions with metadata
        """
        try:
            # Generate embedding for query
            query_embedding = self.embedding_model.encode(query).tolist()

            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )

            # Format results
            formatted_results = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                formatted_results.append({
                    'document': doc,
                    'metadata': metadata,
                    'similarity_score': 1 - distance,  # Convert distance to similarity
                    'rank': i + 1
                })

            logger.info(f"Found {len(formatted_results)} similar sessions for query: {query}")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching similar sessions: {e}")
            return []

    def get_sessions_by_track(self, track: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get all sessions for a specific track

        Args:
            track: Track name
            limit: Maximum number of sessions to return

        Returns:
            List of sessions at the track
        """
        try:
            results = self.collection.get(
                where={"track": track},
                limit=limit,
                include=['documents', 'metadatas']
            )

            formatted_results = []
            for doc, metadata in zip(results['documents'], results['metadatas']):
                formatted_results.append({
                    'document': doc,
                    'metadata': metadata
                })

            logger.info(f"Found {len(formatted_results)} sessions at {track}")
            return formatted_results

        except Exception as e:
            logger.error(f"Error getting sessions by track: {e}")
            return []

    def get_sessions_by_car(self, car: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get all sessions for a specific car

        Args:
            car: Car name
            limit: Maximum number of sessions to return

        Returns:
            List of sessions with the car
        """
        try:
            results = self.collection.get(
                where={"car": car},
                limit=limit,
                include=['documents', 'metadatas']
            )

            formatted_results = []
            for doc, metadata in zip(results['documents'], results['metadatas']):
                formatted_results.append({
                    'document': doc,
                    'metadata': metadata
                })

            logger.info(f"Found {len(formatted_results)} sessions with {car}")
            return formatted_results

        except Exception as e:
            logger.error(f"Error getting sessions by car: {e}")
            return []

    def get_best_lap_times(self, track: str = None, car: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get sessions with best lap times

        Args:
            track: Optional track filter
            car: Optional car filter
            limit: Maximum number of sessions to return

        Returns:
            List of sessions sorted by fastest lap time
        """
        try:
            # Build where clause
            where_clause = {}
            if track:
                where_clause['track'] = track
            if car:
                where_clause['car'] = car

            # Get all matching sessions
            results = self.collection.get(
                where=where_clause if where_clause else None,
                include=['documents', 'metadatas']
            )

            # Sort by fastest lap time
            sessions_with_times = []
            for doc, metadata in zip(results['documents'], results['metadatas']):
                fastest_lap = metadata.get('fastest_lap', 0.0)
                if fastest_lap > 0:  # Only include sessions with valid lap times
                    sessions_with_times.append({
                        'document': doc,
                        'metadata': metadata,
                        'fastest_lap': fastest_lap
                    })

            # Sort by fastest lap time (ascending)
            sessions_with_times.sort(key=lambda x: x['fastest_lap'])

            return sessions_with_times[:limit]

        except Exception as e:
            logger.error(f"Error getting best lap times: {e}")
            return []

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the database

        Returns:
            Dictionary with database statistics
        """
        try:
            # Get collection info
            collection_count = self.collection.count()

            # Get unique tracks and cars
            all_sessions = self.collection.get(include=['metadatas'])

            tracks = set()
            cars = set()
            for metadata in all_sessions['metadatas']:
                if metadata.get('track'):
                    tracks.add(metadata['track'])
                if metadata.get('car'):
                    cars.add(metadata['car'])

            stats = {
                'total_sessions': collection_count,
                'unique_tracks': len(tracks),
                'unique_cars': len(cars),
                'tracks': sorted(list(tracks)),
                'cars': sorted(list(cars)),
                'database_path': str(self.db_path),
                'collection_name': self.collection_name
            }

            return stats

        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}


if __name__ == "__main__":
    # Test the vector database
    db = TelemetryVectorDB()

    print("=== Vector Database Test ===")

    # Test with some sample data
    sample_data = {
        'id': 'test_session_001',
        'processed_timestamp': datetime.now().isoformat(),
        'session_info': {
            'track': 'roadatlanta',
            'car': 'porsche992cup',
            'session_date': '2025-09-13',
            'session_time': '13:27:17'
        },
        'lap_analysis': {
            'total_laps': 5,
            'fastest_lap': 88.67,
            'lap_times': [92.34, 89.56, 88.89, 89.12, 88.67]
        },
        'insights': {
            'strengths': ['Good consistency', 'Strong improvement'],
            'improvement_areas': ['Braking optimization', 'Racing line'],
            'driving_analysis': {
                'consistency_rating': 8.5,
                'improvement_trend': 'Strong improvement'
            },
            'session_summary': {
                'session_rating': {'overall_rating': 7.5}
            }
        }
    }

    # Store sample data
    doc_id = db.store_telemetry_insights(sample_data)
    print(f"Stored sample data with ID: {doc_id}")

    # Test searches
    print("\\n--- Search Tests ---")

    # Search for consistency
    results = db.search_similar_sessions("consistency and improvement", n_results=3)
    print(f"\\nFound {len(results)} results for 'consistency and improvement':")
    for result in results:
        metadata = result['metadata']
        print(f"  - {metadata['track']} with {metadata['car']} (Score: {result['similarity_score']:.3f})")

    # Get database stats
    stats = db.get_database_stats()
    print(f"\\n--- Database Stats ---")
    print(f"Total sessions: {stats['total_sessions']}")
    print(f"Unique tracks: {stats['unique_tracks']}")
    print(f"Unique cars: {stats['unique_cars']}")
    print(f"Tracks: {stats['tracks']}")
    print(f"Cars: {stats['cars']}")

    print("\\n=== Test Complete ===")