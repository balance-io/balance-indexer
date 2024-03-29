from functools import partial
import asyncio
import uvloop
from aiohttp import ClientSession
import signal
import logging
#from web3 import Web3

from balance_indexer.sources import shapeshift, coinwoke, web3_filters, gas_prices
from balance_indexer import keystore

logging.basicConfig(level=logging.INFO)
log=logging.getLogger(__name__)

ONE_MINUTE=60
FIVE_MINUTES=60*5

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

def ask_exit(loop):
  loop.stop()


async def initialize_session(loop):
  return ClientSession(loop=loop)


async def initialize_redis(loop):
  return await keystore.initialize_keystore(loop)


def initialize_web3():
  return Web3(Web3.WebsocketProvider('wss://mainnet.infura.io/_ws'))


def shapeshift_min_deposit_scheduler(period, loop, session, redis_conn):
  asyncio.ensure_future(shapeshift.index_minimum_deposit(session, redis_conn), loop=loop)
  loop.call_later(period, partial(shapeshift_min_deposit_scheduler, period, loop, session, redis_conn))


def coinwoke_erc20_scheduler(period, loop, session, redis_conn):
  asyncio.ensure_future(coinwoke.index_erc20_tokens(session, redis_conn), loop=loop)
  loop.call_later(period, partial(coinwoke_erc20_scheduler, period, loop, session, redis_conn))


def shapeshift_currency_scheduler(period, loop, session, redis_conn):
  asyncio.ensure_future(shapeshift.index_currencies(session, redis_conn), loop=loop)
  loop.call_later(period, partial(shapeshift_currency_scheduler, period, loop, session, redis_conn))


def pending_txn_scheduler(period, loop, w3, txn_filter, redis_conn):
  asyncio.ensure_future(web3_filters.filter_pending_transactions(w3, txn_filter, redis_conn), loop=loop)
  loop.call_later(period, partial(pending_txn_scheduler, period, loop, w3, txn_filter, redis_conn))


def new_block_scheduler(period, loop, w3, block_filter, redis_conn):
  asyncio.ensure_future(web3_filters.filter_new_blocks(w3, block_filter, redis_conn), loop=loop)
  loop.call_later(period, partial(new_block_scheduler, period, loop, w3, block_filter, redis_conn))


def eth_gas_prices_scheduler(period, loop, redis_conn):
  asyncio.ensure_future(gas_prices.get_gas_prices(redis_conn), loop=loop)
  loop.call_later(period, partial(eth_gas_prices_scheduler, period, loop, redis_conn))


def main():
  loop = asyncio.get_event_loop()

  # Get Redis and aiohttp ClientSession
  redis_conn = loop.run_until_complete(initialize_redis(loop))
  session = loop.run_until_complete(initialize_session(loop))

  # Get web3 instance and filters
  #w3 = initialize_web3()
  #txn_filter = w3.eth.filter('pending')
  #block_filter = w3.eth.filter('latest')

  # Add signal handlers for termination
  #for signame in ('SIGINT', 'SIGTERM'):
  #  loop.add_signal_handler(getattr(signal, signame), partial(ask_exit, loop))

  # Schedule Shapeshift and Changelly indexers
  coinwoke_erc20_scheduler(FIVE_MINUTES, loop, session, redis_conn)
  shapeshift_currency_scheduler(FIVE_MINUTES, loop, session, redis_conn)
  shapeshift_min_deposit_scheduler(ONE_MINUTE, loop, session, redis_conn)
  eth_gas_prices_scheduler(ONE_MINUTE, loop, redis_conn)
  #pending_txn_scheduler(ONE_MINUTE, loop, w3, txn_filter, redis_conn)
  #new_block_scheduler(ONE_MINUTE, loop, w3, block_filter, redis_conn)

  try:
    loop.run_forever()
  finally:
    loop.close()


if __name__ == '__main__':
  main()
