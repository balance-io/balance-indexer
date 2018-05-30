import aiohttp
import json

from balance_indexer.errors import SourceError
from balance_indexer import keystore
from balance_indexer.sources import coinwoke

BASE_URL='https://shapeshift.io'


async def index_currencies(session, redis_conn):
  get_coins_url = '{}/getcoins'.format(BASE_URL)
  resp = await session.get(get_coins_url)
  if resp.status != 200:
    raise SourceError('Shapeshift index currency symbols error')
  json_body = await resp.json()
  currencies = [ k for k, v in json_body.items() if v['status'] == 'available']
  erc20_only = await coinwoke.filter_erc20(redis_conn, currencies)
  await keystore.add_shapeshift_tokens(redis_conn, erc20_only)


async def index_minimum_deposit(session, redis_conn):
  market_info_url = '{}/marketinfo'.format(BASE_URL)
  resp = await session.get(market_info_url)
  if resp.status != 200:
    raise SourceError('Shapeshift index market info error')
  json_body = await resp.json()
  all_mins = { pair['pair'].lower(): pair['min'] for pair in json_body }
  await keystore.add_pair_deposit_min(redis_conn, all_mins)


async def index_rates(session, redis_conn):
  # get min deposit amount
  # get all pairs
  # send a request for rate with depositAmount
  quote_url = '{}/sendamount'.format(BASE_URL)
  futures = [session.post(url, {'amount': min_deposit, 'pair': pair}) for pair, min_deposit in all_pairs.items()]
  results = await asyncio.gather(*futures)
  if resp.status != 200:
    raise SourceError('Shapeshift index market info error')
  json_body = await resp.json()
  all_mins = { pair['pair'].lower(): pair['min'] for pair in json_body }
  await keystore.add_pair_deposit_min(redis_conn, all_mins)
