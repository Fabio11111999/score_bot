import time


class Game:
    def __init__(self):
        self.white_team, self.black_team = [], []
        self.start_time = None
        self.scorers, self.assists, self.time_stamps = [], [], []
        self.started = False

    def start(self) -> None:
        self.start_time = time.time()
        self.started = True

    def get_time_message(self) -> str:
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
