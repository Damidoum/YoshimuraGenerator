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


def vector_difference(vector1: tuple[float], vector2: tuple[float]) -> tuple[float]:
    """Compute the difference between two vectors.

    Args:
        vector1 (tuple[float]): first vector
        vector2 (tuple[float]): second vector

    Returns:
        tuple[float]: difference between the two vectors
    """
    return (vector1[0] - vector2[0], vector1[1] - vector2[1])


def vector_sum(vector1: tuple[float], vector2: tuple[float]) -> tuple[float]:
    """Compute the sum of two vectors.

    Args:
        vector1 (tuple[float]): first vector
        vector2 (tuple[float]): second vector

    Returns:
        tuple[float]: sum of the two vectors
    """
    return (vector1[0] + vector2[0], vector1[1] + vector2[1])


def vector_multiply(vector: tuple[float], scalar: float) -> tuple[float]:
    """Multiply a vector by a scalar.

    Args:
        vector (tuple[float]): vector to multiply
        scalar (float): scalar to multiply the vector by

    Returns:
        tuple[float]: multiplied vector
    """
    return (vector[0] * scalar, vector[1] * scalar)


def normalize_vector(vector: tuple[float]) -> tuple[float]:
    """Normalize a vector.

    Args:
        vector (tuple[float]): vector to normalize

    Returns:
        tuple[float]: normalized vector
    """
    norm = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
    return (vector[0] / norm, vector[1] / norm)
