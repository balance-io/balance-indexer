import aioredis
import asyncio

ASSET_PREFIX='asset'

async def initialize_keystore(loop, local=False):
  if local:
    return await create_connection(event_loop=loop)
  else:
    sentinels = sources.get_kms_parameter('balance-indexer-redis-sentinels')
    return await create_sentinel_connection(event_loop=loop, sentinels=sentinels.split(','))


async def create_connection(event_loop, host='localhost', port=6379, db=0):
  redis_uri = 'redis://{}:{}/{}'.format(host, port, db)
  return await aioredis.create_redis(address=redis_uri, db=db, encoding='utf-8', loop=event_loop)


async def create_sentinel_connection(event_loop, sentinels):
  default_port = 26379
  sentinel_ports = [(x, default_port) for x in sentinels]
  sentinel = await aioredis.create_sentinel(sentinel_ports, encoding='utf-8', loop=event_loop)
  return sentinel


async def add_currency_details(redis_conn, all_currencies):
  futures = [redis_conn.hmset_dict(asset_key(key), fields) for key, fields in all_currencies.items()]
  await asyncio.gather(*futures)
  print('added currency details')


def asset_key(symbol):
  return '{}:{}'.format(ASSET_PREFIX, symbol)
