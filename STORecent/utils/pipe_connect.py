import json
import win32file
import pywintypes
from nonebot.log import logger
from .error import ReceiveError, ConnectionError, ConnectionCloseError, SendError

async def send_message(pipe, message):
    try:
        win32file.WriteFile(pipe.handle, message.encode())
        return True
    except:
        raise SendError("An error occurred while sending data.", 3)

async def receive_message(pipe, buffer_size=4096):
    try:
        resp = win32file.ReadFile(pipe, buffer_size)
        received_message = resp[1]
        return received_message
    except:
        raise ReceiveError("An error occurred while receiving data.", 1)

async def pipe_connect_to_server(msg):
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

        if await send_message(pipe, message):
            received_message = await receive_message(pipe)
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
