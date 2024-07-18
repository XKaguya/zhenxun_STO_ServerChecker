from configs.config import Config
from .connect import GetPassiveType, GetImage, CheckLinkAsync
from .messages import SendGroupMessageAsync
from nonebot.adapters.onebot.v11.event import Event
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters.onebot.v11 import Bot
from nonebot.log import logger
import os
import asyncio
import subprocess
from pathlib import Path
from .mtype import ShardStatus

Debug_Mode = Config.get_config("STO_Recent", "DEBUG_MODE")

parent_dir = Path(__file__).resolve().parent.parent
Exe_Path = os.path.join(parent_dir, 'STOChecker')
Exe = os.path.join(Exe_Path, 'STOTool.exe')

Groups = Config.get_config("STO_Recent", "GROUPS")

async def ConnectWithBackendAsync():
    logger.info("Trying to connect with backend program...")
    
    PassiveType = await GetPassiveType()
    if PassiveType:
        logger.success("Backend responded.")
        return PassiveType
    else:
        try:
            logger.info("Trying to restart STOChecker...")
            logger.info(f"Parent dir: {parent_dir}")
            logger.info(f"Exe dir: {Exe}")
            
            subp = subprocess.Popen(Exe, shell=True, cwd=Exe_Path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            await asyncio.sleep(5)
            
            if subp.poll() is None:
                logger.success("STOChecker has been started.")
            else:
                logger.error("Failed to start STOChecker.")
                stdout, stderr = subp.communicate()
                logger.error(f"STDOUT: {stdout.decode()}")
                logger.error(f"STDERR: {stderr.decode()}")
                
            result = await CheckLinkAsync()
            
            if result:
                logger.success("Check passed. STOChecker has been successfully started.")
                
                await asyncio.sleep(8)
                
                PassiveType = await GetPassiveType()
                
                if PassiveType:
                    logger.success("Backend responded.")
                    return PassiveType
            else:
                logger.error("Failed to start STOChecker.")
        
        except Exception as ex:
            logger.error(ex)

async def SendPassiveAsync(bot: Bot):
    PassiveType = await ConnectWithBackendAsync()
    
    msg = ""
    
    match PassiveType:
        case ShardStatus.WaitingForMaintenance:
            logger.info("Server is waiting for maintenance.")
            msg = "STO有新的维护信息啦，获取详情信息请输入指令： /STORecent"
            await SendGroupMessageAsync(Groups, msg, bot)
        
        case ShardStatus.MaintenanceStarted:
            logger.info("Server down and maintenance.")
            msg = "STO已开始维护，获取详情信息请输入指令： /STORecent"
            await SendGroupMessageAsync(Groups, msg, bot)
            
        case ShardStatus.MaintenanceEnded:
            logger.info("Server maintenance has ended.")
            msg = "STO维护已结束。"
            await SendGroupMessageAsync(Groups, msg, bot)
            
        case ShardStatus.Null:
            logger.info("Null return. There might be something wrong on the backend.")
            msg = None

async def SendInitiativeAsync(bot: Bot, ev: Event):
    if await GetImage():
        parent_dir = Path(__file__).resolve().parent.parent
        img_path = os.path.join(parent_dir, 'msg.png')
        logger.info(img_path)
        
        img = MessageSegment.image(file=img_path)
        return img
