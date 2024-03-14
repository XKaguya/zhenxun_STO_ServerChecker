from .utils.initconfig import InitConfig

InitConfig()

from .utils.maintenance import SendInitiativeAsync
from .utils.scheduler import ConnectWithBackendScheduler

from nonebot import on_command, require, get_bot
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters.onebot.v11.event import Event
from configs.config import Config
from nonebot.adapters.onebot.v11 import Bot, Message

__zx_plugin_name__ = "STO状态查询插件重制版"
__plugin_usage__ = """
usage：
STORecent
例：STORecent
""".strip()
__plugin_des__ = "STO状态查询插件重制版"
__plugin_type__ = ("一些工具",)
__plugin_cmd__ = ["STO_Recent"]

__plugin_settings__ = {
	"level": 5,
	"default_status": True,
	"limit_superuser": False,
	"cmd": ["STO_Recent"],
}

scheduler = require("nonebot_plugin_apscheduler").scheduler

Debug_Mode = Config.get_config("STO_Recent", "DEBUG_MODE")
AutoRestart_Mode = Config.get_config("STO_Recent", "Auto_Restart")
Interval = Config.get_config("STO_Recent", "Interval")

@scheduler.scheduled_job("interval", seconds=Interval, id="SchedulerFunc")

async def SchedulerFunc():
	bot = get_bot()
		
	await ConnectWithBackendScheduler(bot)

storecent = on_command("STORecent", priority=5, block=True)

@storecent.handle()
async def _(bot: Bot, ev: Event):
	Image = await SendInitiativeAsync(bot, ev)
	await storecent.send(Image)