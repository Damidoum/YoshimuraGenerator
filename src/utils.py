import math


def end_point_of_line(
    starting_point: tuple[float], length: float, angle: float
) -> tuple[float]:
    """Compute the end point of a line given the starting point, length, and angle.

    Args:
        starting_point (tuple[float]): coordinates of the starting point
        length (float): length of the line
        angle (float): angle of the line in degrees

    Returns:
        tuple[float]: _description_
    """
    x = starting_point[0] + length * math.cos(math.radians(angle))
    y = starting_point[1] + length * math.sin(math.radians(angle))
    return (x, y)
