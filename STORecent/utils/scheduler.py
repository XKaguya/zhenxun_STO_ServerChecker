from configs.config import Config
from nonebot.log import logger
from .maintenance import SendPassiveAsync
from nonebot.adapters.onebot.v11 import Bot

Debug_Mode = Config.get_config("STO_Recent", "DEBUG_MODE")

AutoRestart_Mode = Config.get_config("STO_Recent", "AUTO_RESTART")

async def ConnectWithBackendScheduler(bot: Bot):
    logger.info("STORecent Interval")
    
    await SendPassiveAsync(bot)