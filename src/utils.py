class Position2D:
    """
    CLass to be used to save position states, to avoid create multiple x and y
    variables each time we need a position
    """

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def clear(self):
        self.x = 0
        self.y = 0

    def __str__(self):
        return f"x_axis = {self.x} | y_axis = {self.y}"
