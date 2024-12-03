import os
from pathlib import Path

from nonebot import on_command, require, get_bot
from nonebot.adapters.onebot.v11 import Bot, MessageSegment
from nonebot.adapters.onebot.v11.event import Event
from nonebot.log import logger

from zhenxun.configs.config import Config
from .utils.init import InitConfig
from .utils.messages import SendGroupMessageAsync
from .utils.scheduler import ConnectWithBackendScheduler
from .utils.connect import GetCalendar, GetIfNewsUpdated, GetNewsImage, RefreshCacheAsync
from .utils.maintenance import SendInitiativeAsync

InitConfig()


__zx_plugin_name__ = "STO状态查询插件"
__plugin_usage__ = """
usage：
/STORecent 				| /STOR
/STONews [Index]		| /STON [Index]
/STOCalendar			| /STOC
""".strip()
__plugin_des__ = "STO状态查询插件"
__plugin_type__ = ("一些工具",)
__plugin_cmd__ = ["STORecent"]

__plugin_settings__ = {
	"level": 5,
	"default_status": True,
	"limit_superuser": False,
	"cmd": ["STORecent"],
}

scheduler = require("nonebot_plugin_apscheduler").scheduler

Debug_Mode = Config.get_config("STO_Recent", "DEBUG_MODE")
AutoRestart_Mode = Config.get_config("STO_Recent", "AUTO_RESTART")
Interval = Config.get_config("STO_Recent", "INTERVAL")
Groups = Config.get_config("STO_Recent", "GROUPS")

# Passive

@scheduler.scheduled_job("interval", seconds=Interval, id="SchedulerFunc")

async def SchedulerFunc():
	bot = get_bot()
		
	await ConnectWithBackendScheduler(bot)
 
	if Debug_Mode:
		logger.info("Calling GetIfNewsUpdated...")
 
	success = await GetIfNewsUpdated()
 
	if success:
		parent_dir = Path(__file__).resolve().parent.parent
		parent_dir = os.path.join(parent_dir, 'STORecent')
		autonews_img = os.path.join(parent_dir, 'autonews_img.png')
		msg = MessageSegment.image(file=autonews_img)

		await SendGroupMessageAsync(Groups, msg, bot)


# Initiative
storecent = on_command("STORecent", aliases={"STOR", "STORecent", "stor", "storecent"}, priority=5, block=True)

@storecent.handle()
async def _(bot: Bot, ev: Event):
	Image = await SendInitiativeAsync(bot, ev)
	if Image != "null":
		await storecent.send(Image)
	else:
		await storecent.send("后端返回NULL错误或正在刷新缓存，请检查日志或耐心等待。")

storecent_screenshot = on_command("STONews", aliases={"STON", "STO新闻", "ston"}, priority=5, block=True)

@storecent_screenshot.handle()
async def _(bot: Bot, ev: Event):
	user_input = ev.get_plaintext()
	
	index = 0
	
	possible_prefixes = ["/STONews", "/STON", "/STO新闻", "/ston", "/stonews"]
	prefix = next((prefix for prefix in possible_prefixes if user_input.startswith(prefix)), None)
	
	if prefix:
		try:
			stripped_input = user_input.replace(prefix, "").strip()
		
			if stripped_input:
				try:
					index = int(stripped_input)
				except ValueError:
					await storecent_screenshot.send("输入的索引无效，使用默认索引 0。")
			else:
				await storecent_screenshot.send("未输入索引，使用默认索引 0。")
		except ValueError:
			await storecent_screenshot.send("输入的索引无效，使用默认索引 0。")
	
	parent_dir = Path(__file__).resolve().parent.parent
	parent_dir = os.path.join(parent_dir, 'STORecent')
	news_img = os.path.join(parent_dir, 'news.png')
	
	success, NewsLink = await GetNewsImage(index)
	if success and NewsLink is not None:
		if success == "null" and NewsLink is None:
			await storecent_screenshot.send("后端返回NULL错误或正在刷新缓存，请检查日志或耐心等待。")
		else:
			img = MessageSegment.image(file=news_img)

			await storecent_screenshot.send(f"新闻索引：{index} \n新闻链接： {NewsLink}")
			await storecent_screenshot.send(img)
	else:
		await storecent_screenshot.send("获取新闻图片失败，请稍后再试。")

storecent_refresh = on_command("RefreshCache", aliases={"RC"}, priority=5, block=True)

@storecent_refresh.handle()
async def _(bot: Bot, ev: Event):
	await RefreshCacheAsync()

storecent_getcalendar = on_command("STOCalendar", aliases={"STOC", "STO日历", "stoc"}, priority=5, block=True)

@storecent_getcalendar.handle()
async def _(bot: Bot, ev: Event):
	result = await GetCalendar()

	if result is not False or None:
		await storecent_getcalendar.send(result)