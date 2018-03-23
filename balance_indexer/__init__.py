import argparse
from functools import partial
import asyncio
import uvloop
from aiohttp import ClientSession
import signal

from balance_indexer.sources import changelly
from  balance_indexer.sources import shapeshift
from balance_indexer.sources.changelly import ChangellyApiDetails
from balance_indexer.sources.shapeshift import ShapeshiftApiDetails
from balance_indexer import keystore

PERIOD_IN_SECONDS=60

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

def ask_exit(loop):
  loop.stop()


async def initialize_session(loop):
  return ClientSession(loop=loop)


async def initialize_redis(loop, local=False):
  return await keystore.initialize_keystore(loop, local=local)


def shapeshift_scheduler(period, loop, session, redis_conn, api_details):
  asyncio.ensure_future(shapeshift.index_currencies(session, redis_conn, api_details))
  loop.call_later(period, partial(shapeshift_scheduler, period, loop, session, redis_conn, api_details))


def changelly_scheduler(period, loop, session, redis_conn, api_details):
  asyncio.ensure_future(changelly.index_currencies(session, redis_conn, api_details))
  loop.call_later(period, partial(changelly_scheduler, period, loop, session, redis_conn, api_details))


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--redis-local', action='store_true')
  parser.add_argument('--shapeshift', type=str, default=None, help='API key to use Shapeshift API')
  parser.add_argument('--changelly', type=str, default=None, help='API key to use Changelly API')
  parser.add_argument('--changelly-sign', type=str, default=None, help='Signature to use Changelly API')
  args = parser.parse_args()

  # Get API details
  shapeshift_details = ShapeshiftApiDetails(args.shapeshift)
  changelly_details = ChangellyApiDetails(args.changelly, args.changelly_sign)

  loop = asyncio.get_event_loop()

  # Get Redis and aiohttp ClientSession
  redis_conn = loop.run_until_complete(initialize_redis(loop, args.redis_local))
  session = loop.run_until_complete(initialize_session(loop))

  # Add signal handlers for termination
  for signame in ('SIGINT', 'SIGTERM'):
    loop.add_signal_handler(getattr(signal, signame), partial(ask_exit, loop))

  # Schedule Shapeshift and Changelly indexers
  shapeshift_scheduler(PERIOD_IN_SECONDS, loop, session, redis_conn, shapeshift_details)
  changelly_scheduler(PERIOD_IN_SECONDS, loop, session, redis_conn, changelly_details)

  try:
    loop.run_forever()
  finally:
    loop.close()


if __name__ == '__main__':
  main()
