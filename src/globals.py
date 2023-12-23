class SingletonMeta(type):
    """
    Base singleton Class to be used to create the business logic
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class GameVariables(metaclass=SingletonMeta):
    """
    Global variables to be able to access to this any place we need it
    """
    def __init__(self):
        self.screen = None
        self.delta_time = 0
        self.score = 0
        self.level = 1
