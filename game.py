import time


class Game:
    """Class to represent a game of football"""

    def __init__(self):
        """Initializes the game with empty teams, no start time, no scorers, no assists and no time stamps."""
        self.white_team, self.black_team = [], []
        self.start_time = None
        self.scorers, self.assists, self.time_stamps = [], [], []
        self.started = False

    def start(self) -> None:
        """
        Starts the game.
        :return: None
        """
        self.start_time = time.time()
        self.started = True

    def get_time_message(self) -> str:
        """
        Returns the elapsed time
        :return: the elapsed time in the game formatted into a string
        """
        elapsed_seconds = int(time.time() - self.start_time)
        hours = elapsed_seconds // 3600
        minutes = (elapsed_seconds % 3600) // 60
        seconds = elapsed_seconds % 60
        return (
            "*Current Time:* `"
            + str(hours)
            + "h"
            + str(minutes)
            + "m"
            + str(seconds)
            + "s`"
        )
