# Utility functions for distance calculation between user and facility
import math


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the great circle distance between two points on the earth
    (specified in decimal degrees) using the Haversine formula.

    Args:
        lat1: Latitude of first point.
        lng1: Longitude of first point.
        lat2: Latitude of second point.
        lng2: Longitude of second point.

    Returns:
        Distance between points in kilometers, rounded to 2 decimal places.
    """
    earth_radius_km = 6371.0

    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)

    rad_lat1 = math.radians(lat1)
    rad_lat2 = math.radians(lat2)

    a = (
        math.sin(d_lat / 2.0) ** 2
        + math.cos(rad_lat1) * math.cos(rad_lat2) * math.sin(d_lng / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    distance = earth_radius_km * c
    return round(distance, 2)
