from utils.core import logger
from pyrogram import Client
from data import config
import os

class Accounts:
    def __init__(self):
        self.workdir = config.WORKDIR
        self.api_id = config.API_ID
        self.api_hash = config.API_HASH

    def pars_sessions(self):
        sessions = []
        for file in os.listdir(self.workdir):
            if file.endswith(".session"):
                sessions.append(file.replace(".session", ""))

        logger.info(f"Sesi ditemukan: {len(sessions)}!")
        return sessions

    async def check_valid_sessions(self, sessions: list):
        logger.info(f"Memeriksa validitas sesi!")
        valid_sessions = []
        if config.USE_PROXY:
            proxy_dict = {}
            with open('proxy.txt','r') as file:
                list = [i.strip().split() for i in file.readlines()]
                proxy_list = []
                for info in list:
                    if info!=[]:
                        proxy_list.append((info[0],''.join(info[1:]).replace('.session','')))
                for prox,name in proxy_list:
                    proxy_dict[name] = prox
            for session in sessions:
                try:
                    if session in proxy_dict:
                        proxy = proxy_dict[session]
                        proxy_client = {
                            "scheme": config.PROXY_TYPE,
                            "hostname": proxy.split(':')[0],
                            "port": int(proxy.split(':')[1]),
                            "username": proxy.split(':')[2],
                            "password": proxy.split(':')[3],
                        }
                        client = Client(name=session, api_id=self.api_id, api_hash=self.api_hash, workdir=self.workdir,proxy=proxy_client)

                        if await client.connect():
                            valid_sessions.append(session)
                        else:
                            logger.error(f"{session}.session is invalid")

                        await client.disconnect()
                    else:
                        if config.CHECK_PROXY:
                            logger.error(f"{session}.session PROXY TIDAK DITEMUKAN")
                            continue
                        client = Client(name=session, api_id=self.api_id, api_hash=self.api_hash, workdir=self.workdir)

                        if await client.connect():
                            valid_sessions.append(session)
                        else:
                            logger.error(f"{session}.session is invalid")
                        await client.disconnect()       
                except:
                    logger.error(f"{session}.session is invalid")
            logger.success(f"Sesi yang valid: {len(valid_sessions)}; Tidak sah: {len(sessions)-len(valid_sessions)}")
                
        else:
            for session in sessions:
                try:
                    client = Client(name=session, api_id=self.api_id, api_hash=self.api_hash, workdir=self.workdir)

                    if await client.connect():
                        valid_sessions.append(session)
                    else:
                        logger.error(f"{session}.session is invalid")
                    await client.disconnect()
                except:
                    logger.error(f"{session}.session is invalid")
            logger.success(f"Sesi yang valid: {len(valid_sessions)}; Tidak sah: {len(sessions)-len(valid_sessions)}")
        return valid_sessions

    async def get_accounts(self):
        sessions = self.pars_sessions()
        accounts = await self.check_valid_sessions(sessions)

        if not accounts:
            raise ValueError("Tidak ada sesi yang valid")
        else:
            return accounts
