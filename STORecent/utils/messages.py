from nonebot.adapters.onebot.v11 import Bot, Message
from nonebot.log import logger

async def SendGroupMessageAsync(Groups, Content, bot: Bot):
    if len(Groups) == 0:
        raise IndexError
    
    elif len(Groups) == 1:
        await bot.call_api('send_group_msg', **{'group_id': Groups[0], 'message': Message(Content)})
        logger.info(f"Send {Content} to {Groups[0]}")

    else:
        for i in Groups:
            await bot.call_api('send_group_msg', **{'group_id': i, 'message': Message(Content)})
            logger.info(f"Send {Content} to {i}")