from nonebot import require, get_bot
from configs.config import Config
from .connect import GetMaintenanceInfoAsync
from nonebot.log import logger
# from loguru import logger
from .error import ReceiveError, ConnectionError, ConnectionCloseError, SendError
from .maintenance import SendPassiveAsync
from nonebot.adapters.onebot.v11 import Bot
import subprocess
import os

Debug_Mode = Config.get_config("STO_Recent", "DEBUG_MODE")

AutoRestart_Mode = Config.get_config("STO_Recent", "AUTO_RESTART")

parent_dir = os.path.dirname(os.getcwd())
Exe_Path = os.path.join(parent_dir, 'STOChecker', 'StarTrekOnline-ServerStatus.exe')

async def ConnectWithBackendScheduler(bot: Bot):
    logger.info("STORecent Interval")
    
    await SendPassiveAsync(bot)
    
    