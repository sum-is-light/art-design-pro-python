import uvicorn
import asyncio
from argparse import ArgumentParser

from app import create_app
from config import ENV_CONFIG
from scripts.data_manage import create_superadmin


app = create_app()

parser = ArgumentParser()
parser.add_argument('-c', '--create_superadmin', action='store_true', help='是否创建超级管理员，默认为true')

if __name__ == "__main__":
    args = parser.parse_args()
    if args.create_superadmin:
        name = input('用户名：')
        password = input('密码：')
        asyncio.run(create_superadmin(name=name, password=password))
    else:
        uvicorn.run(
            'main:app', host=ENV_CONFIG.host, port=ENV_CONFIG.port,
            reload=ENV_CONFIG.debug, workers=ENV_CONFIG.workers
        )
