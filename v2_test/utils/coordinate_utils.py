def to_centered_coordinates(x, y, width, height):
    """
    Convert scene coordinates to centered coordinate system.
    Center = (0,0)
    """
    x_centered = x - width / 2
    y_centered = height / 2 - y
    return int(x_centered), int(y_centered) 