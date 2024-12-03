from nonebot.adapters.onebot.v11 import Bot
from nonebot.log import logger

async def SendGroupMessageAsync(Groups, Content, bot: Bot, max_retries=3):
    if not Groups:
        logger.error("Groups list is empty.")
        return
    
    for group in Groups:
        retries = 0
        while retries < max_retries:
            try:
                await bot.call_api('send_group_msg', **{'group_id': group, 'message': Content})
                logger.info(f"Successfully sent '{Content}' to group {group}")
                break
            except Exception as ex:
                retries += 1
                logger.warning(f"Attempt {retries} failed to send message to group {group}: {ex}")
                if retries >= max_retries:
                    logger.error(f"Failed to send message to group {group} after {max_retries} attempts.")