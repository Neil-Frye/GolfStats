"""
Mock implementations of scraper modules for serverless deployment.

This module provides lightweight mock versions of the scraper modules, allowing
the API to run on Vercel without the heavy browser automation dependencies.
"""
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class MockScraperBase:
    """Base class for mock scrapers that provides API-compatible methods."""
    
    def __init__(self, username=None, password=None, **kwargs):
        """Initialize the mock scraper."""
        self.username = username
        self.password = password
        self.is_logged_in = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info(f"Initialized mock {self.__class__.__name__}")
    
    def login(self) -> bool:
        """Mock login method."""
        self.logger.info(f"Mock login attempt with username: {self.username}")
        self.is_logged_in = True
        return True
    
    def logout(self) -> bool:
        """Mock logout method."""
        self.logger.info("Mock logout")
        self.is_logged_in = False
        return True
    
    def get_data(self, **kwargs) -> Dict[str, Any]:
        """Mock data retrieval method."""
        self.logger.info(f"Mock data retrieval with params: {kwargs}")
        return {
            "status": "success",
            "message": "This is a mock implementation for serverless deployment",
            "data": [],
            "source": self.__class__.__name__
        }
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.is_logged_in:
            self.logout()

class MockArccosScraper(MockScraperBase):
    """Mock implementation of ArccosScraper."""
    
    def get_rounds(self, limit=10) -> List[Dict[str, Any]]:
        """Mock method to get golf rounds from Arccos."""
        self.logger.info(f"Mock get_rounds with limit: {limit}")
        return []
    
    def get_shot_data(self, round_id) -> Dict[str, Any]:
        """Mock method to get shot data for a specific round."""
        self.logger.info(f"Mock get_shot_data for round_id: {round_id}")
        return {"round_id": round_id, "shots": []}

class MockTrackmanScraper(MockScraperBase):
    """Mock implementation of TrackmanScraper."""
    
    def get_sessions(self, limit=10) -> List[Dict[str, Any]]:
        """Mock method to get practice sessions from Trackman."""
        self.logger.info(f"Mock get_sessions with limit: {limit}")
        return []
    
    def get_session_details(self, session_id) -> Dict[str, Any]:
        """Mock method to get details for a specific session."""
        self.logger.info(f"Mock get_session_details for session_id: {session_id}")
        return {"session_id": session_id, "shots": []}

class MockSkytrakScraper(MockScraperBase):
    """Mock implementation of SkytrakScraper."""
    
    def get_practice_data(self, limit=10) -> List[Dict[str, Any]]:
        """Mock method to get practice data from Skytrak."""
        self.logger.info(f"Mock get_practice_data with limit: {limit}")
        return []

# Export mock implementations with the same names as the real scrapers
arccos_scraper = MockArccosScraper
trackman_scraper = MockTrackmanScraper
skytrak_scraper = MockSkytrakScraper