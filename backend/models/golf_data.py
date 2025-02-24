"""
Golf data models for GolfStats application.

This module defines models for storing golf-related data such as rounds, shots,
and statistics from various tracking systems.
"""
import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship

from backend.database.db_connection import Base

class GolfRound(Base):
    """Model for a round of golf."""
    
    __tablename__ = "golf_rounds"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    course_name = Column(String(255), nullable=False)
    course_location = Column(String(255), nullable=True)
    tee_color = Column(String(50), nullable=True)
    total_score = Column(Integer, nullable=True)
    total_par = Column(Integer, nullable=True)
    front_nine_score = Column(Integer, nullable=True)
    back_nine_score = Column(Integer, nullable=True)
    weather_conditions = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    source_system = Column(String(50), nullable=True)  # 'arccos', 'manual', etc.
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="golf_rounds")
    holes = relationship("GolfHole", back_populates="round", cascade="all, delete-orphan")
    stats = relationship("RoundStats", back_populates="round", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<GolfRound(id={self.id}, user_id={self.user_id}, date={self.date}, course={self.course_name}, score={self.total_score})>"


class GolfHole(Base):
    """Model for a single hole in a round of golf."""
    
    __tablename__ = "golf_holes"
    
    id = Column(Integer, primary_key=True, index=True)
    round_id = Column(Integer, ForeignKey("golf_rounds.id"), nullable=False)
    hole_number = Column(Integer, nullable=False)
    par = Column(Integer, nullable=False)
    score = Column(Integer, nullable=True)
    fairway_hit = Column(Boolean, nullable=True)
    green_in_regulation = Column(Boolean, nullable=True)
    putts = Column(Integer, nullable=True)
    distance_yards = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    round = relationship("GolfRound", back_populates="holes")
    shots = relationship("GolfShot", back_populates="hole", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<GolfHole(id={self.id}, round_id={self.round_id}, hole_number={self.hole_number}, par={self.par}, score={self.score})>"


class GolfShot(Base):
    """Model for a single shot in a hole."""
    
    __tablename__ = "golf_shots"
    
    id = Column(Integer, primary_key=True, index=True)
    hole_id = Column(Integer, ForeignKey("golf_holes.id"), nullable=False)
    shot_number = Column(Integer, nullable=False)
    club = Column(String(50), nullable=True)
    distance_yards = Column(Float, nullable=True)
    from_location = Column(String(50), nullable=True)  # 'tee', 'fairway', 'rough', 'sand', 'green'
    to_location = Column(String(50), nullable=True)
    is_penalty = Column(Boolean, default=False)
    
    # Shot metrics (from launch monitors)
    ball_speed_mph = Column(Float, nullable=True)
    club_speed_mph = Column(Float, nullable=True)
    smash_factor = Column(Float, nullable=True)
    launch_angle_degrees = Column(Float, nullable=True)
    spin_rate_rpm = Column(Float, nullable=True)
    spin_axis_degrees = Column(Float, nullable=True)
    carry_distance_yards = Column(Float, nullable=True)
    total_distance_yards = Column(Float, nullable=True)
    side_deviation_yards = Column(Float, nullable=True)
    
    # Relationships
    hole = relationship("GolfHole", back_populates="shots")
    
    def __repr__(self):
        return f"<GolfShot(id={self.id}, hole_id={self.hole_id}, shot_number={self.shot_number}, club={self.club})>"


class RoundStats(Base):
    """Model for aggregated statistics for a round."""
    
    __tablename__ = "round_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    round_id = Column(Integer, ForeignKey("golf_rounds.id"), nullable=False, unique=True)
    score_to_par = Column(Integer, nullable=True)
    fairways_hit = Column(Integer, nullable=True)
    fairways_total = Column(Integer, nullable=True)
    greens_in_regulation = Column(Integer, nullable=True)
    putts_total = Column(Integer, nullable=True)
    putts_per_hole = Column(Float, nullable=True)
    sand_saves = Column(Integer, nullable=True)
    sand_save_attempts = Column(Integer, nullable=True)
    penalties = Column(Integer, nullable=True)
    average_drive_yards = Column(Float, nullable=True)
    scrambling_successful = Column(Integer, nullable=True)
    scrambling_attempts = Column(Integer, nullable=True)
    up_and_downs = Column(Integer, nullable=True)
    up_and_down_attempts = Column(Integer, nullable=True)
    three_putts = Column(Integer, nullable=True)
    
    # Extended stats from tracking systems (stored as JSON)
    extended_stats = Column(JSON, nullable=True)
    
    # Relationships
    round = relationship("GolfRound", back_populates="stats")
    
    def __repr__(self):
        return f"<RoundStats(id={self.id}, round_id={self.round_id}, score_to_par={self.score_to_par})>"


class Club(Base):
    """Model for a golf club in the user's bag."""
    
    __tablename__ = "clubs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    club_type = Column(String(50), nullable=False)  # 'driver', 'wood', 'hybrid', 'iron', 'wedge', 'putter'
    brand = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    loft = Column(Float, nullable=True)
    avg_distance_yards = Column(Float, nullable=True)
    max_distance_yards = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="clubs")
    
    def __repr__(self):
        return f"<Club(id={self.id}, user_id={self.user_id}, name={self.name}, type={self.club_type})>"