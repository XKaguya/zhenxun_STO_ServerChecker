from configs.config import Config
from nonebot.log import logger

def InitConfig():
    Config.add_plugin_config("STO_Recent", "Interval", 20, help_="获取间隔")
    Config.add_plugin_config("STO_Recent", "Groups", None, help_="往哪些群里发送服务器状态信息")
    Config.add_plugin_config("STO_Recent", "DEBUG_MODE", False, help_="是否往终端打印Debug信息")
    Config.add_plugin_config("STO_Recent", "Auto_Restart", True, help_="是否自动重启STOChecker")
    
    logger.success("Config registered.")