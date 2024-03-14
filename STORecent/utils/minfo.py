from enum import Enum

class ShardStatus(Enum):
    Maintenance = 0
    WaitingForMaintenance = 1
    Up = 2
    MaintenanceEnded = 3
    Null = 4

class MaintenanceInfo:
    def __init__(self, status, Days, Hours, Minutes, Seconds, NewsContents, RecentNews):
        self.ShardStatus = status
        self.Days = Days
        self.Hours = Hours
        self.Minutes = Minutes
        self.Seconds = Seconds
        self.NewsContents = NewsContents
        self.RecentNews = RecentNews
