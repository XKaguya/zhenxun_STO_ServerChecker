from enum import Enum

class Command(Enum):
    ClientCheckServerAlive = 0
    ClientAskForPassiveType = 1
    ClientAskForScreenshot = 2
    ClientAskForDrawImage = 3
    ClientAskForRefreshCache = 4
    ClientAskForNews = 5
    ClientAskIfHashChanged = 6
    Null = 255