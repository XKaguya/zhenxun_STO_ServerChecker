from configs.config import Config
from .connect import GetPassiveType, GetScreenshot, CheckLinkAsync
from .utils import SendGroupMessageAsync
from nonebot.adapters.onebot.v11.event import Event
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters.onebot.v11 import Bot
from nonebot.log import logger
from .error import ReceiveError, ConnectionError, ConnectionCloseError, SendError
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
    logger.info("Trying connect with backend program...")
    
    try:
        PassiveType = await GetPassiveType()
        if PassiveType:
            logger.success(f"Backend responsed.")
        
            return PassiveType
        elif PassiveType == ShardStatus.Null:
            raise ConnectionCloseError()
        
    except ConnectionError as ex:
        logger.error(ex)
        
        try:
            logger.info("Trying to restart STOChecker...")
            logger.info(f"Parent dir: {parent_dir}")
            logger.info(f"Exe dir: {Exe}")
            
            subp = subprocess.Popen(Exe, shell=True, cwd=Exe_Path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            await asyncio.sleep(5)
            
            if subp.poll() == None:
                logger.success("STOChecker has been started.")
            else:
                logger.error("Failed to start STOChecker.")
                
            result = await CheckLinkAsync()
            
            if result:
                logger.success("Check passed. STOChecker has been successfully started.")
                
                await asyncio.sleep(8)
                
                PassiveType = await GetPassiveType()
                
                if PassiveType:
                    logger.success(f"Backend responsed.")
                    
                    return PassiveType
        
                return None
            
            else:
                logger.error(f"Failed to start STOChecker.")

        except Exception as ex:
            logger.error(ex)

    except ReceiveError as ex:
        logger.error(ex)
        
    except ConnectionCloseError as ex:
        logger.error(ex)
        
    except SendError as ex:
        logger.error(ex)
        
    finally:
        if True:
            logger.info("Function ConnectWithBackendAsync exited.")

            
async def SendPassiveAsync(bot: Bot):
    PassiveType = await ConnectWithBackendAsync()
    
    msg = ""
    
    match PassiveType:
        case ShardStatus.WaitingForMaintenance:
            logger.info("Server is waiting for maintenance.")
            msg = f"STO有新的维护信息啦，获取详情信息请输入指令： /STORecent"
            await SendGroupMessageAsync(Groups, msg, bot)
        
        case ShardStatus.MaintenanceStarted:
            logger.info("Server down and maintenance.")
            msg = f"STO已开始维护，获取详情信息请输入指令： /STORecent"
            await SendGroupMessageAsync(Groups, msg, bot)
            
        case ShardStatus.MaintenanceEnded:
            logger.info("Server maintenance has ended.")
            msg = f"STO维护已结束。"
            await SendGroupMessageAsync(Groups, msg, bot)
            
        case ShardStatus.Null:
            logger.info("Null return. There's might be something error on the backend.")
            msg = None
        
                
async def SendInitiativeAsync(bot: Bot, ev: Event):
    try:
        if (await GetScreenshot()):
            parent_dir = Path(__file__).resolve().parent.parent
            img_path = os.path.join(parent_dir, 'msg.png')
            logger.info(img_path)
            
            img = MessageSegment.image(file=img_path)
                
            return img
        
    except Exception as ex:
        raise ConnectionCloseError()