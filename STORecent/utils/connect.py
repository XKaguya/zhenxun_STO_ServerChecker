import base64
import os
import asyncio
import json
from pathlib import Path

import websockets

from nonebot.log import logger
from zhenxun.configs.config import Config
from .mtype import ShardStatus
from .command import Command


parent_dir = Path(__file__).resolve().parent.parent
img_path = os.path.join(parent_dir, 'msg.png')
news_img = os.path.join(parent_dir, 'news.png')
autonews_img = os.path.join(parent_dir, 'autonews_img.png')

WebSocket = Config.get_config("STO_Recent", "WebSocket")
Debug_Mode = Config.get_config("STO_Recent", "DEBUG_MODE")

if WebSocket is not None:
    websocket_uri = WebSocket
else:
    websocket_uri = "ws://localhost:9500"

async def SendAndReceive(message):
    try:
        async with websockets.connect(websocket_uri, max_size=10000000) as websocket:
            await websocket.send(message)
            response = await websocket.recv()
            return response
    except Exception as ex:
        logger.error(f"An error occurred while connecting to the websocket server.: {ex}")
        return None

async def CheckLinkAsync():
    try:
        message = Command.ClientCheckServerAlive.name
        response = await asyncio.wait_for(SendAndReceive(message), timeout=40)
        return response == "Success"
    except asyncio.TimeoutError:
        logger.error("CheckLinkAsync timed out")
        return False
    except Exception as ex:
        logger.error(f"An error occurred while connecting to the websocket server.: {ex}")
        return False

async def GetPassiveType():
    try:
        message = Command.ClientAskForPassiveType.name
        response = await asyncio.wait_for(SendAndReceive(message), timeout=40)
        if response is not None:
            status_enum = ShardStatus[response]
            return status_enum
        else:
            return False
    except asyncio.TimeoutError:
        logger.error("GetPassiveType timed out")
        return False
    except Exception as ex:
        logger.error(f"An error occurred while connecting to the websocket server.: {ex}")
        return False
    
async def GetCalendar():
    try:
        message = Command.ClientAskForCalendar.name
        response = await asyncio.wait_for(SendAndReceive(message), timeout=40)
        if response is not None:
            return response
        else:
            return False
    except asyncio.TimeoutError:
        logger.error("GetCalendar timed out")
        return False
    except Exception as ex:
        logger.error(f"An error occurred while connecting to the websocket server.: {ex}")
        return False

async def RefreshCacheAsync():
    try:
        message = Command.ClientAskForRefreshCache.name
        await asyncio.wait_for(SendAndReceive(message), timeout=40)
    except asyncio.TimeoutError:
        logger.error("RefreshCacheAsync timed out")
    except Exception as ex:
        logger.error(f"An error occurred while connecting to the websocket server.: {ex}")

async def GetImage():
    try:
        message = Command.ClientAskForDrawImage.name
        response = await asyncio.wait_for(SendAndReceive(message), timeout=40)
        if response is not None:
            if Debug_Mode:
                logger.info(f"Size of data: {len(response)}")
            
            if response == "null":
                return "null"
            
            if "," in response:
                base64_parts = response.split(',')[1:]
                base64_data = ''.join(base64_parts)

                try:
                    image_data = base64.b64decode(base64_data)
                except Exception as decode_ex:
                    logger.error(f"Base64 decode error: {decode_ex}")
                    return False
                
                try:
                    with open(img_path, 'wb') as f:
                        f.write(image_data)
                        if Debug_Mode:
                            logger.info(f"Image written to {img_path}")
                        return True
                except Exception as write_ex:
                    logger.error(f"File write error: {write_ex}")
                    return False
            else:
                logger.error("Received data is not a valid base64 encoded string")
                return False
        
    except asyncio.TimeoutError:
        logger.error("GetImage timed out")
        return False
    except Exception as ex:
        logger.error(f"An error occurred while connecting to the websocket server.: {ex}")
        return False

async def GetIfNewsUpdated():
    try:
        message = Command.ClientAskIfHashChanged.name
        response = await asyncio.wait_for(SendAndReceive(message), timeout=40)
        if response != "null":
            if Debug_Mode:
                logger.info(f"Size of data: {len(response)}")
            
            image_data = base64.b64decode(response)
                
            try:
                with open(autonews_img, 'wb') as f:
                    f.write(image_data)
                    logger.info(f"Image written to {autonews_img}")
                    return True
            except Exception as write_ex:
                logger.error(f"File write error: {write_ex}")
                return False
        else:
            return False
        
    except asyncio.TimeoutError:
        logger.error("GetIfNewsUpdated timed out")
        return False
    except Exception as ex:
        logger.error(f"An error occurred while connecting to the websocket server.: {ex}")
        return False

async def GetNewsImage(index):
    try:
        message = f"{Command.ClientAskForNews.name} {index}"
        response = await asyncio.wait_for(SendAndReceive(message), timeout=40)
        
        if response is not None:
            if Debug_Mode:
                logger.info(f"Size of data: {len(response)}")

            if response == "null":
                return "null"
            
            try:
                result = json.loads(response)
                news_link = result.get("NewsLink")
                base64_image = result.get("Base64Screenshot")
            except json.JSONDecodeError as decode_ex:
                logger.error(f"Failed to decode JSON response: {decode_ex}")
                return False

            if base64_image == "null" or not base64_image:
                return "null"

            image_data = base64.b64decode(base64_image)
                
            try:
                with open(news_img, 'wb') as f:
                    f.write(image_data)
                    if Debug_Mode:
                        logger.info(f"Image written to {img_path}")
                    return True, news_link
            except Exception as write_ex:
                logger.error(f"File write error: {write_ex}")
                return False, None
    except asyncio.TimeoutError:
        logger.error("GetNewsImage timed out")
        return False, None
    except Exception as ex:
        logger.error(f"An error occurred while connecting to the websocket server: {ex}")
        return False, None
