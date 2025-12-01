"""
Helper functions for state validation and distance calculations.
"""
import math
from typing import Optional
from .config import STATE_TO_REGION, VALID_STATES


def state_to_region(state: str) -> Optional[str]:
    """Map a state code to its region (PACIFIC, MOUNTAIN, CENTRAL, EASTERN, OTHER)."""
    return STATE_TO_REGION.get(state.upper())


def validate_state(state: str) -> bool:
    """Check if a state code is valid."""
    return state.upper() in VALID_STATES


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two lat/lon points using Haversine formula (returns km)."""
    R = 6371.0  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

