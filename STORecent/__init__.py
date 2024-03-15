from .utils.initconfig import InitConfig

InitConfig()

from .utils.maintenance import SendInitiativeAsync
from .utils.scheduler import ConnectWithBackendScheduler
from .utils.utils import SendGroupMessageAsync
from .extensions.newsscreenshot import GetNewsScreenshot
from .extensions.autonews import GetNewsAsync

from nonebot import on_command, require, get_bot
from nonebot.adapters.onebot.v11.event import Event
from configs.config import Config
from nonebot.adapters.onebot.v11 import Bot

from playwright.async_api import async_playwright

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
	"cmd": ["STORecent"],
}

scheduler = require("nonebot_plugin_apscheduler").scheduler

Debug_Mode = Config.get_config("STO_Recent", "DEBUG_MODE")
AutoRestart_Mode = Config.get_config("STO_Recent", "Auto_Restart")
Interval = Config.get_config("STO_Recent", "Interval")
Groups = Config.get_config("STO_Recent", "GROUPS")

# Passive

@scheduler.scheduled_job("interval", seconds=Interval, id="SchedulerFunc")

async def SchedulerFunc():
	bot = get_bot()
		
	await ConnectWithBackendScheduler(bot)
 
	msg = await GetNewsAsync()
 
	if msg != 0:
		await SendGroupMessageAsync(Groups, msg, bot)
		
storecent = on_command("STORecent", priority=5, block=True)

# Initiative

@storecent.handle()
async def _(bot: Bot, ev: Event):
	Image = await SendInitiativeAsync(bot, ev)
	await storecent.send(Image)

storecent_screenshot = on_command("STONews", priority=5, block=True)

@storecent_screenshot.handle()
async def _(bot: Bot, ev: Event):
    async with async_playwright() as playwright:
         Image = await GetNewsScreenshot(bot, ev, playwright)
    await storecent_screenshot.send(Image)