import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from pathlib import Path
from nonebot.log import logger
from configs.config import Config
import hashlib
import shutil
from playwright.async_api import async_playwright
from nonebot.adapters.onebot.v11 import MessageSegment


Json_path = Path(__file__).parent / "content.json"
Backup_path = Json_path.with_suffix('.bak')
img_path = Path(__file__).resolve().parent / "screenshot.png"


async def GetNewsAsync():
	try:
		Success = 0
		Debug_Mode = Config.get_config("STO_Recent", "DEBUG_MODE")

		if Debug_Mode:
			logger.info(f'Requesting News Page...')
			Success += 1

		url = 'https://www.arcgames.com/en/games/star-trek-online/news'
		response = requests.get(url)
		html_content = response.text

		existing_data = {}
		if Json_path.is_file():
			with open(Json_path, 'r') as json_file:
				existing_data = json.load(json_file)

		if Debug_Mode:
			logger.info(f'Loading Json File...')
			Success += 1

		current_content_hash = hashlib.sha256(html_content.encode()).hexdigest()

		if Debug_Mode:
			logger.info(f'Current Hash: {current_content_hash}')
		
		existing_content_hash = hashlib.sha256(existing_data.get("html_content", "").encode()).hexdigest()

		if Debug_Mode:
			logger.info(f'Existing Hash: {existing_content_hash}')

		if current_content_hash != existing_content_hash:
			data = {
				"html_content": html_content
			}

			if Debug_Mode:
				logger.info(f'Hash has changed. Updating data...')
				Success += 1

			if Json_path.is_file():
				shutil.copy(Json_path, Backup_path)

			with open(Json_path, 'w') as json_file:
				try:
					json.dump(data, json_file, indent=4)
				except Exception as e:
					logger.error(f'An error occurred while writing JSON file: {str(e)}')
					if Backup_path.is_file():
						shutil.copy(Backup_path, Json_path)
						logger.info(f'Main data file broken.Restoring backup file...')
					else:
						logger.error('No backup file found.')

			soup = BeautifulSoup(html_content, "html.parser")
			news_contents = soup.find_all("div", class_="news-content element")
			news_content = news_contents[0]
			read_more_link = news_content.find("a", class_="read-more")["href"]

			base_url = "https://www.arcgames.com"
			read_more_link = urljoin(base_url, read_more_link)

			url_new = read_more_link
			response = requests.get(url_new)
			html_content_new = response.text

			soup = BeautifulSoup(html_content_new, "html.parser")
			news_title_new = soup.find("div", class_="title-content")
			news_detail_new = soup.find("div", class_="news-detail news-detail--sto")

			msg = ''
			msg += news_title_new.get_text()
			msg += news_detail_new.get_text()
			msg = msg.strip()

			data["buffer"] = msg

			with open(Json_path, 'w') as json_file:
				try:
					json.dump(data, json_file, indent=4)
				except Exception as e:
					logger.error(f'An error occurred while writing JSON file: {str(e)}')
					if Backup_path.is_file():
						shutil.copy(Backup_path, Json_path)
						logger.info(f'Main data file broken.Restoring backup file...')
					else:
						logger.error('No backup file found.')

			if msg == existing_data.get("buffer"):
				if Debug_Mode:
					logger.info(f'Buffer was same. Returning 0 now...')
				return 0
			else:
				if Debug_Mode:
					Success += 1
					logger.info(f'Buffer is different.')
					logger.info(f'Written newest news to buffer...')
				if Debug_Mode and Success == 4:
					logger.info(f'Successfully get newest news... Now returning...')
				
					if len(existing_data.get("buffer")) >= 3000:
						async with async_playwright() as p:
							
							url = "https://www.arcgames.com/en/games/star-trek-online/news"
							response = requests.get(url)
							html = response.text

							soup = BeautifulSoup(html, "html.parser")
							news_contents = soup.find_all("div", class_="news-content element")
							news_content = news_contents[0]
							read_more_link = news_content.find("a", class_="read-more")["href"]
							base_url = "https://www.arcgames.com"
							read_more_link = urljoin(base_url, read_more_link)
							
							browser = await p.chromium.launch()
							page = await browser.new_page()
							await page.goto(read_more_link)
							height = await page.evaluate('() => document.body.scrollHeight')
							await page.set_viewport_size({'width': 750, 'height': height})
							await page.screenshot(path=img_path)
							
							with open(img_path, 'rb') as f:
								img_segment = MessageSegment.image(f.read())
								
							await browser.close()
							return img_segment
					else:
						return msg
		else:
			if Debug_Mode:
				logger.info(f'Content was same. Returning 0 now...')
			return 0

	except Exception as e:
		logger.error(f'An error occurred: {str(e)}')	
		if Backup_path.is_file():
			shutil.copy(Backup_path, Json_path)
		else:
			logger.error('No backup file found.')
		return 0