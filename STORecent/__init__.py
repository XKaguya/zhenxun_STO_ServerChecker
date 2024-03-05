import requests
from PIL import Image, ImageDraw, ImageFont
from nonebot import on_command, require, get_bot
from pathlib import Path
import os
import json
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters.onebot.v11.event import Event
import io
import textwrap
from configs.config import Config
from nonebot.adapters.onebot.v11 import Bot, Message
from .utils.maintenance import check_server
import time

__zx_plugin_name__ = "STO状态查询插件"
__plugin_usage__ = """
usage：
STORecent
例：STORecent
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

json_path = Path(__file__).resolve().parent / "status.json"

Config.add_plugin_config("STO_Recent", "GROUPS", None, help_="往哪些群里发送服务器状态信息")
Config.add_plugin_config("STO_Recent", "DEBUG_MODE", False, help_="是否往终端打印Debug信息")
Debug_Mode = Config.get_config("STO_Recent", "DEBUG_MODE")

scheduler = require("nonebot_plugin_apscheduler").scheduler

@scheduler.scheduled_job("interval", seconds=20, id="processor_a")
async def processor_a():
	bot = get_bot()
	maintenance_details = await check_server()
	logger.info("Calling Function")
	if not os.path.exists(json_path):
		with open(json_path, 'w') as f:
			json.dump({'status': 'server is up', 'flag_0': 'false', 'flag_1': 'false', 'flag_2': 'true'}, f)
			# flag_0 是否在维护信息出现后发送过几时会维护标志位
			# flag_1 是否发送过目前开始维护信息
			# flag_2 是否在有公告的情况下发送过维护结束信息
	with open(json_path, 'r') as f:
		existing_data = json.load(f)
		
	if maintenance_details != 0:
		days = maintenance_details[1]
		hours = maintenance_details[2]
		minutes = maintenance_details[3]
		seconds = maintenance_details[4]
		logger.info(f"Return values: {maintenance_details[0]}")
		logger.info(f"Existing flags: {existing_data.get('flag_0')}, {existing_data.get('flag_1')}, {existing_data.get('flag_2')}") 
	
		if maintenance_details[0] == 0 and existing_data.get("status") == 'server is up' and existing_data.get("flag_1") == 'false':
			msg = f"STO目前正在维护，预计{days}天{hours}小时{minutes}分钟{seconds}秒后结束维护。"
			groups = Config.get_config("STO_Recent", "GROUPS")
			for i in groups:
				await bot.call_api('send_group_msg', **{'group_id': i, 'message': Message(msg)})
				logger.info(f"Send {msg} to {i}")
				logger.info(f"Written 'status': 'server is down', 'flag_0': 'true', 'flag_1': 'true', 'flag_2': 'false' into files")
			logger.info("Executed Path 1")
			with open(json_path, 'w') as f:
				json.dump({'status': 'server is down', 'flag_0': 'true', 'flag_1': 'true', 'flag_2': 'false'}, f)
	
		elif maintenance_details[0] == 1 and existing_data.get("flag_0") == 'false':
			msg = f"STO将在{days}天{hours}小时{minutes}分钟{seconds}秒后开始维护。"
			groups = Config.get_config("STO_Recent", "GROUPS")
			for i in groups:
				await bot.call_api('send_group_msg', **{'group_id': i, 'message': Message(msg)})
				logger.info(f"Send {msg} to {i}")
				logger.info(f"Written 'status': 'server is up', 'flag_0': 'true', 'flag_1': 'false', 'flag_2': 'false' into files")
			logger.info("Executed Path 2")
			with open(json_path, 'w') as f:
				json.dump({'status': 'server is up', 'flag_0': 'true', 'flag_1': 'false', 'flag_2': 'false'}, f)
		
		elif maintenance_details[0] == 3 and existing_data.get('flag_2') == 'false':
			msg = f"STO服务器已结束维护。"
			groups = Config.get_config("STO_Recent", "GROUPS")
			for i in groups:
				await bot.call_api('send_group_msg', **{'group_id': i, 'message': Message(msg)})
				logger.info(f"Send {msg} to {i}")
				logger.info(f"Written 'status': 'server is up', 'flag_0': 'false', 'flag_1': 'false', 'flag_2': 'true' into files")
			logger.info("Executed Path 3")
			with open(json_path, 'w') as f:
				json.dump({'status': 'server is up', 'flag_0': 'false', 'flag_1': 'false', 'flag_2': 'true'}, f)

storecent = on_command("STORecent", priority=5, block=True)

@storecent.handle()
async def _(bot: Bot, ev: Event):
	start_time = time.time()
 
	await draw_server_status(bot, ev)
 
	end_time = time.time()
	time_cost = end_time - start_time
	
	if Debug_Mode == True:
		logger.info("Called STORecent")
		logger.info(f"Time cost: {time_cost}")


async def draw_server_status(bot: Bot, ev: Event):
	img_path = Path(__file__).resolve().parent / "BGWN.png"
	aft_img_path = Path(__file__).resolve().parent / "After.png"
	background_image = Image.open(img_path)
	draw = ImageDraw.Draw(background_image)
	font_small = ImageFont.truetype("msyhl.ttc", 20)
 
	data = await check_server()
	all_in_one = get_split_data(data)

	server_status = data[0]

	status_color = "green" if server_status == "1" or "2" or "3" else "red"
	draw.text((805, 276), "在线" if server_status == "1" or "2" or "3" else "离线", fill=status_color, font=font_small)

	await draw_maintenance_message(all_in_one, server_status, background_image, draw)

	if Debug_Mode == True:
		logger.info("Called draw_server_status")
		
	await draw_news(all_in_one, bot, ev, background_image)
	
	background_image.save(aft_img_path)
	
	img_msg = MessageSegment.image(file=aft_img_path)
	await storecent.send(img_msg)


def get_split_data(data):
	return data[0], data[1], data[2], data[3], data[4], data[5], data[6]

async def draw_maintenance_message(message, server_status, background_image, draw, x=805, y=381):
	font_small = ImageFont.truetype("msyhl.ttc", 30)
	event_status, days, hours, minutes, seconds, news, recentEvents = message
	logger.info(f"{recentEvents}")
 
	y_offset = 40

	for event in recentEvents:
		title = event['Summary']
		time_left = event['TimeTillEnd'].strip('days.')
		start_date = event['StartDate']
		end_date = event['EndDate']
		logger.info(title)
		logger.info(time_left)
		logger.info(start_date)
		logger.info(end_date)

		if 'TimeTillStart' in event and event['TimeTillStart'] != '':
			time_start = event['TimeTillStart'].strip('days.')
			draw.text((x, y + y_offset), "活动将在 " + time_start + " 天后开启", fill="white", font=font_small)
		
		y_offset += 30

		draw.text((x, y + y_offset), "活动 " + title, fill="white", font=font_small)
		y_offset += 30

		draw.text((x, y + y_offset), "活动将在 " + time_left + " 天后结束", fill="white", font=font_small)
		y_offset += 30

		draw.text((x, y + y_offset), "活动开始日期: " + start_date, fill="white", font=font_small)
		y_offset += 30

		draw.text((x, y + y_offset), "活动结束日期: " + end_date, fill="white", font=font_small)
		y_offset += 30
		

	if event_status == 1:
		msg = f"STO将在{days}天{hours}小时{minutes}分钟{seconds}秒后开始维护。"
		draw.text((x, y), f"维护状态：即将维护", fill="white", font=font_small)
		draw.text((x, y + 40), msg, fill="white", font=font_small)
		
	elif event_status == 0:
		msg = f"STO目前正在维护，预计{days}天{hours}小时{minutes}分钟{seconds}秒后结束维护。"
		draw.text((x, y), f"维护状态：正在维护", fill="white", font=font_small)
		draw.text((x, y + 40), msg, fill="white", font=font_small)

async def draw_news(msg, bot: Bot, ev: Event, background_image):
	event_status, days, hours, minutes, seconds, news, recentEvents = msg
	news_data = json.dumps(news)
	news_data = json.loads(news_data)
	logger.info(news)

	grid_width = (2195 - 1471) // 3
	grid_height = (886 - 350) // 3

	x_position = 1471
	y_position = 350
	x_spacing = 40
	y_spacing = 30

	for index, news_content in enumerate(news_data[:9]):
		news_title = news_content['Title']
		img_url = news_content['ImageUrl']

		try:
			img_response = requests.get(img_url)
			img_response.raise_for_status()
			img_data = img_response.content
		except requests.exceptions.RequestException as e:
			img_error = f"下载新闻图片时出错，{e}，可能是网络波动导致的问题，请重试。"
			await bot.send(ev, img_error)
			continue

		if img_data:
			news_image = Image.open(io.BytesIO(img_data))
			news_image.thumbnail((grid_width, grid_height))

			background_image.paste(news_image, (x_position, y_position))
			await draw_news_title(background_image, news_title.strip(), x_position=x_position, y_position=y_position + grid_height)

		if (index + 1) % 3 == 0:
			x_position = 1471
			y_position += grid_height + y_spacing
		else:
			x_position += grid_width + x_spacing


async def draw_news_title(background_image, title, x_position, y_position):
	draw = ImageDraw.Draw(background_image)
	font_title = ImageFont.truetype("msyhl.ttc", 20)
	wrapped_title = textwrap.shorten(title, width=26, placeholder="...")
	draw.text((x_position, y_position), wrapped_title, fill="white", font=font_title)
	
	if Debug_Mode == True:
		logger.info("Called draw_news_title")
