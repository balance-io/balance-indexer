import argparse
from functools import partial
import asyncio
import uvloop
from aiohttp import ClientSession
import signal

from balance_indexer.sources import shapeshift
from balance_indexer.sources import coinwoke
from balance_indexer.sources.shapeshift import ShapeshiftApiDetails
from balance_indexer import keystore

ONE_MINUTE=60
FIVE_MINUTES=60*5

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

def ask_exit(loop):
  loop.stop()


async def initialize_session(loop):
  return ClientSession(loop=loop)


async def initialize_redis(loop, local=False):
  return await keystore.initialize_keystore(loop, local=local)


def shapeshift_market_info_scheduler(period, loop, session, redis_conn, api_details):
  asyncio.ensure_future(shapeshift.index_market_info(session, redis_conn, api_details))
  loop.call_later(period, partial(shapeshift_market_info_scheduler, period, loop, session, redis_conn, api_details))


def coinwoke_erc20_scheduler(period, loop, session, redis_conn):
  asyncio.ensure_future(coinwoke.index_erc20_tokens(session, redis_conn))
  loop.call_later(period, partial(coinwoke_erc20_scheduler, period, loop, session, redis_conn))


def shapeshift_currency_scheduler(period, loop, session, redis_conn):
  asyncio.ensure_future(shapeshift.index_currencies(session, redis_conn))
  loop.call_later(period, partial(shapeshift_currency_scheduler, period, loop, session, redis_conn))


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--redis-local', action='store_true')
  parser.add_argument('--etherscan', type=str, default=None, help='API key to use Etherscan API')
  args = parser.parse_args()

  loop = asyncio.get_event_loop()

  # Get Redis and aiohttp ClientSession
  redis_conn = loop.run_until_complete(initialize_redis(loop, args.redis_local))
  session = loop.run_until_complete(initialize_session(loop))

  # Add signal handlers for termination
  for signame in ('SIGINT', 'SIGTERM'):
    loop.add_signal_handler(getattr(signal, signame), partial(ask_exit, loop))

  # Schedule Shapeshift and Changelly indexers
  coinwoke_erc20_scheduler(FIVE_MINUTES, loop, session, redis_conn)
  shapeshift_currency_scheduler(FIVE_MINUTES, loop, session, redis_conn)
  shapeshift_market_info_scheduler(ONE_MINUTE, loop, session, redis_conn)

  try:
    loop.run_forever()
  finally:
    loop.close()


if __name__ == '__main__':
  main()
