from configs.config import Config
from nonebot.log import logger

def InitConfig():
    Config.add_plugin_config("STO_Recent", "INTERVAL", 20, help_="获取间隔")
    Config.add_plugin_config("STO_Recent", "GROUPS", None, help_="往哪些群里发送服务器状态信息")
    Config.add_plugin_config("STO_Recent", "DEBUG_MODE", False, help_="是否往终端打印Debug信息")
    Config.add_plugin_config("STO_Recent", "AUTO_RESTART", True, help_="是否自动重启STOChecker")
    
    logger.success("Config registered.")
    
    Debug_Mode = Config.get_config("STO_Recent", "DEBUG_MODE")
    Interval = Config.get_config("STO_Recent", "INTERVAL")
    Groups = Config.get_config("STO_Recent", "GROUPS")
    Auto_Restart = Config.get_config("STO_Recent", "AUTO_RESTART")
    
    if Debug_Mode:
        logger.info(f"Settings: Debug_Mode: {Debug_Mode}, Interval: {Interval}, Groups: {Groups}, Auto_Restart: {Auto_Restart}")