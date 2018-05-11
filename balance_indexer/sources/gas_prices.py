import aiohttp

from balance_indexer.errors import SourceError
from balance_indexer import keystore

BASE_URL='https://ethgasstation.info/json/ethgasAPI.json'


async def get_gas_prices(session, redis_conn):
  resp = await session.get(BASE_URL)
  if resp.status != 200:
    raise SourceError('Eth Gas Station get gas prices error')
  json_body = await resp.json()
  await keystore.add_gas_prices(redis_conn, json_body)
