from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters.onebot.v11.event import Event
from nonebot.adapters.onebot.v11 import Bot, Message
from configs.config import Config
from .minfo import ShardStatus
import textwrap
import json
import requests
import io

Debug_Mode = Config.get_config("STO_Recent", "DEBUG_MODE")

async def draw_server_status(bot: Bot, ev: Event, data):
    try:
        img_path = Path(__file__).resolve().parent / "BGWN.png"
        aft_img_path = Path(__file__).resolve().parent / "After.png"
        background_image = Image.open(img_path)
        draw = ImageDraw.Draw(background_image)
        font_small = ImageFont.truetype("msyhl.ttc", 20)

        status_color = "green" if data.ShardStatus == ShardStatus.Up or ShardStatus.MaintenanceEnded or ShardStatus.WaitingForMaintenance else "red"
        draw.text((805, 276), "在线" if data.ShardStatus == ShardStatus.Up or ShardStatus.MaintenanceEnded or ShardStatus.WaitingForMaintenance else "离线", fill=status_color, font=font_small)

        await draw_maintenance_message(data, draw)

        if Debug_Mode == True:
            logger.info("Called draw_server_status")
            
        await draw_news(data, bot, ev, background_image)
        
        background_image.save(aft_img_path)
        
        img_msg = MessageSegment.image(file=aft_img_path)
        return img_msg

    except Exception as ex:
        logger.error(ex)

async def draw_maintenance_message(message, draw, x=805, y=381):
    try:
        font_small = ImageFont.truetype("msyhl.ttc", 30)
 
        y_offset = 40

        for event in message.RecentNews:
            title = event['Summary']
            time_left = event['TimeTillEnd'].strip('days.')
            start_date = event['StartDate']
            end_date = event['EndDate']

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

        if message.ShardStatus == ShardStatus.WaitingForMaintenance:
            msg = f"STO将在{message.Days}天{message.Hours}小时{message.Minutes}分钟{message.Seconds}秒后开始维护。"
            draw.text((x, y), f"维护状态：即将维护", fill="white", font=font_small)
            draw.text((x, y + 40), msg, fill="white", font=font_small)
            
        elif message.ShardStatus == ShardStatus.Maintenance:
            msg = f"STO目前正在维护，预计{message.Days}天{message.Hours}小时{message.Minutes}分钟{message.Seconds}秒后结束维护。"
            draw.text((x, y), f"维护状态：正在维护", fill="white", font=font_small)
            draw.text((x, y + 40), msg, fill="white", font=font_small)
   
    except Exception as ex:
        logger.error(ex)

async def draw_news(msg, bot: Bot, ev: Event, background_image):
    try:
        news_data = json.dumps(msg.NewsContents)
        news_data = json.loads(news_data)

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
    
    except Exception as ex:
        logger.error(ex)

async def draw_news_title(background_image, title, x_position, y_position):
    try:
        draw = ImageDraw.Draw(background_image)
        font_title = ImageFont.truetype("msyhl.ttc", 20)
        wrapped_title = textwrap.shorten(title, width=26, placeholder="...")
        draw.text((x_position, y_position), wrapped_title, fill="white", font=font_title)
        
        if Debug_Mode == True:
            logger.info("Called draw_news_title")

    except Exception as ex:
        logger.error(ex)