import aiohttp
import logging

from balance_indexer import keystore

log=logging.getLogger(__name__)
BASE_URL='https://ethgasstation.info/json/ethgasAPI.json'

async def get_gas_prices(redis_conn):
  async with aiohttp.ClientSession() as session:
    async with session.get(BASE_URL) as resp:
      if resp.status != 200:
        log.error('Eth gas station get gas prices error with status: {}'.format(resp.status))
        return
      json_body = await resp.json()
      log.info(json_body)
      await keystore.add_gas_prices(redis_conn, json_body)
