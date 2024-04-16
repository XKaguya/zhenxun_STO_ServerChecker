import requests
from pathlib import Path
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters.onebot.v11.event import Event
from bs4 import BeautifulSoup
from urllib.parse import urljoin

async def GetNewsScreenshot(bot: Bot, ev: Event, playwright):
	url = "https://www.arcgames.com/en/games/star-trek-online/news"
	response = requests.get(url)
	html = response.text

	soup = BeautifulSoup(html, "html.parser")
	news_contents = soup.find_all("div", class_="news-content element")

	user_input = ev.get_plaintext()
	
	after = int(user_input.replace('/STONews', '').strip())

	msg = ''

	if after >= 0 and after < len(news_contents):
		news_content = news_contents[after]
		news_title = news_content.find("h2", class_="news-title").text.strip()
		module_infos = news_content.find("p", class_="module-infos").text.strip()
		read_more_link = news_content.find("a", class_="read-more")["href"]

		base_url = "https://www.arcgames.com"
		read_more_link = urljoin(base_url, read_more_link)

		msg += "================================\n"
		msg += f'标题：{news_title}\n'
		msg += f'概括：{module_infos}\n'
		msg += f'链接：{read_more_link}\n'

		img_path = Path(__file__).resolve().parent / "screenshot.png"

		browser = await playwright.chromium.launch()
		page = await browser.new_page()
		await page.goto(read_more_link)
		height = await page.evaluate('() => document.body.scrollHeight')
		await page.set_viewport_size({'width': 750, 'height': height})
		await page.screenshot(path=img_path)
		await browser.close()

		img_msg = MessageSegment.image(file=img_path)
		msg += '================================\n'
	else:
		msg = '错误的索引值，请输入正确的序号。\n'
		return msg
	
	msg += img_msg
	return msg