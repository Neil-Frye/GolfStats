"""
Data transformation module for GolfStats application.

This module provides functionality to transform scraped data from various sources
(Trackman, Arccos, SkyTrak) into a standardized format for storage in the database.
"""
import os
import sys
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Add the project root directory to Python path if not already added
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database.db_connection import get_db
from backend.models.golf_data import GolfRound, GolfHole, GolfShot, RoundStats
from backend.database.supabase_data import (
    create_golf_round, 
    add_holes_for_round, 
    add_shots_for_hole, 
    add_round_stats
)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class GolfDataTransformer:
    """
    Transforms scraped golf data into database models.
    """
    
    def __init__(self, user_id: int):
        """
        Initialize the transformer.
        
        Args:
            user_id: Database ID of the user
        """
        self.user_id = user_id
        
    def transform_trackman_data(self, trackman_data: Dict[str, Any]) -> Tuple[GolfRound, List[GolfShot], Dict[str, Any]]:
        """
        Transform Trackman data to GolfStats models.
        
        Args:
            trackman_data: Raw Trackman data
            
        Returns:
            Tuple of (GolfRound, list of GolfShots, stats dictionary)
        """
        logger.info(f"Transforming Trackman data for user {self.user_id}")
        
        # Extract session metadata
        session_date = datetime.strptime(trackman_data.get("session_date", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")
        
        # Create the golf round
        golf_round = GolfRound(
            user_id=self.user_id,
            date=session_date,
            course_name=trackman_data.get("location", "Trackman Session"),
            source_system="trackman",
            notes=trackman_data.get("notes", "")
        )
        
        # Process shots
        shots = []
        for idx, shot_data in enumerate(trackman_data.get("shots", [])):
            shot = GolfShot(
                shot_number=idx + 1,
                club=shot_data.get("club", "Unknown"),
                ball_speed_mph=shot_data.get("ball_speed", None),
                club_speed_mph=shot_data.get("club_speed", None),
                smash_factor=shot_data.get("smash_factor", None),
                launch_angle_degrees=shot_data.get("launch_angle", None),
                spin_rate_rpm=shot_data.get("spin_rate", None),
                spin_axis_degrees=shot_data.get("spin_axis", None),
                carry_distance_yards=shot_data.get("carry_distance", None),
                total_distance_yards=shot_data.get("total_distance", None),
                side_deviation_yards=shot_data.get("side_deviation", None)
            )
            shots.append(shot)
        
        # Aggregate stats
        stats = {
            "average_drive_yards": self._calculate_average_drive_distance(shots),
            "extended_stats": {
                "average_ball_speed": self._calculate_average(shots, "ball_speed_mph"),
                "average_club_speed": self._calculate_average(shots, "club_speed_mph"),
                "average_smash_factor": self._calculate_average(shots, "smash_factor"),
                "average_launch_angle": self._calculate_average(shots, "launch_angle_degrees"),
                "average_spin_rate": self._calculate_average(shots, "spin_rate_rpm"),
                "shot_count": len(shots),
                "data_source": "trackman"
            }
        }
        
        return golf_round, shots, stats
    
    def transform_arccos_data(self, arccos_data: Dict[str, Any]) -> Tuple[GolfRound, List[GolfHole], List[List[GolfShot]], Dict[str, Any]]:
        """
        Transform Arccos data to GolfStats models.
        
        Args:
            arccos_data: Raw Arccos data
            
        Returns:
            Tuple of (GolfRound, list of GolfHoles, list of lists of GolfShots (by hole), stats dictionary)
        """
        logger.info(f"Transforming Arccos data for user {self.user_id}")
        
        # Extract round metadata
        round_date = datetime.strptime(arccos_data.get("date", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")
        course_name = arccos_data.get("course_name", "Unknown Course")
        
        # Create the golf round
        golf_round = GolfRound(
            user_id=self.user_id,
            date=round_date,
            course_name=course_name,
            course_location=arccos_data.get("course_location", ""),
            tee_color=arccos_data.get("tee_color", ""),
            total_score=arccos_data.get("total_score", 0),
            total_par=arccos_data.get("total_par", 0),
            front_nine_score=arccos_data.get("front_nine_score", 0),
            back_nine_score=arccos_data.get("back_nine_score", 0),
            weather_conditions=arccos_data.get("weather", ""),
            source_system="arccos"
        )
        
        # Process holes and shots
        holes = []
        shots_by_hole = []
        
        for hole_data in arccos_data.get("holes", []):
            hole_number = hole_data.get("number", 0)
            par = hole_data.get("par", 0)
            
            # Create hole
            hole = GolfHole(
                hole_number=hole_number,
                par=par,
                score=hole_data.get("score", 0),
                fairway_hit=hole_data.get("fairway_hit", None),
                green_in_regulation=hole_data.get("gir", None),
                putts=hole_data.get("putts", 0),
                distance_yards=hole_data.get("distance", 0)
            )
            holes.append(hole)
            
            # Process shots for this hole
            hole_shots = []
            for idx, shot_data in enumerate(hole_data.get("shots", [])):
                shot = GolfShot(
                    shot_number=idx + 1,
                    club=shot_data.get("club", "Unknown"),
                    distance_yards=shot_data.get("distance", 0),
                    from_location=shot_data.get("from_location", ""),
                    to_location=shot_data.get("to_location", ""),
                    is_penalty=shot_data.get("is_penalty", False),
                    carry_distance_yards=shot_data.get("carry_distance", None),
                    total_distance_yards=shot_data.get("total_distance", None)
                )
                hole_shots.append(shot)
            
            shots_by_hole.append(hole_shots)
        
        # Aggregate stats
        stats = {
            "score_to_par": arccos_data.get("score_to_par", 0),
            "fairways_hit": arccos_data.get("fairways_hit", 0),
            "fairways_total": arccos_data.get("fairways_total", 0),
            "greens_in_regulation": arccos_data.get("gir_total", 0),
            "putts_total": arccos_data.get("putts_total", 0),
            "putts_per_hole": arccos_data.get("putts_avg", 0.0),
            "penalties": arccos_data.get("penalties", 0),
            "extended_stats": arccos_data.get("extended_stats", {
                "data_source": "arccos"
            })
        }
        
        return golf_round, holes, shots_by_hole, stats
    
    def transform_skytrak_data(self, skytrak_data: Dict[str, Any]) -> Tuple[GolfRound, List[GolfShot], Dict[str, Any]]:
        """
        Transform SkyTrak data to GolfStats models.
        
        Args:
            skytrak_data: Raw SkyTrak data
            
        Returns:
            Tuple of (GolfRound, list of GolfShots, stats dictionary)
        """
        logger.info(f"Transforming SkyTrak data for user {self.user_id}")
        
        # Extract session metadata
        session_date = datetime.strptime(skytrak_data.get("session_date", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")
        
        # Create the golf round
        golf_round = GolfRound(
            user_id=self.user_id,
            date=session_date,
            course_name=skytrak_data.get("location", "SkyTrak Session"),
            source_system="skytrak",
            notes=skytrak_data.get("notes", "")
        )
        
        # Process shots
        shots = []
        for idx, shot_data in enumerate(skytrak_data.get("shots", [])):
            shot = GolfShot(
                shot_number=idx + 1,
                club=shot_data.get("club", "Unknown"),
                ball_speed_mph=shot_data.get("ball_speed", None),
                club_speed_mph=shot_data.get("club_speed", None),
                launch_angle_degrees=shot_data.get("launch_angle", None),
                spin_rate_rpm=shot_data.get("spin_rate", None),
                carry_distance_yards=shot_data.get("carry", None),
                total_distance_yards=shot_data.get("total", None)
            )
            shots.append(shot)
        
        # Aggregate stats
        stats = {
            "average_drive_yards": self._calculate_average_drive_distance(shots),
            "extended_stats": {
                "average_ball_speed": self._calculate_average(shots, "ball_speed_mph"),
                "average_launch_angle": self._calculate_average(shots, "launch_angle_degrees"),
                "average_spin_rate": self._calculate_average(shots, "spin_rate_rpm"),
                "shot_count": len(shots),
                "data_source": "skytrak"
            }
        }
        
        return golf_round, shots, stats
    
    def _calculate_average(self, shots: List[GolfShot], attribute_name: str) -> Optional[float]:
        """
        Calculate average for a shot attribute.
        
        Args:
            shots: List of GolfShot objects
            attribute_name: Name of the attribute to average
            
        Returns:
            Average value or None if no valid data
        """
        values = [getattr(shot, attribute_name) for shot in shots 
                 if getattr(shot, attribute_name) is not None]
        
        if not values:
            return None
            
        return sum(values) / len(values)
    
    def _calculate_average_drive_distance(self, shots: List[GolfShot]) -> Optional[float]:
        """
        Calculate average drive distance from shot data.
        
        Args:
            shots: List of GolfShot objects
            
        Returns:
            Average drive distance or None if no valid data
        """
        driver_shots = [shot for shot in shots 
                      if shot.club and shot.club.lower() in ("driver", "1w", "1-wood")
                      and shot.total_distance_yards]
        
        if not driver_shots:
            return None
            
        return sum(shot.total_distance_yards for shot in driver_shots) / len(driver_shots)


class GolfDataStorage:
    """
    Stores transformed golf data in the database.
    """
    
    def __init__(self, use_supabase: bool = True, use_sqlalchemy: bool = True):
        """
        Initialize the storage handler.
        
        Args:
            use_supabase: Whether to store data in Supabase
            use_sqlalchemy: Whether to store data in SQLAlchemy
        """
        self.use_supabase = use_supabase
        self.use_sqlalchemy = use_sqlalchemy
    
    def store_trackman_session(self, user_id: int, trackman_data: Dict[str, Any]) -> Optional[int]:
        """
        Store Trackman session data in the database.
        
        Args:
            user_id: User ID
            trackman_data: Raw Trackman data
            
        Returns:
            ID of the created golf round or None if failed
        """
        # Transform data
        transformer = GolfDataTransformer(user_id)
        golf_round, shots, stats = transformer.transform_trackman_data(trackman_data)
        
        # Store in database
        round_id = None
        
        # Using SQLAlchemy
        if self.use_sqlalchemy:
            try:
                with get_db() as db:
                    # Add round to database
                    db.add(golf_round)
                    db.flush()  # Flush to get the ID
                    round_id = golf_round.id
                    
                    # Create a dummy hole for the shots
                    hole = GolfHole(
                        round_id=round_id,
                        hole_number=1,
                        par=0,
                        distance_yards=0
                    )
                    db.add(hole)
                    db.flush()
                    
                    # Add shots to the hole
                    for shot in shots:
                        shot.hole_id = hole.id
                        db.add(shot)
                    
                    # Add stats
                    round_stats = RoundStats(
                        round_id=round_id,
                        **stats
                    )
                    db.add(round_stats)
                    
                    # Commit transaction
                    db.commit()
                    logger.info(f"Stored Trackman session with round ID {round_id} using SQLAlchemy")
                    
            except Exception as e:
                logger.error(f"Error storing Trackman data with SQLAlchemy: {str(e)}")
                round_id = None
        
        # Using Supabase
        if self.use_supabase:
            try:
                # Create round
                round_dict = {
                    "user_id": str(user_id),
                    "date": golf_round.date.isoformat(),
                    "course_name": golf_round.course_name,
                    "source_system": "trackman",
                    "notes": golf_round.notes
                }
                supabase_round = create_golf_round(str(user_id), round_dict)
                
                if supabase_round:
                    supabase_round_id = supabase_round["id"]
                    round_id = round_id or supabase_round_id
                    
                    # Create a dummy hole
                    hole_data = [{
                        "round_id": supabase_round_id,
                        "hole_number": 1,
                        "par": 0,
                        "distance_yards": 0
                    }]
                    holes_result = add_holes_for_round(supabase_round_id, hole_data)
                    
                    if holes_result:
                        hole_id = holes_result[0]["id"]
                        
                        # Add shots
                        shots_data = []
                        for shot in shots:
                            shot_dict = {
                                "hole_id": hole_id,
                                "shot_number": shot.shot_number,
                                "club": shot.club,
                                "ball_speed_mph": shot.ball_speed_mph,
                                "club_speed_mph": shot.club_speed_mph,
                                "smash_factor": shot.smash_factor,
                                "launch_angle_degrees": shot.launch_angle_degrees,
                                "spin_rate_rpm": shot.spin_rate_rpm,
                                "spin_axis_degrees": shot.spin_axis_degrees,
                                "carry_distance_yards": shot.carry_distance_yards,
                                "total_distance_yards": shot.total_distance_yards,
                                "side_deviation_yards": shot.side_deviation_yards
                            }
                            shots_data.append(shot_dict)
                        
                        add_shots_for_hole(hole_id, shots_data)
                        
                        # Add stats
                        add_round_stats(supabase_round_id, stats)
                        
                        logger.info(f"Stored Trackman session with round ID {supabase_round_id} using Supabase")
                    
            except Exception as e:
                logger.error(f"Error storing Trackman data with Supabase: {str(e)}")
        
        return round_id
    
    def store_arccos_round(self, user_id: int, arccos_data: Dict[str, Any]) -> Optional[int]:
        """
        Store Arccos round data in the database.
        
        Args:
            user_id: User ID
            arccos_data: Raw Arccos data
            
        Returns:
            ID of the created golf round or None if failed
        """
        # Transform data
        transformer = GolfDataTransformer(user_id)
        golf_round, holes, shots_by_hole, stats = transformer.transform_arccos_data(arccos_data)
        
        # Store in database
        round_id = None
        
        # Using SQLAlchemy
        if self.use_sqlalchemy:
            try:
                with get_db() as db:
                    # Add round to database
                    db.add(golf_round)
                    db.flush()  # Flush to get the ID
                    round_id = golf_round.id
                    
                    # Add holes and shots
                    for i, hole in enumerate(holes):
                        hole.round_id = round_id
                        db.add(hole)
                        db.flush()
                        
                        # Add shots for this hole
                        for shot in shots_by_hole[i]:
                            shot.hole_id = hole.id
                            db.add(shot)
                    
                    # Add stats
                    round_stats = RoundStats(
                        round_id=round_id,
                        **stats
                    )
                    db.add(round_stats)
                    
                    # Commit transaction
                    db.commit()
                    logger.info(f"Stored Arccos round with round ID {round_id} using SQLAlchemy")
                    
            except Exception as e:
                logger.error(f"Error storing Arccos data with SQLAlchemy: {str(e)}")
                round_id = None
        
        # Using Supabase
        if self.use_supabase:
            try:
                # Create round
                round_dict = {
                    "user_id": str(user_id),
                    "date": golf_round.date.isoformat(),
                    "course_name": golf_round.course_name,
                    "course_location": golf_round.course_location,
                    "tee_color": golf_round.tee_color,
                    "total_score": golf_round.total_score,
                    "total_par": golf_round.total_par,
                    "front_nine_score": golf_round.front_nine_score,
                    "back_nine_score": golf_round.back_nine_score,
                    "weather_conditions": golf_round.weather_conditions,
                    "source_system": "arccos"
                }
                supabase_round = create_golf_round(str(user_id), round_dict)
                
                if supabase_round:
                    supabase_round_id = supabase_round["id"]
                    round_id = round_id or supabase_round_id
                    
                    # Create holes
                    holes_data = []
                    for hole in holes:
                        hole_dict = {
                            "round_id": supabase_round_id,
                            "hole_number": hole.hole_number,
                            "par": hole.par,
                            "score": hole.score,
                            "fairway_hit": hole.fairway_hit,
                            "green_in_regulation": hole.green_in_regulation,
                            "putts": hole.putts,
                            "distance_yards": hole.distance_yards
                        }
                        holes_data.append(hole_dict)
                    
                    holes_result = add_holes_for_round(supabase_round_id, holes_data)
                    
                    if holes_result:
                        # Add shots for each hole
                        for i, hole_result in enumerate(holes_result):
                            hole_id = hole_result["id"]
                            shots_data = []
                            
                            for shot in shots_by_hole[i]:
                                shot_dict = {
                                    "hole_id": hole_id,
                                    "shot_number": shot.shot_number,
                                    "club": shot.club,
                                    "distance_yards": shot.distance_yards,
                                    "from_location": shot.from_location,
                                    "to_location": shot.to_location,
                                    "is_penalty": shot.is_penalty,
                                    "carry_distance_yards": shot.carry_distance_yards,
                                    "total_distance_yards": shot.total_distance_yards
                                }
                                shots_data.append(shot_dict)
                            
                            if shots_data:
                                add_shots_for_hole(hole_id, shots_data)
                        
                        # Add stats
                        add_round_stats(supabase_round_id, stats)
                        
                        logger.info(f"Stored Arccos round with round ID {supabase_round_id} using Supabase")
                    
            except Exception as e:
                logger.error(f"Error storing Arccos data with Supabase: {str(e)}")
        
        return round_id
    
    def store_skytrak_session(self, user_id: int, skytrak_data: Dict[str, Any]) -> Optional[int]:
        """
        Store SkyTrak session data in the database.
        
        Args:
            user_id: User ID
            skytrak_data: Raw SkyTrak data
            
        Returns:
            ID of the created golf round or None if failed
        """
        # Transform data
        transformer = GolfDataTransformer(user_id)
        golf_round, shots, stats = transformer.transform_skytrak_data(skytrak_data)
        
        # Store in database
        round_id = None
        
        # Using SQLAlchemy
        if self.use_sqlalchemy:
            try:
                with get_db() as db:
                    # Add round to database
                    db.add(golf_round)
                    db.flush()  # Flush to get the ID
                    round_id = golf_round.id
                    
                    # Create a dummy hole for the shots
                    hole = GolfHole(
                        round_id=round_id,
                        hole_number=1,
                        par=0,
                        distance_yards=0
                    )
                    db.add(hole)
                    db.flush()
                    
                    # Add shots to the hole
                    for shot in shots:
                        shot.hole_id = hole.id
                        db.add(shot)
                    
                    # Add stats
                    round_stats = RoundStats(
                        round_id=round_id,
                        **stats
                    )
                    db.add(round_stats)
                    
                    # Commit transaction
                    db.commit()
                    logger.info(f"Stored SkyTrak session with round ID {round_id} using SQLAlchemy")
                    
            except Exception as e:
                logger.error(f"Error storing SkyTrak data with SQLAlchemy: {str(e)}")
                round_id = None
        
        # Using Supabase
        if self.use_supabase:
            try:
                # Create round
                round_dict = {
                    "user_id": str(user_id),
                    "date": golf_round.date.isoformat(),
                    "course_name": golf_round.course_name,
                    "source_system": "skytrak",
                    "notes": golf_round.notes
                }
                supabase_round = create_golf_round(str(user_id), round_dict)
                
                if supabase_round:
                    supabase_round_id = supabase_round["id"]
                    round_id = round_id or supabase_round_id
                    
                    # Create a dummy hole
                    hole_data = [{
                        "round_id": supabase_round_id,
                        "hole_number": 1,
                        "par": 0,
                        "distance_yards": 0
                    }]
                    holes_result = add_holes_for_round(supabase_round_id, hole_data)
                    
                    if holes_result:
                        hole_id = holes_result[0]["id"]
                        
                        # Add shots
                        shots_data = []
                        for shot in shots:
                            shot_dict = {
                                "hole_id": hole_id,
                                "shot_number": shot.shot_number,
                                "club": shot.club,
                                "ball_speed_mph": shot.ball_speed_mph,
                                "club_speed_mph": shot.club_speed_mph,
                                "launch_angle_degrees": shot.launch_angle_degrees,
                                "spin_rate_rpm": shot.spin_rate_rpm,
                                "carry_distance_yards": shot.carry_distance_yards,
                                "total_distance_yards": shot.total_distance_yards
                            }
                            shots_data.append(shot_dict)
                        
                        add_shots_for_hole(hole_id, shots_data)
                        
                        # Add stats
                        add_round_stats(supabase_round_id, stats)
                        
                        logger.info(f"Stored SkyTrak session with round ID {supabase_round_id} using Supabase")
                    
            except Exception as e:
                logger.error(f"Error storing SkyTrak data with Supabase: {str(e)}")
        
        return round_id