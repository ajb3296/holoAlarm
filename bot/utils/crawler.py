import json
import aiohttp

async def getText(url : str, header : str = None):
    if not header:
        async with aiohttp.ClientSession (connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.get (url = url) as r :
                data = await r.text()
            return data
    async with aiohttp.ClientSession (connector=aiohttp.TCPConnector(verify_ssl=False), headers=header) as session:
        async with session.get (url = url) as r :
            data = await r.text()
        return data

async def getJSON(url : str, header : dict = None):
    async with aiohttp.ClientSession (connector=aiohttp.TCPConnector(verify_ssl=False), headers=header) as session:
      async with session.get (url) as r :
        data = await r.read()
      return json.loads(data)