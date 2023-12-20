import json
import win32file
import pywintypes

async def send_message(pipe, message):
    try:
        win32file.WriteFile(pipe.handle, message.encode())
        return True
    except pywintypes.error as e:
        print(f"Error sending message: {e}")
        return False

async def receive_message(pipe, buffer_size=4096):
    try:
        resp = win32file.ReadFile(pipe, buffer_size)
        received_message = resp[1]
        return received_message
    except pywintypes.error as e:
        print(f"Error receiving message: {e}")
        return None

async def pipe_connect_to_server(msg):
    pipe_name = r'\\.\pipe\STOChecker'

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
                
    except pywintypes.error as e:
        print(f"Error: {e}")
    finally:
        try:
            win32file.CloseHandle(pipe.handle)
        except:
            pass
