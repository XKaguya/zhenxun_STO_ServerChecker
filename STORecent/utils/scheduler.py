from nonebot.adapters.onebot.v11 import Bot

from zhenxun.configs.config import Config
from .maintenance import SendPassiveAsync


Debug_Mode = Config.get_config("STO_Recent", "DEBUG_MODE")

AutoRestart_Mode = Config.get_config("STO_Recent", "AUTO_RESTART")

async def ConnectWithBackendScheduler(bot: Bot):
    await SendPassiveAsync(bot)