import json
import win32file
from nonebot.log import logger
# from loguru import logger
from .error import ReceiveError, ConnectionError, ConnectionCloseError, SendError

def GetData(data):
    data = json.loads(data)
    
    return (
        data['ShardStatus'],
        data['Days'],
        data['Hours'],
        data['Minutes'],
        data['Seconds'],
        data['NewsContents'],
        data['RecentNews']
    )

async def GetMaintenanceInfoAsync():
    predata = await ConnectAsync('sS')
    data = json.dumps(predata)
    
    result = GetData(data)
    return result

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

async def SendAsync(pipe, message):
    try:
        win32file.WriteFile(pipe.handle, message.encode())
        return True
    except:
        raise SendError("An error occurred while sending data.", 3)

async def RecvAsync(pipe, buffer_size=4096):
    try:
        resp = win32file.ReadFile(pipe, buffer_size)
        received_message = resp[1]
        return received_message
    except:
        raise ReceiveError("An error occurred while receiving data.", 1)

async def ConnectAsync(msg):
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

        message = msg

        if await SendAsync(pipe, message):
            received_message = await RecvAsync(pipe)
            if received_message:
                received_message_str = received_message
                data = json.loads(received_message_str)
                return data
    except:
        raise ConnectionError("An error occurred while connecting to the pipe server.", 1)
    finally:
        try:
            if pipe is not None:
                win32file.CloseHandle(pipe.handle)
        except:
            if pipe is not None and pipe.handle is not None:
                raise ConnectionCloseError()
            else:
                raise ConnectionCloseError("Error. Pipe server not found.", 2)
