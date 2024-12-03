import os
import asyncio
import subprocess
from pathlib import Path

from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Bot, MessageSegment
from nonebot.adapters.onebot.v11.event import Event

from zhenxun.configs.config import Config
from .connect import GetPassiveType, GetImage, CheckLinkAsync
from .messages import SendGroupMessageAsync
from .mtype import ShardStatus


Debug_Mode = Config.get_config("STO_Recent", "DEBUG_MODE")

parent_dir = Path(__file__).resolve().parent.parent
Exe_Path = os.path.join(parent_dir, 'STOChecker')
Exe = os.path.join(Exe_Path, 'STOTool.exe')

Groups = Config.get_config("STO_Recent", "GROUPS")

async def ConnectWithBackendAsync():
    if Debug_Mode:
        logger.info("Trying to connect with backend program...")
    
    PassiveType = await GetPassiveType()
    if PassiveType:
        if Debug_Mode:
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
                    if Debug_Mode:
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
            if Debug_Mode:
                logger.info("Null return.")
            msg = None

async def SendInitiativeAsync(bot: Bot, ev: Event):
    rst = await GetImage()
    if rst != "null":
        parent_dir = Path(__file__).resolve().parent.parent
        img_path = os.path.join(parent_dir, 'msg.png')
        if Debug_Mode:
            logger.info(img_path)
        
        img = MessageSegment.image(file=img_path)
        return img
    else:
        return "null"
