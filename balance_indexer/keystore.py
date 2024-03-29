import aioredis
import asyncio
import logging

ASSET_PREFIX='asset'
PAIR_PREFIX='pair'

log=logging.getLogger(__name__)

async def initialize_keystore(loop):
  return await create_connection(event_loop=loop)


async def create_connection(event_loop, host='localhost', port=6379, db=0):
  redis_uri = 'redis://{}:{}/{}'.format(host, port, db)
  return await aioredis.create_redis(address=redis_uri, db=db, encoding='utf-8', loop=event_loop)


async def add_shapeshift_tokens(redis_conn, tokens):
  tokens_str = ','.join(tokens)
  await redis_conn.set('shapeshift:tokenlist', tokens_str)
  log.info('added available shapeshift tokens')


async def add_pair_deposit_min(redis_conn, all_pairs):
  futures = [redis_conn.set(pair_key(pair), min_deposit) for pair, min_deposit in all_pairs.items()]
  await asyncio.gather(*futures)
  log.info('added market info')


async def add_erc20_tokens(redis_conn, tokens):
  await redis_conn.sadd('coinwoke:tokens', *tokens)
  log.info('added erc20 tokens')


async def get_erc20_tokens(redis_conn):
  tokens = await redis_conn.smembers('coinwoke:tokens')
  return tokens


async def add_gas_prices(redis_conn, gas_prices):
  await redis_conn.hmset_dict('gasprices', gas_prices)
  log.info('added gas prices')


def token_key(token_address):
  return 'token:addr:{}'.format(token_address)


def asset_key(symbol):
  return '{}:{}'.format(ASSET_PREFIX, symbol)


def pair_key(pair):
  return 'pair:{}'.format(pair)
