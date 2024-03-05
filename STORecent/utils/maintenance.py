from nonebot.log import logger
from datetime import datetime, timedelta
import json
from .pipe_connect import pipe_connect_to_server

def get_data(data):
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

async def check_server():
    predata = await pipe_connect_to_server('sS')
    data = json.dumps(predata)
    
    result = get_data(data)
    return result
