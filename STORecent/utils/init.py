from zhenxun.configs.config import Config
from nonebot.log import logger

def InitConfig():
	Config.add_plugin_config(
		"STO_Recent",
		"INTERVAL",
		20,
		help="获取间隔",
		default_value=20,
		type=int,
	)

	Config.add_plugin_config(
		"STO_Recent",
		"GROUPS",
		None,
		help="往哪些群里发送服务器状态信息",
		default_value=None,
		type=list,
	)

	Config.add_plugin_config(
		"STO_Recent",
		"DEBUG_MODE",
		False,
		help="是否往终端打印Debug信息",
		default_value=False,
		type=bool,
	)

	Config.add_plugin_config(
		"STO_Recent",
		"AUTO_RESTART",
		True,
		help="是否自动重启STOChecker",
		default_value=True,
		type=bool,
	)

	Config.add_plugin_config(
		"STO_Recent",
		"WebSocket",
		"ws://localhost:9500",
		help="WebSocket服务器地址",
		default_value="ws://localhost:9500",
		type=str,
	)
	
	logger.success("Config registered.")
	
	Debug_Mode = Config.get_config("STO_Recent", "DEBUG_MODE")
	Interval = Config.get_config("STO_Recent", "INTERVAL")
	Groups = Config.get_config("STO_Recent", "GROUPS")
	Auto_Restart = Config.get_config("STO_Recent", "AUTO_RESTART")
	WebSocket = Config.get_config("STO_Recent", "WebSocket")
	
	if Debug_Mode:
		logger.info(f"Settings: Debug_Mode: {Debug_Mode}, Interval: {Interval}, Groups: {Groups}, Auto_Restart: {Auto_Restart}, WebSocket: {WebSocket}")