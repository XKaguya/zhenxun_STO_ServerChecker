from .utils.init import InitConfig

InitConfig()

from .utils.messages import SendGroupMessageAsync, SendGroupImageMessageAsync
from .utils.scheduler import ConnectWithBackendScheduler
from .utils.connect import GetIfNewsUpdated, GetNewsImage, RefreshCacheAsync
from .utils.maintenance import SendInitiativeAsync

from nonebot import on_command, require, get_bot
from nonebot.adapters.onebot.v11.event import Event
from configs.config import Config
from nonebot.adapters.onebot.v11 import Bot, MessageSegment

from pathlib import Path

#from loguru import logger
from nonebot.log import logger

import os

__zx_plugin_name__ = "STO状态查询插件重制版"
__plugin_usage__ = """
usage：
STORecent
例：STORecent
""".strip()
__plugin_des__ = "STO状态查询插件重制版"
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
  
		await SendGroupImageMessageAsync(Groups, msg, bot)
		
storecent = on_command("STORecent", priority=5, block=True)

# Initiative

@storecent.handle()
async def _(bot: Bot, ev: Event):
	Image = await SendInitiativeAsync(bot, ev)
	if Image != "null":
		await storecent.send(Image)
	else:
		await storecent.send("后端返回NULL错误或正在刷新缓存，请检查日志或耐心等待。")

storecent_screenshot = on_command("STONews", priority=5, block=True)

@storecent_screenshot.handle()
async def _(bot: Bot, ev: Event):
	user_input = ev.get_plaintext()
	index = int(user_input.replace('/STONews', '').strip())
	
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

storecent_refresh = on_command("RefreshCache", priority=5, block=True)

@storecent_refresh.handle()
async def _(bot: Bot, ev: Event):
	await RefreshCacheAsync()