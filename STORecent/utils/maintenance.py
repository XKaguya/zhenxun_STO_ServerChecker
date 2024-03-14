from configs.config import Config
from .connect import GetMaintenanceInfoAsync, CheckLinkAsync
from nonebot.adapters.onebot.v11.event import Event
from nonebot.adapters.onebot.v11 import Bot, Message
from nonebot.log import logger
from .error import ReceiveError, ConnectionError, ConnectionCloseError, SendError
from .minfo import ShardStatus, MaintenanceInfo
from .draw import draw_server_status
import os
import asyncio
import subprocess
import time
from pathlib import Path
import json

json_path = Path(__file__).resolve().parent / "status.json"

Debug_Mode = Config.get_config("STO_Recent", "DEBUG_MODE")

parent_dir = Path(__file__).resolve().parent.parent
Exe_Path = os.path.join(parent_dir, 'STOChecker')
Exe = os.path.join(Exe_Path, 'StarTrekOnline-ServerStatus.exe')

async def ConnectWithBackendAsync():
    logger.info("Trying connect with backend program...")
    
    try:
        maintenance_details = await GetMaintenanceInfoAsync()
        
        logger.success(f"Backend responsed.")
        
        return maintenance_details
        
    except ConnectionError as ex:
        logger.error(ex)
        
        try:
            logger.info("Trying to restart STOChecker...")
            logger.info(f"Parent dir: {parent_dir}")
            logger.info(f"Exe dir: {Exe}")

            # subp = subprocess.run(f'"{Exe}" --pS', shell=True, check=False, cwd=Exe_Path)
            
            subp = subprocess.Popen(f'"{Exe}" --pS', shell=True, cwd=Exe_Path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            await asyncio.sleep(5)
            
            if subp.poll() == None:
                logger.success("STOChecker has been started.")
            else:
                logger.error("Failed to start STOChecker.")
                
            result = await CheckLinkAsync()
            
            if result:
                logger.success("Check passed. STOChecker has been successfully started.")
                
                await asyncio.sleep(1)
                
                maintenance_details = await GetMaintenanceInfoAsync()
        
                logger.success(f"Backend responsed.")
        
                return maintenance_details
            
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
        # if Debug_Mode:
        if True:
            logger.info("Function ConnectWithBackendAsync exited.")
            
async def SendGroupMessageAsync(Groups, Content, bot: Bot):
    if len(Groups) == 0:
        raise IndexError
    elif len(Groups) == 1:
        await bot.call_api('send_group_msg', **{'group_id': Groups[0], 'message': Message(Content)})
        logger.info(f"Written 'status': 'server is down', 'flag_0': 'true', 'flag_1': 'true', 'flag_2': 'false' into files")
    else:
        for i in Groups:
            await bot.call_api('send_group_msg', **{'group_id': i, 'message': Message(Content)})
            logger.info(f"Send {Content} to {i}")
            logger.info(f"Written 'status': 'server is down', 'flag_0': 'true', 'flag_1': 'true', 'flag_2': 'false' into files")
            
async def Serializer():
    logger.info("Trying to serialize data...")
    maintenanceInfo = await ConnectWithBackendAsync()
    maintenanceInfo = MaintenanceInfo(ShardStatus(maintenanceInfo[0]), maintenanceInfo[1], maintenanceInfo[2], maintenanceInfo[3], maintenanceInfo[4], maintenanceInfo[5], maintenanceInfo[6])

    logger.success(f"Incomming data has been serialized.")
    
    return maintenanceInfo
            
async def SendPassiveAsync(bot: Bot):
    if not os.path.exists(json_path):
        with open(json_path, 'w') as f:
            json.dump({'status': 'server is up', 'flag_0': 'false', 'flag_1': 'false', 'flag_2': 'true'}, f)
			# flag_0 是否在维护信息出现后发送过几时会维护标志位
			# flag_1 是否发送过目前开始维护信息
			# flag_2 是否在有公告的情况下发送过维护结束信息
    with open(json_path, 'r') as f:
        existing_data = json.load(f)
    
    try:
        maintenanceInfo = await Serializer()
        
        groups = Config.get_config("STO_Recent", "GROUPS")
        
        match maintenanceInfo.ShardStatus:
            case ShardStatus.Maintenance:
                if (existing_data.get("status") == 'server is up' and existing_data.get("flag_1") == 'false'):
                    logger.info("Server is currently offline and being maintenance. Please wait.")
                    msg = f"STO目前正在维护，预计{maintenanceInfo.Days}天{maintenanceInfo.Hours}小时{maintenanceInfo.Minutes}分钟{maintenanceInfo.Seconds}秒后结束维护。"
                    
                    await SendGroupMessageAsync(groups, msg, bot)
                    
                    with open(json_path, 'w') as f:
                        json.dump({'status': 'server is down', 'flag_0': 'true', 'flag_1': 'true', 'flag_2': 'false'}, f)
            
            case ShardStatus.WaitingForMaintenance:
                if existing_data.get("flag_0") == 'false':
                    logger.info("Server is waiting for maintenance. Please wait.")
                    msg = f"STO将在{maintenanceInfo.Days}天{maintenanceInfo.Hours}小时{maintenanceInfo.Minutes}分钟{maintenanceInfo.Seconds}秒后开始维护。"
                    
                    await SendGroupMessageAsync(groups, msg, bot)
                    
                    with open(json_path, 'w') as f:
                        json.dump({'status': 'server is up', 'flag_0': 'true', 'flag_1': 'false', 'flag_2': 'false'}, f)
                
            case ShardStatus.Up:
                logger.info("Server is up.")
                msg = f"Server Online"
                
            case ShardStatus.MaintenanceEnded:
                if existing_data.get('flag_2') == 'false':
                    logger.info("The maintenance has ended.")
                    msg = f"STO服务器已结束维护。"
                    
                    await SendGroupMessageAsync(groups, msg, bot)
                    
                    with open(json_path, 'w') as f:
                        json.dump({'status': 'server is up', 'flag_0': 'false', 'flag_1': 'false', 'flag_2': 'true'}, f)
                
            case ShardStatus.Null:
                logger.info("Null return. Please check backend.")
                msg = None
                
            case default:
                logger.error("Unexpected error.")
                msg = Exception
        
    except Exception as ex:
        logger.error(ex)
        
    finally:
        logger.info("Function SendPassiveAsync exited.")
                
async def SendInitiativeAsync(bot: Bot, ev: Event):
    try:
        maintenanceInfo = await Serializer()
        
        start_time = time.time()
 
        img = await draw_server_status(bot, ev, maintenanceInfo)

        end_time = time.time()
        time_cost = end_time - start_time    
        
        if Debug_Mode == True:
            logger.info("Called STORecent")
            logger.info(f"Time cost: {time_cost}")
            
        return img
        
    except Exception as ex:
        logger.error(ex)