from enum import Enum

class Command(Enum):
    ClientCheckServerAlive = 0
    ClientAskForCalendar = 1
    ClientAskForPassiveType = 2
    ClientAskForScreenshot = 3
    ClientAskForDrawImage = 4
    ClientAskForRefreshCache = 5
    ClientAskForNews = 6
    ClientAskIfHashChanged = 7
    Null = 255