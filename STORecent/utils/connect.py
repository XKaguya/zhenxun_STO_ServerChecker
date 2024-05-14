import win32file
#from loguru import logger
from nonebot.log import logger
from .error import ReceiveError, ConnectionError, ConnectionCloseError, SendError
from .mtype import ShardStatus
from pathlib import Path
import base64
import os

parent_dir = Path(__file__).resolve().parent.parent
img_path = os.path.join(parent_dir, 'msg.png')

async def CheckLinkAsync():
    pipe_name = r'\\.\pipe\STOChecker'
    pipe = None

    try:
        pipe = win32file.CreateFile(
            pipe_name,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0,
            None,
            win32file.OPEN_EXISTING,
            0,
            None
        )

        message = "cL"

        if await SendAsync(pipe, message):
            received_bytes = await RecvAsync(pipe)
            
            if received_bytes:
                try:
                    received_message = received_bytes.decode('utf-8')
                    
                    if received_message == "Success":
                        return True
                    else:
                        return False
                except UnicodeDecodeError as decode_error:
                    logger.error(f"Failed to decode received bytes: {decode_error}")
                    return False
            else:
                logger.error("Received empty message.")
                return False

    except Exception as ex:
        logger.error(f"Exception occurred: {ex}")
        return False

async def ConnectPipe(pipe_name):
    pipe = None
    
    try:
        pipe = win32file.CreateFile(
            pipe_name,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0,
            None,
            win32file.OPEN_EXISTING,
            0,
            None
        )
        return pipe
    except:
        raise ConnectionError("An error occurred while connecting to the pipe server.", 1)
    
async def GetPassiveType():
    pipe_name = r'\\.\pipe\STOChecker'
    pipe = None
    
    try:
        pipe = await ConnectPipe(pipe_name)
        
        message = "sS"
        
        if (await SendAsync(pipe, message)):
            rst = await RecvAsync(pipe, buffer_size=4096)
            rst = rst.decode('utf-8')
            
            status_enum = ShardStatus[rst]
            
            return status_enum
        else:
            raise ConnectionError("An error occurred while connecting to the pipe server.", 1)
        
    except Exception as ex:
        raise ConnectionError("An error occurred while connecting to the pipe server.", 1)
    finally:
        try:
            if pipe is not None:
                pipe.close()
        except Exception as ex:
            logger.error(f"Error closing pipe: {ex}")
            raise ConnectionCloseError("Error closing pipe.", 5)
    
async def GetImage():
    pipe_name = r'\\.\pipe\STOChecker'
    pipe = None
    
    try:
        pipe = await ConnectPipe(pipe_name)
        
        message = "dI"
        
        if await SendAsync(pipe, message):
            data = win32file.ReadFile(pipe.handle, 10000000)[1]
            
            logger.info(f"Size of data: {len(data)}")
            
            message = data.decode('utf-8')
            
            base64_parts = message.split(',')[1:]
            base64_data = ''.join(base64_parts)

            # Decode Base64 encoded data to `get` image data
            image_data = base64.b64decode(base64_data)
            
                
            with open(img_path, 'wb') as f:
                f.write(image_data)
            
            return True

    except Exception as ex:
        logger.error(f"Unknown error occurred: {ex}")
        return False
    finally:
        try:
            if pipe is not None:
                pipe.close()
        except Exception as ex:
            logger.error(f"Error closing pipe: {ex}")
            raise ConnectionCloseError("Error closing pipe.", 5)

    return True
    
async def ReadFromPipeWithSizeAsync(pipe, size, buffer_size=4096):
    try:
        data = b""
        while len(data) < size:
            resp = win32file.ReadFile(pipe, min(buffer_size, size - len(data)))
            received_bytes = resp[1]
            if not received_bytes:
                break
            data += received_bytes
        
        logger.info(f"Recived {len(data)} bytes of data.")
        return data
        
    except Exception as ex:
        logger.error(f"Error reading from pipe: {ex}")
        return None

async def RecvAsync(pipe, buffer_size=4096, retry_limit=3):
    received_message = b""
    retries = 0

    while retries < retry_limit:
        try:
            resp = win32file.ReadFile(pipe, buffer_size)
            received_bytes = resp[1]
            
            if not received_bytes:
                break
            
            received_message += received_bytes
            return received_message
        except Exception as ex:
            logger.error(f"Error reading from pipe: {ex}")
            retries += 1
            
    logger.error("Exceeded retry limit for reading from pipe.")
    raise ReceiveError("An error occurred while receiving data.", 4)

async def SendAsync(pipe, message):
    try:
        win32file.WriteFile(pipe.handle, message.encode())
        return True
    except Exception as ex:
        logger.error(f"Error sending data through pipe: {ex}")
        raise SendError("An error occurred while sending data.", 3)