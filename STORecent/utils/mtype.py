from enum import Enum

class ShardStatus(Enum):
    WaitingForMaintenance = 0
    WaitingForMaintenanceSent = 1
    MaintenanceStarted = 2
    MaintenanceStartedSent = 3
    MaintenanceEnded = 4
    MaintenanceEndedSent = 5
    Null = 6
